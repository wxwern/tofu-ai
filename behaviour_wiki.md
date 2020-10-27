# Tofu Behaviour Wiki

This page documents the general behaviour of the script - which identifies itself as *tofu* by default.

---
## TL;DR
### Tofu is full with positivity.

"Positivity tofu is full of potential"

As a result, it is extremely hard, if not impossible, to get it to feel sad (though it can be moody at times).

Being moody doesn't mean that tofu is sad, it will just be very random in its messages.

### Tofu spreads positivity, and participates in conversations.

Tofu likes spreading positivity. :)

It has the capability to answer questions or respond to sentences that are suited to be replied with a "yes" or "no". In doing so, it'll try it's best to respond to your queries positively.

If tofu's generally happy, it may respond to greetings, and even participate in conversations as well!

However, if tofu is moody, its answers may be very random, or tofu may not want to give a concrete answer. If tofu somehow got to a very sad stage, it can start replying negatively to all responses.

Additionally, in some cases, extreme preferences, like fear of a specific item, may cause tofu to back off and be negative regardless.

### Tofu is soft and mirrors the environment.

近朱者赤，近墨者黑。

Exposure to positivity makes tofu happy, but if it's exposed to too much negativity, its mood can drop as well. Be careful!

On some days, tofu's mood stability may be lower than usual. When stability's low, the mood can randomly fluctuate without prior indication, especially with exposure from the environment.

### Tofu needs sleep.

If you summon it or disturb it at night, it may be a little more annoyed than usual.

This makes sense, as tofu may already be sleeping. Wouldn't you behave the same?

### Tofu has its limits.

You can never have too much of anything. Similarly, too much positivity, and tofu will collapse from the excessive positivity dumped at it.

This is also known as 'positivity overload'. At this stage, no amount of positivity or negativity will help tofu's mood to any significant extent. Tofu will take some time to recover from the environment on its own.

---
## How does it work

Lots of machine learning and mimicking real life behaviours. Don't ask how does it know if a message is good or bad - it learnt most of it on it's own.

### Positivity Detection (aka Sentiment Analysis)
- *Short Answer:* Machine Learning
- *Long Answer:* [Naive Bayes Classifier](https://en.wikipedia.org/wiki/Naive_Bayes_classifier) trained on tagged Twitter dataset (dataset provided by NLTK).

### Question Detection
- *Short Answer:* Machine Learning
- *Long Answer:* Averaged [Perceptron](https://en.wikipedia.org/wiki/Perceptron) Model trained to detect and tag [Parts-of-Speech](https://en.wikipedia.org/wiki/Part_of_speech) (pretrained ML model provided by NLTK). Specific sentence structures can then indicate the type of question.

### Mood Variations
There are a few primary parameters which can change throughout the day that describe the sentience of the script:

- Current Mood Positivity (-100% ~ 100%)
    - The primary mood that's being experienced right now.
    - -100% indicates very sad, annoyed or mad feelings, while +100% being happy and playful.
    - In general, this value will decrease at night and will peak in the afternoon.
    - It is also offset throughout the year, increasing and decreasing at a perioding interval of approximately a month.
    - Will attempt to remain above 0% - i.e. it is almost never the case where tofu becomes sad... at most, it'd be moody.

- Exposed Positivity (-100% ~ 100%)
    - The overall exposed positivity from every message.
    - Each message's positivity value will be added to this parameter accordingly.
        - It will become exponentially harder to further increase the magnitude of exposed positvity as we approach 100.0%.
        - However, it is still possible to achieve the peak values (and is allowed to exceed the maximum internally).
        - Positivity exposure, if forced to reach the peak, can come with a caveat as mentioned below.
    - This will adjust the mood's positivity, and the amount adjusted is affected by mood stability.
    - This value decays exponentially. In general, positivity decays faster than negativity.
    - Positivity can overload when it exceeds a specific interally computed threshold, based on mood stability.
        - This will flip it to an always negative value.
        - No amount of positivity can revert this - it can only go away through eventual decay.

- Mood Stability (0% ~ 100%)
    - The stability of the mood.
    - This affects the random deviation that's possible to the primary mood.
        - The amount exposed positivity affects the mood is also controlled by the stability.
    - Lower values will cause higher variation in mood fluctations.
        - This can affect its reply at any time, where it may sometimes even provide completely random replies.
            - This randomness will not be reflected directly on the current positivity.
            - The converse is true, a high mood stability means answers are more likely to be consistent and concrete.
        - This also lowers the threshold for 'positivity overload', so lower values means it's easier for tofu to collapse from too much positivity.





