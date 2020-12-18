from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk.tokenize.casual import casual_tokenize

from positivity import Sentience
from queries import Understanding

import random
import datetime

IDENTITY = Sentience.getIdentity()

__message_combos_cache = {}
def get_message_combos():
    if not __message_combos_cache:
        message_combos = [
                (['ping'], ['pong', 'pong ping?', 'pong?', 'pong'], 0.9),
                (['pong'], ['ping', 'ping pong' , 'pong?', 'ping'], 0.9),
                (['hi', 'hello', 'helo', 'halo', 'hola', 'hai', 'hoi'], ['hello!', 'hi!', 'こんにちは!'], 0.2),
                ([':D', ':)', '(:', ':-)', ':>'], [':)', ':D'], 0.2),
                (['xd', 'lol', 'lmao', 'lmfao', 'haha'], ['lol', 'haha', 'ahaha', 'heh', 'lol', 'hm yes very funny', 'XD'], 0.15)
        ]

        for words, responses, chance in message_combos:
            for word in words:
                __message_combos_cache[word] = (responses, chance)

    return __message_combos_cache

def generate_response(s):

    D_STRUCTURE = s.startswith("!DEBUG_STRUCTURE")
    D_SENTIENCE = s.startswith("!DEBUG_SENTIENCE")
    D_QUERIES = s.startswith("!DEBUG_QUERIES")

    if s.startswith("!DEBUG"):
        s = ' '.join(s.split(' ')[1:]).strip()

    if D_SENTIENCE:
        x = Sentience.getDebugInfoAfterMessage(Understanding.parse_sentence_subject_predicate(s)).replace('\n',' ')
        x2 = ' '
        for c in x:
            if c != ' ' or x2[-1] != ' ':
                x2 += c
        return '`' + x2.replace(' :', ':').strip() + '`'

    if D_STRUCTURE:
        sentences = Understanding.parse_and_split_message(s)
        if len(sentences) > 1:
            print('Sentence Structure: Multiple sentences. Provide each sentence separately for details.')
        if len(sentences) == 0:
            return 'Provide a sentence after the debug command to debug sentence structure.'

        def human_readable_structure(x):
            s, p = Understanding.parse_sentence_subject_predicate(x)
            return 'subj: %s, pred: %s' % (s,p)

        return 'Sentence Structure: `%s`' % str("; ".join(map(human_readable_structure, sentences[0])))


    words = casual_tokenize(s.lower(), reduce_len=True)
    parsed_result = Understanding.parse_queries(s, single_sentence_only=True)

    if D_QUERIES:
        return 'Sentence Queries: `%s`' % str(parsed_result)

    subject_call = parsed_result["subject_call"]
    queries = parsed_result["queries"]
    tofu_tagged = Understanding.is_target_tagged(s)
    tofu_targeted = parsed_result["target_summoned"]

    mood = Sentience.getPrimaryMood()
    agreeability = \
        Sentience.determineResponseAgreeability(
            Understanding.parse_sentence_subject_predicate(queries[0][0]) #TODO: handle multiple queries, parsed subject-predicate components can work well
        ) if queries else 0

    if subject_call is not None and queries == []:
        #greeting likely
        now = datetime.datetime.now()

        if mood > 0.3:
            if (6 <= now.hour <= 11) and 'morning' in words:
                return random.choice(['good morning', 'morning', 'おはよう']) + ('!' if mood > 0.75 else ('.' if mood < 0.5 else ''))
            if (19 <= now.hour <= 23 or now.hour <= 2) and 'night' in words:
                return random.choice(['good night', 'gn', 'おやすみ']) + ('.' if mood < 0.5 else '')

        if 'hello' in words or 'hi' in words:
            if mood > 0.75:
                return random.choice(['hello!', 'hi!', 'こんにちは!'])

        if mood <= 0.3:
            return random.choice(['bleh', 'o', 'meh', 'hmph'])

    c = len(list(filter(lambda x: x[1] == 'YN_QN', queries)))
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
    elif mood > 0.5 and Sentience.getExposedPositivity() > 0:
        if not tofu_targeted and (IDENTITY.lower() in words or IDENTITY.lower() == s.lower()) and random.random() <= 0.1:
            return random.choice(['hmm i heard my name', 'hmmmm', 'interesting', 'hm'])
        elif len(words) <= 5:
            combos = get_message_combos()
            for word in words:
                for w in [word, Understanding.remove_repeated_chars_word(word)]:
                    if w in combos:
                        if tofu_tagged or random.random() <= combos[w][1]:
                            return random.choice(combos[w][0])

    return None
