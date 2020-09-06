from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
import random

def yesno_qn_count(s):
    token_split = [[]]
    for tok,tag in parse_sentence(s) if isinstance(s, str) else s:
        if tag != 'DT':
            token_split[-1].append((tok, tag))
        if tag == 'CC' or tag == ',':
            token_split.append([])
    count = 0
    prev_chunk = []
    for chunk in token_split:
        if len(chunk) >= 2:
            typ1 = chunk[0][1]
            typ2 = chunk[1][1]
            if typ1 in ('MD', 'VBP', 'VBZ') and typ2 in ('PRP', 'PRP$', 'NNS', 'NN', 'NNP', 'NNPS', 'FW', 'VB'):
                count += 1
                prev_chunk = chunk
                continue

        if len(prev_chunk) > 0 and prev_chunk[-1][0].lower() == 'or' and count > 0:
            count += 1
        prev_chunk = chunk

    return count

def asking_tofu_yesno_qn_count(s):
    tokens = parse_sentence(s)
    while len(tokens) > 0 and tokens[0][1] in ('NN', 'NNS'):
        term = tokens[0][0].lower()
        if 'tofu' in term:
            return yesno_qn_count(tokens[1:])
        else:
            tokens = tokens[1:]
    return 0

def parse_sentence(s):
    tokens = list(map(lambda x: 'I' if x == 'i' else x, word_tokenize(s)))
    tagged_tokens = pos_tag(tokens)
    return tagged_tokens

def generate_response(s):
    words = word_tokenize(s.lower())
    c = asking_tofu_yesno_qn_count(s)
    if c == 0:
        c = yesno_qn_count(s)

    if c > 0:
        if c == 1:
            return random.choice([
                "perhaps",
                "i believe yes",
                "maybe not",
                "are you sure about that?",
                "my deductions indicate yes",
                "perhaps you might want to think again",
                "my sources say no",
                "i think so",
                "most definitely",
                "yes indeed",
                "i don't have a clue",
                "my sources cannot be trusted",
                "nah"
            ])
        if c == 2:
            return random.choice([
                "first option",
                "the latter",
                "the former",
                "on second thought, your second option",
                "why not both",
                "i can't find the answer to that",
                "i think neither",
                "go with the first",
            ])
        return random.choice([
            "i'm confused",
            "i don't understand",
        ])
    elif 'nice' == s.lower():
        if random.uniform(0.0,1.0) > 0.85:
            return 'not nice'
        return 'nice'
    elif 'ping' == s.lower():
        return 'pong'
    elif 'pong' == s.lower():
        return 'ping'
    elif s.upper() == s and len(s) >= 4:
        return random.choice([None, ':(', None, None, None])
    elif s in (':D', ':DD', ':DDD', ':)', ':))', ':)))', '(:', ':-)'):
        return random.choice([None, ':)', None, None, None])

    return None
