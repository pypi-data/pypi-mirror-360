from __future__ import annotations

__author__ = "Felix Strieth-Kalthoff (@felix-s-k), Anji Zhang (@atozhang), Martin Seifrid (@mseifrid)， Han Hao (@clascclon)"

from pathlib import Path
from typing import Dict, Union, List, Any, Optional, Tuple, Type
from logging import Logger, getLogger
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import importlib

from matterlab_pumps import SyringePump, TecanXCPump, JKemPump, TecanCentrisPump, TecanXLPPump, RunzePump
from matterlab_valves import SwitchingValve, JKem4in1Valve, ValcoSelectionValve, JKemNewValve, RunzeSelectionValve
from matterlab_hotplates import HeatStirPlate, HeidolphHotplate, IKAHotplate
from matterlab_relays import Relay, R421B16Relay, JYdaqRelay, CE221ARelay

from .Vessel import Vessel
from ..utils.FileHandling import load_json, save_json
from ..utils.MedusaErrors import GraphLayoutError, PathError
# TODO: Check how to to best do module-level absolute imports.
# HH: Tried a bunch and above seeems works


class NodeFactory:
    """
    Factory pattern for creating node objects as instances of the physical devices within the MEDUSA platform.

    General:
        node_settings = {"type": "Hotplate", ...}
        node_object = NodeFactory.generate_object(node_settings)
    """
    devices: dict = {
        "Hotplate": HeatStirPlate,
        "HeidolphHotplate": HeidolphHotplate,
        "IKAHotplate": IKAHotplate,
        "Pump": SyringePump,
        "TecanXCPump": TecanXCPump,
        "TecanXLPPump": TecanXLPPump,
        "TecanCentrisPump": TecanCentrisPump,
        "RunzePump": RunzePump,
        "JKemPump": JKemPump,
        "Valve": SwitchingValve,
        "JKem4in1Valve": JKem4in1Valve,
        "JKemNewValve": JKemNewValve,
        "ValcoSelectionValve": ValcoSelectionValve,
        "RunzeSelectionValve": RunzeSelectionValve,
        "Relay": Relay,
        "R421B16Relay": R421B16Relay,
        "JYdaqRelay": JYdaqRelay,
        "CE221ARelay": CE221ARelay,
        "Vessel": Vessel,
    }

    @classmethod
    def generate_node_instance(cls, node_settings: Dict) -> Union[HeatStirPlate, SyringePump, Relay, SwitchingValve, Vessel, TecanXCPump]:
        """
        Instantiates the respective device from the dictionary of node settings.

        Args:
            node_settings (dict): The dictionary of node settings. Must contain the following keys:
                "type": str (must be one of the keys in the devices dictionary)

        Returns:
            Union[Hotplate, Pump, Relay, Valve, Vessel]: The instantiated device.
        """
        device_type = node_settings.pop("type")
        device_class = cls.devices.get(device_type)
        if device_class is None:
            raise ValueError(f"Unknown device type '{device_type}'.")
        settings = node_settings.get("settings", {})
        return device_class(**settings)

class MedusaGraph(nx.Graph):
    DEVICE_CATEGORIES: dict = {
        SyringePump: 'Pump',
        TecanXCPump: 'Pump',
        TecanXLPPump: 'Pump',
        TecanCentrisPump: 'Pump',
        JKemPump: 'Pump',
        RunzePump: 'Pump',
        SwitchingValve: 'Valve',
        JKem4in1Valve: 'Valve',
        JKemNewValve: 'Valve',
        ValcoSelectionValve: 'Valve',
        RunzeSelectionValve: 'Valve',
        HeatStirPlate: 'Hotplate',
        HeidolphHotplate: 'Hotplate',
        IKAHotplate: 'Hotplate',
        Vessel: 'Vessel',
        Relay: 'Relay',
        R421B16Relay: 'Relay',
        JYdaqRelay: 'Relay',
        CE221ARelay: 'Relay',
        # Add other device types here
    }

    EDGE_TYPES = {
        "volumetric": (),
        "gas": (),
        "thermal": ()
    }

    def __init__(self, logger: Optional[Logger] = None, **attr):
        super().__init__(**attr)
        self.logger = logger if logger is not None else getLogger()

    @classmethod
    def from_json(
            cls,
            file: Path,
            logger: Optional[Logger] = None
    ) -> MedusaGraph:
        """
        Generates a Medusa object from a json file.

        Args:
            file: Path to the json file.
            logger: Optional logger.

        Returns:
            MedusaGraph: A MedusaGraph object.
        """
        graph_layout: Dict[str, List[Dict]] = load_json(file)
        graph = cls(logger=logger)

        for node in graph_layout["nodes"]:
            node_id = node.pop("name")
            device_instance = NodeFactory.generate_node_instance(node)
            graph.add_node(node_id, object=device_instance)

        for edge in graph_layout["links"]:

            source = edge.pop("source")
            target = edge.pop("target")
            if source not in graph.nodes or target not in graph.nodes:
                raise GraphLayoutError(f"Invalid edge: '{source}' -> '{target}'. One or both nodes are missing.")

            edge_settings = edge

            if "type" not in edge_settings:
                raise GraphLayoutError(f"Edge type not found in settings for edge between {source} and {target}.")
            edge_type = edge_settings["type"]
            if edge_type not in cls.EDGE_TYPES:
                raise GraphLayoutError(f"Invalid edge type: {edge_type}.")
            if edge_type == "volumetric":
                edge_settings["content"] = "empty"
            # edge_dict = EdgeFactory.generate_edge_instance(edge)
            graph.add_edge(source, target, **edge_settings)

        graph.logger.info(f"Instantiated a graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges")
        return graph

    def to_json(self, file: Path) -> None:
        """
        Saves the current graph layout to a JSON file.

        Args:
            file: Path to the JSON file.
        """
        graph_layout: Dict[str, List[Dict]] = {"nodes": [], "links": []}

        for node_id, data in self.nodes(data=True):
            node_data = {"name": node_id}
            for key, value in data.items():
                if key != 'object':
                    node_data[key] = value
            graph_layout["nodes"].append(node_data)

        for source, target, data in self.edges(data=True):
            edge_data = {"source": source, "target": target}
            edge_data.update(data)
            graph_layout["links"].append(edge_data)

        save_json(graph_layout, file)
        self.logger.info(f"Graph successfully saved to {file}")

    def validate_nodes_exist(self, nodes: List[str]) -> None:
        missing_nodes = [node for node in nodes if node not in self.nodes]
        if missing_nodes:
            raise GraphLayoutError(f"The following nodes are missing from the graph: {missing_nodes}")

    def view_layout(
            self,
            save_to: Path = None,
            with_labels: bool = True,
            **kwargs
    ) -> None:
        """
        Visualizes the layout of the _graph and saves it to a png file.

        Args:
            save_to: Path to the png file.
            with_labels: True to display node labels
            **kwargs: Keyword arguments for the nx.draw_spring function.
        """
        pos = nx.spring_layout(self)

        # Below is more from ChatGPT, looks ugly but works...

        node_categories = {}
        for node, data in self.nodes(data=True):
            node_obj = data['object']
            node_category = self._get_node_category(node_obj)
            if node_category not in node_categories:
                node_categories[node_category] = []
            node_categories[node_category].append(node)

        node_category_shapes = {
            'Pump': 'h',  # hex
            'Valve': 'P',  # plus filled
            'Hotplate': 's',  # square
            'Vessel': 'o',  # Circle
            'Relay': '|',  # vline
        }

        node_category_colors = {
            'Pump': 'brown',
            'Valve': 'green',
            'Hotplate': 'orange',
            'Vessel': 'lightgrey',
            'Relay': 'purple',
        }

        edge_types = {}
        for u, v, data in self.edges(data=True):
            edge_type = data['type']
            if edge_type not in edge_types:
                edge_types[edge_type] = []
            edge_types[edge_type].append((u, v))

        edge_type_colors = {
            'volumetric': 'steelblue',
            'gas': 'grey',
            'thermal': 'red',
        }

        plt.figure(figsize=(12, 8))

        for edge_type, edges in edge_types.items():
            nx.draw_networkx_edges(
                self,
                pos,
                edgelist=edges,
                edge_color=edge_type_colors.get(edge_type, 'black'),
                width=2,
                label=edge_type,
                **kwargs
            )

        for node_category, nodes in node_categories.items():
            nx.draw_networkx_nodes(
                self,
                pos,
                nodelist=nodes,
                node_shape=node_category_shapes.get(node_category, 'o'),
                node_color=node_category_colors.get(node_category, 'grey'),
                node_size=500,
                label=node_category,
                **kwargs
            )

        if with_labels:
            nx.draw_networkx_labels(self, pos, font_size=10)

        node_legend_elements = []
        for node_category in node_categories.keys():
            node_shape = node_category_shapes.get(node_category, 'o')
            node_color = node_category_colors.get(node_category, 'grey')
            legend_element = Line2D(
                [0], [0],
                marker=node_shape,
                color='w',
                label=node_category,
                markerfacecolor=node_color,
                markersize=10
            )
            node_legend_elements.append(legend_element)

        edge_legend_elements = []
        for edge_type in edge_types.keys():
            edge_color = edge_type_colors.get(edge_type, 'black')
            legend_element = Line2D(
                [0], [0],
                color=edge_color,
                lw=2,
                label=edge_type
            )
            edge_legend_elements.append(legend_element)

        plt.legend(
            handles=node_legend_elements + edge_legend_elements,
            loc='upper right',
            fontsize='medium'
        )

        plt.axis('off')

        if save_to:
            plt.savefig(save_to)
        # plt.show()



    def __call__(self, node_id: str) -> Any:
        """
        Returns the object associated with the node.

        Args:
            node_id (str): The name of the node.

        Returns:
            Any: The object associated with the node.
        """
        return self.nodes[node_id]["object"]

    def edge_type_subgraph(
            self,
            edge_type: str
    ) -> MedusaGraph:
        """
        Generates a subgraph of the Medusa object with only the edges of the specified type.

        Args:
            edge_type (str): The type of edge. Must be one of the keys in the edge_types dictionary.

        Returns:
            MedusaGraph: A MedusaGraph object.
        """
        filtered_edges = []
        for source, target, data in self.edges(data=True):
            if data["type"] == edge_type:
                filtered_edges.append((source, target))
        return self.edge_subgraph(filtered_edges).copy(as_view=False)

    def find_path(
            self,
            source: str,
            target: str,
            edge_type: Optional[Union[str, List[str]]] = None,
            traversed_nodes: Optional[List[str]] = None
    ) -> Tuple[List[str], List[Tuple[str, str]]]:
        """
        Finds the shortest path between two nodes in the _graph.

        Args:
            source (str): The name of the source node.
            target (str): The name of the target node.
            edge_type (Optional[str]): The type of edge that is allowed to be passed on the Path.
            traversed_nodes (Optional[List[str]]): A list of node names that have to be traversed in the path.

        Returns:
            List[str]: A list of node names representing the shortest path between the source and target nodes.
            List[Tuple(str, str)]: A list of tuples representing the edges in the shortest path between the source and target nodes.
        """
        # subgraph = self if edge_type is None else self.edge_type_subgraph(edge_type)
        if edge_type is None:
            subgraph = self
        else:
            allowed_edges = [edge_type] if isinstance(edge_type, str) else edge_type
            edges = [(u, v) for u, v, data in self.edges(data=True) if data.get('type') in allowed_edges]
            subgraph = self.edge_subgraph(edges).copy()

        if traversed_nodes is None:
            node_list = nx.shortest_path(subgraph, source, target)

        else:
            node_list = []
            min_length = np.inf

            for path in nx.all_simple_paths(subgraph, source, target):
                if all([node in path for node in traversed_nodes]) and len(path) < min_length:
                    min_length = len(path)
                    node_list = path

        if len(node_list) == 0:
            raise PathError(f"No path found between '{source}' and '{target}' that includes nodes {traversed_nodes}.")

        edge_list = [(node_list[i], node_list[i+1]) for i in range(len(node_list)-1)]

        return node_list, edge_list

    def find_neighbors(
            self,
            node_id: str,
            edge_type: Optional[str] = None,
            neighbor_type: Optional[Type] = None
    ) -> List[str]:
        """
        Finds the neighbor(s) of the specified node.

        Args:
            node_id (str): The name of the node.
            edge_type (Optional[str]): The type of edge that is allowed to be passed on the Path.
            neighbor_type (Optional[Type]): The type of the neighbor node.
        REturns:
            List[str]: A list of neighbor node IDs matching the criteria.
        """
        if node_id not in self.nodes:
            raise GraphLayoutError(f"Node '{node_id}' not found in the graph.")

        if edge_type is None:
            neighbors = list(self.neighbors(node_id))

        else:
            subgraph = self.edge_type_subgraph(edge_type)
            if node_id not in subgraph:  # Check if the node exists in the subgraph
                return []
            neighbors = list(subgraph.neighbors(node_id))

        if neighbor_type is None:
            return neighbors

        else:
            return [neighbor for neighbor in neighbors if isinstance(self(neighbor), neighbor_type)]

    def _get_node_category(self, node_obj) -> str:
        """
        Determines the category of a node based on its class or attributes.

        Args:
            node_obj: The object associated with the node.

        Returns:
            str: The category of the node (e.g., 'Pump', 'Valve').
        """
        for device_class, category in self.DEVICE_CATEGORIES.items():
            if isinstance(node_obj, device_class):
                return category
        return "Other"

    def _update_edge_content(self, path_edges: List[Tuple[str, str]], content: Optional[str]) -> None:
        """
        Updates the 'content' attribute of the specified edges.

        Args:
            path_edges (List[Tuple[str, str]]): A list of edges represented as tuples of node IDs.
            content (Optional[str]): The content to set for the edges.
        """
        for edge in path_edges:
            if edge in self.edges:
                self.edges[edge]['content'] = content
                self.logger.debug(f"Set edge {edge} 'content' attribute to {content}.")
            else:
                self.logger.warning(f"Attempted to update content for non-existent edge: {edge}")

    def _check_edge_content_compatibility(self, path_edges: List[Tuple[str, str]], new_content: str) -> bool:
        """
        Checks if all specified edges are compatible with the new content.

        Args:
            path_edges (List[Tuple[str, str]]): A list of edges represented as tuples of node IDs.
            new_content (str): The new content that will be passed through the edges.

        Returns:
            bool: True if all edges are compatible, False otherwise.
        """
        for edge in path_edges:
            if edge not in self.edges:
                self.logger.warning(f"Compatibility check skipped for non-existent edge: {edge}")
                continue  # Skip if edge doesn't exist
            current_content = self.edges[edge].get('content', None)
            self.logger.info(f"Edge {edge} current 'content': {current_content}.")
            if not self._are_contents_compatible(current_content, new_content):
                self.logger.debug(f"Edge {edge} with content '{current_content}' is incompatible with '{new_content}'.")
                return False
        return True

    def _are_contents_compatible(self, current_content: str, new_content: str) -> bool:
        """
        Determines if two contents are compatible.

        Args:
            current_content (str): The current content in the edge.
            new_content (str): The new content to be introduced.

        Returns:
            bool: True if contents are compatible or if the edge is empty, False otherwise.
        """
        if current_content == new_content:
            return True
        if current_content == "empty" or current_content is None:
            return True
        if new_content == None:
            return True
        # TODO implement compatibility check
        # return True
        return False  # Default to False if contents are different

    def add_node_from_data(self, node_data: Dict):
        """
        Add a node to the graph from dict

        Args:
            node_data (Dict): data of the node
        """
        if "name" not in node_data:
            raise ValueError("Node data must contain a 'name'.")
        node_id = node_data["name"]

        if node_id in self.nodes:
            raise ValueError(f"Node with name '{node_id}' already exists.")

        try:
            node_settings = node_data.copy()
            node_settings.pop("name")  # Remove name as it's used as node_id
            device_instance = NodeFactory.generate_node_instance(node_settings)
            self.add_node(node_id, object=device_instance, **node_settings)  # Store original settings as well
            self.logger.info(f"Added node '{node_id}' of type '{node_settings.get('type')}'.")
        except Exception as e:
            raise ValueError(f"Error creating or adding node '{node_id}': {e}")

    def add_edge_from_data(self, edge_data: Dict) -> None:
        """
        Adds an edge to the graph from a dictionary of edge data.

        Args:
            edge_data (Dict): Dictionary containing 'source', 'target', 'type', and other attributes.
        """
        if "source" not in edge_data or "target" not in edge_data or "type" not in edge_data:
            raise ValueError("Edge data must contain 'source', 'target', and 'type'.")

        source = edge_data["source"]
        target = edge_data["target"]
        edge_type = edge_data["type"]

        if source not in self.nodes:
            raise ValueError(f"Source node '{source}' not found in the graph.")
        if target not in self.nodes:
            raise ValueError(f"Target node '{target}' not found in the graph.")

        if self.has_edge(source, target):
            # Decide if you want to update or raise an error for existing edges
            self.logger.warning(f"Edge already exists between '{source}' and '{target}'. Updating edge data.")

        if edge_type not in self.EDGE_TYPES:
            raise ValueError(f"Invalid edge type: {edge_type}.")

        # Create a copy to avoid modifying the original dictionary
        edge_attributes = edge_data.copy()
        edge_attributes.pop("source")
        edge_attributes.pop("target")

        if edge_type == "volumetric" and "content" not in edge_attributes:
            edge_attributes["content"] = "empty"

        self.add_edge(source, target, **edge_attributes)
        self.logger.info(f"Added edge from '{source}' to '{target}' with type '{edge_type}'.")
