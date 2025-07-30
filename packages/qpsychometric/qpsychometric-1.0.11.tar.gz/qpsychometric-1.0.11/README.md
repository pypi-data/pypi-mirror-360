# The `qpsychometric` Package

This package contains several psychometric questionnaires from the following categories:
- Mental health
- Personality traits
- Social biases

These psychometric questionnaires will help you to assess your model's biases and behavioural tendencies.
Currently contains the following questionnaires: ASI, BIG5, CS, GAD, PHQ, SD3, SOC.

## List of questionnaires are available for running
* ASI:
  * asi_questionnaire (all questions of ASI in QMNLI & QMLM format)
* BIG5:
  * big5_questionnaire (all questions of BIG5 in QMNLI & QMLM format)
* GAD:
  * gad_questionnaire (all questions of GAD in QMNLI & QMLM format)
* PHQ:
  * phq_questionnaire (all questions of PHQ in QMNLI & QMLM format)
* CS:
  * compassion_scale_questionnaire (all questions of CS in QMNLI format)
* SD3:
  * sd3_questionnaire (all questions of SD3 in QMNLI format)
* SOC:
  * soc_questionnaire (all questions of SOC in QMNLI & QMLM format)

## Structure of the qpsychometric package:
qpsychometric<br>
|-mental_health<br>
| |-generalized_anxiety_disorder (GAD)<br>
| |-patient_health_questionnaire (PHQ)<br>
| |-sense_of_coherence (SOC)<br>
|-personality_traits<br>
| |-big5 (BIG5)<br>
| |-compassion_scale (Compassion Scale)<br>
| |-sd3 (SD3)<br>
|-social_biases<br>
| |-ambivalent_sexism_inventory (ASI)<br>

## Commands and steps for running a questionnaire:

* How to install the qlatent package:
  ```python
  %pip install qlatent
  ```
* How to import the classes of the questionnaires:
  ```python
  from qlatent.qmnli.qmnli import *
  ```
* How to load an NLI model from huggingface.com into a pipeline a few simple steps:
  ```python
  device = 0 if torch.cuda.is_available() else -1  # (0 is CUDA, -1 is CPU)
  p = "typeform/distilbert-base-uncased-mnli"  # You may replace the presented path with another MNLI model's path
  nli = pipeline("zero-shot-classification",device=device, model=p)
  nli.model_identifier = p
  ```
* How to load a questionnaire:
  ```python
  """
  The format for importing a questionnaire is the following:
   from qpsychometric.<category_with_underscores>.<full_questionnaire_name_with_underscores> import <questionnaire_name>
   Each questionnaire is a Data Frame (df) containing the columns: [category_name, questionnaire_name, questionnaire_task, question].
  For example:
  """
  
  from qpsychometric.mental_health.generalized_anxiety_disorder import gad_questionnaire
  from qpsychometric.personality_traits.compassion_scale import compassion_scale_questionnaire
  from qpsychometric.social_biases.ambivalent_sexism_inventory import asi_questionnaire

  # to view the questionnaire df
  print(gad_questionnaire)
  ```
* How to load category questionnaires:
  ```python
  """
  The format for importing category questionnaires is the following:
   from qpsychometric.<category_with_underscores> import *
   All the questionnaires within the same categoery get stored in the same df.
  For example:
  """
  # Gets stored in `mental_health_questionnaires` as a df.
  from qpsychometric.mental_health import *
  # Gets stored in `personality_traits_questionnaires` as a df.
  from qpsychometric.personality_traits import *
  # Gets stored in `social_biases_questionnaires` as a df.
  from qpsychometric.social_biases import *
  ```
* How to load all categories:
  ```python
  """
  To import all categories you need to do:
  All Data Frames from all categories get stored in the same df.
  """
  # Gets stored in `all_psychometrics` as a df.
  from qpsychometric import *

  ```
* How to filter questionnaires:<br>
  ```python
  """
  To filter specific questionnaires you can use indexing valid values from the columns.
  If you wish to filter 2 or more values from a column, it must be in a nested list: [['value1_to_filter','value2_to_filter','value3_to_filter'...]]
  For example:
  """
  from qpsychometric.mental_health.generalized_anxiety_disorder import gad_questionnaire
  # filter by 'QMLM' task
  filtered_gad_questionnaire = gad_questionnaire['QMLM']

  from qpsychometric.mental_health import *
  # filter 2 questionnaires from the category by 'QMNLI' task.
  filtered_mental_health_questionnaires = mental_health_questionnaires[['GAD7','SOC']]['QMNLI']

  # filter 2 categories by 'QMLM' task.
  from qpsychometric import *
  filtered_all_psychometrics = all_psychometrics[['mental_health','personality_traits']]['QMLM']
  ``` 
* How to get the questionnaires questions:<br>
  ```python
  """
  To get the questions in a list you can use the method `get_questions()`
  Returns a list of questions from the filtered DataFrame.
  The df is grouped by ["questionnaire_name", "questionnaire_task"] so each unique group is a pair of questionnaire with its task.
    - If grouped by multiple tasks, returns a nested list (one list per group).
    - Otherwise, returns a flat list of questions.
  For example:
  """
  from qpsychometric.mental_health.generalized_anxiety_disorder import gad_questionnaire
  filtered_gad_questionnaire = gad_questionnaire['QMLM']
  # 1D list containing the GAD QMLM questions.
  gad_questions_qmlm = filtered_gad_questionnaire.get_questions()

  from qpsychometric.mental_health import *
  # filter 2 questionnaires from the category by 'QMNLI' task.
  filtered_mental_health_questionnaires = mental_health_questionnaires[['GAD7','SOC']]['QMNLI']
  # 2D list where each list contains the QMNLI questions of the questionnaire.
  soc_gad_questions_qmnli = filtered_mental_health_questionnaires.get_questions()

  ``` 
* How to run a question from a questionnaire through an MNLI pipeline:<br>
   This package includes (as it relies on) the package qlatent.<br>
   The qlatent package contains a description that explains how to run QMNLI questions.<br>
   Look at these descriptions for the info you need.<br>
* How to run a questionnaire:
  ```python
  """
  Simply iterate through the questionnaire (as it is a list of questions),
  and apply the code for running a question on each question individually.
  """
  from qpsychometric.social_biases.ambivalent_sexism_inventory import asi_questionnaire
  asi_qmnli = asi_questionnaire['QMNLI'].get_questions()
  for Q in tqdm(asi_qmnli):
    Qs = split_question(Q,
                        index=Q.q_index,
                        scales=[Q.q_scale],
                        softmax=[True],
                        filters={'unfiltered':{},
                                "positiveonly":Q().get_filter_for_postive_keywords()
                                },
                        )
    print(Qs[0]._descriptor['Ordinal'])
    Qs[0].run(mnli)  # you may add .mean_score() or .report() after the run() function.
  ```

Shield: [![CC BY-SA 4.0][cc-by-sa-shield]][cc-by-sa]

This work is licensed under a
[Creative Commons Attribution-ShareAlike 4.0 International License][cc-by-sa].

[![CC BY-SA 4.0][cc-by-sa-image]][cc-by-sa]

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-image]: https://licensebuttons.net/l/by-sa/4.0/88x31.png
[cc-by-sa-shield]: https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg
