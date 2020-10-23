from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from positivity import Sentience
import random

IDENTITY = 'tofu'.lower()

def is_question(s):
    #TODO: not implemented
    return False

def yesno_qn_count(s):
    '''Returns the number of yes/no questions being asked in this given string.'''
    token_split = [[]]
    for tok,tag in parse_sentence(s) if isinstance(s, str) else s:
        if tag not in ('RB', 'RBR', 'RBS'):
            token_split[-1].append((tok, tag))

        if tag in ('CC', ',', 'LS'):
            if tok.lower() != 'and':
                token_split.append([])

    count = 0
    prev_chunk = []
    for chunk in token_split:
        if len(chunk) >= 2:
            typ1 = chunk[0][1]
            typ2 = chunk[1][1]

            typ1_valid = typ1 in ('MD', 'VB', 'VBP', 'VBZ', 'VBD')

            if typ1_valid and typ2 == 'VB':
                #in some cases the detection is incorrectly a verb.
                #so we might want to see if it can be interpreted as a noun or other valid term.
                typ2 = parse_sentence(chunk[1][0])[0][1]

            typ2_valid = typ2 in ('PRP', 'PRP$', 'NNS', 'NN', 'NNP', 'NNPS', 'VBG', 'JJ', 'DT')

            if typ1_valid and typ2_valid:
                count += 1
                prev_chunk = chunk
                continue

        if len(prev_chunk) > 0 and prev_chunk[-1][0].lower() == 'or' and count > 0:
            count += 1
        prev_chunk = chunk

    return count

def tofu_called_and_nothing_else(s):
    tokens = parse_sentence(s)
    count = 0
    found = False
    while count < len(tokens) and tokens[count][1] in ('JJ', 'NN', 'NNS', 'NNP', 'NNPS'):
        count += 1
        if IDENTITY.lower() in tokens[0][0].lower():
            found = True
    return found and len(tokens) == count


def asking_tofu_yesno_qn_count(s):
    '''
    Returns the number of yes/no questions being asked to tofu (the subject) in this given string. Returns -1 if the string does not address tofu specifically.

    tofu, the subject name, can be modified.
    '''
    tokens = parse_sentence(s)
    while len(tokens) > 0 and tokens[0][1] in ('NN', 'NNS', 'NNP', 'NNPS'):
        term = tokens[0][0].lower()
        if IDENTITY.lower() in term.lower():
            return yesno_qn_count(tokens[1:])
        else:
            tokens = tokens[1:]
    return -1

def is_tofu_tagged(s):
    return ('@' + IDENTITY.lower()) in s.lower()

def parse_sentence(s):
    if isinstance(s, list):
        return s
    s = s.replace('@' + IDENTITY, IDENTITY)
    tokens = list(map(lambda x: 'I' if x == 'i' else x, word_tokenize(s)))
    tagged_tokens = pos_tag(tokens)
    return tagged_tokens


__message_combos_cache = {}
def get_message_combos():
    if not __message_combos_cache:
        message_combos = [
                (['ping'], ['pong'], 0.9),
                (['pong'], ['ping'], 0.9),
                (['hi', 'hello', 'helo', 'hallo', 'hola', 'hai', 'hoi'], ['hello!', 'hi!', 'こんにちは!'], 0.3),
                ([':D', ':DD', ':DDD', ':)', ':))', ':)))', '(:', ':-)', ':>', ':>>'], [':)', ':D'], 0.3),
        ]

        for words, responses, chance in message_combos:
            for word in words:
                __message_combos_cache[word] = (responses, chance)

    return __message_combos_cache


def generate_response(s):

    D_STRUCTURE = s.startswith("!DEBUG_STRUCTURE")
    D_SENTIENCE = s.startswith("!DEBUG_SENTIENCE")

    if s.startswith("!DEBUG"):
        s = s[16:].strip()

    if D_SENTIENCE:
        x = Sentience.getDebugInfoAfterMessage(s).replace('\n',' ')
        x2 = ' '
        for c in x:
            if c != ' ' or x2[-1] != ' ':
                x2 += c
        return '`' + x2.replace(' :', ':').strip() + '`'

    words = word_tokenize(s.lower())

    tofu_tagged = is_tofu_tagged(s)
    tofu_targeted = tofu_tagged

    #asking_question = is_question(s)
    parsed_s = parse_sentence(s)

    c = asking_tofu_yesno_qn_count(parsed_s)
    if c == -1:
        c = yesno_qn_count(parsed_s)
    else:
        tofu_targeted = True

    if D_STRUCTURE:
        return '`Yes/No Qn: %d; Sentence Structure: %s`' % (c, str(parsed_s))

    agreeability = Sentience.determineResponseAgreeability(s)


    #if tofu_called_and_nothing_else(s):
    #    pass #TODO: greet

    if c > 0:
        if c == 1:

            yes_opt = random.choice([
                "perhaps",
                "i believe yes",
                "yeah",
                "yes",
                "my deductions indicate yes",
                "maybe",
                "i think so",
                "very likely",
                "most definitely",
                "yes indeed",
                "i'd say yes",
            ])
            no_opt = random.choice([
                "maybe not",
                "my sources say no",
                "no",
                "nah",
                "i don't think so",
                "doubt it",
                "probably not",
                "most definitely not",
                "i think no",
                "not at all",
            ])
            rnd_opt = random.choice([
                "i'm not sure about that",
                "bleh",
                "interesting question",
                "i don't wanna tell you right now",
                "i don't have a clue",
                "hmmm",
                "my sources cannot be trusted",
            ])

            if agreeability > 0.3:
                return yes_opt
            elif agreeability < -0.3:
                return no_opt
            else:
                factor = 1-(abs(agreeability))/0.3
                rnd_tri= random.uniform(0.0, factor)
                if rnd_tri > 0.5:
                    return rnd_opt
                elif agreeability > 0.15:
                    return yes_opt
                elif agreeability < -0.15:
                    return no_opt
                else:
                    return random.choice([yes_opt, no_opt])

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
                "can't decide, so i'll say yes",
            ])
        return random.choice([
            "i'm confused",
            "interesting question",
            "i don't understand what you mean",
            "this sentence is too complicated for me to understand",
            "hmm",
        ])
    elif not tofu_targeted and (IDENTITY.lower() in words or IDENTITY.lower() == s.lower()) and random.random() <= 0.1:
        return random.choice(['hmm i heard my name', 'hmmmm', 'interesting', 'hm'])
    elif len(words) <= 5:
        combos = get_message_combos()
        for word in words:
            if word in combos:
                if tofu_tagged or random.random() <= combos[word][1]:
                    return random.choice(combos[word][0])

    return None
