import sys
import re
import collections


class TxtExecutor:

    WORD_RE = re.compile(r'\w+')

    def __init__(self, fp: str):
        self._file_path = fp
        self._words_locations = collections.defaultdict(list)
        self._words_counter = collections.Counter()

    def get_words_location(self):
        with open(self._file_path, encoding='utf-8', mode='r') as f:
            for line_no, line in enumerate(f):
                for match in self.WORD_RE.finditer(line):
                    this_word = match.group()
                    row = line_no + 1
                    column = match.start() + 1
                    location = (row, column)
                    self._words_locations[this_word].append(location)

        return self._words_locations

    def get_words_frequency(self):
        with open(self._file_path, encoding='utf-8', mode='r') as f:
            for line in f.readlines():
                list_of_words = line.strip().split(' ')
                self._words_counter.update(list_of_words)
        return self._words_counter


if __name__ == '__main__':

    file_to_scan_path = sys.argv[1]
    executor = TxtExecutor(file_to_scan_path)

    words_locations = executor.get_words_location()
    for word in sorted(
        words_locations,
        key=str.upper
    ):
        print(word, words_locations[word])

    words_frequency = executor.get_words_frequency()
    for item in words_frequency.items():
        print(f'{item[0]} ---> {item[1]}')
