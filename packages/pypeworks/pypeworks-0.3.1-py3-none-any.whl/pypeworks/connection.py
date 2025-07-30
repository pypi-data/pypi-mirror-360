# ##################################################################################################
#
# Title:
#
#   pypeworks.connection.py
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
#   Part of the Pypeworks framework, implementing the Connection class, which governs how data is
#   passed around in pipeworks.
#
# ##################################################################################################

# ##################################################################################################
# Dependencies
# ##################################################################################################

# Python standard library ##########################################################################

# Fundamentals
from typing import (
    Callable,
    Generic,
    ParamSpec
)

# System
import warnings


# ##################################################################################################
# Classes
# ##################################################################################################

# Connection #######################################################################################

Ps = ParamSpec("Ps")

class Connection(Generic[Ps]):

    """
    Represents a connection between two Nodes in a Pipework.
    """

    # ##############################################################################################
    # Fundamentals
    # ##############################################################################################

    def __init__(
        self, 
        input  : str = None, 
        output : str = None, 
        where  : Callable[Ps, bool] = None, 
        greedy : bool = False, 
        nocopy : bool = False
    ):
        
        """
        Sets up the connection between the sending `input` node and the receiving `output` node.

        Parameters
        ----------

        input
            The name of the node that sends input.

        output
            The name of the node that receives input.

        where
            A function that evaluates the input received, returning a boolean that states whether or
            not this input should be forwarded to the next node. For example::

                Pipework(
                
                    example = Node(
                        lambda _: iter([
                            123,              # Processed by 'process_num'
                            'a',              # Processed by 'process_str'
                            datetime.now(),   # Not processed
                        ])
                    ),

                    connections = [
                    
                        Connection(
                            input = "example", output = "process_str", 
                            where = lambda x: isinstance(x, str)
                        ),

                        Connection(
                            input = "example", output = "process_num",
                            where = lambda x: isinstance(x, numbers.Number)
                        )
                    ]

                )
            
            Stating conditions using the `where`-argument has as benefit that data is not
            unnecessarily duplicated even when `nocopy` has been assigned `False`. By default
            everytime data is forwarded in a Pipework, that data is copied as to ensure that
            different nodes, potentially operating in different threads do not modify the same data.
            The condition stated by `where` is checked before doing so, preventing duplication and
            reducing memory usage.

        greedy
            Determines whether data is only forwarded using this connection when possible (i.e. when 
            the conditions stated by `where` are met), or whether data is also forwarded
            via any subsequent connections attached to the sender.

            Please note that greedy behaviour is affected by the order by which connections are
            declared. For example::

                Pipework(
                
                    step0 = Node(
                        lambda _ = range(0, 5)
                    ),

                    connections = [
                    
                        Connection(input = "step0", output = "step1"),

                        Connection(
                            input = "step0", output = "step2",
                            where = lambda self, x: x < 3, greedy = True
                        ),

                        Connection(input = "step0", output = "step3"),

                    ]
                )

            In the above example the numbers 1, 2, 3, 4 will all be forwarded to `step1`, whereas
            `step3` will only receive the numbers 3 and 4, with the preceding numbers, 1 and 2,
            being processed by `step2`.

        nocopy
            Whether to forego copying objects pushed through this connection. By default
            copies are made to prevent nodes potentially operating in different threads from 
            modifying the same data. In case none of the connecting nodes modify the data input,
            i.e. when this data is only read, one might opt to skip copying to save processing
            cycles.
        """
        
        # ##########################################################################################
        # Argument handling
        # ##########################################################################################

        # input
        if (input is None):

            raise ValueError(
                "Expected an argument for both 'input' and 'output', got None for 'input';"
            )
        
        # output
        if (output is None):

            raise ValueError(
                "Expected an argument for both 'input' and 'output', got None for 'output';"
            )
        
        # where, greedy
        if (where is None) and (greedy is True):

            warnings.warn(
                "A greedy connection was defined, but no conditions were stated; data will not be"
                " propogated through any subsequent connections of the receiving node;"
            )


        # ##########################################################################################
        # Attribute initialization
        # ##########################################################################################
            
        # Sender
        self.sender_name = input
        self.sender_id = None # Assigned by Pipework.__init__

        # Receiver
        self.receiver_name = output
        self.receiver_id = None # Assigned by Pipework.__init__

        # Other
        self.where = where
        self.greedy = greedy
        self.nocopy = nocopy

        # End of method '__init__' #################################################################

    # End of class 'Connection' ####################################################################
        
# End of File ######################################################################################