from rclpy.logging import get_logger
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch import (
    LaunchService,
    LaunchDescription,
    LaunchDescriptionEntity,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
import threading
from multiprocessing import Process
from ament_index_python.packages import get_package_share_directory
from typing import (
    List,
    Optional,
    Dict,
    Union,
    Coroutine,
    Any,
    Iterable,
)
import os
import signal
from ros2_geek.utils import bcolors
from ros2_geek.metaclasses import ManagedSingletonMeta


class Launcher:
    def __init__(
        self,
        argv: Optional[Iterable[str]] = None,
        noninteractive: bool = True,
        debug: bool = False,
    ) -> None:
        self._launch_service = LaunchService(
            argv=argv, noninteractive=noninteractive, debug=debug
        )
        self._launch_process = None
        self._logger = get_logger(Launcher.__name__)

    def launch(
        self,
        launch_description: LaunchDescription,
        launch_configurations: Optional[Dict[str, Any]] = None,
        argv: Optional[List[str]] = None,
        async_run: bool = False,
        new_process: bool = True,
        daemon: bool = True,
    ) -> Optional[Union[Coroutine, int, Process]]:
        assert self._launch_process is None or not self._launch_process.is_alive(), (
            "Launch process are already running"
        )

        def _launch():
            launch_service = self._launch_service
            if argv is not None:
                launch_service.context.argv = argv
            if launch_configurations is not None:
                launch_service.context.launch_configurations.update(
                    launch_configurations
                )
            launch_service.include_launch_description(launch_description)
            # This should only ever be run from the main thread
            # so usually Process will be used
            if async_run:
                raise NotImplementedError("async_run is not implemented")
                return launch_service.run_async()
            else:
                launch_service.run()

        if new_process:
            self._launch_process = Process(target=_launch, daemon=daemon)
            self._launch_process.start()
            return self._launch_process
        else:
            if threading.current_thread() is threading.main_thread():
                return _launch()
            else:
                raise RuntimeError("Launch must be run in the main thread")

    def include(
        self,
        launch_description: LaunchDescription,
    ):
        self._launch_service.include_launch_description(launch_description)

    def wait(self):
        assert self._launch_process is not None, "Launch is not running in subprocess"
        self._launch_process.join()

    def shutdown(self, wait: bool = True, terminate: bool = False):
        self._launch_service.shutdown()
        if self._launch_process is not None:
            if terminate:
                # self._launch_process.terminate()
                sig = signal.SIGKILL
            else:
                sig = signal.SIGINT
            os.kill(self._launch_process.pid, sig)
            if wait:
                self._launch_process.join()

    @staticmethod
    def get_launch_description_source(
        pkg_name: str, launch_file_path: str
    ) -> PythonLaunchDescriptionSource:
        return PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory(pkg_name),
                launch_file_path,
            )
        )

    @classmethod
    def get_include_launch_description(
        cls,
        pkg_name: str,
        launch_file_path: str,
        launch_arguments: Optional[dict] = None,
    ) -> IncludeLaunchDescription:
        if launch_arguments is not None:
            launch_arguments = launch_arguments.items()
        return IncludeLaunchDescription(
            cls.get_launch_description_source(pkg_name, launch_file_path),
            launch_arguments=launch_arguments,
        )

    @staticmethod
    def merge_entities(
        launch_description_sources: List[PythonLaunchDescriptionSource],
    ) -> List[LaunchDescriptionEntity]:
        entities = []
        for desc in launch_description_sources:
            ent = desc.try_get_launch_description_without_context()
            assert ent is not None, f"{desc.location} not found"
            entities.extend(ent.entities)
        return entities

    @classmethod
    def get_source_declared_arguments(
        cls,
        launch_description_sources: List[Union[PythonLaunchDescriptionSource, str]],
    ) -> List[DeclareLaunchArgument]:
        args = []
        for desc in launch_description_sources:
            if isinstance(desc, str):
                desc = cls.get_launch_description_source(*desc.split("/", 1))
            ent = desc.try_get_launch_description_without_context()
            assert ent is not None, f"{desc.location} not found"
            args.extend(ent.get_launch_arguments())
        return args

    def get_logger(self):
        return self._logger


class LaunchManager(metaclass=ManagedSingletonMeta):
    def __init__(self):
        self._launcher_cfgs: Dict[str, tuple] = {}
        self._launchers: Dict[str, Launcher] = {}

    def configure(
        self,
        name: str,
        argv: Optional[Iterable[str]] = None,
        noninteractive: bool = True,
        debug: bool = False,
    ):
        """configure before launch"""
        self._launcher_cfgs[name] = (argv, noninteractive, debug)

    def include(self, name: str, launch_description: LaunchDescription):
        self._launchers[name].include(launch_description)

    def launch(
        self,
        name: Optional[str],
        target: Union[str, List[str]],
        launch_arguments: Optional[Union[Dict[str, Any], List[dict]]] = None,
        include: bool = False,
        async_run: bool = False,
        new_process: bool = True,
        wait: bool = False,
        force: int = 0,
    ) -> Optional[Union[Coroutine, int, Process]]:
        """Launch the target launch files.
        Args:
            name (Optional[str]): The name of the launch, if it is already launched, the launch files should be included by set `include` to True.
            target (Union[str, List[str]]): The target launch files to launch.
            launch_arguments (Optional[Union[Dict[str, Any], List[dict]]]): The arguments to launch the target launch files. Defaults to None.
            include (bool): Whether to include the target launch files if the name is already launched. Defaults to False.
            async_run (bool): Whether to run the launch in async mode. Defaults to False.
            new_process (bool): Whether to run the launch in a new process. Defaults to True.
        Returns:
            Optional[Union[Coroutine, int, Process]]: The result of the launch.

        """
        launched = False
        if name in self._launchers:
            if force == 1:
                pass
            if force:
                self.get_logger().info(f"Force shutdown {name}")
                self.shutdown(name)
            elif not include:
                self.get_logger().warning(
                    f"Launch-skip: {name} is already launched, you can use `include` method or argument"
                    "to process additional launch files with the same name"
                    "or you can `shutdown` and launch again with all targets"
                )
                return
            launched = True

        self.get_logger().info(f"Launching {name}: {target}")

        if isinstance(target, str):
            target = [target]
            launch_arguments = [launch_arguments]
        # assert len(target) == len(
        #     launch_arguments
        # ), f"The length of target launch files and arguments must be the same"
        # try:
        included = []
        for t, args in zip(target, launch_arguments):
            t: str
            pkg_name, launch_file_path = t.split("/", 1)
            included.append(
                Launcher.get_include_launch_description(
                    pkg_name, launch_file_path, args
                )
            )

        launch_description = LaunchDescription(included)
        # except Exception as e:
        #     self.get_logger().error(f"{e}")
        #     return

        if launched:
            self._launchers[name].include(launch_description)
        else:
            self._launchers[name] = Launcher(*self._launcher_cfgs.get(name, ()))
            return self._launchers[name].launch(
                launch_description, None, None, async_run, new_process, not wait
            )

        if wait:
            self.get_logger().info(
                bcolors.OKCYAN + f"Waiting for {name} to be launched"
            )
            self.wait(name)

    def wait(self, name: str):
        self._launchers[name].wait()

    def shutdown(self, name, wait: bool = True, terminate: bool = False):
        self._launchers.pop(name).shutdown(wait, terminate)

    def get_logger(self):
        return get_logger(self.__class__.__name__)
