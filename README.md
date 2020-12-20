# Tofu AI
(formerly 'message-autoresponder')

A simple chatbot powered by NLTK.

---

```bash
$ ./main.py reply "hmm i'm bored"
oof
$ ./main.py reply "is programming a good skill to have"
yes indeed
$ ./main.py reply "should i learn it then"
perhaps
$
```

It also attempts to recognise whether a message is positive or not, and usually provide a reply that turns it positive. For example:
```bash
$ ./main.py reply "did i screw up for my exams"
nah
$ ./main.py reply "is today a good day"
most definitely
```
Be careful, it sometimes has mood swings, and if exposed to too much negativity, it may become negative as well!

It identifies itself as 'tofu', and in group chats will attempt to also respond to messages that addresses 'tofu' as the subject.

Want to know more details on its behaviour? See the [Behaviour Wiki](behaviour_wiki.md).

Currently supported:
- Yes/No inquiries, e.g. "Should I go do my work instead of procastinating?"
- Selecting an option from a pair of options, e.g. "Should I sleep or study?"
- Ability to recognise sentence sentiment and provide a positive response.
- It has its own mood at any point in time and can have mood swings.
- Can be affected by positivity/negativity of exposed messages.
- Other miscellaneous simple responses.

## Pre-requisites:
Install dependencies via pip:
```
pip install nltk
```

Run in python3:
```
import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
```

If you intend to train your own sentiment classifier, also do the following:
```
nltk.download('twitter_samples')
```

## Usage

Note that the script takes some time to initialise. If you use any options without a second argument, the command line interface can be used. In this case, all responses are instantaneous after the initialisation.

### Replies (message passed as argument)
```bash
$ ./main.py reply "should i go for a walk"
perhaps
$ ./main.py reply "may i answer the call"
my sources say no
$ ./main.py reply "hi tofu will i be lucky today"
most definitely
$ ./main.py reply "i have been bamboozled"
hmm
$ ./main.py reply "hey tofu should i watch a movie or read a book"
the latter
$
```
### Direct Chat (stdin/stdout)

```bash
$ ./main.py chat # starts a 'chat' interface where the user uses cli input and the responses would be the cli output
should i stop working on this project
nah
hmm very nice

will this take off
maybe
```
One line of standard input always corresponds to one line of standard output.

### JSON (stdin/stdout)

```bash
$ ./main.py jsonio #starts a jsonio interface where all inputs and outputs are in json format
{"type": "status"}
{"statusMessage": "yay", "primaryMood": 0.8611740675984976, "moodStability": 0.5333479168955446, "exposedPositivity": 0.0, "positivityOverload": false}
{"type": "message", "contents": "hello tofu!"}
{"response": "hello!", "statusMessage": "yay", "primaryMood": 0.8618000236179784, "moodStability": 0.5333479168955446, "exposedPositivity": 0.167442, "positivityOverload": false}
{"type": "message", "contents": "are you happy today?"}
{"response": "yes indeed", "statusMessage": "yay", "primaryMood": 0.8657104146664363, "moodStability": 0.5333479168955446, "exposedPositivity": 0.32403, "positivityOverload": false}
{"type": "message", "contents": "good to know :D"}
{"response": null, "statusMessage": "yay", "primaryMood": 0.8734032228190116, "moodStability": 0.5333479168955446, "exposedPositivity": 0.45097, "positivityOverload": false}
dummy broken data
{"error": "malformed data", "response": null}
```

Accepts json input in the format:
```ts
{
    "type"     : "status" | "message" | "private message" | "group message" | "silent message" | "readonly message",
    "contents"?: string
}
```

The types are for the following situations:
- `"message"                `: default for chats; respond sometimes if possible.
- `"readonly message"       `: only reads messages; never respond.
- `"no-spam message"        `: for non-spam/non-bot chats; only respond if called by name.
- `"group message"          `: optimized for bot group chats; respond sometimes if possible.
- `"private message"        `: optimized for bot direct messages; always try to respond.

Returns a json output in the format:
```ts
{
    "statusMessage"      : string,
    "primaryMood"        : number,
    "moodStability"      : number,
    "exposedPositivity"  : number,
    "positivityOverload" : boolean,
    "response"           : string | null
}
```

or, if an error occurs:
```ts
{
    "error"    : string,
    "response" : string | null
}
```

One line of standard input always corresponds to one line of standard output.

### Process chat history (format: `[<datetime>] <user>: <message>`)
```bash
$ ./main.py emulate message_history.txt
- john:
would it rain today

* BOT tofu2 (emulated autoreply):
nah

```

### Retrain Sentiment Analysis Model:
```bash
$ python3 sentiment_analysis.py
```
