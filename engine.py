from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
import random

def yesno_qn_count(s):
    '''Returns the number of yes/no questions being asked in this given string.'''
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

            typ1_valid = typ1 in ('MD', 'VBP', 'VBZ')

            if typ1_valid and typ2 == 'VB':
                #in some cases the detection is incorrectly a verb.
                #so we might want to see if it can be interpreted as a noun or other valid term.
                typ2 = parse_sentence(chunk[1][0])[0][1]

            typ2_valid = typ2 in ('PRP', 'PRP$', 'NNS', 'NN', 'NNP', 'NNPS', 'VBG')

            if typ1_valid and typ2_valid:
                count += 1
                prev_chunk = chunk
                continue

        if len(prev_chunk) > 0 and prev_chunk[-1][0].lower() == 'or' and count > 0:
            count += 1
        prev_chunk = chunk

    return count

def asking_tofu_yesno_qn_count(s):
    '''Returns the number of yes/no questions being asked to tofu in this given string. Returns -1 if the string does not address tofu specifically.'''
    tokens = parse_sentence(s)
    while len(tokens) > 0 and tokens[0][1] in ('NN', 'NNS'):
        term = tokens[0][0].lower()
        if 'tofu' in term:
            return yesno_qn_count(tokens[1:])
        else:
            tokens = tokens[1:]
    return -1

def parse_sentence(s):
    tokens = list(map(lambda x: 'I' if x == 'i' else x, word_tokenize(s)))
    tagged_tokens = pos_tag(tokens)
    return tagged_tokens

def generate_response(s):
    words = word_tokenize(s.lower())
    c = asking_tofu_yesno_qn_count(s)
    if c == -1:
        c = yesno_qn_count(s)

    if c > 0:
        if c == 1:
            return random.choice([
                "perhaps",
                "i believe yes",
                "maybe",
                "maybe not",
                "are you sure about that?",
                "my deductions indicate yes",
                "perhaps you might want to think again",
                "my sources say no",
                "i think so",
                "most definitely",
                "yes indeed",
                "i'd say yes",
                "i don't have a clue",
                "hmmmm",
                "my sources... cannot be trusted",
                "nah",
                "i don't think so",
                "doubt it",
                "probably not",
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
                "second option",
                "i sense a potential r/inclusiveor answer, so i'd say yes",
            ])
        return random.choice([
            "i'm confused",
            "interesting question",
            "i don't understand what you mean",
            "this sentence is too complicated for me to understand",
            "hmmm",
        ])
    elif 'nice' == s.lower():
        if random.uniform(0.0,1.0) > 0.9:
            return 'not nice'
        return 'nice'
    elif 'ping' == s.lower():
        return 'pong'
    elif 'pong' == s.lower():
        return 'ping'
    elif 'tofu' in words:
        if random.uniform(0.0,1.0) > 0.95:
            return random.choice(['hm i heard my name'])
    elif s in (':D', ':DD', ':DDD', ':)', ':))', ':)))', '(:', ':-)'):
        if random.uniform(0.0,1.0) > 0.9:
            return random.choice([':)', ':D'])
    return None