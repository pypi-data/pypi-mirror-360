# ##################################################################################################
#
# Title:
#
#   pypeworks.nodes.py
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
#   Part of the Pypeworks framework, implementing various classes that represent nodes that can
#   make up a pipework, a finite state machine that processes data in parallel.
#
# ##################################################################################################

# ##################################################################################################
# Dependencies
# ##################################################################################################

# Local ############################################################################################

from .node import (
    Node
)


# ##################################################################################################
# Classes
# ##################################################################################################        

# Identity #########################################################################################
        
class Identity(Node):

    """
    Passes through the input to any subsequent nodes.

    A use case for this node is a situation where one would like to join data from a number of 
    preceeding nodes whereby the joined data needs to be processed by multiple nodes in parallel.
    For example, consider the following::

        Pipework(
        
            step0_1 = Node(
                lambda x: (random.random() for _ in range(0, 5))
            ),

            step_2 = Node(
                lambda x: (random.random() for _ in range(0, 5))
            ),

            identity = Identity(join = True),

            step1_1 = Node(min),
            step1_2 = Node(len),
            step1_3 = Node(max),

            connections = [
                Connection("step0_1", "identity"),
                Connection("step0_2", "identity"),
                Connection("identity", "step1_1"),
                Connection("identity", "step1_2"),
                Connection("identity", "step1_3"),
            ]

        )

    In this case none of the operations in step 1 can be carried out without having access to the 
    full list of numbers generated in step 0. Accordingly, the outputs from step 0 need to be 
    concatenated before being input into step 1. That can be done by assigning all substeps of
    step 1 'join' behaviour, but doing so would be wasteful as this join would have to be carried
    out for each substep. By adding an intermediate identity node, the join is carried out but once.
    """

    def __init__(self, *args, **kwargs):

        """
        Initializes an `IdentityNode`.
        """

        super().__init__(*args, callable = lambda x: x, **kwargs)

        # End of method '__init__' #################################################################

    # End of class 'Identity' ######################################################################
        

# Repeater #########################################################################################

class Repeater(Node):

    """
    Takes any input received and repeats it a specified number of times before forwarding this to
    any subsequent nodes.

    A use case for this node is a situation wherein a previous output, perhaps produced under great
    computational expense, needs to be repeatedly fed to the subsequent nodes, which may process
    this output differently each time. For example, consider the following::

        Pipework(
        
            init = Node(
                lambda _: random.randint(0, 100)
            ),

            repeater = Repeater(10000),

            rand_cmp = Node(
                lambda x: x == random.randint(0, 100)
            ),

            p = Node(
                lambda xs: sum(xs) / len(xs),
                join = True
            ),

            connections = [
                Connection("init",     "repeater"),
                Connection("repeater", "rand_cmp"),
                Connection("rand_cmp",        "p")
            ]

        At first a random number is produced, which is then forwarded to a randomized comparison
        function checking if the same can be produced at random. 10.000 of such comparisons are
        made in parallel, to finally be aggregated, to determine the probability of a hit.

        )
    """

    def __init__(self, *args, n : int, **kwargs):

        """
        Sets up a repeater to repeat the input received by `n` times.

        Parameters
        ----------
        
        n 
            Number of times to repeat the input.
        """

        # Delegate to super class.
        super().__init__(*args, callable = lambda x: (x for _ in range(0, n)), **kwargs)

        # End of method '__init__' #################################################################

    # End of class 'Repeater' ######################################################################
        
# End of File ######################################################################################