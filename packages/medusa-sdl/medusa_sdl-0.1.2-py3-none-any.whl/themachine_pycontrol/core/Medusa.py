__author__ = "Felix Strieth-Kalthoff (@felix-s-k) Han Hao (@clascclon)"

import time
from typing import List, Tuple, Optional, Union
from pathlib import Path
from logging import Logger, getLogger
import importlib.resources
from math import ceil

from .MedusaGraph import MedusaGraph
from .Vessel import Vessel
from ..utils import load_json
from ..utils import GraphLayoutError, PathError, HardwareError
from matterlab_hotplates import HeatStirPlate
from matterlab_valves import SwitchingValve
from matterlab_pumps import SyringePump
from matterlab_relays import Relay

class Medusa(object):
    """
    Parent class for the Medusa platform.

    Public methods to be used:

        transfer_liquid(source: str, destination: str, pump: str, volume: float)

        heat_stir(vessel: str, heat: bool = False, temperature: float = 20.0, stir: bool = False, rpm: float = 0.0)
    """
    # Define the resource path for the default graph and default settings file
    # These paths are relative to the root of the installed package
    # DEFAULT_GRAPH_RESOURCE_PATH = 'defaults'
    # DEFAULT_GRAPH_FILENAME = 'demo_exp_mini.json' # Using demo_exp_mini.json as the default graph
    DEFAULT_SETTINGS_RESOURCE_PATH = 'themachine_pycontrol.defaults'
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
                if val in self._graph.nodes:
                    resolved_defaults[key] = val
                    continue
                mathches = [
                    n for n, d in self._graph.nodes(data=True)
                    if self._graph._get_node_category(d["object"]).lower() == val.lower()
                ]
                if mathches:
                    resolved_defaults[key] = mathches[0]
                    self.logger.info(f"Default '{key}' matched category '{val}'. Using node '{mathches[0]}'.")
                    continue
                if val.endswith("*"):
                    prefix = val[:-1]
                    matches = [n for n in self._graph.nodes if n.startswith(prefix)]
                    if matches:
                        resolved_defaults[key] = matches[0]
                        self.logger.info(f"Default '{key}' matched wildcard '{val}'. Using node '{mathches[0]}'.")
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
            destination: str,
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
        destination.
        Args:
            source: Identifier of the source vessel.
            destination: Identifier of the target vessel.
            pump_id: Pump to be used for the transfer
            volume: Volume to transfer (in mL).
            transfer_type: gas or liquid
            flush: Number of flushes that the transfer path should be flushed with gas after the transfer
                    (so that all residues in the transfer path are pushed into the destination vessel).
            rinse: Number of rinse that the transfer path should be rinsed with liquid after the transfer
            draw_speed: Speed of the syringe pump during the draw step (in mL/min).
            dispense_speed: Speed of the syringe pump during the dispense step (in mL/min).
            compatibility_check: True to check path compatibility
        """
        valid_transfer_types = {"liquid", "gas"}
        if transfer_type not in valid_transfer_types:
            raise ValueError(f"Invalid transfer_type '{transfer_type}'. Must be 'liquid' or 'gas'.")

        pump_device = self._graph(pump_id)
        if not isinstance(pump_device, SyringePump):
            raise TypeError(f"Node {pump_id} is not a SyringePump or does not exist in the Graph")
        
        num_transfer = ceil(volume / (pump_device.syringe_volume*1000)) # 1000 is due to syringe size issue
        volume_per_transfer = volume / num_transfer

        for pre_rinse_iteration in range(pre_rinse):
            waste = self._defaults.get("waste")
            if waste and gas_reservoir:
                self.logger.info(f"Pre-rinse pump with {source}...")
                self._execute_volumetric_transfer(source, waste, pump_id, volume, "liquid",
                                                  edge_type="volumetric",
                                                  via_draw_nodes=draw_nodes[:-1])  # Rinse draw path
            else:
                self.logger.warning("Waste reservoir not defined in defaults. Skipping pre rinse.")

        self.logger.info(f"Transfer {volume} mL from {source} to {destination}...")
        for i in range(0, num_transfer):
            draw_nodes, draw_edges, dispense_nodes, dispense_edges = self._execute_volumetric_transfer(
                source=source,
                destination=destination,
                pump_id=pump_id,
                volume=volume_per_transfer, 
                transfer_type=transfer_type,
                draw_speed=draw_speed,
                dispense_speed=dispense_speed,
                compatibility_check=compatibility_check
            )
        
        gas_reservoir = self._defaults.get("gas_reservoir")
        waste = self._defaults.get("waste")
        if gas_reservoir:
            self.logger.info(f"Flushing tubing to {destination} with {gas_reservoir}")
            for flush_iteration in range(flush):
                self._execute_volumetric_transfer(gas_reservoir, destination, pump_id, volume_per_transfer, "gas", # change in flush volume!
                                                  via_dispense_nodes=dispense_nodes)
                
            self._execute_volumetric_transfer(gas_reservoir, waste, pump_id, volume_per_transfer, "gas",# change in flush volume!
                                                via_dispense_nodes=draw_nodes[:-1])  # Flush draw path to waste
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
                                                  via_draw_nodes=draw_nodes[:-1])  # Rinse draw path
            self._execute_volumetric_transfer(gas_reservoir, waste, pump_id, volume, "gas", edge_type="volumetric",
                                                via_dispense_nodes=draw_nodes[:-1])  # Flush rinse solvent with gas
        else:
            self.logger.warning("Rinse solvent, waste, or gas reservoir not defined in defaults. Skipping rinse.")

        if transfer_type == "liquid" and hasattr(self._graph(source), 'content'):
            self._update_path_content(draw_edges + dispense_edges, self._graph(source).content)
        elif transfer_type == "gas" and hasattr(self._graph(source), 'content'):
            self._update_path_content(draw_edges + dispense_edges, "gas")

        self.logger.info(f"Transfer of {volume} mL of {transfer_type} from {source} to {destination} completed.")

    def _execute_volumetric_transfer(
            self,
            source: str,
            destination: str,
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
        self._validate_transfer(source, destination, volume, transfer_type)
        if transfer_type == "gas":
            edge_type = ["gas", "volumetric"]
        draw_nodes, draw_edges, dispense_nodes, dispense_edges = self._find_transfer_paths(
            source, destination, pump_id, edge_type, via_draw_nodes, via_dispense_nodes
        )

        if transfer_type == "liquid" and compatibility_check:
            source_vessel = self._graph(source)
            if not hasattr(source_vessel, 'content'):
                self.logger.warning(
                    f"Source '{source}' does not have a 'content' attribute. Skipping compatibility check.")
            elif not self._check_path_compatibility(draw_edges + dispense_edges, source_vessel.content):
                raise PathError(f"Path content is not compatible with source {source} content {source_vessel.content}")

        self._set_transfer_valves(draw_nodes, draw_edges)
        self._execute_pump_action(pump_id, volume, "draw", draw_speed)
        if transfer_type == "liquid":
            self._update_vessel_volume(source, -volume)  # Volume removed

        self._set_transfer_valves(dispense_nodes, dispense_edges)
        self._execute_pump_action(pump_id, volume, "dispense", dispense_speed)
        if transfer_type == "liquid":
            self._update_vessel_volume(destination, volume)  # Volume added

        return draw_nodes, draw_edges, dispense_nodes, dispense_edges

    def _validate_transfer(self, source: str, destination: str, volume: float, transfer_type: str) -> None:
        """
        Validates if a liquid transfer is possible.
        """
        if transfer_type == "liquid":
            source_vessel = self._graph(source)
            destination_vessel = self._graph(destination)
            if not isinstance(source_vessel, Vessel):
                raise TypeError(f"Source '{source}' is not a Vessel.")
            if not isinstance(destination_vessel, Vessel):
                raise TypeError(f"Destination '{destination}' is not a Vessel.")

            source_vessel.validate_transfer(volume, direction="remove")
            destination_vessel.validate_transfer(volume, direction="add")

    def _find_transfer_paths(
            self,
            source: str,
            destination: str,
            pump_id: str,
            edge_type: Union[str, List[str]],
            via_draw_nodes: Optional[List[str]] = None,
            via_dispense_nodes: Optional[List[str]] = None
    ) -> Tuple[List[str], List[Tuple[str, str]], List[str], List[Tuple[str, str]]]:
        """
        Finds the necessary paths for a pump-based transfer.
        """
        draw_nodes, draw_edges = self._graph.find_path(pump_id, source, edge_type, traversed_nodes=via_draw_nodes)
        dispense_nodes, dispense_edges = self._graph.find_path(pump_id, destination, edge_type,
                                                               traversed_nodes=via_dispense_nodes)

        return draw_nodes, draw_edges, dispense_nodes, dispense_edges

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
        # The path nodes include the pump at one end and the source/destination at the other.
        # The nodes we need to set are the intermediate valves and potentially the pump itself if it has settable ports.
        # We can iterate through the nodes in the path (excluding the start/end) and check if they are valves or pumps.

        for i in range(len(path_nodes) - 1):
            u, v = path_nodes[i], path_nodes[i + 1]
            device_u = self._graph(u)
            # Check if the edge exists and has port information (assuming source_port is on node u side)
            if (u, v) in self._graph.edges and "source_port" in self._graph.edges[(u, v)]:
                output_port = self._graph.edges[(u, v)]["source_port"]
                if isinstance(device_u, (SwitchingValve, SyringePump)):
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
        if not isinstance(pump_device, SyringePump):
            raise TypeError(f"Device '{pump_id}' is not a SyringePump.")

        if action == "draw":
            pump_device.draw(volume, speed=speed)
            self.logger.debug(f"Completed: Drawing {volume} mL with pump {pump_id}.")
        elif action == "dispense":
            pump_device.dispense(volume, speed=speed)
            self.logger.debug(f"Completed: Dispensing {volume} mL with pump {pump_id}.")
        else:
            raise ValueError(f"Invalid pump action: {action}. Must be 'draw' or 'dispense'.")

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
            vessel: str,
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
        connected_hotplates = self._graph.find_neighbors(
            node_id=vessel,
            edge_type="thermal",
            neighbor_type=HeatStirPlate,
        )

        if len(connected_hotplates) != 1:
            raise GraphLayoutError(f"Vessel {vessel} must be connected to exactly one hotplate "
                                   f"(found: {len(connected_hotplates)}).")

        hotplate: HeatStirPlate = self._graph(connected_hotplates[0])
        thermal_connection_nodes, thermal_connection_edges = self._graph.find_path(source=connected_hotplates[0],
                                                                                   target=vessel, edge_type="thermal")
        if not thermal_connection_nodes:
            raise PathError(f"Hotplate {connected_hotplates[0]} and vessel {vessel} have no thermal connection")
        hotplate.rpm = rpm
        hotplate.temp = temperature
        self.logger.info(f"Completed: Set heat/stir on vessel {vessel} using hotplate {connected_hotplates[0]}.")

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

        gas_device = self._graph(gas_nodes[-1])
        if not isinstance(gas_device, Relay):
            raise TypeError(f"Device '{gas_nodes[-1]}' on the gas path is not a Relay.")

        vac_device = self._graph(vac_nodes[-1])
        if not isinstance(vac_device, Relay):
            raise TypeError(f"Device '{vac_nodes[-1]}' on the vacuum path is not a Relay.")

        if refill:
            device = self._graph(gas_nodes[-1])
            device.on = True
        else:
            device = self._graph(gas_nodes[-1])
            device.on = False

        if vacuum:
            device = self._graph(vac_nodes[-1])
            device.on = True
        else:
            device = self._graph(vac_nodes[-1])
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
            gas_inlet_name = direct_gas_path_nodes[-1]
            gas_inlet_dev = self._graph(gas_inlet_name)
            if isinstance(gas_inlet_dev, Relay):
                gas_inlet_dev.on = True
                self.logger.info(f"Turned ON gas inlet device {gas_inlet_name}.")
            else:
                self.logger.info(f"Continuous feeding.")

            for i in range(cycles):
                self.logger.debug(f"Continuous supply cycle {i + 1}/{cycles}")
                self.transfer_volumetric(vessel, "waste", volume, "gas")

            if isinstance(gas_inlet_dev, Relay):
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