from .gad_qmnli import gad_qmnli_list
from .gad_qmlm import gad_qmlm_list
import pandas as pd
import os
from ...utils import QuestionnaireData, verify_df_intergrity



# gad_questionnaire = {'QMNLI':gad_qmnli_list, 'QMLM':gad_qmmlm_list}

data = []

# Get the name of the parent directory of the current file directory
parent_directory_name = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
category_name = parent_directory_name


def get_questionnaire_info(question_class):
    task_name = question_class.__bases__[0].__name__
    question_obj = question_class()
    questionnaire_name = question_obj._descriptor["Questionnair"] 
    return task_name, questionnaire_name


if gad_qmlm_list:
    question_class_nli = gad_qmlm_list[0]
    task_name, questionnaire_name = get_questionnaire_info(question_class_nli)
    for mlm_question in gad_qmlm_list:
        data.append((category_name, questionnaire_name, task_name, mlm_question))


if gad_qmnli_list:
    question_class_nli = gad_qmnli_list[0]
    task_name, questionnaire_name = get_questionnaire_info(question_class_nli)
    for nli_question in gad_qmnli_list:
        data.append((category_name, questionnaire_name, task_name, nli_question))



gad_questionnaire = QuestionnaireData(pd.DataFrame(data, columns=['category_name', 'questionnaire_name', 'questionnaire_task', 'question']))




__all__ = ['gad_questionnaire']