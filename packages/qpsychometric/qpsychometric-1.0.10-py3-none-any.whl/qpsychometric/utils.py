import pandas as pd



def verify_df_intergrity(df):
    """
    Verify that the DataFrame has no common elements between columns.
    """
    # Extract the columns as a list for iteration
    columns = df.columns.tolist()
    
    # Check each column against every other column
    for i in range(len(columns)):
        for j in range(i + 1, len(columns)):
            # Use sets to find common elements
            if set(df[columns[i]]) & set(df[columns[j]]):
                # Return False if any common elements are found
                return False
    # If no common elements are found in any columns, return True
    return True



class QuestionnaireData:
    def __init__(self, df):
        """
        Initialize the QuestionnaireData object.
        """
        if isinstance(df, pd.DataFrame):
            self.df = df.reset_index(drop=True, inplace=False)
        else:
            raise ValueError("Data must be a pandas DataFrame.")

        if not verify_df_intergrity(self.df):
            raise ValueError("The 'Questionnaire Category', 'Questionnair Name', 'Questionnaire Task', and 'Question Class' must not have any common values.")

    def __getitem__(self, key):
        """
        Custom indexing to filter by a column value or multiple column values.
        Supports filtering with both single values and lists of values.
        Examples:
        - obj['mental_health_questionnaires'] -> filters by category_name='mental_health_questionnaires'
        - obj[['SOC', 'PHQ9']] -> filters by multiple questionnaire_name values
        - obj['mental_health_questionnaires']['PHQ9']['QMLM'] -> filters by multiple columns
        """
        if isinstance(key, list):  # If key is a list, check all columns for matches
            key_set = set(key)  # Convert the list to a set to use issubset
            if key_set.issubset(self.df['category_name'].values):
                filtered_df = self.df[self.df['category_name'].isin(key)]
            elif key_set.issubset(self.df['questionnaire_name'].values):
                filtered_df = self.df[self.df['questionnaire_name'].isin(key)]
            elif key_set.issubset(self.df['questionnaire_task'].values):
                filtered_df = self.df[self.df['questionnaire_task'].isin(key)]
            else:
                raise KeyError(f"Keys '{key}' not found in any column.")
        else:  # If key is a single value, check each column for matches
            if key in self.df['category_name'].values:
                filtered_df = self.df[self.df['category_name'] == key]
            elif key in self.df['questionnaire_name'].values:
                filtered_df = self.df[self.df['questionnaire_name'] == key]
            elif key in self.df['questionnaire_task'].values:
                filtered_df = self.df[self.df['questionnaire_task'] == key]
            else:
                raise KeyError(f"Key '{key}' not found in any column.")

        # Return a new instance of QuestionnaireData with the filtered DataFrame
        filtered_df.reset_index(drop=True, inplace=True)
        return QuestionnaireData(filtered_df)

    def __str__(self):
        """String representation of the DataFrame."""
        return self.df.to_string()
    
    def __len__(self):
        return len(self.df)

    def get_questions(self):
        """
        Returns a list of questions from the filtered DataFrame.
        - If grouped by multiple tasks, returns a nested list (one list per group).
        - Otherwise, returns a flat list of questions.
        """
        if self.df.empty:
            return []  # No results found
        
        grouped_filter_df = self.df.groupby(["questionnaire_name", "questionnaire_task"])
        list_of_questions = [
            list(group['question']) for _, group in grouped_filter_df
        ]
        return list_of_questions if len(list_of_questions) > 1 else list_of_questions[0]
