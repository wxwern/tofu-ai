import copy
from nltk.tag import pos_tag
from nltk.tokenize.casual import casual_tokenize

IDENTITY = None

#common loosely defined tag sets
__NOUN_SET       = {'DT', 'JJ', 'NN', 'NNS', 'NNP', 'NNPS', 'PRP', 'PRP$'}
__VERB_SET       = {'VB', 'VBP', 'VBZ', 'VBD'}
__ADVERB_SET     = {'RB', 'RBR', 'RBS'}
__ADJECTIVE_SET  = {'JJ', 'IN', 'MD'}
__PARTICLE_SET   = set(['RP'])
__DETERMINER_SET   = set(['DT'])
__CONNECTOR_SET  = {'CC', 'LS', ','}
__TERMINATE_SET  = set(['.'])
__WH_QN_SET      = {'WP', 'WP$', 'WRB', 'WDT'}

__TAG_SET_TYPES = ['NOUN', 'VERB', 'ADVERB', 'ADJECTIVE', 'PARTICLE', 'DETERMINER', 'CONNECTOR', 'TERMINATE', 'WH-']
def get_tag_set_types():
    return __TAG_SET_TYPES

def tag_in_set(tag, st):
    '''
    Returns True if a tag exists in a tag set, False otherwise.
    Valid set terms: NOUN, VERB, ADVERB, CONNECTOR, TERMINATE, WH-
    '''

    TAG_SET_MAP = {
        'NOUN': __NOUN_SET,
        'VERB': __VERB_SET,
        'ADVERB': __ADVERB_SET,
        'ADJECTIVE': __ADJECTIVE_SET,
        'PARTICLE': __PARTICLE_SET,
        'DETERMINER': __DETERMINER_SET,
        'CONNECTOR': __CONNECTOR_SET,
        'TERMINATE': __TERMINATE_SET,
        'WH-': __WH_QN_SET
    }

    if isinstance(st, list):
        for _st in st:
            if tag_in_set(tag, _st):
                return True
        return False
    res = (tag in TAG_SET_MAP[st]) if (st in TAG_SET_MAP) else False
    return res

#sentence structures to note ("sentence signatures")
__YN_QN_SETLIST  = [
    {'MD', 'VB', 'VBP', 'VBZ', 'VBD'},
    {'PRP', 'PRP$', 'NNS', 'NN', 'NNP', 'NNPS', 'VBG', 'JJ', 'DT'}
]
__STD_QN_SETLIST = [
    {'WP', 'WP$', 'WRB', 'WDT'},
    {'MD', 'VB', 'VBP', 'VBZ', 'VBD', 'PRP', 'PRP$', 'NNS', 'NN', 'NNP', 'NNPS', 'JJ', 'IN'}
]

__QUERY_TYPES = ['YN_QN', 'STD_QN']
def get_query_types():
    return __QUERY_TYPES

def simple_sentence_is_type(toktags, typ):
    SENTENCE_TYPE_MAP = {
        'YN_QN': __YN_QN_SETLIST,
        'STD_QN': __STD_QN_SETLIST
    }
    if typ not in SENTENCE_TYPE_MAP or toktags == []:
        return False

    setlist = SENTENCE_TYPE_MAP[typ]

    c = 0
    for i, toktag in enumerate(toktags):
        if i >= len(setlist):
            break
        if toktag[1] not in setlist[i]:
            return False
        c += 1
    return c == len(setlist)

# ----------- #
class Understanding:
    '''Breaks down messages into easy to digest portions'''
    @staticmethod
    def parse_queries(s, single_sentence_only=False, merge_results=False):
        '''
        Returns all questions being asked in this given string and relevant information as a dictionary.

        Return format: {
            'queries': list of queries, each query tagged with their types, and each query being a list of tokenized tagged words.
            'subject_call': list of tokenized tagged words corresponding to the subject call, which can be None if not present.
            'target_summoned': True if the target subject is called in the query, False otherwise.
        }

        Returns a list of the above if more than one sentence provided (unless single_sentence_only is True, then returns the last sentence instead).
        '''

        subject_call_tokens, content_tokens, target_summoned = Understanding.parse_subject_message_target(s)

        sentences = Understanding.parse_and_split_message(content_tokens)
        if len(sentences) > 1:
            #perform recursive computation
            if single_sentence_only:
                sentences = [sentences[-1]]
            else:
                results = []
                sentences[0].insert(0, subject_call_tokens)
                for sentence_portion in sentences:
                    sentence = []
                    for portion in sentence_portion:
                        sentence += portion
                    s = Understanding.parse_queries(sentence)
                    if s is not None:
                        results.append(s)

                if not merge_results:
                    return results

                queries = []
                statements = []
                for result in results:
                    queries.extend(result["queries"])
                    statements.extend(result["statements"])

                merged_results = {
                    "queries": queries,
                    "statements": statements,
                    "subject_call": results[0]["subject_call"],
                    "target_summoned": results[0]["target_summoned"]
                }
                return merged_results


        queries = []
        statements = []

        first_portion_ynqn = False
        sentence_portions = sentences[0] if sentences else []
        for i, portion in enumerate(sentence_portions):
            selected_query_type = None
            for query_type in get_query_types():
                if simple_sentence_is_type(portion, query_type):
                    queries.append((portion, query_type))
                    selected_query_type = query_type
                    break

            if not selected_query_type and len(portion) >= 2:
                for query_type in get_query_types():
                    if portion[1][1] == 'VB':
                        #in some cases the detection is incorrectly a verb.
                        #so we might want to see if it can be interpreted as a noun or other valid term.
                        portion_alt = copy.deepcopy((portion))
                        portion_alt[1] = (portion_alt[1][0], Understanding.parse_sentence(portion_alt[1][0])[0][1])

                        if simple_sentence_is_type(portion_alt, query_type):
                            queries.append((portion_alt, query_type))
                            selected_query_type = query_type
                            break

            # heuristics for yn question parsing
            # the ideal way would be to do more parsing
            # but i am lazy
            if i == 0 and selected_query_type == 'YN_QN' and portion and portion[-1][0] == 'or':
                first_portion_ynqn = True

            if i > 0 and first_portion_ynqn and not selected_query_type:
                queries.append((portion, 'YN_QN'))
                continue

            if not selected_query_type:
                statements.append((portion, 'SM'))

        return {
            "queries": queries,
            "statements": statements,
            "subject_call": subject_call_tokens,
            "target_summoned": target_summoned
        }

    @staticmethod
    def parse_sentence_subject_predicate(s):
        '''
        Attempts to perform a quick simple split of the sentence into subject and predicate.
        Assumes input to be a singular sentence.

        Returns two lists of tagged tokens [(token, tag)].
        Both partial lists are returned as a tuple format (subject, predicate).

        Accuracy is not guaranteed, and may not work well for more ambiguous sentences.
        Order of words are guaranteed to be preserved.
        '''
        if isinstance(s, tuple):
            return s

        toktags = Understanding.parse_sentence(s)
        was_noun = False
        predicate_idx = None

        for i, toktag in enumerate(toktags):
            tok, tag = toktag
            if was_noun and tag_in_set(tag, ['VERB', 'ADVERB', 'ADJECTIVE']):
                predicate_idx = i
            was_noun = tag_in_set(tag, ['DETERMINER', 'NOUN']) or tag in ('VBG','IN')

        if predicate_idx is None:
            return ([], toktags[:])

        return (toktags[:predicate_idx], toktags[predicate_idx:])

    @staticmethod
    def is_target_tagged(s):
        global IDENTITY
        if IDENTITY is None:
            import positivity
            IDENTITY = positivity.Sentience.getIdentity()

        return ('@' + IDENTITY.lower()) in s.lower()

    @staticmethod
    def matches_target(t):
        '''Returns True if given token matches identity'''
        global IDENTITY
        if IDENTITY is None:
            import positivity
            IDENTITY = positivity.Sentience.getIdentity()
        return IDENTITY.lower() in t.lower() and len(t) - len(IDENTITY) <= 2

    @staticmethod
    def remove_repeated_chars_word(w):
        x = ''
        for c in w:
            if x == '' or c != x[-1]:
                x += c
        return x

    @staticmethod
    def parse_sentence(s):
        '''
        Returns the tagged and tokenized sentence in the form of a (token, tag) list.

        If a (token, tag) list is given, it returns itself. This allows for redundant calls to make sure the sentence is tokenized.
        '''
        if isinstance(s, list):
            return s

        global IDENTITY
        if IDENTITY is None:
            import positivity
            IDENTITY = positivity.Sentience.getIdentity()

        s = s.replace('@' + IDENTITY, IDENTITY)
        tokens = list(map(lambda x: 'I' if x == 'i' else x, casual_tokenize(s,reduce_len=True)))
        tagged_tokens = list(map(lambda x: (x[0], 'NN') if Understanding.matches_target(x[0]) else x, pos_tag(tokens)))
        return tagged_tokens

    @staticmethod
    def unparse_sentence(tt):
        '''
        Reconstructs the sentence from tagged tokens in the form of a (token, tag) list,
        then returns a string.

        Note: This cannot 100% reproduce the original sentence, and may have spacing errors.

        If a string is given, it returns itself. This allows for redundant calls to make sure the sentence is untokenized.
        '''
        if isinstance(tt, str):
            return tt
        return ' '.join(map(lambda x: x[0], tt)).strip()

    @staticmethod
    def parse_and_split_message(s):
        '''
        Returns parsed data split into sentences and sentence parts. This will return a 3D list of (token, tag).
        '''
        tokens = Understanding.parse_sentence(s)
        sentences = [[]]
        for toktag in tokens:
            sentences[-1].append(toktag)
            if tag_in_set(toktag[1], 'TERMINATE'):
                sentences.append([])

        while sentences != [] and sentences[-1] == []:
            sentences = sentences[:-1]

        for i, sent in enumerate(sentences):
            split_sent = [[]]

            for toktag in sent:
                split_sent[-1].append(toktag)
                if toktag[0] != 'and' and tag_in_set(toktag[1], 'CONNECTOR'):
                    split_sent.append([])

            while split_sent != [] and split_sent[-1] == []:
                split_sent = split_sent[:-1]

            sentences[i] = split_sent

        return sentences

    @staticmethod
    def parse_subject_message_target(s):
        '''
        Processes whether the message calls a subject, and whether the subject is target (self).

        Returns a tuple in the format:
        (
            subject_call_tokens: list or None,
            content_tokens     : list,
            target_summoned    : bool
        )
        '''
        if isinstance(s, tuple):
            return s

        tokens = Understanding.parse_sentence(s)

        target_summoned = False

        index_after_target = 0
        for i, tok_tag in enumerate(tokens):
            tok, tag = tok_tag

            if (i == index_after_target) and tag_in_set(tag, 'NOUN'):
                index_after_target += 1
                if Understanding.matches_target(tok):
                    target_summoned = True
                continue
            if tag_in_set(tag, 'CONNECTOR'):
                index_after_target += 1
                continue
            if i != index_after_target:
                break

        return (tokens[:index_after_target] if index_after_target > 0 else None, tokens[index_after_target:], target_summoned)


    @staticmethod
    def parse_sentence_human_description(s):
        s = Understanding.parse_sentence(s)
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
