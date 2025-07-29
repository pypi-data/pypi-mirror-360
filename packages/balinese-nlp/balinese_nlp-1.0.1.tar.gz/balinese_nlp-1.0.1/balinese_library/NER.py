import nltk
from nltk.tokenize import word_tokenize
import string
import re
import os


class NER_name:
    def __init__(self):
        self.cerita = []
        self.listStop = []
        self.namadepan = []
        self.jawaban = []
        self.sanskerta = []
        self.id_text = 0
        self.total = 0
        self.punc = '''!()-[]{};:.'"”\<>/?@#$%^&*_~'''
        self.gender = ['I', 'Ni', 'Bagus', 'Ayu']
        self.urutankelahiran = ['Putu', 'Gede', 'Wayan', 'Luh', 'Made',
                                'Madé', 'Kadek', 'Nengah', 'Nyoman', 'Komang', 'Ketut']
        self.wangsa = ['Ida', 'Anak', 'Cokorda', 'Tjokorda', 'Gusti',
                       'Dewa', 'Sang', 'Ngakan', 'Bagus', 'Desak', 'Jero', 'Anake', 'Ratu']
        self.singkatan = ['IB', 'IA', 'Gde', 'Gd', 'Cok', 'AA', 'Gst', 'Dw', 'Ngkn', 'Dsk.', 'W',
                          'Wy', 'Wyn', 'Pt', 'Ngh', 'Md', 'N', 'Nymn', 'Ny', 'Kt', 'Dayu', 'Pan', 'Men', 'Nang', 'Bapa', 'Kak', 'Dong', 'Dadong']
        self.pengenalan = ['madan', 'mawasta', 'mewasta',
                           'maparab', 'mapesengan', 'kaparabin']

        self.namadepan.append(self.gender)
        self.namadepan.append(self.urutankelahiran)
        self.namadepan.append(self.wangsa)
        self.namadepan.append(self.singkatan)

    def load_vocabulary(self):
        path = os.path.dirname(__file__)
        vocab_path = os.path.dirname(__file__) + "/data/BaliVocab.txt"
        with open(vocab_path, 'r') as s_file:
            for line in s_file:
                stripped_line = line.strip('\n')
                self.listStop.append(stripped_line)

        sansekerta_path = os.path.dirname(
            __file__) + "/data/sansekertavocab.txt"
        with open(sansekerta_path, 'r', encoding="utf8") as s_file:
            for line in s_file:
                stripped_line = line.strip('\n')
                self.sanskerta.append(stripped_line)

    def person_(self,sentence):
        namadepan = self.gender + self.urutankelahiran + self.wangsa + self.singkatan
        pengenalan = self.pengenalan
        listStop = self.listStop
        sanskerta = self.sanskerta
        sentences = nltk.tokenize.sent_tokenize(sentence)
        punc = string.punctuation
        names = []

        # tokenize dan hilangkan punctuation
        for sindex, sentence in enumerate(sentences):
            for char in sentence:
                if (char in punc):
                    sentences[sindex] = sentences[sindex].replace(char, "")
            sentences[sindex] = nltk.tokenize.word_tokenize(sentence)

        # hilangkan suffix 'ne'
        # for sindex, words in enumerate(sentences):
            # for windex, word in enumerate(words):
                # sentences[sindex][windex] = re.sub('ne$', '', word)

        # apply NER rule based
        for sindex, words in enumerate(sentences):
            for windex, word in enumerate(words):
                # aturan 1
                if (word in namadepan):
                    # append ke names dan dapatkan index sementara
                    names.append([word])
                    temp = names.index([word])
                    for c in range((windex+1), (len(sentences[sindex]))):
                        try:
                            next_word = sentences[sindex][c]
                            if (next_word[0].isupper()):
                                names[temp].append(next_word)
                            else:
                                break
                        except:
                            continue
                    continue
                # aturan 2
                elif ((word in listStop) or (word.lower() in listStop)):
                    continue

                # aturan 3
                if (word in pengenalan):
                    temp = []
                    for c in range((windex+1), (len(sentences[sindex]))):
                        try:
                            next_word = sentences[sindex][c]
                            if (next_word[0].isupper()):
                                temp.append(next_word)
                            else:
                                break
                        except:
                            continue
                    names.append(temp)
                    continue

                # aturan 4
                try:
                    if (word.isupper()):
                        if ((word in sanskerta) or (word.lower() in sanskerta)):
                            names.append([word])
                            temp = names.index([word])
                            for c in range((windex+1), (len(sentences[sindex]))):
                                try:
                                    next_word = sentences[sindex][c]
                                    if (next_word[0].isupper()):
                                        names[temp].append(next_word)
                                    else:
                                        break
                                except:
                                    continue
                            continue
                except:
                    continue
        # merge names
        output = list()
        for i in names:
            if (len(i) >= 1):
                i = ' '.join(i)
                output.append(i)
        output = list(dict.fromkeys(output))
        return output 
        
    def person(self, sentence):
        self.load_vocabulary()
        names = []
        output = []
        kalimat = sentence
        kalimat = nltk.tokenize.sent_tokenize(kalimat)

        for sindex, i in enumerate(kalimat):
            for j in i:
                if (j in self.punc):
                    kalimat[sindex] = kalimat[sindex].replace(j, "")
            kalimat[sindex] = nltk.tokenize.word_tokenize(i)
        for sindex, a in enumerate(kalimat):
            for gindex, b in enumerate(a):
                kalimat[sindex][gindex] = re.sub('ne$', '', b)
                # kalimat[sindex][gindex] = re.sub('e$', '', b)

        for sindex, sentence in enumerate(kalimat):
            rule = 0
            for gindex, a in enumerate(sentence):
                if (a in (item for sublist in self.namadepan for item in sublist)):
                    names.append([a])
                    temp = names.index([a])
                    for c in range((gindex+1), (len(kalimat[sindex]))):
                        try:
                            if (kalimat[sindex][c][0].isupper()):
                                names[temp].append(kalimat[sindex][c])
                            else:
                                break
                        except:
                            continue
                    continue
                elif ([b for b in self.listStop if a == b] or [b for b in self.listStop if a.lower() == b] and rule == 0):
                    continue
                if (a in self.pengenalan):
                    temp = []
                    for c in range((gindex+1), (len(kalimat[sindex]))):
                        try:
                            if (kalimat[sindex][c][0].isupper()):
                                temp.append(kalimat[sindex][c])
                            else:
                                break
                        except:
                            continue
                    names.append(temp)
                    continue
                try:
                    if (a[0].isupper()):
                        if ([b for b in self.sanskerta if a == b] or [b for b in self.sanskerta if a.lower() == b]):
                            names.append([a])
                            temp = names.index([a])
                            for c in range((gindex+1), (len(kalimat[sindex]))):
                                try:
                                    if (kalimat[sindex][c][0].isupper()):
                                        names[temp].append(kalimat[sindex][c])
                                    else:
                                        break
                                except:
                                    continue
                            continue
                except:
                    continue
                else:
                    continue

        for i in names:
            if (len(i) > 1):
                i = ' '.join(i)
                output.append(i)

        same_name = []
        output = list(dict.fromkeys(output))
        copy = output.copy()
        for i in range(0, len(output)):
            for j in range(0, len(output)):
                if ((copy[i] in output[j]) and i != j):
                    same_name.append(copy[i])

        output = [e for e in output if e not in same_name]
        return output


class NER_location:
    pass


class NER_time:
    pass
