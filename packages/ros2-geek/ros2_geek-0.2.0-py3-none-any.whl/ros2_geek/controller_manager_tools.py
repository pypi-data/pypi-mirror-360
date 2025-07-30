import rclpy
from lifecycle_msgs.msg import State
from controller_manager import (
    list_controller_types,
    list_controllers,
    switch_controllers,
    load_controller,
    unload_controller,
    configure_controller,
    set_controller_parameters,
    set_controller_parameters_from_param_files,
    list_hardware_components,
    set_hardware_component_state,
)

from controller_manager_msgs.msg import (
    ControllerState,
    HardwareComponentState,
)
from controller_manager_msgs.srv import (
    ListHardwareComponents,
    SwitchController,
    SetHardwareComponentState,
    ConfigureController,
    LoadController,
    UnloadController,
    ListControllers,
    ListControllerTypes,
)
from typing import (
    List,
    Optional,
    Dict,
    Union,
    Any,
    Set,
    Tuple,
)
from ros2_geek.node_pro import NodePro


class ControllerManagerTools:
    def __init__(self, node: NodePro, name: str = "controller_manager") -> None:
        """Create a controller manager utils interface to manage controllers."""
        self.manager_name = name
        self._node = node
        self._activated = False
        self._controllers: Dict[str, ControllerState] = {}

    def get_logger(self):
        return self._node.get_logger().get_child(
            self.manager_name.removeprefix("/").replace("/", ".")
        )

    def activate(self) -> bool:
        if self._activated:
            return True
        if not rclpy.get_default_context().ok():
            self.get_logger().warning("The default context is not ok, try to init it")
            rclpy.init()
        # self.get_logger().info(
        #     bcolors.OKCYAN + "Waiting for the controller manager to be ready..."
        # )
        self._activated = self.switch_controllers([], [], timeout=10)
        return self._activated

    def update_controllers(self, service_timeout: Optional[float] = None):
        """Update the controllers list.
        Args:
            service_timeout (Optional[float]): The timeout to get the controllers. Defaults to None.
        """
        controllers = self.list_controllers(service_timeout)
        for controller in controllers:
            self._controllers[controller.name] = controller
        return self._controllers

    def conflicting_controllers(
        self,
        controllers: Set[str],
        references: Optional[Set[str]] = None,
        service_timeout: Optional[float] = None,
    ) -> Tuple[List[str], List[str]]:
        """Check if the controllers are conflicting with the references. Which means the
        required command interfaces of the controllers are conflicting with the claimed
        interfaces of the references (or the required command interfaces if active).
        Args:
            controllers (Set[str]): The controllers to check.
            references (Optional[Set[str]]): The references to check against. Defaults to None
            to get the current active controllers. Intersection of controllers and references
            will not be considerd.
        Returns:
            Tuple[List[str], List[str]]: The conflicting controllers. The first list is the
            controllers and the second list is the references.
        """
        # must update controllers once to get the curent claimed interfaces of the references
        updated = False
        if references is None:
            self.update_controllers(service_timeout)
            references = self._filt_active_controller_names(self._controllers.values())
            updated = True
        controllers = set(controllers)
        references = set(references)
        intersection = controllers & references
        controllers -= intersection
        references -= intersection
        conflited = ([], [])
        if references:
            if not updated:
                self.update_controllers(service_timeout)
            for controller in controllers:
                required_command_interfaces = set(
                    self._controllers[controller].required_command_interfaces
                )
                for ref in references:
                    if required_command_interfaces & set(
                        self._controllers[ref].required_command_interfaces
                    ):
                        conflited[0].append(controller)
                        conflited[1].append(ref)
                        break
        return conflited

    def list_controller_types(
        self, service_timeout: Optional[float] = None
    ) -> List[str]:
        service_timeout = 0 if service_timeout is None else service_timeout
        response: ListControllerTypes.Response = list_controller_types(
            self._node, self.manager_name, service_timeout
        )
        return response.types

    def list_controllers(
        self, service_timeout: Optional[float] = None
    ) -> List[ControllerState]:
        service_timeout = 0 if service_timeout is None else service_timeout
        response: ListControllers.Response = list_controllers(
            self._node, self.manager_name, service_timeout
        )
        return response.controller

    def list_controller_names(
        self, service_timeout: Optional[float] = None
    ) -> List[str]:
        """List all controller names."""
        controllers = self.list_controllers(service_timeout)
        if controllers is not None:
            return [controller.name for controller in controllers]

    def is_controllers_loaded(
        self, controller_names: List[str], service_timeout: Optional[float] = None
    ) -> bool:
        service_timeout = 0 if service_timeout is None else service_timeout
        loaded_controllers = set(
            controller.name for controller in self.list_controllers(service_timeout)
        )
        not_loaded = set(controller_names) - loaded_controllers
        if not_loaded:
            self.get_logger().warning(
                f"Controllers not loaded: {not_loaded}\n"
                f"Loaded controllers: {loaded_controllers}"
            )
            return False
        return True

    def list_active_controllers(
        self, service_timeout: Optional[float] = None
    ) -> Optional[List[ControllerState]]:
        controllers = self.list_controllers(service_timeout)
        if controllers is not None:
            return self._filt_active_controllers(controllers)

    def _filt_active_controllers(
        self, controllers: Set[ControllerState]
    ) -> Set[ControllerState]:
        """Filter the active controllers from the list of controllers."""
        return {
            controller for controller in controllers if controller.state == "active"
        }

    def _filt_active_controller_names(
        self, controllers: Set[ControllerState]
    ) -> Set[str]:
        """Filter the active controllers from the list of controllers."""
        return {
            controller.name
            for controller in controllers
            if controller.state == "active"
        }

    def list_active_controller_names(
        self, service_timeout: Optional[float] = None
    ) -> Optional[List[str]]:
        controllers = self.list_active_controllers(service_timeout)
        if controllers is not None:
            return [controller.name for controller in controllers]

    def switch_controllers(
        self,
        activate_controllers: List[str],
        deactivate_controllers: List[str],
        strict: bool = False,
        activate_asap: bool = True,
        timeout: float = 1.0,
        auto_deactivate: bool = False,
    ) -> bool:
        """Switch the controllers.
        Args:
            activate_controllers (List[str]): The controllers to activate.
            deactivate_controllers (List[str]): The controllers to deactivate.
            strict (bool): Whether to use strict mode. Defaults to False.
            activate_asap (bool): Whether to activate the controllers as soon as possible. Defaults to True.
            timeout (float): The timeout for the service call. Defaults to 1.0.
            auto_deactivate (bool): Whether to automatically deactivate the conflicting controllers. Defaults to False.
        Return:

        """
        if auto_deactivate:
            deactivate_controllers = list(
                set(
                    self.conflicting_controllers(
                        activate_controllers, service_timeout=timeout
                    )[1]
                    + deactivate_controllers
                )
            )
        sc: SwitchController.Response = switch_controllers(
            self._node,
            self.manager_name,
            deactivate_controllers,
            activate_controllers,
            strict,
            activate_asap,
            timeout,
        )
        return sc.ok

    def load_controller(
        self, name: str, service_timeout: Optional[float] = None
    ) -> bool:
        service_timeout = 0 if service_timeout is None else service_timeout
        lc: LoadController.Response = load_controller(
            self._node, self.manager_name, name, service_timeout
        )
        return lc.ok

    def unload_controller(
        self, name: str, service_timeout: Optional[float] = None
    ) -> bool:
        service_timeout = 0 if service_timeout is None else service_timeout
        uc: UnloadController.Response = unload_controller(
            self._node, self.manager_name, name, service_timeout
        )
        return uc.ok

    def configure_controller(
        self, name: str, service_timeout: Optional[float] = None
    ) -> bool:
        service_timeout = 0 if service_timeout is None else service_timeout
        cc: ConfigureController.Response = configure_controller(
            self._node, self.manager_name, name, service_timeout
        )
        return cc.ok

    def set_controller_parameters(
        self,
        controller_name: str,
        parameters: Union[Dict[str, Any], str],
        namespace: Optional[str] = None,
    ) -> bool:
        """Set parameters for a controller.
        namespace only works for setting parameters from a parameter file.
        """
        basic_args = (self._node, self.manager_name, controller_name)
        if isinstance(parameters, str):
            return set_controller_parameters_from_param_files(
                *basic_args,
                parameters,
                namespace,
            )
        else:
            for name, value in parameters.items():
                if not set_controller_parameters(*basic_args, name, value):
                    self.get_logger().error(
                        f"Failed to set parameters for {controller_name}: {name}:{value}"
                    )
                    return False
            return True

    def list_hardware_components(
        self, service_timeout: Optional[float] = None, check_empty_name: bool = True
    ) -> List[HardwareComponentState]:
        service_timeout = 0 if service_timeout is None else service_timeout
        while True:
            hw: ListHardwareComponents.Response = list_hardware_components(
                self._node, self.manager_name, service_timeout
            )
            if check_empty_name:
                components: List[HardwareComponentState] = hw.component
            for component in components:
                if not component.name:
                    self.get_logger().error(
                        f"Component {component} has empty name. "
                        "Please check the robot description or make sure"
                        "the controller manager is totally ready."
                    )
                    break
            else:
                break
        return hw.component

    def list_hardware_component_names(
        self, service_timeout: Optional[float] = None
    ) -> List[str]:
        """List all hardware component names."""
        components = self.list_hardware_components(service_timeout)
        return [component.name for component in components]

    def is_hardware_components_loaded(
        self, components: List[str], service_timeout: Optional[float] = None
    ) -> bool:
        service_timeout = 0 if service_timeout is None else service_timeout
        loaded_components = set(
            comp.name for comp in self.list_hardware_components(service_timeout)
        )
        not_loaded = set(components) - loaded_components
        if not_loaded:
            self.get_logger().warning(
                f"Components not loaded: {not_loaded}\n"
                f"Loaded components: {loaded_components}"
            )
            return False
        return True

    def set_hardware_components_state(self, components: List[str], state: str) -> bool:
        if not self.is_hardware_components_loaded(components):
            return False
        lable2id = {
            "active": State.PRIMARY_STATE_ACTIVE,
            "inactive": State.PRIMARY_STATE_INACTIVE,
        }
        target_state = State()
        target_state.id = lable2id[state]
        target_state.label = state
        for component in components:
            response: SetHardwareComponentState.Response = set_hardware_component_state(
                self._node, self.manager_name, component, target_state
            )
            if not (response.ok and response.state == target_state):
                if not response.ok:
                    des = "Service call failed. Wrong component name?"
                else:
                    des = f"response state: {response.state} is not equal to target state '{target_state}'."

                self.get_logger().error(f"Failed to set {component} to {state}: {des}")
                return False
        return True

    def activate_hardware_components(self, components: List[str]) -> bool:
        """Activate hardware components (auto configure first).
        components must be loaded first by the controller manager given the robot description.
        """
        return self.set_hardware_components_state(components, "active")

    def configure_hardware_components(self, components: List[str]) -> bool:
        return self.set_hardware_components_state(components, "inactive")

    @property
    def controllers(self) -> Dict[str, ControllerState]:
        return self._controllers.copy()
