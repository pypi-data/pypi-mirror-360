import os
import pandas as pd
from importlib import resources

# Helper function to get the path to a data file within the package


def get_package_data_path(filename):
    """
    Returns the absolute path to a data file located within the package.
    Uses importlib.resources for robust path resolution.
    """
    # Use resources.path to get a context manager that provides the file path
    # 'balinese_nlp' is the top-level package name
    with resources.path(f'balinese_nlp.ner.data', filename) as p:
        return str(p)


def load_bali_vocabs():
   """
   Loads the balinese vocabs to helps the rule-based model learns
   """
   file_path = get_package_data_path('BaliVocab.txt')
   with open(file_path, 'r', encoding="utf8") as file:
         baliVocabs = sorted([
             term.strip('\n') for term in file.readlines()
         ])
   return baliVocabs


def load_sansekerta_vocabs():
   """
   Loads the sansekerta vocabs to helps the rule-based model learns
   """
   file_path = get_package_data_path('sansekertavocab.txt')
   with open(file_path, 'r', encoding="utf8") as file:
         sansekertavocabs = sorted([
             term.strip('\n') for term in file.readlines()
         ])
   return sansekertavocabs


   
   

   


  

