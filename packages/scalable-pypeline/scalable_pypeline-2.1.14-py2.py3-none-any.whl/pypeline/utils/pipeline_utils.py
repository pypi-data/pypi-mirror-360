import logging
import typing
import networkx as nx


T = typing.TypeVar("T")  # T can be any type


logger = logging.getLogger(__name__)


def get_execution_graph(
    config: dict,
    adjacency_key: str = "dagAdjacency",
    task_definitions_key: str = "taskDefinitions",
) -> nx.DiGraph:
    """Generate a directed graph based on a pipeline config's adjacency list
    and task definitions.

    `dagAdjacency` is a dictionary containing all nodes and downstream
    nodes.

    `taskDefinitions` is a dictionary containing metadata required for
    each node such as the worker, model version, etc. This metadata is
    attached to each node so it can be retrieved directly from the graph.
    """
    G = nx.DiGraph()

    # Get our adjacency list and task definitions
    adjacency_dict = config.get(adjacency_key, {})
    task_definitions = config.get(task_definitions_key, {})
    if len(adjacency_dict.keys()) == 0:
        logger.warning(
            "Adjacency definition `{}` was not found ...".format(adjacency_key)
        )

    # Build the graph
    for node in adjacency_dict.keys():
        adjacent_nodes = adjacency_dict[node]

        # If no adjacent nodes, then this is a terminal node
        if len(adjacent_nodes) == 0:
            G.add_node(node, attr_dict=task_definitions.get(node, {}))
            continue

        # Otherwise, we'll add an edge from this node to all adjacent nodes
        # and add the task defnition metadata to the edge
        G.add_edges_from(
            [(node, n, task_definitions.get(n, {})) for n in adjacent_nodes]
        )
    return G


def process_non_none_value(value: T) -> None:
    """
    Processes a value that must not be None.

    The function checks if the provided value is None and raises a ValueError if it is.
    If the value is not None, it proceeds to process and print the value.

    :param value: The value to process. Can be of any type, but must not be None.

    :raises ValueError: If the value is None.

    Example:
    >>> process_non_none_value(42)
    Processing value: 42

    >>> process_non_none_value("hello")
    Processing value: hello

    >>> process_non_none_value(None)
    Traceback (most recent call last):
        ...
    ValueError: None value is not allowed
    """
    if value is None:
        raise ValueError("None value is not allowed")


def topological_sort_with_parallelism(
    graph: nx.DiGraph, executable_nodes=None
) -> typing.List[typing.List[T]]:
    """
    Recurse over the graph to find an optimal execution strategy for processing nodes in an order where
    no node shall be processed before all of its predecessors have been processed. The function handles
    parallel execution by identifying nodes that can be processed in parallel at each step. If the graph
    contains a cycle, the function will not be able to generate an execution plan and will raise an exception.

    :param graph: A directed acyclic graph (DiGraph) from NetworkX.
    :param executable_nodes: A list of lists where each inner list contains nodes that can be executed
                              in parallel at each step. This parameter is used for recursion.
    :return: A list of lists where each inner list contains nodes that can be executed in parallel at each step.

    >>> g = nx.DiGraph()
    >>> g.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 4)])
    >>> topological_sort_with_parallelism(g)
    [[1], [2, 3], [4]]

    >>> g = nx.DiGraph()
    >>> g.add_edges_from([(1, 2), (2, 3), (3, 4)])
    >>> topological_sort_with_parallelism(g)
    [[1], [2], [3], [4]]

    >>> g = nx.DiGraph()
    >>> g.add_edges_from([(1, 2), (2, 3), (3, 1)])
    >>> topological_sort_with_parallelism(g)
    Traceback (most recent call last):
        ...
    NetworkXUnfeasible: Graph contains a cycle, cannot compute a topological sort.
    """
    nodes = list(nx.topological_sort(graph))
    round_executable_nodes = [n for n in nodes if graph.in_degree(n) == 0]
    graph.remove_nodes_from(round_executable_nodes)

    if len(round_executable_nodes) == 0:
        return executable_nodes
    else:
        executable_nodes = [] if executable_nodes is None else executable_nodes
        executable_nodes.append(round_executable_nodes)
        return topological_sort_with_parallelism(graph, executable_nodes)


def plt_execution_tree(G):
    import networkx as nx
    import matplotlib.pyplot as plt

    # Draw the graph
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G)  # Compute positions for nodes
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="lightblue",
        node_size=3000,
        edge_color="gray",
        arrowsize=20,
        font_size=12,
    )

    # Show the plot
    plt.title("Directed Graph Visualization")
    plt.show()
