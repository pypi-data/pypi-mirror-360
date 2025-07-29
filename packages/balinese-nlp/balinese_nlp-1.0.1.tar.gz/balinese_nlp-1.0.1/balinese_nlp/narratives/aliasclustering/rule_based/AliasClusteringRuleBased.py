import numpy as np
import re

# jaccard similarity
from nltk.metrics import jaccard_distance


from .PairwiseDistanceString import PairwiseDistanceString


class AliasClusteringRuleBased(PairwiseDistanceString):
    def __init__(self, pairwise_distance='ratcliff', avg_threshold_similarity=0.85):
        """
        <Parameters>
        - pairwise_distance
            - Algoritma yang digunakan dalam perhitungan pairwise distance string similarity
            - Option: 'ratcliff', 'jaccard', 'sorensen-dice', 'jaro-distance', 'jaro-winkler'
            - Default: 'ratcliff'
                - 'ratcliff': Calculate using Ratcliff-Obershelp algorithm from difflib.SequenceMatcher
                - 'jaccard': Calculate using Jaccard similarity formula
                - 'sorensen-dice': Calculate using Sorensen-dice similarity formula
                - 'jaro-distance': Jaro Similarity is the measure of similarity between two strings. The value of Jaro distance ranges from 0 to 1. where 1 means the strings are equal and 0 means no similarity between the two strings.  
                - 'jaro-winkler': The Jaro-Winkler similarity is a string metric measuring edit distance between two strings. Jaro – Winkler Similarity is much similar to Jaro Similarity. They both differ when the prefix of two string match. Jaro – Winkler Similarity uses a prefix scale ‘p’ which gives a more accurate answer when the strings have a common prefix up to a defined maximum length l. We calculate jaro-winkler using jaro-winkler python package
        - avg_threshold_similarity
            - Rata-rata threshold untuk menentukan suatu string masuk ke dalam suatu kelompok tertentu
            - Default: 0.85
        """
        self.avg_threshold_similarity = avg_threshold_similarity
        self.kata_sandang_bali = ['i', 'ni', 'jro', 'jero', 'sang', 'ida']

        if pairwise_distance == 'ratcliff':
            self.pairwise_method = self._ratcliff_obershelp_algorithm
        elif pairwise_distance == 'jaccard':
            self.pairwise_method = self._jaccard_similarity
        elif pairwise_distance == 'sorensen-dice':
            self.pairwise_method = self._sorensen_dice_similarity
        elif pairwise_distance == 'jaro-distance':
            self.pairwise_method = self._jaro_similarity
        elif pairwise_distance == 'jaro-winkler':
            self.pairwise_method = self._jaro_winkler_similarity
        else:
            raise ValueError('Pairwise distance algorithm does not exists!')

    def fit(self, X_predicted_chars, delimiter=';'):
        """
        <Descriptions>
        Preparing list of unique set of predicted chars from user input
        <Input>
        - X_predicted_chars: 
            --List of string predicted chars: ["I Sangsiah", "I Durbudi"]
            --List of string predicted chars separated with delimiter: ["I Macan; I Suriah", "I Budi; Pan Ana"]
            --List of list of string predicted chars: [
            ['I Sansiah; I Macan'],
            ['I Meme'],
            ['Meong Kuuk; I Singa']
            ]
        - delimiter: str()
        <Output>
        Return the model with list of unique set of predicted chars
        """
        self.pred_characters = self._prepare_data_format(X_predicted_chars)
        return self

    def cluster(self):
        """
        <Description>
        - Module untuk alias clustering berbasis aturan dengan algoritma pairwise string distance similarity yang dipilih
        """
        pred_characters = self.pred_characters
        kata_sandang_bali = self.kata_sandang_bali
        avg_threshold_similarity = self.avg_threshold_similarity
        merge_extracted_characters = [
            tokoh for tokoh in pred_characters if len(tokoh) != 1 and tokoh.lower() not in kata_sandang_bali
        ]
        cluster_characters = dict()
        counter = 1
        while (len(merge_extracted_characters) > 0):
            key = 'Tokoh-'+str(counter)
            cluster_characters[key] = list()
            for tokoh in merge_extracted_characters:
                # pengecekan selalu diulangi dari awal dictionary lagi
                for i in range(1, counter):
                    key = 'Tokoh-'+str(i)
                    if (tokoh not in cluster_characters[key]) and (len(cluster_characters[key]) == 0):
                        if tokoh in merge_extracted_characters:
                            cluster_characters[key].append(tokoh)
                            merge_extracted_characters.pop(
                                merge_extracted_characters.index(tokoh))
                    else:
                        # check average similarity dengan sesama list apakah ada yang mirip, threshold=0.8
                        avg_similarity = 0
                        for grouped_tokoh in cluster_characters[key]:
                            x = tokoh.lower()
                            y = grouped_tokoh.lower()
                            filtered_x = " ".join(
                                [a for a in x.split(' ') if a not in kata_sandang_bali])
                            filtered_y = " ".join(
                                [a for a in y.split(' ') if a not in kata_sandang_bali])
                            avg_similarity += self.pairwise_method(
                                filtered_x, filtered_y)
                        avg_similarity /= len(cluster_characters[key])
                        if avg_similarity >= avg_threshold_similarity:
                            if tokoh in merge_extracted_characters:
                                cluster_characters[key].append(tokoh)
                                merge_extracted_characters.pop(
                                    merge_extracted_characters.index(tokoh))
                        else:
                            # Find match substring exactly after filtered from kata penunjuk bali
                            for grouped_tokoh in cluster_characters[key]:
                                x = tokoh.lower()
                                y = grouped_tokoh.lower()
                                filtered_x = " ".join(
                                    [a for a in x.split(' ') if a not in kata_sandang_bali])
                                filtered_y = " ".join(
                                    [a for a in y.split(' ') if a not in kata_sandang_bali])
                                # cari substring x pada y [dewane; dewa], [arjunane; arjuna]-->found
                                z = filtered_x.find(filtered_y)
                                if z != -1:
                                    if tokoh in merge_extracted_characters:
                                        cluster_characters[key].append(tokoh)
                                        merge_extracted_characters.pop(
                                            merge_extracted_characters.index(tokoh))
                                    break
            counter += 1
        self.characters_alias_clustering = dict(
            [(k, v) for k, v in cluster_characters.items() if len(v) != 0]
        )
        self.__clean_cluster_results()

        return self.characters_alias_clustering

    def save_cluster_results(self, path_filename, format='txt'):
        try:
            if format == 'txt':
                self.__save_txt(path_filename)
            return self
        except NameError:
            print('Alias clustering results is not defined yet!')

    @staticmethod
    def evaluate_alias_cluster_results(true_clusters, predicted_clusters, threshold_tolerance=0.6):
        """
        Calculate the recall, precision, f1-score between list of list of true clusters and list of list of predicted_clusters
        <Input>:
        - true_cluters: List(List())
        true_clusters = [
            ['I Angsa', 'Angsa', 'angsa'],
            ['I Kerkuak', 'Kerkuak', 'kerkuak'],
            ['I Cicing', 'Cicing', 'cicing', 'cicinge'],
            ['Pan Berag'],
            ['Sang Raja', 'Rajane', 'I Raja'],
        ]
        - predicted_clusters: List(List())
        predicted_alias_clustering = [
            ['Pan Berag'],
            ['I Kerkuak', 'Kerkuak'],
            ['I Angsa', 'Angsa', 'angsa'],
            ['kerkuak'],
            ['Cicing', 'I Cicing','cicinge','cicing'],
            ['Sang Raja', 'I Raja', 'Rajane'],
        ]
        - threshold_tolerance: Percentage of tolerance misclassified cluster. The more threshold tolerance the tighter the results. Default 60%
        <Output>:
        -results : Dict(Recall, Precision, F1-score)
        """
        number_of_E_exists_in_G = 0
        number_of_G_exists_in_E = 0
        number_of_E_not_exists_in_G = 0
        number_of_G_not_exists_in_E = 0
        n_true_clusters = len(true_clusters)
        n_predicted_clusters = len(predicted_clusters)
        for pred_cluster in predicted_clusters:
            # check if pred_cluster is exists in any list of true_clusters
            found = False
            for true_cluster in true_clusters:
                if set(true_cluster) == set(pred_cluster):
                    found = True
                    number_of_E_exists_in_G += 1
                    number_of_G_exists_in_E += 1
                    true_clusters.pop(true_clusters.index(true_cluster))
                    break
                else:
                    # cari subset anggota himpunan, kalau subset anggota himpunan lebih dari 3/4 dari seluruh true cluster maka dianggap sama
                    subset = set(true_cluster).intersection(set(pred_cluster))
                    threshold = threshold_tolerance * \
                        (100/(len(true_cluster)/len(pred_cluster)))/100
                    persentase_subset = len(subset)/len(true_cluster)
                    if len(subset) != 0 and persentase_subset > threshold:
                        found = True
                        number_of_E_exists_in_G += 1
                        number_of_G_exists_in_E += 1
                        true_clusters.pop(true_clusters.index(true_cluster))
                        break

            if not found:
                number_of_E_not_exists_in_G += 1

        number_of_G_not_exists_in_E = n_true_clusters - number_of_G_exists_in_E

        # calculate recall, precision, f1-score
        recall = (1 - (number_of_G_not_exists_in_E/n_true_clusters)
                  ) if n_true_clusters != 0 else 0
        precision = (1 - (number_of_E_not_exists_in_G /
                     n_predicted_clusters)) if n_predicted_clusters != 0 else 0
        results = {
            'recall': recall,
            'precision': precision,
            'f1_score': (2*recall*precision)/(recall+precision) if (recall != 0) and (precision != 0) else 0
        }
        return results

    def __clean_cluster_results(self):
        """
        <Description>
        - Module for clean the alias cluster results from any punctuation left and split string of detected characters by comma
        """
        for key_tokoh, alias_cluster in self.characters_alias_clustering.items():
            input_string = ", ".join(alias_cluster)
            self.characters_alias_clustering[key_tokoh] = re.sub(
                r'[.]', '', input_string)
            self.characters_alias_clustering[key_tokoh] = [
                tokoh.strip() for tokoh in self.characters_alias_clustering[key_tokoh].split(',')
            ]

        return self

    def __save_txt(self, path_filename):
        alias_clustering_results = self.characters_alias_clustering
        texts = ""
        for key_tokoh, characters in alias_clustering_results.items():
            text = "".join(key_tokoh + str(' : '))
            chars = ", ".join(characters)
            texts += text + chars + "\n"

            with open(path_filename, 'w') as f:
                f.writelines(texts)
        return self

    @staticmethod
    def _prepare_data_format(X_predicted_chars, delimiter=';'):
        # preprocess X_predicted_chars into correct list format
        pred_characters = list()
        for pred_chars in X_predicted_chars:
            if type(pred_chars) is list:
                for char in pred_chars:
                    for x in char.split(delimiter):
                        pred_characters.append(x.strip())
            elif type(pred_chars) is str:
                for char in pred_chars.split(delimiter):
                    pred_characters.append(char.strip())
            elif pred_chars is np.nan:
                continue
        # unique names without nan values
        return list({pred_char for pred_char in pred_characters if pred_char == pred_char})
