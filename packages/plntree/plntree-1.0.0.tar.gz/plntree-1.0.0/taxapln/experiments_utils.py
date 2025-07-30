import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import ot
import pandas as pd
import seaborn as sns
import torch
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm

from scipy.stats import wasserstein_distance, ks_2samp, entropy, gaussian_kde
from diversity_metrics import bray_curtis_dissimilarity_matrix, shannon_index, simpson_index

from skbio.stats.distance import permanova, permdisp
from skbio.stats.distance import DistanceMatrix
from skbio.diversity import beta_diversity
from skbio.stats.ordination import pcoa
from sklearn.decomposition import PCA


def seed_all(seed):
    """
    Seed all random number generators.
    Parameters
    ----------
    seed: int

    Returns
    -------

    """
    if seed is None:
        return
    np.random.seed(seed)
    torch.random.manual_seed(seed)

def savefig(name, extension='tif', dpi=350):
    """
    Save the current figure with the given name and extension.
    Parameters
    ----------
    name: str
    extension: str

    Returns
    -------

    """
    plt.savefig(f"pictures/{name}.{extension}".replace(' ', '_'), bbox_inches='tight', dpi=dpi)

def save_dataset(name, X, hierarchy):
    """
    Save the hierarchical count data and its associated hierarchy into the with the given name.
    Parameters
    ----------
    name: str
    X: torch.Tensor
    hierarchy: list

    Returns
    -------

    """
    np.save(f'datasets/{name}.npy', X[:, -1].detach().numpy())
    np.save(f'datasets/{name}_hierarchy.npy', np.array(hierarchy))

def load_dataset(name):
    """
    Load the hierarchical count data and its associated hierarchy with the given name.
    Parameters
    ----------
    name: str

    Returns
    -------
    (torch.Tensor, np.ndarray)
    """
    return np.load(f'datasets/{name}.npy'), np.load(f'datasets/{name}_hierarchy.npy')

def to_proportion(X):
    X_ = X / X.sum(-1, keepdims=True)
    X_[X_.isnan()] = 0.
    return X_

def plot_alpha_diversity(tree, X_list, colors,
                         alpha_div={'Shannon':shannon_index, 'Simpson':simpson_index},
                         plot_type='boxplot', show_points=False, rotation=45, level=None,
                         return_axis=False, ax=None
                         ):
    """
    Plot the alpha diversity of the given samples for each level of the tree.
    Parameters
    ----------
    tree: plntree.utils.Tree
    X_list: dict[str, torch.Tensor]
    colors: dict[str, str]
    alpha_div: dict[str, callable]
    plot_type: str
    show_points: bool
    rotation: int,
    level: int or None

    Returns
    -------
    list[dict[str, list[float]]]
    """
    alpha = []
    for l in range(tree.L):
        alpha_l = {}
        for alpha_div_name, alpha_div_fun in alpha_div.items():
            alpha_l[alpha_div_name] = []
            for group, X in X_list.items():
                alpha_value = alpha_div_fun(X[:, l, :tree.K[l]].numpy())
                alpha_l[alpha_div_name] += [alpha_value]
        alpha += [alpha_l]

    if level is not None:
        alpha = [alpha[level]]
        fig, axs = plt.subplots(len(alpha_div), 1, figsize=(15, 5))
        axs = [[ax] for ax in axs]
        L = 1
        level_name = level
    else:
        fig, axs = plt.subplots(len(alpha_div), tree.L, figsize=(15, 5))
        L = tree.L
        level_name = None
    for level in range(L):
        if level_name is None:
            axs[0][level].set_title(f'$\ell = {level}$')
        else:
            axs[0][level].set_title(f'$\ell = {level_name}$')
        for k, alpha_name in enumerate(alpha[level]):
            alpha_values = alpha[level][alpha_name]
            groups = list(X_list)
            df = None
            colors_groups = []
            for g, group in enumerate(groups):
                if df is None:
                    df = pd.Series(alpha_values[g], name=group).to_frame()
                else:
                    df = pd.concat([pd.Series(alpha_values[g], name=group).reset_index(drop=True) for g, group in enumerate(groups)], axis=1)
                colors_groups += [colors[group]]
            if plot_type == 'boxplot':
                sns.boxplot(data=df, width=0.7, ax=axs[k][level], showfliers=False, palette=colors_groups)
            elif plot_type == 'violin':
                sns.violinplot(data=df, width=0.7, ax=axs[k][level], showfliers=False, palette=colors_groups)
            axs[k][0].set_ylabel(alpha_name)
            if k == len(alpha[level])-1:
                axs[k][level].set_xticklabels(axs[k][level].get_xticklabels(), rotation=rotation)
            else:
                axs[k][level].set_xticklabels([])
    if return_axis:
        return alpha, (fig, axs)
    return alpha

def vizualize_distributions(tree, X_dic, title='Abundance', figsize=(14, 10), rotation=-90, layer=None):
    """
    Vizualize the abundance distributions of the given samples for each level of the tree.
    Parameters
    ----------
    tree: plntree.utils.Tree
    X_dic: dict[str, torch.Tensor]
    title: str
    figsize: tuple[int]
    rotation: int
    layer: None or int

    Returns
    -------

    """
    if layer is not None:
        fig, axs = plt.subplots(figsize=figsize)
    else:
        fig, axs = plt.subplots(tree.L, 1, figsize=figsize)
    for level in range(tree.L):
        if layer is not None and level != layer:
            continue
        melt = torch.cat(
            [X_dic[group][:, level, :tree.K[level]] for group in X_dic.keys()],
        )
        df = pd.DataFrame(data=melt)
        groups = []
        for group in X_dic.keys():
            groups += [group] * len(X_dic[group])
        df['group'] = groups
        df = pd.melt(df, id_vars='group', var_name='', value_name='value')
        if layer is not None:
            sns.boxplot(df, ax=axs, x='', y='value', hue='group', showfliers=False)
            axs.set_xticklabels(tree.clades[level, :tree.K[level]].numpy().astype(np.int32), rotation=rotation)
            axs.set_title(f'$\ell = {level}$')
            [axs.axvline(x + .5, color='gray', linestyle='--', alpha=0.25) for x in axs.get_xticks()]
            axs.set_ylabel(title)
        else:
            sns.boxplot(df, ax=axs[level], x='', y='value', hue='group', showfliers=False)
            axs[level].set_xticklabels(tree.clades[level, :tree.K[level]].numpy().astype(np.int32), rotation=rotation)
            axs[level].set_title(f'$\ell = {level}$')
            [axs[level].axvline(x + .5, color='gray', linestyle='--', alpha=0.25) for x in axs[level].get_xticks()]
            axs[level].set_ylabel(title)
    if layer is None:
        axs[level].set_xlabel('Clade')
        fig.legend(*axs[0].get_legend_handles_labels(), loc='lower center', ncol=len(X_dic), fontsize=13)
        for ax in axs:
            ax.legend_ = None
    else:
        axs.set_xlabel('Clade')
        fig.legend(*axs.get_legend_handles_labels(), loc='lower center', ncol=len(X_dic), fontsize=13)
        axs.legend_ = None


def correlation(X_base, X_comp, plntree):
    """
    Compute the correlation between the base and compared samples for each level of the tree.
    Parameters
    ----------
    X_base: torch.Tensor
    X_comp: torch.Tensor
    plntree: plntree.utils.Tree

    Returns
    -------

    """
    correlations = []
    for layer, K_l in enumerate(plntree.tree.K):
        mask = plntree.tree.K_mask[layer]
        corr = torch.zeros(len(X_base))
        for i in range(len(X_base)):
            X_base_l = X_base[i, layer, mask]
            X_comp_l = X_comp[i, layer, mask]
            stack = torch.stack((X_base_l, X_comp_l))
            corr[i] = torch.corrcoef(stack)[0][1]
        correlations.append(corr)
    return correlations


def correlation_3d_plot(X_base, X_list, groups, plntree, bins=30, hist_lim=1000, saveName=''):
    """
    Plot the 3D histograms of the correlations between the base and compared samples for each level of the tree.
    Parameters
    ----------
    X_base: torch.Tensor
    X_list: list[torch.Tensor]
    groups: list[str]
    plntree: plntree.PLNTree
    bins: int
    hist_lim: int
    saveName: str

    Returns
    -------

    """
    # Create subplots
    K = plntree.tree.K
    fig, axs = plt.subplots(1, len(K), figsize=(15, 5), subplot_kw={'projection': '3d'})

    correlations_list = [correlation(X_base, X_comp, plntree) for X_comp in X_list]
    viridis = matplotlib.colormaps.get_cmap('viridis')
    colors = [viridis(1e-8 + (i + 1) / len(correlations_list)) for i in range(len(correlations_list))]

    # Plot 3D histograms for each list of tensors
    for i in range(len(axs)):

        for j, (color, label) in enumerate(zip(colors, groups)):
            hist, bins = np.histogram(correlations_list[j][i], bins=bins, density=True)
            hist[hist > hist_lim] = hist_lim
            xs = (bins[:-1] + bins[1:]) / 2
            axs[i].bar(xs, hist, zs=j, zdir='y', width=0.03, color=color, alpha=0.5)

        axs[i].set_ylabel('')
        axs[i].set_xlabel('Correlation')
        axs[i].set_zlabel('Frequency')
        axs[i].set_title(f'$\ell={i + 1}$')
    for ax in axs:
        ax.set_yticks(np.arange(len(groups)))
        ax.set_yticklabels(groups, rotation=-75)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=10)

    if len(saveName) > 0:
        savefig(f"{saveName}_3d_correlations")
    plt.show()


def mae(X_base, X_comp):
    """
    Compute the mean absolute error between the base and compared samples.
    Parameters
    ----------
    X_base: torch.Tensor
    X_comp: torch.Tensor

    Returns
    -------

    """
    n_models = X_comp.size(0) // X_base.size(0)
    n_samples = X_base.size(0)
    m = torch.zeros(n_models)
    for i in range(n_models):
        m[i] = torch.mean((torch.flatten(X_base - X_comp[i * n_samples:(i + 1) * n_samples])).abs())
    return m


def kl_divergence(p_samples, q_samples, bias=1e-15):
    """
    Compute the Kullback-Leibler divergence between the two samples.
    Parameters
    ----------
    p_samples: np.ndarray
    q_samples: np.ndarray
    bias: float

    Returns
    -------
    float
    """
    try:
        kde_p = gaussian_kde(p_samples)
        kde_q = gaussian_kde(q_samples)
    except:
        return np.inf
    min_val = min(np.min(p_samples), np.min(q_samples))
    max_val = max(np.max(p_samples), np.max(q_samples))
    grid = np.linspace(min_val, max_val, 1000)
    pdf_p = kde_p(grid) + bias
    pdf_q = kde_q(grid)
    pdf_q[pdf_q < bias] = bias
    if np.isnan(np.sum(pdf_p * np.log(pdf_p / pdf_q + bias))):
        print(pdf_p / pdf_q)
    return entropy(pdf_p, pdf_q)


def total_variation(samples1, samples2):
    """
    Compute the total variation between the two samples.
    Parameters
    ----------
    samples1: np.ndarray
    samples2: np.ndarray

    Returns
    -------
    float
    """
    try:
        kde_1 = gaussian_kde(samples1)
        kde_2 = gaussian_kde(samples2)
    except:
        return np.inf
    min_val = min(np.min(samples1), np.min(samples2))
    max_val = max(np.max(samples1), np.max(samples2))
    grid = np.linspace(min_val, max_val, 1000)
    pdf_1 = kde_1(grid)
    pdf_2 = kde_2(grid)
    return 0.5 * np.sum(np.abs(pdf_1 - pdf_2) / len(grid))


def kolmogorov_smirnov(samples1, samples2):
    """
    Compute the Kolmogorov-Smirnov statistic between the two samples.
    Parameters
    ----------
    samples1: np.ndarray
    samples2: np.ndarray

    Returns
    -------
    float
    """
    ks_statistic, _ = ks_2samp(samples1, samples2)
    return ks_statistic

def multilayer_alpha_diversity(tree, X, alpha='shannon'):
    """
    Compute the alpha diversity for each level of the tree with the given samples
    Parameters
    ----------
    tree: plntree.utils.Tree
    X: torch.Tensor
    alpha: str

    Returns
    -------
    pd.DataFrame
    """
    alpha_fun = None
    if alpha.lower() == 'shannon':
        alpha_fun = shannon_index
    elif alpha.lower() == 'simpson':
        alpha_fun = simpson_index
    alpha_per_level = []
    for level in range(tree.L):
        alpha_per_level.append(alpha_fun(X[:, level, :tree.K[level]]).numpy())
    alpha_df = pd.DataFrame(alpha_per_level).T
    alpha_df.columns = [f'{alpha} l = {level}' for level in range(tree.L)]
    return alpha_df

def compute_alpha_diversity(X_dic, tree, alpha=('shannon', 'simpson')):
    """
    Compute the alpha diversities for each level of the tree with the given samples which must be of the same size.
    Parameters
    ----------
    X_dic: dict[str, torch.Tensor]
    tree: plntree.utils.Tree
    alpha: tuple[str]

    Returns
    -------
    pd.DataFrame
    """
    groups = []
    for key, X in X_dic.items():
        groups += [key] * len(X)
        assert X.shape[0] == list(X_dic.values())[0].shape[0], 'Compared ecosystems must have the same number of samples.'

    alpha_values = []
    for key, X in X_dic.items():
        sub_alpha = pd.DataFrame()
        for alpha_name in alpha:
            sub_alpha = multilayer_alpha_diversity(tree, X, alpha=alpha_name).join(sub_alpha)
        alpha_values.append(sub_alpha)
    alpha_df = pd.concat(alpha_values, ignore_index=True)
    alpha_df['Group'] = groups
    return alpha_df

def compute_distance(grouped_metric_matrix, reference_group, distance=wasserstein_distance):
    """
    Compute the distance between the reference group and the other groups.
    Parameters
    ----------
    grouped_metric_matrix: pd.DataFrame
    reference_group: str
    distance: callable

    Returns
    -------
    pd.Series
    """
    reference = grouped_metric_matrix[grouped_metric_matrix['Group'] == reference_group]
    distances = []
    other_groups = []
    metrics = grouped_metric_matrix.columns[:-1]
    for group in grouped_metric_matrix['Group'].unique():
        if group == reference_group:
            continue
        other_groups += [group]
        group_values = grouped_metric_matrix[grouped_metric_matrix['Group'] == group]
        d_values = []
        for metric in metrics:
            d_values += [distance(reference[metric], group_values[metric])]
        distances.append(d_values)
    return pd.DataFrame(data=distances, index=other_groups, columns=metrics)

def bold_min(df):
    """
    Highlight the minimum value of each row in the DataFrame.
    Parameters
    ----------
    df: pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    def highlight_min(data):
        attr = 'font-weight: bold'
        if data.ndim == 1:  # Series from .apply(axis=0) or axis=1
            is_min = data == data.min()
            return [attr if v else '' for v in is_min]
        else:  # DataFrame from .apply(axis=None)
            is_min = data == data.min()
            return pd.DataFrame(np.where(is_min, attr, ''), index=data.index, columns=data.columns)
    return df.style.apply(highlight_min, axis=1)


def repeated_alpha_diversity_distance(tree, X_dic, reference_group, distance=wasserstein_distance):
    """
    Compute the alpha_diversity distance between the reference group and the other groups.
    If the compared tensors have a different size than the reference, the distance is computed several times by splitting
    the compared tensors into the size of the reference, thus providing the mean result and associated standard deviation.

    All compared tensors must have the same size.

    Parameters
    ----------
    tree: plntree.utils.Tree
    X_dic: dict[str, torch.Tensor]
    reference_group: str
    distance: callable

    Returns
    -------
    pd.DataFrame
    """
    X_ref = X_dic[reference_group]
    size = X_ref.shape[0]
    compared_size = list(X_dic.values())[1].shape[0]
    n_splits = compared_size // size
    distances = []
    print('Alpha diversity distance was assessed', n_splits, 'times.')
    ranking = {key: [] for key in X_dic}
    ranking.pop(reference_group, None)
    for i in range(n_splits):
        X_sub_dic = {}
        for key, X in X_dic.items():
            if key == reference_group:
                X_sub_dic[key] = X
            else:
                X_sub_dic[key] = X[i * size:(i + 1) * size]
        alpha_df = compute_alpha_diversity(X_sub_dic, tree)
        dist = compute_distance(alpha_df, reference_group, distance=distance)
        dist_ranking = dist.mean(axis=1).sort_values(ascending=True).index
        for r, group in enumerate(dist_ranking):
            ranking[group] += [r]
        distances.append(dist)
    ranking = pd.DataFrame(ranking)
    ranking_mean = np.mean(ranking, axis=0)
    ranking_std = np.std(ranking, axis=0)
    distances = pd.concat(distances)
    mean_distances = {}
    std_distances = {}
    for group, X in X_dic.items():
        if group == reference_group:
            continue
        mean_distances[group] = distances.loc[group].mean(axis=0)
        std_distances[group] = distances.loc[group].std(axis=0)
    mean_distances = pd.DataFrame(mean_distances)
    std_distances = pd.DataFrame(std_distances)

    visual = pd.DataFrame()
    for group in mean_distances:
        visual[group] = [f'{np.round(mean_distances[group].iloc[i], 3)} ({np.round(std_distances[group].iloc[i], 3)})'
                         for i in range(len(mean_distances[group]))]
    visual.index = mean_distances.index
    visual.loc['Rank'] = [f'{np.round(ranking_mean[i], 2)} ({np.round(ranking_std[i], 2)})' for i in range(len(ranking_mean))]
    visual = visual[ranking_mean.sort_values(ascending=True).index]
    return bold_min(visual)



def emd(batch1, batch2):
    """
    Compute the empirical Wasserstein distance between the two batches of samples.
    Parameters
    ----------
    batch1: torch.Tensor
    batch2: torch.Tensor

    Returns
    -------
    torch.Tensor
    """
    batch1 = np.array(batch1)
    batch2 = np.array(batch2)
    # Multivariate Wasserstein distance
    M = ot.dist(batch1, batch2, metric='euclidean')
    a_weight, b_weight = np.ones(batch1.shape[0], ) / batch1.shape[0], np.ones(batch2.shape[0], ) / batch2.shape[0]
    return ot.emd2(a_weight, b_weight, M)


def compute_emd_distance(tree, X_dic, reference_group):
    """
    Compute the empirical Wasserstein between the reference group and the other groups.
    Each group must be of the same as the reference.

    Parameters
    ----------
    tree: plntree.utils.Tree
    X_dic: dict[str, torch.Tensor]
    reference_group: str

    Returns
    -------
    pd.DataFrame
    """
    values = []
    groups = []
    for group, X in X_dic.items():
        if group == reference_group:
            continue
        values_group = []
        groups += [group]
        for level in range(tree.L):
            X_ref = X_dic[reference_group][:, level, :tree.K[level]]
            X_comp = X[:, level, :tree.K[level]]
            values_group += [emd(X_ref, X_comp)]
        values += [values_group]
    values = pd.DataFrame(data=values, columns=[f'l = {i}' for i in range(tree.L)], index=groups)
    return values


def repeated_empirical_wasserstein_compute(tree, X_dic, reference_group):
    """
    Compute the empirical Wasserstein distance between the reference group and the other groups.
    If the compared tensors have a different size than the reference, the distance is computed several times by splitting
    the compared tensors into the size of the reference, thus providing the mean result and associated standard deviation.

    All compared tensors must have the same size.
    Parameters
    ----------
    tree: plntree.utils.Tree
    X_dic: dict[str, torch.Tensor]
    reference_group: str

    Returns
    -------
    pd.DataFrame
    """
    size = X_dic[reference_group].shape[0]
    compared_size = list(X_dic.values())[1].shape[0]
    n_splits = compared_size // size
    ranking = {key: [] for key in X_dic}
    ranking.pop(reference_group, None)
    distances = []
    print('Empirical Wasserstein was assessed', n_splits, 'times.')
    for i in range(n_splits):
        X_sub_dic = {}
        for key, X in X_dic.items():
            # Normalize the counts as we do not want the total sum to be taken into account
            if key == reference_group:
                X_sub_dic[key] = to_proportion(X)
            else:
                X_sub_dic[key] = to_proportion(X[i * size:(i + 1) * size])
        dist = compute_emd_distance(tree, X_sub_dic, reference_group)
        dist_ranking = dist.mean(axis=1).sort_values(ascending=True).index
        for r, group in enumerate(dist_ranking):
            ranking[group] += [r]
        distances.append(dist)
    distances = pd.concat(distances)
    mean_distances = {}
    std_distances = {}
    for group, X in X_dic.items():
        if group == reference_group:
            continue
        mean_distances[group] = distances.loc[group].mean(axis=0)
        std_distances[group] = distances.loc[group].std(axis=0)
    mean_distances = pd.DataFrame(mean_distances)
    std_distances = pd.DataFrame(std_distances)
    ranking = pd.DataFrame(ranking)
    ranking_mean = np.mean(ranking, axis=0)
    ranking_std = np.std(ranking, axis=0)

    visual = pd.DataFrame()
    for group in mean_distances:
        visual[group] = [f'{np.round(mean_distances[group].iloc[i], 3)} ({np.round(std_distances[group].iloc[i], 3)})'
                         for i in range(len(mean_distances[group]))]
    visual.index = mean_distances.index
    visual.loc['Rank'] = [f'{np.round(ranking_mean[i], 2)} ({np.round(ranking_std[i], 2)})' for i in
                          range(len(ranking_mean))]
    visual = visual.transpose().sort_values(by='Rank').transpose()
    return bold_min(visual)


def repeat_test_braycurtis_diversity(tree, X_dic, reference_group, test, n_repeat=10, n_samples=100, permutations=100, seed=None):
    """
    Repeat the test (PERMANVOVA or PERMDISP) of the Bray-Curtis diversity between the reference group and the other groups.
    Parameters
    ----------
    tree: plntree.utils.Tree
    X_dic: dict[str, torch.Tensor]
    reference_group: str
    test: str
    n_repeat: int
    n_samples: int
    permutations: int
    seed: int

    Returns
    -------
    list[pd.DataFrame]
    """
    seed_all(seed)
    X_ref = X_dic[reference_group]
    X_others = X_dic.copy()
    X_others.pop(reference_group)

    indices = np.arange(len(X_ref))
    pvalues_per_level = []
    for level in range(tree.L):
        pvalues = {key:[] for key in X_others}
        for i in range(n_repeat):
            np.random.shuffle(indices)
            X_ref_l = X_ref[indices[:n_samples], level, :tree.K[level]]
            for group, X in X_others.items():
                group_indices = np.arange(len(X))
                np.random.shuffle(group_indices)
                X_group_l = X[group_indices[:n_samples], level, :tree.K[level]]
                X_cat = torch.cat((X_ref_l, X_group_l))
                grouping = np.array([0] * n_samples + [1] * n_samples)
                bc_matrix = bray_curtis_dissimilarity_matrix(X_cat)
                dissimilarity = DistanceMatrix(bc_matrix)
                if test == 'permanova':
                    pvalues[group].append(permanova(dissimilarity, grouping, permutations=permutations)['p-value'])
                elif test == 'permdisp':
                    pvalues[group].append(permdisp(dissimilarity, grouping, permutations=permutations)['p-value'])
        pvalues_per_level.append(pd.DataFrame(pvalues))
    return pvalues_per_level

def plot_pvalues_per_level(pvalues_per_level, figsize=(15, 8), rotation=90):
    """
    Plot the p-values for each level of the tree.
    Parameters
    ----------
    pvalues_per_level: list[pd.DataFrame]
    figsize: tuple[int]
    rotation: int

    Returns
    -------

    """
    fig, axs = plt.subplots(len(pvalues_per_level), 1, figsize=figsize)
    for level in range(len(pvalues_per_level)):
        pvalues = pvalues_per_level[level]
        sns.boxplot(pvalues, ax=axs[level], palette="Set2")
        sns.stripplot(jitter=True, marker='o', alpha=0.7, data=pvalues, ax=axs[level], color='k')
        axs[level].set_ylabel('p-value')
        axs[level].set_title(f'$\ell = {level}$')
        if level != len(pvalues_per_level)-1:
            axs[level].set_xticklabels([])
    axs[-1].set_xticklabels(axs[-1].get_xticklabels(), rotation=rotation)

def reject_rate_per_level(pvalues_per_level):
    """
    Compute the reject rate given pvalues for each level of the tree.
    Parameters
    ----------
    pvalues_per_level: list[pd.DataFrame]

    Returns
    -------
    pd.DataFrame
    """
    values = pd.DataFrame(columns=pvalues_per_level[0].columns)
    for level in range(len(pvalues_per_level)):
        pvalues = pvalues_per_level[level]
        values.loc[f'l = {level}'] = 1*(pvalues < 0.05).mean(axis=0)
    # Compute average reject rate
    values.loc['Reject rate'] = values.mean(axis=0)
    # Sort by reject rate
    values = values.transpose().sort_values(by='Reject rate').transpose()
    return values


def pcoa_plot(counts, labels, n_samples_total, dissimilarity='braycurtis', colormap=None, colors=None, alpha=0.25, show_mean=False, marker={}, seed=None):
    if seed is None:
        seed = np.random.randint(10_000)
    if colormap is None:
        colormap = cm.Set2

    # Assume df is your counts dataframe and metadata is a dataframe with a 'disease' column
    # Ensure they share the same index

    # Get unique disease groups and calculate samples per group
    if colors is not None:
        unique_diseases = list(colors.keys())
    else:
        unique_diseases = labels.unique()
    n_diseases = len(unique_diseases)
    if n_samples_total <= 0:
        samples_per_group = np.inf
    else:
        samples_per_group = n_samples_total // n_diseases  # integer division

    # Perform stratified sampling by disease
    groups = pd.DataFrame(columns=['Label'], data=labels.values, index=labels.index)
    balanced_metadata = groups.groupby('Label', group_keys=False).apply(
        lambda grp: grp.sample(n=min(samples_per_group, len(grp)), random_state=seed)
    )

    # Get the indices of the balanced sample and subset the counts dataframe
    balanced_indices = balanced_metadata.index
    pcoa_samples = counts.loc[balanced_indices]
    pcoa_samples = pcoa_samples / pcoa_samples.sum(axis=1).mean()
    pcoa_labels = groups.loc[balanced_indices]
    pcoa_labels.value_counts()

    # Compute the Bray-Curtis dissimilarity matrix:
    bc_dm = beta_diversity(dissimilarity, pcoa_samples.values, ids=pcoa_samples.index)

    # Perform PCoA:
    pcoa_results = pcoa(bc_dm, number_of_dimensions=2)
    pcoa_df = pcoa_results.samples.join(groups)

    # Create a gridspec layout:
    fig = plt.figure(figsize=(10, 10))
    gs = gridspec.GridSpec(2, 2, width_ratios=[4, 1], height_ratios=[1, 4],
                           wspace=0.05, hspace=0.05)
    ax_scatter = plt.subplot(gs[1, 0])
    ax_box_top = plt.subplot(gs[0, 0], sharex=ax_scatter)
    ax_box_right = plt.subplot(gs[1, 1], sharey=ax_scatter)

    # Create a dictionary mapping each disease (study_condition) to a color
    if colors is not None:
        disease_colors = colors
    else:
        disease_colors = {disease: colormap(i) for i, disease in enumerate(unique_diseases)}

    # Randomize the order of all points for the scatter plot
    pcoa_shuffled = pcoa_df.sample(frac=1, random_state=42)  # shuffle all rows
    for disease in marker:
        pcoa_shuffled = pcoa_shuffled[pcoa_shuffled['Label'] != disease]
    # Map each point's study_condition to its corresponding color
    colors_shuffled = pcoa_shuffled['Label'].map(disease_colors)

    # Plot all points in the randomized order
    ax_scatter.scatter(pcoa_shuffled['PC1'], pcoa_shuffled['PC2'], alpha=alpha, c=colors_shuffled)
    for disease in marker:
        pcoa_disease_df = pcoa_df[pcoa_df['Label'] == disease]
        ax_scatter.scatter(pcoa_disease_df['PC1'], pcoa_disease_df['PC2'], alpha=alpha, c=disease_colors[disease], marker=marker[disease])

    # Now, add the mean marker for each group on top
    if show_mean:
        grouping = pcoa_df.groupby('Label')
        for disease in np.flip(unique_diseases):
            if disease in grouping.groups:  # ensure the disease exists in your data
                if disease in marker:
                    marker_style = marker[disease]
                else:
                    marker_style = 'o'
                group = grouping.get_group(disease)  # get the entire group as a DataFrame
                mean_pc1 = group['PC1'].mean()
                mean_pc2 = group['PC2'].mean()
                ax_scatter.plot(mean_pc1, mean_pc2, marker=marker_style, markersize=8,
                                color=disease_colors[disease], markeredgecolor='k',
                                linestyle='None', label=disease)
    # If we don't plot the means, just add the legend
    else:
        for disease in unique_diseases:
            if disease in marker:
                marker_style = marker[disease]
            else:
                marker_style = 'o'
            ax_scatter.plot([], [], marker=marker_style, markersize=8,
                            color=disease_colors[disease], markeredgecolor='k',
                            linestyle='None', label=disease)
    pc1_exp = pcoa_results.proportion_explained['PC1']
    pc2_exp = pcoa_results.proportion_explained['PC2']
    ax_scatter.set_xlabel(f'PCoA1 ({np.round(pc1_exp * 100)}%)')
    ax_scatter.set_ylabel(f'PCoA2 ({np.round(pc2_exp * 100)}%)')
    ax_scatter.legend()

    # Create the top boxplots (for PC1) in horizontal orientation:
    # Use the original group order from unique_diseases for consistency.
    data_pc1 = [pcoa_df[pcoa_df['Label'] == disease]['PC1'].values for disease in unique_diseases]
    bplot_top = ax_box_top.boxplot(data_pc1, patch_artist=True, vert=False,
                                   flierprops=dict(marker='x', markersize=5))
    for patch, disease in zip(bplot_top['boxes'], unique_diseases):
        patch.set_facecolor(disease_colors[disease])
    for median in bplot_top['medians']:
        median.set_color('black')
    ax_box_top.set_yticklabels(unique_diseases)
    ax_box_top.set_xticks([])

    # Create the right boxplots (for PC2) in vertical orientation:
    data_pc2 = [pcoa_df[pcoa_df['Label'] == disease]['PC2'].values for disease in unique_diseases]
    bplot_right = ax_box_right.boxplot(data_pc2, patch_artist=True,
                                       flierprops=dict(marker='x', markersize=3))
    for patch, disease in zip(bplot_right['boxes'], unique_diseases):
        patch.set_facecolor(disease_colors[disease])
    for median in bplot_right['medians']:
        median.set_color('black')
    ax_box_right.set_yticks([])
    ax_box_right.set_xticklabels(unique_diseases, rotation=-90)

    plt.tight_layout()


def plot_clr_pca(
        X_, y_,
        label_names=('class 0', 'class 1'),
        pca=None,
        pseudocount=1e-6,
        figsize=(6, 5),
        point_size=30,
        title='CLR-PCA',
        ax=None,
        legend=True,
        **scatter_kw):
    X_ = np.asarray(X_, dtype=float)
    y_ = np.asarray(y_)
    assert set(np.unique(y_)) <= {0, 1}, f"y must contain only 0 and 1. Current values: {set(np.unique(y_))}"

    X_log = np.log(X_ + pseudocount)
    X_clr = X_log - X_log.mean(axis=1, keepdims=True)

    if pca is None:
        pca = PCA(n_components=2).fit(X_clr)
    pcs = pca.transform(X_clr)
    var_exp = pca.explained_variance_ratio_ * 100

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    face_colours = np.array(['#3182bd', '#e6550d'])

    for lbl in (0, 1):
        idx = y_ == lbl
        ax.scatter(
            pcs[idx, 0], pcs[idx, 1],
            s=point_size,
            c=face_colours[lbl],
            alpha=0.2,
            linewidths=0.4,
            label=label_names[lbl],
            **scatter_kw
        )

    ax.set_xlabel(f'PC1 ({var_exp[0]:.1f}%)')
    ax.set_ylabel(f'PC2 ({var_exp[1]:.1f}%)')
    ax.set_title(title)
    ax.grid(False)

    # Legend centred below plot
    if legend:
        ax.legend(
            loc='upper center',
            bbox_to_anchor=(0.5, -0.12),
            ncol=2,
            frameon=False
        )
    return ax, pca