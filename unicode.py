import string
import unicodedata

NORM_FORM_COMPOSED = 'NFC'
NORM_FORM_DECOMPOSED = 'NFC'

class TxtManager:

    @staticmethod
    def nfc_equal(text1: str, text2: str) -> bool:
        return unicodedata.normalize(NORM_FORM_COMPOSED, text1) \
               == unicodedata.normalize(NORM_FORM_COMPOSED, text2)

    @staticmethod
    def fold_equal(text1: str, text2: str) -> bool:
        return unicodedata.normalize(NORM_FORM_COMPOSED, text1).casefold() \
               == unicodedata.normalize(NORM_FORM_COMPOSED, text2).casefold()

    @staticmethod
    def shave_marks_ascii(text: str):
        norm_decomposed_text = unicodedata.normalize(NORM_FORM_DECOMPOSED, text)
        base_letter_is_ascii = False
        refined_letters = []

        for letter in norm_decomposed_text:
            if unicodedata.combining(letter) and base_letter_is_ascii:
                continue
            refined_letters.append(letter)
            if not unicodedata.combining(letter):
                base_letter_is_ascii = letter in string.ascii_letters

        shaved_text = ''.join(refined_letters)
        norm_composed_text = unicodedata.normalize(NORM_FORM_COMPOSED, shaved_text)
        return norm_composed_text


if __name__ == '__main__':
    textman = TxtManager()
    w1 = 'café'
    w2 = 'cafe\u0301'

    if not (w1 == w2) and textman.nfc_equal(w1, w1):
        print(w1, w2, sep='\t')                         # café	café
