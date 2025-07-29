import re
from balinese_nlp.textpreprocessor import TextPreprocessor

class NERLocation:

    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.conjungtion = ['tur', 'lan', 'miwah', 'sareng', 'utawi']
        self.days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu', 'Redite', 'Soma', 'Anggara', 'Buda', 'Wraspati', 'Sukra', 'Caniscara']
        self.month = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Nopember', 'Desember']
        self.notLocation = ['Sang', 'Hyang', 'Ida', 'Sanghyang', 'Dewa', 'Dewi', 'Tuhan', 'Bapak', 'Ibu', 'Rp', 'Raja', 'Ratu', 'Betari', 'PT', 'Basa', 'Legenda', 'Patih', 
        'Perguruan', 'Fakultas', 'Universitas', 'Institut', 'TK', 'SD', 'SMP', 'SMA', 'SMK', 'SMEAN', 'ITB', 'Teknik', 'Institut',
        'Dewata', 'Kubilai', 'Purwa', 'Calonarang', 'Babad', 'Ramayana', 'Rama', 'Subali', 'Sugriwa', 'Rahwana', 'Sayyidina', 'Puputan']

        self.area = ['wewidangan', 'widang', 'gumi', 'wilayah', 'bongkol', 'jagat', 'sawengkon', 'wawengkon']
        self.prefixsLocation = ['Gunung', 'Danau', 'Danu', 'Kebun', 'Pasih', 'Segara','Peken', 'Desa', 'Kelurahan', 'Kecamatan', 'Kabupaten', 'Kota', 'Provinsi', 
        'Propinsi', 'Pulau', 'Pulo', 'Nusa', 'Tanjung', 'Pasisi', 'Pura', 'Rumah', 'Museum', 'Bandara', 'Kompleks', 'Jalan', 'Gedong', 'Setra', 'Taman', 'Candi',
        'Kerajaan', 'Krajan', 'Kesultanan', 'Jembatan', 'Pelabuhan', 'Pelabuan', 'Pesisi']
        self.prepotitionPrefixs = ['ring', 'di', 'saking', 'ka', 'ke', 'uli', 'Ring', 'Di', 'Saking', 'Ka', 'Ke', 'Uli']
        self.directionssuffix = ['Utara', 'Timur', 'Selatan', 'Barat', 'Kaja', 'Kangin', 'Kelod', 'Kauh', 'Tenggara', 'Tengah', 'Loka', 'Kulon']
        self.directionprefix = ['Dauh','dangin','badangin','arep', 'batan', 'badauh', 'tengahing', 'ajeng', 'madianing', 'pusat', 'ungkur', 'muncuk']
        self.punctuation = ".?!"
        self.document = {}

    def predict(self, sentence):
        text_preprocessed = self.__preprocess_text(sentence)
        locations = self.__ruleBasedNER(text_preprocessed)
        return locations
        

    def __preprocess_text(self,text):
        """Function to preprocess text into cleaned tokens

        Args:
            text (str): input text in string format
        """
        symbols = "\"#$%&*+:;<=>@[\]^_`{|}~\n"
        text = self.preprocessor.convert_ascii_sentence(text)
        text = self.preprocessor.remove_non_ascii_punctuation(text)
        text = text.replace('\n',' ')
        text = text.translate(str.maketrans("","", symbols))
        tokens = self.preprocessor.balinese_word_tokenize(text)
        return tokens
    
    def __ruleBasedNER(self, textPrep):
        locations = list()
        n = len(textPrep) # Dapatkan panjang list di awal untuk pemeriksaan batas
        
        for index, i in enumerate(textPrep):
            # aturan tanggal
            date = []
            # Pastikan ada cukup elemen untuk memeriksa k+2
            # Perulangan ini sangat tidak efisien dan rentan, perlu dipertimbangkan ulang logikanya
            # Ini akan mengiterasi setiap karakter dalam kata `i`
            # dan akan menyebabkan masalah jika `i` sangat panjang atau tidak berisi digit/garis miring
            # Jika tujuannya mencari pola tanggal seperti "DD/MM" dalam satu token, pendekatan ini salah
            # Asumsi: Anda ingin mendeteksi token yang merupakan format tanggal seperti "10/11"
            # Jika token itu sendiri adalah tanggal
            if re.match(r'\d{1,2}/\d{1,2}', i): # Lebih aman dan jelas untuk pola tanggal
                # Jika token sebelumnya adalah judul (misal: "Jakarta, 10/11")
                if index > 0 and textPrep[index-1].istitle():
                    locations.append(textPrep[index-1])
            
            # aturan tempat, tanggal (misal: "Denpasar, 10 November")
            # Pastikan ada cukup elemen untuk index+2
            if index + 2 < n: 
                if i == ',' and textPrep[index+1].isdigit() and textPrep[index+2] in self.month:
                    temp = []
                    # Perulangan mundur, pastikan index-1 tidak keluar batas
                    for j in range(index-1, -1, -1): 
                        if textPrep[j] and textPrep[j] not in self.prepotitionPrefixs and textPrep[j] not in self.prefixsLocation and textPrep[j] not in self.notLocation:
                            if textPrep[j].istitle() or (textPrep[j].isupper() and not textPrep[j].isdigit() and textPrep[j] not in self.punctuation):
                                temp.append(textPrep[j])
                            else:
                                break
                        else:
                            # Jika ditemukan kata yang tidak relevan, hentikan pencarian ke belakang
                            break # Mengubah temp = [] menjadi break untuk efisiensi
                    if temp:
                        locations.append(" ".join(reversed(temp)))
            
            # aturan mata angin (misal: "Nusa Tenggara Barat", "Denpasar Utara")
            # Pastikan ada cukup elemen untuk index+1 dan index-1
            if i in self.directionssuffix:
                temp = []
                
                # Aturan untuk "X Y Tenggara" atau "X Barat"
                # Periksa index-1 dan index+1 dengan hati-hati
                # If textPrep[index+1] not in self.directionssuffix (Misal: "Barat Daya" vs "Barat Laut")
                if index + 1 < n and textPrep[index+1] in self.directionssuffix: # Kasus seperti "Barat Daya", "Utara Timur"
                    temp.append(i)
                    temp.append(textPrep[index+1])
                    # Sekarang cari kata-kata sebelumnya
                    for j in range(index - 1, -1, -1):
                        # Kondisi yang sama seperti di bawah, tapi diulang untuk konsistensi
                        if textPrep[j] not in self.prepotitionPrefixs and \
                           textPrep[j] not in self.prefixsLocation and \
                           textPrep[j] not in self.punctuation and \
                           not textPrep[j].isdigit() and \
                           (textPrep[j].istitle() or textPrep[j].isupper()):
                            temp.append(textPrep[j])
                        else:
                            break
                    if temp:
                        locations.append(" ".join(reversed(temp)))
                    continue # Lanjutkan ke iterasi berikutnya setelah menemukan multi-word direction

                # Kasus umum seperti "Denpasar Utara"
                # Perlu memastikan index-1 valid
                if index > 0 and \
                   textPrep[index-1] not in self.prepotitionPrefixs and \
                   textPrep[index-1] not in self.prefixsLocation and \
                   (textPrep[index-1].istitle() or textPrep[index-1].isupper()) and \
                   (index + 1 >= n or textPrep[index+1] not in self.directionssuffix): # Pastikan bukan bagian dari kombinasi dua mata angin
                    
                    temp.append(i) # Tambahkan mata anginnya
                    temp.append(textPrep[index-1]) # Tambahkan kata sebelumnya (misal: "Denpasar")
                    
                    # Lanjutkan pencarian ke belakang untuk kata-kata lain
                    for j in range(index-2, -1, -1): # Mulai dari index-2
                        if textPrep[j] not in self.prepotitionPrefixs and \
                           textPrep[j] not in self.prefixsLocation and \
                           textPrep[j] not in self.punctuation and \
                           not textPrep[j].isdigit(): 
                            if textPrep[j].istitle() or textPrep[j].isupper():
                                temp.append(textPrep[j])
                            else:
                                break
                        else:
                            break
                    
                    # Tidak perlu pengecekan 'lenght == len(temp)' lagi karena logikanya sudah diperbaiki
                    if temp:
                        locations.append(" ".join(reversed(temp)))
            
            # aturan preposisi ('ring', 'di', 'saking', 'ka', 'uli')
            # Pastikan ada cukup elemen untuk index+1
            if i in self.prepotitionPrefixs:
                temp = []
                if index + 1 < n and textPrep[index+1] not in self.directionssuffix and \
                   textPrep[index+1] not in self.notLocation and not textPrep[index+1].isdigit():
                    
                    # Iterasi hingga akhir list atau sampai kondisi berhenti
                    for j in range(index+1, n): # Ubah len(textPrep)-1 menjadi n
                        if textPrep[j] not in self.punctuation and \
                           (textPrep[j].istitle() or textPrep[j].isupper() or textPrep[j].isdigit()):
                            temp.append(textPrep[j])
                        elif textPrep[j].lower() == 'de': # Gunakan .lower() untuk perbandingan yang konsisten
                            temp.append(textPrep[j])
                        else:
                            if textPrep[j].lower() == 'diri' and temp: # Pastikan temp tidak kosong sebelum del
                                temp.pop() # Menggunakan pop() lebih Pythonic daripada del temp[-1]
                            break
                    if temp: 
                        locations.append(" ".join(temp))
            
            # aturan pake kata depan lokasi (misal: "Gunung Agung", "Peken Sanglah")
            if i in self.prefixsLocation:
                temp = []
                # Kasus jika di awal kalimat: "Gunung Agung"
                if index == 0:
                    # Pastikan index+1 valid
                    if index + 1 < n and textPrep[index+1] not in self.punctuation and \
                       (textPrep[index+1].istitle() or textPrep[index+1].isdigit()):
                        temp.append(i)
                # Kasus jika di tengah kalimat: "blablabla Gunung Agung"
                else: 
                    # Pastikan index-1 valid dan index+1 valid
                    if index - 1 >= 0 and index + 1 < n and \
                       textPrep[index-1] not in self.notLocation and \
                       textPrep[index-1] not in self.prepotitionPrefixs and \
                       textPrep[index-1] not in self.prefixsLocation and \
                       (textPrep[index+1].istitle() or textPrep[index+1].isdigit()):
                        temp.append(i)
                    else:
                        continue # Lanjutkan ke iterasi berikutnya jika kondisi tidak terpenuhi
                
                # Jika `temp` sudah memiliki `i`, lanjutkan untuk mencari kata-kata berikutnya
                if temp and len(temp) == 1: # Pastikan i sudah ditambahkan dan tidak ada masalah di awal
                    for j in range(index+1, n): # Ubah len(textPrep)-1 menjadi n
                        if textPrep[j] not in self.punctuation and \
                           (textPrep[j].istitle() or textPrep[j].isdigit()):
                            temp.append(textPrep[j])
                        else:
                            break
                
                if temp:
                    locations.append(" ".join(temp))

            # aturan pake area, misalnya wewidangan Karangasem
            if i in self.area:
                temp = []
                # Iterasi hingga akhir list
                for j in range(index+1, n): # Ubah len(textPrep)-1 menjadi n
                    if textPrep[j] not in self.punctuation and textPrep[j].istitle():
                        if textPrep[j] not in self.directionssuffix and \
                           textPrep[j] not in self.prefixsLocation and \
                           textPrep[j] not in self.prepotitionPrefixs:
                            temp.append(textPrep[j])
                        else:
                            # Jika ditemukan kata yang tidak relevan, hentikan
                            break
                    else:
                        break
                if temp: 
                    locations.append(" ".join(temp))

            # aturan conjongtion, aturan untuk lokasi beruntun yang langsung nama, kek Desa Pertima, Karangasem
            if i in self.conjungtion or i == ',':
                temp = []
                loc = []
                locjoin = []
                
                # Mencari lokasi sebelumnya
                for j in range(index-1, -1, -1): 
                    if textPrep[j].istitle():
                        loc.append(textPrep[j])
                    else:
                        break
                
                if loc:
                    locjoin.append(" ".join(reversed(loc)))
                
                # Memastikan lokasi sebelumnya sudah terdeteksi dan merupakan lokasi yang valid
                if locjoin and locjoin[0] in locations:
                    # Mencari lokasi setelah konjungsi/koma
                    for j in range(index+1, n): # Ubah len(textPrep)-1 menjadi n
                        if textPrep[j] not in self.punctuation and \
                           (textPrep[j].istitle() or textPrep[j].isupper()):
                            if textPrep[j] not in self.directionssuffix and \
                               textPrep[j] not in self.prefixsLocation and \
                               textPrep[j] not in self.prepotitionPrefixs and \
                               textPrep[j] not in self.notLocation:
                                temp.append(textPrep[j])
                            else:
                                break
                        else:
                            break
                if temp: 
                    locations.append(" ".join(temp))

        # cleaning resulted locations
        same_place=[]
        locations = list(dict.fromkeys(locations)) # Hapus duplikat
        
        # Perbaiki logika pembersihan lokasi tumpang tindih
        # Gunakan set untuk melacak lokasi yang akan dihapus
        to_remove = set()
        for i in range(len(locations)):
            for j in range(len(locations)):
                if i != j and locations[i] in locations[j]:
                    to_remove.add(locations[i])
        
        locations = [loc for loc in locations if loc not in to_remove]

        locations = ", ".join(locations)
        locations = "Location : " + locations

        return locations