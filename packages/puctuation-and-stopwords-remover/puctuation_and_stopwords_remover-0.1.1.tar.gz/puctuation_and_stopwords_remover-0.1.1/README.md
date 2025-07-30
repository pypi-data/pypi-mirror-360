# Text Cleaner Module for NLP based projects

A simple Python package that removes punctuation and stopwords from text using `nltk` & `string`.

## Installation

First install the package:

```bash
pip install puctuation_and_stopwords_remover
```

## Usage Example

Import the module and use the `remove_punc_and_stopwords` function:

```python
from puctuation_and_stopwords_remover import remove_punc_and_stopwords

text = "This is an example sentence, with punctuation and stopwords!"

# Remove punctuation and stopwords, return as text
cleaned_text = remove_punc_and_stopwords(text)
print(cleaned_text)
# Output: example sentence punctuation stopwords

# Remove punctuation and stopwords, return as list
cleaned_list = remove_punc_and_stopwords(text, output_format="list")
print(cleaned_list)
# Output: ['example', 'sentence', 'punctuation', 'stopwords']

# Specify a different language (if supported)
cleaned_text_spanish = remove_punc_and_stopwords("Este es un ejemplo de texto.", lang="spanish")
print(cleaned_text_spanish)
```

**Function signature:**
```python
def remove_punc_and_stopwords(text_to_clean, output_format="text", lang="english"):
    """
    Removes punctuation and stopwords from the input text.

    Args:
        text_to_clean (str): The raw input text.
        output_format (str): 'text' (default) or 'list' for list output.
        lang (str): Language for stopwords (default: 'english').

    Returns:
        str or list: Cleaned text.
    """
```
