from .compassion_scale_qmnli import compassion_scale_qmnli_list
from .compassion_scale_qmlm import compassion_scale_qmlm_list
import os
import pandas as pd
from ...utils import QuestionnaireData

data = []

# Get the name of the parent directory of the current file directory
parent_directory_name = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

category_name = parent_directory_name


def get_questionnaire_info(question_class):
    task_name = question_class.__bases__[0].__name__
    question_obj = question_class()
    questionnaire_name = question_obj._descriptor["Questionnair"] 
    return task_name, questionnaire_name


if compassion_scale_qmlm_list:
    question_class_nli = compassion_scale_qmlm_list[0]
    task_name, questionnaire_name = get_questionnaire_info(question_class_nli)
    for mlm_question in compassion_scale_qmlm_list:
        data.append((category_name, questionnaire_name, task_name, mlm_question))


if compassion_scale_qmnli_list:
    question_class_nli = compassion_scale_qmnli_list[0]
    task_name, questionnaire_name = get_questionnaire_info(question_class_nli)
    for nli_question in compassion_scale_qmnli_list:
        data.append((category_name, questionnaire_name, task_name, nli_question))

compassion_scale_questionnaire = QuestionnaireData(pd.DataFrame(data, columns=['category_name', 'questionnaire_name', 'questionnaire_task', 'question']))


__all__ = ['compassion_scale_questionnaire']
