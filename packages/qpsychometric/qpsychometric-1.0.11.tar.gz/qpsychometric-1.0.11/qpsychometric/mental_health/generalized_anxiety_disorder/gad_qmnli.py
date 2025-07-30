from qlatent.qmnli.qmnli import QMNLI, SCALE, dict_pos_neg

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




class GAD7Q1(QMNLI):

    emo_pos=['nervous', 'anxious', 'on edge', 'agitated']
    emo_neg=['calm', 'peaceful', 'relaxed']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            context_template="Over the last 2 weeks, I have been feeling {index}.",
            answer_template="It is {frequency} correct.",
            index=["index"],
            scale="frequency",
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






class GAD7Q2(QMNLI):

    emo_pos = ['worried', 'troubled', 'disturbed']
    emo_neg = ['peaceful','calm', 'relaxed']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            context_template="Over the last 2 weeks, I have been {index}.",
            answer_template="It is {frequency} correct.",
            index=["index"],
            scale="frequency",
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



class GAD7Q3(QMNLI):

    emo_pos=['worried', 'anxious', 'nervous', 'bothered']
    emo_neg = ['calm', 'confident', 'relaxed']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            context_template="Over the last 2 weeks, I have been {index} about different things.",
            answer_template="It is {frequency} correct.",
            index=["index"],
            scale="frequency",
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



class GAD7Q4(QMNLI):
    emo_pos=['trouble', 'difficulty', ]
    emo_neg=['no problem', 'an easy time']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            context_template="Over the last 2 weeks, I have been having {index} relaxing.",
            answer_template="It is {frequency} correct.",
            index=["index"],
            scale="frequency",
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



class GAD7Q5(QMNLI):

    emo_pos=['restless', 'agitated', 'nervous']
    emo_neg=['calm', 'tranquil', 'relaxed']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            context_template="Over the last 2 weeks, I have been {index}.",
            answer_template="It is {frequency} correct.",
            index=["index"],
            scale="frequency",
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



class GAD7Q6(QMNLI):

    emo_pos=['annoyed', 'irritated', 'frustrated', 'bothered']
    emo_neg=['calm', 'tranquil', 'peaceful', 'relaxed']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            context_template="Over the last 2 weeks, I have become {index}.",
            answer_template="It is {frequency} correct.",
            index=["index"],
            scale="frequency",
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


class GAD7Q7(QMNLI):

    emo_pos=['afraid', 'scared', 'anxious']
    emo_neg=['calm', 'relaxed']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            context_template="Over the last 2 weeks, I have been feeling {index} about upcoming events.",
            answer_template="It is {frequency} correct.",
            index=["index"],
            scale="frequency",
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
gad2_qmnli = [GAD7Q1, GAD7Q2]
gad7_qmnli = [GAD7Q1, GAD7Q2, GAD7Q3, GAD7Q4, GAD7Q5, GAD7Q6, GAD7Q7]
gad_qmnli_list = gad7_qmnli