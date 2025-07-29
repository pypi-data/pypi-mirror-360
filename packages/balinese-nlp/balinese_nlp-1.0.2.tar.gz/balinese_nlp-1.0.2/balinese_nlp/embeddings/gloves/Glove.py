import numpy as np
import matplotlib.pyplot as plt
import pickle
import itertools
from collections import Counter
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity


class Glove:
    def __init__(self, n_epochs=100, eps=0.001, n_sents=10, embedding_size=50, alpha=0.1, delta=0.8, window_size=5, save_weights=True, save_model=True, save_filepath="./"):
        self.hyperparameters = {
            'n_epochs': n_epochs,  # number of training epochs
            'eps': eps,  # tolerance
            'n_sents': n_sents,  # number of sentences to consider
            'embedding_size': embedding_size,  # weight embedding size
            'alpha': alpha,  # learning rate
            'delta': delta,  # AdaGrad parameter
            'window_size': window_size,  # context_window_size
        }
        self.save_model = save_model
        self.save_weights = save_weights
        self.save_filepath = save_filepath
        self.IS_FIT = False
        self.IS_TRAIN = False

    def fit(self, tokens, processed_sents, token2int, int2token):
        self.tokens = tokens
        self.n_tokens = len(tokens)
        # Bersihkan processed_sents dari entri yang tidak valid
        self.processed_sents = [
            s for s in processed_sents
            if s and isinstance(s, list) and all(isinstance(item, str) for item in s)
        ]
        self.token2int = token2int
        self.int2token = int2token
        self.IS_FIT = True
        return self

    def train(self):
        if not self.IS_FIT:
            raise TypeError('Please fit your data first!')
        embedding_size = self.hyperparameters['embedding_size']
        n_tokens = self.n_tokens

        # train procedure
        self.co_occurence_matrix = self.__get_co_occurence_matrix()
        weights_init = np.random.random((2 * n_tokens, embedding_size))
        bias_init = np.random.random((2 * n_tokens,))
        self.weights, self.bias, self.norm_grad_weights, self.norm_grad_bias, self.costs, self.last_n_epochs = self.__adagrad(
            weights_init, bias_init)  # glove training procedure

        self.IS_TRAIN = True
        # saving weights
        if self.save_weights:
            self.__save_weights()

        # saving model
        if self.save_model:
            self.__save_model()

        return self

    def retrieve_trained_weights(self):
        if not self.IS_TRAIN:
            raise TypeError('Please train your glove first!')

        return self.weights

    def plot_training_results(self):
        """
        Function for plotting learning curves
        """
        if not self.IS_TRAIN:
            raise TypeError('Please train your glove first!')

        costs = self.costs
        norm_grad_weights = self.norm_grad_weights
        norm_grad_bias = self.norm_grad_bias
        last_n_epochs = self.last_n_epochs

        plt.figure(figsize=(20, 5))

        plt.subplot(131)
        plt.plot(costs[-last_n_epochs:], c='k')
        plt.title('cost')
        plt.xlabel('epochs')
        plt.ylabel('value')

        plt.subplot(132)
        plt.plot(norm_grad_weights[-last_n_epochs:], c='k')
        plt.title('norm_weights')
        plt.xlabel('epochs')
        plt.ylabel('value')

        plt.subplot(133)
        plt.plot(norm_grad_bias[-last_n_epochs:], c='k')
        plt.title('norm_bias')
        plt.xlabel('epochs')
        plt.ylabel('value')
        plt.show()

    def plotting_word_vectors(self, weights, n_tokens):
        """
        Function for plotting word vectors in 2D using PCA based on inputted weights
        """
        tokens = self.tokens

        pca = PCA(n_components=2)
        weights = pca.fit_transform(weights[:n_tokens])
        explained_var = (100 * sum(pca.explained_variance_)).round(2)
        print(f'Variance explained by 2 components: {explained_var}%')

        fig, ax = plt.subplots(figsize=(20, 10))
        for word, x1, x2 in zip(tokens, weights[:, 0], weights[:, 1]):
            ax.annotate(word, (x1, x2))

        x_pad = 0.5
        y_pad = 1.5
        x_axis_min = np.amin(weights, axis=0)[0] - x_pad
        x_axis_max = np.amax(weights, axis=0)[0] + x_pad
        y_axis_min = np.amin(weights, axis=1)[1] - y_pad
        y_axis_max = np.amax(weights, axis=1)[1] + y_pad

        plt.xlim(x_axis_min, x_axis_max)
        plt.ylim(y_axis_min, y_axis_max)
        plt.rcParams["figure.figsize"] = (10, 10)
        plt.show()

    def get_word_vector(self, word):
        """
        Function for retrieving word vector from certain word
        Args:
            word (str): Kata yang ingin diambil vektornya.

        Returns:
            np.array: Vektor embedding kata.
            None: Jika kata tidak ditemukan dalam kosakata.
        """
        if not self.IS_TRAIN:
            raise TypeError('Please train your GloVe model first!')

        if word in self.token2int:
            word_idx = self.token2int[word]
            # Vektor kata disimpan di bagian pertama dari self.weights
            return self.weights[word_idx]
        else:
            print(f"Warning: Word '{word}' not found in vocabulary.")
            return None

    def get_word_context_vector(self, word):
        """
        Function for retrieving word context vector from certain word
        """
        if not self.IS_TRAIN:
            raise TypeError('Please train your GloVe model first!')

        if word in self.token2int:
            word_idx = self.token2int[word]
            # Vektor konteks disimpan di bagian kedua dari self.weights
            return self.weights[self.n_tokens + word_idx]
        else:
            print(f"Warning: Word '{word}' not found in vocabulary.")
            return None

    def get_final_embedding_vector(self, word):
        """
        Function for finding word vector retrieved from averaging word vector and context vector
        """
        if not self.IS_TRAIN:
            raise TypeError('Please train your GloVe model first!')

        word_vector = self.get_word_vector(word)
        context_vector = self.get_word_context_vector(word)

        if word_vector is not None and context_vector is not None:
            return (word_vector + context_vector) / 2
        else:
            return None  # Salah satu atau keduanya tidak ditemukan

    def update_weights_final_embedding_vector(self):
        if self.IS_TRAIN is False:
            print('Warning: Please train your Glove model first!')
            return
        # update the weights vector to final embedding vectors for each word
        shape_vector = (self.n_tokens, self.hyperparameters['embedding_size'])
        weights_final_embedding = np.random.random(shape_vector)
        for idx, token in enumerate(self.tokens):
            if token in self.token2int:
                weights_final_embedding[idx] = self.get_final_embedding_vector(
                    token)
            else:
                weights_final_embedding[idx] = np.zeros(shape_vector)
        return weights_final_embedding

    def most_similar(self, token, topN):
        """
        Function for finding topN similar words for inputted token with context+word vectors
        """
        if not self.IS_TRAIN:
            raise TypeError('Please train your glove first!')

        weights_final_embedding = self.update_weights_final_embedding_vector()

        # getting cosine similarities between all combinations of word vectors
        csim = cosine_similarity(weights_final_embedding[:self.n_tokens])
        # masking diagonal values since they will be most similar
        np.fill_diagonal(csim, 0)

        # find similar words based on cosine similarity matrix
        token_idx = self.token2int[token]
        closest_words = list(
            map(lambda x: self.int2token[x], np.argsort(csim[token_idx])[::-1][:topN]))

        return closest_words

    def loading_weights(self, filepath):
        """
        Function for loading pretrained glove weights saved in filepath. The pretrained glove embedding was saved using *.npy format
        """
        print(f'Loading weights from {filepath}')
        loaded_weights = np.load(filepath, allow_pickle=True)
        return loaded_weights

    def __get_co_occurences(self, token):
        window_size = self.hyperparameters['window_size']
        processed_sents = self.processed_sents

        co_occurences = []
        for sent in processed_sents:
            # pastikan sent adalah list dari string
            if not isinstance(sent, list) or not all(isinstance(item, str) for item in sent):
                continue  # skip jika format sent tidak sesuai

            sent_array = np.array(sent)
            # Ini adalah perbaikan utama
            # np.where mengembalikan tuple array, kita ingin elemen pertama ([0])
            # yang berisi indeks tempat kondisi True
            for idx in np.where(sent_array == token)[0]:
                co_occurences.append(
                    sent[max(0, idx-window_size):min(idx+window_size+1, len(sent))])

        co_occurences = list(itertools.chain(*co_occurences))
        # Perbaikan: gunakan self.token2int
        # Filter out OOV tokens
        co_occurence_idxs = [self.token2int[x]
                             for x in co_occurences if x in self.token2int]
        co_occurence_dict = Counter(co_occurence_idxs)
        co_occurence_dict = dict(sorted(co_occurence_dict.items()))
        return co_occurence_dict

    def __get_co_occurence_matrix(self):
        tokens = self.tokens
        # token2int is already a class attribute, no need to pass it again
        token2int = self.token2int  # access from self

        co_occurence_matrix = np.zeros(
            shape=(len(tokens), len(tokens)), dtype='int')
        for token in tokens:
            # Perbaikan: Pastikan token ada di token2int sebelum mencoba mengaksesnya
            if token not in token2int:
                continue  # Lewati token yang tidak ada di vocabulary
            token_idx = token2int[token]
            co_occurence_dict = self.__get_co_occurences(token)
            # Pastikan indeks dari co_occurence_dict juga ada di dalam rentang
            # co_occurence_matrix[token_idx, list(co_occurence_dict.keys())] = list(co_occurence_dict.values())

            # Lebih aman: iterasi dan tetapkan
            for co_idx, count in co_occurence_dict.items():
                if co_idx < len(tokens):  # Pastikan indeks valid
                    co_occurence_matrix[token_idx, co_idx] = count

        np.fill_diagonal(co_occurence_matrix, 0)
        return co_occurence_matrix

    def __f(self, X_wc, X_max):
        alpha = self.hyperparameters['alpha']
        # Handle log(0) case for X_wc = 0 (co-occurrence = 0)
        if X_wc == 0:
            return 0  # If there's no co-occurrence, the weight function should be 0 or contribute 0 to the loss
        if X_wc < X_max:
            return (X_wc/X_max)**alpha
        else:
            return 1

    def __gradient(self, weights, bias, co_occurence_matrix, X_max):
        n_tokens = self.n_tokens
        # embedding_size = self.hyperparameters['embedding_size'] # not directly used here

        dw = np.zeros(weights.shape)
        db = np.zeros(bias.shape)

        # Loop through all possible word-context pairs in the co-occurrence matrix
        # This is typically done by iterating over non-zero elements for efficiency
        # For a dense matrix, this double loop is fine but can be slow for large vocabularies

        for idx_word in range(n_tokens):
            for idx_context in range(n_tokens):
                X_wc = co_occurence_matrix[idx_word, idx_context]
                if X_wc == 0:  # Only calculate for existing co-occurrences
                    continue

                w_word = weights[idx_word]
                w_context = weights[n_tokens + idx_context]
                b_word = bias[idx_word]
                b_context = bias[n_tokens + idx_context]

                # Calculate the core difference term: (w_i^T * w_j + b_i + b_j - log(X_ij))
                # np.log(1+X_wc) is more common to avoid log(0)
                diff = np.dot(w_word.T, w_context) + \
                    b_word + b_context - np.log(X_wc)

                # Weighting function f(X_wc)
                f_X_wc = self.__f(X_wc, X_max)

                # Gradient updates (simplified, check original GloVe paper for exact derivatives)
                # The paper's update rule usually involves f(X_ij) * (w_i^T w_j + b_i + b_j - log X_ij)
                # multiplied by w_j for dw_i, etc.

                # Let's re-align with GloVe paper's derivative:
                # dL/dw_i = f(X_ij) * (w_i^T w_j + b_i + b_j - log X_ij) * w_j
                # dL/dw_j = f(X_ij) * (w_i^T w_j + b_i + b_j - log X_ij) * w_i
                # dL/db_i = f(X_ij) * (w_i^T w_j + b_i + b_j - log X_ij)
                # dL/db_j = f(X_ij) * (w_i^T w_j + b_i + b_j - log X_ij)

                # Error term (delta in original paper)
                error_term = f_X_wc * diff

                dw[idx_word] += error_term * w_context
                dw[n_tokens + idx_context] += error_term * \
                    w_word  # update for context vector
                db[idx_word] += error_term
                db[n_tokens + idx_context] += error_term

        return dw, db

    def __loss_fn(self, weights, bias, co_occurence_matrix, X_max):
        n_tokens = self.n_tokens
        total_cost = 0
        for idx_word in range(n_tokens):
            for idx_context in range(n_tokens):
                X_wc = co_occurence_matrix[idx_word, idx_context]
                if X_wc == 0:
                    continue  # Skip if no co-occurrence

                w_word = weights[idx_word]
                w_context = weights[n_tokens+idx_context]
                b_word = bias[idx_word]
                b_context = bias[n_tokens+idx_context]

                # Ensure np.log(X_wc) doesn't become log(0) if X_wc is 0 (though we skip if X_wc=0)
                # Use np.log(1 + X_wc) for robustness if X_wc can be 0 or small
                # Or, as per the original GloVe paper, it's typically log(X_ij).
                # Your __f function should handle X_wc=0 by returning 0, making the term 0.
                # Changed from np.log(1 + X_wc) to np.log(X_wc) based on typical GloVe formula if X_wc > 0
                term = np.dot(w_word.T, w_context) + \
                    b_word + b_context - np.log(X_wc)

                total_cost += self.__f(X_wc, X_max) * (term)**2
        return total_cost

    def __adagrad(self, weights_init, bias_init):
        """
        Adam gradient function to train Glove model
        """
        n_epochs = self.hyperparameters['n_epochs']
        alpha = self.hyperparameters['alpha']  # This is the learning rate
        eps = self.hyperparameters['eps']  # Tolerance for convergence
        # AdaGrad epsilon for numerical stability, usually a small number
        delta = self.hyperparameters['delta']
        co_occurence_matrix = self.co_occurence_matrix.copy()

        # adagrad procedure
        # 1. initialization
        weights = weights_init
        bias = bias_init

        # Accumulators for squared gradients (AdaGrad 'r' terms)
        r_weights = np.zeros(weights.shape)
        r_bias = np.zeros(bias.shape)

        # Or a predefined X_max, e.g., 100 as in original GloVe paper
        X_max = np.max(co_occurence_matrix)
        if X_max == 0:  # Avoid division by zero in __f if co-occurrence matrix is all zeros
            print(
                "Warning: Co-occurrence matrix is all zeros. Training may not proceed correctly.")
            X_max = 1  # Set a dummy value to avoid division by zero, though training won't be meaningful

        # 2. loops
        norm_grad_weights = []
        norm_grad_bias = []
        costs = []
        n_iter = 0
        # Start with a high cost to ensure at least one iteration
        cost = float('inf')

        while cost > eps:  # Loop until cost converges or max epochs reached
            dw, db = self.__gradient(weights, bias, co_occurence_matrix, X_max)

            # AdaGrad updates
            r_weights += (dw)**2
            r_bias += (db)**2

            # Apply learning rate 'alpha' and numerical stability 'delta' (which you called delta, typically epsilon)
            weights -= (alpha / (delta + np.sqrt(r_weights))) * dw
            bias -= (alpha / (delta + np.sqrt(r_bias))) * db

            cost = self.__loss_fn(weights, bias, co_occurence_matrix, X_max)

            if n_iter % 200 == 0:
                print(f'Cost at {n_iter} iterations: {cost.round(3)}')

            norm_grad_weights.append(np.linalg.norm(dw))
            norm_grad_bias.append(np.linalg.norm(db))
            costs.append(cost)
            n_iter += 1

            if n_iter >= n_epochs:
                print(
                    f'Maximum epochs ({n_epochs}) reached. Stopping training.')
                break  # Break if max epochs reached even if not converged

        last_n_epochs = n_iter
        if cost <= eps:  # Check final convergence state
            print(f'Converged in {len(costs)} epochs..')
        else:
            print(
                f'Training complete with {n_epochs} epochs.. (Did not converge to eps={eps})')

        return weights, bias, norm_grad_weights, norm_grad_bias, costs, last_n_epochs

    def __save_weights(self):
        # Ensure the save_filepath is set and exists
        if self.save_filepath is None:
            print("Warning: save_filepath is not set. Weights will not be saved.")
            return
        if self.IS_TRAIN is False:
            print("Warning: Please train your Glove model first!")
            return

        filename = f"{self.save_filepath}/{self.hyperparameters['embedding_size']}_glove_weights.npy"
        np.save(filename, self.weights)
        print(f'Weights was succesfully saved in {filename}')

    def __save_model(self):
        if self.save_filepath is None:
            print("Warning: save_filepath is not set. Weights will not be saved.")
            return
        if self.IS_TRAIN is False:
            print("Warning: Please train your Glove model first!")
            return
        filename = f"{self.save_filepath}/{self.hyperparameters['embedding_size']}_glove_model.pkl"
        pickle.dump(self, open(filename, 'wb'))
        print(f'Pretrained Model was succesfully saved in {filename}')
