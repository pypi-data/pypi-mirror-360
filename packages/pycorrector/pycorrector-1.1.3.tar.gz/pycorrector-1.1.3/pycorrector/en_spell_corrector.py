# -*- coding: utf-8 -*-
"""
@author:XuMing(xuming624@qq.com)
@description: english correction
refer: http://norvig.com/spell-correct.html
"""

import gzip
import json
import operator
import os
from codecs import open
from typing import List

from loguru import logger

from pycorrector.utils.text_utils import is_alphabet_string
from pycorrector.utils.tokenizer import split_text_into_sentences_by_symbol

pwd_path = os.path.abspath(os.path.dirname(__file__))
# 英文拼写词频文件
default_en_dict_path = os.path.join(pwd_path, 'data/en.json.gz')


class EnSpellCorrector:
    def __init__(self, word_freq_dict: dict = None, custom_confusion_dict: dict = None, en_dict_path: str = None):
        """
        Init english spell corrector
        Args:
            word_freq_dict: Word freq dict, k=word, v=int(freq)
            custom_confusion_dict:
            en_dict_path:
        """
        if word_freq_dict and en_dict_path:
            raise ValueError('word_freq_dict and en_dict_path can not be set at the same time.')
        if word_freq_dict is None:
            word_freq_dict = {}
        if custom_confusion_dict is None:
            custom_confusion_dict = {}
        if not word_freq_dict and en_dict_path is None:
            en_dict_path = default_en_dict_path
        self.word_freq_dict = word_freq_dict
        self.custom_confusion_dict = custom_confusion_dict
        if en_dict_path and os.path.exists(en_dict_path):
            with gzip.open(en_dict_path, "rb") as f:
                all_word_freq_dict = json.loads(f.read())
                word_freq = {}
                for k, v in all_word_freq_dict.items():
                    # 英语常用单词3万个，取词频高于400
                    if v > 400:
                        word_freq[k] = v
                self.word_freq_dict = word_freq
                logger.debug("load en spell data: %s, size: %d" % (
                    en_dict_path, len(self.word_freq_dict)))
        # 词频总和
        self.sum_freq = sum(self.word_freq_dict.values())

    @staticmethod
    def edits1(word):
        """
        all edits that are one edit away from 'word'
        :param word:
        :return:
        """
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self, word):
        """
        all edit that are two edits away from 'word'
        :param word:
        :return:
        """
        return (e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))

    def known(self, word_freq_dict):
        """
        the subset of 'word_freq_dict' that appear in the dictionary of word_freq_dict
        :param word_freq_dict:
        :param limit_count:
        :return:
        """
        return set(w for w in word_freq_dict if w in self.word_freq_dict)

    def probability(self, word):
        """
        probability of word
        :param word:
        :return:float
        """
        return self.word_freq_dict.get(word, 0) / self.sum_freq

    def candidates(self, word):
        """
        generate possible spelling corrections for word.
        :param word:
        :return:
        """
        return self.known([word]) or self.known(self.edits1(word)) or self.known(self.edits2(word)) or {word}

    def correct_word(self, word):
        """
        most probable spelling correction for word
        :param word:
        :param mini_prob:
        :return:
        """
        candi_prob = {i: self.probability(i) for i in self.candidates(word)}
        sort_candi_prob = sorted(candi_prob.items(), key=operator.itemgetter(1))
        return sort_candi_prob[-1][0]

    @staticmethod
    def _get_custom_confusion_dict(path):
        """
        取自定义困惑集
        :param path:
        :return: dict, {variant: origin}, eg: {"交通先行": "交通限行"}
        """
        confusion = {}
        if path and os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#'):
                        continue
                    terms = line.split()
                    if len(terms) < 2:
                        continue
                    wrong = terms[0]
                    right = terms[1]
                    confusion[wrong] = right
        return confusion

    def set_en_custom_confusion_dict(self, path):
        """
        设置混淆纠错词典
        :param path:
        :return:
        """
        self.custom_confusion_dict = self._get_custom_confusion_dict(path)
        logger.debug('Loaded en spell confusion path: %s, size: %d' % (path, len(self.custom_confusion_dict)))

    def correct(self, sentence, include_symbol=True):
        """
        most probable spelling correction for text
        :param sentence: input query
        :param include_symbol: True, default
        :return: {'source': 'src', 'target': 'trg', 'errors': [(error_word, correct_word, position), ...]}
        example:
            cann you speling it? [['cann', 'can'], ['speling', 'spelling']]
        """
        text_new = ''
        details = []
        blocks = split_text_into_sentences_by_symbol(sentence, include_symbol=include_symbol)
        for w, idx in blocks:
            # 大于1个字符的英文词
            if len(w) > 1 and is_alphabet_string(w):
                if w in self.custom_confusion_dict:
                    corrected_item = self.custom_confusion_dict[w]
                else:
                    corrected_item = self.correct_word(w)
                if corrected_item != w:
                    begin_idx = idx
                    detail_word = (w, corrected_item, begin_idx)
                    details.append(detail_word)
                    w = corrected_item
            text_new += w
        # 以begin_idx排序
        details = sorted(details, key=operator.itemgetter(2))
        return {'source': sentence, 'target': text_new, 'errors': details}

    def correct_batch(self, sentences: List[str], **kwargs):
        """
        批量句子纠错
        :param sentences: 句子文本列表
        :param kwargs: 其他参数
        :return: list of {'source': 'src', 'target': 'trg', 'errors': [(error_word, correct_word, position), ...]}
        """
        return [self.correct(s, **kwargs) for s in sentences]
