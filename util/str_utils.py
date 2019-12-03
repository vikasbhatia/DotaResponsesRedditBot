import string

PUNCTUATION_TRANS = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
WHITESPACE_TRANS = str.maketrans(string.whitespace, ' ' * len(string.whitespace))


def preprocess_text(text):
    """Method for pre-processing the given response text.
    It:
    * changes to lowercase
    * removes trailing and leading spaces
    * removes all punctuations
    * removes double spaces

    :param text: the text to be cleaned
    :return: cleaned text
    """
    text = text.strip().lower()

    text = text.translate(PUNCTUATION_TRANS)
    text = text.translate(WHITESPACE_TRANS)

    while '  ' in text:
        text = text.replace('  ', ' ')

    return text
