import os
import importlib
import pandas as pd
from ..utils import QuestionnaireData

__all__ = ['social_biases_questionnaires']  # Start with an empty export list
package_directory = os.path.dirname(__file__)  # Get the directory of the current package
package_name = __name__

            
social_biases_questionnaires = pd.DataFrame([], columns=['category_name', 'questionnaire_name', 'questionnaire_task', 'question'])


# List only the top-level directories (modules) directly under the package directory
for entry in os.listdir(package_directory):
    if os.path.isdir(os.path.join(package_directory, entry)) and not entry.startswith('_') or entry.startswith('.'):
        # Construct the module name
        module_name = f"{package_name}.{entry}"
        # Import the module
        module = importlib.import_module(module_name)
        # Some modules don't have the __all__ global var, only packages.
        if hasattr(module, "__all__"):
            # Get the module global variable defined in `__all__`
            module_wild_card_var = module.__all__[0]
            wrapped_module_questions = getattr(module, module_wild_card_var)
            social_biases_questionnaires = pd.concat([social_biases_questionnaires, wrapped_module_questions.df], ignore_index=True)
            pass
        
        
social_biases_questionnaires=QuestionnaireData(social_biases_questionnaires)