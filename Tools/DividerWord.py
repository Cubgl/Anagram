import itertools


class DividerWord():
    def __init__(self, phrase):
        self.phrase = phrase
        self.mask_phrase = self.make_mask(phrase)

    def make_mask(self, phrase):
        mask = ''
        for ch in phrase:
            if ch.isalpha():
                mask += ch.lower()
        return mask

    def is_vowel(self, word):
        set_vowel = {'а', 'е', 'и', 'о', 'у', 'э', 'ы', 'ю', 'я'}
        for char in word:
            if char in set_vowel:
                return True
        return False

    def generate_split(self):
        for template in itertools.product(range(2), repeat=len(self.mask_phrase) - 1):
            first_part, second_part = '', ''
            template = (0,) + template
            for i in range(len(template)):
                if template[i] == 0:
                    first_part += self.mask_phrase[i]
                else:
                    second_part += self.mask_phrase[i]
            if not self.is_vowel(first_part) or not self.is_vowel(second_part):
                continue
            if second_part == '':
                second_part = first_part
            yield first_part, second_part

    def generate_three_split(self):
        for template in itertools.product(range(3), repeat=len(self.mask_phrase) - 1):
            first_part, second_part, three_part = '', '', ''
            for i in range(len(template)):
                if template[i] == 0:
                    first_part += self.mask_phrase[i]
                elif template[i] == 1:
                    second_part += self.mask_phrase[i]
                else:
                    three_part += self.mask_phrase[i]
            if not self.is_vowel(first_part) or not self.is_vowel(second_part) or \
                    not self.is_vowel(three_part):
                continue
            yield first_part, second_part, three_part


if __name__ == '__main__':
    divider = DividerWord('Перескокова Ольга')
    for one, two in divider.generate_split():
        print(one, two)
