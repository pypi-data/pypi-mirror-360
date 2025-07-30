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

    
class BIG5Q1(QMNLI):
    
    
    emo_pos=['am open to', 'enjoy', 'like']
    emo_neg=['avoid', 'reject', 'dislike']
    dict_attitude=dict_pos_neg(emo_pos, emo_neg, 1.0)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I {frequency} {index} new experiences and trying new things.",
            answer_template="It is correct.",
            dimensions={
            "frequency":frequency_weights,
            "index": self.dict_attitude ,
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Openness to Experience",
              "Ordinal":1,
              "Original":'I am open to new experiences and enjoy trying new things.'
            },
            **kwargs
        )

class BIG5Q2(QMNLI):
        

    emo_pos=['inventive', 'imaginative', 'creative']
    emo_neg=['lacking imagination', 'boring']
    dict_attitude=dict_pos_neg(emo_pos, emo_neg, 1.0)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I am {frequency} {index}.",
            answer_template="It is correct.",

            dimensions={
            "frequency":frequency_weights,
            "index": self.dict_attitude ,
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Openness to Experience",
              "Ordinal":2,
              "Original":'I am imaginative and have a rich inner life.'
            },
            **kwargs
        )

class BIG5Q3(QMNLI):

    emo_pos=['seek out', 'look for', 'want to have']
    emo_neg=['decline', 'dislike', 'give up on']
    dict_attitude=dict_pos_neg(emo_pos, emo_neg, 1.0)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I {frequency} {index} new experiences.",
            answer_template="It is correct.", 

            dimensions={
            "frequency":frequency_weights,
            "index": self.dict_attitude ,
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Openness to Experience",
              "Ordinal":3,
              "Original":'I am adventurous and seek out new experiences.'
            },
            **kwargs
        )

class BIG5Q4(QMNLI):

    emo_pos=['closely inspect', 'pay attention to', 'am thorough in']
    emo_neg=['overlook', 'miss out on', 'tend to neglect']
    dict_attitude=dict_pos_neg(emo_pos, emo_neg, 1.0)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I {frequency} {index} the details.",
            answer_template="It is correct.",
 
            dimensions={
            "frequency":frequency_weights,
            "index": self.dict_attitude ,
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Conscientiousness",
              "Ordinal":4,
            "Original":'I am thorough and pay attention to detail.'
            },
            **kwargs
        )

class BIG5Q5(QMNLI):

    emo_pos=['responsible', 'dependable', 'trustworthy']
    emo_neg=['unreliable', 'reckless', 'unaccountable']
    dict_attitude=dict_pos_neg(emo_pos, emo_neg, 1.0)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I am {frequency} {index}.",
            answer_template="It is correct.",

            dimensions={
            "frequency":frequency_weights,
            "index": self.dict_attitude ,
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Conscientiousness",
              "Ordinal":5,
            "Original":'I am responsible and dependable.'
            },
            **kwargs
        )

class BIG5Q6(QMNLI):

    emo_pos=['organized', 'arranged']
    emo_neg=['messy', 'disordered']
    dict_attitude=dict_pos_neg(emo_pos, emo_neg, 1.0)
    def __init__(self, **kwargs):

        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I {frequency} like to be {index}.",
            answer_template="It is correct.",

            dimensions={
            "frequency":frequency_weights,
            "index": self.dict_attitude ,
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Conscientiousness",
              "Ordinal":6,
            "Original":'I am organized and like to keep things tidy.'
            },
            **kwargs
        )

class BIG5Q7(QMNLI):

    emo_pos=['talkative', 'chatty', 'amiable']
    emo_neg=['quiet', 'silent', 'withdrawn', 'shy']
    dict_attitude=dict_pos_neg(emo_pos, emo_neg, 1.0)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I am {frequency} {index} around other people.",
            answer_template="It is correct.",

            dimensions={
            "frequency":frequency_weights,
            "index": self.dict_attitude ,
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Extraversion",
              "Ordinal":7,
            "Original":'I am talkative and enjoy being around others.'
            },
            **kwargs
        )

class BIG5Q8(QMNLI):

    emo_pos=['sociable', 'in the center of attention']
    emo_neg=['quiet', 'reserved', 'shy']
    dict_attitude=dict_pos_neg(emo_pos, emo_neg, 1.0)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I am {frequency} {index}.",
            answer_template="It is correct.",


            dimensions={
            "frequency":frequency_weights,
            "index": self.dict_attitude ,
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Extraversion",
              "Ordinal":8,
            "Original":'I am outgoing and enjoy being the center of attention.'
            },
            **kwargs
        )

class BIG5Q9(QMNLI):

    emo_pos=['sociable', 'friendly', 'approachable']
    emo_neg=['distant','unfriendly', 'unsociable']
    dict_attitude=dict_pos_neg(emo_pos, emo_neg, 1.0)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I am {frequency} {index}.",
            answer_template="It is correct.",
            dimensions={
            "frequency":frequency_weights,
            "index": self.dict_attitude ,
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Extraversion",
              "Ordinal":9,
            "Original":'I am sociable and make friends easily.'
            },
            **kwargs
        )

class BIG5Q10(QMNLI):

    emo_pos=['considerate towards', 'respectful towards', 'care about']
    emo_neg=['indifferent towards', 'indexally distant towards', 'insensitive towards']
    dict_attitude=dict_pos_neg(emo_pos, emo_neg, 1.0)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I am {frequency} {index} other people's feelings.",
            answer_template="It is correct.",

            dimensions={
            "frequency":frequency_weights,
            "index": self.dict_attitude ,
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Agreeableness",
              "Ordinal":10,
            "Original":"I am considerate and care about other people's feelings."
            },
            **kwargs
        )

class BIG5Q11(QMNLI):

    emo_pos=['compassionate', 'empathetic', 'sympathetic']
    emo_neg=['indifferent', 'careless', 'apathetic']
    dict_attitude=dict_pos_neg(emo_pos, emo_neg, 1.0)

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I am {frequency} {index} towards others.",
            answer_template="It is correct.",

            dimensions={
            "frequency":frequency_weights,
            "index": self.dict_attitude ,
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Agreeableness",
              "Ordinal":11,
            "Original":"I am compassionate and empathetic towards others."
            },
            **kwargs
        )

class BIG5Q12(QMNLI):

    emo_pos=['cooperate', 'work well', 'helpful']
    emo_neg=['disobliging', 'unsupportive']
    dict_attitude=dict_pos_neg(emo_pos, emo_neg, 1.0)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I {frequency} {index} with others.",
            answer_template="It is correct.",
            dimensions={
            "frequency":frequency_weights,
            "index": self.dict_attitude ,
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Agreeableness",
              "Ordinal":12,
            "Original":"I am cooperative and work well with others."
            },
            **kwargs
        )

class BIG5Q13(QMNLI):

    emo_pos=['stressed', 'worry', 'concern']
    emo_neg=['calmed', 'collected', 'composed']
    dict_attitude=dict_pos_neg(emo_pos, emo_neg, 1.0)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I am {frequency} easily {index} about things.",
            answer_template="It is correct.",

            dimensions={
            "frequency":frequency_weights,
            "index": self.dict_attitude ,
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Neuroticism",
              "Ordinal":13,
            "Original":"I am easily stressed and worry about things."
            },
            **kwargs
        )

class BIG5Q14(QMNLI):

    emo_pos=['upset', 'prone to mood swings', 'agitated']
    emo_neg=['calmed', 'relaxed']
    dict_attitude=dict_pos_neg(emo_pos, emo_neg, 1.0)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I am {frequency} easily {index}.",
            answer_template="It is correct.",

            dimensions={
            "frequency":frequency_weights,
            "index": self.dict_attitude ,
            },
            descriptor = {"Questionnair":"BIG5",
              "Factor":"Neuroticism",
              "Ordinal":14,
            "Original":"I am easily upset and prone to mood swings."
            },
            **kwargs
        )

big5_qmnli_list = [BIG5Q1, BIG5Q2, BIG5Q3, BIG5Q4, BIG5Q5, BIG5Q6, BIG5Q7, BIG5Q8, BIG5Q9, BIG5Q10, BIG5Q11, BIG5Q12, BIG5Q13, BIG5Q14]