import time
import datetime
import random
import math

from sentiment_analysis import getSentencePositivity

class Sentience:

    @staticmethod
    def getPrimaryMood():
        """
        Returns primary mood as of the current time.
        Ranges between [-1.0, 1.0], with -1.0 being very sad/annoyed/mad, 0.0 being neutral and 1.0 being very happy
        """
        now = datetime.datetime.now()

        # sin curve, best mood during noon 2pm, worst mood during midnight 2am.
        time_offset = max(0.0, min(((now.hour*60 + now.minute - 120) % 1440)/(1440), 1.0))
        time_moodadj = math.sin(time_offset*math.pi)

        # approximately monthly cos curve where middle of the month is moody
        date_offset = max(0.0, min(((now.month-1)*30 + (now.day-1))/360, 1.0))
        date_moodadj = math.cos(date_offset*(12*math.pi))

        mood = 0.1 + date_moodadj*0.3 + time_moodadj*0.6
        return mood

    @staticmethod
    def getMoodStability():
        """
        Returns stability of mood as of today.
        Output ranges between [0.0, 1.0], with 1.0 indicating most stable.
        """
        now = datetime.datetime.now()
        random.seed(int((now.month-1)*30 + (now.day-1) + 1))
        ans = random.uniform(0.1,0.6) + random.uniform(0.1,0.4)
        random.seed(time.time())
        return ans

    exposed_positivity = 0.0
    last_message_exposure = 0.0
    @staticmethod
    def getExposedPositivity():
        """
        Returns exposed positivity over time from messages.
        Exposed positivity decays with a half life of 1 minute.
        Output ranges from [-1.0, 1.0].
        """

        #half life factor
        factor = max(0.0, min(2**min(0.0, (Sentience.last_message_exposure - time.time())/60), 1.0))

        #recompute current exposed positivity
        Sentience.exposed_positivity = max(-1.0, min(Sentience.exposed_positivity, 1.0))*factor
        Sentience.last_message_exposure = time.time()

        return Sentience.exposed_positivity

    @staticmethod
    def _addExposedPositivity(x):
        """
        Updates exposed positivity value.
        """
        Sentience.exposed_positivity = Sentience.getExposedPositivity() + x*0.3

    @staticmethod
    def determineMessagePositivity(message):
        """
        Returns positivity of message.
        Output ranges between [-1.0, 1.0], with -1.0 being most negative and 1.0 being most positive.
        """
        if not isinstance(message, str):
            try:
                return max(-1.0,min(float(message), 1.0))
            except:
                return 0

        if not message.strip():
            return 0.0

        return getSentencePositivity(message)

    @staticmethod
    def preloadPositivityClassifier():
        """Preloads the classifier used to determine whether a sentence is positive or negative."""
        getSentencePositivity("dummy text")

    @staticmethod
    def determineResponseAgreeability(message_positivity=0.0):
        """
        Returns how much to 'agree' with a message received with the given positivity (defaults to neutral).

        Also updates exposed positivity.

        Output ranges are between [-1.0, 1.0]
        """

        if isinstance(message_positivity, str):
            message_positivity = Sentience.determineMessagePositivity(message_positivity)

        if message_positivity is None:
            random.seed(time.time())
            message_positivity = random.uniform(-1.0,1.0)

        Sentience._addExposedPositivity(message_positivity)

        #compute random deviation from current time
        random.seed(time.time())
        deviation = random.uniform(-1.0,1.0) * (1-Sentience.getMoodStability())

        tofu_mood = Sentience.getPrimaryMood()

        #return result
        return max(-1.0, min(
            (tofu_mood + Sentience.getExposedPositivity()*0.25 + deviation)*(message_positivity),
        1.0))

    @staticmethod
    def getDebugInfo():
        return "Current Mood Positivity : %6.1f%%;\nMood Stability          : %6.1f%%;\nExposed Positivity      : %6.1f%%;" % \
            (Sentience.getPrimaryMood()*100, Sentience.getMoodStability()*100, Sentience.getExposedPositivity()*100)

    @staticmethod
    def getDebugInfoAfterMessage(message):
        if not message.strip():
            return "%s\nOrigin Msg Positivity   : N/A;\nAgrees w/ Origin        : N/A;" % \
                (Sentience.getDebugInfo())

        ori_pos = Sentience.determineMessagePositivity(message)
        res_pos = Sentience.determineResponseAgreeability(message_positivity=ori_pos)

        if ori_pos == None:
            return "%s\nOrigin Msg Positivity   : ERROR_CLASSIFIER_MISSING;\nAgrees w/ Origin        : %6.1f%%;" % \
                (Sentience.getDebugInfo(), res_pos*100)
        else:
            return "%s\nOrigin Msg Positivity   : %6.1f%%;\nAgrees w/ Origin        : %6.1f%%;" % \
                (Sentience.getDebugInfo(), ori_pos*100, res_pos*100)

Sentience.preloadPositivityClassifier()

if __name__ == "__main__" :
    print(Sentience.getDebugInfo())
