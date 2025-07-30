# ##################################################################################################
#
# Title:
#
#   pypeworks.util.py
#
# License:
#
#   Copyright 2025 Rosaia B.V.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except 
#   in compliance with the License. You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software distributed under the 
#   License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#   express or implied. See the License for the specific language governing permissions and 
#   limitations under the License.
#
#   [Apache License, version 2.0]
#
# Description: 
#
#   Part of the Pypeworks framework, implementing various commonly applied procedures.
#
# ##################################################################################################

# ##################################################################################################
# Dependencies
# ##################################################################################################

# Python standard library ##########################################################################

# Fundamentals
from typing import (
    Any
)

# ##################################################################################################
# Functions
# ##################################################################################################

# flatten ##########################################################################################

def flatten(xs : list) -> list | Any | None:

    """
    Takes a list and attempts to flatten it. If the list contains but one non-None value, it returns
    said non-None value. If the lists contains multiple non-None values, the original list is 
    returned. Otherwise, if the list contains only None-values, a None-value is returned.
    """

    # Create a generator, returning non-None values.
    generator = (x for x in xs if x is not None)

    # Attempt to retrieve the first non-None value.
    x1 = next(generator, None)

    # If no non-None values could be retrieved, the list did not contain any non-None values and a
    # singular non-None value is returned.
    if x1 is None:
        return None
    
    # Attempt to retrieve the second non-None value.
    x2 = next(generator, None)

    # If a non-None value was retrieved, multiple non-None values are present and the original
    # list should be returned.
    if x2 is not None:
        return xs
    
    # Return the non-None value if no other no-None value was found.
    return x1

    # End of function 'flatten' ####################################################################


# End of File ######################################################################################