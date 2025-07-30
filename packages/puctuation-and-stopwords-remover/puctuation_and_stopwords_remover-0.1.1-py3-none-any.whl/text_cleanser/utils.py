import string
import nltk
from nltk.corpus import stopwords

def remove_punc_and_stopwords(text_to_clean, output_format="text", lang="english"):
    """
    Removes punctuation and stopwords from the input text.
    
    Args:
        text_to_clean (str): The raw input text.
        output_format (str): 'list' (default) or 'word' for space-joined string output.
        lang (str): Language for stopwords (default: 'english').

    Returns:
        list or text (str): Cleaned text.
    """

    try:
        stop_words = set(stopwords.words(lang))
    except LookupError:
        nltk.download('stopwords')
        stop_words = set(stopwords.words(lang))

    if lang not in stopwords.fileids():
        return f"No support for language: {lang}"

    # Remove punctuation
    cleaned_punctuation_data = "".join([ch for ch in text_to_clean if ch not in string.punctuation])
    
    # Remove stopwords
    cleaned_data = [word for word in cleaned_punctuation_data.split() if word.lower() not in stop_words]

    return " ".join(cleaned_data) if output_format == "text" else cleaned_data
