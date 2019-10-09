import re
import sys

class Group:
    def __init__(self, l):
        self.line = l
        self.gtype = self.__get_group()

    def __get_group(self):
        if "```" in self.line[0] or "#+BEGIN_SRC" in self.line[0]:
            return "CODE"
        else:
            return "TEXT"

    def add_line(self, l):
        self.line.append(l)

    def update(self, text):
        self.line = text

class Text:
    def __init__(self, filename):
        self.f = open(filename, "r")
        self.groups = []

    # グループ化
    def parse(self):
        lines = []
        code_flag = 0 # ``` には開始，終了の区別ができないためflagでcode中か判別
        for line in self.f:            
            ### キーとなる文字列でグループ化
            # 空行で分割
            if line == "":
                self.groups.append(Group(lines))
                line = []
            # コード記法部分を分割(開始)
            elif (code_flag == 0 and "```" in line) or "#+BEGIN_SRC" in line:
                code_flag = 1
                self.groups.append(Group(lines))
                lines = [line[:-1]]
            # コード記法部分を分割(終了)
            elif (code_flag == 1 and "```" in line) or "#+END_SRC" in line:
                code_flag = 0
                lines.append(line)
                self.groups.append(Group(lines))
                lines = []
            # 何もなければ追加のみ
            else:
                lines.append(line[:-1])

class Converter:
    def __init__(self, mode, text):
        self.mode = mode
        self.text = text
        self.converted = []

    def convert(self):
        for group in self.text.groups:
            if group.gtype == "TEXT":
                self.converted.append(self.__text_convert(group))
            elif group.gtype == "CODE":
                self.converted.append(self.__code_convert(group))
        return self.converted

    def __text_convert(self, group):
        result = []
        for l in group.line:
            # 見出しなら
            if l.startswith("*"):
                m = re.search("(\*+)(.*)", l)
                size = "*" * (5 - len(m.group(1))) # * → **** ** → *** つまり，5-(元の個数)
                try:
                    title = m.group(2)[1:]
                except:
                    title = "NONE"
                convl = "[" + size + " " + title + "]"
            # 箇条書きなら
            elif l.replace(" ", "").startswith("+"):
                convl = l.replace("+ ", "")
            else:
                convl = l
            # リンクを処理
            m = re.search(".*(\[\[(.*)\]\[(.*)\]\]).*", convl)
            if m:
                if m.group(2).startswith("http"):
                    link = m.group(2) # ひだり
                else:
                    link = "[" + m.group(3) + "]" # みぎ
                convl = re.sub("\[\[(.*)\]\[(.*)\]\]", link, convl)
            # 1行ずつ変換結果を保存
            result.append(convl)
            
        return "\n".join(result)

    def __code_convert(self, group):
        m = re.search("(#\+BEGIN_SRC|```)(.*)", group.line[0])
        if m:
            lang = m.group(2).replace(" ", "")
        else:
            lang = "None"
        result = ["code:" + lang]
        trimed = group.line[1:-1] # BEGIN END 行を削除
        for l in trimed:
            if l != "": result.append(l)
        return "\n".join(result)
    
if __name__ == "__main__":
    text = Text(sys.argv[1])
    text.parse()

    converted = Converter("Scrapbox", text).convert()
    for l in converted:
        print(l)