class FeatureExtraction:

    def __init__(self):
        pass

    def lexicon_based(self, X_prep, lexicon_word_positif, lexicon_word_negatif, list_of_tags=['RB', 'JJ', 'VB', 'NN']):
        # variable for final result lexicon feature extraction
        X_lexicon_features = list()

        for document in X_prep:
            # tokenization document
            text_token = document.split(' ')

            # variabel menampung fitur lexicon positif
            lexicon_word_positif = dict()
            for tag in list_of_tags:
                lexicon_word_positif[tag] = list()

            # masukkan term-term pada positif lexicon yang terdapat pada dokumen sesuai kelas katanya
            for idx, pos_balinese_lexicon in positif_balinese_lexicons.iterrows():
                term = pos_balinese_lexicon['term']
                if term in text_token:
                    lexicon_word_positif[pos_balinese_lexicon['tag']].append(
                        term)

            # variabel menampung fitur lexicon negatif
            lexicon_word_negatif = dict()
            for tag in list_of_tags:
                lexicon_word_negatif[tag] = list()

            # masukkan term-term pada negatif lexicon yang terdapat pada dokumen sesuai kelas katanya
            for idx, neg_balinese_lexicon in negatif_balinese_lexicons.iterrows():
                term = neg_balinese_lexicon['term']
                if term in text_token:
                    lexicon_word_negatif[neg_balinese_lexicon['tag']].append(
                        term)

            # hitung total banyak term pada masing-masing kelas kata pada setiap polaritynya
            total_lexicon_by_tag = dict()
            for tag in list_of_tags:
                total_lexicon_by_tag[tag] = len(
                    lexicon_word_positif[tag]) + len(lexicon_word_negatif[tag])

            # hitung fitur leksikon [a,b,...,g,h]
            lexicon_fitur_positif = list()
            lexicon_fitur_negatif = list()

            # hitung persentase lexicon positif dan negatif untuk setiap kelas katanya
            for tag, tag_items in lexicon_word_positif.items():
                pembilang = len(tag_items)
                penyebut = total_lexicon_by_tag[tag]

                # append 0 for avoiding 0 division
                if penyebut == 0:
                    lexicon_fitur_positif.append(0)
                else:
                    lexicon_fitur_positif.append(pembilang/penyebut)

            for tag, tag_items in lexicon_word_negatif.items():
                pembilang = len(tag_items)
                penyebut = total_lexicon_by_tag[tag]

                # append 0 for avoiding 0 division
                if penyebut == 0:
                    lexicon_fitur_negatif.append(0)
                else:
                    lexicon_fitur_negatif.append(pembilang/penyebut)

            # concatenate lexicon_positive_features with lexicon_negative_features in axis=1
            lexicon_features = lexicon_fitur_positif + lexicon_fitur_negatif

            # append into X_train_lexicon_features
            X_lexicon_features.append(lexicon_features)

        return X_lexicon_features
