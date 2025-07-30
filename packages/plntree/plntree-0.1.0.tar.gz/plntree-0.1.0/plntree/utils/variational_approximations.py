import torch.nn as nn

from plntree.utils.modules import (DenseNeuralNetwork, CombinedNeuralNetworks, AttentionBasedCombiningLayer, BoundLayer,
                                   CountsPreprocessing, PartialCountsPreprocessing, AttentionFiLM)

# The variational approximations are bounded in certain intervals to numerically stabilize the learning
# The bounds can take upmost a value of around 25 as we take the exponent in the ELBO
mean_bound = BoundLayer(-100, 25, 0.05)
# The variance is bounded between 1e-8 and around 10, which we hope fits most problems
# The issue lies in the ELBO for which we have a sum of m + S/2, so we ensure that this can be computed by having upmost 30
# Experiments have shown that we generally overestimate the variance, so we can afford to have a smaller bound
log_variance_bound = BoundLayer(-18, 2.5, 0.1)

def mean_field(tree, covariates_params, n_layers, preprocessing=None):
    """
    Mean field approximation for the variational distribution of the latents: at level l, the parameters only depend on
    the counts at level l and the covariates.
    Parameters
    ----------
    tree: plntree.utils.utils.Tree
    covariates_params: dict or None
    n_layers: int
    preprocessing: str or None

    Returns
    -------
    (nn.ModuleList, nn.ModuleList)
    """
    # In the mean field case, each parameter only takes as input the counts at the current level and the covariates
    m_fun = nn.ModuleList()
    log_S_fun = nn.ModuleList()
    for level in range(tree.L):
        # Counts dimension at level
        K_l = tree.K[level]
        # Latents dimension at this level
        K_l_eff = tree.K_eff[level]
        if covariates_params['size'] <= 0:
            m_l = nn.Sequential(
                CountsPreprocessing(preprocessing),
                DenseNeuralNetwork(K_l, K_l, K_l_eff, n_layers),
                mean_bound
            )
            log_S_l = nn.Sequential(
                CountsPreprocessing(preprocessing),
                DenseNeuralNetwork(K_l, K_l, K_l_eff, n_layers),
                log_variance_bound
            )
            m_l = CombinedNeuralNetworks(m_l, None, None, None)
            log_S_l = CombinedNeuralNetworks(log_S_l, None, None, None)
        else:
            if covariates_params['type'] == 'film':
                preprocessing_module = CountsPreprocessing(preprocessing)
                m_l_X = nn.Sequential(
                    DenseNeuralNetwork(K_l, K_l, K_l_eff, n_layers),
                    mean_bound
                )
                m_l = AttentionFiLM(
                    m_l_X, preprocessing_module, covariates_params['size'],
                    K_l, covariates_params['n_layers'], None
                )

                log_S_l_X = nn.Sequential(
                    DenseNeuralNetwork(K_l, K_l, K_l_eff, n_layers),
                    log_variance_bound
                )
                log_S_l = AttentionFiLM(
                    log_S_l_X, preprocessing_module, covariates_params['size'],
                    K_l, covariates_params['n_layers'], None
                )
            else:
                m_l_X = nn.Sequential(
                    CountsPreprocessing(preprocessing),
                    DenseNeuralNetwork(K_l, K_l, K_l, n_layers)
                )
                m_l = AttentionBasedCombiningLayer(
                            counts_network=m_l_X,
                            input_dim=K_l,
                            output_dim=K_l_eff,
                            covariates_dim=covariates_params['size'],
                            n_heads=covariates_params['n_heads'],
                            n_output_layers=covariates_params['n_layers'],
                            output_module=mean_bound
                        )

                log_S_l_X = nn.Sequential(
                    CountsPreprocessing(preprocessing),
                    DenseNeuralNetwork(K_l, K_l, K_l, n_layers)
                )
                log_S_l = AttentionBasedCombiningLayer(
                                counts_network=log_S_l_X,
                                input_dim=K_l,
                                output_dim=K_l_eff,
                                covariates_dim=covariates_params['size'],
                                n_heads=covariates_params['n_heads'],
                                n_output_layers=covariates_params['n_layers'],
                                output_module=log_variance_bound
                            )
        m_fun.append(m_l)
        log_S_fun.append(log_S_l)
    return m_fun, log_S_fun


def weak_backward_markov(tree, covariates_params, n_layers, preprocessing=None):
    """
    Weak amortized approximation for the variational distribution of the latents: at level l, the parameters depend on
    the counts at level l, the latents at level l + 1, and the covariates.
    Parameters
    ----------
    tree: plntree.utils.utils.Tree
    covariates_params: dict or None
    n_layers: int
    preprocessing: str or None

    Returns
    -------
    (nn.ModuleList, nn.ModuleList)
    """
    # The first layer is only getting X^{L}
    # The other layers are getting X^{l} and Z^{l + 1}
    # In the end, the size of the input "l" is K_{l + 1} + K_{l}
    m_fun = nn.ModuleList()
    log_S_fun = nn.ModuleList()
    for level in range(tree.L):
        # The input size of X^{1:l} would be sum(self.K[:i+1])
        # But we only give X^{l} in the weak amortized framework
        input_size = tree.K[level].clone()
        # If we are not at the last layer, the model also gets Z^{l+1} as input
        if level != tree.L - 1:
            input_size += tree.K_eff[level + 1]

        if covariates_params['size'] <= 0:
            m_l = nn.Sequential(
                PartialCountsPreprocessing(input_size, preprocessing),
                DenseNeuralNetwork(input_size, input_size, tree.K_eff[level], n_layers),
                mean_bound
            )
            log_S_l = nn.Sequential(
                PartialCountsPreprocessing(input_size, preprocessing),
                DenseNeuralNetwork(input_size, input_size, tree.K_eff[level], n_layers),
                log_variance_bound
            )
            m_l = CombinedNeuralNetworks(m_l, None, None, None)
            log_S_l = CombinedNeuralNetworks(log_S_l, None, None, None)
        else:
            if covariates_params['type'] == 'film':
                preprocessing_module = PartialCountsPreprocessing(input_size, preprocessing)
                m_l_XZ = nn.Sequential(
                    DenseNeuralNetwork(input_size, input_size, tree.K_eff[level], n_layers),
                    mean_bound
                )
                m_l = AttentionFiLM(
                    m_l_XZ, preprocessing_module, covariates_params['size'],
                    input_size, covariates_params['n_layers'], None
                )

                log_S_l_XZ = nn.Sequential(
                    DenseNeuralNetwork(input_size, input_size, tree.K_eff[level], n_layers),
                    log_variance_bound
                )
                log_S_l = AttentionFiLM(
                    log_S_l_XZ, preprocessing_module, covariates_params['size'],
                    input_size, covariates_params['n_layers'], None
                )
            else:
                m_l_XZ = nn.Sequential(
                    PartialCountsPreprocessing(input_size, preprocessing),
                    DenseNeuralNetwork(input_size, input_size, input_size, n_layers)
                )
                m_l = AttentionBasedCombiningLayer(
                            m_l_XZ, input_size, tree.K_eff[level], covariates_params['size'],
                            covariates_params['n_heads'], covariates_params['n_layers'],
                            mean_bound
                        )

                log_S_l_E = nn.Sequential(
                    PartialCountsPreprocessing(input_size, preprocessing),
                    DenseNeuralNetwork(input_size, input_size, input_size, n_layers)
                )
                log_S_l = AttentionBasedCombiningLayer(
                            log_S_l_E, input_size, tree.K_eff[level], covariates_params['size'],
                            covariates_params['n_heads'], covariates_params['n_layers'],
                            log_variance_bound
                        )

        m_fun.append(m_l)
        log_S_fun.append(log_S_l)
    return m_fun, log_S_fun


class Embedder(nn.Module):

    def __init__(self, input_size, embedding_size, hidden_size, n_layers, recurrent_network="GRU", dropout=0.2,
                 preprocessing=None):
        """
        Recurrent network module that maps the inputs towards a lower dimensional space independent of the amount of levels.
        Parameters
        ----------
        input_size: int
        embedding_size: int
        hidden_size: int
        n_layers: int
        recurrent_network: str
        dropout: float
        preprocessing: str or None
        """
        super(Embedder, self).__init__()
        self.embedding_size = embedding_size
        self.embedding_hidden_size = hidden_size
        if recurrent_network == "GRU":
            self.rnn = nn.GRU(
                input_size=input_size,
                hidden_size=self.embedding_hidden_size,
                num_layers=n_layers,
                batch_first=True,
                dropout=dropout
            )
        elif recurrent_network == "LSTM":
            self.rnn = nn.LSTM(
                input_size=input_size,
                hidden_size=self.embedding_hidden_size,
                num_layers=n_layers,
                batch_first=True,
                dropout=dropout
            )
        else:
            raise ValueError("Type of RNN not recognized. Choose between 'GRU' and 'LSTM'.")
        self.batch_norm = nn.BatchNorm1d(self.embedding_hidden_size)
        self.linear = nn.Linear(self.embedding_hidden_size, self.embedding_size)
        self.preprocessing = CountsPreprocessing(preprocessing)

    def forward(self, X):
        x = self.preprocessing(X)
        x = self.rnn(x)[0][:, -1, :]
        x = nn.functional.relu(x)
        x = self.batch_norm(x)
        x = self.linear(x)
        return x


def residual_backward_markov(tree, covariates_params, embedder_type, embedding_size, n_embedding_layers=2,
                             n_embedding_neurons=32, embedder_dropout=0.1, n_after_layers=1,
                             preprocessing=None):
    """
    Residual amortized approximation for the variational distribution of the latents: at level l, the parameters depend on
    the counts from level 0 to l amortized with residual connection for the last level,
    the latents at level l + 1, and the covariates.
    Parameters
    ----------
    tree: plntree.utils.utils.Tree
    covariates_params: dict or None
    embedder_type: str
    embedding_size: int
    n_embedding_layers: int
    n_embedding_neurons: int
    embedder_dropout: float
    n_after_layers: int
    preprocessing: str or None

    Returns
    -------

    """
    # The first layer is only getting embedder(X^{1:L}), X^{l}
    # The other layers are getting embedder(X^{1:l}), X^{l} and Z^{l + 1}
    # In the end, the size of the input "l" is K_{l + 1} + input_size + K_{l}
    embedder = Embedder(
        input_size=tree.K_max,
        embedding_size=embedding_size,
        hidden_size=n_embedding_neurons,
        n_layers=n_embedding_layers,
        recurrent_network=embedder_type,
        dropout=embedder_dropout,
        preprocessing=preprocessing
    )
    m_fun = nn.ModuleList()
    log_S_fun = nn.ModuleList()
    for level in range(tree.L):
        # The input size of X^{1:l} would be sum(self.K[:i+1])
        # But it's simpler now with the embedding!
        # It only gets X^{l} concatenated with the Embedding E^{l}
        input_size = tree.K[level] + embedding_size
        # If we are not at the last layer, the model also gets Z^{l+1} as input
        if level != tree.L - 1:
            input_size += tree.K_eff[level + 1]

        if covariates_params['size'] <= 0:
            m_l = nn.Sequential(
                PartialCountsPreprocessing(tree.K[level], preprocessing),
                DenseNeuralNetwork(input_size, input_size, tree.K_eff[level], n_after_layers),
                mean_bound
            )
            log_S_l = nn.Sequential(
                PartialCountsPreprocessing(tree.K[level], preprocessing),
                DenseNeuralNetwork(input_size, input_size, tree.K_eff[level], n_after_layers),
                log_variance_bound
            )
            m_l = CombinedNeuralNetworks(m_l, None, None, None)
            log_S_l = CombinedNeuralNetworks(log_S_l, None, None, None)
        else:
            if covariates_params['type'] == 'film':
                preprocessing_module = PartialCountsPreprocessing(tree.K[level], preprocessing)
                m_l_E = nn.Sequential(
                    DenseNeuralNetwork(input_size, input_size, tree.K_eff[level], n_after_layers),
                    mean_bound
                )
                m_l = AttentionFiLM(
                    m_l_E, preprocessing_module, covariates_params['size'],
                    input_size, covariates_params['n_layers'], None
                )

                log_S_l_E = nn.Sequential(
                    DenseNeuralNetwork(input_size, input_size, tree.K_eff[level], n_after_layers),
                    log_variance_bound
                )
                log_S_l = AttentionFiLM(
                    log_S_l_E, preprocessing_module, covariates_params['size'],
                    input_size, covariates_params['n_layers'], None
                )
            else:
                m_l_E = nn.Sequential(
                    PartialCountsPreprocessing(tree.K[level], preprocessing),
                    DenseNeuralNetwork(input_size, input_size, input_size, n_after_layers),
                )
                m_l = AttentionBasedCombiningLayer(
                            m_l_E, input_size, tree.K_eff[level], covariates_params['size'],
                            covariates_params['n_heads'], covariates_params['n_layers'],
                            mean_bound
                        )

                log_S_l_E = nn.Sequential(
                    PartialCountsPreprocessing(tree.K[level], preprocessing),
                    DenseNeuralNetwork(input_size, input_size, input_size, n_after_layers),
                )
                log_S_l = AttentionBasedCombiningLayer(
                            log_S_l_E, input_size, tree.K_eff[level], covariates_params['size'],
                            covariates_params['n_heads'], covariates_params['n_layers'],
                            log_variance_bound
                        )
        m_fun.append(m_l)
        log_S_fun.append(log_S_l)
    return m_fun, log_S_fun, embedder
