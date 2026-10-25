# Errors for data validation
class DatabaseErrors(Exception): 
    """Base class for this library"""

class QueryDeleteError(DatabaseErrors):
    def __str__(self):
        return f'Unable to delete selected item. Probably constrained due to it being a Foreign Key'

class IngredientInUseError(DatabaseErrors):
    def __str__(self):
        return f'This ingredient is being used in a meal!'

class QueryInvalidFK(DatabaseErrors):
    def __str__(self):
            return f'Foreign key not found!!'