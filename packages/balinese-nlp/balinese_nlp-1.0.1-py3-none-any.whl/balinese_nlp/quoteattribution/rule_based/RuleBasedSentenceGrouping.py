from balinese_nlp.corefresolution.rule_based import CoreferenceResolution
from numpy import nan
from pandas import DataFrame
import os

class RuleBasedSentenceGrouping:
    def __init__(self,
                 use_coreference_resolution=False,
                 add_characterization_column=True,
                 path_saved_file="saved_file",
                 filename="eg_sentence_grouping.xlsx",
                 ):
        """
        <Description>
        Module untuk melakukan pengelompokkan kalimat berdasarkan hasil alias cluster yang diinputkan

        <Input>
        - use_coreference_resolution: <Bool>
            -> Menggunakan coreference resolution pada kalimat ketika bernilai True
        - add_characterization_column: <Bool>
            -> Menambahkan kolom characterization dari setiap kelompok tokoh pada dataframe dengan initial nilai NaN
        - path_saved_file: <Str>
            -> folder tempat menyimpan file hasil sentence grouping by default
        - filename: <Str>
            -> Nama file untuk penyimpanan
        """
        self.coreference_model = None
        self.use_coreference_resolution = use_coreference_resolution
        self.data_extracted_sentence = {
            'CharactersID': list(),
            'AliasCharacters': list(),
            'GroupedSentences': list(),
        }
        self.filename = filename
        self.path_saved_file = self.__create_saved_folder(path_saved_file)
        self.add_characterization_column = add_characterization_column
    

    def fit(self, sentences, characters_alias_clustering, characters_characterization=None):
        """
        <Description>
        Module untuk memasukkan data-data input yang diperlukan untuk proses sentence grouping

        <Input>
        - sentences: <List>
            -> List of sentences pada setiap satua
        - characters_alias_clustering: <Dictionary>
            -> Kamus pasangan key, value antara key tokoh dengan semua kombinasi nama alias tokoh tersebut dalam list
        - characters_characterization: <List>
            -> Watak dari setiap key tokoh yang dimasukkan sebelumnya
        """
        # set init variables with user params input
        self.sentences = sentences
        self.characters_alias_clustering = characters_alias_clustering

        # check if user use the characterization column but passing the value not equal with amount of characters alias clustering
        if self.add_characterization_column:
            if characters_characterization is None:
                raise ValueError(
                    "List tidak boleh kosong kalau ingin menambahkan kolom characterization!")
            if len(characters_characterization) != len(characters_alias_clustering.keys()):
                raise KeyError(
                    'Jumlah watak yang dimasukkan tidak sama dengan yang ada pada alias clustering')
            self.data_extracted_sentence.update({
                'characterization': characters_characterization
            })

        # check if user use coreference resolution steps
        if self.use_coreference_resolution:
            self.coreference_model = CoreferenceResolution().fit(self.sentences)
            self.sentences = self.coreference_model.predict()

        return self

    def predict(self):
        """
        <Description>
        Module to group sentence based on group of detected characters
        """
        # processes
        for key, characters_alias in self.characters_alias_clustering.items():
            # cari kalimat-kalimat yang mengandung entitas tokoh dari alias clustering
            list_of_sentence_from_characters = list()
            for idx_char, character in enumerate(characters_alias):
                for sentence in self.sentences:
                    # cek apakah setiap kalimat mengandung enetitas tokoh
                    if sentence.lower().find(character.lower()) != -1:
                        # check data duplikat
                        if sentence not in list_of_sentence_from_characters:
                            list_of_sentence_from_characters.append(sentence)
            # append extracted information into dataframe
            self.data_extracted_sentence['CharactersID'].append(key)
            self.data_extracted_sentence['AliasCharacters'].append(
                ", ".join(characters_alias))
            self.data_extracted_sentence['GroupedSentences'].append(
                ' '.join(list_of_sentence_from_characters))

        # convert sentence grouping dictionary results into DataFrame format
        self.df_data_extracted_sentence = DataFrame(
            self.data_extracted_sentence)

        return self.df_data_extracted_sentence

    def save(self, format='xlsx'):
        """
        Modul untuk menyimpan hasil sentence grouping 
        """
        if self.filename is None:
            raise Exception("Please input your filename and format!")
        else:
            if format == "xlsx":
                self.df_data_extracted_sentence.to_excel(
                    self.path_saved_file+self.filename, index=False)
                print("{} was successfully saved in {}".format(
                    self.filename, self.path_saved_file))

    def __create_saved_folder(self, path_saved_file):
        """Function for creating saved folder to store sentence grouping results by default

        Args:
            path_saved_file (str): default folder
        """
        ROOT_PATH_FOLDER = os.path.dirname(os.getcwd())
        full_path = os.path.join(ROOT_PATH_FOLDER, path_saved_file)
        try:
            os.makedirs(full_path, exist_ok=True)
            print(f"Direktori '{full_path}' berhasil dibuat (atau sudah ada).")
            return full_path
        except OSError as e:
            # Menangkap error lain selain direktori sudah ada
            print(f"Terjadi kesalahan saat membuat direktori '{full_path}': {e}")
