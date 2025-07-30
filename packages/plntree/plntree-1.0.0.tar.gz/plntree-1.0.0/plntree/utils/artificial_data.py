import networkx
import numpy as np
import random
import networkx as nx
import torch

def generate_hierarchy(K, seed=None):
    """
    Generates a hierarchy based on a vector of nodes per layer
    Parameters
    ----------
    K: list[int]
    seed: int or None

    Returns
    -------
    list[str]
    """

    def generate_groups(K_l, K_l_parent):
        """
        Generate a vector of integers with specified properties.
        """
        if K_l_parent >= K_l:
            raise ValueError("K_l_parent must be less than K_l")
        vector = list(range(K_l_parent))
        additional_values = np.random.randint(0, K_l_parent, size=(K_l - K_l_parent))
        vector.extend(additional_values)
        return np.array(vector)

    groups = []
    torch.random.manual_seed(seed)
    np.random.seed(seed)
    for i in range(len(K)-1):
        level = len(K) - i - 1
        parent_level = len(K) - i - 2
        K_l = K[level]
        K_l_parent = K[parent_level]
        groups += [generate_groups(K_l, K_l_parent)]
    groups = list(reversed(groups))

    hierarchy_per_level = []
    for k in range(K[0]):
        hierarchy_per_level.append(f'A__{k}')
    hierarchy_per_level = [hierarchy_per_level]
    hierarchy_names = ['B', 'C', 'D', 'E', 'F', 'G', 'H']
    for level in range(1, len(K)):
        hierarchy_l = []
        hierarchy_parent = hierarchy_per_level[-1]
        for k in range(K[level]):
            parent = hierarchy_parent[groups[level-1][k]]
            hierarchy_l.append(parent + '|' + hierarchy_names[level-1] + '__' + str(k))
        hierarchy_per_level.append(hierarchy_l)
    hierarchy = hierarchy_per_level[-1]
    return hierarchy


def generate_adjacency_matrix(n_nodes, args=(.5,), method="erdos_renyi", seed=None, returnNetworkx=False):
    """
    Generates a random adjacency matrix
    Parameters
    ----------
    n_nodes: number of nodes
    args: arguments of the method. Refers to https://networkx.org/documentation/stable/reference/generators.html
    method: valued in ["erdos_renyi", "preferential_attachment"]
    seed: random seed
    returnNetworkx

    Returns
    -------

    """
    G = None
    if method == "erdos_renyi":
        G = nx.gnp_random_graph(n_nodes, *args, seed=seed)
    elif method == "preferential_attachment":
        G = nx.barabasi_albert_graph(n_nodes, *args)
    if returnNetworkx:
        return G
    return nx.to_numpy_array(G)


def generate_community_adjacency_matrix(n_nodes_per_community, n_random_edges, method="erdos_renyi", method_args=(.5,),
                                        seed=None):
    """
    Generates a random adjacency matrix based on communities interactions
    Parameters
    ----------
    n_nodes_per_community: list[int]
    n_random_edges: int
    method: valued in ["erdos_renyi", "preferential_attachment"]
    method_args: Any
        arguments of the method. Refers to https://networkx.org/documentation/stable/reference/generators.html
    seed: int

    Returns
    -------

    """
    np.random.seed(seed)
    G = None
    for n_nodes in n_nodes_per_community:
        C = generate_adjacency_matrix(n_nodes, args=method_args, method=method, returnNetworkx=True)
        if G is None:
            G = C
        else:
            G = networkx.disjoint_union(G, C)

    for _ in range(n_random_edges):
        nonedges = list(nx.non_edges(G))
        if len(nonedges) == 0:
            break
        chosen_nonedge = random.choice(nonedges)
        G.add_edge(chosen_nonedge[0], chosen_nonedge[1])

    return nx.to_numpy_array(G)


def generate_precision_matrix(adjacency_matrix, conditioning=0.1, correlation=0.3):
    """
    Generates a precision matrix based on an adjacency matrix
    Parameters
    ----------
    adjacency_matrix: np.ndarray
    conditioning: float
    correlation: float

    Returns
    -------
    np.ndarray
    """
    omega = correlation * adjacency_matrix
    eigen_values, eigen_vectors = np.linalg.eig(omega)
    return omega + np.identity(len(omega)) * (np.abs(np.min(eigen_values)) + conditioning)


def generate_markov_dirichlet_hierarchical_data(n_samples, tree, Omega, mu, offset_total_count, offset_probs,
                                                alpha_structures, seed=None):
    """
    Generates a dataset based on a Markov Dirichlet hierarchical model
    Parameters
    ----------
    n_samples: int
    tree: plntree.utils.Tree
    Omega: np.ndarray
    mu: np.ndarray
    offset_total_count: int
    offset_probs: np.ndarray
    alpha_structures: list[list[int]]
    seed: int or None

    Returns
    -------
    torch.Tensor
    """
    if seed is not None:
        torch.random.manual_seed(seed)
    # Computing the counts parameters
    log_a = torch.distributions.MultivariateNormal(torch.tensor(mu), precision_matrix=torch.tensor(Omega)).sample((n_samples,))
    a = torch.exp(log_a)
    pi = torch.nn.functional.softmax(a - torch.max(a), dim=1)
    N = torch.distributions.NegativeBinomial(offset_total_count, offset_probs).sample((n_samples,))
    # Getting the structure of the data
    K = tree.K
    L = len(K)
    X = torch.zeros((n_samples, L, max(K)))
    # Building the Dirichlet parameters for propagation
    alpha_modules = []
    for l in range(0, L - 1):
        if alpha_structures is not None:
            structure = [K[l]] + alpha_structures[l] + [K[l + 1]]
        else:
            structure = [K[l], K[l + 1]]
        module = torch.nn.Sequential()
        for i in range(len(structure) - 1):
            module.append(torch.nn.Linear(structure[i], structure[i + 1]))
            module.append(torch.nn.Softplus())
        alpha_modules.append(module)
    # Draw the first layer
    for i, n in enumerate(N):
        X[i, 0, :K[0]] = torch.distributions.Multinomial(int(n), pi[i]).sample()
    # Propagate the counts
    for l in range(1, L):
        alpha = alpha_modules[l - 1](X[:, l - 1, :K[l - 1]])
        for k, X_parent in enumerate(X[:, l-1, :K[l-1]]):
            mask = tree.affiliation_matrix[l][k]
            alpha_children = alpha[:, mask]
            for i, X_i_parent in enumerate(X_parent):
                parent_value = int(X_i_parent)
                prop = torch.distributions.Dirichlet(alpha_children[i] + 1e-8).sample()
                if parent_value != 0:
                    X[k, l, mask] = torch.distributions.Multinomial(parent_value, prop).sample()
    return X[:, -1, :K[-1]]