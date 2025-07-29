from numpy import ndarray, zeros
from pandas import DataFrame
import os
from .BaseModelFeatureExtraction import BaseModelFeatureExtraction

class LexiconFeatureExtraction(BaseModelFeatureExtraction):
    """
    <Description>
    Module untuk ekstraksi fitur berbasis lexicon

    <Methods>
    - __init__(): mempersiapkan variabel initial untuk diproses pada method
    - fit(): memasukkan data yang akan diekstraksi fitur teksnya
    - transform(): melakukan proses ekstraksi fitur berbasis leksikon dari data yang dihasilkan dari method fit()
    - get_fetures_names_out(): mengembalikan daftar fitur yang diekstraksi
    - get_features_definition(): mengembalikan definisi feature default yang digunakan pada package ini

    <Features Definition>
    Secara default terdapat beberapa fitur leksikon yang diekstraksi
    - LF1: Total skor synset dengan polaritas positif
    - LF2: Total skor synset dengan polaritas negatif
    - LF3: Jumlah kata-kata dengan polaritas positif
    - LF4: Jumlah kata-kata dengan polaritas negatif
    - LF5: Jumlah kata-kata dengan polaritas positif untuk kelas kata adjective
    - LF6: Jumlah kata-kata dengan polaritas negatif untuk kelas kata adjective
    - LF7: Jumlah kata-kata dengan polaritas positif untuk kelas kata verb
    - LF8: Jumlah kata-kata dengan polaritas negatif untuk kelas kata verb
    - LF9: Jumlah kata-kata dengan polaritas positif untuk kelas kata adverb
    - LF10: Jumlah kata-kata dengan polaritas negatif untuk kelas kata adverb
    - LF11: Total skor synset dengan polaritas positif untuk kelas kata adjective
    - LF12: Total skor synset dengan polaritas negatif untuk kelas kata adjective
    - LF13: Total skor synset dengan polaritas positif untuk kelas kata verb
    - LF14: Total skor synset dengan polaritas negatif untuk kelas kata verb
    - LF15: Total skor synset dengan polaritas positif untuk kelas kata adverb
    - LF16: Total skor synset dengan polaritas negatif untuk kelas kata adverb
    """

    def __init__(self,
                 lexicons={
                     'lexicon_terms': None,
                     'lexicon_tags': None,
                     'lexicon_positive_scores': None,
                     'lecixon_negative_scores': None
                 },
                 list_of_feature="__all__",
                 lexicon_enrichment={
                     'negation_words': False,
                     'booster_words': False
                 },
                 lexicon_enrichment_files={
                     'negation_words': '../results/balinese_lexicon_SentiWordNet/negation_words.txt',
                     'booster_words': '../results/balinese_lexicon_SentiWordNet/booster_words.txt'
                 },
                 tags_dictionary={
                     'noun': 'NN',
                     'adjective': 'JJ',
                     'adverb': 'RB',
                     'verb': 'VB'
                 },
                 text_column_to_extracted='preprocessed_context_sentence'
                 ):
        """
        <Input>
        - lexicons: <Dict>
            -> <Description>: Lexicon yang menjadi acuan untuk proses ekstraksi fitur
            -> 'lexicon_terms': <List>
            -> 'lexicon_tags': <List>
            -> 'lexicon_positive_scores': <List>
            -> 'lecixon_negative_scores': <List>
        - list_of_feature: <List of str>
            -> <Description>: Daftar kode fitur yang digunakan LF1 - LF16
            -> <Default>: Menggunakan semua fitur LF1 - LF16
            -> <Example>: ['LF1', 'LF5', 'LF12']
        - lexicon_enrichment : <Dict>
            -> <Description>: Daftar step untuk lexicon enrichment yang akan dilakukan, terdiri dari negation word handling dan booster words
            -> <Input>:
                (a) If negation_words is True -> Tahap negation handling dilakukan terhadap index kolom 0 dan 1
                (b) If booster_words is True -> Tahap booster words dilakukan terhadap index kolom 0 dan 1
        - tags_dictionary: <Dict>
            -> <Description>: pasangan key value antara kelas kata dengan kode kelas katanya
        - text_column_to_extracted: <str>
            -> <Description>: nama kolom dari dataframe yang dimasukkan pada method fit() yang akan diekstraksi fitur teksnya

        """
        # DEFINE CONSTANT
        self.NUMBER_OF_ALL_FEATURES = 16
        self.CODE_FEATURE = 'LF'

        # run parent init method
        super().__init__(
            list_of_feature=list_of_feature,
            number_of_all_features=self.NUMBER_OF_ALL_FEATURES,
            code_feature=self.CODE_FEATURE
        )

        # initialize variables from child class
        self.lexicon_terms = lexicons['lexicon_terms']
        self.lexicon_tags = lexicons['lexicon_tags']
        self.lexicon_positive_scores = lexicons['lexicon_positive_scores']
        self.lecixon_negative_scores = lexicons['lecixon_negative_scores']
        self.text_column_to_extracted = text_column_to_extracted
        self.tags_dictionary = tags_dictionary
        self.is_negation_words = lexicon_enrichment['negation_words']
        self.is_booster_words = lexicon_enrichment['booster_words']

        # results variables from processing
        self.lexicon_extracted_features = None

        # list of negation words and booster words by default
        self.ROOT_DIRECTORY = os.path.abspath(
            os.path.join(os.getcwd(), os.pardir))
        self.LEXICON_ENRICHMENT_FILES = lexicon_enrichment_files
        if self.is_negation_words:
            if type(lexicon_enrichment_files['negation_words']) is list:
                self.negation_words = [line.strip().lower()
                                       for line in lexicon_enrichment_files['negation_words'] if line.strip() != '']
            elif type(lexicon_enrichment_files['negation_words']) is str:
                self.__initialize_lexicon_enrichment()

        if self.is_booster_words:
            if type(lexicon_enrichment_files['booster_words']) is list:
                self.booster_words = [line.strip().lower()
                                      for line in lexicon_enrichment_files['booster_words'] if line.strip() != '']
            elif type(lexicon_enrichment_files['booster_words']) is str:
                self.__initialize_lexicon_enrichment()

    def fit(self, X):
        self.lexicon_extracted_features = self._initialize_extracted_features()
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
        <Description>
        Ekstraksi fitur berbasis leksikon serta lexicon enrichment jika ada
        """
        if not self._IS_FIT_METHOD:
            raise Exception('Please fit your data first using fit method!')

        lexicon_extracted_features = self.lexicon_extracted_features.copy()
        for sentence in self.X_features:
            # tokenize sentence
            tokens_sentence = [token.strip().lower()
                               for token in sentence.split(' ')]

            # buat dictionary of list from each feature code
            temp_extracted_features = dict([
                (feature_code, list()) for feature_code in self.list_of_feature
            ])
            temp_extracted_features['LF1'] = zeros(len(tokens_sentence))
            temp_extracted_features['LF2'] = zeros(len(tokens_sentence))

            # feature extraction process for each feature code
            flag_booster_words_index = None
            for idx_term, term in enumerate(tokens_sentence):
                if term in self.lexicon_terms:
                    # get the positive, negative scores and term POS Tag
                    positive_score_term = self.lexicon_positive_scores[self.lexicon_terms.index(
                        term)]
                    negative_score_term = self.lecixon_negative_scores[self.lexicon_terms.index(
                        term)]
                    tag_term = self.lexicon_tags[self.lexicon_terms.index(
                        term)]

                    # extract f1 (positif polarity score) dan f2 (negative polarity score)
                    if self.is_negation_words:
                        if idx_term > 0 and idx_term <= len(tokens_sentence)-1:
                            if tokens_sentence[idx_term-1] in self.negation_words:
                                # swap skor positif dan negatif
                                positive_score_term, negative_score_term = negative_score_term, positive_score_term
                                temp_extracted_features['LF1'][idx_term-1] = 0
                                temp_extracted_features['LF2'][idx_term-1] = 0
                    if self.is_booster_words:
                        if idx_term < len(tokens_sentence)-1:
                            if tokens_sentence[idx_term+1] in self.booster_words:
                                flag_booster_words_index = idx_term+1
                                # atur nilai maksimum menjadi 1 pada polaritas tertinggi
                                if positive_score_term > negative_score_term:
                                    positive_score_term, negative_score_term = 1, 0
                                elif negative_score_term > positive_score_term:
                                    negative_score_term, positive_score_term = 1, 0

                    if 'LF1' in self.list_of_feature:
                        temp_extracted_features['LF1'][idx_term] = positive_score_term
                        if flag_booster_words_index == idx_term:
                            temp_extracted_features['LF1'][idx_term] = 0
                    if 'LF2' in self.list_of_feature:
                        temp_extracted_features['LF2'][idx_term] = negative_score_term
                        if flag_booster_words_index == idx_term:
                            temp_extracted_features['LF2'][idx_term] = 0

                    # extract f3 and f5, f7, f9
                    if 'LF3' in self.list_of_feature:
                        if positive_score_term > negative_score_term:
                            temp_extracted_features['LF3'].append(1)
                            if 'LF5' in self.list_of_feature:
                                if tag_term == self.tags_dictionary['adjective']:
                                    temp_extracted_features['LF5'].append(
                                        1)
                            if 'LF7' in self.list_of_feature:
                                if tag_term == self.tags_dictionary['verb']:
                                    temp_extracted_features['LF7'].append(
                                        1)
                            if 'LF9' in self.list_of_feature:
                                if tag_term == self.tags_dictionary['adverb']:
                                    temp_extracted_features['LF9'].append(
                                        1)
                            if 'LF11' in self.list_of_feature:
                                if tag_term == self.tags_dictionary['adjective']:
                                    temp_extracted_features['LF11'].append(
                                        positive_score_term)
                            if 'LF13' in self.list_of_feature:
                                if tag_term == self.tags_dictionary['verb']:
                                    temp_extracted_features['LF13'].append(
                                        positive_score_term)
                            if 'LF15' in self.list_of_feature:
                                if tag_term == self.tags_dictionary['adverb']:
                                    temp_extracted_features['LF15'].append(
                                        positive_score_term)

                    # extract f4 and f6, f8, f10
                    if 'LF4' in self.list_of_feature:
                        if negative_score_term > positive_score_term:
                            temp_extracted_features['LF4'].append(1)
                            if 'LF6' in self.list_of_feature:
                                if tag_term == self.tags_dictionary['adjective']:
                                    temp_extracted_features['LF6'].append(
                                        1)
                            if 'LF8' in self.list_of_feature:
                                if tag_term == self.tags_dictionary['verb']:
                                    temp_extracted_features['LF8'].append(
                                        1)
                            if 'LF10' in self.list_of_feature:
                                if tag_term == self.tags_dictionary['adverb']:
                                    temp_extracted_features['LF10'].append(
                                        1)
                            if 'LF12' in self.list_of_feature:
                                if tag_term == self.tags_dictionary['adjective']:
                                    temp_extracted_features['LF12'].append(
                                        negative_score_term)
                            if 'LF14' in self.list_of_feature:
                                if tag_term == self.tags_dictionary['verb']:
                                    temp_extracted_features['LF14'].append(
                                        negative_score_term)
                            if 'LF16' in self.list_of_feature:
                                if tag_term == self.tags_dictionary['adverb']:
                                    temp_extracted_features['LF16'].append(
                                        negative_score_term)

            # summarize all features and append into dictionary
            for feature_code in self.list_of_feature:
                lexicon_extracted_features[feature_code].append(
                    sum(temp_extracted_features[feature_code]))

        # convert data format into DataFrame
        self.lexicon_extracted_features = DataFrame(lexicon_extracted_features)
        self._IS_TRANSFORM_METHOD = True
        return self.lexicon_extracted_features

    def __initialize_lexicon_enrichment(self):
        # initialize list of negation words
        file_path = os.path.join(
            self.ROOT_DIRECTORY, self.LEXICON_ENRICHMENT_FILES['negation_words'])
        with open(file_path, 'r') as file:
            lines = file.readlines()
        self.negation_words = [line.strip().lower()
                               for line in lines if line.strip() != '']

        # initialize list of booster words
        file_path = os.path.join(
            self.ROOT_DIRECTORY, self.LEXICON_ENRICHMENT_FILES['booster_words'])
        with open(file_path, 'r') as file:
            lines = file.readlines()
        self.booster_words = [line.strip().lower()
                              for line in lines if line.strip() != '']
