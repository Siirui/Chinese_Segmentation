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
    path = {}             # path[state_i] records the max probability path ending with state_i
    for state in states:  # Initialize the delta
        delta[0][state] = -np.log(max(start_p.get(state, 1e-18), 1e-18)) - np.log(max(emit_p[state].get(obs[0], 1e-18), 1e-18))
        path[state] = [state]
    for idx in range(1, len(obs)):
        delta.append({})
        tmp_path = {}
        for state_i in states:
            min_value = 1e9
            min_state = "S"   #!!! if every trainstion returns 0 it inclined that the previous one is 'S' and this one tend to be single
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

    def fetch_spans(self, sentence):        # get spans from sentence considering the words whether to be split
        start_, end_ = 0, 0
        while end_ < len(sentence) - 1:
            if sentence[end_:end_ + 2] not in self.near_char:     # check str(end_end_+1)
                yield sentence[start_: end_ + 1]                  # take str(start_...end_) as a span
                start_ = end_ + 1
            end_ += 1

        yield sentence[start_:]                               # take str(_start...'end of string') as a span

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

    def cut(self, sentence, need_spans=False):                    # API of HMM Chinese segmentation
        re_handle = re.compile(r"([\u4E00-\u9FD5a-zA-Z0-9+#&\._%\-]+)", re.U)   # regex for split chinese
        re_skip = re.compile("(\r\n|\s)", re.U)  # regex for split non chinese words
        blocks = re.split(re_handle, sentence)

        if need_spans is True:
            default_seg = self.fetch_spans
        else:
            default_seg = lambda x: (x,)
        for blk in blocks:
            if re.match(re_handle, blk):
                for span in default_seg(blk):
                    print(span)
                    for word in self.__cut(span):
                        yield word



text = "这几天心里颇不宁静。今晚在院子里坐着乘凉，忽然想起日日走过的荷塘，在这满月的光里"
text3 = "鷁首徐回"
text2 = "，总该另有一番样子吧。月亮渐渐地升高了，墙外马路上孩子们的欢笑，已经听不见了；妻在屋里拍着闰儿，迷迷糊糊地哼着眠歌。我悄悄地披了大衫，带上门出去。沿着荷塘，是一条曲折的小煤屑路。这是一条幽僻的路；白天也少人走，夜晚更加寂寞。荷塘四面，长着许多树，蓊蓊郁郁的。路的一旁，是些杨柳，和一些不知道名字的树。没有月光的晚上，这路上阴森森的，有些怕人。今晚却很好，虽然月光也还是淡淡的。路上只我一个人，背着手踱着。这一片天地好像是我的；我也像超出了平常的自己，到了另一世界里。我爱热闹，也爱冷静；爱群居，也爱独处。像今晚上，一个人在这苍茫的月下，什么都可以想，什么都可以不想，便觉是个自由的人。白天里一定要做的事，一定要说的话，现在都可不理。这是独处的妙处，我且受用这无边的荷香月色好了。曲曲折折的荷塘上面，弥望的是田田的叶子。叶子出水很高，像亭亭的舞女的裙。层层的叶子中间，零星地点缀着些白花，有袅娜地开着的，有羞涩地打着朵儿的；正如一粒粒的明珠，又如碧天里的星星，又如刚出浴的美人。微风过处，送来缕缕清香，仿佛远处高楼上渺茫的歌声似的。这时候叶子与花也有一丝的颤动，像闪电般，霎时传过荷塘的那边去了。叶子本是肩并肩密密地挨着，这便宛然有了一道凝碧的波痕。叶子底下是脉脉的流水，遮住了，不能见一些颜色；而叶子却更见风致了。月光如流水一般，静静地泻在这一片叶子和花上。薄薄的青雾浮起在荷塘里。叶子和花仿佛在牛乳中洗过一样；又像笼着轻纱的梦。虽然是满月，天上却有一层淡淡的云，所以不能朗照；但我以为这恰是到了好处——酣眠固不可少，小睡也别有风味的。月光是隔了树照过来的，高处丛生的灌木，落下参差的斑驳的黑影，峭楞楞如鬼一般；弯弯的杨柳的稀疏的倩影，却又像是画在荷叶上。塘中的月色并不均匀；但光与影有着和谐的旋律，如梵婀玲上奏着的名曲。荷塘的四面，远远近近，高高低低都是树，而杨柳最多。这些树将一片荷塘重重围住；只在小路一旁，漏着几段空隙，像是特为月光留下的。树色一例是阴阴的，乍看像一团烟雾；但杨柳的丰姿，便在烟雾里也辨得出。树梢上隐隐约约的是一带远山，只有些大意罢了。树缝里也漏着一两点路灯光，没精打采的，是渴睡人的眼。这时候最热闹的，要数树上的蝉声与水里的蛙声；但热闹是它们的，我什么也没有。忽然想起采莲的事情来了。采莲是江南的旧俗，似乎很早就有，而六朝时为盛；从诗歌里可以约略知道。采莲的是少年的女子，她们是荡着小船，唱着艳歌去的。采莲人不用说很多，还有看采莲的人。那是一个热闹的季节，也是一个风流的季节。梁元帝《采莲赋》里说得好：于是妖童媛女，荡舟心许；鷁首徐回，兼传羽杯；欋将移而藻挂，船欲动而萍开。尔其纤腰束素，迁延顾步；夏始春余，叶嫩花初，恐沾裳而浅笑，畏倾船而敛裾。可见当时嬉游的光景了。这真是有趣的事，可惜我们现在早已无福消受了。于是又记起《西洲曲》里的句子：采莲南塘秋，莲花过人头；低头弄莲子，莲子清如水。今晚若有采莲人，这儿的莲花也算得“过人头”了；只不见一些流水的影子，是不行的。这令我到底惦着江南了。——这样想着，猛一抬头，不觉已是自己的门前；轻轻地推门进去，什么声息也没有，妻已睡熟好久了。"
test = HMM()
seg_list = test.cut(text, need_spans="True")
print("/ ".join(seg_list))