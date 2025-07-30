from enum import IntEnum

class Type:
        ENTRY = "E"
        OUT = "O"

        TYPE = (
               (ENTRY , "E"),
               (OUT , 'O')
        )
        
class RegistryClassification:
        VARIABLE = "variable"
        FIX = "fix"
        INVESTIMENT = "investiment"


class Frequency(IntEnum):
        NONE = 0
        WEEK = 7
        BIWEEK = 15
        MONTH = 30
        YEAR = 365

        @staticmethod
        def get_frequency(frequency: int):
            mapping = {
                7 : 2,
                15 : 3,
                30 : 4,
                365 : 5,
                 
            }
            return mapping.get(frequency, 1)
