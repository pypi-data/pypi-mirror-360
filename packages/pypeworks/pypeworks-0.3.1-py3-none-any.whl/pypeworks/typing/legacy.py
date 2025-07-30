# ##################################################################################################
#
# Title:
#
#   pypeworks.typing.legacy.py
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
#   Part of the Pypeworks framework, implementing various classes that help typehint pipework nodes.
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
from typing import(
    Any,
    Callable
)


# Name #############################################################################################


class Name:

    """
    Class used in conjunction with the :py:class:`Param` class to assign a name to a return value.
    """

    def __class_getitem__(cls, name : str):

        return GenericAlias(Name, name)
    
        # End of method '__class_getitem__' ########################################################
    
    # End of class 'Name' ##########################################################################
    

# Default ##########################################################################################

class Default:

    """
    Class used in conjunction with the :py:class:`Param` class to assign a default value for a 
    return value.
    """

    def __class_getitem__(cls, value : Any):

        return GenericAlias(Default, value)
    
        # End of method '__class_getitem__' ########################################################
    
    # End of class 'Default' #######################################################################


# Factory ##########################################################################################

class Factory:

    """
    Class used in conjunction with the :py:class:`Param` class to specify a default factory for a 
    return value.
    """

    def __class_getitem__(cls, factory : Callable[[], Any]):

        return GenericAlias(Factory, factory)
    
        # End of method '__class_getitem__' ########################################################
    
    # End of class 'Factory ########################################################################


# _ParamAlias ######################################################################################
    
class _ParamAlias(GenericAlias):
    pass

    # End of class '_ParamAlias' ###################################################################


# Param ############################################################################################

class Param:

    """
    Class used in conjunction with :py:class:`Args` to typehint the return values of a function. The
    user is expected to specify at least the type (at index 0).

    Note that `Param`-objects can be build up using both positional and named attributes. So any of
    the following specifications are valid::

        Param[int]
        Param[int, "x"]
        Param[int, Name["x"]]
        Param[int, "x", 0]
        Param[int, "x", Default[0]]
        Param[int, Default[0], Name["x"]]

    Mixing is subject to general Python rules. So the following is not possible::

        Param[int, Name["x"], 0] # Invalid
    """

    def __class_getitem__(cls, args : Any | tuple[Any | Name | Default | Factory]):

        # ##########################################################################################
        # Argument handling
        # ##########################################################################################

        # args #####################################################################################

        # Prepare variables to hold result.
        metadata : dict[str, Any] = dict()

        # Handle cases whereby only one argument was passed.
        if not isinstance(args, tuple):

            if not isinstance(args, (type)):

                # Raise error if the first argument was anything else but the type specification.
                raise TypeError(
                    f"Expected type specification at index '0', but annotation"
                    f" '{typing.get_origin(args)}' was passed instead;"
                )
            
            # Store type information.
            metadata["type"] = args
            
        # Handle cases whereby multiple arguments were passed.
        else:

            # Raise error if the first argument was anything else but the type specification.
            if typing.get_origin(args[0]) in [Name, Default, Factory]:

                raise TypeError(
                    f"Expected type specification at index '0', but annotation"
                    f" '{typing.get_origin(args[0])}' was passed instead;"
                )
            
            # Store type information.
            metadata["type"] = args[0]

            # Set-up variable to track whether a named argument was used.
            named_arg : bool = False
            
            # Check validity of remaining arguments.
            for i, arg in enumerate(args[1:]):

                # Predeclare variables to represent argument as key-value pair.
                key  : str = None
                value : Any = None

                # Retrieve origin of the argument, or type if a non-annotated object was passed.
                type_ = typing.get_origin(arg) or type(arg)

                # Check if a positional argument was passed.
                if type_ not in [Name, Default, Factory]:

                    # Check if positional arguments are not mixed with named arguments.
                    if named_arg == True:

                        raise TypeError(
                            f"Positional argument follows key word argument;"
                        )

                    # Attempt to handle argument based on its position.
                    if i == 0 and type_ == str:
                        key = "name"

                    elif i == 1:
                        key = "default"

                    elif i == 2 and hasattr(arg, "__call__"):
                        key = "factory"

                    else:
                        
                        raise TypeError(
                            f"Expected one of 'Name', 'Default' or 'Factory' to be specified, but"
                            f" received object of type '{type_}' at index '{i}' instead;"
                        )
                    
                    # Assign value.
                    value = arg

                # Handle named arguments.
                else:

                    # Assign name as key.
                    key = type_.__qualname__.lower()

                    # Retrieve value.
                    value = typing.get_args(arg)[0]

                    # Set flag to signify that a named argument was processed.
                    named_arg = True
                
                # Check if a argument of the same type was already processed before.
                if key in metadata:

                    raise TypeError(
                        f"Received second object of type '{key}' at index '{i};" 
                    )
                
                else:

                    # Store key-value pair
                    metadata[key] = value

        # ##########################################################################################
        # Return alias
        # ##########################################################################################

        return _ParamAlias(Param, metadata)
    
        # End of method '__class_getitem__' ########################################################
    
    # End of class 'Param' #########################################################################


# _ArgsAlias #######################################################################################
    
class _ArgsAlias(GenericAlias):
    pass

    # End of class '_ArgsAlias' ####################################################################


# Args #############################################################################################

class Args:

    """
    Class that can be used to typehint the return values of a function, allowing for these return
    values to be named and to be assigned a default value or factory. Within `pypeworks` this class
    is used to map one Node's outputs to another Node's input parameters.

    Consider for example the following example, wherein a node produces pairs of x and y coordinates
    in an incremental lineair fashion::

        class Pipeline(Pipework):
        
            @Pipework.connect(input = "enter")
            def init(self, _) -> Args[Param[int, "x"], Param[int, "y"]]:
            
                for i in range(0, 100):
                    yield i, i

            @Pipework.connect(input = "init")
            @Pipework.connect(output = "exit")
            def process(self, x : int, y : int):
            
                print(i, i)

    The class may also be used standalone to construct a dictionary from a group of arguments::

        sig = Args[Param[int, "x", 0], Param[int, "y", 0]]

        # Single argument
        Args(123, sig).kwargs # {'x': 123, 'y': 0}  

        # Two arguments (passed as tuple)
        Args((123, 456), sig).kwargs # {'x': 123, 'y': 0}  

    """

    # ##############################################################################################
    # Class fundamentals 
    # ##############################################################################################

    # __init__ #####################################################################################

    def __init__(self, args : tuple[Any, ...] | Any, params : _ArgsAlias):

        """
        Constructs a dictionary according to specification outlined by `params` from the given 
        group of arguments passed to `args`.

        Parameters
        ----------

        args
            Argument(s) to be wrapped in a dictionary;
        params
            `Args`-alias to be used as guideline for the conversion;
        """

        # ##########################################################################################
        # Argument handling
        # ##########################################################################################

        # args #####################################################################################

        # Wrap non-tuples in a tuple.
        if not isinstance(args, tuple):
            args = (args, )


        # params ###################################################################################

        # Check if an Args-alias was passed for params.
        if not isinstance(params, _ArgsAlias):

            raise ValueError(
                f"Object '{str(params)}' was passed for 'params' were 'Args[...]' was expected;" 
            )
        
        # Unwrap alias.
        params : list[dict[str, Any]] = typing.get_args(params)[0]


        # ##########################################################################################
        # Build up args
        # ##########################################################################################

        # Set-up args member.
        self.args : list[Any] = []

        if len(params) > 0 and params[0].get("name", None) is None:
            self.args = [args[0]]


        # ##########################################################################################
        # Build up kwargs
        # ##########################################################################################

        # Set-up kwargs members.
        self.kwargs : dict[str, Any] = dict()

        args_offset = len(self.args)

        # Determine number of arguments passed.
        kwargs_len = len(args) - args_offset
        
        # Iterate over possible number of parameters.
        for i in range(len(params) - args_offset):

            # Get argument (if any) and parameter at given index.
            arg   : Any            = args[i + args_offset] if i < kwargs_len else None
            param : dict[str, Any] = params[i + args_offset]
            
            # Add argument to internal dictionary.
            self.kwargs[param["name"]] = (
                (
                    arg or param.get("default", None) or param.get("factory", lambda: None)()
                )
                if arg != 0 else 0
            )


        # End of '__init__' ########################################################################


    # __class_getitem__ ############################################################################

    def __class_getitem__(cls, params : Param | tuple[Param]) -> _ArgsAlias:

        # ##########################################################################################
        # Argument handling
        # ##########################################################################################

        # params ###################################################################################

        # Set-up intermediate variable to hold references to dict-represented parameters.
        dict_params : list[dict[str, Any]] = list()

        # Check if multiple parameters were passed.
        if isinstance(params, tuple):

            # Iterate over the given parameters.
            for i, param in enumerate(params):

                # Check if a Param object was used to define the parameter.
                if not isinstance(param, _ParamAlias):

                    raise TypeError(
                        f"Object of type '{type(param)}' at index '{i}' was passed to"
                        f" Args where object of type 'Param' was expected;"
                    )
                
                # Get dictionary representation of parameter.
                param_dict = typing.get_args(param)[0]
                
                # Check if no more than one arg is defined.
                if i > 0 and param_dict.get("name", None) is None:

                    raise ValueError(
                        f"Object at index '{i}' was passed without specifying a name, while this"
                        " may only be done for Param objects at index '0';"
                    )
                
                # Get dictionary representation of parameter, and store reference to it.
                dict_params.append(param_dict)
                
        # Handle case wherein only one parameter was passed, check if it is wrapped by Param object.
        elif not isinstance(params, _ParamAlias):

            raise TypeError(
                f"Object of type'{typing.get_origin(params)}' was passed to Args where object of"
                f" type 'Arg' was expected;"
            )
        
        # Handle singular parameters wrapped by a Param object.
        else:
            dict_params.append(typing.get_args(params)[0])


        # ##########################################################################################
        # Generate alias
        # ##########################################################################################

        return _ArgsAlias(Args, dict_params)
    
        # End of method '__class_getitem__' ########################################################
    

    # __repr__ #####################################################################################

    def __repr__(self):

        return f"Args[arg={self.args}; kwargs={self.kwargs}]"
    
        # End of method 'kwargs' ###################################################################
    
    # End of class 'Args' ##########################################################################

# End of File ######################################################################################