# -*- coding:utf-8 -*-
import numpy as np
import re
import os


def load_file(filename):
    current_path = os.path.normpath(os.path.join(os.getcwd()))
    file_path = os.path.normpath(os.path.join(current_path, filename))
    if file_path.endswith(".py"):
        return eval(open(file_path, "rb").read())
    else:
        set_ = set()
        with open(file_path, "rb") as r:
            lines = r.readlines()
        for line in lines:
            set_.add(line.strip().decode("utf-8"))
        return set_


def vertibi(obs, states, trans_p, start_p, emit_p):
    delta = [{}]
    path = {}  # path[state_i] records the max probability path ending with state_i
    for state in states:  # Initialize the delta
        delta[0][state] = -np.log(max(start_p.get(state, 1e-18), 1e-18)) - np.log(max(emit_p[state].get(obs[0], 1e-18), 1e-18))
        path[state] = [state]
    for idx in range(1, len(obs)):
        delta.append({})
        tmp_path = {}
        for state_i in states:
            min_value = 1e9
            min_state = "S"  # !!! if every transition returns 0 it inclined that the previous one is 'S' and this one tend to be single
            for state_j in states:
                tmp_value = delta[idx - 1][state_j] - np.log(max(trans_p[state_j].get(state_i, 1e-18), 1e-18))  # dp transition function
                if tmp_value < min_value:
                    min_value = tmp_value
                    min_state = state_j

            delta[idx][state_i] = min_value - np.log(max(emit_p[state_i].get(obs[idx], 1e-18), 1e-18))
            tmp_path[state_i] = path[min_state] + [state_i]
        path = tmp_path

    min_end_state = 'E'
    if emit_p['M'].get(obs[-1], 1e-18) > emit_p['S'].get(obs[-1], 1e-18):
        for state in ('M', 'E'):
            if delta[len(obs) - 1][min_end_state] > delta[len(obs) - 1][state]:
                min_end_state = state
    else:
        for state in states:
            if delta[len(obs) - 1][min_end_state] > delta[len(obs) - 1][state]:
                min_end_state = state

    return delta, path[min_end_state]


class HMM(object):
    trans_p = load_file("prob_trans.py")
    start_p = load_file("prob_start.py")
    emit_p = load_file("prob_emit.py")
    near_char = load_file("near_char_tab.txt")

    def fetch_spans(self, sentence):  # get spans from sentence considering the words whether to be split
        start_, end_ = 0, 0
        while end_ < len(sentence) - 1:
            if sentence[end_:end_ + 2] not in self.near_char:  # check str(end_end_+1)
                yield sentence[start_: end_ + 1]  # take str(start_...end_) as a span
                start_ = end_ + 1
            end_ += 1

        yield sentence[start_:]  # take str(_start...'end of string') as a span

    def __cut(self, span):
        states = ('S', 'B', 'M', 'E')
        delta, path = vertibi(span, states, self.trans_p, self.start_p, self.emit_p)
        start_ = 0
        for idx in range(len(span)):
            tag = path[idx]
            if tag == 'B':
                start_ = idx
            elif tag == 'E':
                yield span[start_: idx + 1]
                start_ = idx + 1
            elif tag == 'S':
                yield span[idx]
                start_ = idx + 1
        if start_ < len(span):
            yield span[start_:]

    def cut(self, sentence, need_spans=False):  # API of HMM Chinese segmentation
        re_handle = re.compile(r"([\u4E00-\u9FD5a-zA-Z0-9+#&._%\-]+)", re.U)  # regex for split chinese
        re_skip = re.compile("(\r\n\s)", re.U)  # regex for split non chinese words
        blocks = re.split(re_handle, sentence)

        if need_spans is True:
            default_seg = self.fetch_spans
        else:
            default_seg = lambda x: (x,)
        for blk in blocks:
            if re.match(re_handle, blk):
                for span in default_seg(blk):
                    # print(span)
                    for word in self.__cut(span):
                        yield word


text = "???????????????????????????"
text3 = "???????????????"
text2 = "?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????"
test = HMM()
seg_list = test.cut(text3, need_spans=True)
print("/ ".join(seg_list))
