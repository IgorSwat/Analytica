from typing import Any, Dict, Tuple
from collections import deque


# Short config - list of available nodes and their respective (id, output_name)
# Second value is important, because it is used inside processors to extract input arguments
RAW_DATA_NODE = ("raw_data", "df")
SELECT_DATA_NODE = ("select_data", "df")
SELECT_FEATURES_NODE_1 = ("select_features_1", "df")
EXTRACT_TYPES_NODE = ("extract_f_types", "f_types")
SERIALIZE_DATA_NODE_1 = ("serialize_data_1", "df_serialized")
SERIALIZE_TYPES_NODE = ("serialize_f_types", "types_serialized")
NORMALIZE_DATA_NODE = ("normalize_data", "df_normalized")
SERIALIZE_DATA_NODE_2 = ("serialize_data_2", "df_serialized")
ANALYZE_PCA_NODE = ("analyze_pca", "pca_stats")
PLOT_PCA_NODE = ("plot_pca", "plot_data")

SELECT_FEATURES_NODE_2 = ("select_features_2", "df_processed")

CLUSTER_DATA_NODE = ("cluster_data", "df_clustered")
GET_PCA_NODE = ("return_pca_data", "pca_data")
PLOT_CLUSTER_NODE = ("plot_cluster", "plot_cluster_data")

# ........


# Node class, designed to:
# 1) Encapsulate processor
# 2) Build the structure of data processing graph
class DataNode:

    def __init__(self, node_properties: Tuple[str, str], processor=None, active=False):
        self.node_id = node_properties[0]
        self.output_name = node_properties[1]
        self.processor = processor          # Main computational class which does something with data (needs to be a functor!)
        self.active = active                # State of node

        self.predecessors = []              # List of input nodes
        self.successors = []                # List of nodes which takes current node data as an input

        self.last_result = None             # For optimization purposes, remember the last computed values


    def process(self, input: Dict[str, Any]) -> Any:
        if not self.active:
            print(f"Error in {self.node_id}: node is not active...")
            return None

        if self.last_result is None:
            self.last_result = self.processor(**input)
            if self.processor.error is not None:
                print(f"Error in {self.node_id}: {self.processor.error}")

        return self.last_result


    def has_processor(self) -> bool:
        return self.processor is not None


    def reset_memory(self) -> None:
        self.last_result = None


# The main class of data processing, represents graph of connected processors (encapsulated in nodes)
class DataFlow:

    def __init__(self):
        # Define nodes
        self.nodes : Dict[str, DataNode] = {
            RAW_DATA_NODE[0]: DataNode(RAW_DATA_NODE),
            SELECT_DATA_NODE[0]: DataNode(SELECT_DATA_NODE),
            SELECT_FEATURES_NODE_1[0]: DataNode(SELECT_FEATURES_NODE_1),
            EXTRACT_TYPES_NODE[0]: DataNode(EXTRACT_TYPES_NODE),
            SERIALIZE_DATA_NODE_1[0]: DataNode(SERIALIZE_DATA_NODE_1),
            SERIALIZE_TYPES_NODE[0]: DataNode(SERIALIZE_TYPES_NODE),
            NORMALIZE_DATA_NODE[0]: DataNode(NORMALIZE_DATA_NODE),
            SERIALIZE_DATA_NODE_2[0]: DataNode(SERIALIZE_DATA_NODE_2),
            ANALYZE_PCA_NODE[0]: DataNode(ANALYZE_PCA_NODE),
            PLOT_PCA_NODE[0]: DataNode(PLOT_PCA_NODE),
            SELECT_FEATURES_NODE_2[0]: DataNode(SELECT_FEATURES_NODE_2),

            GET_PCA_NODE[0]: DataNode(GET_PCA_NODE),
            CLUSTER_DATA_NODE[0]: DataNode(CLUSTER_DATA_NODE),
            PLOT_CLUSTER_NODE[0]: DataNode(PLOT_CLUSTER_NODE),

        }

        # Define connections (edges in directed, acyclic graph)
        self.__make_connection(RAW_DATA_NODE[0], SELECT_DATA_NODE[0])
        self.__make_connection(RAW_DATA_NODE[0], EXTRACT_TYPES_NODE[0])
        self.__make_connection(SELECT_DATA_NODE[0], SERIALIZE_DATA_NODE_1[0])
        self.__make_connection(EXTRACT_TYPES_NODE[0], SERIALIZE_TYPES_NODE[0])
        self.__make_connection(SELECT_DATA_NODE[0], SELECT_FEATURES_NODE_1[0])
        self.__make_connection(SELECT_FEATURES_NODE_1[0], NORMALIZE_DATA_NODE[0])
        self.__make_connection(EXTRACT_TYPES_NODE[0], NORMALIZE_DATA_NODE[0])
        self.__make_connection(NORMALIZE_DATA_NODE[0], SERIALIZE_DATA_NODE_2[0])
        self.__make_connection(NORMALIZE_DATA_NODE[0], PLOT_PCA_NODE[0])
        self.__make_connection(NORMALIZE_DATA_NODE[0], ANALYZE_PCA_NODE[0])
        self.__make_connection(NORMALIZE_DATA_NODE[0], SELECT_FEATURES_NODE_2[0])
        
        self.__make_connection(NORMALIZE_DATA_NODE[0], GET_PCA_NODE[0])
        self.__make_connection(GET_PCA_NODE[0], CLUSTER_DATA_NODE[0])
        self.__make_connection(NORMALIZE_DATA_NODE[0], CLUSTER_DATA_NODE[0])
        self.__make_connection(CLUSTER_DATA_NODE[0], PLOT_CLUSTER_NODE[0])



    # This function process all the nodes that lead do node_id in the graph, by performing backpropagation
    def process(self, node_id: str) -> Any:
        if node_id not in self.nodes:
            print(f"Error: node {node_id} not found during processing")
            return None

        # Recursive calls, using backpropagation to compute all the necessary nodes
        node = self.nodes[node_id]
        processor_input = {p.output_name: self.process(p.node_id) for p in node.predecessors}

        # Check for errors
        for input_name, input_value in processor_input.items():
            if input_value is None:
                print(f"Error: input '{input_name}' is None during processing of {node_id}")
                return None

        return node.process(processor_input)


    # Replaces the processor, also activates the node
    def set_processor(self, node_id: str, processor: Any) -> None:
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.active = True

            # TODO: Test this optimization for it's correctness
            if node.processor is None or node.processor != processor:
                node.processor = processor
                self.__reset_related_nodes(node_id, root_exc=False)


    def activate_node(self, node_id: str) -> None:
        if node_id in self.nodes:
            if not self.nodes[node_id].has_processor():
                print(f"Error: Trying to activate node {node_id}, which does not have any processor...")
            else:
                self.nodes[node_id].active = True


    def deactivate_node(self, node_id: str) -> None:
        if node_id in self.nodes:
            self.nodes[node_id].active = False


    # Access processed data at any stage (represented by some node)
    def load_memory(self, node_id: str) -> Any:
        return self.nodes[node_id].last_result if node_id in self.nodes else None


    # Save new data to given node
    def save_memory(self, node_id: str, new_value: Any) -> None:
        if node_id in self.nodes:
            self.nodes[node_id].last_result = new_value
            self.__reset_related_nodes(node_id, root_exc=True)


    def get_processor(self, node_id):
        return self.nodes[node_id].processor if node_id in self.nodes else None


    def __make_connection(self, predecessor_id: str, successor_id: str) -> None:
        if predecessor_id in self.nodes and successor_id in self.nodes:
            self.nodes[predecessor_id].successors.append(self.nodes[successor_id])
            self.nodes[successor_id].predecessors.append(self.nodes[predecessor_id])


    # Reset the memorized values in all related nodes
    # Since some processor has changed, it should affect the results of it's successors, so the result must be recomputed
    def __reset_related_nodes(self, node_id: str, root_exc: bool = False) -> None:
        if node_id in self.nodes:
            node = self.nodes[node_id]

            # This time we use BFS instead of DFS :)
            nodes_to_reset = deque([node])
            while nodes_to_reset:
                node_to_reset = nodes_to_reset.popleft()
                if not root_exc or node_to_reset.node_id != node_id:
                    node_to_reset.reset_memory()
                for successor in node_to_reset.successors:
                    nodes_to_reset.append(successor)