from typing import List
from maleo_foundation.models.schemas.general import BaseGeneralSchemas

class ExtendedTypes:
    #* DateFilter-related types
    ListOfDateFilters = List[BaseGeneralSchemas.DateFilter]

    #* SortColumn-related types
    ListOfSortColumns = List[BaseGeneralSchemas.SortColumn]