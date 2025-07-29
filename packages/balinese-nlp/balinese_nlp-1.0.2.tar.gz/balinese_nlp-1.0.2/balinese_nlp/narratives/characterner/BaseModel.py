from sklearn_crfsuite.utils import flatten
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
from balinese_nlp.postag.HMM import HiddenMarkovModelPOSTag
from balinese_nlp.textpreprocessor import TextPreprocessor
import pandas as pd
import numpy as np
import pickle


class BaseModel:
    def __init__(
        self,
        model_clf=None,
        feature_encoding={
            'w[i]': True,
            'w[i].lower()': True,
            'surr:w[i]': True,
            'surr:w[i].lower()': True,
            'pref:w[i]': True,
            'suff:w[i]': True,
            'surrPreff:w[i]': True,
            'surrSuff:w[i]': True,
            'w[i].isLessThres': True,
            'w[i].isdigit()': True,
            'surr:w[i].isdigit()': True,
            'w[i].isupper()': True,
            'surr:w[i].isupper()': True,
            'w[i].istitle()': True,
            'surr:w[i].istitle()': True,
            'w[i].isStartWord()': True,
            'w[i].isEndWord()': True,
            'pos:w[i]': True,
            'surrPos:w[i]': True,
        }
    ):
        # supervised ML from scikit-learn
        self.MODEL_CLF = model_clf
        self.FEATURE_ENCODING = feature_encoding
        self.TYPE_OF_BOOLEAN_FEATURES = [
            'isLessThres()',
            'isdigit()',
            'isupper()',
            'istitle()',
            'isStartWord()',
            'isEndWord()',
        ]
        self.POSTag = HiddenMarkovModelPOSTag()
        self.preprocessor = TextPreprocessor()

    @staticmethod
    def dataframe2sequential(data_df):
        Seqdata = list()

        satua_titles = set(list(data_df['StoryTitle'].values))
        for title in satua_titles:
            stories = data_df[
                data_df['StoryTitle'] == title
            ]
            # get the sentences ID in the stories
            stories_sentences_ids = set(list(stories['SentenceID'].values))
            for sentence_id in stories_sentences_ids:
                stories_group_by_sentence = stories[
                    stories['SentenceID'] == sentence_id
                ]
                sentence_list = list()
                for idx, row in stories_group_by_sentence.iterrows():
                    word = row['Word']
                    pos_tag = row['POS Tag']
                    ner_tag = row['Character Named Entity Tagset']
                    sentence_list.append((word, pos_tag, ner_tag))
                Seqdata.append(sentence_list)
        return Seqdata

    @staticmethod
    def sentence2features(sent, bit_encoding):
        """
        Function to extract features from a sentence based on activated bit_encoding

        Args:
            - sent: input sentence will be extracted
            - bit_encoding: encoding of any activated feature extraction

        Returns:
            list of dictionary of extracted features of each words in sent
        """
        sentence_length = len(sent)
        w2features = list()
        for index_word, values in enumerate(sent):
            # features untuk setiap w[i] pada sent
            features = dict()
            word = values[0]
            postag = values[1]

            # mapping procedure
            mapping = {
                'w[i]': {
                    'w[i]': word
                },
                'pref:w[i]': {
                    'pref:w[i][0:1]': word[0:1],
                    'pref:w[i][0:2]': word[0:2],
                    'pref:w[i][0:3]': word[0:3],
                },
                'suff:w[i]': {
                    'suff:w[i][-1:]': word[-1:],
                    'suff:w[i][-2:]': word[-2:],
                    'suff:w[i][-3:]': word[-3:],
                },
                'pos:w[i]': {
                    'pos:w[i]': postag
                },
                'w[i].lower()': {
                    'w[i].lower()': word.lower()
                },
                'w[i].isdigit()': {
                    'w[i].isdigit()': word.isdigit()
                },
                'w[i].isupper()': {
                    'w[i].isupper()': word.isupper()
                },
                'w[i].istitle()': {
                    'w[i].istitle()': word.istitle()
                },
                'w[i].isLessThres': {
                    'w[i].istitle()': True if len(word) < 5 else False
                },
                'surr:w[i]': dict(),
                'surr:w[i].lower()': dict(),
                'surrPreff:w[i]': dict(),
                'surrSuff:w[i]': dict(),
                'surr:w[i].isdigit()': dict(),
                'surr:w[i].isupper()': dict(),
                'surr:w[i].istitle()': dict(),
                'w[i].isStartWord()': dict(),
                'w[i].isEndWord()': dict(),
                'surrPos:w[i]': dict(),
            }
            if index_word > 0:
                # ambil 1 kata sebelumnya
                wordPrev1 = sent[index_word-1][0]
                posPrev1 = sent[index_word-1][1]
                mapping['surr:w[i]'].update({
                    'surr:w[i-1]': wordPrev1
                })
                mapping['surr:w[i].lower()'].update({
                    'surr:w[i-1].lower()': wordPrev1.lower()
                })
                mapping['surrPreff:w[i]'].update({
                    'surrPreff:w[i-1][0:1]': wordPrev1[0:1],
                    'surrPreff:w[i-1][0:2]': wordPrev1[0:2],
                    'surrPreff:w[i-1][0:3]': wordPrev1[0:3],
                })
                mapping['surrSuff:w[i]'].update({
                    'surrSuff:w[i-1][-1:]': wordPrev1[-1:],
                    'surrSuff:w[i-1][-2:]': wordPrev1[-2:],
                    'surrSuff:w[i-1][-3:]': wordPrev1[-3:],
                })
                mapping['surr:w[i].isdigit()'].update({
                    'surr:w[i-1].isdigit()': wordPrev1.isdigit()
                })
                mapping['surr:w[i].isupper()'].update({
                    'surr:w[i-1].isupper()': wordPrev1.isupper()
                })
                mapping['surr:w[i].istitle()'].update({
                    'surr:w[i-1].istitle()': wordPrev1.istitle()
                })
                mapping['w[i].isStartWord()'].update({
                    'w[i].isStartWord()': False
                })
                mapping['w[i].isEndWord()'].update({
                    'w[i].isEndWord()': False
                })
                mapping['surrPos:w[i]'].update({
                    'surrPos:w[i-1]': posPrev1
                })

            if index_word < sentence_length-1:
                # ambil 1 kata setelahnya
                wordNext1 = sent[index_word+1][0]
                posNext1 = sent[index_word+1][1]
                mapping['surr:w[i]'].update({
                    'surr:w[i+1]': wordNext1
                })
                mapping['surr:w[i].lower()'].update({
                    'surr:w[i+1].lower()': wordNext1.lower()
                })
                mapping['surrPreff:w[i]'].update({
                    'surrPreff:w[i+1][0:1]': wordNext1[0:1],
                    'surrPreff:w[i+1][0:2]': wordNext1[0:2],
                    'surrPreff:w[i+1][0:3]': wordNext1[0:3],
                })
                mapping['surrSuff:w[i]'].update({
                    'surrSuff:w[i+1][-1:]': wordNext1[-1:],
                    'surrSuff:w[i+1][-2:]': wordNext1[-2:],
                    'surrSuff:w[i+1][-3:]': wordNext1[-3:],
                })
                mapping['surr:w[i].isdigit()'].update({
                    'surr:w[i+1].isdigit()': wordNext1.isdigit()
                })
                mapping['surr:w[i].isupper()'].update({
                    'surr:w[i+1].isupper()': wordNext1.isupper()
                })
                mapping['surr:w[i].istitle()'].update({
                    'surr:w[i+1].istitle()': wordNext1.istitle()
                })
                mapping['w[i].isStartWord()'].update({
                    'w[i].isStartWord()': False
                })
                mapping['w[i].isEndWord()'].update({
                    'w[i].isEndWord()': False
                })
                mapping['surrPos:w[i]'].update({
                    'surrPos:w[i+1]': posNext1
                })

            if index_word == 0 or index_word == sentence_length:
                mapping['w[i].isStartWord()'].update({
                    'w[i].isStartWord()': True
                })
                mapping['w[i].isEndWord()'].update({
                    'w[i].isEndWord()': False
                })
                if index_word == sentence_length:
                    mapping['w[i].isStartWord()'].update({
                        'w[i].isStartWord()': False
                    })
                    mapping['w[i].isEndWord()'].update({
                        'w[i].isEndWord()': True
                    })

            for key, isActive in bit_encoding.items():
                if isActive is True:
                    features.update(mapping[key])
            w2features.append(features)

        return w2features

    @staticmethod
    def sentence2labels(sent):
        return [label for token, postag, label in sent]

    @staticmethod
    def sentence2tokens(sent):
        return [token for token, postag, label in sent]

    @staticmethod
    def token_with_predicted_tags(token_sentence, y_pred):
        token_with_predicted_tag = list()
        for idx_token, token in enumerate(token_sentence):
            token_with_predicted_tag.append(
                str(token) + "/" + str(y_pred[idx_token]))
        return token_with_predicted_tag

    @staticmethod
    def extract_predicted_characters_from_sentence(sentence, y_pred):
        """
        <Description>
        Module untuk mengekstrak daftar karakter dari kalimat yang sudah diprediksi model
        """
        token_sentence = sentence.split(' ')
        list_of_characters_from_example_kalimat = list()
        counter_list_of_characters = -1
        for idx_word, word in enumerate(token_sentence):
            split_ner_tags = y_pred[idx_word].split('-')
            if split_ner_tags[0] == 'B':
                list_of_characters_from_example_kalimat.append(word)
                counter_list_of_characters += 1
            elif split_ner_tags[0] == 'I':
                if counter_list_of_characters == -1:
                    list_of_characters_from_example_kalimat.append(word)
                    counter_list_of_characters += 1
                else:
                    list_of_characters_from_example_kalimat[counter_list_of_characters] = list_of_characters_from_example_kalimat[
                        counter_list_of_characters] + " " + word
            elif split_ner_tags[0] == 'O':
                continue

        # return value
        n_predicted_chars = len(list_of_characters_from_example_kalimat)
        context = {
            'n_predicted_chars': n_predicted_chars,
            'predicted_chars': '; '.join(list_of_characters_from_example_kalimat) if n_predicted_chars != 0 else np.nan
        }
        return context

    @staticmethod
    def identify_characters(preprocessed_story, pretrained_model):
        """
        Function to identify all character named entities present in a given story
        <Parameters>:
        - preprocessed_story: <string>
            --> a string of Balinese story text. You can pass a preprocessed text here.
        - pretrained_model: <pickle object>
            --> pass our one of our loaded pretrained model here.
        <Output>:
        - List of identified characters by the provided pretrained models 
        """
        # Split the story into list of sentences
        preprocessed_story = preprocessed_story.split("\\n")
        preprocessed_story.pop()  # pop empty string

        # identify the character entities from each sentence
        predicted_characters = set()
        for sentence in preprocessed_story:
            sentence = sentence.strip()
            y_pred, token_with_predicted_chars = pretrained_model.predict_sentence(
                sentence)
            results = pretrained_model.extract_predicted_characters_from_sentence(
                sentence, y_pred)
            results_predicted_chars = results['predicted_chars']
            if results_predicted_chars is not np.nan and results_predicted_chars != "":
                for pred_char in results_predicted_chars.split(';'):
                    predicted_characters.add(pred_char.strip())

        return list(predicted_characters)

    def _prepare_input_sentence(self, sentence):
        # pos tagging
        sentence_with_postag = self.POSTag.predict(sentence)

        # word tokenize sentence_with_postag ()
        token_sentence = sentence_with_postag.strip().split(' ')

        # buat sequential data
        seq_data = list()
        for token in token_sentence:
            pos = token.split('/')[1]
            seq_data.append((token, pos))

        # ekstraksi fitur
        X_features = [
            self.sentence2features(seq_data, self.FEATURE_ENCODING)
        ]
        return token_sentence, X_features

    def evaluate(self, y_train, y_pred_train, y_test, y_pred_test, average_metric='weighted'):
        # flatten process
        if (type(y_pred_train) is np.ndarray) or (type(y_pred_test) is np.ndarray):
            y_train = y_train.flatten()
            y_pred_train = y_pred_train.flatten()
            y_test = y_test.flatten()
            y_pred_test = y_pred_test.flatten()
        elif (type(y_pred_train) is list) or (type(y_pred_test) is list):
            y_train = flatten(y_train)
            y_pred_train = flatten(y_pred_train)
            y_test = flatten(y_test)
            y_pred_test = flatten(y_pred_test)

        self.test_evaluation = {
            'accuracy': accuracy_score(y_test, y_pred_test),
            'recall': recall_score(y_test, y_pred_test, average=average_metric, zero_division=0),
            'precision': precision_score(y_test, y_pred_test, average=average_metric, zero_division=0),
            'f1_score': f1_score(y_test, y_pred_test, average=average_metric, zero_division=0)
        }
        self.train_evaluation = {
            'accuracy': accuracy_score(y_train, y_pred_train),
            'recall': recall_score(y_train, y_pred_train, average=average_metric, zero_division=0),
            'precision': precision_score(y_train, y_pred_train, average=average_metric, zero_division=0),
            'f1_score': f1_score(y_train, y_pred_train, average=average_metric, zero_division=0)
        }
        return self.train_evaluation, self.test_evaluation

    def classification_report(self, y_train, y_pred_train, y_test, y_pred_test, print_train=True, relax_match=False, target_names=None):
        # flatten process
        if (type(y_pred_train) is np.ndarray) or (type(y_pred_test) is np.ndarray):
            y_train = y_train.flatten()
            y_pred_train = y_pred_train.flatten()
            y_test = y_test.flatten()
            y_pred_test = y_pred_test.flatten()
        elif (type(y_pred_train) is list) or (type(y_pred_test) is list):
            y_train = flatten(y_train)
            y_pred_train = flatten(y_pred_train)
            y_test = flatten(y_test)
            y_pred_test = flatten(y_pred_test)

        if relax_match:
            y_train = np.array(pd.Series(y_train).apply(lambda x: x.split(
                '-')[0] if len(x.split('-')) == 1 else x.split('-')[1]))
            y_pred_train = np.array(pd.Series(y_pred_train).apply(
                lambda x: x.split('-')[0] if len(x.split('-')) == 1 else x.split('-')[1]))
            y_test = np.array(pd.Series(y_test).apply(lambda x: x.split(
                '-')[0] if len(x.split('-')) == 1 else x.split('-')[1]))
            y_pred_test = np.array(pd.Series(y_pred_test).apply(
                lambda x: x.split('-')[0] if len(x.split('-')) == 1 else x.split('-')[1]))

        if print_train:
            print('='*50)
            print('CLASSIFICATION REPORT FOR TRAINING DATA\n')
            print(classification_report(y_train, y_pred_train,
                  digits=4, target_names=target_names))
            print('='*50)
        print('='*50)
        print('CLASSIFICATION REPORT FOR TESTING DATA\n')
        print(classification_report(y_test, y_pred_test,
              digits=4, target_names=target_names))
        print('='*50)

    def save(self, saved_model, path_to_save, filename):
        """
        Function to save the pretrained model and others data in pickle format (.pkl)

        Args:
            - saved_model: dictionary contain data that will be saved, including 'model' key that
            - path_to_save: path directory for saving the model
            - filename: filename with .pkl suffix

        Returns: None
        """
        pickle.dump(saved_model, open(path_to_save+filename, 'wb'))
