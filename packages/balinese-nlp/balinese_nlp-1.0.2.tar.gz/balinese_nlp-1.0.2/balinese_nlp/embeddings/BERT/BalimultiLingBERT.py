from balinese_nlp.embeddings.BasePretrained import BasePretrained
from huggingface_hub import hf_hub_download
from transformers import AutoTokenizer, AutoModelForMaskedLM, pipeline, AutoModel
import torch


class BalimultiLingBERT(BasePretrained):
    def __init__(self, huggingface_ID='satriabimantara/balinese-pretrained-bert', fine_tuned_folder='balinese-bert-mlm-finetuned', task='mlm'):
        super().__init__(huggingface_ID)
        self.huggingface_ID = f"{huggingface_ID}"
        self.subfolder_finetuned_model = f"{fine_tuned_folder}"
        self.task = task
    
    def load_pretrained_model(self):
        super().load_pretrained_model()
        if self.task == 'mlm':
            return self.__load_mlm_finetuned_model()
        return None
        

    def __load_mlm_finetuned_model(self):
        repo_id = self.huggingface_ID
        subfolder = self.subfolder_finetuned_model
        # muat tokenizer dan model
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(repo_id, subfolder=subfolder)
            # Gunakan AutoModelForMaskedLM jika Anda ingin melakukan tugas MLM (seperti prediksi kata yang di-mask)
            # Gunakan AutoModel jika Anda ingin mengekstrak embeddings (fitur semantik)
            self.model_mlm = AutoModelForMaskedLM.from_pretrained(repo_id, subfolder=subfolder)
            self.model_base = AutoModel.from_pretrained(repo_id, subfolder=subfolder) # Untuk ekstraksi fitur

            # Opsional: Pindahkan model ke GPU jika tersedia
            if torch.cuda.is_available():
                self.model_mlm.to('cuda')
                self.model_base.to('cuda')
                print("Model dipindahkan ke GPU.")
            else:
                print("GPU tidak terdeteksi, model akan berjalan di CPU.")

            print("Model Balinese BERT dan Tokenizer berhasil dimuat.")
            return {
                'tokenizer': self.tokenizer,
                'model_mlm': self.model_mlm,
                'model_base': self.model_base
            }
        except Exception as e:
            print(f"Gagal memuat model atau tokenizer: {e}")
            print("Pastikan path ke direktori model sudah benar dan file ada.")