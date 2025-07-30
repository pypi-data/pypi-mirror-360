import numpy as np
import torch


def shannon_index(counts):
    """
    Compute the Shannon index alpha diversity of the counts.
    Parameters
    ----------
    counts: torch.Tensor or np.ndarray

    Returns
    -------
    torch.Tensor or np.ndarray
    """
    proportions = counts / counts.sum(axis=-1, keepdims=True)
    log = np.log
    if type(counts) == torch.Tensor:
        log = torch.log
        proportions[proportions.isnan()] = 0.
    else:
        proportions[np.isnan(proportions)] = 0.
    return -(proportions * log(proportions + 1e-36)).sum(axis=-1)


def simpson_index(counts):
    """
    Compute the Simpson index alpha diversity of the counts.
    Parameters
    ----------
    counts: torch.Tensor or np.ndarray

    Returns
    -------
    torch.Tensor or np.ndarray
    """
    proportions = counts / counts.sum(axis=-1, keepdims=True)
    return (proportions ** 2).sum(axis=-1)


def bray_curtis_distance(counts_1, counts_2):
    """
    Compute the Bray-Curtis dissimilarity between the counts (dissimilarity matrix).
    Parameters
    ----------
    counts_1: torch.Tensor or np.ndarray
    counts_2: torch.Tensor or np.ndarray

    Returns
    -------
    torch.Tensor or np.ndarray
    """
    assert counts_1.shape == counts_2.shape
    observed_OTUs_1 = counts_1 * (counts_1 > 0) * (counts_2 > 0)
    observed_OTUs_2 = counts_2 * (counts_1 > 0) * (counts_2 > 0)
    # Compute the minimum of the observed OTUs (not using numpy or torch to make it cross compatible)
    C = (0.5 * (observed_OTUs_1 + observed_OTUs_2 - (observed_OTUs_1 - observed_OTUs_2).abs())).sum(axis=-1)
    S_1 = observed_OTUs_1.sum(axis=-1)
    S_2 = observed_OTUs_2.sum(axis=-1)
    denominator = S_1 + S_2
    denominator[denominator == 0] = torch.inf  # Avoid division by zero and output 1
    return 1. - 2. * C / denominator

def bray_curtis_dissimilarity_matrix(counts):
    """
    Compute the Bray-Curtis dissimilarity matrix between the counts (pairwise).
    Parameters
    ----------
    counts: torch.Tensor or np.ndarray

    Returns
    -------
    np.ndarray
    """
    matrix = np.zeros((len(counts), len(counts)))
    for i in range(len(counts)):
        for j in range(len(counts)):
            if j >= i:
                break
            matrix[i][j] = bray_curtis_distance(counts[i], counts[j])
    matrix += matrix.transpose()
    return matrix