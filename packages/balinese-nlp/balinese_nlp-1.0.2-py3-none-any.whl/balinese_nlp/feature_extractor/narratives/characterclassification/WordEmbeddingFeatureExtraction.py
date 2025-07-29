from pandas import DataFrame
from numpy import ndarray, zeros, array


class WordEmbeddingFeatureExtraction:

    def __init__(self, pretrained_word_embedding, text_column_to_extracted='preprocessed_context_sentence'):
        self.word_embedding_extracted_features = None
        self.pretrained_word_embedding = pretrained_word_embedding
        self.text_column_to_extracted = text_column_to_extracted
        self._IS_FIT_METHOD = False
        self._IS_TRANSFORM_METHOD = False

    def fit(self, X):
        if isinstance(X, DataFrame):
            self.X_features = X[self.text_column_to_extracted].values
        elif isinstance(X, ndarray) or (type(X) is list):
            self.X_features = X
        else:
            raise TypeError(
                'Does not fit with your data type! Please format your data type')
        self._IS_FIT_METHOD = True
        return self

    def transform(self):
        """
        Ekstraksi fitur berbasis word embedding
        """
        if not self._IS_FIT_METHOD:
            raise Exception('Please fit your data first using fit method!')

        self.word_embedding_extracted_features = list()
        model = self.pretrained_word_embedding
        vector_size = model.vector_size

        # calculate average word vector for each sentence
        for sentence in self.X_features:
            words = sentence.split()
            word_vectors = [self.pretrained_word_embedding.wv[word]
                            for word in words if word in self.pretrained_word_embedding.wv]
            if word_vectors:
                # Calculate the average vector for the sentence
                sentence_vector = sum(word_vectors) / len(word_vectors)
            else:
                sentence_vector = zeros(vector_size)
            self.word_embedding_extracted_features.append(sentence_vector)
        self._IS_TRANSFORM_METHOD = True
        self.word_embedding_extracted_features = array(
            self.word_embedding_extracted_features)
        return self.word_embedding_extracted_features
