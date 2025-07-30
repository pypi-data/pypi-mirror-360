import re
from typing import List


def get_number(string: str) -> List[float]:
    nums = re.findall(r'\d+\.?\d*', string)
    return [float(x) for x in nums]


def split_string(s: str) -> str:
    words = re.findall(r'[A-Z][a-z]*', s)
    prepositions = {'the', 'of', 'for', 'and', 'in', 'at', 'on', 'to'}
    added = False
    dictionary = ['Coff', 'Cruisg']
    final_words = []
    for word in words:
        for p in prepositions:
            if p in word and (word.startswith(p) or word.endswith(p)):
                if word.startswith(p):
                    remain = word.replace(p, "", 1)
                    final_words.append(p)
                    final_words.append(split_string(remain))
                    added = True
                    break
                elif word.endswith(p):
                    remain = word.replace(p, "", 1)
                    if remain[-1] in ['a', 'i', 'o', 'u'] or remain in dictionary or (
                            remain[-1] in ['e', 'i'] and remain[-2] in ['a', 'i', 'o', 'u', 'A', 'O', 'U', 'I', 'w']):
                        continue
                    final_words.append(split_string(remain))
                    final_words.append(p)
                    added = True
                    break
                else:
                    pass
        if added:
            added = False
            continue
        final_words.append(word)

    return ' '.join(final_words)


def convert_lightcone_effect(text: str, rank: int) -> str:
    pattern = r'(\d+(\.\d+)?(%?)(/\d+(\.\d+)?%?){4})'
    matches = [match[0] for match in re.finditer(pattern, text)]
    if len(matches) > 0:
        for match_obj in matches:
            values = match_obj.split('/')
            text = re.sub(match_obj, values[rank - 1], text)
    return text


def is_numeric(s: str) -> bool:
    if not isinstance(s, str):
        return False
    pattern = r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$'
    return bool(re.match(pattern, s))


def get_string(s: str) -> str:
    return s
