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

class SOCQ4(QMNLI):
  


  kw_attitude_neg = ["meaningless", "dull", "aimless", 'boring']
  kw_attitude_pos = ["meaningful", "interesting", "fulfilling", 'fascinating']
  dict_attitude = dict_pos_neg(kw_attitude_pos,kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="What goes around me is {index} to me.",
        answer_template="It is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Meaningfulness",
                      "Ordinal":4,
                      "Original":"Do you have the feeling that you don’t really care what goes on around you? "
        },
        **kwargs,
    )

class SOCQ5(QMNLI):
  


  kw_attitude_neg = ['surprised by','puzzled by']
  kw_attitude_pos = ['expecting','anticipating']
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="I am {frequency} {index} the behavior of people I thought I knew well.",
        answer_template="True.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Comprehensibility",
                      "Ordinal":5,
                      "Original":"Has it happened in the past that you were surprised by the behavior of people whom you thought you knew well? "
        },
        **kwargs,
    )

class SOCQ6(QMNLI):
  


  kw_attitude_neg = ["disappointed", 'failed']
  kw_attitude_pos = ["supported", "helped"]
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="People whom I counted on {frequency} {index} me.",
        answer_template="True.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Manageability",
                      "Ordinal":6,
                      "Original":"Has it happened that people whom you counted on disappointed you? "
        },
        **kwargs,
    )

class SOCQ8(QMNLI):


  kw_attitude_neg = ["meaningless", "dull", "aimless", 'boring']
  kw_attitude_pos = ["meaningful", "interesting", "fulfilling", 'fascinating']
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="My life is {index}.",
        answer_template="It is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Meaningfulness",
                      "Ordinal":8,
                      "Original":"Until now your life has had: "
        },
        **kwargs,
    )

class SOCQ9(QMNLI):


  kw_attitude_neg = ["unfairly", "unjustly", "with discrimination", "unequally"]
  kw_attitude_pos = ["fairly", "justly", "equally"]
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="I feel that I am being treated {index}.",
        answer_template="It is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Manageability",
                      "Ordinal":9,
                      "Original":"Do you have the feeling that you’re being treated unfairly? "
        },
        **kwargs,
    )

class SOCQ12(QMNLI):
  


  kw_attitude_neg = ["helpless", "hopeless", 'powerless']
  kw_attitude_pos = ["easy", "comfortable", "relaxed"]
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="In unfamiliar situation I feel {index}.",
        answer_template="It is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Comprehensibility",
                      "Ordinal":12,
                      "Original":"Do you have the feeling that you’re in an unfamiliar situation and don’t know what to do?"
        },
        **kwargs,
    )

class SOCQ16(QMNLI):


  kw_attitude_neg = ["meaningless", "dull", "aimless", 'boring']
  kw_attitude_pos = ["meaningful", "interesting", "fulfilling", 'fascinating']
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="Things I do every day are {index}.",
        answer_template="It is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Meaningfulness",
                      "Ordinal":16,
                      "Original":"Doing the things you do every day is: "
        },
        **kwargs,
    )

class SOCQ19(QMNLI):
  


  kw_attitude_pos = ["clear", "coherent", 'logical', 'comprehensible']
  kw_attitude_neg = ["mixed-up", "confounded"]
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="I have {index} feelings and ideas.",
        answer_template="It is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Comprehensibility",
                      "Ordinal":19,
                      "Original":"Do you have very mixed-up feelings and ideas? "
        },
        **kwargs,
    )

class SOCQ21(QMNLI):
  


  kw_attitude_neg = ['face', 'confront', 'acknowledge', 'process', 'accept']
  kw_attitude_pos = ['ignore', 'avoid', 'dismiss']
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="I have feelings inside I would like to {index}.",
        answer_template="It is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Comprehensibility",
                      "Ordinal":21,
                      "Original":"Does it happen that you have feelings inside you would rather not feel? "
        },
        **kwargs,
    )

class SOCQ25(QMNLI):
  


  kw_attitude_neg = ["loser", "sad sack"]
  kw_attitude_pos = ["winner", "success"]
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="I’m a {index}.",
        answer_template="It is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Manageability",
                      "Ordinal":25,
                      "Original":"Many people—even those with a strong character—sometimes feel like sad sacks (losers) in certain situations. How often have you felt this way in the past? "
        },
        **kwargs,
    )

class SOCQ26(QMNLI):
  

  kw_attitude_pos = ["estimate in proportion", "judge in proportion"]
  kw_attitude_neg = ["overestimate","misjudge",'underestimate']
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="I {index} the importance of something that happened.",
        answer_template="It is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Comprehensibility",
                      "Ordinal":26,
                      "Original":"When something happened‚ you have generally found that: you overestimated or underestimated its importance, you saw things in the right proportion"
        },
        **kwargs,
    )

class SOCQ28(QMNLI):
  


  kw_attitude_neg = ["meaningless", "dull", "aimless", 'boring']
  kw_attitude_pos = ["meaningful", "interesting", "fulfilling", 'fascinating']
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="The things I do in my daily life are {index} to me.",
        answer_template="It is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Meaningfulness",
                      "Ordinal":28,
                      "Original":"How often do you have the feeling that there’s little meaning in the things you do in your daily life? "
        },
        **kwargs,
    )

class SOCQ29(QMNLI):


  kw_attitude_neg = ["out of control", "uncontrollable", 'unmanageable']
  kw_attitude_pos = ["contained", "collected", 'controlled']
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="I feel that my feelings are {index}.",
        answer_template="It is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Manageability",
                      "Ordinal":29,
                      "Original":"How often do you have feelings that you’re not sure you can keep under control? "
        },
        **kwargs,
    )

soc_qmnli_list = [SOCQ4, SOCQ5, SOCQ6, SOCQ8, SOCQ12, SOCQ16, SOCQ19, SOCQ21, SOCQ25, SOCQ26, SOCQ28, SOCQ29]