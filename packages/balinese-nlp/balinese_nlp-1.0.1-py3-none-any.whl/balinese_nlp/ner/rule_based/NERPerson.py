from balinese_nlp.textpreprocessor import TextPreprocessor
from balinese_nlp.ner.utils import load_bali_vocabs, load_sansekerta_vocabs
import string
import re
import os



class NERPerson:
    def __init__(self):
        self.cerita = []
        self.listStop = load_bali_vocabs()
        self.sanskerta = load_sansekerta_vocabs()
        self.namadepan = []
        self.jawaban = []
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
        self.preprocessor = TextPreprocessor()


    def predict(self, sentence):
        names = []
        output = []
        kalimat = sentence
        kalimat = self.preprocessor.balinese_sentences_segmentation(kalimat)

        for sindex, i in enumerate(kalimat):
            for j in i:
                if (j in self.punc):
                    kalimat[sindex] = kalimat[sindex].replace(j, "")
            kalimat[sindex] = self.preprocessor.balinese_word_tokenize(i)
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
