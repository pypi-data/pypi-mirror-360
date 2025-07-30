import rclpy
import rclpy.clock
from rclpy.logging import get_logger
from threading import Event
from pathlib import Path
from pprint import pprint
from sensor_msgs.msg import JointState
from ament_index_python.packages import get_package_share_directory
import importlib.util
from typing import (
    List,
    Optional,
    Dict,
    Union,
    Any,
    Hashable,
    Set,
    Tuple,
)
import os
import re
import yaml
from collections import defaultdict
import subprocess
from pydantic import BaseModel
from enum import Enum
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from ros2_geek.topic_manager import TopicManager
from ros2_geek.node_pro import NodePro


def get_parent_class(super_instance: super):
    mro = super_instance.__self__.__class__.__mro__
    parent_class = mro[mro.index(super_instance.__thisclass__) + 1]
    return parent_class


class LifecycleStateLabel(str, Enum):
    UNCONFIGURED = "unconfigured"
    INACTIVE = "inactive"
    ACTIVE = "active"

    def __str__(self):
        return self.value


class NodeConfig(BaseModel):
    node_name: str
    namespace: str = "/"
    domain_id: Optional[int] = None

    def create_node_pro(self):
        return NodePro(self.node_name, self.namespace, self.domain_id)


def get_file_abs_path(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    return os.path.join(package_path, file_path)


def load_file(package_name, file_path):
    try:
        with open(get_file_abs_path(package_name, file_path), "r") as file:
            return file.read()
    except EnvironmentError:
        return None


def load_yaml(package_name, file_path) -> Optional[dict]:
    try:
        with open(get_file_abs_path(package_name, file_path), "r") as file:
            return yaml.safe_load(file)
    except EnvironmentError:
        return None


def save_yaml(package_name: str, file_path: str, data: dict) -> str:
    """Save the data to the target yaml file and return the absolute file path"""
    absolute_file_path = get_file_abs_path(package_name, file_path)
    with open(absolute_file_path, "w") as file:
        yaml.dump(data, file)
    return absolute_file_path


def load_python(file_path: str, module_name: str = "example_module") -> Any:
    """Load a python file as a module."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dynamic_import(module_name, attribute_name):
    module = importlib.import_module(module_name)
    attribute = getattr(module, attribute_name)
    return attribute


class YamlModifier(object):
    def __init__(self, input_file: str, output_file: Optional[str] = None) -> None:
        self.input_file = input_file
        self.output_file = output_file
        assert os.path.exists(input_file), f"File not found: {input_file}"
        with open(input_file, "r") as file:
            self.config: dict = yaml.safe_load(file)

    def update(self, params: dict):
        def recursive_update(config, params):
            for key, value in params.items():
                if isinstance(value, dict):
                    if key in config and isinstance(config[key], dict):
                        recursive_update(config[key], value)
                    else:
                        config[key] = value
                else:
                    if key in config:
                        config[key] = value

        recursive_update(self.config, params)

    def pop_keys(self, params: Union[dict, List[Union[str, dict]]]):
        params = params.copy()
        if not isinstance(params, dict):
            for key in params.copy():
                if isinstance(key, dict):
                    continue
                self.config.pop(key, None)
                params.remove(key)
        else:
            params = [params]

        def recursive_pop(config, params: dict):
            for key, value in params.items():
                # print(f"key: {key}, value: {value}")
                if isinstance(value, dict):
                    recursive_pop(config[key], value)
                else:
                    assert isinstance(config[key], dict), "Value must be a dict"
                    for k in value:
                        config[key].pop(k, None)

        for param_dict in params:
            assert isinstance(param_dict, dict), "Value must be a dict"
            recursive_pop(self.config, param_dict)

    def remove_values(self, params: dict):
        def recursive_remove(config, params):
            for key, value in params.items():
                if isinstance(value, dict):
                    recursive_remove(config[key], value)
                else:
                    assert isinstance(config[key], list), "Value must be a list"
                    for k in value:
                        config[key].remove(k)

        recursive_remove(self.config, params)

    def show(self):
        pprint(self.config)

    def save(self):
        file_path = self.input_file
        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path).replace(".yaml", "_modified.yaml")
        output_file = self.output_file or f"{file_dir}/{file_name}"
        with open(output_file, "w") as file:
            yaml.dump(self.config, file)


def get_joint_values_by_names(
    joint_states: JointState, names: List[str], field: str = "position"
) -> List[float]:
    assert names, "names must not be empty"
    joint_values = []
    no_joints = set(names) - set(joint_states.name)
    if no_joints:
        get_logger("get_joint_values_by_names").warning(
            f"Joint names not found in joint_states: {no_joints}"
        )
    else:
        if joint_states is not None:
            for name in names:
                index = joint_states.name.index(name)
                joint_values.append(getattr(joint_states, field)[index])
    return joint_values


def get_key_by_value(d: dict, value: Any) -> Optional[Hashable]:
    """Get key by value from a dictionary (only first matching)."""
    try:
        return list(d.keys())[list(d.values()).index(value)]
    except ValueError:
        return None


def get_sub_dict_by_key(d: dict, keys: List[Hashable]) -> dict:
    return {k: d[k] for k in keys if k in d}


def get_sub_dict_by_value(d: dict, values: List[Any]) -> dict:
    return {k: v for k, v in d.items() if v in values}


def repeated2dict(keys: list, values: list) -> dict:
    return {k: v for k, v in zip(keys, values)}


def group_repeated_by_key(keys: list, values: list) -> dict:
    result = defaultdict(list)
    for key, value in zip(keys, values):
        result[key].append(value)
    return result


def group_repeated_by_value(keys: list, values: list) -> dict:
    result = defaultdict(list)
    for key, value in zip(keys, values):
        result[value].append(key)
    return result


def group_dict_by_value(dic: dict) -> dict:
    result = defaultdict(list)
    for key, value in dic.items():
        result[value].append(key)
    return result


class NameCaseUtils:
    @staticmethod
    def is_pascal_case(name):
        """also known as UpperCamelCase"""
        pattern = r"^[A-Z][a-zA-Z0-9]*$"
        return bool(re.match(pattern, name))

    @staticmethod
    def is_snake_case(name):
        """snake_case"""
        pattern = r"^[a-z][a-z0-9_]*$"
        return bool(re.match(pattern, name))

    @classmethod
    def pascal2screaming_snake(cls, name: str) -> str:
        """Convert PascalName to SCREAMING_SNAKE_CASE name"""
        assert cls.is_pascal_case(name), f"{name} is not pascal case"
        if not any(c.islower() for c in name):
            return name.upper()
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        result = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
        return result.upper()

    @staticmethod
    def screaming_snake2pascal(name: str) -> str:
        """Convert SCREAMING_SNAKE_CASE name to PascalName"""
        assert name.isupper(), f"{name} is not screaming snake case"
        return "".join([word.capitalize() for word in name.split("_")])

    @staticmethod
    def snake2pascal(name: str) -> str:
        """Convert snake_name to PascalName"""
        assert name.islower(), f"{name} is not snake case"
        return "".join([word.capitalize() for word in name.split("_")])

    @staticmethod
    def screaming_snake2snake(name: str) -> str:
        assert name.isupper(), f"{name} is not screaming snake case"
        return name.lower()


def simple_cmd_run(command: str) -> Any:
    try:
        result = subprocess.run(
            command, shell=True, check=True, text=True, capture_output=True
        )
    except subprocess.CalledProcessError as e:
        result = e
    return result


def parse_ros_path(path: str) -> tuple:
    """Parse the package name and the relative path from the given path"""
    assert not path.startswith("/"), "must be a relative path"
    package, *paths = path.split("/")
    return package, "/".join(paths)


def reorder_lists(new_order, *lists):
    first_list = lists[0]
    index_dict = {value: index for index, value in enumerate(first_list)}
    for item in new_order:
        if item not in index_dict:
            raise ValueError(f"item {item} is not in the first list")

    sorted_indices = [index_dict[item] for item in new_order]

    sorted_lists = []
    for lst in lists:
        if not lst:
            sorted_lists.append([])
        else:
            sorted_subset = [lst[i] for i in sorted_indices]
            sorted_lists.append(sorted_subset)

    return sorted_lists


def relative_path_between(path1: Path, path2: Path) -> Path:
    """Returns path1 relative to path2."""
    path1 = path1.absolute()
    path2 = path2.absolute()
    try:
        return path1.relative_to(path2)
    except ValueError:  # most likely because path1 is not a subpath of path2
        common_parts = Path(os.path.commonpath([path1, path2])).parts
        return Path(
            "/".join(
                [".."] * (len(path2.parts) - len(common_parts))
                + list(path1.parts[len(common_parts) :])
            )
        )


def collect_diagnoustics(
    hardware_ids: Set[str],
    topic_manager: TopicManager,
    topic_name: str,
    level: int = DiagnosticStatus.WARN,
    timeout_sec: Optional[float] = None,
) -> Dict[str, Dict[int, Set[Tuple[float, str, Dict[str, str]]]]]:
    """get the hw abnormal status from the corresponding diagnostics topic"""
    diags_comp = defaultdict(lambda: defaultdict(set))
    received_all = Event()
    now_stamp = rclpy.clock.Clock().now()

    def process_status(msg: DiagnosticArray):
        # ensure the stamp is newer than now
        if msg.header.stamp.sec > now_stamp.to_msg().sec:
            status: List[DiagnosticStatus] = msg.status
            for s in status:
                if s.level >= level:
                    values: List[KeyValue] = s.values
                    diags_comp[s.hardware_id][s.level].add(
                        (msg.header.stamp, s.message, {v.key: v.value for v in values})
                    )
            if set(hardware_ids) == set(diags_comp.keys()):
                received_all.set()

    topic_manager.listen_to(
        topic_name,
        DiagnosticArray,
        callbacks=process_status,
        qos_profile=len(hardware_ids),
    )

    # wait to collect all the diags
    received_all.wait(timeout_sec)
    topic_manager.stop_listen(topic_name)
    return diags_comp


# from https://stackoverflow.com/a/287944
class bcolors:
    MAGENTA = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
