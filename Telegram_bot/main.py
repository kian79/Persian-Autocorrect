from collections import Counter

import requests
import yaml
import numpy as np
import pandas as pd
from tqdm import tqdm
from hazm import *


class AutoCorrect:

    def __init__(self):
        self.data_path = 'data/wiki.txt'
        self.filtered_words_freq = self.get_data()

    def get_data(self):
        wiki_list = []
        with open(self.data_path, 'r') as txt_file:
            for line in txt_file:
                wiki_list.append(line)
        words = []
        for wiki in wiki_list:
            words.extend(word_tokenize(wiki))
        words_freq = Counter(words)
        filtered_words_freq = {key: val for key, val in words_freq.items() if val > 20}
        return filtered_words_freq

    persian_keyboard_list = list('ضصثقفغعهخحجچشسیبلاتنمکگ---ظطزرذدپو--')
    persian_keyboard = np.array(persian_keyboard_list).reshape(3, 12)

    def levenshtein(self, word1, word2):
        # print(word1, word2)
        ins_cost = 1
        del_cost = 1
        # rep_cost = replace_cost(ch1,ch2)
        if len(word1) < len(word2):
            word1, word2 = word2, word1

        # len(s1) >= len(s2)
        if len(word2) == 0:
            return len(word1)

        previous_row = range(len(word2) + 1)
        for i, c1 in enumerate(word1):
            current_row = [i + 1]
            for j, c2 in enumerate(word2):
                insertions = previous_row[
                                 j + 1] + ins_cost  # j+1 instead of j since previous_row and current_row are one character longer
                deletions = current_row[j] + del_cost  # than s2
                substitutions = previous_row[j] + self.replace_cost(c1, c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def replace_cost(self, ch1, ch2):
        if ch1 == "_" or ch2 == "_" or ch1 == 'ـ' or ch2 == 'ـ' or ch1 == 'ۀ' or ch2 == 'ۀ':
            return 2
        # if ch2=="آ":
        # ch2 == 'ا'
        if ch1 == "آ":
            ch1 = 'ا'
        if ch2 == "آ":
            ch2 = 'ا'
        if ch1 == "ژ":
            ch1 = 'ز'
        if ch2 == "ژ":
            ch2 = 'ز'
        if ch1 == "ئ":
            ch1 = 'س'
        if ch2 == "ئ":
            ch2 = 'س'
        if ch1 == "ة":
            ch1 = 'ت'
        if ch2 == "ة":
            ch2 = 'ت'
        if ch1 == "ؤ":
            ch1 = 'ش'
        if ch2 == "ؤ":
            ch2 = 'ش'
        if ch1 == "أ":
            ch1 = 'ل'
        if ch2 == "أ":
            ch2 = 'ل'
        if ch1 == "ء":
            ch1 = 'پ'
        if ch2 == "ء":
            ch2 = 'پ'
        if ch1 == "إ":
            ch1 = 'ب'
        if ch2 == "إ":
            ch2 = 'ب'
        if ch1 not in self.persian_keyboard_list or ch2 not in self.persian_keyboard_list:
            return 2
        # print(ch1,ch2)
        if ch1 == ch2:
            return 0
        row1, col1 = np.where(self.persian_keyboard == ch1)
        row2, col2 = np.where(self.persian_keyboard == ch2)
        row1, row2, col1, col2 = int(row1), int(row2), int(col1), int(col2)
        dis = ((row1 - row2) ** 2 + (col1 - col2) ** 2) ** 0.5
        if dis <= 1:
            return 0.5
        if dis <= 2:
            return 0.9
        if dis <= 3:
            return 1.5
        return 2

    def get_recoms(self, input_word):
        similarities = []
        for word in tqdm(self.filtered_words_freq.keys()):
            if len(input_word) - 2 <= len(word) <= len(input_word) + 2:
                similarities.append((word, self.levenshtein(word, input_word), 1 / self.filtered_words_freq[word]))
        similarities = sorted(similarities, key=lambda x: (x[1], x[2]), reverse=False)
        recoms = similarities[:3]
        words = []
        distance = []
        freq = []
        for recom in recoms:
            words.append(recom[0])
            distance.append(recom[1])
            freq.append(1 / recom[2])

        return words, distance, freq


def get_token(file_path='token.yml'):
    bot_token_file = open(file_path)
    bot_token = yaml.safe_load(bot_token_file)
    return bot_token['token']


class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}/"

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        response = requests.get(self.api_url + method, params)
        result = response.json()['result']
        return result

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        response = requests.post(self.api_url + method, params)
        return response

    def get_last_update(self):
        result = self.get_updates()
        if len(result) > 0:
            last_update = result[-1]
        else:
            last_update = None
        return last_update


if __name__ == '__main__':
    my_bot = BotHandler(get_token())
    offset = None
    auto_correct = AutoCorrect()
    while True:
        print(1)
        my_bot.get_updates(offset=offset)
        last_update = my_bot.get_last_update()
        last_update_id = last_update['update_id']
        last_chat_text = last_update['message']['text'].lower()
        last_chat_id = last_update['message']['chat']['id']
        last_chat_name = last_update['message']['chat']['first_name'].lower()
        last_chat_username = last_update['message']['chat']['username'].lower()
        print(f"last text : {last_chat_text} , last name : {last_chat_name}")
        offset = last_update_id + 1
        corrections = {}
        for word in last_chat_text.split():
            print(f'processing {word}')
            w, d, f = auto_correct.get_recoms(word)
            if d[0]:
                corrections[word] = [w]
        msg = []
        if len(corrections):
            if len(corrections) > 1:
                msg.append(f" اینارو اشتباه کردی : ")
            for word in corrections.keys():
                msg.append(f"{word} غلطه منظورت کدوم بوده؟")
                for w in corrections[word]:
                    for i in range(len(w)):
                        msg.append(f"{i+1}){w[i]}")
        else:
            msg.append("احسنت اشتباه تایپی نداری.")
        msg_str = "\n".join(map(str, msg))
        print(msg_str)
        my_bot.send_message(last_chat_id, msg_str)
        print(f"sent msg to {last_chat_name}")
