from sklearn_crfsuite.utils import flatten
import pandas as pd
from numpy import array
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.feature_extraction.text import CountVectorizer
from .BaseModel import BaseModel
from sklearn.svm import SVC
from sklearn.base import TransformerMixin


class ArrayTransformers(TransformerMixin):

    def fit(self, X, y=None, **fit_params):
        return self

    def transform(self, X, y=None, **fit_params):
        return X.toarray()


class ScikitLearnClassifiers(BaseModel):
    def __init__(
            self,
            scikit_learn_model={
                'model': SVC(
                    C=1,
                    kernel='rbf',
                    degree=3,
                    gamma='scale',
                    coef0=0.0,
                ),
                'model_name': 'svm_model',
                'sparse_to_dense': False
            },
            *args,
            **kwargs
    ):
        self.__model = scikit_learn_model['model']
        if 'feature_encoding' in kwargs:
            BaseModel.__init__(self,
                               model_clf=self.__model,
                               feature_encoding=kwargs['feature_encoding']
                               )
        else:
            BaseModel.__init__(self,
                               model_clf=self.__model,
                               )
        self.__label_encoder = LabelEncoder()
        self.__model_name = scikit_learn_model['model_name']
        self.__model_sparse_to_dense = scikit_learn_model['sparse_to_dense']

    def fit(self, data_train_df):
        # feature extraction
        train_features_2_df = self.__feature_formatting(data_train_df)

        # feature engineering pada data training
        feature_engineering_results = self.__feature_engineering(
            train_features_2_df)
        self.preprocessor = feature_engineering_results['preprocessor']
        self.X_TRAIN = feature_engineering_results['X']
        self.Y_TRAIN = feature_engineering_results['Y']

        # modelling
        pipeline = [
            ('preprocessor', self.preprocessor),
            (self.__model_name, self.__model)
        ]
        if self.__model_sparse_to_dense:
            pipeline.insert(1, ('sparse_to_dense', ArrayTransformers()))

        # fit into pipeline
        self.estimator = Pipeline(pipeline)
        self.estimator.fit(self.X_TRAIN, self.Y_TRAIN)
        return self

    def predict(self, data_test_df):
        # feature formatting for test data
        test_features_2_df = self.__feature_formatting(data_test_df)

        # prepare data input for test data
        self.X_TEST, y_test_labels = self.__separate_data_df_columns(
            test_features_2_df)

        # transform test label using Label Encoder
        self.Y_TEST = self.get_label_encoder().transform(y_test_labels)

        # predict for train and test data
        self.y_pred_train = self.estimator.predict(self.X_TRAIN)
        self.y_pred_test = self.estimator.predict(self.X_TEST)

        return self.y_pred_test

    def predict_sentence(self, sentence):
        # prepare format for sentence input
        token_sentence, sentence_features = super()._prepare_input_sentence(sentence)

        if len(token_sentence) == 1:
            # sentence input tidak valid, return /O
            tags_y_pred = array(['O'])
            token_with_predicted_tag = self.token_with_predicted_tags(
                token_sentence, tags_y_pred)
        else:
            # sentence input valid
            self.X_sentence_features = pd.DataFrame(sentence_features[0])

            # predict
            y_pred = self.estimator.predict(self.X_sentence_features)
            tags_y_pred = self.get_label_encoder().inverse_transform(y_pred)
            token_with_predicted_tag = self.token_with_predicted_tags(
                token_sentence, tags_y_pred)
        return tags_y_pred, token_with_predicted_tag

    def __feature_formatting(self, data_df):
        # convert data df to sequential data format
        data_df_2_sequential = self.dataframe2sequential(data_df)
        ner_label_data = flatten([self.sentence2labels(sentence)
                                 for sentence in data_df_2_sequential])

        # extract feature from sequential data format using feature BIT Encoding
        data_sequential_2_features = [self.sentence2features(
            sentence, self.FEATURE_ENCODING) for sentence in data_df_2_sequential]

        # convert feature to dataframe format
        data_features_2_df = pd.DataFrame()
        for sentence in data_sequential_2_features:
            row_to_concat = pd.DataFrame(sentence)
            data_features_2_df = pd.concat(
                [data_features_2_df, row_to_concat], ignore_index=True)

        # append label satua as a ground truth
        data_features_2_df['label'] = ner_label_data

        return data_features_2_df

    def __separate_data_df_columns(self,
                                   data,
                                   columns_description={
                                       'tokens': 'w[i]',
                                       'labels': 'label'
                                   }
                                   ):
        # separate X_features and Y_label
        Y_labels = data[columns_description['labels']]
        X_features = data.drop(
            columns=columns_description['labels'],
            axis=1
        )

        return X_features, Y_labels

    def _preprocess_label(self, labels):
        """
        <Description>
        Module untuk preprocessing labels sebelum masuk ke model ML

        <Input>
        - labels: List()
        List dari daftar label baik array atau list dengan dimensi 1

        <Output>
        - preprocessed_labels: List()
        List dari labels yang sudah dipreprocessing
        """
        # label encoding for NER label
        preprocessed_labels = self.get_label_encoder().transform(labels)
        return preprocessed_labels

    def __feature_engineering(self, data_features_df):
        """
        <Description>
        Module untuk pengelolaan feature dan memproses feature sesuai formatnya
        """
        # get initial data
        type_of_boolean_features = self.TYPE_OF_BOOLEAN_FEATURES

        # separate data columns from df
        x_train_features, y_train_labels = self.__separate_data_df_columns(
            data_features_df)

        # process the boolean feature types
        # 1. get the boolean column from data features df
        boolean_features = [x for x in x_train_features.columns.values if len(
            x.split(".")) > 1 if x.split('.')[1] in type_of_boolean_features]
        # 2. create pipeline for boolean features
        boolean_pipeline = Pipeline([
            ('nan_imputation', SimpleImputer(strategy='most_frequent')),
            ('standard_scaling', StandardScaler())
        ])

        # process the categorical feature types
        # 1. get the categorical column from data features df
        categorical_features = x_train_features.drop(
            columns=boolean_features, axis=1).columns.values
        # 2. create pipeline for categorical features
        categorical_pipeline = Pipeline([
            ('one_hot_encoding', OneHotEncoder(handle_unknown='ignore'))
        ])

        # merge all pipeline into 1 preprocessor steps of Columns Transformers
        preprocessor = ColumnTransformer([
            ('categorical', categorical_pipeline, categorical_features),
            ('boolean', boolean_pipeline, boolean_features)
        ])

        # preprocess label target
        self.get_label_encoder().fit(y_train_labels)
        y_train_le = self.get_label_encoder().transform(y_train_labels)

        # return value
        context = {
            'preprocessor': preprocessor,
            'X': x_train_features,
            'Y': y_train_le,
        }
        return context

    def get_label_encoder(self):
        return self.__label_encoder
