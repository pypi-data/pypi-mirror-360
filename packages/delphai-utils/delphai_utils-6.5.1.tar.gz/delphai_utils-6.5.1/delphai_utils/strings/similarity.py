import re
from typing import Set


def get_bow(sentence: str) -> Set[str]:
    return {x for x in re.split(r"\W+", sentence.lower()) if x}


def get_trigrams(sentence: str) -> Set[str]:
    if not sentence:
        return set()
    clear_sentence = " ".join([x for x in re.split(r"\W+", sentence.lower()) if x])
    return {clear_sentence[i - 3 : i] for i in range(3, len(clear_sentence) + 1)}


def similarity(s1: str, s2: str) -> float:
    s1_set: Set[str] = get_trigrams(s1)
    s2_set: Set[str] = get_trigrams(s2)
    return len(s1_set & s2_set) / max(1, len(s1_set | s2_set))
