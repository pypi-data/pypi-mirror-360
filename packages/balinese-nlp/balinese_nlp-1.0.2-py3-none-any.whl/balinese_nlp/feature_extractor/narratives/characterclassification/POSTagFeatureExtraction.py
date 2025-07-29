from pandas import DataFrame
from numpy import ndarray
from string import punctuation
from balinese_nlp.postag.HMM import HiddenMarkovModelPOSTag
from .BaseModelFeatureExtraction import BaseModelFeatureExtraction


class POSTagFeatureExtraction(BaseModelFeatureExtraction):
    """
    <Description>
    Module untuk ekstraksi fitur POS Tag pada teks

    <Methods>
    - __init__(): mempersiapkan variabel initial untuk diproses pada method
    - fit(): memasukkan data yang akan diekstraksi fitur teksnya
    - transform(): melakukan proses ekstraksi fitur berbasis leksikon dari data yang dihasilkan dari method fit()
    - get_fetures_names_out(): mengembalikan daftar fitur yang diekstraksi
    - get_features_definition(): mengembalikan definisi feature default yang digunakan pada package ini

    <Features Definition>
    Secara default terdapat beberapa fitur leksikon yang diekstraksi
    - PTF1: Persentase kata-kata dengan kelas kata noun pada teks
    - PTF2: Persentase kata-kata dengan kelas kata adjective pada teks
    - PTF3: Persentase kata-kata dengan kelas kata adverb pada teks
    - PTF4: Persentase kata-kata dengan kelas kata verb pada teks
    """

    def __init__(
        self,
        list_of_feature="__all__",
        tags_dictionary={
            'noun': 'NN',
            'adjective': 'JJ',
            'adverb': 'RB',
            'verb': 'VB'
        },
        text_column_to_extracted='context_sentence'

    ):
        """
        <Input>
        - list_of_feature: <List of str>
            -> <Description>: Daftar kode fitur yang digunakan PTF1 - PTF4
            -> <Default>: Menggunakan semua fitur PTF1 - PTF4
            -> <Example>: ['PTF1', 'PTF2', 'PTF3']
        - tags_dictionary: <Dict>
            -> <Description>: pasangan key value antara kelas kata dengan kode kelas katanya
        - text_column_to_extracted: <str>
            -> <Description>: nama kolom dari dataframe yang dimasukkan pada method fit() yang akan diekstraksi fitur teksnya
        """
        # DEFINE CONSTANT
        self.NUMBER_OF_ALL_FEATURES = 4
        self.CODE_FEATURE = 'PTF'

        # run parent init method
        super().__init__(
            list_of_feature=list_of_feature,
            number_of_all_features=self.NUMBER_OF_ALL_FEATURES,
            code_feature=self.CODE_FEATURE
        )

        # initialize variables from child class
        self.text_column_to_extracted = text_column_to_extracted
        self.tags_dictionary = tags_dictionary

        # initialize variables from external sources
        self.punctuation = punctuation

        # initialize pos tagger
        self.POSTag = HiddenMarkovModelPOSTag()

    def fit(self, X):
        self.pos_tag_extracted_features = self._initialize_extracted_features()
        if isinstance(X, DataFrame):
            self.X_features = X[self.text_column_to_extracted].values
        elif isinstance(X, ndarray) or (type(X) is list):
            self.X_features = X
        else:
            raise TypeError(
                'Does not fit with your data type! Please format your data type')
        self.__IS_FIT_METHOD = True
        return self

    def transform(self):
        """
        Ekstraksi fitur berbasis leksikon serta lexicon enrichment jika ada
        """
        if not self.__IS_FIT_METHOD:
            raise Exception('Please fit your data first using fit method!')

        for sentences in self.X_features:

            # buat dictionary of list from each feature code
            temp_extracted_features = dict([
                (feature_code, list()) for feature_code in self.list_of_feature
            ])

            # get POS Tag labels from sentences
            token_with_pos_tag = self.POSTag.predict(sentences).strip().split(' ')
            token_with_pos_tag_dict = dict([
                (token_tag.split('/')[0], token_tag.split('/')[1]) for token_tag in token_with_pos_tag
            ])

            # feature extraction process for each feature code
            for token, pos_tag in token_with_pos_tag_dict.items():
                if token not in self.punctuation:
                    # extract PTF1
                    if 'PTF1' in self.list_of_feature:
                        if pos_tag == self.tags_dictionary['noun']:
                            temp_extracted_features['PTF1'].append(1)

                    # extract PTF2
                    if 'PTF2' in self.list_of_feature:
                        if pos_tag == self.tags_dictionary['adjective']:
                            temp_extracted_features['PTF2'].append(1)

                    # extract PTF3
                    if 'PTF3' in self.list_of_feature:
                        if pos_tag == self.tags_dictionary['adverb']:
                            temp_extracted_features['PTF3'].append(1)

                    # extract PTF4
                    if 'PTF4' in self.list_of_feature:
                        if pos_tag == self.tags_dictionary['verb']:
                            temp_extracted_features['PTF4'].append(1)

            # summarize all features and append into dictionary
            total_percentage = total_sum = sum(
                sum(values) for values in temp_extracted_features.values())
            for feature_code in self.list_of_feature:
                if total_percentage == 0:
                    self.pos_tag_extracted_features[feature_code].append(0)
                else:
                    self.pos_tag_extracted_features[feature_code].append(
                        sum(temp_extracted_features[feature_code])/total_percentage)

        # convert dictionary results into Dataframe
        self.pos_tag_extracted_features = DataFrame(
            self.pos_tag_extracted_features)
        self.__IS_TRANSFORM_METHOD = True

        return self.pos_tag_extracted_features
