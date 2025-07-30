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


class BIG5Q1(QMLM):

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template="I am {frequency} {index} new experiences.",
            dimensions={
                "frequency":frequency_weights,
                "index":dict_pos_neg(['enjoying', 'appreciating'], 
                                     ['avoiding', 'dodging', 'evading'],1.0),
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Openness to Experience",
              "Ordinal":1,
              "Original":'I am open to new experiences and enjoy trying new things.'
            },
            **kwargs
        )
        
        
class BIG5Q2(QMLM):

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template="I am {frequency} {index}.",
            dimensions={
                "frequency":frequency_weights,
#                 "index":dict_pos_neg(['inventive', 'imaginative', 'creative'], 
#                                      ['lacking imagination', 'boring', 'dull'],1.0),
                "index":dict_pos_neg(['inventive', 'imaginative', 'creative'], 
                                     ['ordinary', 'realistic', 'reasonable', 'usual'],1.0),
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Openness to Experience",
              "Ordinal":2,
              "Original":'I am imaginative and have a rich inner life.'
            },
            **kwargs
        )
        
class BIG5Q3(QMLM):

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template="I {frequency} {index} new experiences.", 
            dimensions={
                "frequency":frequency_weights,
                "index":dict_pos_neg(['seek', 'look for', 'pursue'], 
                                     ['ignore', 'disregard', 'neglect'],1.0),
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Openness to Experience",
              "Ordinal":3,
              "Original":'I am adventurous and seek out new experiences.'
            },
            **kwargs
        )
        
class BIG5Q4(QMLM):

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template="I am {frequency} {index}.", 
            dimensions={
                "frequency":frequency_weights,
                "index":dict_pos_neg(['careful', 'thorough'], 
                                     ['overlook', 'careless', ],1.0),
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Conscientiousness",
              "Ordinal":4,
            "Original":'I am thorough and pay attention to detail.'
            },
            **kwargs
        )
        
class BIG5Q5(QMLM):

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template="I am {frequency} {index}.", 
            dimensions={
                "frequency":frequency_weights,
                "index":dict_pos_neg(['responsible', 'dependable', 'liable'], 
                                     ['unreliable', 'irresponsible'],1.0),
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Conscientiousness",
              "Ordinal":5,
            "Original":'I am responsible and dependable.'
            },
            **kwargs
        )
        
class BIG5Q6(QMLM):

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template="I am {frequency} like to be {index}.", 
            dimensions={
                "frequency":frequency_weights,
                "index":dict_pos_neg(['organized', 'arranged', 'tidy'], 
                                     ['messy', 'sloppy', 'dirty'],1.0),
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Conscientiousness",
              "Ordinal":6,
            "Original":'I am organized and like to keep things tidy.'
            },
            **kwargs
        )
        

class BIG5Q7(QMLM):

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template="I am {frequency} {index} around other people.", 
            dimensions={
                "frequency":frequency_weights,
                "index":dict_pos_neg(['talkative', 'chatty', 'communicative'], 
                                     ['quiet', 'silent', 'untalkative'],1.0),
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Extraversion",
              "Ordinal":7,
            "Original":'I am talkative and enjoy being around others.'
            },
            **kwargs
        )
        
class BIG5Q8(QMLM):

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template="I am {frequency} {index}.", 
            dimensions={
                "frequency":frequency_weights,
                "index":dict_pos_neg(['sociable', 'outgoing', 'friendly',], 
                                     ['reserved', 'unsociable', 'quiet',],1.0),
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Extraversion",
              "Ordinal":8,
            "Original":'I am outgoing and enjoy being the center of attention.'
            },
            **kwargs
        )
        
        
class BIG5Q9(QMLM):

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template="I am {frequency} {index}.", 
            dimensions={
                "frequency":frequency_weights,
                "index":dict_pos_neg(['sociable', 'friendly', 'approachable'], 
                                     ['distant','unfriendly', 'unsociable'],1.0),
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Extraversion",
              "Ordinal":9,
            "Original":'I am sociable and make friends easily.'
            },
            **kwargs
        )
        
        
class BIG5Q10(QMLM):

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template="I am {frequency} {index} towards other people's feelings.", 
            dimensions={
                "frequency":frequency_weights,
                "index":dict_pos_neg(['considerate', 'respectful', 'sympathetic'], 
                                     ['indifferent', 'distant', 'insensitive'],1.0),
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Agreeableness",
              "Ordinal":10,
            "Original":"I am considerate and care about other people's feelings."
            },
            **kwargs
        )
        
class BIG5Q11(QMLM):

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template="I am {frequency} {index} toward others.", 
            dimensions={
                "frequency":frequency_weights,
                "index":dict_pos_neg(['compassionate', 'sympathetic',], 
                                     ['indifferent', 'distant', 'insensitive'],1.0),
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Agreeableness",
              "Ordinal":11,
            "Original":"I am compassionate and empathetic towards others."
            },
            **kwargs
        )
        
        
class BIG5Q12(QMLM):

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template="I am {frequency} {index} toward others.", 
            dimensions={
                "frequency":frequency_weights,
                "index":dict_pos_neg(['cooperative', 'helpful',], 
                                     ['disobliging', 'uncooperative'],1.0),
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Agreeableness",
              "Ordinal":12,
            "Original":"I am cooperative and work well with others."
            },
            **kwargs
        )
        
        
class BIG5Q13(QMLM):

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template="I am {frequency} {index} about things.", 
            dimensions={
                "frequency":frequency_weights,
                "index":dict_pos_neg(['stressed', 'worried', 'concerned',], 
                                     ['calmed', 'composed'],1.0),
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Neuroticism",
              "Ordinal":13,
            "Original":"I am easily stressed and worry about things."
            },
            **kwargs
        )
        
class BIG5Q14(QMLM):

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            template="I am {frequency} {index}.", 
            dimensions={
                "frequency":frequency_weights,
                "index":dict_pos_neg(['upset', 'prone to mood swings', 'agitated'], 
                                     ['calm', 'relaxed'],1.0),
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Neuroticism",
              "Ordinal":14,
            "Original":"I am easily upset and prone to mood swings."
            },
            **kwargs
        )
        
big5_qmlm_list = [BIG5Q1, BIG5Q2, BIG5Q3, BIG5Q4, BIG5Q5, BIG5Q6, BIG5Q7, BIG5Q8, BIG5Q9, BIG5Q10, BIG5Q11, BIG5Q12, BIG5Q13, BIG5Q14]