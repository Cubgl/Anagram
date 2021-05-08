import random

from data import db_session
from data.enigma import Enigma


class TheGame:
    def __init__(self):
        self.db_sess = db_session.create_session()
        random.seed()
        self.score = 0
        self.pos_in_game = 0
        self.count_tasks = 5
        self.tasks = []
        self.load_tasks()
        self.used = [False] * len(self.tasks)
        self.attempts = [None] * len(self.tasks)
        self.indexes = self.make_new_game()
        self.take_task()
        self.sed_phrases = [
            'К сожаленью, это неправильный ответ.', 'Увы, но это неверно.',
            'Не удалось угадать.', 'Этот ответ я не могу принять как правильный.',
            'Возможно, в следующий раз получится лучше, но пока это "холостой выстрел".',
            'Нет, это не так.', "Правильный ответ содержит другое слово", "Неверно!"
        ]
        self.ok_phrases = [
            'Совершенно верно!', 'Правильно!', 'Да, это правильный ответ!'
            'Умница, это точный ответ.', 'Молодец, этот ответ подходит.',
            'Это верное слово.', 'ОК, ответ принят.', 'Совершенно точно!',
            'Да, это так.', 'Прямо в "яблочко"!', "Верно!"
        ]

    def get_phrase_for_wrong_answer(self):
        return random.choice(self.sed_phrases)

    def get_phrase_for_ok_answer(self):
        return random.choice(self.ok_phrases)

    def load_tasks(self):
        for enigma in self.db_sess.query(Enigma).all():
            self.tasks.append(enigma)

    def get_difficult(self, task):
        if task.good_answers == 0 and task.bad_answers == 0:
            return 1
        return task.difficult

    def make_new_game(self):
        numbers = [i for i in range(len(self.tasks)) if not self.used[i]]
        while len(numbers) < self.count_tasks:
            number = random.randint(0, len(self.tasks) - 1)
            while number in numbers:
                number = random.randint(0, len(self.tasks) - 1)
            numbers.append(number)
        if len(numbers) > self.count_tasks:
            random.shuffle(numbers)
            numbers = numbers[:5]
        for_sort = []
        for index in numbers:
            for_sort.append((index, self.get_difficult(self.tasks[index])))
        for_sort.sort(key=lambda x: x[1])
        print(for_sort)
        return list(map(lambda x: x[0], for_sort))

    def take_task(self):
        self.cur_index = self.indexes[0]
        self.used[self.cur_index] = True
        self.pos_in_game += 1
        self.indexes = self.indexes[1:]
        print('indexes = ', self.indexes)

    def the_end(self):
        return self.pos_in_game == self.count_tasks

    def get_question(self):
        return [line.strip() for line in self.tasks[self.cur_index].question.split('|')]

    def checking_answer(self, user_answer):
        return self.tasks[self.cur_index].check_answer(user_answer)

    def get_subquestion(self):
        return self.tasks[self.cur_index].subquestion

    def get_subanswer(self):
        return self.tasks[self.cur_index].subanswer

    def get_helper(self):
        return self.tasks[self.cur_index].helper

    def set_stats(self, success):
        if success:
            self.tasks[self.cur_index].good_answers += 1
            self.score += 1
        else:
            self.tasks[self.cur_index].bad_answers += 1
        self.tasks[self.cur_index].difficult = 1 - self.tasks[self.cur_index].good_answers / (
                self.tasks[self.cur_index].good_answers + self.tasks[self.cur_index].bad_answers)
        self.db_sess.commit()
