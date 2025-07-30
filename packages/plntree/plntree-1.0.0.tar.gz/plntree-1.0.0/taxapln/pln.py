from pyPLNmodels import Pln
import torch
import numpy as np
from plntree.utils.utils import batch_matrix_product

def learn_pln(hierarchical_counts, K, covariates=None, seed=None):
    """
    Learn a Poisson Log-Normal model for each level of the hierarchical data.
    Parameters
    ----------
    hierarchical_counts: torch.Tensor
    K: list[int]
    seed: int or None

    Returns
    -------
    list[Pln]
    """
    list_pln = []
    if seed is not None:
        torch.random.manual_seed(seed)
        np.random.seed(seed)
    for level in range(len(K)):
        endog = hierarchical_counts[:, level, :K[level]]
        pln = Pln(endog.to(dtype=torch.float64), exog=covariates, add_const=True)
        pln.fit(tol=1e-5, nb_max_iteration=30_000)
        list_pln += [pln]
    return list_pln

def mu(pln):
    """
    Compute the latent mean of the Poisson Log-Normal model.
    Parameters
    ----------
    pln: Pln

    Returns
    -------
    np.ndarray
    """
    try:
        return pln.coef.reshape(-1, ) + pln.offsets.mean(axis=0)
    except:
        print('No mean found.')
        return 0.

def sigma(pln):
    """
    Compute the covariance matrix of the Poisson Log-Normal model.
    Parameters
    ----------
    pln: Pln

    Returns
    -------
    torch.Tensor
    """
    return pln.covariance
def omega(pln):
    """
    Compute the precision matrix of the Poisson Log-Normal model.
    Parameters
    ----------
    pln: Pln

    Returns
    -------
    torch.Tensor
    """
    return torch.inverse(sigma(pln))

def sample(pln, n_samples, offsets=None, covariates=None, seed=None):
    """
    Sample from a Poisson Log-Normal model.
    Parameters
    ----------
    pln: Pln
    n_samples: int
    offsets: np.ndarray or None
    seed: int or None

    Returns
    -------
    np.ndarray, np.ndarray
    """
    if seed is not None:
        torch.random.manual_seed(seed)
    if covariates is None:
        means = mu(pln)
    else:
        means = torch.tensor(covariates.to_numpy()) @ pln.coef
    cov = sigma(pln)
    X = np.zeros((n_samples, cov.shape[1]), dtype=np.float64)
    Z = np.zeros((n_samples, cov.shape[1]), dtype=np.float64)
    if offsets is None:
        O = np.zeros(n_samples) + pln.offsets.mean(axis=0).mean().numpy()
    else:
        O = offsets
    if covariates is None:
        means -= pln.offsets.mean(axis=0)
    for i in range(n_samples):
        if covariates is None:
            Z_i = np.random.multivariate_normal(
                mean=means + O[i],
                cov=cov
            )
        else:
            Z_i = np.random.multivariate_normal(
                mean=means[i] + O[i],
                cov=cov
            )
        # Sample X ~ Poisson(Z)
        threshold = 20.
        if np.any(Z_i > threshold):
            Z_i= threshold - Z_i.max()
        X_i = np.random.poisson(np.exp(Z_i.astype(np.float64)))

        X[i] = X_i
        Z[i] = Z_i
    return X, Z

def generate_pln_data(pln_layers, n_samples, tree, seed=None):
    """
    Generate data from a Poisson Log-Normal model, both per layer and filled from the last layer.
    Parameters
    ----------
    pln_layers: list[Pln]
    n_samples: int
    tree: plntree.utils.Tree
    seed: int or None

    Returns
    -------
    torch.Tensor, torch.Tensor, torch.Tensor
    """
    if seed is not None:
        torch.random.manual_seed(seed)
    X_pln = torch.zeros(n_samples, tree.L, tree.K_max)
    Z_pln = torch.zeros(n_samples, tree.L, tree.K_max)
    for level in range(tree.L):
        pln = pln_layers[level]
        X_pln_l, Z_pln_l = sample(pln, n_samples)
        X_pln[:, level, :tree.K[level]] = torch.tensor(X_pln_l, dtype=X_pln.dtype)
        Z_pln[:, level, :tree.K[level]] = torch.tensor(Z_pln_l, dtype=Z_pln.dtype)
    X_pln_fill = torch.zeros(n_samples, tree.L, tree.K_max)
    X_pln_fill[:, -1, :] = X_pln[:, -1, :]
    for level in range(tree.L-1):
        l = tree.L - level - 1
        X_pln_fill[:, l-1, :tree.K[l-1]] = batch_matrix_product(
                    tree.affiliation_matrix[l].to(dtype=X_pln_fill.dtype),
                    X_pln_fill[:, l, :tree.K[l]].to(dtype=X_pln_fill.dtype)
                )
    return X_pln, Z_pln, X_pln_fill

def vamp_sample(pln, n_samples):
    M = pln.latent_mean
    indices = torch.randint(0, M.shape[0], (n_samples,))
    O = pln.offsets[indices]
    M = M[indices] + O
    S = torch.diag_embed(torch.exp(pln.latent_sqrt_var[indices])**2)
    Z = torch.distributions.MultivariateNormal(
            loc=M,
            covariance_matrix=S
    ).sample()
    threshold = 20.
    denied_samples_mask = torch.any(Z > threshold, dim=-1)
    Z[denied_samples_mask] = threshold - Z[denied_samples_mask].max(dim=-1, keepdim=True).values
    X = torch.distributions.Poisson(torch.exp(Z)).sample()
    if pln.exog is not None:
        return X, Z, pln.exog[indices]
    return X, Z

def vamp_sample_per_layer(pln_layers, tree, n_samples, seed=None):
    if seed is not None:
        torch.random.manual_seed(seed)
    Z = torch.zeros((n_samples, tree.L, tree.K_max))
    X = torch.zeros_like(Z)
    for level in range(tree.L):
        X_l, Z_l = vamp_sample(pln_layers[level], n_samples)
        Z[:, level, :tree.K[level]] = Z_l
        X[:, level, :tree.K[level]] = X_l
    return X, Z