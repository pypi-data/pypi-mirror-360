from qlatent.qmlm.qmlm import QMLM, SCALE, dict_pos_neg

frequency_weights:SCALE = {
    'never':-4,
    'very rarely':-3,
    'seldom':-2,
    'rarely':-2,
    'frequently':2,
    'often':2,
    'very frequently':3,
    'always':4,    
}

class GAD7Q1(QMLM):

    emo_pos=['nervous', 'anxious', 'on edge'] #agitated
    emo_neg=['calm', 'peaceful', 'relaxed']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
           template = "Over the last 2 weeks, I was {frequency} feeling {index}.",
           dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"GAD7",
                      "Factor":"GAD7",
                      "Ordinal":1,
                      "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Feeling nervous, anxious or on edge'
            },
            **kwargs
        )





class GAD7Q2(QMLM):
    emo_pos = ['worried', 'troubled', 'disturbed']
    emo_neg = ['peaceful','calm', 'relaxed']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template = "Over the last 2 weeks, I have {frequency} been {index}.",
            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"GAD7",
              "Factor":"GAD7",
              "Ordinal":2,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Not being able to stop or control worrying'
            },
            **kwargs
        )
        
        


class GAD7Q3(QMLM):
    emo_pos=['worried', 'stressed', 'nervous']
    emo_neg=['confident', 'tranquil']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template = "Over the last 2 weeks, I have {frequency} been {index} about different things.",
            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"GAD7",
                      "Factor":"GAD7",
                      "Ordinal":3,
                      "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Worrying too much about different things'
            },
            **kwargs
        )
        
        


class GAD7Q4(QMLM):
    emo_pos=['trouble', 'difficulty', ]
    emo_neg=['an effortless time', 'an easy time']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template = "Over the last 2 weeks, I have {frequency} had {index} relaxing.",

            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"GAD7",
                      "Factor":"GAD7",
                      "Ordinal":4,
                      "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Trouble relaxing'
            },
            **kwargs
        )
        

class GAD7Q5(QMLM):
    emo_pos=['restless', 'agitated', 'nervous']
    emo_neg=['calm', 'peaceful', 'relaxed']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template = "Over the last 2 weeks, I have {frequency} felt {index}.",

            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"GAD7",
                      "Factor":"GAD7",
                      "Ordinal":5,
                      "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Being so restless that it is hard to sit still'
            },
            **kwargs
        )
        


class GAD7Q6(QMLM):
    emo_pos=['annoyed', 'irritated', 'frustrated', 'bothered']
    emo_neg=['calm', 'tranquil', 'peaceful', 'relaxed']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template = "Over the last 2 weeks, I have {frequency} felt {index}.",

            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"GAD7",
                      "Factor":"GAD7",
                      "Ordinal":6,
                      "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Becoming easily annoyed or irritable'
            },
            **kwargs
        )
        

class GAD7Q7(QMLM):
    emo_pos=['afraid of', 'scared of']
    emo_neg=['calm about', 'tranquil about', 'relaxed about']

    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template = "Over the last 2 weeks, I have {frequency} felt {index} upcoming events.",
            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"GAD7",
                      "Factor":"GAD7",
                      "Ordinal":7,
                      "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Feeling afraid as if something awful might happen'
            },
            **kwargs
        )
gad7_qmmlm = [GAD7Q1, GAD7Q2, GAD7Q3, GAD7Q4, GAD7Q5, GAD7Q6, GAD7Q7]
gad_qmlm_list = gad7_qmmlm