import os
import pandas as pd
from importlib import resources

# Helper function to get the path to a data file within the package


def get_package_data_path(subfolder, filename):
    """
    Returns the absolute path to a data file located within the package.
    Uses importlib.resources for robust path resolution.
    """
    # Use resources.path to get a context manager that provides the file path
    # 'balinese_nlp' is the top-level package name
    with resources.path(f'balinese_nlp.postag.data.{subfolder}', filename) as p:
        return str(p)

def load_pretrained_hmm_model():
    file_path = get_package_data_path(subfolder='HMM', filename='hmmmodel.txt')
    pretrained_hmm_model = open(file_path, 'r')
    return pretrained_hmm_model