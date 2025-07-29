import nltk
from nltk.tokenize import word_tokenize 
import string
import re
import glob
import os 

global names, kalimat, output, total
cerita=[]
listStop=[]
namadepan=[]
jawaban=[]
output=[]
sanskerta=[]
id_text = 0
total  = 0
punc = '''!()-[]{};:.'"”\<>/?@#$%^&*_~'''

gender=['I','Ni','Bagus','Ayu']
urutankelahiran=['Putu','Gede','Wayan','Luh','Made','Madé','Kadek','Nengah','Nyoman','Komang','Ketut']
wangsa=['Ida','Anak','Cokorda','Tjokorda','Gusti','Dewa','Sang','Ngakan','Bagus','Desak']
singkatan=['IB','IA','Gde','Gd','Cok','AA','Gst','Dw','Ngkn','Dsk.','W','Wy','Wyn','Pt','Ngh','Md','N','Nymn','Ny','Kt','Dayu','Pan','Men']

namadepan.append(gender)
namadepan.append(urutankelahiran)
namadepan.append(wangsa)
namadepan.append(singkatan)
path = os.path.dirname(__file__)
vocab_path = os.path.dirname(__file__) + "/storage/BaliVocab.txt"
with open( vocab_path, 'r' ) as s_file:
    for line in s_file:
        stripped_line = line.strip('\n')
        listStop.append(stripped_line)

sansekerta_path = os.path.dirname(__file__) + "/storage/sansekertavocab.txt"
with open(sansekerta_path,'r',encoding="utf8" ) as s_file:
    for line in s_file:
        stripped_line = line.strip('\n')
        sanskerta.append(stripped_line)

names=[] 
def ner_name(sentences):
    global output
    kalimat = sentences
    kalimat = nltk.tokenize.sent_tokenize(kalimat)

    for sindex,i in enumerate(kalimat):
        for j in i:
            if(j in punc):
                kalimat[sindex] = kalimat[sindex].replace(j, "")
        kalimat[sindex] = nltk.tokenize.word_tokenize(i)
    for sindex, a in enumerate(kalimat):
        for gindex, b in enumerate(a):
            kalimat[sindex][gindex] = re.sub('ne$', '', b)

    for sindex, sentence in enumerate(kalimat):
        for gindex, a in enumerate(sentence):
            if ([b for b in listStop if a == b] or [b for b in listStop if a.lower() == b]) :
                continue
            elif(a in(item for sublist in namadepan for item in sublist)):
                names.append([a])
                temp = names.index([a])
                for c in range((gindex+1),(len(kalimat[sindex]))):
                    try:
                        if(kalimat[sindex][c][0].isupper()):
                            names[temp].append(kalimat[sindex][c])
                        else:
                            break
                    except:
                        continue
                continue
            try:
                if(a[0].isupper()):
                    if([b for b in sanskerta if a.lower() == b] or [b for b in sanskerta if a.lower() == b]):
                        names.append([a])
                        temp = names.index([a])
                        for c in range((gindex+1),(len(kalimat[sindex]))):
                            try:
                                if(kalimat[sindex][c][0].isupper()):
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
        if(len(i)>1):
            i = ' '.join(i)
            output.append(i)

    same_name=[]
    output = list(dict.fromkeys(output))
    copy = output
    for i in range(0,len(output)):
        for j in range(0,len(output)):
            if((copy[i] in output[j]) and i!=j):
                same_name.append(copy[i])

    output = [e for e in output if e not in same_name]
    
    name = ', '.join(map(str, output))
    name = "Nama : " + name
    return name                       