# A dedicated file for data/model loading helpers

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
    # f'data.{subfolder}' specifies the nested package for data
    with resources.path(f'balinese_nlp.textpreprocessor.data.{subfolder}', filename) as p:
        return str(p)


def load_balinese_stop_words():
    """Loads the list of Balinese stop words."""
    file_path = get_package_data_path(
        'stopwords', 'data.txt')
    with open(file_path, 'r', encoding='utf-8') as file:
        stop_words = sorted([term.strip().lower()
                            for term in file.readlines()])
    return list(dict.fromkeys(stop_words))  # Remove duplicates


def load_balinese_normalization_dict():
    """Loads the Balinese normalization dictionary."""
    file_path = get_package_data_path(
        'normalizedwords', 'data.xlsx')
    df = pd.read_excel(file_path)
    return {
        'normalized': list(df['normalized'].str.lower()),
        'unnormalized': list(df['unormalized'].str.lower())
    }


def load_balinese_lemmatization_file():
    """
    Function to load Balinese lemmatization file
    """
    file_path = get_package_data_path(
        'lemmatization', 'balivocab.txt')
    vocabs = []
    with open(file_path) as f:
        vocabs = f.read().splitlines()
    return vocabs
