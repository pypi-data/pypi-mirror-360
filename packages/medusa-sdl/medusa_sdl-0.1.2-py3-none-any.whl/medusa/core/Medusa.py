__author__ = "Felix Strieth-Kalthoff (@felix-s-k) Han Hao (@clascclon)"

import time
from typing import List, Tuple, Optional, Union, Protocol, runtime_checkable
from pathlib import Path
from logging import Logger, getLogger
import importlib.resources
from math import ceil

from .MedusaGraph import MedusaGraph
from .vessel import Vessel
from ..utils import load_json
from ..utils import GraphLayoutError, PathError, HardwareError
# from matterlab_hotplates import HeatStirPlate
# from matterlab_valves import SwitchingValve
# from matterlab_pumps import SyringePump
# from matterlab_relays import Relay
from medusa.core.driver_loader import get_driver, get_classes_by_category, get_classes_by_category_or_name, DEVICE_REGISTRY

class Medusa(object):
    """
    Parent class for the Medusa platform.

    Public methods to be used:

        transfer_liquid(source: str, target: str, pump: str, volume: float)

        heat_stir(vessel: str, heat: bool = False, temperature: float = 20.0, stir: bool = False, rpm: float = 0.0)
    """
    
    # Define the resource path for the default graph and default settings file
    # These paths are relative to the root of the installed package
    # DEFAULT_GRAPH_RESOURCE_PATH = 'defaults'
    # DEFAULT_GRAPH_FILENAME = 'demo_exp_mini.json' # Using demo_exp_mini.json as the default graph
    DEFAULT_SETTINGS_RESOURCE_PATH = 'medusa.defaults'
    DEFAULT_SETTINGS_FILENAME = 'GraphDefaults.json'
 
    def __init__(
            self,
            graph_layout: Path,
            defaults_dir: Optional[Path]=None,  
            logger: Optional[Logger] = None
    ):
        self.logger = logger if logger is not None else getLogger(__name__)
        self._graph = MedusaGraph.from_json(graph_layout, logger=self.logger)
        self._load_setting(defaults_dir=defaults_dir)       
        self._PUMP_CLASS     = get_classes_by_category_or_name("Pump")
        self._VALVE_CLASS    = get_classes_by_category_or_name("Valve")
        self._HOTPLATE_CLASS = get_classes_by_category_or_name("Hotplate")
        self._RELAY_CLASS    = get_classes_by_category_or_name("Relay")
        self._SHAKER_CLASS   = get_classes_by_category_or_name("Shaker")
        self._PUMP_VALVE_CLASS   = self._PUMP_CLASS + self._VALVE_CLASS 

    def _load_setting(self, defaults_dir):
        """
        load the default graph setting from GraphDefaults.json
        verify the content, then load to self._defaults
        """
        if defaults_dir is None:
            defaults_dir = self.DEFAULT_SETTINGS_RESOURCE_PATH
        self.logger.info(f"Loading default settings from package resources: {defaults_dir}/{self.DEFAULT_SETTINGS_FILENAME}")
        try:
            default_settings_resource = importlib.resources.files(defaults_dir) / self.DEFAULT_SETTINGS_FILENAME

            if not default_settings_resource.is_file():
                 raise FileNotFoundError(f"Default settings resource not found: {default_settings_resource}")

            # default_settings = load_json(default_settings_resource)
            # self._graph.validate_nodes_exist(list(default_settings.values()))
            raw_settings = load_json(default_settings_resource)
            resolved_defaults = {}

            for key, val in raw_settings.items():
                # exact match
                if val in self._graph.nodes:
                    resolved_defaults[key] = val
                    continue

                wc_matches = [
                    n for n, d in self._graph.nodes(data=True)
                    if self._graph._get_node_category(d["object"]).lower() == val.lower()
                ]
                if wc_matches:
                    resolved_defaults[key] = wc_matches[0]
                    self.logger.info(f"Default '{key}' matched category '{val}'. Using node '{wc_matches[0]}'.")
                    continue

                # substring match
                sub_matches = [
                    n for n in self._graph.nodes
                    if val.lower() in n.lower()
                ]
                if sub_matches:
                    resolved_defaults[key] = sub_matches[0]
                    self.logger.info(f"Default '{key}' matched name substring '{val}'. Using node '{sub_matches[0]}'.")
                    continue

                # wildcard match
                if val.endswith("*"):
                    prefix = val[:-1]
                    wc_matches = [n for n in self._graph.nodes if n.startswith(prefix)]
                    if wc_matches:
                        resolved_defaults[key] = wc_matches[0]
                        self.logger.info(f"Default '{key}' matched wildcard '{val}'. Using node '{wc_matches[0]}'.")
                    continue
                
                self.logger.error(f"An unexpected error occurred loading default settings.")
                raise GraphLayoutError(f"Error loading default settings")
            self._graph.validate_nodes_exist(list(resolved_defaults.values()))
            self._defaults = resolved_defaults

        except FileNotFoundError as e:
            self.logger.error(f"Failed to load default settings resource: {e}")
            raise GraphLayoutError(f"Default settings resource not found: {defaults_dir}/{self.DEFAULT_SETTINGS_FILENAME}") from e
        except Exception as e:
            self.logger.error(f"An unexpected error occurred loading default settings: {e}")
            raise GraphLayoutError(f"Error loading default settings: {e}") from e

    def view_layout(self,save_to: Path = None,with_labels: bool = True) -> None:
        """
        preview the graph level layout

        Args:
            save_to: Path to save the layout to
            with_labels: True to label each node
        """
        self._graph.view_layout(save_to=save_to, with_labels=with_labels)

    def transfer_volumetric(
            self,
            source: str,
            target: str,
            pump_id: str,
            volume: float,
            transfer_type: str,
            pre_rinse: int = 0,
            flush: int = 1,
            post_rinse: int = 0,
            draw_speed: Optional[float] = None,
            dispense_speed: Optional[float] = None,
            compatibility_check: bool = False
    ) -> None:
        """
        Performs volumetric transfer (via the syringe pump and volumetric connections) from the source to the
        target.
        Args:
            source: Identifier of the source vessel.
            target: Identifier of the target vessel.
            pump_id: Pump to be used for the transfer
            volume: Volume to transfer (in mL).
            transfer_type: gas or liquid
            flush: Number of flushes that the transfer path should be flushed with gas after the transfer
                    (so that all residues in the transfer path are pushed into the target vessel).
            rinse: Number of rinse that the transfer path should be rinsed with liquid after the transfer
            draw_speed: Speed of the syringe pump during the draw step (in mL/min).
            dispense_speed: Speed of the syringe pump during the dispense step (in mL/min).
            compatibility_check: True to check path compatibility
        """
        valid_transfer_types = {"liquid", "gas"}
        if transfer_type not in valid_transfer_types:
            raise ValueError(f"Invalid transfer_type '{transfer_type}'. Must be 'liquid' or 'gas'.")

        pump_device = self._graph(pump_id)
        # if not isinstance(pump_device, SyringePump):
        if not isinstance(pump_device, self._PUMP_CLASS):
            raise TypeError(f"Node {pump_id} is not a SyringePump or does not exist in the Graph")
        
        gas_reservoir = self._defaults.get("gas_reservoir")
        waste = self._defaults.get("waste")

        num_transfer = ceil(volume / (pump_device.syringe_volume*1000)) # 1000 is due to syringe size issue
        volume_per_transfer = volume / num_transfer

        for pre_rinse_iteration in range(pre_rinse):
            waste = self._defaults.get("waste")
            if waste and gas_reservoir:
                self.logger.info(f"Pre-rinse pump with {source}...")
                self._execute_volumetric_transfer(source, waste, pump_id, volume, "liquid",
                                                  edge_type="volumetric",
                                                  via_draw_nodes=src_nodes[:-1])  # Rinse draw path
            else:
                self.logger.warning("Waste reservoir not defined in defaults. Skipping pre rinse.")

        self.logger.info(f"Transfer {volume} mL from {source} to {target}...")
        for i in range(0, num_transfer):
            src_nodes, src_edges, tgt_nodes, tgt_edges = self._execute_volumetric_transfer(
                source=source,
                target=target,
                pump_id=pump_id,
                volume=volume_per_transfer, 
                transfer_type=transfer_type,
                draw_speed=draw_speed,
                dispense_speed=dispense_speed,
                compatibility_check=compatibility_check
            )
                
        if gas_reservoir:
            self.logger.info(f"Flushing tubing to {target} with {gas_reservoir}")
            for flush_iteration in range(flush):
                self._execute_volumetric_transfer(gas_reservoir, target, pump_id, volume_per_transfer, "gas", # change in flush volume!
                                                  via_dispense_nodes=tgt_nodes)
                
            self._execute_volumetric_transfer(gas_reservoir, waste, pump_id, volume_per_transfer, "gas",# change in flush volume!
                                                via_dispense_nodes=src_nodes[:-1])  # Flush draw path to waste
        else:
            self.logger.warning("Gas reservoir or waste not defined in defaults. Skipping flush.")

        rinse_solvent = self._defaults.get("rinse_solvent")
        waste = self._defaults.get("waste")
        gas_reservoir = self._defaults.get("gas_reservoir")
        if rinse_solvent and waste and gas_reservoir:
            self.logger.info(f"Flushing tubing and pump from {rinse_solvent}")
            for post_rinse_iteration in range(post_rinse):
                self._execute_volumetric_transfer(rinse_solvent, waste, pump_id, volume, "liquid",
                                                  edge_type="volumetric",
                                                  via_draw_nodes=src_nodes[:-1])  # Rinse draw path
            self._execute_volumetric_transfer(gas_reservoir, waste, pump_id, volume, "gas", edge_type="volumetric",
                                                via_dispense_nodes=src_nodes[:-1])  # Flush rinse solvent with gas
        else:
            self.logger.warning("Rinse solvent, waste, or gas reservoir not defined in defaults. Skipping rinse.")

        if transfer_type == "liquid" and hasattr(self._graph(source), 'content'):
            self._update_path_content(src_edges + tgt_edges, self._graph(source).content)
        elif transfer_type == "gas" and hasattr(self._graph(source), 'content'):
            self._update_path_content(src_edges + tgt_edges, "gas")

        self.logger.info(f"Transfer of {volume} mL of {transfer_type} from {source} to {target} completed.")

    def transfer_continuous(
            self,
            source: str,
            target: str,
            pump_id: str,
            transfer_rate: float = 0,
            direction_CW: bool = True,
            compatibility_check: bool = False
    ) -> None:
        """
        Performs continuous transfer from source to target (via the peristaltic or continuous syringe pump 
        and volumetric connections) from the source to the target.
        Source and target can be the same for circulating.
        Args:
            source: Identifier of the source vessel.
            target: Identifier of the target vessel.
            pump_id: Pump to be used for the transfer
            transfer_rate: rate of transfer, mL/s, to be implemented #TODO
            compatibility_check: True to check path compatibility

        #TODO volume update
        """
        transfer_type = "volumetric"
        on = True if transfer_rate != 0 else False
        pump_device = self._graph(pump_id)
        # if not isinstance(pump_device, SyringePump):
        if not isinstance(pump_device, self._PUMP_CLASS):
            raise TypeError(f"Node {pump_id} is not a Peristaltic/Continuous Syreinge Pump or does not exist in the Graph")

        
        nodes, edges = self._find_continuous_paths(source=source, target=target, pump_id=pump_id, edge_type=transfer_type)
        if compatibility_check:
            source_vessel = self._graph(source)
            if not hasattr(source_vessel, 'content'):
                self.logger.warning(
                    f"Source '{source}' does not have a 'content' attribute. Skipping compatibility check.")
            elif not self._check_path_compatibility(edges, source_vessel.content):
                raise PathError(f"Path content is not compatible with source {source} content {source_vessel.content}")
        self._set_transfer_valves(nodes, edges)
        self._execute_continuous_pump_action(pump_id=pump_id, rpm=transfer_rate, on=on, direction=direction_CW)
        self.logger.info(f"Set continuous pump {pump_id} to {transfer_rate} rpm, on/off {on}, CW/CCW {direction_CW}")



    def _execute_volumetric_transfer(
            self,
            source: str,
            target: str,
            pump_id: str,
            volume: float,
            transfer_type: str,
            draw_speed: Optional[float] = None,
            dispense_speed: Optional[float] = None,
            via_draw_nodes: Optional[List[str]] = None,
            via_dispense_nodes: Optional[List[str]] = None,
            compatibility_check: bool = False,
            edge_type: str = "volumetric"
    ) -> Tuple[List[str], List[Tuple[str, str]], List[str], List[Tuple[str, str]]]:
        """
        Orchestrates the steps for a volumetric transfer using the pump.
        """
        self._validate_transfer(source, target, volume, transfer_type)
        if transfer_type == "gas":
            edge_type = ["gas", "volumetric"]
        src_nodes, src_edges, tgt_nodes, tgt_edges = self._find_transfer_paths(
            source, target, pump_id, edge_type, via_draw_nodes, via_dispense_nodes
        )

        if transfer_type == "liquid" and compatibility_check:
            source_vessel = self._graph(source)
            if not hasattr(source_vessel, 'content'):
                self.logger.warning(
                    f"Source '{source}' does not have a 'content' attribute. Skipping compatibility check.")
            elif not self._check_path_compatibility(src_edges + tgt_edges, source_vessel.content):
                raise PathError(f"Path content is not compatible with source {source} content {source_vessel.content}")

        self._set_transfer_valves(src_nodes, src_edges)
        self._execute_pump_action(pump_id, volume, "draw", draw_speed)
        if transfer_type == "liquid":
            self._update_vessel_volume(source, -volume)  # Volume removed

        self._set_transfer_valves(tgt_nodes, tgt_edges)
        self._execute_pump_action(pump_id, volume, "dispense", dispense_speed)
        if transfer_type == "liquid":
            self._update_vessel_volume(target, volume)  # Volume added

        return src_nodes, src_edges, tgt_nodes, tgt_edges

    def _validate_transfer(self, source: str, target: str, volume: float, transfer_type: str) -> None:
        """
        Validates if a liquid transfer is possible.
        """
        if transfer_type == "liquid":
            source_vessel = self._graph(source)
            target_vessel = self._graph(target)
            if not isinstance(source_vessel, Vessel):
                raise TypeError(f"Source '{source}' is not a Vessel.")
            if not isinstance(target_vessel, Vessel):
                raise TypeError(f"Target '{target}' is not a Vessel.")

            source_vessel.validate_transfer(volume, direction="remove")
            target_vessel.validate_transfer(volume, direction="add")

    def _find_transfer_paths(
            self,
            source: str,
            target: str,
            pump_id: str,
            edge_type: Union[str, List[str]],
            via_draw_nodes: Optional[List[str]] = None,
            via_dispense_nodes: Optional[List[str]] = None
    ) -> Tuple[List[str], List[Tuple[str, str]], List[str], List[Tuple[str, str]]]:
        """
        Finds the necessary paths for a pump-based transfer.
        """
        src_nodes, src_edges = self._graph.find_path(source, pump_id, edge_type, traversed_nodes=via_draw_nodes)
        tgt_nodes, tgt_edges = self._graph.find_path(pump_id, target, edge_type, traversed_nodes=via_dispense_nodes)
        self.logger.debug(f"Transfer path identified. src_nodes {src_nodes}, src_edges {src_edges}, "
                          f"tgt_nodes {tgt_nodes}, tgt_edges {tgt_edges}")
        return src_nodes, src_edges, tgt_nodes, tgt_edges

    def _find_continuous_paths(
            self,
            source: str,
            target: str,
            pump_id: str,
            edge_type: Union[str, List[str]],
            via_nodes: Optional[List[str]] = None, 
    ) -> Tuple[List[str], List[Tuple[str, str]]]:
        """
        Finds the necessary paths for a continuous pump based transfer
        """
        traversed_nodes = [pump_id] + (via_nodes or [])
        nodes, edges = self._graph.find_path(source=source, target=target, edge_type=edge_type, traversed_nodes=traversed_nodes)
        self.logger.debug(f"Continuous path identified. nodes {nodes}, edges {edges}.")
        return nodes, edges

    def _check_path_compatibility(self, path_edges: List[Tuple[str, str]], content: str) -> bool:
        """
        Checks if the edges in the path are compatible with the content being transferred.
        """
        return self._graph._check_edge_content_compatibility(path_edges, content)

    def _set_transfer_valves(
            self,
            path_nodes: List[str],
            path_edges: List[Tuple[str, str]]
    ) -> None:
        """
        Sets the valves along the transfer path. Assumes only pumps and valves are in the path.
        """
        # The path nodes include the pump at one end and the source/target at the other.
        # The nodes we need to set are the intermediate valves and potentially the pump itself if it has settable ports.
        # We can iterate through the nodes in the path (excluding the start/end) and check if they are valves or pumps.

        for i in range(len(path_nodes) - 1):
            u, v = path_nodes[i], path_nodes[i + 1]
            device_u = self._graph(u)
            # Check if the edge exists and has port information (assuming source_port is on node u side)
            if (u, v) in self._graph.edges and "source_port" in self._graph.edges[(u, v)]:
                output_port = self._graph.edges[(u, v)]["source_port"]
                # if isinstance(device_u, (SwitchingValve, SyringePump)):
                if isinstance(device_u, self._PUMP_VALVE_CLASS):
                    if hasattr(device_u, 'port'):
                        device_u.port = output_port
                        self.logger.debug(f"Set device {u} to port {output_port}")
                    else:
                        self.logger.warning(f"Device {u} is a valve/pump but does not have a 'port' attribute.")

    def _execute_pump_action(self, pump_id: str, volume: float, action: str, speed: Optional[float]) -> None:
        """
        Executes a draw or dispense action on the pump.
        """
        pump_device = self._graph(pump_id)
        # if not isinstance(pump_device, SyringePump):
        if not isinstance(pump_device, self._PUMP_CLASS):
            raise TypeError(f"Device '{pump_id}' is not a SyringePump.")

        if action == "draw":
            pump_device.draw(volume, speed=speed)
            self.logger.debug(f"Completed: Drawing {volume} mL with pump {pump_id}.")
        elif action == "dispense":
            pump_device.dispense(volume, speed=speed)
            self.logger.debug(f"Completed: Dispensing {volume} mL with pump {pump_id}.")
        else:
            raise ValueError(f"Invalid pump action: {action}. Must be 'draw' or 'dispense'.")

    def _execute_continuous_pump_action(self, pump_id: str, rpm: float, on: bool, direction: bool)->None:
        """
        Execute a continuous pump
        """
        pump_device = self._graph(pump_id)
        if not isinstance(pump_device, self._PUMP_CLASS):
            raise TypeError(f"Device '{pump_id}' is not a Pump.")
        
        pump_device.set_pump(rpm = rpm, on = on, direction = direction)
        self.logger.debug(f"Completed: Setting pump {pump_id} to {rpm} rpm, on/off to {on}, CW/CCW to {direction}.")

    def _update_vessel_volume(self, vessel_id: str, volume_change: float) -> None:
        """
        Updates the volume of a vessel.
        """
        vessel_device = self._graph(vessel_id)
        if not isinstance(vessel_device, Vessel):
            self.logger.warning(f"Node '{vessel_id}' is not a Vessel. Volume not updated.")
            return

        direction = "add" if volume_change >= 0 else "remove"
        vessel_device.update_volume(abs(volume_change), direction)
        self.logger.debug(f"Updated volume of vessel {vessel_id} by {volume_change} mL.")

    def _update_path_content(self, path_edges: List[Tuple[str, str]], content: Optional[str]) -> None:
        """
        Updates the content attribute of the edges in the path.
        """
        self._graph._update_edge_content(path_edges, content)

    def heat_stir(
            self,
            vessel: Union[str, List[str]],
            temperature: float = 20.0,
            rpm: float = 0.0
    ):
        """
        Sets the heating and stirring state of a vessel.

        Automatically identifies the connected hotplate, and sets the temperature and stir speed.

        Args:
            vessel: Identifier of the vessel.
            temperature: Temperature to heat the vessel to (in °C).
            rpm: Stirring speed (in rpm).
        """
        connected_hotplates = []
        vessel = [vessel] if isinstance(vessel, str) else vessel
        for v in vessel:
            connected_hotplates += self._graph.find_neighbors(
                node_id=v,
                edge_type="thermal",
                # neighbor_type=HeatStirPlate,
                neighbor_type=self._HOTPLATE_CLASS,
            )
        connected_hotplates = list(set(connected_hotplates))

        if len(connected_hotplates) != 1:
            raise GraphLayoutError(f"Vessel {vessel} must be connected to exactly one hotplate "
                                   f"(found: {len(connected_hotplates)}).")

        # hotplate: HeatStirPlate = self._graph(connected_hotplates[0])
        hotplate = self._graph(connected_hotplates[0])
        thermal_connection_nodes, thermal_connection_edges = self._graph.find_path(source=connected_hotplates[0],
                                                                                   target=vessel, edge_type="thermal")
        if not thermal_connection_nodes:
            raise PathError(f"Hotplate {connected_hotplates[0]} and vessel {vessel} have no thermal connection")
        hotplate.rpm = rpm
        hotplate.temp = temperature
        self.logger.info(f"Completed: Set heat/stir on vessel {vessel} using hotplate {connected_hotplates[0]}.")

    def _get_hp_temp_rpm(self, vessel: str)->Tuple:
        """
        Get the temp and rpm of hotplate with thermal connection of a vessel

        Args:
            vessel: Identifier of the vessel.
        """
        connected_hotplates = self._graph.find_neighbors(
            node_id=vessel,
            edge_type="thermal",
            # neighbor_type=HeatStirPlate,
            neighbor_type=self._HOTPLATE_CLASS,
        )

        if len(connected_hotplates) != 1:
            raise GraphLayoutError(f"Vessel {vessel} must be connected to exactly one hotplate "
                                   f"(found: {len(connected_hotplates)}).")

        # hotplate: HeatStirPlate = self._graph(connected_hotplates[0])
        hotplate = self._graph(connected_hotplates[0])
        thermal_connection_nodes, thermal_connection_edges = self._graph.find_path(source=connected_hotplates[0],
                                                                                   target=vessel, edge_type="thermal")
        if not thermal_connection_nodes:
            raise PathError(f"Hotplate {connected_hotplates[0]} and vessel {vessel} have no thermal connection")
        
        temp = hotplate.temp
        rpm = hotplate.rpm

        self.logger.info(f"Current Temperature {temp}, rpm {rpm} retrived from hotplate {connected_hotplates[0]} connecting to {vessel}.")
        return temp, rpm

    def get_hotplate_temperature(self, vessel: str)-> float:
        """
        Get the hotplate temperature of the hotplate connected to the vessel

        Args:
            vessel: Identifier of the vessel.
        """
        return self._get_hp_temp_rpm(vessel=vessel)[0]
    
    def get_hotplate_rpm(self, vessel: str)-> float:
        """
        Get the hotplate rpm of the hotplate connected to the vessel

        Args:
            vessel: Identifier of the vessel.
        """
        return self._get_hp_temp_rpm(vessel=vessel)[1]
        

    def _find_gas_vac_path(self, source: str, target: str) -> Tuple[List[str], List[Tuple[str, str]]]:
        """
        Finds a path for gas or vacuum, prioritizing volumetric edges if they exist.
        """
        try:
            nodes, edges = self._graph.find_path(source, target, edge_type="gas")
            self.logger.debug(f"Found 'gas' path from {source} to {target}.")
            return nodes, edges
        except PathError:
            self.logger.debug(f"No 'gas' path found from {source} to {target}. Trying 'volumetric' path.")
            try:
                nodes, edges = self._graph.find_path(source, target, edge_type="volumetric")
                self.logger.debug(f"Found 'volumetric' path from {source} to {target}.")
                return nodes, edges
            except PathError:
                raise PathError(f"No 'gas' or 'volumetric' path found from '{source}' to '{target}'.")

    def gas_connection(self, vessel: str, refill: bool = False, vacuum: bool = False):
        """
        Manage the gas connection to a given vessel

        Args:
            vessel: vessel to run gas handling
            refill: True to refill the vessel
            vacuum: True to evacuate the vessel
        """
        gas = self._defaults["gas_reservoir"]
        if "vacuum_reservoir" in self._defaults:
            if refill and vacuum:
                raise ValueError("Refill and evacuate can not be performed simultaneously with active vacuum reservoir")
            vac = self._defaults["vacuum_reservoir"]
        else:
            vac = self._defaults["waste"]
        gas_nodes, gas_edges = self._find_gas_vac_path(gas, vessel)
        vac_nodes, vac_edges = self._find_gas_vac_path(vessel, vac)

        gas_device = self._graph(gas_nodes[-2])  # change from -1 to -2 so not access last node which is Vessel
        # if not isinstance(gas_device, Relay):
        if not isinstance(gas_device, self._RELAY_CLASS):
            raise TypeError(f"Device '{gas_nodes[-2]}' on the gas path is not a Relay.")

        vac_device = self._graph(vac_nodes[-2])
        # if not isinstance(vac_device, Relay):
        if not isinstance(vac_device, self._RELAY_CLASS):
            raise TypeError(f"Device '{vac_nodes[-2]}' on the vacuum path is not a Relay.")

        if refill:
            device = self._graph(gas_nodes[-2])
            device.on = True
        else:
            device = self._graph(gas_nodes[-2])
            device.on = False

        if vacuum:
            device = self._graph(vac_nodes[-2])
            device.on = True
        else:
            device = self._graph(vac_nodes[-2])
            device.on = False

    def _perform_pump_exchange(self, vessel: str, cycles: int, pump_id: str, volume: float):
        """
        Performs atmosphere exchange using a syringe pump.
        Determines method based on vessel connections to gas reservoir.
        """
        gas_reservoir = self._defaults.get("gas_reservoir")
        waste = self._defaults.get("waste")

        if not gas_reservoir or not waste:
            raise GraphLayoutError("Gas reservoir and waste must be defined in defaults for pump exchange.")

        direct_gas_path_nodes, direct_gas_path_edges = self._graph.find_path(gas_reservoir, vessel, edge_type="gas")
        if direct_gas_path_nodes:
            self.logger.debug(f"Found direct gas inlet path to vessel {vessel}.")
            gas_inlet_name = direct_gas_path_nodes[-2]
            gas_inlet_dev = self._graph(gas_inlet_name)
            # if isinstance(gas_inlet_dev, Relay):
            if isinstance(gas_inlet_dev, self._RELAY_CLASS):
                gas_inlet_dev.on = True
                self.logger.info(f"Turned ON gas inlet device {gas_inlet_name}.")
            else:
                self.logger.info(f"Continuous feeding.")

            for i in range(cycles):
                self.logger.debug(f"Continuous supply cycle {i + 1}/{cycles}")
                self.transfer_volumetric(vessel, "waste", volume, "gas")

            # if isinstance(gas_inlet_dev, Relay):
            if isinstance(gas_inlet_dev, self._RELAY_CLASS):
                gas_inlet_dev.on = False
                self.logger.debug(f"Turned OFF gas inlet device {gas_inlet_name}.")
        else:
            self.logger.debug(f"Performing pump exchange of Evacuation-Refill for vessel {vessel}.")
            for i in range(cycles):
                self.logger.debug(f"Evacuation-Refill cycle {i + 1}/{cycles}")
                self.transfer_volumetric(vessel, "waste", pump_id, volume, "volumetric", flush=0)
                self.transfer_volumetric("gas_reservoir", vessel, pump_id, volume, "gas", flush=0)

    def _perform_schlenk_exchange(self, vessel: str, cycles: int, delay: float = 5):
        """
        Performs atmosphere exchange using schlenk line (relays for gas and vacuum).
        """
        for i in range(cycles):
            self.logger.debug(f"Schlenk exchange cycle {i + 1}/{cycles}")
            self.gas_connection(vessel, vacuum=True, refill=False)  # Evacuate
            time.sleep(delay)
            self.gas_connection(vessel, vacuum=False, refill=False)  # Turn off vacuum
            time.sleep(0.5)
            self.gas_connection(vessel, vacuum=False, refill=True)  # Refill with gas
            time.sleep(delay)
            self.gas_connection(vessel, vacuum=False, refill=False)  # Turn off gas

    def _perform_flushing(self, vessel: str, flush_time: float):
        """
        Performs atmosphere flushing with gas.
        """
        self.logger.debug(f"Performing atmosphere flushing for vessel {vessel} for {flush_time} seconds.")
        self.gas_connection(vessel, refill=True, vacuum=False)  # Turn on gas
        time.sleep(flush_time)  # Flush for specified time
        self.gas_connection(vessel, refill=False, vacuum=False)

    def write_serial(self, device: str, command: Union[str, bytes, bytearray]):
        dev = self._graph(device)
        dev.open_device_comm()
        dev.write(command)
        dev.close_device_comm()
        self.logger.info(f"Wrote to {device} command {str(command)}")