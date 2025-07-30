![PyPI](https://img.shields.io/pypi/v/plntree)
![GitHub](https://img.shields.io/github/license/AlexandreChaussard/PLNTree-package)
![Python Versions](https://img.shields.io/badge/python-3.8+-blue)
![GPU Support](https://img.shields.io/badge/GPU-Supported-brightgreen)
# PLN-Tree: Hierarchical Poisson Log-Normal models
> The Poisson Log-Normal (PLN) models are used for the
> analysis of multivariate count data. PLN-Tree extends this framework to 
> hierarchically organized count data by incorporating tree-like structures
> into the analysis. This package provides efficient algorithms to perform PLN-Tree inference
> by leveraging PyTorch with GPU acceleration.
> 
> PLN-Tree has shown interesting applications to metagenomics, exploiting the taxonomy 
> as a guide for microbiome modeling. 

> Typical applications involve:
> - **Hierarchical Modeling**: investigate the relationships between taxa at different levels of the taxonomy, between levels relationships and covariates impact.
> - **Data Augmentation**: generate synthetic samples to inflate training sets and enhance performances. See TaxaPLN augmentation.
> - **Counts Preprocessing**: transform counts using the LP-CLR transform to tackle the challenges of compositionality and integer constraints of count data.

## 📖 Documentation and tutorials

Want to learn how to use the package? 
Start with the quickstart guide below, 
then explore the [documentation](https://github.com/AlexandreChaussard/PLNTree-package/wiki).

If you are interest specifically in the TaxaPLN augmentation strategy for microbiome data, check out our [TaxaPLN starting guide](https://github.com/AlexandreChaussard/PLNTree-package/blob/master/taxapln/README.md).

## 🛠 Installation

**PLN-Tree** is available on [PyPI](https://pypi.org/project/plntree/) for faster installation.

```sh
pip install plntree
```

## ⚡️ Quickstart

This package comes with human microbiome data from the [curatedMetagenomicData](https://waldronlab.io/curatedMetagenomicData/index.html) library.
```python
from plntree.data import cMD

taxa_abundance = cMD.get_study(
    study='ZhuF_2020',           # Study name
    taxonomic_levels=('c', 's'), # Taxonomic levels to retrieve
    prevalence=0.,               # Minimum prevalence of taxa to include
    total_reads=100_000          # Total abundance of each sample (proportions to counts)
)

covariates = cMD.metadata(
    study='ZhuF_2020',           # Study name
)
```

The `taxa_abundance` is a `pandas.DataFrame` containing the microbial composition 
of each patient, while the `covariates` is a `pandas.DataFrame` with the metadata 
associated to each patient.

### Training a PLN-Tree model

The `PLNTree` class allows to specify the parameters of the model, and perform the inference on the training data.
```python
from plntree import PLNTree
model = PLNTree(
            taxa_abundance,   # DataFrame with counts (rows: samples, columns: taxa)
            covariates=None,  # DataFrame with covariates (optional, default None)
            device='cpu',     # Device to use for training (default CPU, or 'cuda' for GPU)
            seed=0,           # Random seed for reproducibility (default None)
)
```
By default the latent dynamic is set to a Markov Linear model, which is suitable for most metagenomics cases.
Besides, the variational approximation is set to a residual amortized backward method, which is more efficient than
the mean-field approximation for PLN-Tree, but requires more parameters. If you use the covariates,
the default implementation relies on FiLM.
See the [documentation](https://github.com/AlexandreChaussard/PLNTree-package/wiki) to understand how to customize these parameters.

The package comes with visualization functions to help interpret the data, notably
calling the `tree.plot` method, which will display the tree structure.
```python
from plntree import PLNTree
model.tree.plot()
```

Training a PLN-Tree model is done by calling the `fit` method on the model. 
More parameters are available for early stopping or convergence monitoring.
```python
model.fit(max_epoch=5_000, batch_size=512, learning_rate=1e-3)
```

### Applications

#### Data Augmentation
PLN-Tree can be used to generate synthetic samples to augment training sets and 
improve downstream tasks performances.

For microbiome data, an effective way to perform data augmentation relies on the [TaxaPLN](https://github.com/AlexandreChaussard/PLNTree-package/blob/master/taxapln/README.md) strategy,
which is thoroughly described in [this paper](https://arxiv.org/abs/2507.03588). In a nutshell, TaxaPLN uses the PLN-Tree model to generate synthetic samples
through a post-hoc VAMP sampler that is instanciated from the trained model.
```python
X_aug, Z_aug = model.vamp_sample(n_samples=1000, seed=0)
```
Covariate-aware sampling is also available if the model was trained with covariates using the `covariates` parameter.

#### Count Preprocessing with LP-CLR
PLN-Tree can also be used to preprocess count data using the LP-CLR transform, 
which is a log-ratio transformation that addresses the challenges of compositionality 
and integer constraints of count data by leveraging the latent space.

Upon training a PLN-Tree model, applying the preprocessing can be done through the `latent_proportion` method
which defines counts in the latent space, before applying the CLR transform.
```python
Z = model.encode(taxa_abundance)                                # First, encode the counts to the latent space
X_preprocessed = model.latent_proportions(Z, clr=True, seed=0)  # Then, apply the LP-CLR transform
```
This preprocessing is also compatible with covariates.

## 👐 Contributing

Want to contribute? Check the guidelines in [CONTRIBUTING.md](https://github.com/AlexandreChaussard/PLNTree-package/blob/master/CONTRIBUTING.md).

## 📜 Citations

Please cite our work using the following references:

- Chaussard, A., Bonnet, A., Gassiat, E., Le Corff, S.. Tree-based variational inference for Poisson log-normal models. Statistics and Computing 35, 135 (2025). [SpringerLink](https://doi.org/10.1007/s11222-025-10668-w).

