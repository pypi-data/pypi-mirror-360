import re
import ass
import chardet


def remove_tags(text):
    clean_text = re.sub(r'{\\[^}]+}', '', text)
    clean_text = clean_text.strip()
    clean_text = clean_text.replace('\\N', '\\n')
    return clean_text.strip()


def read_ass(filename):
    with open(str(filename), mode="rb") as f:
        result = chardet.detect(f.read())
        encoding = result["encoding"]
    with open(filename, encoding=encoding) as f:
        subs = ass.parse(f)
        sub_list = []

        for event in subs.events:
            # Extracting start time, end time, and content of subtitles
            start = event.start.total_seconds()
            end = event.end.total_seconds()
            content = event.text
            # Removing special effects if any
            content = remove_tags(content)
            # Append data to the list
            sub_list.append({'start': start, 'end': end, 'content': content})
        return sub_list

