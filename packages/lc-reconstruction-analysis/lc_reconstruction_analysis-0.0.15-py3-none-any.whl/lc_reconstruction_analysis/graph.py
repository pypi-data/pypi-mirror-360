"""
    Builds summary graphs of axon trees
"""

import seaborn as sns
import networkx as nx
from tqdm import tqdm
import matplotlib.pyplot as plt
from collections import Counter

import lc_reconstruction_analysis.clustering as clustering


def build_all_trees(
    dataDF,
    graphs,
    pos=None,
    DATA_DIR=None,
    use_coarse_names=True,
    RESULTS_DIR=None,
    df=None,
):
    """
    Build and plot all summary trees for each individual cell
    pos = centroids of the ROIs
    df, dataframe of axon lengths. if provided used to size nodes by
        axon length
    """
    for name in list(graphs.keys()):
        g = graphs[name]
        r = build_tree(g, DATA_DIR, use_coarse_names)
        if df is not None:
            size = get_node_size(df, name, r)
        else:
            size = 600
        plot_tree(r, name, pos, RESULTS_DIR=RESULTS_DIR, node_size=size)


def get_node_size(df, name, tree, base=7200):
    """
    Determine node size by axon length in df
    """
    node_size = [df.loc[name][x] * base for x in list(tree.nodes)]
    return node_size


def build_tree(graph, DATA_DIR=None, use_coarse_names=True):
    """
    Compute summary tree for a single cell
    """
    edges = build_summary_tree(graph, DATA_DIR, use_coarse_names)
    r = nx.DiGraph()
    r = nx.from_edgelist(edges, r)
    return r


def build_combined_tree(
    dataDF,
    graphs,
    DATA_DIR=None,
    use_coarse_names=True,
    roi_version=1,
    weight_type="fraction",
):
    """
    Build combined tree across all neurons
    can weight edges either by "fraction" or "conditional"
    """
    edges = []
    ncells = len(dataDF["Graph"])
    nodes = []
    # Iterate through cells and get nodes/edges
    for name in tqdm(dataDF["Graph"]):
        this_edge = build_summary_tree(
            graphs[name],
            DATA_DIR=DATA_DIR,
            use_coarse_names=use_coarse_names,
            roi_version=roi_version,
        )
        this_nodes = set([x for y in this_edge for x in y])
        edges += this_edge
        nodes += this_nodes
    edges = Counter(edges)
    nodes = Counter(nodes)

    # Determine edge weights
    weighted_edges = []
    for edge in edges:
        if weight_type == "fraction":
            weighted_edges.append((edge[0], edge[1], edges[edge] / ncells))
        elif weight_type == "conditional":
            weighted_edges.append(
                (edge[0], edge[1], edges[edge] / nodes[edge[0]])
            )

    # Build graph
    r = nx.DiGraph()
    r.add_weighted_edges_from(weighted_edges)
    return r


def build_summary_tree(
    graph, DATA_DIR=None, use_coarse_names=True, roi_version=1
):
    """
    compute the summary tree based on the presence of an edge
    """
    if roi_version == 1:
        rois = [
            "CB",
            "MY",
            "P",
            "MB",
            "TH",
            "HY",
            "CNU",
            "CTXsp",
            "HPF",
            "OLF",
            "Isocortex",
            "fiber tracts",
            "VS",
            "grv",
            "retina",
        ]
    elif roi_version == 2:
        rois = [
            "CB",
            "MY",
            "P",
            "MB",
            "TH",
            "HY",
            "CNU",
            "CTXsp",
            "HPF",
            "OLF",
            "Isocortex",
            "cbf",
            "lfbs",
            "mfbs",
            "VS",
            "grv",
            "retina",
        ]
    id_to_roi, id_to_acronym, id_to_parent = clustering.get_roi_map(
        DATA_DIR, rois=rois
    )
    if use_coarse_names:
        for node in graph.nodes():
            graph.nodes[node]["structure"] = id_to_acronym[
                id_to_roi[graph.nodes[node]["allen_id"]]
            ]
    else:
        for node in graph.nodes():
            graph.nodes[node]["structure"] = id_to_acronym[
                graph.nodes[node]["allen_id"]
            ]

    region_edges = []
    for u, v in graph.edges:
        if (graph.nodes[u]["structure_id"] in [1, 2]) & (
            graph.nodes[v]["structure_id"] in [1, 2]
        ):
            u_location = graph.nodes[u]["structure"]
            v_location = graph.nodes[v]["structure"]
            edge = (u_location, v_location)
            if (
                (u_location != v_location)
                and (edge not in region_edges)
                and ("NaN" not in edge)
                and (None not in edge)
            ):
                region_edges.append(edge)
    return region_edges


def plot_tree(tree, name, pos=None, RESULTS_DIR=None, node_size=600):
    """
    Plot the summary tree for a single cell
    """

    # Set up figure
    plt.figure(figsize=(10, 4))
    ax = plt.gca()

    # Draw tree
    nx.draw_networkx(
        tree,
        pos,
        node_size=node_size,
        font_color="darkred",
        font_weight="bold",
        node_color="cornflowerblue",
    )

    # Clean up
    plt.title(name)
    plt.xlim([3224, 12284])
    plt.ylim([-6382, -2195])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)

    # Save figure
    if RESULTS_DIR is not None:
        plt.savefig(RESULTS_DIR + name + ".png")


def plot_combined_tree(tree, pos):
    """
    Plot the summary combined tree
    """
    # Set up figure
    plt.figure(figsize=(10, 4))
    ax = plt.gca()

    # Plot the tree
    weights = [tree[u][v]["weight"] * 4 for u, v in tree.edges()]
    nx.draw_networkx(
        tree,
        pos,
        width=weights,
        node_size=600,
        font_color="darkred",
        font_weight="bold",
        node_color="cornflowerblue",
    )
    # Add this to split the directional weights
    # connectionstyle='arc3,rad=0.05'

    # Clean up
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    plt.title("Combined")
    plt.xlim([3224, 12284])
    plt.ylim([-6382, -2195])


def plot_combined_adjacency(tree, roi_version=1):
    """
    Plot the combined adjacency matrix
    """

    if roi_version == 1:
        sorted_columns = [
            "OLF",
            "Isocortex",
            "HPF",
            "CTXsp",
            "CNU",
            "TH",
            "HY",
            "MB",
            "CB",
            "P",
            "MY",
            "fiber tracts",
            "VS",
        ]
    elif roi_version == 2:
        sorted_columns = [
            "OLF",
            "Isocortex",
            "HPF",
            "CTXsp",
            "CNU",
            "TH",
            "HY",
            "MB",
            "CB",
            "P",
            "MY",
            "lfbs",
            "mfbs",
            "cbf",
            "VS",
        ]

    A = nx.to_pandas_adjacency(tree)
    A = A[sorted_columns]
    A = (
        A.reset_index()
        .sort_values(
            by="index",
            key=lambda column: column.map(lambda e: sorted_columns.index(e)),
        )
        .set_index("index", drop=True)
    )
    plt.figure()
    sns.heatmap(A.T, vmin=0, vmax=1)
    plt.tight_layout()
