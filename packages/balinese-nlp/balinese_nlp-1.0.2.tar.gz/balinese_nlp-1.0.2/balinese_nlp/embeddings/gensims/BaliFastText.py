from balinese_nlp.embeddings.BasePretrained import BasePretrained
from gensim.models import FastText
from huggingface_hub import hf_hub_download
import os


class BaliFastText(BasePretrained):

    def __init__(self, huggingface_repo_ID, pretrained_model_bin_filename="200_fasttext_model.bin"):
        super().__init__(
            huggingface_repo_ID=huggingface_repo_ID
        )
        self.filepath_pretrained_model_bin = f"FastText/{pretrained_model_bin_filename}"
        self.filepath_pretrained_model_npy = f"FastText/{pretrained_model_bin_filename}.wv.vectors_ngrams.npy"

    def load_pretrained_model(self):
        super().load_pretrained_model()

        # download the .bin file into local disk
        repo_id = self.repo_id
        fasttext_bin_filename = self.filepath_pretrained_model_bin
        print(f"Downloading {fasttext_bin_filename} from {repo_id}...")
        local_bin_path_fasttext = hf_hub_download(
            repo_id=repo_id, filename=fasttext_bin_filename)
        print(f"Downloaded to: {local_bin_path_fasttext}")

        # download the .npy file into local disk
        # Example for downloading .npy files if using gensim and they are needed alongside:
        # Get the directory where the .bin was downloaded
        local_dir = os.path.dirname(local_bin_path_fasttext)
        fasttext_npy_filename = self.filepath_pretrained_model_npy
        print(f"Downloading {fasttext_npy_filename} to {local_dir}...")
        local_npy_path = hf_hub_download(repo_id=repo_id, filename=fasttext_npy_filename)

        # retrieve the pretrained model
        self.pretrained_model = FastText.load(local_bin_path_fasttext)

        return self.pretrained_model
