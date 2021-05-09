import os
from pprint import pprint

from Tools.DividerWord import DividerWord

PATH_FOR_DATA = '../Dict'
FILENAME_DICT = 'slovar.TXT'
FILENAME_BINARY_DICT = 'dictionary.dat'
FILENAME_BINARY_WORDS = 'words.dat'


class Solver():
    def __init__(self, phrase):
        self.phrase = phrase
        self.data = AnagramKnow()
        self.divider = DividerWord(phrase)
        self.result = {}

    def solve(self, count_words=2):
        for first, second in self.divider.generate_split():
            # print(first, second)
            sorted_first = ''.join(sorted(first))
            sorted_second = ''.join(sorted(second))
            if self.data.know_mask(sorted_first) and self.data.know_mask(sorted_second):
                key = frozenset({sorted_first, sorted_second})
                if key not in self.result:
                    self.result[key] = (self.phrase, [self.data.get_word(sorted_first),
                                                      self.data.get_word(sorted_second)])
            else:
                if len(sorted_first) <= 3 and self.data.know_mask(sorted_first):
                    self.small_divider = DividerWord(second)
                    for one, two in self.small_divider.generate_split():
                        sorted_one = ''.join(sorted(one))
                        sorted_two = ''.join(sorted(two))
                        if self.data.know_mask(sorted_one) and self.data.know_mask(sorted_two):
                            key = frozenset({sorted_first, sorted_one, sorted_two})
                            if key not in self.result:
                                self.result[key] = (self.phrase, [self.data.get_word(sorted_first),
                                                                  self.data.get_word(sorted_one),
                                                                  self.data.get_word(sorted_two)])
                elif len(sorted_second) <= 3 and self.data.know_mask(sorted_second):
                    self.small_divider = DividerWord(first)
                    for one, two in self.small_divider.generate_split():
                        sorted_one = ''.join(sorted(one))
                        sorted_two = ''.join(sorted(two))
                        if self.data.know_mask(sorted_one) and self.data.know_mask(sorted_two):
                            key = frozenset({sorted_one, sorted_two, sorted_second})
                            if key not in self.result:
                                self.result[key] = (self.phrase, [self.data.get_word(sorted_one),
                                                                  self.data.get_word(sorted_two),
                                                                  self.data.get_word(sorted_second)])
        if count_words == 2:
            return
        for first, second, third in self.divider.generate_three_split():
            if second == '':
                second = first
            if third == '':
                third = first
            sorted_first = ''.join(sorted(first))
            sorted_second = ''.join(sorted(second))
            sorted_third = ''.join(sorted(third))
            if self.data.know_mask(sorted_first) and self.data.know_mask(sorted_second) and \
                    self.data.know_mask(sorted_third):
                key = frozenset({sorted_first, sorted_second, sorted_third})
                if key not in self.result:
                    self.result[key] = (self.phrase, [self.data.get_word(sorted_first),
                                                      self.data.get_word(sorted_second),
                                                      self.data.get_word(sorted_third)])


class AnagramKnow():
    def __init__(self):
        self.dict_anagram_simple = DictAnagramSimple()
        self.dict_len_groups = DictLenGroups(self.dict_anagram_simple.dictionary).dict_for_len_group

    def is_anagram(self, word):
        mask = ''.join(sorted(word))
        return mask in self.dict_anagram_simple.dictionary and \
               word in self.dict_anagram_simple.dictionary[mask]

    def get_anagram(self, word):
        mask = ''.join(sorted(word))
        return self.dict_anagram_simple.dictionary.get(mask)

    def know_word(self, word):
        return word in self.dict_anagram_simple.words

    def know_mask(self, mask):
        return mask in self.dict_anagram_simple.dictionary

    def get_group(self, number):
        return self.dict_len_groups.get(number)


class DictAnagramSimple():
    def __init__(self):
        self.dictionary = {}
        self.words = set()
        if os.path.exists(PATH_FOR_DATA + '/' + FILENAME_BINARY_DICT) and \
            os.path.exists(PATH_FOR_DATA + '/' + FILENAME_BINARY_WORDS):
            self.load_dict_from_binary_file()
            self.load_words_from_binary_file()
        else:
            self.load_words_from_textfile()
        self.dict_no_repeat = {}
        self.create_dict_no_repeat()

    def load_words_from_textfile(self):
        with open(PATH_FOR_DATA + '/' + FILENAME_DICT, 'r', encoding='utf-8') as textfile:
            for line in textfile:
                word = line.strip()
                self.words.add(word)
                mask = ''.join(sorted(word))
                if mask not in self.dictionary:
                    self.dictionary[mask] = set()
                self.dictionary[mask].add(word)

    def create_dict_no_repeat(self):
        for mask, group in self.dictionary.items():
            if len(group) > 1:
                self.dict_no_repeat[mask] = group

    def print_into_file(self, filename, dictionary):
        with open(filename, 'w', encoding='utf-8') as textfile:
            for mask, group in dictionary.items():
                sorted_list = sorted(list(group))
                print(f'{mask}:', *sorted_list, file=textfile)

    def print_dict_to_binary_file(self):
        with open(PATH_FOR_DATA + '/' + FILENAME_BINARY_DICT, 'wb') as binary_file:
            binary_file.write(bytes(str(self.dictionary).encode()))

    def print_words_to_binary_file(self):
        with open(PATH_FOR_DATA + '/' + FILENAME_BINARY_WORDS, 'wb') as binary_file:
            binary_file.write(bytes(str(self.words).encode()))

    def load_dict_from_binary_file(self):
        with open(PATH_FOR_DATA + '/' + FILENAME_BINARY_DICT, 'rb') as binary_file:
            data_dict = binary_file.read()
        self.dictionary = eval(f'{data_dict.decode()}')

    def load_words_from_binary_file(self):
        with open(PATH_FOR_DATA + '/' + FILENAME_BINARY_WORDS, 'rb') as binary_file:
            data_words = binary_file.read()
        self.words = eval(f'{data_words.decode()}')

class DictLenGroups():
    def __init__(self, simple_dict):
        self.dict_for_len_group = {}
        self.create_dict_for_len_group(simple_dict)

    def create_dict_for_len_group(self, simple_dict):
        for mask, group in simple_dict.items():
            count = len(group)
            if count not in self.dict_for_len_group:
                new_dict = dict()
                new_dict[mask] = group
                self.dict_for_len_group[count] = new_dict
            else:
                cur_dict = self.dict_for_len_group[count]
                cur_dict[mask] = group

    def print_into_file(self, filename, dictionary):
        with open(filename, 'w', encoding='utf-8') as textfile:
            counts = sorted(dictionary.keys(), reverse=True)
            for elem in counts:
                print(f'Количество слов в группе: {elem}', file=textfile)
                for mask, group in dictionary[elem].items():
                    sorted_list = sorted(list(group))
                    print(f'{mask}:', *sorted_list, file=textfile)
                print(file=textfile)


if __name__ == '__main__':
    my = AnagramKnow()
    print(my.get_anagram('американское'))
