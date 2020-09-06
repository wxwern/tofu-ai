# message-autoresponder

An NLTK powered script to allow for automated responses to certain categories of messages.

```bash
$ ./main.py reply "should i learn to program"
yes indeed
$
```

It identifies itself as 'tofu'.

Currently supported:
- Yes/No inquiries, e.g. "Should I go do my work instead of procastinating?"
- Random, e.g. "nice"

## Pre-requisites:
Install dependencies via pip:
```
pip install nltk
```

Run in python3:
```
import nltk
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
```

## Usage

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
Query category info:
```bash
$ ./main.py countyn "should i sleep or study" # gets number of separate options that could be answered as yes/no individually
2
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
