from plntree import PLNTree
from plntree.utils.utils import load_losses, load_model_weights, save_losses, save_model_weights
from plntree.data import cMD
from experiments_utils import *
import os
from sklearn.model_selection import train_test_split

import argparse

parser = argparse.ArgumentParser(description='Arguments for PLN-Tree training on curated metagenomics datasets.')
parser.add_argument('-d', '--dataset', type=str, default='HMP_2019_ibdmdb', help='Dataset for PLN-Tree data augmentation.')
parser.add_argument('-r', '--repeats', type=int, default=20, help='Number of hold-out repeats for model training.')
parser.add_argument('-s', '--size', type=float, default=0.1, help='Proportion of training samples.')
parser.add_argument('-c', '--covariates', type=str, default="none", help='Select covariates: none, all.')
parser.add_argument('-e', '--epoch', type=int, default=10_000, help='Number of epochs.')
parser.add_argument('-p', '--prevalence', type=float, default=0.15, help='Prevalence threshold.')
args = parser.parse_args()
config = vars(args)

study = config['dataset']
n_holdout = config['repeats']
cov_scenario = config['covariates']
if cov_scenario not in ['none', 'all']:
    raise ValueError('Covariates must be one of: none, all.')
n_epoch = config['epoch']
prevalence = config['prevalence']
train_proportion = np.round(config['size'], 2)
seed = 0

save_folder = 'cache/'
device = 'cuda' if torch.cuda.is_available() else 'cpu'

print('[INFO] Dataset:', study)
print('[INFO] Prevalence:', prevalence)
print('[INFO] Covariates:', cov_scenario)
print('[INFO] Number of hold-out:', n_holdout)
print('[INFO] Training size:', train_proportion)
print('[INFO] Seed:', seed)
print('[INFO] Save folder:', save_folder)
print('[INFO] Using device:', device)

seed_all(seed)
# Import the dataset with taxonomic information between the class and the species
levels = ('c', 's')
counts = cMD.get_study(
    study=study,
    taxonomic_levels=levels,
    prevalence=prevalence,
    total_reads=100_000,
    directory='./plntree/data/cMD',
)
metadata = cMD.metadata(
    study=study,
    directory='./plntree/data/cMD',
)
metadata = metadata.loc[counts.index]

# Preprocess the covariates
def preprocess_covariates(cov):
    # Select only a few covariates to be used
    cov_emb = cov.copy()[['country', 'age_category', 'gender', 'BMI']].dropna()
    if cov_emb.empty:
        print('[INFO] No covariates available for this study.')
        return cov.copy()

    # One-hot encoding of the countries
    for country in cov_emb['country'].unique():
        cov_emb[country] = [1 * (cov_emb.country.iloc[i] == country) for i in range(cov_emb.shape[0])]
    cov_emb = cov_emb.drop(columns=['country'])

    # Define the order of the ages
    ages = {'newborn': 0, 'child': 0.2, 'schoolage': 0.5, 'adult': 0.7, 'senior': 1}
    cov_emb['age_category'] = cov_emb['age_category'].apply(lambda x: ages[x])

    # Categorical encoding for sex
    sex = {'male': 0, 'female': 1}
    cov_emb['gender'] = cov_emb['gender'].apply(lambda x: sex[x])

    # Normalization of BMI
    cov_emb['BMI'] = cov_emb['BMI'].astype(float)
    cov_emb['BMI'] = (cov_emb['BMI'] - cov_emb['BMI'].min()) / (cov_emb['BMI'].max() - cov_emb['BMI'].min())

    cov_emb = cov_emb.astype(float)
    return cov_emb
covariates = preprocess_covariates(metadata)
if cov_scenario == 'country':
    covariates = covariates.drop(columns=['age_category', 'gender', 'BMI'])
    covariates = covariates[covariates.columns[1:]].astype(float)
metadata = metadata.loc[covariates.index]
print('[INFO] Covariates shape:', covariates.shape)
print('[INFO] Covariate keys:', list(covariates.columns))

# Define a base PLN-Tree model, BUT WHAT FOR?
hierarchy = counts.columns
base = PLNTree(
    counts=counts,
)

datasets = []
levels_str = ''
for level in levels:
    levels_str += level
prefix_all = f'plntreeHO-{study}-LV{levels_str}-prev{prevalence}-s{seed}-train{train_proportion}'
for i in range(n_holdout):
    ho_file_name = save_folder + prefix_all + '-ho' + str(i) + '.csv'
    if not os.path.isfile(ho_file_name):
        # Select a random stratified partition of the dataset for the selected dataset
        df_train, df_test = train_test_split(
            metadata,
            train_size=train_proportion,
            stratify=metadata['study_condition'],
            random_state=seed+i,
        )
        df_train['Train'] = 1
        df_test['Train'] = 0

        df_train = df_train['Train'].reset_index()
        df_test = df_test['Train'].reset_index()

        df_ho = pd.concat([df_train, df_test], axis=0)
        df_ho.columns = ['patient_id', 'train_label']

        df_ho.to_csv(ho_file_name, index=False)
        print('[INFO] Hold-out', i, 'saved to', ho_file_name)
    df_ho = pd.read_csv(ho_file_name)
    df_ho['patient_id'] = df_ho['patient_id'].astype(str)
    df_ho['train_label'] = df_ho['train_label'].astype(int)

    # We keep the cross-validation pipeline to be able to use the same functions as in the original code
    # But since it's just a hold-out, we will use only "one fold", that's actually a simple split
    folds = []
    for k in range(1):
        train_fold = df_ho[df_ho['train_label'] == 1]
        test_fold = df_ho[df_ho['train_label'] == 0]
        train_indices = list(train_fold['patient_id'].values.flatten())
        test_indices = list(test_fold['patient_id'].values.flatten())
        X_train = counts.loc[train_indices].copy()
        X_test = counts.loc[test_indices].copy()
        cov_train = covariates.loc[X_train.index].copy()
        cov_test = covariates.loc[X_test.index].copy()
        if cov_scenario == 'none':
            cov_train = None
            cov_test = None
        folds.append((X_train, cov_train, X_test, cov_test))
    datasets.append(folds)
print(f'[INFO] Datasets prepared for {n_holdout} Hold-Outs of size {len(train_indices)} train / {len(test_indices)} test')

def get_disease_samples(disease, X):
    meta = metadata.loc[X.index]
    # if disease in ['UC', 'CD']:
    #     disease_index = meta[(meta.study_condition == 'IBD') & (meta.disease_subtype == disease)].index
    # else:
    #     disease_index = meta[meta.study_condition == disease].index
    disease_index = meta[meta.study_condition == disease].index
    return X.loc[disease_index].copy()


diseases_dic = {
    'WirbelJ_2018': ['CRC', 'control'],
    'KosticAD_2015': ['T1D', 'control'],
    'RubelMA_2020': ['STH', 'control'],
    'ZhuF_2020': ['schizophrenia', 'control'],
    'ZellerG_2014': ['adenoma', 'control'],
    'YachidaS_2019': ['adenoma', 'control'],
    'JieZ_2017': ['ACVD', 'control'],
    'YuJ_2015': ['CRC', 'control'],
    'NielsenHB_2014': ['IBD', 'control'],
    'HMP_2019_ibdmdb': ['IBD', 'control'],
}
#diseases = metadata.study_condition.unique()
diseases = diseases_dic[study]
# if 'IBD' in diseases:
#     diseases = diseases[diseases != 'IBD']
#     diseases += ['UC', 'CD']

for disease in diseases:
    # Prefix for file saving
    prefix = prefix_all + '-' + disease
    print('[INFO] Condition:', disease, study)

    def embedder_params(embedder_type='GRU', embedding_size=16, n_embedding_layers=2, n_embedding_neurons=32,
                        n_after_layers=2):
        preprocessing = 'proportion'
        params = {
            'method': 'residual',
            'embedder_type': embedder_type,
            'embedding_size': embedding_size,
            'n_embedding_layers': n_embedding_layers,
            'n_embedding_neurons': n_embedding_neurons,
            'n_after_layers': n_after_layers,
            'counts_preprocessing': preprocessing
        }
        name = params['method'] + f'-Emb{embedder_type}-{n_embedding_layers}x{n_embedding_neurons}to{embedding_size}-{n_after_layers}-{preprocessing}'
        return name, params


    def meanfield_params(n_layers, preprocessing):
        params = {
            'method': 'mean field',
            'n_layers': n_layers,
            'counts_preprocessing': preprocessing
        }
        name = params['method'] + '-' + params['counts_preprocessing'] + '-' + str(n_layers)
        return name, params


    def monitor_alpha_diversity(X_train, X_monitor):
        tree = base.tree
        X_dic = {'Train': X_train, 'Monitor': X_monitor}
        reference_group = 'Train'
        distance = wasserstein_distance
        X_ref = X_dic[reference_group]
        size = X_ref.shape[0]
        compared_size = list(X_dic.values())[1].shape[0]
        n_splits = compared_size // size
        distances = []
        for i in range(n_splits):
            X_sub_dic = {}
            for key, X in X_dic.items():
                if key == reference_group:
                    X_sub_dic[key] = X.clone().detach().cpu()
                else:
                    X_sub_dic[key] = X[i * size:(i + 1) * size].clone().detach().cpu()
            alpha_df = compute_alpha_diversity(X_sub_dic, tree)
            dist = compute_distance(alpha_df, reference_group, distance=distance)
            distances.append(dist)
        distances = pd.concat(distances)
        return distances.mean(axis=0).mean()


    def learn_plntree(X_train, cov_train, cov_params, n_latent_layers, variational_approx,
                        n_epoch=n_epoch, load_file=None, seed=None):
        seed_all(seed)
        latent_dynamic = {
            'n_layers': n_latent_layers,
            'counts_preprocessing': 'proportion',
        }
        estimator = PLNTree(
            counts=X_train,
            covariates=cov_train,
            latent_dynamic=latent_dynamic,
            variational_approx=variational_approx,
            covariates_params=cov_params,
            device=device,
            seed=seed,
        )
        print(X_train.shape)
        try:
            load_model_weights(estimator, save_folder + load_file)
            losses = load_losses(save_folder + load_file + '_loss')
        except:
            print('[INFO] Training PLN-Tree: ' + load_file)
            #losses = estimator.fit(verbose=10, tolerance_smoothing=2500, max_epoch=n_epoch)
            losses = estimator.fit(verbose=100, tolerance_smoothing=250000, max_epoch=n_epoch,
                                   #monitor={'function': monitor_alpha_diversity, 'step': 200, 'repeat': 25,'file':  save_folder + load_file}
                                              )
            save_model_weights(estimator, save_folder + load_file)
            save_losses(losses, save_folder + load_file + '_loss')
            #save_losses(monitored, save_folder + load_file + '_monitored')
        print('Loaded PLN-Tree ' + load_file)
        return estimator, losses


    def bootstrap_plntree(datasets, cov_params, n_latent_layers, variational_approx, emb_name, n_epoch=n_epoch, seed=None):
        wrapper = []
        for cv, folds in enumerate(datasets):
            for k, (X_train, cov_train, X_test, cov_test) in enumerate(folds):
                if cov_scenario == 'none':
                    load_file = prefix + '_' + str(n_latent_layers) + '--' + emb_name + f'_cv{cv}-{k}'
                else:
                    load_file = prefix + '_' + str(n_latent_layers) + '--' + cov_scenario + '-' + cov_params['type'] + str(cov_params['n_heads']) + '.' + str(cov_params['n_layers']) + '--' + emb_name + f'_cv{cv}-{k}'
                X_disease_train = get_disease_samples(disease, X_train)
                if cov_train is not None:
                    cov_disease_train = cov_train.loc[X_disease_train.index]
                else:
                    cov_disease_train = None
                estimator, losses = learn_plntree(X_disease_train, cov_disease_train,
                                                  cov_params,
                                                  n_latent_layers, variational_approx,
                                                  n_epoch=n_epoch, load_file=load_file, seed=seed)
                wrapper.append((estimator, losses, X_train, X_test))
        return wrapper


    def parse_tag(plntree_tag):
        s = plntree_tag.split(':')
        n_latent_layers = int(s[0])
        p = s[1].split('-')
        if p[0] == 'mean field':
            var_params = meanfield_params(int(p[2]), p[1])
        else:
            p = p[2:]
            var_params = embedder_params(
                embedding_size=int(p[0].split('to')[-1]),
                n_embedding_layers=int(p[0].split('x')[0]),
                n_embedding_neurons=int(p[0].split('x')[1].split('to')[0]),
                n_after_layers=int(p[-1])
            )
        return n_latent_layers, var_params

    cov_params = {'type': 'film', 'n_layers': 2, 'n_heads': 0}
    #cov_params = {'type': 'attention', 'n_heads': 4, 'n_layers': 1}
    # n_latent_layers, (emb_name, variational_approx) = (0, meanfield_params(2, 'proportion'))
    n_latent_layers, (emb_name, variational_approx) = (1, embedder_params(
        embedder_type='GRU',
        embedding_size=32,
        n_embedding_layers=2,
        n_embedding_neurons=32,
        n_after_layers=2
        )
    )
    bootstrap_plntree(datasets, cov_params, n_latent_layers, variational_approx, emb_name, n_epoch=n_epoch, seed=seed)