# setup.py
from setuptools import setup, find_packages
import os

# Function to read the README.md content


def read_readme():
    try:
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""


setup(
    name='balinese_nlp',  # The name users will use to pip install
    version='1.0.2',  # last version v1.0.2
    # Automatically finds 'balipkg' and any sub-packages
    packages=find_packages(),

    # Crucial for including non-code files like models and data
    package_data={
        'balinese_nlp': [
            'models/*.pkl',
            'models/*.pt',  # Include if you have PyTorch models
            # Include if you have other binary models (e.g., for spaCy)
            'models/*.bin',
            'feature_extractor/data/booster_words.txt',
            'feature_extractor/data/negation_words.txt',
            'ner/data/BaliVocab.txt',
            'ner/data/sansekertavocab.txt',
            'ner/data/sansekertavocab.txt',
            'postag/data/HMM/hmmmodel.txt',
            'textpreprocessor/data/lemmatization/balivocab.txt',
            'textpreprocessor/data/normalizedwords/data.xlsx',
            'textpreprocessor/data/stopwords/data.txt',
        ],
    },
    include_package_data=True,  # Essential for using package_data

    install_requires=[
        'gensim==4.3.3',
        'huggingface-hub==0.33.0',
        'scikit-learn==1.2.1',
        'matplotlib==3.6.3',
        'matplotlib-inline==0.1.6',
        'nltk',
        'transformers==4.33.3',
        'torch==2.3.0',
        'pandas==1.5.3',
        'jaro-winkler==2.0.3',
        'sklearn-crfsuite==0.3.6',
        'hmmlearn==0.3.0'
    ],
    entry_points={
        # Optional: If you want to provide command-line scripts
        # 'console_scripts': [
        #     'analyze-balinese-text=balipkg.cli:main_function',
        # ],
    },

    author='I Made Satria Bimantara',
    author_email='satriabimantara.md@gmail.com',
    description='A comprehensive Python package tools for Balinese Natural Language Processing',
    long_description=read_readme(),  # Reads content from README.md
    long_description_content_type='text/markdown',  # Specify content type for PyPI
    keywords=['Balinese', 'NLP', 'Text Preprocessing', 'Semantic Feature Extraction',
              'Embedding Models', 'Narrative Analysis', 'NER', 'POS Tagging', 'Summarization'],
    classifiers=[
        # Or 4 - Beta, 5 - Production/Stable
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
        # Balinese is not a specific classifier, but Bahasa Indonesia is close
        'Natural Language :: Indonesian',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.8',  # Minimum Python version
)
