import csv
import json
import os
import pickle
from pathlib import Path


def read_txt(file):
    with open(file, "r", encoding="utf8") as f:
        return f.read()


def write_txt(file, data):
    with open(file, "w", encoding="utf8") as f:
        f.write(data)


def read_json(file):
    return json.loads(read_txt(file))


def write_json(file, data):
    write_txt(file, json.dumps(data, ensure_ascii=False))


def write_pickle(file, data):
    data = pickle.dumps(data)
    with open(file, "wb") as f:
        f.write(data)


def load_pickle(file):
    if Path(file).exists():
        with open(file, "rb") as f:
            return pickle.loads(f.read())
    return None


def read_txt_lines(file):
    content = read_txt(file)
    return content.split("\n")


def write_txt_lines(file, lines):
    with open(file, "w", encoding="utf8") as f:
        for l in lines:
            f.writelines(l + "\n")


def read_csv(file):
    with open(file, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def get_folder_files(folder_list, extends=None):
    if extends is None:
        extends = ['srt', 'ass', 'mp4', "mkv"]
    files_list = []
    for folder in folder_list:
        path = [p for ext in extends for p in Path(f'{folder}').glob(f'**/*.{ext}')]
        for p in path:
            files_list.append(p)
    return files_list


def create_folder(path):
    path = Path(str(path))
    if path.is_file():
        if not path.parent.exists():
            os.makedirs(str(path.parent))
    else:
        if not path.exists():
            if path.suffix != "":
                if not path.parent.exists():
                    os.makedirs(str(path.parent))
            else:
                os.makedirs(str(path))
