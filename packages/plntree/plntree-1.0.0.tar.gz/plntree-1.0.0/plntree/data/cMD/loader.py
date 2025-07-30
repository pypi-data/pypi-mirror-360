import numpy as np
import pandas as pd
import warnings
import os
import importlib.resources

warnings.filterwarnings("ignore")

def metadata(directory='./', study=None):
    """
    Get the metadata for a specific study, or all of none specified.
    Parameters
    ----------
    directory: str
        Look for the metadata file in this directory; if not found, use the default package resource.
    study: None or str
        Name of the study. If None, return all metadata.

    Returns
    -------
    pd.DataFrame
    """
    path = os.path.join(directory, 'metadata.csv')
    if os.path.exists(path):
        metadata = pd.read_csv(path, dtype=str).set_index('sample_id')
    else:
        with importlib.resources.path(__package__.split('.')[0] + '.data.cMD', 'metadata.csv') as metadata_path:
            metadata = pd.read_csv(metadata_path, dtype=str).set_index('sample_id')
    if study is None:
        return metadata
    metadata = metadata[metadata['study_name'] == study]
    return metadata

def get_study(directory='./', study=None, taxonomic_levels=('c', 's'), prevalence=0., total_reads=100_000):
    """
    Get the taxa abundance  for a specific study.
    Parameters
    ----------
    directory: str
        Look for the study counts in this directory; if not found, use the default package resource.
    study: str
        Name of the study.

    Returns
    -------
    pd.DataFrame
    """
    path = directory, 'studies'
    try:
        iterator = os.listdir(path)
    except TypeError:
        path = __package__.split('.')[0] + '.data.cMD.studies'
        iterator = importlib.resources.files(path).iterdir()
        iterator = [str(f.name) for f in iterator if f.is_file()]
    for filename in iterator:
        if study in filename:
            study = filename
            break
    if study is None:
        raise ValueError(f'Study not found.')
    path = directory + f'/studies/{study}'
    if os.path.exists(path):
        abundance = pd.read_csv(directory + f'/studies/{study}', index_col=0).astype(float)
    else:
        with importlib.resources.path(__package__.split('.')[0] + '.data.cMD.studies', study) as study_path:
            abundance = pd.read_csv(study_path, index_col=0).astype(float)
    abundance = _get_bacteria(abundance)
    abundance = _aggregate_abundances(abundance, taxonomic_levels[1])

    levels = ['p', 'c', 'o', 'f', 'g', 's']
    if taxonomic_levels[1] not in levels:
        raise ValueError(f'Precision should be a string in {levels}.')
    for i in range(len(levels)):
        if levels[i] == taxonomic_levels[0]:
            break
    if i > 0:
        level_removed = levels[i - 1]
    else:
        level_removed = 'k'
    abundance = _prune_top_levels(abundance, level_removed)
    if prevalence > 0.:
        abundance = prevalence_filter(abundance.transpose(), prevalence).transpose()
    abundance = abundance.div(abundance.sum(axis=1), axis=0) # Normalized abundances
    if total_reads > 0:
        abundance = multinomial_resampling(abundance.transpose(), total_reads).transpose()
    return abundance


def _aggregate_abundances(df, level):
    """
    Aggregate the taxa at a specific taxonomic level
    """
    levels = ['p', 'c', 'o', 'f', 'g', 's']
    if level not in levels:
        raise ValueError(f'Precision should be a string in {levels}.')

    def extract_taxa(taxa, level):
        parts = taxa.split('|')
        i = 0
        part = parts[i]
        agg_taxa = part
        while f'{level}__' not in part:
            i += 1
            part = parts[i]
            agg_taxa = agg_taxa + '|' + part
        return agg_taxa

    def aggregate_taxa(df_T, aggregation_map):
        values = {}
        for agg_taxa in aggregation_map:
            values[agg_taxa] = df_T.loc[[i for i in df_T.index if agg_taxa in i]].sum(axis=0)
        return values

    aggregated_taxa = pd.Series(df.columns).apply(lambda x: extract_taxa(x, level)).unique()
    df_agg = pd.DataFrame(aggregate_taxa(df.transpose(), aggregated_taxa))

    return df_agg


def _prune_top_levels(raw_abundances, taxonomic_level):
    """
    Prune the taxonomy up to the selected level.
    Parameters
    ----------
    raw_abundances: pd.DataFrame
    taxonomic_level: str

    Returns
    -------
    pd.DataFrame
    """
    taxonomic_levels = ['k', 'p', 'c', 'o', 'f', 'g', 's']
    if taxonomic_level not in taxonomic_levels or taxonomic_level == 's':
        raise ValueError('Taxonomic level must be one of the following: k, p, c, o, f, g')
    for cur, level in enumerate(taxonomic_levels):
        if level == taxonomic_level:
            break
    level = taxonomic_levels[cur+1]
    taxa = []
    abundances = raw_abundances.copy().transpose()
    for i in range(len(abundances)):
        filtered_taxa = abundances.index[i].split(f'{level}__')[1]
        taxa.append(f'{level}__' + filtered_taxa)

    abundances.index = taxa
    return abundances.transpose()

def _get_bacteria(raw_abundance):
    """
    Get the bacteria from the raw abundance data.
    Parameters
    ----------
    raw_abundance: pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    bacteria_columns = [c for c in raw_abundance.columns if 'k__Bacteria' in c]
    return raw_abundance[bacteria_columns].copy()


def prevalence_filter(counts, prevalence=0.1):
    """
    Filter the count data based on the prevalence.
    Parameters
    ----------
    counts
    prevalence: float

    Returns
    -------
    pd.DataFrame
    """
    presence = 1*(counts > 0)
    presence = presence.mean(axis=1)
    presence = presence[presence >= prevalence]
    return counts.loc[presence.index]


def multinomial_resampling(raw_abundance, total_reads=10_000, seed=None):
    """
    Resample the raw abundance data.
    Parameters
    ----------
    raw_abundance: pd.DataFrame
    total_reads: int

    Returns
    -------
    pd.DataFrame
    """
    counts = raw_abundance.copy()
    if seed is not None:
        np.random.seed(seed)
    counts = counts / counts.sum(axis=0)
    counts[counts.isna()] = 0.
    counts = counts.apply(lambda x: np.random.multinomial(total_reads, x), axis=0)
    return counts