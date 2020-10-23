# message-autoresponder

An NLTK powered script to allow for random automated responses to certain categories of messages.

It can automatically determine whether a message matches a supported category, and if so craft a response.
```bash
$ ./main.py reply "hmm i'm bored"
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


Useful for just-for-fun chatbots and the like.

It identifies itself as 'tofu', and will attempt to also respond to messages that addresses 'tofu' as the subject. [WIP]

Currently supported:
- Yes/No inquiries, e.g. "Should I go do my work instead of procastinating?"
- Selecting an option from a pair of options, e.g. "Should I sleep or study?"
- Ability to recognise sentence sentiment and provide a positive response.
- It has its own mood at any point in time and can have mood swings.
- Can be affected by positivity/negativity of exposed messages.
- Random, e.g. "nice", ":)"


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

Replies:
```bash
$ ./main.py reply "should i go for a walk"
perhaps
$ ./main.py reply "may i answer the call"
my sources say no
$ ./main.py reply "hi tofu will i be lucky today"
most definitely
$ ./main.py reply "i have been bamboozled" # does not provide a response as it is not within a supported message category
$ ./main.py reply "hey tofu should i watch a movie or read a book"
the latter
$
```
Direct input/output:
```bash
$ ./main.py chat # starts a 'chat' interface where the user uses cli input and the responses would be the cli output
should i stop working on this project
nah
hmm very nice
will this take off
maybe
```

\* When using `chat`, one line of input always corresponds to one line of output, so you can use standard input and output to process live data.

Query category info:
```bash
$ ./main.py countyn "should i sleep or study" # gets number of separate options that could be answered as yes/no individually
2
$ ./main.py countyn "wow that's great"
0
$
```
Process chat history (format: `[<datetime>] <user>: <message>`)
```bash
$ ./main.py emulate message_history.txt
- john:
would it rain today

* BOT tofu2 (emulated autoreply):
nah

```

Retrain Sentiment Analysis Model:
```bash
$ python3 sentiment_analysis.py
```
