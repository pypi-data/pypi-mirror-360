from numpy import nan, array, where
import pickle
from copy import deepcopy


class Node:
    def __init__(self, sentence, characters_identification_pretrained_model=None, next=None, before=None):
        # node properties
        self.pronomina_bali = ['ia', 'ida', 'iya', 'dane', 'cai', 'nyai']
        self.sentence = str(sentence)
        self.__tokenize_sentence()
        self.characters_detection_pretrained_model = characters_identification_pretrained_model
        self.predicted_chars = self.__predict_characters()
        self.is_detected_chars = self.__detect_characters()
        self.is_pronomina_exists, self.pronomina_exists = self.__check_pronomina_exists()
        # di akhir proses, delete semua pretrained model yang diload supaya hemat memori
        del self.characters_detection_pretrained_model

        # double linkedlist properties
        self.next = next
        self.before = before

    def __tokenize_sentence(self):
        self.token_sentence = self.sentence.split(' ')
        self.lower_token_sentence = [token.lower()
                                     for token in self.token_sentence]

    def __predict_characters(self):
        """
        Method untuk memprediksi daftar karakter dari kalimat saat ini
        """
        sentence = self.sentence
        y_pred, token_with_predicted_tags = self.characters_detection_pretrained_model.predict_sentence(
            sentence)
        results = self.characters_detection_pretrained_model.extract_predicted_characters_from_sentence(
            sentence, y_pred)
        predicted_chars = nan
        if results['predicted_chars'] is not nan:
            predicted_chars = [tokoh.strip()
                               for tokoh in results['predicted_chars'].split(';')]
        return predicted_chars

    def __detect_characters(self):
        is_any_chars_detected = True
        if self.predicted_chars is nan:
            is_any_chars_detected = False
        return is_any_chars_detected

    def __check_pronomina_exists(self):
        """
        Method untuk mengecek apakah daftar pronomina (yang telah ditentukan) exists di kalimat

        <Default>
        - pronomina: ['ida', 'ia', 'iya']

        <Deskripsi>
        - pronomina 'ida' hanya dideteksi ada jika predicted chars tidak ada yang mengandung kata 'ida'
        """

        # replace substring predicted chars pada node ini dengan ""
        cleaned_sentence = deepcopy(self.sentence)
        if self.predicted_chars is not nan:
            for pred_char in self.predicted_chars:
                cleaned_sentence = cleaned_sentence.replace(
                    pred_char, "").strip()

        # tokenize cleaned sentence
        tokenized_cleaned_sentence = [token.lower()
                                      for token in cleaned_sentence.split(' ')]

        # check if the pronomina exists in clean token
        list_pronomina_exists = list()
        for pronomina in self.pronomina_bali:
            if pronomina in tokenized_cleaned_sentence:
                list_pronomina_exists.append(pronomina)

        is_pronomina_exists = False
        if len(list_pronomina_exists) > 0:
            is_pronomina_exists = True

        return is_pronomina_exists, list_pronomina_exists

    def replace_pronomina(self, replace_with):
        """
        Method untuk mengganti semua pronomina bali yang terdapat pada suatu kalimat dengan nilai pada variabel replace with

        <Input>
        - replace_with: string untuk mengganti pronomina 

        <Process>
        1. Replace semua substring 

        <Output>
        - sentence: kalimat yang pronominanya sudah diganti dengan replace_with
        """
        # get initial data from class
        sentence = self.sentence.lower()
        predicted_chars = self.predicted_chars
        pronomina_bali = self.pronomina_bali

        # process
        # - ganti semua substring tokoh yang terdeteksi pada kalimat ini agar tidak terdeteksi substring 'ida' nantinya
        if self.is_detected_chars:
            for index, value in enumerate(predicted_chars):
                sentence = sentence.replace(
                    value.lower(), "[{}]".format(index))

        # - tokenize sentence yang substring tokohnya sudah diganti dengan key sementara
        token_sentence = array([token.strip()
                               for token in sentence.split(' ')])

        # - untuk semua pronomina bali, ganti pronomina dengan nilai pada variabel replace with setelah sentence direplace
        for pronomina in pronomina_bali:
            token_sentence = where(
                token_sentence == pronomina, replace_with, token_sentence)

        # - convert tokenize sentence back into sentence
        sentence = " ".join(token_sentence)

        # - kembalikan semua substring tokoh yang direplace di awal
        if self.is_detected_chars:
            for index, value in enumerate(predicted_chars):
                sentence = sentence.replace("[{}]".format(index), value)

        # perbarui init variabel dengan nilai terbaru hasil proses replace pronomina
        self.sentence = sentence
        self.__tokenize_sentence()


class LinkedList:
    def __init__(self, chars_identification_pretrained_model):
        self.head = None
        self.tail = None
        self.size = 0
        self.chars_identification_pretrained_model = chars_identification_pretrained_model

    # memeriksa list apakah kosong
    def isEmpty(self):
        return self.size == 0

    # menambah node pada posisi pertama
    def addFirst(self, sentence):
        newnode = Node(
            sentence,
            characters_identification_pretrained_model=self.chars_identification_pretrained_model
        )
        if not self.isEmpty():
            newnode.next = self.head
            newnode.before = None
            self.head.before = newnode
            self.head = newnode
            self.size += 1
        else:
            # head menunjuk ke new node
            self.head = newnode
            self.tail = self.head
            self.size += 1

    # get first node
    def getFirstNode(self):
        return self.head

    # get first sentence
    def getFirstSentence(self):
        if self.isEmpty():
            return None
        else:
            return self.head.sentence

    # update first sentence
    def updateFirstSentence(self, sentence):
        if not self.isEmpty():
            # pindahkan posisi head ke node setelahnya
            temp = self.head
            self.head = self.head.next
            self.head.before = None
            del temp
            self.size -= 1

            # arahkan head ke node baru
            newnode = Node(
                sentence,
                characters_identification_pretrained_model=self.chars_identification_pretrained_model
            )
            newnode.next = self.head
            self.head.before = newnode
            self.head = newnode
        else:
            return None

    # menambah node pada posisi terakhir
    def addLast(self, sentence):
        new_node = Node(
            sentence,
            characters_identification_pretrained_model=self.chars_identification_pretrained_model
        )
        if not self.isEmpty():
            new_node.next = None
            new_node.before = self.tail
            self.tail.next = new_node
            self.tail = new_node
            self.size += 1
        else:
            self.addFirst(sentence)

    # get last node
    def getLastNode(self):
        return self.tail

    # get last sentence
    def getLastSentence(self):
        if self.isEmpty():
            return None
        else:
            return self.tail.sentence

    # update last sentence
    def updateLastSentence(self, sentence):
        if not self.isEmpty():
            # pindahkan posisi tail ke node sebelumnya
            temp = self.tail
            self.tail = self.tail.before
            self.tail.next = None
            del temp
            self.size -= 1

            # arahkan tail ke node baru
            newnode = Node(
                sentence,
                characters_identification_pretrained_model=self.chars_identification_pretrained_model
            )
            newnode.before = self.tail
            self.tail.next = newnode
            self.tail = newnode
        else:
            return None

    # menampilkan semua sentence pada simpul node
    def return_sentences(self):
        list_of_sentences = list()
        current = self.head
        while (current is not None):
            list_of_sentences.append(current.sentence)
            current = current.next
        return list_of_sentences
