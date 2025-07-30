from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.node import Node
from rclpy.client import Client
from rclpy.action import ActionClient
from rclpy.task import Future
from rclpy.logging import get_logger
from threading import Event
from functools import partial
from typing import (
    Optional,
    Dict,
    Union,
    Any,
)
from ros2_geek.metaclasses import ManagedSingletonMeta

# from concurrent.futures import Future
from pydantic import BaseModel, ConfigDict
from inspect import signature


class ClientManager(metaclass=ManagedSingletonMeta):
    class ClientInfo(BaseModel):
        model_config = ConfigDict(
            arbitrary_types_allowed=True,
        )
        srv_name: str = ""
        future: Optional[Future] = None
        result: Any = None
        done: Event = Event()

    def __init__(self, node: Node):
        """
        manage clients by their service names
        """
        self._node = node
        self.node_name = node.get_name()
        self.clients: Dict[str, Client] = {}
        self.clients_info: Dict[str, ClientManager.ClientInfo] = {}

    def get_logger(self):
        return get_logger(ClientManager.__name__)

    def add(self, client: Union[Client, ActionClient]):
        srv_name = self.get_service_name(client)
        if srv_name in self.clients:
            self.get_logger().warning(f"Client of service: {srv_name} already exists")
            return
        self.clients[srv_name] = client
        info = ClientManager.ClientInfo()
        info.done.set()
        self.clients_info[srv_name] = info
        self.clients_info[srv_name].srv_name = srv_name

    def _create_client(
        self, srv_type, srv_name, *, qos_profile=None, callback_group=None, action=False
    ):
        if callback_group is None:
            callback_group = MutuallyExclusiveCallbackGroup()
        qos_profile_kwargs = {}
        if srv_name not in self.clients:
            if not action:
                if qos_profile is not None:
                    qos_profile_kwargs["qos_profile"] = qos_profile
                if self._node.__class__ is Node:
                    node = self._node
                else:
                    mro = self._node.__class__.__mro__
                    node_index = mro.index(Node)
                    node = super(mro[node_index - 1], self._node)
                client = node.create_client(
                    srv_type,
                    srv_name,
                    **qos_profile_kwargs,
                    callback_group=callback_group,
                )
            else:
                if qos_profile is not None:
                    qos_profile_kwargs = {
                        "goal_service_qos_profile": qos_profile,
                        "result_service_qos_profile": qos_profile,
                        "cancel_service_qos_profile": qos_profile,
                    }
                client = ActionClient(
                    self._node,
                    srv_type,
                    srv_name,
                    callback_group=callback_group,
                    **qos_profile_kwargs,
                )
            self.add(client)
        else:
            srv_type_ = self.get_service_type(srv_name)
            if srv_type == srv_type_:
                self.get_logger().warning(
                    f"Client of service: {srv_name} with type {srv_type} already exists and will be reused"
                )
            else:
                # TODO: should raise error? or should we allow different types with the same name?
                raise NotImplementedError(
                    f"Service {srv_name} has different types: {srv_type} and {srv_type_}"
                )
            client = self.clients[srv_name]
        return client

    def create_client(
        self,
        srv_type,
        srv_name,
        *,
        qos_profile=None,
        callback_group=None,
    ) -> Client:
        """Create a Client or ActionClient"""
        return self._create_client(
            srv_type,
            srv_name,
            qos_profile=qos_profile,
            callback_group=callback_group,
            action=False,
        )

    def create_action_client(
        self,
        srv_type,
        srv_name,
        *,
        qos_profile=None,
        callback_group=None,
    ) -> ActionClient:
        return self._create_client(
            srv_type,
            srv_name,
            qos_profile=qos_profile,
            callback_group=callback_group,
            action=True,
        )

    def wait_for_service(
        self,
        client: Union[str, Client, ActionClient],
        timeout_sec: Optional[float] = None,
    ):
        if isinstance(client, str):
            client = self.clients[client]
        if isinstance(client, Client):
            return client.wait_for_service(timeout_sec)
        elif isinstance(client, ActionClient):
            return client.wait_for_server(timeout_sec)
        else:
            raise TypeError(f"client must be a Client or ActionClient: {client}")

    def service_is_ready(self, client: Union[str, Client, ActionClient]) -> bool:
        if isinstance(client, str):
            client = self.clients[client]
        if isinstance(client, Client):
            return client.service_is_ready()
        elif isinstance(client, ActionClient):
            return client.server_is_ready()
        else:
            raise TypeError(f"client must be a Client or ActionClient: {client}")

    def call(
        self,
        client: Union[str, Client, ActionClient],
        request: Any,
        wait: bool = False,
        timeout_sec: Optional[float] = None,
    ) -> Any:
        if isinstance(client, str):
            client = self.clients[client]
        # get call functions and info
        if isinstance(client, Client):
            if signature(client.call).parameters.get("timeout_sec") is not None:
                call = partial(client.call, timeout_sec=timeout_sec)
            else:
                self.get_logger().warning(
                    "Client has no timeout_sec parameter in ROS2 foxy"
                )
                call = client.call
            call_async = client.call_async
            info = self.clients_info[client.srv_name]
        elif isinstance(client, ActionClient):
            call = client.send_goal
            call_async = client.send_goal_async
            info = self.clients_info[client._action_name]
        else:
            raise TypeError(f"client must be a Client or ActionClient: {client}")

        info.result = None
        if not info.done.is_set():
            self.get_logger().warning(
                f"Waiting for {info.srv_name} to finish the previous call"
            )
            if not info.done.wait(timeout_sec):
                info.future.cancel()
                self.get_logger().warning(
                    f"Timeout waiting for {info.srv_name} to finish the previous call"
                )
                info.future = None
                raise TimeoutError(f"Timeout waiting for {info.srv_name} to finish")
                # should return False? or configure to continue?
                # return False
        # self.get_logger().error(f"Calling {info.srv_name}. wait: {wait}")
        if wait:
            info.result = call(request)
        else:
            info.future = None
            info.done.clear()
            info.future = call_async(request)
            info.future.add_done_callback(partial(self.__callback, info.srv_name))
        # self.get_logger().error(f"Called {info.srv_name} done")
        return info.result

    def wait(
        self,
        client: Union[str, Client, ActionClient],
        timeout_sec: Optional[float] = None,
    ) -> bool:
        return self.get_info(client).done.wait(timeout_sec)

    def get_result(self, client: Union[str, Client, ActionClient]) -> Any:
        return self.get_info(client).result

    def get_future(self, client: Union[str, Client, ActionClient]) -> Optional[Future]:
        return self.get_info(client).future

    def get_service_name(self, client: Union[str, Client, ActionClient]) -> str:
        if isinstance(client, str):
            return client
        elif isinstance(client, Client):
            return client.srv_name
        elif isinstance(client, ActionClient):
            return client._action_name
        else:
            raise TypeError(f"client must be a Client or ActionClient: {client}")

    def get_service_type(self, client: Union[str, Client, ActionClient]) -> Any:
        if isinstance(client, str):
            client = self.clients[client]

        if isinstance(client, Client):
            return client.srv_type
        elif isinstance(client, ActionClient):
            return client._action_type
        else:
            raise TypeError(f"client must be a Client or ActionClient: {client}")

    def get_info(
        self, client: Union[str, Client, ActionClient]
    ) -> "ClientManager.ClientInfo":
        return self.clients_info[self.get_service_name(client)]

    def __callback(self, srv_name: str, future: Future):
        info = self.clients_info[srv_name]
        info.result = future.result()
        info.done.set()
