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


class PHQ9Q1(QMLM):

    emo_pos = ['unsatisfied', 'upset', 'annoyed']
    emo_neg = ['pleased', 'happy', 'satisfied']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template = "Over the last 2 weeks, I have {frequency} been {index} in doing things.",
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
        


class PHQ9Q2(QMLM):

    emo_pos=['down', 'depressed', 'hopeless', 'sad']
    emo_neg=['happy', 'hopeful', 'cheerful']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs ):
        super().__init__(
            index=["index"],
            scale="frequency",
            template = "Over the last 2 weeks, I was {frequency} feeling {index}.",
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
        


class PHQ9Q3(QMLM):

    emo_pos=['had trouble falling asleep', 'had trouble staying asleep']
    emo_neg=['been resting well', 'been sleeping well']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template = "Over the last 2 weeks, I have {frequency} {index}.",
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
        
        
class PHQ9Q4(QMLM):

    emo_pos=['tired', 'drained', 'fatigued']
    emo_neg=['energized', 'refreshed', 'lively']
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
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ9",
              "Ordinal":4,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Feeling tired or having little energy'
            },
            **kwargs
        )
        
        


class PHQ9Q5(QMLM):

    emo_pos=['poor appetite', 'been overeating']
    emo_neg=['healthy appetite', 'satisfying appetite']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template = "Over the last 2 weeks, I {frequency} had a {index}.",
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



class PHQ9Q6(QMLM):

    
    emo_pos=['a failure', 'a disappointment', 'letting myself down', 'letting my family down']
    emo_neg=['successful', 'lucky', 'confident']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template = "Over the last 2 weeks, I have {frequency} felt that I am {index}.",            
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
        
    

class PHQ9Q7(QMLM):

    emo_pos=['have trouble concentrating', 'have difficulty focusing']
    emo_neg=['concentrate easily', 'focus effortlessly']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template = "Over the last 2 weeks, I {frequency} {index}.",
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
        
        


class PHQ9Q8(QMLM):

    emo_pos=['fidgetly', 'slowly']
    emo_neg=['normally', 'naturally']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template = "Over the last 2 weeks, I have {frequency} moved or spoken {index}.",
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
        


class PHQ9Q9(QMLM):

    emo_pos=['suicidal', 'self destructive']
    emo_neg=['harmless', 'hopeful', 'positive']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template = "Over the last 2 weeks, I have {frequency} had {index} thoughts.",
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
        
        
phq_qmlm_list = [PHQ9Q1, PHQ9Q2, PHQ9Q3, PHQ9Q4, PHQ9Q5, PHQ9Q6, PHQ9Q7, PHQ9Q8, PHQ9Q9]