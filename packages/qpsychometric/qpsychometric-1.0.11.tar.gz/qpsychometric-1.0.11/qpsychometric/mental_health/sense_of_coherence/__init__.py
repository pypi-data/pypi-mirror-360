from .soc_qmnli import soc_qmnli_list
from .soc_qmlm import soc_qmlm_list
import os
import pandas as pd
from ...utils import QuestionnaireData

data = []

# Get the name of the parent directory of the current file directory
parent_directory_name = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

category_name = parent_directory_name
questions_class_nli = soc_qmnli_list[0]
questions_class_mlm = soc_qmlm_list[0]

question_obj = questions_class_nli()
questionnaire_name = question_obj._descriptor["Questionnair"]
task_name = questions_class_mlm.__bases__[0].__name__

for mlm_question in soc_qmlm_list:
    data.append((category_name, questionnaire_name, task_name, mlm_question))
    

task_name = questions_class_nli.__bases__[0].__name__

for nli_question in soc_qmnli_list:
    data.append((category_name, questionnaire_name, task_name, nli_question))

soc_questionnaire = QuestionnaireData(pd.DataFrame(data, columns=['category_name', 'questionnaire_name', 'questionnaire_task', 'question']))




__all__ = ['soc_questionnaire']