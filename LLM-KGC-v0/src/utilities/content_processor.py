import nltk
from nltk import pos_tag
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.stem import SnowballStemmer, RegexpStemmer
from nltk.corpus import stopwords
import string
import hashlib
# nltk.download('punkt') # For sentence tokenizer
# nltk.download('wordnet') # For lemmatizer
# nltk.download('omw-1.4') # For lemmatizer
# nltk.download('averaged_perceptron_tagger') # For pos_tag
# nltk.download('stopwords')

import sys
from pathlib import Path

# Add packages to sys.path
UTILITIES_RELATIVE_PATH = '../'
UTILITIES_ABSOLUTE_PATH = str((Path(__file__).parent / UTILITIES_RELATIVE_PATH).resolve())
if UTILITIES_ABSOLUTE_PATH not in sys.path:
    sys.path.append(UTILITIES_ABSOLUTE_PATH)


import re

LEMMATISER = WordNetLemmatizer()
STEMMER = SnowballStemmer("english")

STOPWORDS_EN = set(stopwords.words('english'))
PUNCTUATION = string.punctuation





def detokenise_text(tokens: list) -> str:
    """
    Detokenise a list of tokens
    """
    return TreebankWordDetokenizer().detokenize(tokens)

def remove_stopwords(tokens: list) -> list:
    """
    Remove stopwords from a list of tokens
    """
    return [token for token in tokens if token.lower() not in STOPWORDS_EN]

def remove_punctuation(tokens: list) -> list:
    """
    Remove punctuation from a list of tokens
    """
    return [token for token in tokens if token not in PUNCTUATION]


def sanitise_iri(label: str) -> str:
    """
    Senatise a IRL label
    """

    if label == "" or label is None:
        print("sanitise_iri: The label is empty")
        return "_"

    # Define the allowed characters: letters, numbers, underscores, dashes, and dots
    label = re.sub(r' ', '_', label)
    label = re.sub(r'[^A-Za-z0-9._-]', '', label)
    return label

def hash_md5(s):
    return hashlib.md5(s.encode()).hexdigest()


def tokenise_text(text: str) -> list:
    """
    Tokenise a given sentence
    """
    return word_tokenize(text)


def get_pos(tokens: list) -> list:
    """
    Get the token and POS pairs of a sentence
    """
    token_pos_pairs = pos_tag(tokens)
    return [pair[1] for pair in token_pos_pairs]

def stem_text(tokens: list) -> list:
    """
    Stem a given sentence
    """
    return [STEMMER.stem(token) for token in tokens]


def lemmatise_text(tokens: list, pos=None) -> list:
    """
    Lemmatise a given sentence
    """

    # Lemmatize
    if pos:
        # Function to convert NLTK POS tagging to WordNet POS tagging
        to_wordnet_pos = lambda t: 'a' if t == 'j' else (t if t in ['n', 'v', 'r'] else 'n') # COMP4650 Lab 1

        lemmatised_sentence_tokens = [(LEMMATISER.lemmatize(token.lower(), to_wordnet_pos(pos[0].lower()))) 
                               for token, pos in zip(tokens, pos)] # COMP4650 Lab 1
    else:
        lemmatised_sentence_tokens = [(LEMMATISER.lemmatize(token.lower())) 
                               for token in tokens]
        
    return lemmatised_sentence_tokens


# def stem_text(tokens: list) -> list:
#     """
#     Stem a given sentence
#     """
#     return [STEMMER.stem(token) for token in tokens]


def check_equal_fuzzy(a, b):
    a = str(a)
    b = str(b)

    tokenised_a = tokenise_text(a)
    tokenised_b = tokenise_text(b)

    normalised_a = lemmatise_text(tokenised_a, pos=None)
    normalised_b = lemmatise_text(tokenised_b, pos=None)

    normalised_a = " ".join(normalised_a)
    normalised_b = " ".join(normalised_b)

    return (normalised_a in normalised_b) or (normalised_b in normalised_a)



def find_existence_in_sentence(sentence: dict | str, term: str) -> list:
    """
    Find all the starting indices of a term in a sentence
    """
    if isinstance(sentence, str):
        text = sentence
    else:
        text = sentence["text"]

    if term == "" or term is None or text == "" or text is None:
        print()
        print(term)
        print(text)
        print()
        raise ValueError("find_existence_in_sentence: The term or text is empty")

    indices = set()

    # Tokenise the text and term
    text_tokenised = tokenise_text(text)
    term_tokenised = tokenise_text(term)


    # (1) Check if the lemmatised term exists in the lemmatised text

    text_normalised = lemmatise_text(text_tokenised, pos=None)
    term_normalised = lemmatise_text(term_tokenised, pos=None)

    # Find all the starting indices of the term in the text, (inspired by Copilot)
    i = 0
    while i < len(text_normalised):
        if text_normalised[i:i+len(term_normalised)] == term_normalised: # i+len(term_lemmatised) can be out of range
            indices.add(i)
            i += len(term_normalised)
        else:
            i += 1

    return list(indices)


def check_existence_in_sentence(sentence: dict | str, term: str) -> bool:
    """
    Check if a term exists in a sentence
    """

    # Assertion is included in the function
    indices = find_existence_in_sentence(sentence, term)
    
    if len(indices) > 0:
        return True
    else:
        return False
    



def check_equal(a, b):
    a = str(a)
    b = str(b)

    tokenised_a = tokenise_text(a)
    tokenised_b = tokenise_text(b)

    normalised_a = lemmatise_text(tokenised_a, pos=None)
    normalised_b = lemmatise_text(tokenised_b, pos=None)

    return " ".join(normalised_a) == " ".join(normalised_b)



def annotate_sentence(sentence: dict, label: str, start_tag="@@", end_tag="## ") -> str:
    """
    Annotate all the occurrences of a label in a sentence
    """
    text = sentence["text"]
    label_tokenised = tokenise_text(label)
    text_tokenised = tokenise_text(text)

    # Assertion is included in the function
    indices = find_existence_in_sentence(sentence, label)

    if indices == []:
        raise ValueError("annotate_sentence: The label does not exist in the sentence")
    
    # Annotate the text
    annotated_text = []
    start_index = 0
    for index in indices:
        annotated_text += text_tokenised[start_index:index] + [start_tag] + text_tokenised[index:index+len(label_tokenised)] + [end_tag]
        start_index = index+len(label_tokenised)

    annotated_text += text_tokenised[start_index:]

    return TreebankWordDetokenizer().detokenize(annotated_text)

    

def annotate_paragraph_single_term(sentence: dict, paragraph: dict, term: str, start_tag="@@", end_tag="## ") -> str:
    """
    Output a paragraph where all the occurrences of a specific term in a specific sentence are annotated
    """

    # Annotate the sentence
    annotated_sentence = annotate_sentence(sentence, term, start_tag=start_tag, end_tag=end_tag)

    output_paragraph = []

    # Get the text of the paragraph
    for sen in paragraph["sentences"]:
        if sen["iri"] == sentence["iri"]:
            output_paragraph.append(annotated_sentence)
        else:
            output_paragraph.append(sen["text"])

    return " ".join(output_paragraph)





if __name__ == "__main__":
    
    # Test the function (Generated by Github Copilot)
    sentence = "The quick brown foxes are jumping over the lazy dogs. This are embeddings."
    token = tokenise_text(sentence)
    lemmatise_text_1 = lemmatise_text(token)
    lemmatise_text_2 = lemmatise_text(token, get_pos(token))
    print(lemmatise_text_1)
    print(lemmatise_text_2)


    # Test the function (Generated by Github Copilot)
    label = "The quick ##$$ brown foxes are --- jumping over the &%^&*() lazy dogs."
    valid_label = sanitise_iri(label)
    print(valid_label)

    # Test cases is generated by Github Copilot
    sentence = {}
    sentence["text"] = "The quick quick brown fox jumped over the lazy dog. Quick quick!!!!"
    label = "quick"
    print(annotate_sentence(sentence, label))