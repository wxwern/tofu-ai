import random
import datetime
import json

from nltk.tokenize.casual import casual_tokenize

from positivity import Sentience
from queries import Understanding


IDENTITY = Sentience.getIdentity()

__message_combos_cache = {}
def _get_message_combos():
    global __message_combos_cache
    if not __message_combos_cache:
        message_combos = [
                (['ping'], ['pong', 'pong ping?', 'pong?', 'pong'], 0.9),
                (['pong'], ['ping', 'ping pong' , 'pong?', 'ping'], 0.9),
                (['hi', 'hello', 'helo', 'halo', 'hola', 'hai', 'hoi'], ['hello!', 'hi!', 'こんにちは!'], 0.2),
                (['oof'], ['oof'], 0.2),
                ([':D', ':)', '(:', ':-)', ':>'], [':)', ':D'], 0.2),
                (['xd', 'lol', 'lmao', 'lmfao', 'haha'], ['lol', 'haha', 'ahaha', 'heh', 'lol', 'hm yes very funny', 'XD'], 0.15)
        ]

        for words, responses, chance in message_combos:
            for word in words:
                __message_combos_cache[word] = (responses, chance)

    return __message_combos_cache

class Responder:

    @staticmethod
    def process_debug_output(s):
        D_STRUCTURE = s.startswith("!DEBUG_STRUCTURE")
        D_SENTIENCE = s.startswith("!DEBUG_SENTIENCE")
        D_QUERIES_VB = s.startswith("!DEBUG_QUERIES_VB")
        D_QUERIES = s.startswith("!DEBUG_QUERIES")

        debug = False
        if s.startswith("!DEBUG"):
            debug = True
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

        if D_QUERIES_VB:
            return 'Sentence Queries: `%s`' % str(Understanding.parse_queries(s, merge_results=True))

        if D_QUERIES:
            res = Understanding.parse_queries(s, merge_results=True)
            res["queries"] = list(map(lambda x: (Understanding.unparse_sentence(x[0]), x[1]), res["queries"]))
            res["statements"] = list(map(lambda x: (Understanding.unparse_sentence(x[0]), x[1]), res["statements"]))
            if res["subject_call"] is not None:
                res["subject_call"] = Understanding.unparse_sentence(res["subject_call"])
            return 'Sentence Queries: `%s`' % str(res)

        if debug:
            return 'Invalid debug call'

        return None

    @staticmethod
    def get_info(d):
        '''
        Retrieves data using the given json as parameters. Returns a json string.

        Accepts json input in the format:
        ```
        {
            "type"     : "status" | "private message" | "group message" | "no-spam message" | "readonly message" | "message",
            "contents"?: string
        }
        ```

        Types are:
        - `"message"                `: default for chats; respond sometimes if possible.
        - `"readonly message"       `: only reads messages; never respond.
        - `"no-spam message"        `: for non-spam/non-bot chats; only respond if called by name.
        - `"group message"          `: optimized for bot group chats; respond sometimes if possible.
        - `"private message"        `: optimized for bot direct messages; always try to respond.


        Returns a json output in the format:
        ```
        {
            "primaryMood"        : number,
            "moodStability"      : number,
            "exposedPositivity"  : number,
            "positivityOverload" : bool,
            "response"           : string | null
        }
        ```
        or, if an error occurs:
        ```
        {
            "error"              : string,
            "response"           : string | null
        }
        ```
        '''
        err = {}
        res = {"response": None}
        info = {}
        try:
            data = json.loads(d)
            t = data["type"].lower()
            if t == "status":
                info = Sentience.getDebugInfoDict()
                return json.dumps({**info, **res})

            autoanswer_level = 0
            contents = str(data["contents"] if "contents" in data else None)
            if t == "no-spam message":
                autoanswer_level = 1
            if t == "readonly message":
                autoanswer_level = 0
            if t in ("group message", "message"):
                autoanswer_level = 2
            if t == "private message":
                autoanswer_level = 4
        except:
            err = {"error": "malformed data"}
            res["response"] = None

        try:
            if not err and "message" in t:
                res["response"] = Responder.generate_response(contents, autoanswer_level=autoanswer_level)
        except:
            err = {"error": "generated response is invalid"}
            res["response"] = None

        if not err:
            info = Sentience.getDebugInfoDict()
        return json.dumps({**err, **res, **info})


    @staticmethod
    def generate_response(s, autoanswer_level=2):
        '''
        Generates a response for the given message with the autoanswer_level (default 1).

        autoanswer_level:
        - 0: Do not answer except for debug calls
        - 1: Only respond if called by name
        - 2: Respond sometimes if confident
        - 3: Respond whenever possible
        - 4: Always respond
        '''

        debug_out = Responder.process_debug_output(s)
        if debug_out:
            return debug_out

        #
        # SENTENCE PARSING
        #

        words = casual_tokenize(s.lower(), reduce_len=True)
        parsed_result = Understanding.parse_queries(s, merge_results=True)

        subject_call = parsed_result["subject_call"]
        queries = parsed_result["queries"]
        statements = parsed_result["statements"]
        tofu_tagged = Understanding.is_target_tagged(s)
        tofu_targeted = parsed_result["target_summoned"] or autoanswer_level >= 3

        query_types = set(map(lambda x: x[1], queries))
        too_complicated = len(query_types) > 1 or len(queries) > 4

        Sentience.exposeToMessage(s)
        mood = Sentience.getPrimaryMood()

        if autoanswer_level == 0:
            return None

        #
        # Greetings
        #
        if subject_call is not None and queries == [] and statements == [] and tofu_targeted:
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

        #
        # Query answering
        #

        if too_complicated:
            if tofu_targeted:
                return random.choice([
                    "i'm confused",
                    "interesting question",
                    "uh.. i am confused",
                    "i don't understand what you mean",
                    "this sentence is too complicated for me to understand",
                    "this question is too confusing for me"
                    "hmm",
                ])
            return None

        if 'STD_QN' in query_types and tofu_targeted:
            return random.choice([
                "sorry, this question is not within my capabilities to answer",
                "i can't answer that yet oops",
                "sorry, the question is too open-ended for me",
                "i don't know how to answer that, am weak in FRQs sry",
                "i'm not smart enough to know how to answer that",
                "that sounds like an interesting question",
                "hmm",
            ])

        if 'YN_QN' in query_types and (autoanswer_level >= 2 or tofu_targeted):
            filtered_queries = list(filter(lambda x: x[1] == 'YN_QN', queries))
            if len(filtered_queries) == 1:
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
                    "i'd say yes"
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
                    "not at all"
                ])
                rnd_opt = random.choice([
                    "i'm not sure about that",
                    "bleh",
                    "interesting question",
                    "i don't wanna tell you right now",
                    "i don't have a clue",
                    "hmmm",
                    "my sources cannot be trusted"
                ])

                chosen = Sentience.decideResponseAgree(filtered_queries[0][0])
                if chosen is None:
                    return rnd_opt
                return yes_opt if chosen else no_opt

            if len(filtered_queries) == 2:
                opt_1 = random.choice([
                    "first option",
                    "go with the first",
                    "the former"
                ])
                opt_2 = random.choice([
                    "second option",
                    "on second thought, your second option",
                    "the latter"
                ])
                opt_nil = random.choice([
                    "why not both",
                    "i can't find the answer to that",
                    "i think neither",
                    "can't decide, so i'll say yes"
                ])
                subj, pred1 = Understanding.parse_sentence_subject_predicate(filtered_queries[0][0])
                _   , pred2 = Understanding.parse_sentence_subject_predicate(filtered_queries[1][0])
                chosen = Sentience.decideResponseOptionsIndex(subj, [pred1, pred2])
                if chosen == 0:
                    return opt_1
                if chosen == 1:
                    return opt_2
                return opt_nil

            if len(filtered_queries) > 2 and tofu_targeted:
                subject = None
                options = []
                for query, _ in filtered_queries:
                    res = Understanding.parse_sentence_subject_predicate(query)
                    if subject is None:
                        subject = res[0]
                    options.append(res[1])
                chosen = Sentience.decideResponseOptionsIndex(subject, options)
                if chosen is None:
                    return random.choice([
                        "i can't decide",
                        "am a little confused here",
                        "not sure which one"
                    ])
                return random.choice([
                    "option %d it is",
                    "i'll pick option %d",
                    "i think option %d",
                    "option %d"
                ]) % (chosen+1)


        #
        # Misc responses
        #
        if mood > 0.5 and Sentience.getExposedPositivity() >= 0 and autoanswer_level >= 1:
            if not tofu_targeted and (IDENTITY.lower() in words or IDENTITY.lower() == s.lower()) and random.random() <= 0.1:
                return random.choice(['hmm i heard my name', 'hmmmm', 'interesting', 'hm'])
            if len(words) <= 5:
                combos = _get_message_combos()
                for word in words:
                    for w in [word, Understanding.remove_repeated_chars_word(word)]:
                        if w in combos:
                            w_response, w_response_chance = combos[w]
                            if autoanswer_level >= 3:
                                w_response_chance **= 0.5
                            if (tofu_tagged or random.random() <= w_response_chance):
                                return random.choice(w_response)

        roll = random.random()
        if autoanswer_level >= 4 or (autoanswer_level >= 2 and roll > 0.95) or (tofu_targeted and roll > 0.75):
            if mood >= 0.3:
                x = Sentience.determineMessagePositivity(s)
                if x >= 0.6:
                    return random.choice([
                        'ay',
                        'nice',
                        ':D',
                        'yay',
                        'heh',
                        'haha',
                        'lol',
                    ])

                if x < 0:
                    return random.choice([
                        'oof',
                        'ono',
                        'uh',
                        'oops',
                        'sad',
                        ':(',
                        '.-.',
                    ])

                return random.choice([
                    'hmm',
                    'ah',
                    'hm',
                    'oof',
                    'interesting',
                ])


            return random.choice(['o', 'meh', 'm', '.'])

        return None
