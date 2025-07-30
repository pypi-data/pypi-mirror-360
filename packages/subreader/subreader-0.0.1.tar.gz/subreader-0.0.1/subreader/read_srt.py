import json
from pathlib import Path
import chardet
from apnode.node import string_to_node_tree
from subreader.file_ops import write_txt


def read_txt_chardet(filename):
    with open(str(filename), mode="rb") as f:
        result = chardet.detect(f.read())
        # if not str(result["encoding"]).lower().startswith("utf-8"):
        #     print("文件 {} 格式:{}".format(filename, result))
        encoding = result["encoding"]
    with open(str(filename), mode="r", encoding=encoding) as f:
        return f.read()

def read_srt(filename):
    content = read_txt_chardet(filename)
    content = content[1:]
    root = string_to_node_tree(content, ["^(?P<id>\d*)$"])
    root = root.prune(1, lambda v: len(v.children) == 0 and v.level == 1)

    result_list = []
    for node in root.children:
        node.extract_value_info(2, ["^(?P<s_hour>[0-9]*):(?P<s_min>[0-9]*):(?P<s_sec>[0-9]*),(?P<s_ms>[0-9]*) *-->.*$"])
        node.extract_value_info(2, ["^.*--> *(?P<e_hour>[0-9]*):(?P<e_min>[0-9]*):(?P<e_sec>[0-9]*),(?P<e_ms>[0-9]*).*$"])
        s_hour = node.find_children_info_value("s_hour")
        s_min = node.find_children_info_value("s_min")
        s_sec = node.find_children_info_value("s_sec")
        s_ms = node.find_children_info_value("s_ms")
        e_hour = node.find_children_info_value("e_hour")
        e_min = node.find_children_info_value("e_min")
        e_sec = node.find_children_info_value("e_sec")
        e_ms = node.find_children_info_value("e_ms")
        start = s_hour.to_float() * 3600 + s_min.to_float() * 60 + s_sec.to_float() + s_ms.to_float() / 1000
        end = e_hour.to_float() * 3600 + e_min.to_float() * 60 + e_sec.to_float() + e_ms.to_float() / 1000
        content = ""
        for i, n in enumerate(node.children):
            if i > 0:
                value = n.value.to_str()
                if len(value) > 0:
                    content += value + " "
        result_list.append({
            "start": start,
            "end": end,
            "content": content
        })
    return result_list


def time_to_string(time):
    ms = int(time * 1000 % 1000)
    h = int(time / 3600)
    m = int(time % 3600 / 60)
    s = int(time % 3600 % 60)
    return "{:0>2d}:{:0>2d}:{:0>2d},{:0>3d}".format(h, m, s, ms)


class SRTObject:
    def __init__(self, file=None):
        self.file = file
        self.objs = []
        if file is not None and Path(file).exists():
            self.objs = read_srt(file)

    def add_obj(self, obj):
        self.objs.append(obj)
        self.__sort_objs()

    def __sort_objs(self):
        self.objs = sorted(self.objs, key=lambda x: x['start'])

    def save(self, filename=None):
        if filename is None:
            filename = self.file
        with open(filename, "w", encoding="utf-8") as f:
            for i, obj in enumerate(self.objs):
                f.writelines("{}\n".format(i + 1))
                f.writelines("{} --> {}\n".format(time_to_string(obj["start"]), time_to_string(obj["end"])))
                f.writelines("{}\n".format(obj["content"]))

    def save_to_json(self, filename=None):
        if filename is None:
            filename = self.file
        write_txt(filename, json.dumps(self.objs))

    def adjust_time(self, offset):
        for i, obj in enumerate(self.objs):
            obj["start"] += offset
            obj["end"] += offset


def save_srt(objs, filepath):
    srt = SRTObject(filepath)
    for o in objs:
        srt.add_obj(o)
    srt.save()