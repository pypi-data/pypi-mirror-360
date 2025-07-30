import rclpy
from rclpy.executors import SingleThreadedExecutor, MultiThreadedExecutor, Executor
from rclpy.node import Node
from rclpy.logging import get_logger
from threading import Thread
from typing import (
    Optional,
    Dict,
    Any,
    Callable,
    Set,
    Union,
)

# from builtins import ellipsis
import os
from collections import defaultdict
from ros2_geek.metaclasses import ManagedCachedMeta
from ros2_geek.topic_manager import TopicManager
from ros2_geek.client_manager import ClientManager
from inspect import signature


class NodeProMeta(ManagedCachedMeta):
    def __call__(
        self,
        node_name: str,
        namespace: Optional[str] = None,
        domain_id: Optional[int] = None,
    ):
        # same node must have the same namespace, name and domain id
        if domain_id is None:
            domain_id = self.get_env_domain_id()
        return super().__call__(node_name, namespace, domain_id)


class NodePro(Node, metaclass=NodeProMeta):
    executor_num_threads = 4
    executors: Set[Executor] = set()
    contexts: Dict[int, rclpy.Context] = {}
    _spin_threads: Dict[Executor, Thread] = {}
    __nodes: Dict[int, Dict[str, Node]] = defaultdict(dict)

    _topic_manager = None
    _client_manager = None

    def __init__(
        self,
        node_name: str,
        namespace: Optional[str] = None,
        domain_id: Optional[int] = None,
    ) -> None:
        """Create a Node with additional functions to manage multiple nodes easily.
        Args:
            node_name (str): The name of the node.
            namespace (Optional[str]): The namespace of the node. Defaults to None. If None, the node will be created without a namespace. If not None, the node will be created with the given namespace: {namespace}/{node_name}.
            domain_id (Optional[int]): The domain id of the node. Defaults to None to get the domain id from the environment. The context will be create to initialize the node by the domain id and reused if the domain id is the same.
        """
        if domain_id is None:
            domain_id = self.get_env_domain_id()
        self.domain_id = domain_id
        context = self.create_context(domain_id)
        super().__init__(node_name, context=context, namespace=namespace)
        # node_name = self.get_fully_qualified_name()
        node_name = self.get_name()
        self.__nodes[domain_id][node_name] = self
        # must be after super().__init__
        self.get_logger().info(f"Created in ROS_DOMAIN_ID: {domain_id}")
        self._spining = False

    def get_fully_qualified_name(self) -> str:
        return self.get_name()

    def new_node(
        self,
        node_name: str,
        namespace: Optional[str] = None,
        domain_id: Optional[int] = None,
    ) -> "NodePro":
        """Create a new NodePro instance with the same domain id and context if None."""
        namespace = namespace if namespace is not None else self.get_namespace()
        domain_id = domain_id if domain_id is not None else self.domain_id
        return NodePro(node_name, namespace, domain_id)

    @classmethod
    def create_context(
        cls, domain_id: Optional[int] = None, args=None
    ) -> rclpy.Context:
        """Create a context by the domain id. The context will be reused if the domain id is the same.
        Args:
            domain_id (Optional[int]): The domain id of the context. Defaults to None to get the domain id from the environment.
            args ([str]): The arguments to create the context. Defaults to None to use the default arguments. The context will be initialized using `rclpy.init` so there is no need to call it manually.
        Returns:
            rclpy.Context: The context created.
        """
        if domain_id is None:
            domain_id = cls.get_env_domain_id()
        if domain_id not in cls.contexts:
            context = rclpy.Context()
            # check if init has domain_id argument
            if "domain_id" in signature(rclpy.init).parameters:
                rclpy.init(args=args, context=context, domain_id=domain_id)
            else:
                cls.get_class_logger().warning(
                    "Domain ID arg is not supported for ROS2 foxy context"
                )
                rclpy.init(args=args, context=context)
            cls.contexts[domain_id] = context
        return cls.contexts[domain_id]

    @classmethod
    def get_default_context() -> rclpy.Context:
        return rclpy.get_default_context()

    def spin_self(
        self,
        timeout_sec: Optional[Union[float, "ellipsis"]] = ...,  # noqa: F821
        detach: bool = False,
    ) -> Optional[Thread]:
        """Spin the node.
        Args:
            timeout_sec (Optional[Union[float, "ellipsis"]]): The timeout seconds to spin the node.
                If timeout_sec is ..., the node will spin forever.
                If timeout_sec is None, the node will spin once.
            detach (bool): If True, the node will be spun in a new thread.
                If False, the node will be spun in the current thread.
        Returns:
            Optional[Thread]: The thread that is spinning the node.
                If detach is False, the thread will be None.
                If detach is True, the thread will be the thread that is spinning the node.
        """
        # TODO: add lock to avoid multiple spin_self calls
        assert self.executor is not None, f"{self} has no executor"

        def self_spin():
            self._spining = True
            if timeout_sec is ...:
                self.executor.spin()
            else:
                # self.get_logger().info(f"Spinning self once with timeout {timeout_sec}")
                self.executor.spin_once(timeout_sec)
            self._spining = False

        if not detach:
            self_spin()
        else:
            thread = Thread(target=self_spin, daemon=True)
            thread.start()
            self._spin_threads[self.executor] = thread
            return thread

    def is_spining(self) -> bool:
        return self._spining

    @classmethod
    def destroy_all_nodes(cls, stop_spin: bool = True, stop_contex: bool = False):
        if stop_spin:
            for executor in cls.executors:
                executor.shutdown()
        for di, node_dict in cls.__nodes.items():
            for node in node_dict.values():
                node.destroy_node()
        if stop_contex:
            for context in cls.contexts.values():
                context.shutdown()
            cls.contexts.clear()
        for thread in cls._spin_threads.values():
            thread.join()
        cls._spin_threads.clear()
        cls.__nodes.clear()
        cls.executors.clear()

    @staticmethod
    def get_env_domain_id() -> int:
        domain_id = os.getenv("ROS_DOMAIN_ID")
        if domain_id is not None:
            return int(domain_id)
        return 0

    @staticmethod
    def set_env_domain_id(domain_id: int):
        os.environ["ROS_DOMAIN_ID"] = str(domain_id)

    def create_topic_manager(
        self,
        max_frequency=None,
        topic_name_to_msg_type: Optional[Any] = None,
    ) -> TopicManager:
        manager = TopicManager(self, max_frequency, topic_name_to_msg_type)
        NodePro._topic_manager = manager
        return manager

    def create_client_manager(self):
        manager = self._client_manager
        if manager is None:
            NodePro._client_manager = ClientManager(self)
        return self._client_manager

    def create_client(
        self, srv_type, srv_name, *, qos_profile=None, callback_group=None
    ):
        """Create a Client or ActionClient and the client with the same name will be reused if it is not shutdown."""
        return self.client_manager.create_client(
            srv_type, srv_name, qos_profile=qos_profile, callback_group=callback_group
        )

    @classmethod
    def create_executor_for_node(cls, node: Node, num_threads: int = 1) -> Executor:
        assert node.executor is None, (
            f"{node} already has an executor {node.executor}, please use it or remove it first"
        )
        if num_threads <= 1:
            executor = SingleThreadedExecutor(context=node.context)
        else:
            executor = MultiThreadedExecutor(
                num_threads=num_threads, context=node.context
            )
        assert executor.add_node(node), f"{node} failed to add to {executor}"
        # add executor to keep the weak reference
        cls.executors.add(executor)
        return executor

    def create_executor_for_self(self, num_threads: int) -> Executor:
        return self.create_executor_for_node(self, num_threads)

    def add_to_executor(self, executor: Executor):
        assert executor.add_node(self), f"{self} failed to add to {executor}"
        # add executor to keep the weak reference
        self.executors.add(executor)

    def create_safe_timer(
        self, period_sec: float, callback: Callable, autostart=True
    ) -> Thread:
        """Create a timer using Thread and Rate, make sure do not to effect other callback.
        Now the timer can not be stopped until the node context shutdown.
        """

        def loop():
            rate = self.create_rate(1 / period_sec)
            while self.ok:
                callback()
                rate.sleep()

        thread = Thread(target=loop, daemon=True)
        if autostart:
            thread.start()
        return thread

    @classmethod
    def get_topic_manager(cls) -> Optional[TopicManager]:
        return cls._topic_manager

    @classmethod
    def get_client_manager(cls) -> Optional[ClientManager]:
        return cls._client_manager

    @property
    def topic_manager(self) -> TopicManager:
        if self._topic_manager is None:
            self.get_logger().warning(
                "TopicManager has not been created and will be created using default settings"
            )
            NodePro._topic_manager = TopicManager(self)
        return self._topic_manager

    @property
    def client_manager(self) -> ClientManager:
        if self._client_manager is None:
            self.get_logger().warning(
                "ClientManager has not been created and will be created using default settings"
            )
            NodePro._client_manager = ClientManager(self)
        return self._client_manager

    @property
    def ok(self) -> bool:
        return self.context.ok()

    @classmethod
    def get_class_logger(cls):
        return get_logger(cls.__name__)
