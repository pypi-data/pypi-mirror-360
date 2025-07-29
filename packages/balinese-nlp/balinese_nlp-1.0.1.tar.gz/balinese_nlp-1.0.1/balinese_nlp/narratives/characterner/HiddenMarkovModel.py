import numpy as np
from hmmlearn import hmm
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
import pandas as pd
from .BaseModel import BaseModel


class HiddenMarkovModel(BaseModel):
    def __init__(self, algorithm='viterbi', random_state=42, n_iter=100, train_sampling_percentage=0.01):
        BaseModel.__init__(self)
        self.hmm = {
            'params_config': {
                'algorithm': algorithm,
                'random_state': random_state,
                'n_iter': n_iter
            }
        }
        self.train_sampling_percentage = train_sampling_percentage

    def fit(self, data_train):
        self.data_train = self.__preprocessing_data_input(data_train)
        self.Y_TRAIN = list(self.data_train['Character Named Entity Tagset'].values)
        self.__sampling_data_train()
        self.__get_training_attributes()
        self.__prepare_hmm_components()
        self.__calculate_hmm_components()
        self.__fit_hmm()

        return self

    def __preprocessing_data_input(self, data):
        # lower case 'Word' column
        data['Word'] = data['Word'].str.lower()
        return data

    def __sampling_data_train(self):
        # sediakan token <UNK> pada data training untuk mengantisipasi kata yang tidak dikenali pada data testing
        # kata-kata yang tidak dikenali akan menggunakan emission probability setiap state dari token <UNK>
        # sampling sebesar 1% dari data training untuk mengatasi unknown token
        dfupdate = self.data_train.sample(
            frac=self.train_sampling_percentage,
            replace=False,
            random_state=42
        )
        dfupdate.Word = '<UNK>'
        self.data_train.update(dfupdate)
        return self

    def __get_training_attributes(self):
        # save training attributes
        self.training_attributes = {
            'words': list(set(self.data_train['Word'].values)),
            'ner_tag': list(set(self.data_train['Character Named Entity Tagset'].values)),
        }
        self.training_attributes.update({
            'word2id': {w: i for i, w in enumerate(self.training_attributes['words'])},
            'tag2id': {t: i for i, t in enumerate(self.training_attributes['ner_tag'])},
            'id2tag': {i: t for i, t in enumerate(self.training_attributes['ner_tag'])},
        })
        return self

    def __prepare_hmm_components(self):
        """
        <Description>
        Module untuk menyiapkan komponen yang digunakan dalam perhitungan HMM
        - A (transition probability matrix)
        - B (emission probability matrix)
        - phi (initial probability distribution)
        """
        tags = self.training_attributes['ner_tag']
        # prepare HMM Params
        self.params_hmm = dict()
        self.params_hmm['count_tags'] = dict(
            self.data_train['Character Named Entity Tagset'].value_counts())

        # siapkan komponen A (transition probability matrix)
        # hitung ada berapa banyak kemunculan pasangan[q(i), q(i+1)]
        columns = [None] * len(tags)
        index = [None] * len(tags)
        count_tags_to_next_tags = np.zeros((len(tags), len(tags)), dtype=int)
        sentences = list(self.data_train['SentenceID'])
        pos = list(self.data_train['Character Named Entity Tagset'])
        for i in range(len(sentences)):
            if (i > 0) and (sentences[i] == sentences[i - 1]):
                prevtagid = self.training_attributes['tag2id'][pos[i - 1]]
                nexttagid = self.training_attributes['tag2id'][pos[i]]
                # increment 1 setiap kemunculan kombinasi tersebut
                count_tags_to_next_tags[prevtagid][nexttagid] += 1
                # simpan nama tag dari previous dan next tag untuk dataframe visualisasi
                columns[prevtagid] = pos[i - 1]
                index[nexttagid] = pos[i]
        self.params_hmm['count_tags_to_next_tags'] = count_tags_to_next_tags

        # siapkan komponen B (Emission probability matrix)
        # yaitu jumlah kemunculan dari pasangan hidden state dengan setiap observation pada data training
        count_tags_to_words = self.data_train.groupby(['Character Named Entity Tagset']).apply(
            lambda grp: grp.groupby('Word')['Character Named Entity Tagset'].count().to_dict()).to_dict()
        self.params_hmm['count_tags_to_words'] = count_tags_to_words

        # siapkan komponen phi (initial propbability distribution)
        # hitung pada saat t=1 (awal kalimat) paling sering muncul hidden state mana dan berapa banyak
        count_init_tags = dict(self.data_train.groupby(
            ['SentenceID']).first()['Character Named Entity Tagset'].value_counts())
        self.params_hmm['count_init_tags'] = count_init_tags

        return self

    def __calculate_hmm_components(self):
        """
        <Description>
        Module untuk menghitung komponen HMM yang sudah disiapkan
        """
        tags = self.training_attributes['ner_tag']
        words = self.training_attributes['words']
        count_tags_to_next_tags = self.params_hmm['count_tags_to_next_tags']
        count_init_tags = self.params_hmm['count_init_tags']
        count_tags_to_words = self.params_hmm['count_tags_to_words']
        count_tags = self.params_hmm['count_tags']
        tag2id = self.training_attributes['tag2id']
        word2id = self.training_attributes['word2id']

        # calculate A, B, phi
        # siapkan matriks A,B dan vektor baris phi
        self.mystartprob = np.zeros((len(tags),))
        self.mytransmat = np.zeros((len(tags), len(tags)))
        self.myemissionprob = np.zeros((len(tags), len(words)))

        # jumlahkan secara vertikal dari komponen A
        sum_tags_to_next_tags = np.sum(count_tags_to_next_tags, axis=1)

        # jumlahkan semua kemungkinan dari kemunculan setiap tag pada awal kalimat (digunakan untuk perhitungan phi)
        num_sentences = sum(count_init_tags.values())

        index_phi = [None] * len(tags)
        columns_emission = [None] * len(words)

        # hitung komponen A,B,phi
        for tag, tagid in tag2id.items():
            index_phi[tagid] = tag

            # hitung phi
            self.mystartprob[tagid] = count_init_tags.get(
                tag, 0) / num_sentences

            # hitung A
            for tag2, tagid2 in tag2id.items():
                self.mytransmat[tagid][tagid2] = count_tags_to_next_tags[tagid][tagid2] / \
                    sum_tags_to_next_tags[tagid]

            # hitung B
            for word, wordid in word2id.items():
                columns_emission[wordid] = word
                self.myemissionprob[tagid][wordid] = count_tags_to_words.get(
                    tag, {}).get(word, 0) / float(count_tags.get(tag, 0))

        return self

    def __fit_hmm(self):
        """
        <Description>
        Module untuk mengeset model HMM dengan komponen-komponen yang sudah dihitung
        """
        tags = self.training_attributes['ner_tag']

        # dengan menggunakan package HMM, set nilai A,B,phi dari yang sudah dihitung serta atur Viterbi untuk menggunakan algoritma viterbi
        model = hmm.CategoricalHMM(
            n_components=len(tags),
            algorithm=self.hmm['params_config']['algorithm'],
            random_state=self.hmm['params_config']['random_state'],
            n_iter=self.hmm['params_config']['n_iter']
        )
        model.startprob_ = self.mystartprob
        model.transmat_ = self.mytransmat
        model.emissionprob_ = self.myemissionprob
        self.hmm.update({
            'initial_probability_distribution': self.mystartprob,
            'transition_probability_matrix': self.mytransmat,
            'emission_probability_matrix': self.myemissionprob,
            'model': model
        })
        return self

    def predict(self, data_test):
        """
        <Description>
        Module untuk memprediksi NER tag dari data test
        """
        self.data_test = self.__preprocessing_data_input(data_test)
        self.Y_TEST = list(self.data_test['Character Named Entity Tagset'].values)

        # prepare data input for training and testing
        X_train, length_X_train = self.__prepare_data_input(self.data_train)
        X_test, length_X_test = self.__prepare_data_input(data_test)

        # predict
        self.y_pred_train = self.hmm['model'].predict(X_train, length_X_train)
        self.y_pred_test = self.hmm['model'].predict(X_test, length_X_test)

        return self.y_pred_test

    def __prepare_data_input(self, data):
        """
        <Description>
        Module untuk mempersiapkan dataframe dalam format yang sesuai sebelum diprediksi oleh model
        """
        # ganti semua kata pada data X_words yang tidak dikenali pada data training dengan <UNK>
        words = self.training_attributes['words']
        word2id = self.training_attributes['word2id']
        data.loc[~data['Word'].isin(words), 'Word'] = '<UNK>'
        word_test = list(data['Word'])
        X_test = []

        # input data test berupa id dari word
        for i, val in enumerate(word_test):
            X_test.append([word2id[val]])

        # hitung panjang segment kata untuk setiap kalimat testing
        length_X_test = []
        count = 0
        sentences = list(data['SentenceID'])
        for i in range(len(sentences)):
            if (i > 0):
                if (sentences[i] == sentences[i - 1]):
                    count += 1
                else:
                    length_X_test.append(count)
                    count = 1
            else:
                count = 1

            if (i == len(sentences)-1):
                length_X_test.append(count)

        return X_test, length_X_test

    def predict_sentence(self, X_sentence):
        """
        <Description>
        Module untuk memprediksi label NER dari kalimat yang dimasukkan
        """
        # get initial data from class
        word2id = self.training_attributes['word2id']
        id2tag = self.training_attributes['id2tag']

        # convert word to id format
        X_sentence = X_sentence.lower()
        token_sentence = X_sentence.split(' ')
        samples_test = []
        for i, val in enumerate(token_sentence):
            try:
                samples_test.append([word2id[val]])
            except:
                samples_test.append([word2id['<UNK>']])

        # predict using pretrained
        y_pred = self.hmm['model'].predict(samples_test, len(samples_test))
        y_pred_tag = [id2tag[y] for y in y_pred]

        # print token with predicted tag
        token_with_predicted_tag = self.token_with_predicted_tags(
            token_sentence, y_pred_tag)

        return y_pred_tag, token_with_predicted_tag

    def evaluate(self, y_train, y_pred_train, y_test, y_pred_test, average_metric='weighted'):
        """
        <Description>
        Module untuk menghasilkan evaluasi terhadap data train dan data test
        """
        # get initial data
        tag2id = self.training_attributes['tag2id']

        # evaluate on train data
        y_train_id = np.zeros((len(y_train), ), dtype=int)
        for i, val in enumerate(y_train):
            y_train_id[i] = tag2id[val]
        min_length_train = min(len(y_train_id), len(y_pred_train))
        self.train_evaluation = {
            'accuracy': accuracy_score(
                y_train_id[:min_length_train], y_pred_train[:min_length_train]),
            'recall': recall_score(
                y_train_id[:min_length_train], y_pred_train[:min_length_train], average=average_metric),
            'precision': precision_score(
                y_train_id[:min_length_train], y_pred_train[:min_length_train], average=average_metric),
            'f1_score': f1_score(
                y_train_id[:min_length_train], y_pred_train[:min_length_train], average=average_metric)
        }

        # evaluate on test data
        y_test_id = np.zeros((len(y_test), ), dtype=int)
        for i, val in enumerate(y_test):
            y_test_id[i] = tag2id[val]
        min_length_test = min(len(y_test_id), len(y_pred_test))
        self.test_evaluation = {
            'accuracy': accuracy_score(
                y_test_id[:min_length_test], y_pred_test[:min_length_test]),
            'recall': recall_score(
                y_test_id[:min_length_test], y_pred_test[:min_length_test], average=average_metric),
            'precision': precision_score(
                y_test_id[:min_length_test], y_pred_test[:min_length_test], average=average_metric),
            'f1_score': f1_score(
                y_test_id[:min_length_test], y_pred_test[:min_length_test], average=average_metric)
        }
        return self.train_evaluation, self.test_evaluation

    def classification_report(self, y_train, y_pred_train, y_test, y_pred_test, print_train=True, relax_match=False):

        # get initial data
        id2tag = self.training_attributes['id2tag']

        # classification report for train data
        y_pred_train_tag = list()
        for idx, val in enumerate(y_pred_train):
            y_pred_train_tag.append(id2tag[int(val)])
        minimum_length_train = min(len(y_train), len(y_pred_train_tag))
        y_train = y_train[:minimum_length_train]
        y_pred_train = y_pred_train_tag[:minimum_length_train]

        # classification report for test data
        y_pred_test_tag = list()
        for idx, val in enumerate(y_pred_test):
            y_pred_test_tag.append(id2tag[int(val)])
        minimum_length_test = min(len(y_test), len(y_pred_test_tag))
        y_test = y_test[:minimum_length_test]
        y_pred_test = y_pred_test_tag[:minimum_length_test]

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
            print(classification_report(y_train, y_pred_train, digits=4))
            print('='*50)
        print('='*50)
        print('CLASSIFICATION REPORT FOR TESTING DATA\n')
        print(classification_report(y_test, y_pred_test, digits=4))
        print('='*50)
