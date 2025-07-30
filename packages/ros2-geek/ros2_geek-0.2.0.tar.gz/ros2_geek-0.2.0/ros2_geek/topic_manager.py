import rclpy
from rclpy.time import Time
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, CallbackGroup
from rclpy.node import Node
from rclpy.publisher import Publisher
from rclpy.logging import get_logger
from threading import Thread
from functools import partial
from typing import (
    List,
    Optional,
    Dict,
    Union,
    Any,
    Callable,
    Type,
)
import time
import re
from abc import ABC, abstractmethod
from geometry_msgs.msg import TransformStamped
import tf2_ros
from rclpy.qos import QoSProfile
from builtin_interfaces.msg import Time as TimeMsg
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    PositiveInt,
    NonNegativeFloat,
    NonNegativeInt,
)
from ros2_geek.metaclasses import ManagedSingletonMeta
from ros2_geek.async_tools import AsyncTimer
import inspect


class TopicManagerMeta(ManagedSingletonMeta):
    def __call__(self, node, max_frequency=None, type_mapping=None):
        instance = super().__call__(node, max_frequency, type_mapping)
        instance.update_params(max_frequency, type_mapping)
        return instance


class TopicMsgTypeMappingABC(ABC):
    mapping_dict = {}
    mapping_func = set()

    @classmethod
    @abstractmethod
    def get_topic_msg_type(cls, topic_name: str) -> Optional[Type[Any]]:
        raise NotImplementedError

    @staticmethod
    def is_from_template(candidate: str, template: str) -> bool:
        pattern = re.sub(r"\{[^}]+\}", r".*", template)
        pattern = f"^{pattern}$"
        return bool(re.match(pattern, candidate))

    def get(self, topic_name: str, default=...):
        # raise Exception("Not implemented")
        tp = self.get_topic_msg_type(topic_name)
        if tp is None:
            tp = self.mapping_dict.get(topic_name, None)
            if tp is None:
                for func in self.mapping_func:
                    tp = func(topic_name)
                    if tp is not None:
                        break
                else:
                    if default is ...:
                        raise KeyError(
                            f"Topic name: {topic_name} is not in the mapping"
                        )
        return tp

    def update(self, mapping: Union[dict, Callable]):
        if isinstance(mapping, dict):
            self.mapping_dict.update(mapping)
        elif callable(mapping):
            self.mapping_func.add(mapping)
        elif isinstance(mapping, TopicMsgTypeMappingABC):
            self.mapping_dict.update(mapping.mapping_dict)
            self.mapping_func.update(mapping.mapping_func)
        else:
            raise TypeError("Param mapping should be a dict or a Callable")

    # def __getitem__(self, topic_name: str):
    #     return self.get(topic_name)


class TopicManager(metaclass=TopicManagerMeta):
    # TODO: make sure thread safe
    class TopicInfo(BaseModel):
        model_config = ConfigDict(
            arbitrary_types_allowed=True,
        )
        msg: Any = None
        stamp: Time = Field(default_factory=Time)
        stamp_last: Time = Field(default_factory=Time)
        frequency: NonNegativeFloat = 0.0
        freq_ref_stamp: Time = Field(default_factory=Time)
        freq_buffer: PositiveInt = 5
        freq_bufffer_cur: NonNegativeInt = 0

    def __init__(
        self,
        node: Node,
        max_frequency: int,
        type_mapping: Optional[Union[dict, TopicMsgTypeMappingABC]] = None,
    ):
        """
        Args:
            node (Node): The node to manage the topics.
            max_frequency (int): The maximum frequency to publish the topics.
            type_mapping (Optional[Union[dict, TopicMsgTypeMappingABC]]): The type mapping for the topics.
                If not provided, the type must be provided manually.
        """
        self.get_logger().info(
            f"Creating TopicManager for {node.get_name()} with {max_frequency} Hz and {type_mapping}"
        )
        self.__node = node
        self.node_name = node.get_name()
        # subscribe control
        self._sub_handle = {}
        self._sub_info: Dict[str, TopicManager.TopicInfo] = {}
        self._sub_callbacks: Dict[str, list] = {}
        # publish control
        self._pub_topic: Dict[str, Publisher] = {}
        self._pub_msg = {}
        self._pub_freq = {}
        self._pub_duration = {}
        self._pub_duration_cur = {}
        self._pub_same_judger = {}
        self._pub_timer = None
        self._pub_functions: set = set()
        self._atimer = None
        self._configure(max_frequency, type_mapping)
        self._static_tfer = None

    @classmethod
    def get_logger(cls):
        return get_logger(cls.__name__)

    def _listen_to(
        self,
        topic_name: str,
        msg_type: Optional[Any],
        callback: Callable,
        qos_profile: int,
        callback_group: CallbackGroup = MutuallyExclusiveCallbackGroup(),
    ) -> bool:
        if msg_type is None:
            msg_type = self.type_mapping.get(topic_name)
            assert msg_type is not None, f"msg_type is not provided for {topic_name}"

        # TODO: why using thread here?
        def create_sub():
            self._sub_handle[topic_name] = self.__node.create_subscription(
                msg_type,
                topic_name,
                callback,
                qos_profile,
                callback_group=callback_group,
            )

        thread = Thread(target=create_sub)
        thread.start()
        thread.join()
        return True

    def update(
        self, topic_names: Union[str, List[str]], timeout_sec: Optional[float] = None
    ):
        self.get_logger().info(f"Updating {topic_names}")
        updated = False

        def spin_executor():
            try:
                while not updated:
                    rclpy.spin_once(
                        self.__node, executor=self.__node.executor, timeout_sec=0.001
                    )
            except ValueError as e:
                assert str(e) == "generator already executing", e

        thread = Thread(target=spin_executor)
        msgs = self.wait_for_msg(topic_names, timeout_sec)
        updated = True
        if thread.is_alive():
            thread.join()
        self.get_logger().info(f"Updated {topic_names}")
        return msgs

    def listen_to(
        self,
        topic_names: Union[str, List[str]],
        msg_type: Optional[Any] = None,
        callbacks: Optional[Union[Callable, List[Callable]]] = None,
        qos_profile: int = 1,
        callback_group: CallbackGroup = MutuallyExclusiveCallbackGroup(),
    ):
        if isinstance(topic_names, str):
            topic_names = [topic_names]

        if (callbacks is None) or callable(callbacks):
            callbacks = [callbacks for _ in topic_names]
        else:
            assert len(callbacks) == len(topic_names), "Callbacks should match topics"

        for topic_name, callback in zip(topic_names, callbacks):
            assert isinstance(topic_name, str), (
                f"Topic name should be a string: {topic_name}"
            )
            if self.is_listening(topic_name):
                self.get_logger().warning(f"{topic_name} has already been listened")
                continue
            self._sub_info[topic_name] = TopicManager.TopicInfo()
            if callback is not None:
                self.add_sub_callback(topic_name, callback)

            def _callback(topic_name, msg):
                info = self._sub_info[topic_name]
                info.msg = msg
                info.stamp_last = info.stamp
                info.stamp = self.__node.get_clock().now()
                info.freq_bufffer_cur += 1
                if info.freq_bufffer_cur == 1:
                    info.freq_ref_stamp = info.stamp
                elif info.freq_bufffer_cur >= info.freq_buffer:
                    info.frequency = (
                        info.freq_buffer
                        / (info.stamp - info.stamp_last).nanoseconds
                        * 1e9
                    )
                    info.freq_bufffer_cur = 0
                sub_callbacks = self._sub_callbacks.get(topic_name, None)
                if sub_callbacks:
                    for cb in sub_callbacks:
                        cb(msg)

            self._sub_info[topic_name].stamp = self.__node.get_clock().now()
            self._listen_to(
                topic_name,
                msg_type,
                partial(_callback, topic_name),
                qos_profile,
                callback_group,
            )

    def add_sub_callback(self, topic_name: str, callback: Callable):
        if topic_name in self._sub_callbacks:
            self._sub_callbacks[topic_name].append(callback)
        else:
            self._sub_callbacks[topic_name] = [callback]

    def wait_for_msg(
        self,
        topic_names: Union[str, List[str]],
        timeout_sec: Optional[float] = None,
        interval: float = 0.05,
    ) -> Optional[Dict[str, Any]]:
        """Wait for the listened topic messages by the given topic names.
        return the listened messages and can wait for the newest messages.
        """
        start = time.time()
        if isinstance(topic_names, str):
            topic_names = [topic_names]
        msgs = {}
        for topic_name in topic_names:
            info = self._sub_info.get(topic_name, None)
            if info is None:
                self.get_logger().warning(f"{topic_name} is not being listened")
                return None
            last_time = info.stamp
            while last_time == info.stamp:
                if timeout_sec is not None:
                    if time.time() - start > timeout_sec:
                        self.get_logger().error(f"Timeout waiting for {topic_names}")
                        return None
                time.sleep(interval)
            msgs[topic_name] = info.msg
        return msgs

    def get_topic_msg(self, topic_name: str, wait: Optional[float] = 0) -> Any:
        """Get the listened topic message from the given topic name.
        Args:
            topic_name (str): The topic name to get the message.
            wait (Union[float, None]): The time to wait for the next message.
                Wait forever if wait is None. Default to 0.
                If wait is 0, the function will return the last message.
        Returns:
            Any: The message of the topic.
        """
        if wait != 0:
            self.wait_for_msg(topic_name, wait)
        info = self._sub_info.get(topic_name, None)
        if info is None:
            self.get_logger().warning(f"{topic_name} is not being listened")
            return 0
        return info.msg

    def get_topic_stamp(self, topic_name: str) -> TimeMsg:
        """Get the stamp of the listened topic message from the given topic name."""
        info = self._sub_info.get(topic_name, None)
        if info is None:
            self.get_logger().warning(f"{topic_name} is not being listened")
            return 0
        return info.stamp.to_msg()

    def stop_listen(self, topic_names: Union[str, List[str]]) -> bool:
        if isinstance(topic_names, str):
            topic_names = [topic_names]
        success = True
        for topic_name in topic_names:
            if self.__node.destroy_subscription(self._sub_handle[topic_name]):
                self._sub_handle.pop(topic_name)
                self._sub_info.pop(topic_name)
            else:
                success = False
        return success

    def is_listening(self, topic_name) -> bool:
        return topic_name in self._sub_handle

    def add_topic_monitor(self, topic_name: str, callback: Callable, frequency: float):
        """Add a monitor to the topic with the given frequency.
        The monitor will pass the message and its monitored information to the callback
        at the given frequency.
        """

        self.__node.create_timer(
            1 / frequency,
            lambda: callback(self._sub_info[topic_name]),
        )

    def _publish_to(
        self,
        topic_name: str,
        msg_type: Optional[Any] = None,
        frequency: float = 0,
        duration: float = 0,
        qos_profile: int = 1,
    ) -> Publisher:
        if frequency > self._max_frequency:
            self.get_logger().warning(
                f"Frequency {frequency} is too high, set to {self._max_frequency}"
            )
            frequency = self._max_frequency
        if msg_type is None:
            msg_type = self.type_mapping.get(topic_name)
        if duration > 0:
            pub_cnt = duration * frequency
        else:
            pub_cnt = -1
        self._pub_duration[topic_name] = pub_cnt
        self._pub_duration_cur[topic_name] = 0  # TODO: set to pub_cnt?
        puber = self.__node.create_publisher(msg_type, topic_name, qos_profile)
        self._pub_topic[topic_name] = puber
        self._pub_freq[topic_name] = frequency

        def publish_msg():
            msg = self._pub_msg.get(topic_name, None)
            if msg is not None:
                cur = self._pub_duration_cur[topic_name]
                # self.get_logger().info(f"Publishing {topic_name} : {msg}")
                # cur < 0 will publish forever
                if cur != 0:
                    self._pub_topic[topic_name].publish(msg)
                if cur > 0:
                    self._pub_duration_cur[topic_name] -= 1

        if frequency > 0:
            self._atimer.add(1 / frequency, topic_name, publish_msg)
            if self._pub_timer is None:
                # self.get_logger().info("Start publishing timer")
                self._pub_timer = self.__node.create_timer(
                    1 / self._max_frequency,
                    self._atimer.update,
                    MutuallyExclusiveCallbackGroup(),
                )

        return puber

    def is_publishing(self, topic_name: str) -> bool:
        return topic_name in self._pub_topic

    def publish_to(
        self,
        topic_names: Union[str, List[str]],
        msg_type: Optional[Any] = None,
        frequency: float = 0,
        duration: float = 0,
        qos_profile: int = 1,
        same_judger: Optional[Callable] = None,
    ) -> Dict[str, Publisher]:
        """Publish topics.
        Args:
            topic_names (Union[str, List[str]): The topic names to publish.
            msg_type (Optional[Any]): The message type to publish.
            frequency (float): The frequency (Hz) to publish the message in a loop.
                0 means publish only when 'set_pub_msg' is called.
            duration (float): The duration (s) to publish the message after a new msg is set at the given positive frequency. 0 means publish forever when frequency is positive.
            qos_profile (int): The quality of service profile to publish the message.
            same_judger (Optional[Callable]): The judger to determine if the message is new (need to publish).
                For more details, please refer to 'set_pub_same_msg_judger'.

        Returns:
            Dict[str, Publisher]: The publishers to the topics corresponding to the topic names.
        """
        # TODO: support publish groups to avoid blocking pub
        if isinstance(topic_names, str):
            topic_names = [topic_names]
        pubers = {}
        for topic_name in topic_names:
            if self.is_publishing(topic_name):
                self.get_logger().warning(f"{topic_name} is already being published")
                continue
            pubers[topic_name] = self._publish_to(
                topic_name, msg_type, frequency, duration, qos_profile
            )
            self.set_pub_same_msg_judger(topic_name, same_judger)
        return pubers

    def set_pub_same_msg_judger(
        self, topic_name: str, judger: Optional[Union[Callable, str]] = None
    ) -> Callable:
        """Set the judger to determine if the message is the same as the previous one.
        Args:
            topic_name (str): The topic name to set the judger.
            judger (Optional[Union[Callable, str]]): The judger to determine if the message is the same as the previous one. The judger will return True when the msg is considered the same, otherwise False. The judger can be a callable, 'any', 'same' or None. 'any' means never publish the message while None means always publish the message. 'same' means publish the message only when it is different from the previous one.

        Returns:
            Callable: The judger function.
        """
        judger_dict = {
            None: lambda msg: False,
            "any": lambda msg: True,
            "same": lambda msg: msg == self._pub_msg.get(topic_name, None),
        }
        judger = judger_dict.get(judger, judger)
        assert callable(judger), (
            f"Judger should be a callable or one of: {judger_dict.keys()}, but got {judger}"
        )
        self._pub_same_judger[topic_name] = judger
        return judger

    def add_pub_function(
        self,
        function: Callable,
        frequency: Optional[float] = None,
        handle_name: Optional[str] = None,
    ) -> bool:
        if handle_name is None:
            handle_name = "__pub_func__"
        elif handle_name in self._pub_functions:
            self.get_logger().warning(
                f"{handle_name} is already added, please remove it first"
            )
            return False
        self._pub_functions.add(handle_name)
        if frequency is None:
            frequency = self._max_frequency
        self._atimer.add(1 / frequency, handle_name, function)
        return True

    def remove_pub_function(self, handle_name: str) -> bool:
        if handle_name not in self._pub_functions:
            self.get_logger().warning(f"{handle_name} is not added")
            return False
        self._atimer.remove(handle_name)
        return True

    def set_pub_msg(self, topic_name: str, msg: Any):
        self._pub_msg[topic_name] = msg
        assert topic_name in self._pub_topic, f"{topic_name} is not being published"
        # self.get_logger().info(f"Set msg to {topic_name} : {msg}")
        if not self._pub_same_judger[topic_name](msg):
            if self._pub_freq[topic_name] == 0:
                self._pub_topic[topic_name].publish(msg)
            else:
                self._pub_duration_cur[topic_name] = self._pub_duration[topic_name]

    def stop_pub(self, topic_names: Union[str, List[str]], destroy: bool = False):
        if isinstance(topic_names, str):
            topic_names = [topic_names]
        for topic in topic_names:
            if destroy:
                self.__node.destroy_publisher(self._pub_topic[topic])
                self._pub_topic.pop(topic)
                self._pub_freq.pop(topic)
                self._pub_duration.pop(topic)
                self._pub_duration_cur.pop(topic)
                self._atimer.remove(topic_names)
            else:
                self.set_pub_msg(topic, None)

    def broadcast_static_tf(
        self,
        transform: Union[TransformStamped, List[TransformStamped]],
        qos_profile: Optional[Union[QoSProfile, int]] = None,
    ):
        """Broadcast static transform.
        Args:
            transform (TransformStamped): The transform to broadcast.
            qos_profile (QoSProfile): The quality of service profile to publish the message.
        """
        if self._static_tfer is None:
            self._static_tfer = tf2_ros.StaticTransformBroadcaster(
                self.__node, qos_profile
            )
        self._static_tfer.sendTransform(transform)

    def _configure(
        self,
        max_frequency: int,
        type_mapping: Optional[Union[dict, TopicMsgTypeMappingABC]] = None,
    ):
        assert max_frequency > 0, (
            f"Max frequency should be positive, but got {max_frequency}"
        )
        assert not inspect.isclass(type_mapping), (
            "Type mapping should not be a class, please use a instance"
        )
        self._max_frequency = max_frequency
        self.type_mapping = {} if type_mapping is None else type_mapping
        self._atimer = AsyncTimer(self._max_frequency)

    def update_params(
        self,
        max_frequency: Optional[int] = None,
        type_mapping: Optional[Union[dict, TopicMsgTypeMappingABC]] = None,
    ):
        if max_frequency is not None and self._max_frequency < max_frequency:
            if self._pub_timer is not None:
                self._pub_timer.timer_period_ns = 1e9 / max_frequency
            self._max_frequency = max_frequency
            self._atimer.reset_frequency(max_frequency)
            self.get_logger().info(f"Max frequency updated to {max_frequency}")
        if type_mapping is not None:
            if isinstance(self.type_mapping, dict):
                type_mapping.update(self.type_mapping)
                self.type_mapping = type_mapping
            else:
                self.type_mapping.update(type_mapping)
            self.get_logger().info(f"Type mapping updated by {type_mapping}")
        return max_frequency, type_mapping

    @property
    def topics_sub(self) -> List[str]:
        return list(self._sub_handle.keys())

    @property
    def topics_pub(self) -> List[str]:
        return list(self._pub_topic.keys())

    @property
    def max_frequency(self) -> int:
        return self._max_frequency
