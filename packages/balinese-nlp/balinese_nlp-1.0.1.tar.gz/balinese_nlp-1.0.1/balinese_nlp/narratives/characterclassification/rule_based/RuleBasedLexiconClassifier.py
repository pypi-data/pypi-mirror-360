from pandas import DataFrame
from numpy import ndarray, where


class RuleBasedLexiconClassifier:
    def __init__(self,
                 label_encoder_model,
                 index_extracted_columns=[0, 1],
                 ):
        """
        Module untuk mengklasifikasikan polaritas dengan menggunakan algoritma pengklasifikasi sederhana berbasis lexicon
        <Parameters>
        - label_encoder_model: List()
            -> <Description>: Label encoder yang sudah dimapping dari y_true yang berisi label Protagonis atau Antagonis
        - index_extracted_columns: List()
            -> Description: index kolom yang mengandung fitur skor total polaritas positif dna skor total polaritas negatif. Secara default, index kolom 0 untuk skor total polaritas positif dan index kolom 1 untuk skor total polaritas negatif
            -> Default: [0,1]

        """
        self.positive_column_name = index_extracted_columns[0]
        self.negative_column_name = index_extracted_columns[1]
        self.label_encoder_model = label_encoder_model

    def fit(self, X):
        if isinstance(X, DataFrame):
            self.X_features = X.values
        elif isinstance(X, ndarray) or (type(X) is list):
            self.X_features = X
        else:
            raise Exception(
                'Does not fit with your data type! Please format your data type')
        return self

    def predict(self):
        """
        <Description>
        Method untuk memprediksi polaritas suatu kalimat berdasarkan total skor sentimen positif dan skor sentimen negatif. Proses prediksi juga memperhatikan apakah dilakukan lexicon enrichment atau tidak.
        """
        y_pred = where(self.X_features[:, 0] > self.X_features[
                       :, 1], "Protagonis", "Antagonis")
        self.y_pred = self.label_encoder_model.transform(y_pred)
        return self.y_pred
