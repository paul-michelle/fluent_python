import sys
import re
from typing import (
    Dict, List, Tuple
)


class TxtExecutor:

    WORD_RE = re.compile(r'\w+')

    def __init__(self, file_path: str):
        self._file_path = file_path
        self._words_location: Dict = {}

    def get_words_location(self) -> Dict[str, List[Tuple[int]]]:
        with open(self._file_path, encoding='utf-8', mode='r') as file:
            for line_no, line in enumerate(file, start=1):
                for match in self.WORD_RE.finditer(line):
                    current_word = match.group()
                    row = line_no
                    column = match.start() + 1
                    self._words_location.setdefault(current_word, []).append((row, column))

        return self._words_location


if __name__ == '__main__':

    file_to_read = sys.argv[1]
    exe = TxtExecutor(file_to_read)
    words_dict = exe.get_words_location()

    for word in sorted(
            words_dict,
            key=str.upper
    ):
        print(f'{word} : {words_dict[word]}')
