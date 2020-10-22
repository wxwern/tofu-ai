from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import twitter_samples, stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk import FreqDist, classify, NaiveBayesClassifier
import re, string, random
import pickle
stop_words = stopwords.words('english')

def saveClassifier(classifier):
    f = open('sentiment_classifier.pickle', 'wb')
    pickle.dump(classifier, f)
    f.close()

def loadClassifier():
    global __classifier
    try:
        f = open('sentiment_classifier.pickle', 'rb')
        __classifier = pickle.load(f)
        f.close()
    except:
        __classifier = None

loadClassifier()

def __getClassifier():
    return __classifier

def isWordPositive(word):
    classifier = __getClassifier()
    if classifier is None:
        return False
    custom_tokens = __remove_noise([word])
    return __classifier.classify(dict([token, True] for token in custom_tokens)) == 'Positive'

def isSentencePositive(sentence):
    classifier = __getClassifier()
    if classifier is None:
        return False
    custom_tokens = __remove_noise(word_tokenize(sentence))
    return classifier.classify(dict([token, True] for token in custom_tokens)) == 'Positive'

def getSentencePositivity(sentence):
    classifier = __getClassifier()
    if classifier is None:
        #fallback to random if without training data
        return random.uniform(-1.0, 1.0)

    pos = 0
    total = 0
    for word in word_tokenize(sentence):
        if word.lower() in stop_words:
            continue

        if isWordPositive(word):
            pos += 1
        total += 1

    if total == 0:
        return 0.0

    if total <= 1 or isSentencePositive(sentence):
        return pos/total
    else:
        return -(1-pos/total)


def __remove_noise(tweet_tokens, stop_words = ()):

    cleaned_tokens = []

    for token, tag in pos_tag(tweet_tokens):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        token = re.sub("(@[A-Za-z0-9_]+)","", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)

        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            cleaned_tokens.append(token.lower())
    return cleaned_tokens

def __get_all_words(cleaned_tokens_list):
    for tokens in cleaned_tokens_list:
        for token in tokens:
            yield token

def __get_tweets_for_model(cleaned_tokens_list):
    for tweet_tokens in cleaned_tokens_list:
        yield dict([token, True] for token in tweet_tokens)

if __name__ == "__main__":


    if __classifier is not None:
        print('train __classifier [t] or use previous [p]?')

    if __classifier is None or (str(input()) + ' ').lower()[0] == 't':
        positive_tweets = twitter_samples.strings('positive_tweets.json')
        negative_tweets = twitter_samples.strings('negative_tweets.json')
        text = twitter_samples.strings('tweets.20150430-223406.json')
        tweet_tokens = twitter_samples.tokenized('positive_tweets.json')[0]


        positive_tweet_tokens = twitter_samples.tokenized('positive_tweets.json')
        negative_tweet_tokens = twitter_samples.tokenized('negative_tweets.json')

        positive_cleaned_tokens_list = []
        negative_cleaned_tokens_list = []

        for tokens in positive_tweet_tokens:
            positive_cleaned_tokens_list.append(__remove_noise(tokens, stop_words))

        for tokens in negative_tweet_tokens:
            negative_cleaned_tokens_list.append(__remove_noise(tokens, stop_words))

        all_pos_words = __get_all_words(positive_cleaned_tokens_list)

        freq_dist_pos = FreqDist(all_pos_words)
        print(freq_dist_pos.most_common(10))

        positive_tokens_for_model = __get_tweets_for_model(positive_cleaned_tokens_list)
        negative_tokens_for_model = __get_tweets_for_model(negative_cleaned_tokens_list)

        positive_dataset = [(tweet_dict, "Positive")
                             for tweet_dict in positive_tokens_for_model]

        negative_dataset = [(tweet_dict, "Negative")
                             for tweet_dict in negative_tokens_for_model]

        dataset = positive_dataset + negative_dataset

        random.shuffle(dataset)

        train_data = dataset[:7000]
        test_data = dataset[7000:]

        __classifier = NaiveBayesClassifier.train(train_data)
        print("Accuracy is:", classify.accuracy(__classifier, test_data))

        saveClassifier(__classifier)

    print(__classifier.show_most_informative_features(10))

