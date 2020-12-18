import time
import datetime
import random
import math

from sentiment_analysis import getSentencePositivity

class Sentience:

    __IDENTITY = 'tofu'
    @staticmethod
    def getIdentity():
        """Returns identity of script, the name it goes by. This should be a single word."""
        return Sentience.__IDENTITY.lower()

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

        # recompute exposed positivity as exponential of degree 3, adjustable by how stable the mood is
        exp_pos = Sentience.getExposedPositivity()
        if exp_pos < 0:
            exp_pos = (exp_pos**3) * (1-Sentience.getMoodStability())
        else:
            exp_pos = exp_pos**3 * Sentience.getMoodStability()

        mood = 0.3 + date_moodadj*0.2 + time_moodadj*0.5 + exp_pos*0.25
        return max(-1.0, min(mood, 1.0))

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

    __exposed_positivity = 0.0
    __last_message_exposure = 0.0
    __positivity_overload = False
    @staticmethod
    def getExposedPositivity(unlimited=False):
        """
        Returns exposed positivity over time from messages.

        Exposed positivity decays with varying half life. As a rule of thumb, negativity decays slower than positivity.

        Output ranges is capped between [-1.0, 1.0], unless the unlimited argument is set to True.
        """

        if Sentience.__positivity_overload:
            Sentience.__exposed_positivity = -abs(Sentience.__exposed_positivity)

        #half life factor computation
        half_life_ctrl = 0.3 if Sentience.__positivity_overload else (0.5 if Sentience.__exposed_positivity < 0 else 1.2)
        half_life_factor = max(0.0, min(2**(min(0.0, (Sentience.__last_message_exposure - time.time())/60)*half_life_ctrl), 1.0))

        #recompute current exposed positivity
        Sentience.__exposed_positivity = max(-1.5, min(Sentience.__exposed_positivity, 2.0)) * half_life_factor
        Sentience.__last_message_exposure = time.time()

        if Sentience.__exposed_positivity > -0.5:
            Sentience.__positivity_overload = False

        return Sentience.__exposed_positivity if unlimited else max(-1.0, min(Sentience.__exposed_positivity, 1.0))

    @staticmethod
    def isExposedPositivityOverloaded():
        """
        Returns whether there is too much exposed positivity.
        When this is True, most gained positivity and negativity will have minimal effect on the final exposed positivity.
        """

        Sentience.getExposedPositivity() #preprocess current positivity, which will update whether positivity overload is in effect

        return Sentience.__positivity_overload

    @staticmethod
    def _addExposedPositivity(x):
        """
        Updates exposed positivity value.
        """
        current_pos = Sentience.getExposedPositivity(unlimited=True)
        if not Sentience.__positivity_overload:
            current_pos += x*(0.3*max((1-abs(current_pos))**2, 0.1))
        else:
            current_pos += -abs(max(-0.05, min(x*0.3, 0.001)))

        Sentience.__exposed_positivity = current_pos
        if Sentience.__exposed_positivity > 0.5 + Sentience.getMoodStability():
            Sentience.__positivity_overload = True

    __DEF_PROB_THRESHOLD = 0.02
    @staticmethod
    def _cleanupPositivityValue(v):
        if v is None:
            return None
        if abs(v) <= abs(Sentience.__DEF_PROB_THRESHOLD) + 0.00001:
            return 0
        return v

    @staticmethod
    def _determineMessagePositivityWrapper(message, overall=True):
        if isinstance(message, tuple):
            subject, predicate = tuple(map(lambda x: ' '.join(map(lambda y: y[0], x)), message))
            if overall:
                message = (subject + ' ' + predicate).strip()
            else:
                res_subj = Sentience._cleanupPositivityValue(getSentencePositivity(subject))
                res_pred = Sentience._cleanupPositivityValue(getSentencePositivity(predicate))

                if res_subj is None or res_pred is None:
                    return None

                if res_subj > -0.15:
                    #subject is neutral or positive, agree if predicate is positive
                    return res_pred

                #subject is negative, agree if predicate is negative
                return res_pred * -1

        if not isinstance(message, str):
            try:
                return max(-1.0,min(float(message), 1.0))
            except ValueError:
                return 0

        if not message.strip():
            return 0.0

        res = getSentencePositivity(message)
        return Sentience._cleanupPositivityValue(res)

    @staticmethod
    def determineMessagePositivity(message):
        """
        Returns the overall positivity (sentiment) of message.

        For example, "I'm really happy" yields positive.

        The parameter accepts a message in a string format or a message tokenized
        and split into subject-predicate form with Understanding.

        Messages that are tokenized and split into subject-predicate form are
        usually more accurate.

        Output ranges between [-1.0, 1.0], with -1.0 being most negative and 1.0
        being most positive.
        """
        return Sentience._determineMessagePositivityWrapper(message, overall=True)

    @staticmethod
    def determineMessageValidity(message):
        """
        Returns validity of the message based of whether the sentiment in it
        is contradictory.

        The parameter accepts a message in a string format or a message tokenized
        and split into subject-predicate form with Understanding.

        Messages that are tokenized and split into subject-predicate form are
        usually more accurate.

        Unlike determineMessagePositivity, this checks whether the positivity of
        parts of the sentence itself agrees with each other. For example,
        "losing is sad" would be negative, but it is valid in the sense that
        "losing" and "sad" are negative and does not contradict. This processing
        only works if a subject-predicate tokenized input is provided.

        Output ranges between [-1.0, 1.0], with -1.0 being most invalid and 1.0
        being most valid.
        """
        return Sentience._determineMessagePositivityWrapper(message, overall=False)


    @staticmethod
    def preloadPositivityClassifier():
        """Preloads the classifier used to determine whether a sentence is positive or negative."""
        Sentience.__DEF_PROB_THRESHOLD = getSentencePositivity("!@#$%^&*")

    @staticmethod
    def determineResponseAgreeability(message):
        """
        Returns how much to 'agree' with a message received with the given message.
        The parameter accepts a message in a string format or tokenized and split into subject-predicate form with Understanding.

        Also updates exposed positivity.

        Output ranges are between [-1.0, 1.0]
        """

        message_positivity = Sentience.determineMessagePositivity(message)
        message_validity = Sentience.determineMessageValidity(message)
        if message_validity is None:
            random.seed(time.time())
            message_validity = random.uniform(-1.0,1.0)
            message_positivity = message_validity

        Sentience._addExposedPositivity(message_positivity)

        #compute random deviation from current time
        random.seed(time.time())
        deviation = random.uniform(-0.5,0.5) * (1-Sentience.getMoodStability())

        tofu_mood = Sentience.getPrimaryMood()

        #return result
        result = max(-1.0, min(
            (tofu_mood + Sentience.getExposedPositivity()*0.25 + deviation)*(message_validity),
        1.0))
        return result

    @staticmethod
    def getDebugInfo():
        return "Current Mood Positivity : %6.1f%%;\nMood Stability          : %6.1f%%;\nExposed Positivity      : %6.1f%%%s;" % \
            (Sentience.getPrimaryMood()*100, Sentience.getMoodStability()*100, Sentience.getExposedPositivity()*100, " (positivity overload)" if Sentience.isExposedPositivityOverloaded() else "")

    @staticmethod
    def getDebugInfoAfterMessage(message):
        if not message:
            return "%s\nOrigin Msg Positivity   : N/A;\nAgrees w/ Origin        : N/A;" % \
                (Sentience.getDebugInfo())

        ori_pos   = Sentience.determineMessagePositivity(message)
        ori_valid = Sentience.determineMessageValidity(message)
        res_agree = Sentience.determineResponseAgreeability(message)

        if ori_pos is None:
            return "%s\nERROR_CLASSIFIER_MISSING;\nAgrees w/ Origin        : %6.1f%%;" % \
                (Sentience.getDebugInfo(), res_agree*100)
        else:
            return "%s\nOrigin Msg Positivity   : %6.1f%%;\nOrigin Msg Validity     : %6.1f%%;\nAgrees w/ Origin        : %6.1f%%;" % \
                (Sentience.getDebugInfo(), ori_pos*100, ori_valid*100, res_agree*100)

Sentience.preloadPositivityClassifier()

if __name__ == "__main__" :
    print(Sentience.getDebugInfo())
