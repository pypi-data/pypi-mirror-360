# TaxaPLN: a taxonomy-aware augmentation strategy for microbiome-trait classification including metadata

> Microbiome datasets are often high dimensional, limited in size and highly variable, making it hard for machine learning models to find reliable patterns.
> In this context, data augmentation emerges as a promising solution to improve model performance by generating synthetic samples.
>
> Here, we develop and evaluate TaxaPLN, an augmentation strategy for microbiome data which leverages taxonomic information through PLN-Tree coupled with a VAMP sampler to generate new biologically faithful microbiome compositions. 
> It can also generate microbiomes conditioned on exogenous information, allowing for covariate-aware augmentation.

# ⚡️ General usage

First, install the `plntree` package, which contains the implementation of TaxaPLN:
```bash
pip install plntree
```

Then, import your microbiome data as a `pandas.DataFrame` with the counts of each taxon (rows: samples, columns: taxa), as well as your covariates if you want to include them.
We provide a fast access to microbiome studies from the `curatedMetagenomicData` package, which can be used to retrieve the data and covariates as follows:
```python
import curatedMetagenomicData as cMD

taxa_abundance = cMD.taxa_abundance(
    study='ZhuF_2020',           # Study name
    taxonomic_levels=('c', 's'), # Taxonomic levels to retrieve
    prevalence=0.15,             # Minimum prevalence of taxa to include
    total_reads=100_000          # Total abundance of each sample (proportions to counts)
)
covariates = cMD.metadata(
    study='ZhuF_2020',           # Study name
)
```

Upon data retrieval, you can use the `PLNTree` class to train a model on your data, as follows:
```python
from plntree import PLNTree

model = PLNTree(
    taxa_abundance,         # DataFrame with counts (rows: samples, columns: taxa)
    covariates=covariates,  # DataFrame with covariates (optional, default None)
    device='cpu',           # Device to use for training (default CPU, or 'cuda' for GPU)
    seed=0,                 # Random seed for reproducibility (default None)
)
```

Then, you can fit the model on your data:
```python
loss = model.fit(max_epoch=4_000, batch_size=512, learning_rate=1e-3, verbose=50)
```

Finally, you can use the model to generate synthetic samples using the `sample` method:
```python
X_aug, Z_aug = model.vamp_sample(n_samples=1000, seed=0)
```
which you can concatenate with your original data to augment your training set as follows:
```python
import pandas as pd

X_L = X_aug[:, -1, :]                                   # Last layer of the hierarchy contains the same entries as the original data
X_L = pd.DataFrame(X_L, columns=model.counts.columns)   # Convert to DataFrame, keeping columns in order of model counts
X_L = X_L[taxa_abundance.columns]                       # Reorder taxa according to the original count data
X_augmented = pd.concat([taxa_abundance, X_L], axis=0)  # Concatenate original and augmented data
```

# ⚡️ Reproducing our results

We implemented TaxaPLN as part of the PLN-Tree package. 
In this folder, you will find the code and experiments that we ran in the context of [our paper available here](https://arxiv.org/abs/2507.03588).

To reproduce our results from this paper, you first need to install the `plntree` package:
```bash
pip install plntree
```
You also need to install the following dependencies:
```bash
pip install pyPLNmodels==0.0.69
pip install scikit-bio==0.6.3
pip install ete4==4.1.1
pip install POT==0.9.5
```

Then, you need to train the PLN-Tree models for each dataset from the `curatedMetagenomicData` package we used, using the following command:
```bash
python3 curated_train_dataset_CV.py -d <dataset_name> -r 25 -c <covariates "none" or "all"> -e <max_epoch>
```
Since we ran comprehensive experiments in 25 x 5-Fold CV (125 models per dataset), this procedure takes several days to end.
Use covariates `all` to reproduce the covariate-aware results, or `none` to reproduce the vanilla augmentation results.
Dataset names are among: 
`WirbelJ_2018, KosticAD_2015, RubelMA_2020, ZhuF_2020, ZellerG_2014, YachidaS_2019, YuJ_2015, NielsenHB_2014, HMP_2019_ibdmdb`.
Refer to the [original paper](https://arxiv.org/abs/2507.03588) for more details on the datasets and see which are compatible with covariates.

If you want to use the model weights we trained, you can download them from [Zenodo](https://zenodo.org/records/15736785) (~40 Go) using the following command:
```bash
wget https://zenodo.org/records/15736785/files/plntree-cache.zip
```
Then, unzip the file in the `taxapln` folder and merge it with the existing `cache` folder:
```bash
unzip plntree-cache.zip
```

Upon completion, the model weights should be available in `cache`, allowing you to run the [plntree_data_augmentation-CV.ipynb](https://github.com/AlexandreChaussard/PLNTree-package/blob/master/taxapln/plntree_data_augmentation-CV.ipynb) notebook and reproduce the results of our paper.

## 📜 Citation

Please cite our work using the following reference:

- Alexandre Chaussard, Anna Bonnet, Sylvain Le Corff, & Harry Sokol. (2025). TaxaPLN: a taxonomy-aware augmentation strategy for microbiome-trait classification including metadata. arXiv preprint arXiv:2507.03588.