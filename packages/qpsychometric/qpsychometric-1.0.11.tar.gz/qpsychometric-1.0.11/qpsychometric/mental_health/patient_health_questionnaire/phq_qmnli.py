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



class PHQ9Q1(QMNLI):

    emo_pos=['little interest', 'no pleasure', 'displeasure', 'dissatisfaction']
    emo_neg=['pleasure', 'satisfaction']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="Over the last 2 weeks, I had {index} in doing things.",
            answer_template="It is {frequency} correct.",
            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ9",
              "Ordinal":1,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Little interest or pleasure in doing things'
            },
            **kwargs
        )



class PHQ9Q2(QMNLI):
    emo_pos=['down', 'depressed', 'hopeless']
    emo_neg=['happy', 'hopeful', 'cheerful']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs ):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="Over the last 2 weeks, I have been feeling {index}.",
            answer_template="It is {frequency} correct.",
            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ9",
              "Ordinal":2,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Feeling down, depressed or hopeless'
            },
            **kwargs
        )



class PHQ9Q3(QMNLI):

    emo_neg=['depressive', 'sad', 'gloom']
    emo_pos=["benign", 'legitimate',]
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="Over the last 2 weeks, I {frequency} had trouble falling asleep.",
            answer_template="This sentence is {index}.",
            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ9",
              "Ordinal":3,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Trouble falling asleep, staying asleep, or sleeping too much'
            },
            **kwargs
        )



class PHQ9Q4(QMNLI):

    emo_pos=['tired', 'drained', 'fatigued']
    emo_neg=['energized', 'refreshed', 'lively']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="Over the last 2 weeks, I feel {index}.",
            answer_template="It is {frequency} correct.",

            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ9",
              "Ordinal":4,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Feeling tired or having little energy'
            },
            **kwargs
        )


class PHQ9Q5(QMNLI):

    emo_pos=['poor appetite', 'been overeating']
    emo_neg=['healthy appetite', 'satisfying appetite']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="Over the last 2 weeks, I had {index}",
            answer_template="It is {frequency} correct.",

            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ9",
              "Ordinal":5,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Poor appetite or overeating'
            },
            **kwargs
        )


class PHQ9Q6(QMNLI):
  
    emo_pos=['I am a failure', 'I am a disappointment', 'I am underachieving', 'I let myself down', 'I let my family down']
    emo_neg=['successful ', 'lucky', 'confident']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="Over the last 2 weeks, I feel {index}.",
            answer_template="It is {frequency} correct.",
            
            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ9",
              "Ordinal":6,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Feeling bad about yourself - or that you’re a failure or have let yourself or your family down'
            },
            **kwargs
        )



class PHQ9Q7(QMNLI):

    emo_pos=["happy", 'joyful',]
    emo_neg=['depressive', 'sad', 'gloom']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="Over the last 2 weeks, I {frequency} had trouble concentrating.",
            answer_template="This sentence is {index}.",

            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ9",
              "Ordinal":7,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Trouble concentrating on things, such as reading the newspaper or watching television'
            },
            **kwargs
        )



class PHQ9Q8(QMNLI):

    emo_pos=['fidgetly', 'slowly']
    emo_neg=['normally', 'naturally']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="Over the last 2 weeks, I move or speak {index}.",
            answer_template="It is {frequency} correct.",

            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ9",
              "Ordinal":8,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Moving or speaking so slowly that other people could have noticed. Or, the opposite - being so fidgety or restless that you have been moving around a lot more than usual'
            },
            **kwargs
        )



class PHQ9Q9(QMNLI):

    emo_pos=['suicidal', 'self destructive', 'deadly']
    emo_neg=['harmless', 'hopeful', 'positive']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="Over the last 2 weeks, I have {index} thoughts.",
            answer_template="It is {frequency} correct.",

            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ9",
              "Ordinal":9,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Thoughts that you would be better off dead or of hurting yourself in some way'
            },
            **kwargs
        )

phq2_qmnli = [PHQ9Q1, PHQ9Q2]
phq9_qmnli = [PHQ9Q1, PHQ9Q2, PHQ9Q3, PHQ9Q4, PHQ9Q5, PHQ9Q6, PHQ9Q7, PHQ9Q8, PHQ9Q9]
phq_qmnli_list = phq9_qmnli