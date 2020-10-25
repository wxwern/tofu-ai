from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk.tokenize.casual import casual_tokenize
from positivity import Sentience

IDENTITY = Sentience.getIdentity()

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
    found = False
    for token in tokens:
        if IDENTITY.lower() in token[0].lower():
            found = True
        if token[1] not in ('JJ', 'NN', 'NNS', 'NNP', 'NNPS'):
            return False
    return found


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
    tokens = list(map(lambda x: 'I' if x == 'i' else x, casual_tokenize(s,reduce_len=True)))
    tagged_tokens = pos_tag(tokens)
    return tagged_tokens

def parse_sentence_human_description(s):
    s = parse_sentence(s)
    mappings = {
        'CC': 'Coordinating Conjunction',
        'CD': 'Cardinal Digit',
        'DT': 'Determiner',
        'EX': 'Existential There',
        'FW': 'Foreign Word',
        'IN': 'Preposition/Subordinating Conjunction',
        'JJ': 'Adjective',
        'JJR': 'Adjective, Comparative',
        'JJS': 'Adjective, Superlative',
        'LS': 'List Marker',
        'MD': 'Modal',
        'NN': 'Noun, Singular',
        'NNS': 'Noun, Plural',
        'NNP': 'Proper Noun, Singular',
        'NNPS': 'Proper Noun, Plural',
        'PDT': 'Predeterminer',
        'POS': 'Possessive Ending',
        'PRP': 'Personal Pronoun',
        'PRP$': 'Possessive Pronoun',
        'RB': 'Adverb',
        'RBR': 'Adverb, Comparative',
        'RBS': 'Adverb, Superlative',
        'RP': 'Particle',
        'TO': 'to',
        'UH': 'Interjection',
        'VB': 'Verb, Base Form',
        'VBD': 'Verb, Past Tense',
        'VBG': 'Verb, Gerund/Present Participle',
        'VBN': 'Verb, Past Participle',
        'VBP': 'Verb, Non-3rd person Singular Present',
        'VBZ': 'Verb, 3rd person Singular Present',
        'WDT': 'wh-determiner',
        'WP': 'wh-pronoun',
        'WP$': 'Possessive wh-pronoun',
        'WRB': 'wh-abverb'
    }
    return list(map(lambda x: x + ((mappings[x[1]],) if x[1] in mappings else ()),s))



