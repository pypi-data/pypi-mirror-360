# ##################################################################################################
#
# Title:
#
#   pypeworks.typing.future.py
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
#   Part of the Pypeworks framework, implementing type hinting utilities for future use in 
#   Pypeworks.
#
# ##################################################################################################

# ##################################################################################################
# Dependencies
# ##################################################################################################

# Python standard library ##########################################################################

# Fundamentals
from types import (
    GenericAlias
)

import typing
from typing import (
    Generic,
    NotRequired,
    TypeVar
)

# TODO: Remove some time after Python 3.15 is released.
try:
    from typing_extensions import (
        TypedDict,
        TypeIs,
        overload
    )
except:
    from typing import (
        TypedDict
    )


# ##################################################################################################
# Types
# ##################################################################################################

Kwargs = TypedDict
"""
Alias for `typing.TypedDict <https://typing.python.org/en/latest/spec/typeddict.html>`_.
"""


# ##################################################################################################
# Classes
# ##################################################################################################

# Args #############################################################################################

_Arg = TypeVar("_Arg")
_Kwargs = TypeVar("_Kwargs")

class Args(Generic[_Arg, _Kwargs]):

    """
    Utility class for type hinting the return values of a :py:class:`~pypeworks.node.Node` function.
    This class primarily serves to name return values, so that one node's outputs may be mapped to
    another node's inputs.

    Consider for example the following example, wherein a node produces pairs of x and y coordinates
    in an incremental lineair fashion::

        class Pipeline(Pipework):
        
            @Pipework.connect(input = "enter")
            def init(self, _) -> Args[:, Kwargs({"x": int, "y": int})]:
            
                for i in range(0, 100):
                    yield i, i

            @Pipework.connect(input = "init")
            @Pipework.connect(output = "exit")
            def process(self, x : int, y : int):
            
                print(i, i)

    The class may also be used standalone to construct a dictionary from a group of arguments::

        Args[:, Kwargs({"x": int, "y": int})](123, 456).kwargs # {"x": 123, "y": 456}
    """

    # ##############################################################################################
    # Class attributes
    # ##############################################################################################

    # Private ######################################################################################

    __arg    : type[_Arg]
    __kwargs : type[_Kwargs]


    # ##############################################################################################
    # Class fundamentals
    # ##############################################################################################

    # __init__ #####################################################################################

    def __init__(self, *args, **kwargs):

        # ##########################################################################################
        # Argument handling
        # ##########################################################################################

        # Preparation ##############################################################################

        # Set-up class attributes.
        self.args   : tuple[_Arg, ...] = ()
        self.kwargs : _Kwargs          = {}

        # Set up temporary, helper variables.
        __kwargs : dict[str, type] = getattr(self.__kwargs or {}, "__annotations__", {})

        __kwargs_keys_required : set[str] = (
            {k for k, v in __kwargs.items() if typing.get_args(v) is not NotRequired}
        )

        __kwargs_keys_it = iter(__kwargs.keys())


        # Handle positional arguments ##############################################################

        # Error check cases wherein no args are expected.
        if self.__arg is None:

            # Check if args may be fitted onto kwargs.
            if len(args) > len(__kwargs):

                raise TypeError(
                    f"Args(...) was given {len(args)} positional arguments, but may only take"
                    f" {len(__kwargs)} arguments;" 
                )
        
        # Error check cases wherein an arg is expected.
        else:

            # Check if no more args were given than may be fitted.
            if len(args) > (1 + len(__kwargs)):

                raise TypeError(
                    f"Args(...) was given {len(args)} positional arguments, but may only take"
                    f" {1 + len(__kwargs)} arguments;" 
                )
            
        # Handle cases wherein no args have been passed.
        if len(args) == 0:
            
            # Do nothing, maintain defaults.
            pass

        # Handle cases wherein args have been passed.
        else: # if len(args) > 0

            # Set arg.
            if self.__arg is not None:
                self.args = (args[0], )

            # Set kwargs.
            self.kwargs = {k: v for v, k in zip(args[len(self.args):], __kwargs_keys_it)}

        
        # Handle keyword arguments #################################################################

        # Check for duplicates.
        if len(self.kwargs.keys() & kwargs.keys()) > 0:

            raise TypeError(
                "Args(...) got multiple values for arguments: "
                + "'" + ("', '".join(self.kwargs.keys() & kwargs.keys())) + "'"
            )

        # Check for redundancies.
        if len(kwargs.keys() - __kwargs.keys()) > 0:

            raise TypeError(
                "Args(...) got unexpected keyword arguments: "
                + "'" + ("', '".join(kwargs.keys() - __kwargs.keys())) + "'"
            )
        
        # Check for missings.
        if len(__kwargs_keys_required - (self.kwargs.keys() | kwargs.keys())) > 0:

            keys = __kwargs_keys_required - (self.kwargs.keys() | kwargs.keys())
            
            raise TypeError(
                f"Args(...) is missing required arguments: "
                + "'" + ("', '".join(keys)) + "'"
            )
        
        # Merge in passed kwargs.
        self.kwargs.update({k: kwargs[k] for k in __kwargs_keys_it})
        

        # End of '__init__' ########################################################################


    # __class_getitem__ (i.e. Args[]) ##############################################################

    def __class_getitem__(cls, params):
        
        """
        Args takes two generics:

            1. A type hint for the first value returned by a :py:class:`~pypeworks.node.Node`'s 
               callable. When type hinted, this first value will be passed to subsequent nodes as a
               unnamed, positional argument (`*args`). If this is not desired, pass a sentinel type 
               hint (`:`)::

                   node_1a = Node(lambda _: 123, returns = Args[int]),
                   node_1b = Node(lambda _: 123, returns = Args[:, Kwargs[{"y": int}]]),

                   node_2 = Node(lambda x = -1, y = -1: (x, y))
                   # Returns (123, -1) for node_1a's outputs, and (-1, 123) for node_1b's.

            2. (optionally) Type hints for return values to be passed forward as keyword arguments.
               These must be specified using `TypedDict` or its Pypeworks specific alias, 
               :py:class:`~typing.future.Kwargs`. If you do not wish to pass along keyword arguments
               skip definition of the second generic.
        """

        # TODO: This method may be deprecated if Python implements any built-in functionality to 
        # determine type parameters in __init__ and/or __new__.

        # ##########################################################################################
        # Argument handling
        # ##########################################################################################

        # Prepare variables to hold intermediate results ###########################################

        # Predeclare variables to hold intermediate results.
        arg    = None
        kwargs = None


        # Processing ###############################################################################

        # Handle cases wherein multiple arguments were passed.
        if isinstance(params, tuple):

            # Check for the sentinel, skipping assignment of arg if so.
            if not isinstance(params[0], slice):
                arg = params[0]

            kwargs = params[1]

        # Handle cases wherein only one argument was passed.
        else:

            # Check for the sentinel, skipping assignment of arg if so.
            if not isinstance(params, slice):
                arg = params

        # Create a new class annotated with the passed typing data for reuse during instantiation.
        # Note we need to base from a unparameterized Args to ensure to isinstance works correctly.
        new_cls = type(cls.__name__, (Args, *cls.__bases__), dict(cls.__dict__))

        new_cls.__arg = arg
        new_cls.__kwargs = kwargs

        # Return an alias referencing the newly created class.
        return (
            GenericAlias(
                new_cls, (
                    *((arg,) if arg is not None else ()), 
                    *((kwargs,) if kwargs is not None else ())
                )
            )
        )
    
        # End of '__class_getitem__' ###############################################################


    # __repr__ #####################################################################################

    def __repr__(self):

        return f"Args[args={self.args}, kwargs={self.kwargs}]"

        # End of '__repr__' ########################################################################


    # ##############################################################################################
    # Methods
    # ##############################################################################################

    # unpack #######################################################################################

    def unpack(self) -> tuple[_Arg, _Kwargs]:

        """
        Unpack wrapped `args` and `kwargs` into a tuple.
        """

        return self.args, self.kwargs
    
        # End of method 'unpack' ###################################################################


    # End of class 'Args' ##########################################################################


# End of File ######################################################################################