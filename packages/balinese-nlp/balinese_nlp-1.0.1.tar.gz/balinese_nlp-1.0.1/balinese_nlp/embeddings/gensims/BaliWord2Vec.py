from balinese_nlp.embeddings.BasePretrained import BasePretrained
from gensim.models import Word2Vec
from huggingface_hub import hf_hub_download


class BaliWord2Vec(BasePretrained):

    def __init__(self, huggingface_repo_ID, pretrained_model_filename="200_word2vec_model.bin"):
        super().__init__(
            huggingface_repo_ID=huggingface_repo_ID
        )
        self.filepath_pretrained_model = f"Word2Vec/{pretrained_model_filename}"

    def load_pretrained_model(self):
        super().load_pretrained_model()

        # download the .bin file into local disk
        repo_id = self.repo_id
        word2vec_bin_filename = self.filepath_pretrained_model
        local_bin_path_word2vec = hf_hub_download(
            repo_id=repo_id, filename=word2vec_bin_filename)

        # retrieve the pretrained model
        self.pretrained_model = Word2Vec.load(local_bin_path_word2vec)

        return self.pretrained_model
