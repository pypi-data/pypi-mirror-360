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






class CSQ1(QMNLI):
    """
    """


    kw_attitude_neg = ['incorrect', 'false', 'imprecise', 'invalid']
    kw_attitude_pos = ['correct', 'true', 'accurate', 'a fact']
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I {frequency} distant when people cry in front of me.",
            answer_template="This is {index}",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Disengagement",
                          "Ordinal":1,
                          "Original":"when people cry in front of me, I often don’t feel anything at all."
            },
            **kwargs,
        )

class CSQ7(QMNLI):
    """
    """


    kw_attitude_neg = ['incorrect', 'false', 'imprecise', 'invalid']
    kw_attitude_pos = ['correct', 'true', 'accurate', 'a fact']
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I {frequency} distant when people tell me about their troubles.",
            answer_template="This is {index}",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Disengagement",
                          "Ordinal":7,
                          "Original":"I often tune out when people tell me about their troubles"
            },
            **kwargs,
        )

class CSQ19(QMNLI):
    """
    """


    kw_attitude_neg = ['correct', 'true', 'accurate', 'a fact']
    kw_attitude_pos = ['incorrect', 'false', 'imprecise', 'invalid']
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I {frequency} care much about the concerns of others.",
            answer_template="This is {index}.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Disengagement",
                          "Ordinal":19,
                          "Original":"I don’t think much about the concerns of others"
            },
            **kwargs,
        )


class CSQ23(QMNLI):
    """
    """


    kw_attitude_neg = ['incorrect', 'false', 'imprecise', 'invalid']
    kw_attitude_pos = ['correct', 'true', 'accurate', 'a fact']
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I {frequency} avoid people who are experiencing a lot of pain.",
            answer_template="This sentence is {index}.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Disengagement",
                          "Ordinal":23,
                          "Original":"I try to avoid people who are experiencing a lot of pain"
            },
            **kwargs,
        )


class CSQ2(QMNLI):
    """
    """


    kw_attitude_neg = ['incorrect', 'false', 'imprecise']
    kw_attitude_pos = ['correct', 'true', 'accurate',]
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I feel like I don’t care when people talk about their problems.",
            answer_template="It is {frequency} {index}.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Indifference",
                          "Ordinal":2,
                          "Original":"sometimes when people talk about their problems, I feel like I don’t care"
            },
            **kwargs,
        )

class CSQ12(QMNLI):
    """
    """


    kw_attitude_neg = ['incorrect', 'false', 'imprecise',]
    kw_attitude_pos = ['correct', 'true', 'accurate',]
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I am indifferent to people who are down and out.",
            answer_template= "It is {frequency} {index}.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Indifference",
                          "Ordinal":12,
                          "Original":"Sometimes I am cold to others when they are down and out."
            },
            **kwargs,
        )

class CSQ14(QMNLI):
    """
    """


    kw_attitude_neg = ['incorrect', 'false', 'imprecise',]
    kw_attitude_pos = ['correct', 'true', 'accurate',]
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I am indifferent to other people’s problems.",
            answer_template= "It is {frequency} {index}.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Indifference",
                          "Ordinal":14,
                          "Original":"I don’t concern myself with other people’s problems."
            },
            **kwargs,
        )

class CSQ18(QMNLI):
    """
    """


    kw_attitude_neg = ['incorrect', 'false', 'imprecise',]
    kw_attitude_pos = ['correct', 'true', 'accurate',]
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I am {frequency} indifferent to people who are feeling troubled.",
            answer_template= "It is {index}.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Indifference",
                          "Ordinal":18,
                          "Original":"When others are feeling troubled, I usually let someone else attend to them."
            },
            **kwargs,
        )

class CSQ3(QMNLI):
    """
    """


    kw_attitude_neg = ['incorrect', 'false']
    kw_attitude_pos = ['correct', 'true']
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I {frequency} feel emotionally disconnected to people in pain.",
            answer_template="It is {index}.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Separation",
                          "Ordinal":3,
                          "Original":"I don’t feel emotionally connected to people in pain"
            },
            **kwargs,
        )

class CSQ5(QMNLI):
    """
    """


    kw_attitude_neg = ['incorrect', 'false']
    kw_attitude_pos = ['correct', 'true']
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I feel detached from others when they tell me their tales of woe.",
            answer_template="It is {frequency} {index}.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Separation",
                          "Ordinal":5,
                          "Original":"I feel detached from others when they tell me their tales of woe."
            },
            **kwargs,
        )

class CSQ10(QMNLI):
    """
    """


    kw_attitude_neg = ['incorrect', 'false']
    kw_attitude_pos = ['correct', 'true']
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I feel like I can’t relate to them when I see someone feeling down.",
            answer_template="It is {frequency} {index}.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Separation",
                          "Ordinal":10,
                          "Original":"when I see someone feeling down, I feel like I can’t relate to them"
            },
            **kwargs,
        )

class CSQ22(QMNLI):
    """
    """


    kw_attitude_neg = ['incorrect', 'false']
    kw_attitude_pos = ['correct', 'true']
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I can’t really connect with other people when they’re suffering.",
            answer_template="It is {frequency} {index}.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Separation",
                          "Ordinal":22,
                          "Original":"I can’t really connect with other people when they’re suffering"
            },
            **kwargs,
        )

class CSQ4(QMNLI):
    """
    """


    kw_attitude_neg = ['incorrect', 'false', 'imprecise', 'invalid']
    kw_attitude_pos = ['correct', 'true', 'accurate', 'a fact']
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I pay careful attention when other people talk to me.",
            answer_template="This sentence is {frequency} {index}.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Mindfulness",
                          "Ordinal":4,
                          "Original":"I pay careful attention when other people talk to me."
            },
            **kwargs,
        )

class CSQ9(QMNLI):
    """
    """


    kw_attitude_neg = ['incorrect', 'false', 'imprecise', 'invalid']
    kw_attitude_pos = ['correct', 'true', 'accurate', 'a fact']
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I {index} when people are upset.",
            answer_template="It is {frequency} correct.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Mindfulness",
                          "Ordinal":9,
                          "Original":"I notice when people are upset, even if they don’t say anything."
            },
            **kwargs,
        )

class CSQ13(QMNLI):
    """
    """


    kw_attitude_neg = ['incorrect', 'false', 'imprecise', 'invalid']
    kw_attitude_pos = ['correct', 'true', 'accurate', 'a fact']
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I tend to listen patiently when people tell me their problems.",
            answer_template="It is {frequency} {index}.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Mindfulness",
                          "Ordinal":13,
                          "Original":"I tend to listen patiently when people tell me their problems"
            },
            **kwargs,
        )

class CSQ21(QMNLI):
    """
    """


    kw_attitude_neg = ['biased', 'unbalanced', 'disproportioned', 'skewed']
    kw_attitude_pos = ['balanced', 'reasonable', 'sensible', 'impartial']
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="When people tell me about their problems, I try to keep a {index} perspective on the situation.",
            answer_template="It is {frequency} correct.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Mindfulness",
                          "Ordinal":21,
                          "Original":"when people tell me about their problems, I try to keep a balanced perspective on the situation"
            },
            **kwargs,
        )

class CSQ6(QMNLI):
    """
    """


    kw_attitude_neg = ['indifferent to', 'ignore', 'cold to', 'avoid']
    kw_attitude_pos = ['caring toward', 'kind to', 'sympathize with']
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I {frequency} {index} people who are going through a difficult time.",
            answer_template="It is correct.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Kindness",
                          "Ordinal":6,
                          "Original":"If I see someone going through a difficult time, I try to be caring toward that person"
            },
            **kwargs,
        )

class CSQ8(QMNLI):
    """
    """


    kw_attitude_neg = ['indifferent to', 'ignore', 'cold to', 'avoid']
    kw_attitude_pos = ['caring toward', 'kind to']
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="I {frequency} {index} people that are in times of difficulty.",
            answer_template="It is correct.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Kindness",
                          "Ordinal":8,
                          "Original":" I like to be there for others in times of difficulty"
            },
            **kwargs,
        )

class CSQ16(QMNLI):
    """
    """


    kw_attitude_neg = ['indifferent to', 'ignore', 'cold to', 'avoid']
    kw_attitude_pos = ['caring toward', 'kind to', 'sympathize with']
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index = ["index"],
            scale = "frequency",
            context_template="I {frequency} {index} people that are unhappy.",
            answer_template="It is correct.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Kindness",
                          "Ordinal":16,
                          "Original":"My heart goes out to people who are unhappy"
            },
            **kwargs,
        )

class CSQ24(QMNLI):
    """
    """


    kw_attitude_neg = ['indifferent to', 'ignore', 'cold to', 'avoid']
    kw_attitude_pos = ['caring toward', 'kind to', 'sympathize with']
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index = ["index"],
            scale = "frequency",
            context_template="I {frequency} {index} people that feel sadness.",
            answer_template="It is correct.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Kindness",
                          "Ordinal":24,
                          "Original":"when others feel sadness, I try to comfort them"
            },
            **kwargs,
        )

class CSQ11(QMNLI):
    """
    """


    kw_attitude_pos = ['an important', 'an essential', 'a significant', 'a critical',]
    kw_attitude_neg = ['an insignificant', 'an unimportant', 'an irrelevant', 'a minor',]
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index = ["index"],
            scale = "frequency",
            context_template="Being down is {index} part of being human.",
            answer_template="It is {frequency} correct.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Common Humanity",
                          "Ordinal":11,
                          "Original":"Everyone feels down sometimes, it is part of being human"
            },
            **kwargs,
        )

class CSQ15(QMNLI):
    """
    """


    kw_attitude_pos = ['an important', 'an essential', 'a significant', 'a critical',]
    kw_attitude_neg = ['an insignificant', 'an unimportant', 'an irrelevant', 'a minor',]
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index = ["index"],
            scale = "frequency",
            context_template="Recognizing that all people have weaknesses is {index} part of life.",
            answer_template="It is {frequency} correct.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Common Humanity",
                          "Ordinal":15,
                          "Original":"it’s important to recognize that all people have weaknesses and no one’s perfect"
            },
            **kwargs,
        )

class CSQ17(QMNLI):
    """
    """


    kw_attitude_pos = ['an important', 'an essential', 'a significant', 'a critical',]
    kw_attitude_neg = ['an insignificant', 'an unimportant', 'an irrelevant', 'a minor',]
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index = ["index"],
            scale = "frequency",
            context_template="Knowing that all people feels pain is {index} part of life.",
            answer_template="It is {frequency} correct.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Common Humanity",
                          "Ordinal":17,
                          "Original":"Despite my differences with others, I know that everyone feels pain just like me"
            },
            **kwargs,
        )

class CSQ20(QMNLI):
    """
    """


    kw_attitude_pos = ['an important','a crucial', 'an essential', 'a significant', 'a critical',]
    kw_attitude_neg = ['an insignificant', 'an unimportant', 'an irrelevant', 'a minor',]
    dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)
    
    def __init__(self, **kwargs):
        super().__init__(
            index = ["index"],
            scale = "frequency",
            context_template="Suffering is just {index} part of the common human experience.",
            answer_template="It is {frequency} correct.",
            dimensions={
                "frequency":frequency_weights,
                "index":self.dict_attitude,
            },
            descriptor = {"Questionnair":"CS",
                          "Factor":"Common Humanity",
                          "Ordinal":20,
                          "Original":" suffering is just a part of the common human experience"
            },
            **kwargs,
        )

compassion_scale_qmnli_list = [CSQ1, CSQ2, CSQ3, CSQ4, CSQ5, CSQ6, CSQ7, CSQ8, CSQ9, CSQ10, CSQ11, CSQ12, CSQ13, CSQ14, CSQ15, CSQ16, CSQ17, CSQ18, CSQ19, CSQ20, CSQ21, CSQ22, CSQ23, CSQ24]