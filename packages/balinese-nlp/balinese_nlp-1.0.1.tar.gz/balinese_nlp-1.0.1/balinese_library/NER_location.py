# PENTING!
# Penulisan input harus diakhiri dengan tanda baca, n kalo nama lokasi ya pake hurup kapital
# Misal, Desa Karangasem. dimana karangasem-nya pake huruf kapital n diakhiri tanda baca, kalo ga gitu ya ga kedetect
# Inputnya pake perulangan, kalo mau suud tinggal enter jak

import os, string, re, nltk, csv
from nltk.tokenize import word_tokenize
documents = {}
punctuation = ".?!"
conjungtion = ['tur', 'lan', 'miwah', 'sareng', 'utawi']
days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu', 'Redite', 'Soma', 'Anggara', 'Buda', 'Wraspati', 'Sukra', 'Caniscara']
month = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Nopember', 'Desember']
notLocation = ['Sang', 'Hyang', 'Ida', 'Sanghyang', 'Dewa', 'Dewi', 'Tuhan', 'Bapak', 'Ibu', 'Rp', 'Raja', 'Ratu', 'Betari', 'PT', 'Basa', 'Legenda', 'Patih', 
'Perguruan', 'Fakultas', 'Universitas', 'Institut', 'TK', 'SD', 'SMP', 'SMA', 'SMK', 'SMEAN', 'ITB', 'Teknik', 'Institut',
'Dewata', 'Kubilai', 'Purwa', 'Calonarang', 'Babad', 'Ramayana', 'Rama', 'Subali', 'Sugriwa', 'Rahwana', 'Sayyidina', 'Puputan']

area = ['wewidangan', 'widang', 'gumi', 'wilayah', 'bongkol', 'jagat', 'sawengkon', 'wawengkon']
prefixsLocation = ['Gunung', 'Danau', 'Danu', 'Kebun', 'Pasih', 'Segara','Peken', 'Desa', 'Kelurahan', 'Kecamatan', 'Kabupaten', 'Kota', 'Provinsi', 
'Propinsi', 'Pulau', 'Pulo', 'Nusa', 'Tanjung', 'Pasisi', 'Pura', 'Rumah', 'Museum', 'Bandara', 'Kompleks', 'Jalan', 'Gedong', 'Setra', 'Taman', 'Candi',
'Kerajaan', 'Krajan', 'Kesultanan', 'Jembatan', 'Pelabuhan', 'Pelabuan', 'Pesisi']
prepotitionPrefixs = ['ring', 'di', 'saking', 'ka', 'ke', 'uli', 'Ring', 'Di', 'Saking', 'Ka', 'Ke', 'Uli']
directionssuffix = ['Utara', 'Timur', 'Selatan', 'Barat', 'Kaja', 'Kangin', 'Kelod', 'Kauh', 'Tenggara', 'Tengah', 'Loka', 'Kulon']
directionprefix = ['arep', 'batan', 'badauh', 'tengahing', 'ajeng', 'madianing', 'pusat', 'ungkur', 'muncuk']


def listDocuments():
    dokumenList = os.listdir('documents')
    global documents
    for i in dokumenList:
        index = re.findall("(\\d+)", i)[0]
        documents[index] = i
    documents_sorted = {k: v for k, v in sorted(documents.items(), key=lambda item: item[0])}
    documents = documents_sorted
    dataPreprocessing = readDocuments(documents)
    return dataPreprocessing

def readDocuments(documents):
    dataPreprocessing = {}
    for index in documents:
        text = open('documents/'+documents[index])
        text = text.read()
        tittle = text.partition('\n')[0]
        text = text.replace(tittle, "", 1)
        prep = preprocessing(text)
        dataPreprocessing[index] = prep
    return dataPreprocessing

def preprocessing(text):
    symbols = "\"#$%&*+:;<=>@[\]^_`{|}~\n"
    text = text.replace('é','e')
    text = text.replace('Ã©','e')
    text = text.replace('\n',' ')
    text = text.translate(str.maketrans("","", symbols))
    tokens = nltk.tokenize.word_tokenize(text)
    return tokens

def ruleBased(textPrep, locations):
    for index, i in enumerate(textPrep):
        # aturan tanggal
        date = []
        for j in range(len(i)):
            for k in range(j, len(i)-1):
                if i[k].isdigit() and i[k+1] == '/' and i[k+2].isdigit():
                    date.append(i)
                else:
                    break
        if i in date:
            if textPrep[index-1].istitle():
                locations.append(textPrep[index-1])
        
        # aturan tempat, tanggal 
        if i == ',' and textPrep[index+1].isdigit() and textPrep[index+2] in month: # benerin Wanita Batu (drama/monolog,2006)
            temp = []
            for j in range(index-1, -1, -1): 
                if textPrep[j] and textPrep[j] not in prepotitionPrefixs and textPrep[j] not in prefixsLocation and textPrep[j] not in notLocation:
                    if textPrep[j].istitle() or textPrep[j].isupper() and not textPrep[j].isdigit() and textPrep[j] not in punctuation:
                        temp.append(textPrep[j])
                    else:
                        break
                else:
                    temp = []
                    break
            if(temp):
                locations.append(" ".join(reversed(temp)))
        
        # aturan mata angin
        if i in directionssuffix: #benerin NUSA TENGGARA BARAT
            temp = []
            lenght = 0
            if textPrep[index+1] not in directionssuffix: 
                if textPrep[index-1] is not None and textPrep[index-1] not in prepotitionPrefixs and textPrep[index+1] not in directionssuffix and textPrep[index-1] not in prefixsLocation and (textPrep[index-1].istitle() or textPrep[index-1].isupper()):
                    temp.append(i)
                    temp.append(textPrep[index-1])
                    for j in range(index-2, -1, -1):
                        if textPrep[j] and textPrep[j] not in prepotitionPrefixs and textPrep[j] not in prefixsLocation and textPrep[j] not in punctuation and not textPrep[j].isdigit():   
                            if textPrep[j].istitle() or textPrep[j].isupper():
                                temp.append(textPrep[j])
                            else:
                                break
                        else:
                            temp = []
                            break
                else:
                    temp = []
            for j in temp:
                if j in directionssuffix:
                    lenght += 1
            if lenght == len(temp):
                temp = []
            if(temp):                
                locations.append(" ".join(reversed(temp)))        
                
        # aturan preprosisi ('ring', 'di', 'saking', 'ka', 'uli')
        if i in prepotitionPrefixs:
            temp = []
            if textPrep[index+1] not in directionssuffix and textPrep[index+1] not in notLocation and not textPrep[index+1].isdigit():
                for j in range(index+1, len(textPrep)-1):
                    if textPrep[j] not in punctuation and (textPrep[j].istitle() or textPrep[j].isupper() or textPrep[j].isdigit()):
                        temp.append(textPrep[j])
                    elif textPrep[j] == 'de':
                        temp.append(textPrep[j])
                    else:
                        if textPrep[j] == 'diri':
                            del temp[-1]
                        break
            if(temp):          
                locations.append(" ".join(temp))
                
        # aturan pake kata depan lokasi
        if i in prefixsLocation:
            temp = []
            if i is textPrep[0]: #Gunung Agung
                if textPrep[index+1] not in punctuation and (textPrep[index+1].istitle() or textPrep[index+1].isdigit()): #and not textPrep[index+1].isdigit()
                    temp.append(i)
            else: #blablabla Gunung Agung
                if textPrep[index-1] not in notLocation and textPrep[index-1] not in prepotitionPrefixs and textPrep[index-1] not in prefixsLocation and (textPrep[index+1].istitle() or textPrep[index+1].isdigit()):
                    temp.append(i)
                else:
                    temp = []
                    continue
            for j in range(index+1, len(textPrep)-1):
                if textPrep[j] not in punctuation and (textPrep[j].istitle() or textPrep[j].isdigit()):
                    temp.append(textPrep[j])
                else:
                    break

            if(temp):
                locations.append(" ".join(temp))

        # aturan pake area, misalnya wewidangan Karangasem
        if i in area:
            temp = []
            for j in range(index+1, len(textPrep)-1):
                if textPrep[j] not in punctuation and textPrep[j].istitle():
                    if textPrep[j] not in directionssuffix and textPrep[j] not in prefixsLocation and textPrep[j] not in prepotitionPrefixs:
                        temp.append(textPrep[j])
                    else:
                        temp = []
                        break
                else:
                    break
            if(temp):          
                locations.append(" ".join(temp))

        # aturan conjongtion, aturan untuk lokasi beruntun yang langsung nama, kek Desa Pertima, Karangasem
        if i in conjungtion or i == ',':
            temp = []
            loc = []
            locjoin = []
            for j in range(index-1, -1, -1): 
                if textPrep[j].istitle():
                    loc.append(textPrep[j])
                else:
                    break
            if loc:
                locjoin.append(" ".join(reversed(loc)))
            if locjoin and locjoin[0] in locations:
                for j in range(index+1, len(textPrep)-1):
                    if textPrep[j] not in punctuation and (textPrep[j].istitle() or textPrep[j].isupper()):
                        if textPrep[j] not in directionssuffix and textPrep[j] not in prefixsLocation and textPrep[j] not in prepotitionPrefixs and textPrep[j] not in notLocation:
                            temp.append(textPrep[j])
                        else:
                            temp = []
                            break
                    else:
                        break
            if(temp):          
                locations.append(" ".join(temp))

    return locations

def showLocations(locationRetrieve):
    for key, val in locationRetrieve.items():
        locations = ", ".join(val)
        print("Location(s) in document-"+key+": ", end ="")
        if(locations):
            print(locations, end ="")
        else:
            print("-", end ="")
        print('\n', end ="")
    print('\n', end ="")    

def writeToFile(locationRetrieve):
    with open('evaluation/locationRetrieve.txt', 'w', newline='') as dataLocation:
        csvWriter = csv.writer(dataLocation, delimiter=':')
        for key, val in locationRetrieve.items():
            locations = ", ".join(val)
            csvWriter.writerow([key, locations])
            
def ner_location(sentences):
    text = sentences
    locations = []
    textPrep = preprocessing(text)
    locations = ruleBased(textPrep, locations)
    same_place=[]
    locations = list(dict.fromkeys(locations))
    copy = locations
    for i in range(len(locations)-1,0,-1):
        for j in range(len(locations)-1,0,-1):
            if((copy[i] in locations[j]) and i!=j):
                same_place.append(copy[i])
    locations = [e for e in locations if e not in same_place]
    locations = ", ".join(locations)
    locations = "Location : " + locations
    return locations

