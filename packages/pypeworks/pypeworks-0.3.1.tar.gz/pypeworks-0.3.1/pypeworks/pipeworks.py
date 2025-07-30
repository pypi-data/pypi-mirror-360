# ##################################################################################################
#
# Title:
#
#   pypework.pipeworks.py
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
#   Part of the Pypeworks framework, implementing various specialised pipework classes.
#
# ##################################################################################################

# ##################################################################################################
# Dependencies
# ##################################################################################################

# Python standard library ##########################################################################

# Fundamentals
import copy
import itertools
import threading

from typing import (
    Callable,
    Literal,
    TypeVar
)

import warnings


# Local ############################################################################################

from .connection import (
    Connection
)

from .pipework import (
    Pipework
)

from .node import (
    Node
)


# ##################################################################################################
# Classes
# ##################################################################################################

# Replicator #######################################################################################

T = TypeVar("T")
R = TypeVar("R")

class Replicator(Pipework[T, R]):

    """
    A `Replicator` is a procedually generated pipework generated from a single 
    :py:class:`pypeworks.Node`,  whereby said node is replicated in parallel together with a network 
    of connections that distributes input across these replications. Replicators are ideally suited 
    to scale nodes that have a long execution time.
    """

    def __init__(
        self, 
        node         : Node[T], 
        replications : int, 
        processes    : int                                       = None, 
        nocopy       : bool                                      = False,
        copying      : None | Literal["auto", "deep", "shallow"] = "deep"
    ):
        
        """
        Instantiates a new Replicator.

        Parameters
        ----------
        node
            Node to replicate.
        
        replications
            The number of replications to generate.

        processes
            The number of worker processes to use to operate the underlying 
            :py:class:`pypeworks.Pipework`. By default this number is equal to the number of 
            logical CPUs in the system.

        nocopy
            .. deprecated:: v0.3.0
                Use `copying` instead. This argument will be removed by v0.4.0.

        copying
            Specifies whether and how to assign each replication its own of the node. By default 
            (`"deep"`) each replication is assigned a deep copy of the given node. Alternatively,
            one may also opt for a shallow copy (using `"shallow"`), allowing for easier handling
            of nodes wrapping unpickable objects. When set to `"auto"`, the replicator will first
            try to make a deep copy, opting for a shallow copy if this fails. If no copying is
            desired, this value may be set to `None`, allowing for the node to be shared among
            replications. However, beware thread-safety and side-effects when working with
            (automatic) shallow or none-copies!
        """

        # ##########################################################################################
        # Initialization
        # ##########################################################################################

        # Set-up scheduling mechanism ##############################################################

        # Assign variable to keep track of replication scheduled next to process input.
        current : int = 0

        # Set up lock, to govern access to tracker.
        current_lock : threading.Lock = threading.Lock()

        # Set-up thread-safe function to update the scheduler using a simple spinning mechanism.
        def check_schedule(r : int):

            # Access variables in the body of '__init__'
            nonlocal current
            nonlocal current_lock

            # Acquire lock to access variable.
            with current_lock:

                # Check if the current replication has been scheduled for processing.
                if r == current:

                    # If so, update the schedule, and return a positive feedback.
                    current = (current + 1) % replications
                    return True

                # Otherwise, give a negative feedback.
                return False
            
            # End of inner function 'spin' #########################################################

        
        # Set-up inner pipework ####################################################################

        # Handle deprecation of 'nocopy'.
        if nocopy == True:

            # Alter `copying`.
            copying = None

            warnings.warn(

                "Argument `nocopy` of class Replicator has been deprecated; please switch to use"
                " of `copying` by 0.4.0;",

                DeprecationWarning
            )
            

        # Pre-define function handling copying behaviour.
        copy_node : Callable[[Node], Node] = None

        if copying == "deep":
            copy_node = copy.deepcopy

        elif copying == "shallow":
            copy_node = copy.copy

        elif copying == "auto":
            
            def copy_node(node : Node):

                try:
                    return copy.deepcopy(node)
                except:
                    return copy.copy(node)
                
        
        # Delegate to super class.
        super().__init__(

            # Configuration ########################################################################

            processes = processes,

            # Nodes ################################################################################           
                
            # Register a node for each replication.
            **{
                f"r{i}": (node if copying is None else copy_node(node)) 
                for i in range(0, replications)
            },

            # Connections ##########################################################################

            # Connect all replications to the entry and exit points.
            connections = list(
                # Flatten list of pairs as generated below.
                itertools.chain.from_iterable([
                    # Generate for each replication a connection to the entry point, and a 
                    # connection to the exit point.
                    (
                        # Create a connection from the entry point to the replication.
                        Connection(

                            # Define input and output.
                            "enter", f"r{i}",

                            # Only forward to the replication scheduled to process next.
                            where = (lambda r: (lambda _: check_schedule(r)))(i),
                            greedy = True,
                            
                            # No need to cover for side-effects.
                            nocopy = True
                        ),
                        
                        # Create a connection from replication to exit point.
                        Connection(f"r{i}", "exit", nocopy = True)
                    )
                    for i in range(0, replications)
                ])
            )
        )

        # End of '__init__' ########################################################################

    # End of class 'Replicator' ####################################################################

# End of File ######################################################################################