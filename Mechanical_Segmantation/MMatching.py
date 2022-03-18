import re
import os

re_dictionary = re.compile('^(.+?)( [0-9]+)?( [a-z]+)?$', re.U)
re_handle = re.compile(r"([\u4E00-\u9FD5a-zA-Z0-9+#&._%\-]+)", re.U)  # regex for split chinese
re_skip = re.compile("(\r\n\s)", re.U)  # regex for split non chinese words

class MMatching(object):

    def __init__(self):
        self.total = 0
        self.dict = {}

    def load_dictionary(self, dict_name="dict.txt.small"):
        current_path = os.getcwd()
        dict_path = os.path.normpath(os.path.join(current_path, "./../Dictionary/", dict_name))
        with open(dict_path, "rb") as r:
            lines = r.readlines()
        for line in lines:
            try:
                line = line.strip()
                line = line.decode('utf-8').lstrip('\ufeff')
            except UnicodeDecodeError:
                raise ValueError('dictionary file %s must be utf-8' % dict_name)
            if not line:
                continue

            word, freq, tag = re_dictionary.match(line).groups()
            if freq is not None:
                freq = freq.strip()
            if tag is not None:
                tag = tag.strip()

            freq = int(freq)
            self.dict[word] = freq
            self.total += freq

    def forward_max_matching(self, sentence, max_length=5):
        idx = 0
        while idx < len(sentence):
            length = max_length
            while length >= 2:
                if idx + length - 1 < len(sentence):
                    word = sentence[idx:idx + length]
                    if word in self.dict:
                        yield word
                        idx += length - 1
                        break
                length -= 1
            if length == 1:
                yield sentence[idx]
            idx += 1

    def forward_min_matching(self, sentence, max_length=5):
        idx = 0
        while idx < len(sentence):
            length = 2
            while length <= max_length:
                if idx + length - 1 < len(sentence):
                    word = sentence[idx:idx + length]
                    if word in self.dict:
                        yield word
                        idx += length - 1
                        break
                length += 1
            if length > max_length:
                yield sentence[idx]
            idx += 1

    def backward_max_matching(self, sentence, max_length=5):
        idx = len(sentence) - 1
        while idx >= 0:
            length = max_length
            while length >= 2:
                if idx - length + 1 >= 0:
                    word = sentence[idx-length + 1:idx + 1]
                    if word in self.dict:
                        yield word
                        idx -= length - 1
                        break
                length -= 1
            if length == 1:
                yield sentence[idx]
            idx -= 1

    def backward_min_matching(self, sentence, max_length=5):
        idx = len(sentence) - 1
        while idx >= 0:
            length = 2
            while length <= max_length:
                if idx - length + 1 >= 0:
                    word = sentence[idx-length + 1:idx + 1]
                    if word in self.dict:
                        yield word
                        idx -= length - 1
                        break
                length += 1
            if length > max_length:
                yield sentence[idx]
            idx -= 1

    def adjacent_matching(self, sentence):
        idx = 0
        while idx < len(sentence) - 1:
            word_list = []
            for key, value in self.dict.items():
                if sentence[idx:idx+2] in key:
                    word_list.append(key)
            if len(word_list) == 0:
                yield sentence[idx]
                idx += 1
                continue
            end_ = idx + 1
            while end_ + 2 < len(sentence) and sentence[idx: (end_ + 1) + 1] in word_list:
                end_ += 1
            yield sentence[idx: end_ + 1]
            idx = end_ + 1

    def cut(self, sentence, type_="ForwardMaxMatching", max_length=5):
        blocks = re.split(re_handle, sentence)

        if type_ == "ForwardMaxMatching":
            default_seg = self.forward_max_matching
        if type_ == "ForwardMinMatching":
            default_seg = self.forward_min_matching
        elif type_ == "BackwardMaxMatching":
            default_seg = self.backward_max_matching
        elif type_ == "BackwardMinMatching":
            default_seg = self.backward_min_matching

        for blk in blocks:
            if re.match(re_handle, blk):
                if type_ == "AdjacentMatching":
                    for word in self.adjacent_matching(blk):
                        yield word
                elif type_ == "BackwardMaxMatching" or type_ == "BackwardMinMatching":
                    word_list = []
                    for word in default_seg(blk, max_length):
                        word_list.append(word)
                        # yield word
                    for idx in range(1, len(word_list)):
                        yield word_list[-idx]
                    yield word_list[0]
                else:
                    for word in default_seg(blk, max_length):
                        yield word


text2 = "这块肉的确切得不错"
text3 = "为奥运会健儿加油啊"
text = "他将来上海"
test = MMatching()
test.load_dictionary()
print("ForwardMaxMatching")
seg_list = test.cut(text3, type_="ForwardMaxMatching")
print("/ ".join(seg_list))
print("ForwardMinMatching")
seg_list = test.cut(text3, type_="ForwardMinMatching")
print("/ ".join(seg_list))
print("BackwardMaxMatching")
seg_list = test.cut(text3, type_="BackwardMaxMatching")
print("/ ".join(seg_list))
print("BackwardMinMatching")
seg_list = test.cut(text3, type_="BackwardMinMatching")
print("/ ".join(seg_list))
print("AdjacentMatching")
seg_list = test.cut(text3, type_="AdjacentMatching")
print("/ ".join(seg_list))