from .LinkedList import LinkedList
import pickle
import os
from numpy import nan
import sys
ROOT_PATH_FOLDER = os.path.dirname(os.getcwd())

# register our package BalineseNER here
sys.path.append(ROOT_PATH_FOLDER+"\\packages\\")

class CoreferenceResolution:
    def __init__(
            self, 
            characters_identification_pretrained_model='satuaner'
    ):
        """
        <Parameters>:
        - characters_identification_pretrained_model: Predefined character identification model provided by users or you can use our pretrained character identification models.
            --> Options: 'satuaner', 'svm', 'hmm', 'crf'
            --> Default: 'satuaner'
        """
        ROOT_PATH_PRETRAINED_FOLDER = ROOT_PATH_FOLDER+"\\pretrained-models\\character-identification"
        if type(characters_identification_pretrained_model) is str:
            if characters_identification_pretrained_model == "satuaner":
                characters_identification_pretrained_model = pickle.load(
                    open(ROOT_PATH_PRETRAINED_FOLDER+"\\SatuaNER\\pretrained_best_model.pkl", 'rb')
                )['optimal_best_all_train_model']
            elif characters_identification_pretrained_model == "svm":
                characters_identification_pretrained_model = pickle.load(
                    open(ROOT_PATH_PRETRAINED_FOLDER+"\\SVM\\pretrained_best_model.pkl", 'rb')
                )['optimal_best_all_train_model']
            elif characters_identification_pretrained_model == "hmm":
                characters_identification_pretrained_model = pickle.load(
                    open(ROOT_PATH_PRETRAINED_FOLDER+"\\HMM\\pretrained_best_model.pkl", 'rb')
                )['optimal_best_all_train_model']
            elif characters_identification_pretrained_model == "crf":
                characters_identification_pretrained_model = pickle.load(
                    open(ROOT_PATH_PRETRAINED_FOLDER+"\\CRF-2\\pretrained_best_model.pkl", 'rb')
                )['optimal_best_all_train_model']
        
        self.linkedlist = LinkedList(
            chars_identification_pretrained_model=characters_identification_pretrained_model
        )

    def fit(self, sentences):
        """
        Module untuk memfit sekumpulan kalimat sebelum diproses dengan rule based coreference resolution
        """
        # get initial data from init
        linkedlist = self.linkedlist

        # 1. Initialization: add semua sentence sebagai node baru di linked list
        for sentence in sentences:
            linkedlist.addLast(sentence)

        return self

    def predict(self):
        """
        <Description>
        Module untuk proses coreference resolution dengan rule based
        """
        # get current linkedlist with fitted data
        linkedlist = self.get_linked_list()

        # processes
        current_node_chars = linkedlist.getFirstNode()
        # initialize counter node with the first (head) node
        counter = linkedlist.getFirstNode()
        while (counter is not None):

            # (1) Jika pada kalimat ke-i ada CHAR NE dan pronomina ketiga,
            # maka ganti pronomina ketiga tersebut dengan CHAR NE yang terdeteksi pertama
            if counter.predicted_chars is not nan:
                current_node_chars = counter
                if counter.is_pronomina_exists:
                    if counter.is_detected_chars:
                        # ganti semua pronomina ia pada token sentence dengan counter predicted char
                        counter.replace_pronomina(
                            replace_with=counter.predicted_chars[0])

            # (2) Jika pada kalimat ke-i ada CHAR NE dan tidak ada pronomina ketiga,
            # maka pronomina ketiga pada kalimat ke (i+1), ke (i+2) dst sampai ditemukan kembali CHAR NE diganti dengan CHAR NE pada kalimat ke (i) pertama
            temp = counter.next
            # selama temp bukan di akhir node (None), maka ganti semua pronomina pada temp sampai ditemukan kembali char NE di kalimat itu
            while (temp is not linkedlist.getLastNode().next):
                if (temp.is_pronomina_exists):
                    if temp.predicted_chars is not nan:
                        break
                    else:
                        if current_node_chars.is_detected_chars:
                            temp.replace_pronomina(
                                current_node_chars.predicted_chars[0])
                temp = temp.next

            # move counter pointer into temp pointer
            counter = temp

        return linkedlist.return_sentences()

    def get_linked_list(self):
        return self.linkedlist
