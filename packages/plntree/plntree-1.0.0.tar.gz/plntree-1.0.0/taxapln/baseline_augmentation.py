# This script is a fork from the AugCoda packages functions and PhyloMix package
# Credits to https://github.com/cunningham-lab/AugCoDa and https://github.com/batmen-lab/phylomix

import numpy as np
import torch
import gzip
import re
import pandas as pd
from ete4 import Tree
from tqdm.auto import tqdm

from phylomix.src.mixup import augment
from phylomix.src.mixup.data import PhylogenyDataset, PhylogenyTree

def vanilla_mixup(X_train, n_aug=10):
    """
    Generate augmented data using vanilla mixup.
    Parameters
    ----------
    X_train: np.ndarray
    n_aug: int

    Returns
    -------

    """
    X = X_train.copy()
    n = X.shape[0]

    lam = np.random.rand(n_aug).reshape([-1, 1])
    idx1 = np.random.choice(n, size=n_aug)
    idx2 = np.random.choice(n, size=n_aug)

    # Take convex combination
    X_aug = lam * X[idx1, :] + (1 - lam) * X[idx2, :]
    return X_aug


def compositional_cutmix(X_train, n_aug=10, normalize=True):
    """
    Generate augmented data using compositional cutmix.
    Parameters
    ----------
    X_train: np.ndarray
    n_aug: int
    normalize: bool

    Returns
    -------

    """
    X = X_train.copy()

    X_temp = X_train.copy()
    n = X_temp.shape[0]

    idx1 = np.random.choice(n, size=n_aug)
    idx2 = np.random.choice(n, size=n_aug)

    p = np.random.rand(n_aug)
    mask = np.random.binomial(1, p, [X_temp.shape[1], n_aug]).T
    X_aug = mask * X_temp[idx1, :] + (1 - mask) * X_temp[idx2, :]

    if normalize:
        X_aug = X_aug / (X_aug.sum(axis=-1, keepdims=True) + 1e-32)

    return X_aug


def augcoda(function, X, tree, n_aug=10, y=None):
    """
    Generate augmented data using the specified augmentation function.
    Parameters
    ----------
    function: str or callable
    X: np.ndarray
    tree: plntree.utils.Tree
    n_aug: int
    y: None

    Returns
    -------

    """
    if y == None:
        y = np.zeros(X.shape[0])
    if function == 'vanilla-mixup':
        function = vanilla_mixup
    elif function == 'compositional-cutmix':
        function = compositional_cutmix

    X_augmented = torch.zeros((n_aug, X.shape[1], X.shape[2]))
    for level in range(X.shape[1]):
        X_augmented[:, level, :tree.K[level]] = torch.tensor(
            function(X[:, level, :tree.K[level]].detach().numpy(), n_aug)
        )
    return X_augmented


def phylomix(X, n_samples, tree='taxonomy', clr=False):
    """
    Generate augmented data using PhyloMix augmentation.
    Parameters
    ----------
    X: pd.DataFrame
    n_samples: int
    tree: str
    clr: bool

    Returns
    -------

    """
    phylodata = PhylogenyDataset(
        X.to_numpy(),
        np.array([1]*X.shape[0]),
        X.index.to_numpy(),
        np.array([col.split('|')[-1] for col in X.columns])
    )

    # Build the tree by iterating over each taxonomic level.
    if tree == 'taxonomy':
        phylotree = get_taxonomy(X)
    elif tree == 'phylogeny':
        phylotree, X = get_phylogeny(X.transpose())

    n = X.shape[0]
    prop_augmentation = (n_samples + n) / n

    augmented_data = augment(
        data=phylodata,
        phylogeny_tree=phylotree,
        num_samples=prop_augmentation,
        aug_type='phylomix',
        normalize=False,
        one_hot_encoding=False,
        clr=clr,
    )
    X_gen = augmented_data.X[-n_samples:]
    if clr:
        X_gen = pd.DataFrame(torch.softmax(torch.tensor(X_gen), -1), columns=X.columns)
    else:
        X_gen = pd.DataFrame(X_gen, columns=X.columns)
    return X_gen

def get_taxonomy(X):
    taxonomy = Tree()
    for tax_string in X.columns:
        taxa = tax_string.split('|')
        current_node = taxonomy
        for tax in taxa:
            matching_children = [child for child in current_node.get_children() if child.name == tax]
            if matching_children:
                current_node = matching_children[0]
            else:
                current_node = current_node.add_child(name=tax)
    taxonomy = PhylogenyTree(taxonomy)
    return taxonomy

def get_phylogeny(X):
    """
    Get the GTDB phylogeny and taxonomy for the given counts matrix.
    Parameters
    ----------
    X: pd.DataFrame

    Returns
    -------

    """
    release = "226"
    files = {
        "bac_tree": f"phylogeny/bac120_r{release}.tree",  # or .tree.gz
        "arc_tree": f"phylogeny/ar53_r{release}.tree",
        "bac_tax": f"phylogeny/bac120_taxonomy_r{release}.tsv.gz",
        "arc_tax": f"phylogeny/ar53_taxonomy_r{release}.tsv.gz",
    }

    def taxon_to_species(taxon: str) -> str | None:
        last = taxon.split('|')[-1]  # s__Genus_species
        if last.startswith('s__'):
            sp = last[3:].replace('_', ' ')
            return sp if sp.lower() != 'unclassified' else None
        return None

    wanted_species = (
        X.transpose().index.map(taxon_to_species).dropna().unique().tolist()
    )

    def load_tax(path: str) -> pd.DataFrame:
        with gzip.open(path, 'rt') as fh:
            return pd.read_csv(
                fh, sep='\t', names=['gid', 'lineage'], usecols=[0, 1], dtype=str
            )

    tax = pd.concat(
        [load_tax(files['bac_tax']), load_tax(files['arc_tax'])],
        ignore_index=True
    )

    gid2species = {}
    for gid, lineage in tqdm(tax.itertuples(index=False), total=len(tax)):
        if ';s__' in lineage:
            gid2species[gid] = lineage.split(';')[-1][3:].replace('_', ' ')

    _support_prefix = re.compile(r"'[0-9.]+:")

    def load_newick(path: str) -> Tree:
        opener = gzip.open if path.endswith(".gz") else open
        with opener(path, "rt") as fh:
            text = _support_prefix.sub("'", fh.read())
        return Tree(text, parser=1)  # internal node names

    t_bac = load_newick(files['bac_tree'])
    t_arc = load_newick(files['arc_tree'])

    leaf_names = {n.name for n in t_bac if n.is_leaf} | \
                 {n.name for n in t_arc if n.is_leaf}

    species2gid = {}
    for gid, sp in gid2species.items():
        if gid in leaf_names and sp not in species2gid:
            species2gid[sp] = gid

    genomes_of_interest = [species2gid[sp]
                           for sp in wanted_species if sp in species2gid]

    missing = [sp for sp in wanted_species if sp not in species2gid]
    if missing:
        print(f"[warning] {len(missing)} species absent from GTDB backbone "
              f"(e.g. {missing[:3]}) – skipped.")

    root = Tree()
    root.add_child(t_bac)
    root.add_child(t_arc)

    root.prune(genomes_of_interest, preserve_branch_length=True)

    for leaf in root:
        leaf.name = gid2species[leaf.name]  # Genus species

    phylo_tree = root

    # set of species names that survived the prune step
    phylo_species = {leaf.name for leaf in phylo_tree if leaf.is_leaf}
    mask = X.transpose().index.map(lambda t: taxon_to_species(t) in phylo_species)
    counts = X.transpose().loc[mask].copy().transpose()
    return phylo_tree, counts