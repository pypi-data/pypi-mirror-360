# ##################################################################################################
#
# Title:
#
#   pypework.pipework.py
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
#   Part of the Pypeworks framework, implementing the Pipework class, a finite state machine to 
#   process data in parallel.
#
# ##################################################################################################

# ##################################################################################################
# Dependencies
# ##################################################################################################

# Python standard library ##########################################################################

# Fundamentals
import collections
import copy

from dataclasses import (
    dataclass,
    field
)

import functools
import itertools
import operator
import queue

import typing
from typing import (
    Any,
    Callable,
    Generic,
    Iterator,
    Literal,
    Sequence,
    TypeVar
)

# System
import logging
import multiprocessing.pool
import threading
import time
import traceback
import warnings

# Util
import graphlib
import textwrap


# Local ############################################################################################

from .connection import (
    Connection
)

from .node import (
    Node
)

from .typing import (
    Args,
    _ArgsAlias,
    Param
)

from pypeworks.typing.future import (
    Args as fArgs
)

from .util import (
    flatten
)


# ##################################################################################################
# Classes
# ##################################################################################################

# __QueuedItem__ ###################################################################################
        
@dataclass(order = True)
class __QueuedItem__:

    """
    Utility class to work the Pipework's priority queue.
    """

    node_id : int
    obj_id  : int = field(compare = False)

    # End of class '__QueuedItem__' ################################################################


# __NodeCounter__ ##################################################################################
    
@dataclass
class __NodeCounter__:

    """
    Utility class to keep count of the number of objects being held by a node.
    """

    cnt  :            int = field(default = 0)
    lock : threading.Lock = field(default_factory = threading.Lock)

    # End of class '__NodeCounter__' ###############################################################


# __NodeError__ ####################################################################################

@dataclass
class __NodeError__:

    """
    Utility class to register errors occuring within nodes.
    """

    # ##############################################################################################
    # Properties
    # ##############################################################################################

    pipework : type["Pipework"] = field(default = None)

    node_id : int               = field(default = -1)

    error   : BaseException     = field(default = None)

    args    : list[Any]         = field(default_factory = list)
    kwargs  : dict[str, Any]    = field(default_factory = dict)


    # ##############################################################################################
    # Methods
    # ##############################################################################################

    def format_error_message(self):

        # Set-up buffer to hold components of the error message.
        msg : list[str] = []

        # Generate a traceback of nodes.
        node : Node = self.pipework.nodes_by_id.get(self.node_id, None)

        while node is not None:

            msg.append(
                # Object
                f"{type(node).__qualname__}"
                # Identifier
                f" {('"' + node.name + '"') if node.name is not None else '<anonymous>'}"
                # Parameters
                + (
                    f", with parameters <args = {self.args}, kwargs = {self.kwargs}>" 
                    if len(msg) == 0 else ""
                ) +
                # Hierarchy
                f", in\n"
            )

            node = node.parent

        # Add traceback of calls.
        msg = (
            # Reverse initial messages, to read through the hierarchy from top to bottom.
            msg[::-1]
            # Get only calls within nodes.
            + traceback.format_exception(type(self.error), self.error, self.error.__traceback__)[2:]
        )

        # Add indentation.
        msg = [
            textwrap.indent(msg, " " * indent) 
            for indent, msg in zip(range(2, 2 + 2 * len(msg), 2), msg)
        ]

        # Add traceback header.
        msg = (["Traceback (most recent call last):\n"] + msg)

        # Convert to single string, and return result.
        return "".join(msg)

        # End of method 'format_error_message' #####################################################

    # End of class '__NodeError__' #################################################################


# __ObjectHandle__ #################################################################################
    
@dataclass
class __ObjectHandle__:

    """
    Utility class to store a thread-safe, counted reference to an object.
    """

    refs      :            int = field(default = 0)
    refs_lock : threading.Lock = field(default_factory = threading.Lock)
    obj       :            Any = field(default = None)

    # End of class '__ObjectHandle__' ##############################################################


# Pipework #########################################################################################

T = TypeVar("T")
R = TypeVar("R")

class Pipework(Node[Iterator[T] | T], Generic[T, R]):

    """
    A `Pipework` is a directed acylic graph composed of nodes and connections. Each `Node` serves as
    a standalone processing unit that takes in data, transforms it, and outputs it. `Connection`
    objects move this data throughout the pipework, until data reaches the exit node.

    A `Pipework` may be declared through sub-classing, allowing them to be templated::

        class ExamplePipework(Pipework):
        
            @Pipework.connect(input = "enter")
            @Pipework.connect(output = "exit")
            def passthrough(self, x):
                return x

    A `Pipework` may also be declared on the fly, allowing them to be dynamically instantiated::

        Pipework(
        
            passthrough = Node(lambda x: x),

            connections = [
                Connection("enter"       , "passthrough"),
                Connection("passthrough" , "exit"       )
            ]
        )

    Furthermore, both instantiation methods may be mixed::

        class ExamplePipework(Pipework):
        
            @Pipework.connect(input = "enter")
            def prepare(self, x):
                return str(x)

        ExamplePipework(
        
            passthrough = Node(lambda x: x),

            connections = [
                Connection("prepare"     , "passthrough"),
                Connection("passthrough" , "exit"       )
            ]
        )

    """

    # ##############################################################################################
    # Static attributes
    # ##############################################################################################

    # Internal #####################################################################################

    __connections__: dict[str, list[Connection]] = dict()
    """List of all the defined connections in the pipework."""


    # ##############################################################################################
    # Fundamentals
    # ##############################################################################################

    # __init__ #####################################################################################

    def __init__(
        self, 
        processes     : int                     = None,
        connections   : list[Connection]        = None, 
        logger        : logging.Logger          = None,
        ignore_errors : Sequence[BaseException] = None,

        join          : bool                    = False,
        join_groupby  : list[str]               = None,
        join_flatten  : bool                    = False,

        **nodes       : dict[str, Node]
    ):
        
        """
        Instantiates a new Pipework.

        Parameters
        ----------

        procesess
            The number of worker processes to use to operate the `Pipework`. By default this number 
            is equal to the number of logical CPUs in the system.

        connections
            The connections between the nodes in the `Pipework`.

        logger
            Logger compatible with Python's 
            `logging <https://docs.python.org/3/library/logging.html>`_ module, providing control 
            over the registration of events occuring within the Pipework.

            .. versionadded:: 0.2.0

        ignore_errors
            Sequence of errors (and exceptions), which if raised, are ignored by the Pipework,
            allowing it to continue execution.

            .. versionadded:: 0.2.0

        nodes
            The nodes that make up the `Pipework`.

        """

        # ##########################################################################################
        # Instantiation
        # ##########################################################################################

        # Internal #################################################################################

        # __path__   :   Describes the path of the class.
        self.__path__ = f"{self.__module__}.{type(self).__name__}"


        # ##########################################################################################
        # Argument handling
        # ##########################################################################################

        # connections ##############################################################################

        # Set-up attribute to hold a list of all connections, initially setting it to the list of 
        # connections defined as part of the template.
        self.connections : list[Connection] = Pipework.__connections__.get(self.__path__) or []
            
        # Add the connections defined on runtime, but do so only after making a deep copy of these
        # connections as to prevent potential side-effects.
        self.connections += copy.deepcopy(connections) if connections is not None else []


        # nodes (kwargs) ###########################################################################

        ### Merge design-time and runtime nodes ####################################################

        nodes = {
            
            # Design time
            **{
                name: Node(
                    callable     = func, 
                    join         = getattr(func, "join", False),
                    join_groupby = getattr(func, "join_groupby", None),
                    join_flatten = getattr(func, "join_flatten", False)
                )
                # Get unique (method) names of all nodes referenced in connections.
                for name in 
                set(
                    # Flatten the list.
                    itertools.chain.from_iterable(
                        # Extract all (method) names referenced by connections defined.
                        [(conn.sender_name, conn.receiver_name) for conn in self.connections]
                    )
                )
                if name != "enter" and name != "exit" and hasattr(self, name)
                # Get reference to the method.
                for func in (getattr(self, name),)
            },

            # Runtime
            **nodes
        }


        ### Draw up lookup map for nodes indexed by name ###########################################

        # Set-up attribute to hold lookup map for nodes indexed by name.
        self.nodes_by_name : dict[str, Node] = dict()

        # Iterate over unspecified key-value arguments (kwargs) representing the nodes.
        for key, value in nodes.items():

            # Only handle nodes.
            if not isinstance(value, Node):
                
                raise TypeError(
                    f"Object of type '{type(value)}' was passed where object of type 'Node' was"
                    f"expected;"
                )
            
            # Store node in the lookup map.
            self.nodes_by_name[key] = value

            # Extra: piggyback loop to assign name attribute of the node, and to add a reference to
            # this pipework.
            value.name = key
            value.parent = self

        # Check for default nodes.
        if self.nodes_by_name.get("enter", None) is None:

            self.nodes_by_name["enter"] = (

                Node(
                    lambda *args, **kwargs: (

                        # If kwargs were passed, produce an argument signature matching these
                        # kwargs to be able to forward these kwargs.
                        Args(

                            (*args[:1], *kwargs.values()),

                            Args[
                                *([Param[type(input), "input"]] if len(args) > 0 else []),
                                *[Param[type(v), k] for k, v in kwargs.items()]
                            ]

                        )

                        if len(kwargs) > 0 else

                        # If no kwargs were produced, we only need to forward the input.
                        args[0]
                    )
                )

            )

        if self.nodes_by_name.get("exit", None) is None:
            self.nodes_by_name["exit"] = Node(lambda x: x)


        # processes ################################################################################

        self.processes = processes


        # logger ###################################################################################

        # Store the passed logger, or instantiate a new logger.
        self.logger : logging.Logger = logger or logging.Logger(f"<Pipework {hash(self)}>")


        # ignore_errors ############################################################################

        # Validate the argument.
        if ignore_errors is not None and not hasattr(ignore_errors, "__len__"):

            raise ValueError(
                f"Excepted a sequence (i.e. a list or tupple) for 'ignore_errors', but"
                f" '{ignore_errors}' was passed instead;"
            )

        # Store argument.
        self.ignore_errors : tuple[BaseException] | None = None

        if ignore_errors is not None and len(ignore_errors) > 0:
            self.ignore_errors = tuple(ignore_errors)
            

        # ##########################################################################################
        # Processing
        # ##########################################################################################      

        # Determine ordering of nodes in the pipework ##############################################
        
        ### Determine dependencies among nodes #####################################################
        
        # Set-up variable to hold data on dependencies, stored as dict with the key representing
        # the sender, and the value composed by a list of receivers.
        dependencies : dict[str, set[str]] = {}

        # Set-up list to hold potential deletions (if connections are assigned to undefined nodes).
        deletions : list[int] = []
            
        # Iterate over all connections.
        for i, connection in enumerate(self.connections):
        
            # Type check
            if not isinstance(connection, Connection):

                raise TypeError(
                    f"Object of type '{type(connection)}' was passed for 'connections' where"
                    f"type 'Connection' was expected;"
                )
            
            # Check if sender and receiver exist.
            if self.nodes_by_name.get(connection.sender_name, None) is None:

                # Give warning.
                warnings.warn(
                    f"Connection defined between '{connection.sender_name}' and"
                    f" '{connection.receiver_name}',but no node with name"
                    f" '{connection.sender_name}' could be found; ignorning connection;"
                )

                # Flag for deletion and skip processing.
                deletions.append(i)
                continue

            if self.nodes_by_name.get(connection.receiver_name, None) is None:

                # Give warning.
                warnings.warn(
                    f"Connection defined between '{connection.sender_name}' and"
                    f" '{connection.receiver_name}', but no node with name"
                    f" '{connection.receiver_name}' could be found; ignorning connection;"
                )

                # Flag for deletion and skip processing.
                deletions.append(i)
                continue
            
            # Each key-value pair represents a sender and its associated receivers.
            receivers = dependencies.setdefault(connection.sender_name, set())

            # Add a new receiver.
            receivers.add(connection.receiver_name)

        # Delete redundant connections.
        for i in sorted(deletions, reverse = True):
            del self.connections[i]

        del deletions


        ### Determine actual ordering of nodes #####################################################
            
        # Store the data on the ordering internally for later reuse.
        self.ids_by_name : dict[str, int] = (
            {
                # Each node is represented with a key-value pair, with the key being the node's
                # qualified name, and the value the node's ordered index number.
                k: n 
                for n, k in enumerate(
                    # Generate a list using the nodes' qualified names, sorted by execution
                    # order.
                    list(
                        # Sort nodes with graphlib, using dependency map.
                        graphlib.TopologicalSorter(dependencies).static_order()
                    )[::-1]
                )
            }
        )

        # Set-up reverse look-up dictionary for potential downstream use.
        self.names_by_id : dict[int, str] = {v: k for k, v in self.ids_by_name.items()}


        # Complete connections data ################################################################

        # Set-up attribute to hold lookup map to quickly access connections by sending id.
        self.connections_by_id : dict[int, list[Connection]] = dict()

        # Iterate over all connections.
        for connection in self.connections:

            # Add sender's and receiver's id as derived from their index number ####################
            connection.sender_name_id = self.ids_by_name.get(connection.sender_name, None)
            connection.receiver_name_id = self.ids_by_name.get(connection.receiver_name, None)

            # Piggyback to draw up lookup map for connections as indexed by name ###################
            (
                self.connections_by_id
                .setdefault(connection.sender_name_id, [])
                .append(connection)
            )

        
        # Set-up lookup maps for quick access ######################################################
            
        # Create a lookup map indexed by id to quickly access individual nodes.
        self.nodes_by_id : dict[int, Node] = {
            self.ids_by_name[name]: node for name, node in self.nodes_by_name.items()
        }


        # ##########################################################################################
        # Delegation to super class
        # ##########################################################################################
        
        # Node
        super().__init__(

            callable = self.__call__, 

            join         = join,
            join_groupby = join_groupby,
            join_flatten = join_flatten
            
        )


    # End of '__init__' ############################################################################


    # __call__ #####################################################################################        

    def __call__(self, *args : Iterator[T] | T, **kwargs) -> Iterator[R]:

        """
        Pushes data into the `Pipework`, returning a generator that may be used to retrieve data as
        processed by the pipework.

        .. tip::

            In case you want this method to return type hints, add annotations when instantiating
            the pipework itself::

                Pipework[int, str](
                    x # Shows as : int
                ) # Shows as -> str
        """

        # ##########################################################################################
        # Argument handling
        # ##########################################################################################

        # args #####################################################################################

        # Check if not too many arguments were passed.
        if len(args) > 1:

            raise ValueError(
                "Pipework only takes at most one unnamed argument (arg);"
            )
        

        # args, kwargs #############################################################################

        if len(args) == 0 and len(kwargs) == 0:

            raise ValueError(
                "Pipework requires at least one argument, either named (kwarg) or unnamed (arg), to"
                " be passed;"
            )
        

        # ##########################################################################################
        # Get references to commonly reused data
        # ##########################################################################################

        # Entry point ##############################################################################

        # Get id of entry point.
        # (note: we do not assume this to be zero as the pipework might be be unproperly plumbed)
        enter_id : int = self.ids_by_name.get("enter", None)

        # Check if the pipework contains an entry point.
        if enter_id is None:

            raise IndexError(
                "Entry point was not found; cannot insert data into pipework;"
            )

        # Exit point ###############################################################################

        # Get id of exit point.
        # (note: we do not assume this to be equal to the number of nodes in the pipework as the 
        #        pipework might be be unproperly plumbed)
        exit_id : int = self.ids_by_name.get("exit", None)

        # Check if the pipework contains an exit.
        if exit_id is None:

            raise IndexError(
                "Exit was not found; cannot retrieve final results from pipework;"
            )
        

        # ##########################################################################################
        # Populate priority queue and set-up supporting, thread-safe infrastructure
        # ##########################################################################################

        # Set-up data structures ###################################################################

        # Lookup map indexed by identifiers of objects for which the 'handles' are stored, that is a 
        # manually counted reference to the object. This lookup map is used to minimize the overhead
        # of the priority queue operated. As both the lookup map itself and the individual object's
        # references counts can be manipulated accross threads, both are assigned locks.
        object_handles : dict[int, __ObjectHandle__] = dict()
        object_handles_lock : threading.Lock = threading.Lock()

        # Priority queue ordered by the identifier of the nodes to which an object has been pushed.
        objects_queue : queue.PriorityQueue[__QueuedItem__] = queue.PriorityQueue()

        # Queue length counter to keep track whether any outstanding objects are still being 
        # processed.
        objects_len : int = 0
        objects_len_lock : threading.Lock = threading.Lock()

        # Counters for each node.
        counters : dict[int, __NodeCounter__] = {
            node_id: __NodeCounter__() for node_id in self.names_by_id.keys()
        }


        # Set-up supporting functions ##############################################################

        def push_object(obj : Any, to : int, nocopy : bool = False):

            """
            Pushes object `obj` to the connection specified by `to`, if needed making a deep copy
            before doing so as to prevent side-effects.
            """

            # ######################################################################################
            # Access superceding function's variables
            # ######################################################################################

            nonlocal object_handles
            nonlocal objects_queue
            nonlocal objects_len
            nonlocal objects_len_lock
            nonlocal counters

            # ######################################################################################
            # Push object
            # ######################################################################################

            # Get local reference to counter.
            counter = counters[to]

            # Get exclusive access to counters.
            with objects_len_lock and counter.lock:

                # Update counters.
                objects_len += 1
                counter.cnt += 1

                # Make a copy of the object if necessary.
                if nocopy is False:
                    obj = copy.deepcopy(obj)

                # Get object identifier.
                obj_id = id(obj)
                
                # Add object to the stack.
                obj_handle         : __ObjectHandle__ = None

                with object_handles_lock:

                    obj_handle = object_handles.setdefault(obj_id, __ObjectHandle__(obj = obj))
                    
                    with obj_handle.refs_lock:
                        obj_handle.refs += 1

                # Add object to the priority queue
                objects_queue.put(
                    __QueuedItem__(node_id = to, obj_id = obj_id)
                )

            # End of inner function 'push_object' #################################################
                
        
        def release_object(node_id : int, obj_id : int = None):

            """
            Updates counters associated with the given node upon releasing an object.

            Optionally also updates reference count for given object.
            """

            # ######################################################################################
            # Access superceding function's variables
            # ######################################################################################

            nonlocal objects_len
            nonlocal objects_len_lock
            nonlocal counters
            nonlocal object_handles

            # ######################################################################################
            # Release object
            # ######################################################################################

            # Get counter.
            counter = counters[node_id]

            # Acquire locks to safely alter the counts.
            with objects_len_lock and counter.lock:

                objects_len -= 1
                counter.cnt -= 1

            # ######################################################################################
            # Update reference count (if needed)
            # ######################################################################################
                
            # Check if the reference count needs to be updated.
            if obj_id is None:
                return
            
            # Get exclusive handle on object.
            with object_handles_lock:

                # Get handle on object.
                obj_handle = object_handles.get(obj_id, None)

                # If no handle was retrieved, something went wrong.
                if obj_handle is None:
                    
                    self.logger.warning(
                        f"Attempted to retrieve handle to object with id '{obj_id}', but none was"
                        f" retrieved;"
                    )

                    return

                # Get exclusive access to reference count of the object.
                with obj_handle.refs_lock:

                    # Update reference count.
                    obj_handle.refs -= 1

                    # Delete the object if it is no longer referenced by anything.
                    if obj_handle.refs <= 0:
                        del object_handles[obj_id]

            # End of inner function 'release_object' ###############################################


        # Populate the queue #######################################################################
                
        # Predine variable to hold worker (or mock representation) used to populate the stack.
        populate_thread : threading.Thread = None
                
        # Determine how the queue should be populated, based on whether iterables or plain objects
        # (eventually mixed with iterables) were passed.
                
        # Check if only iterables were passed, in which case the queue will be populated 
        # asynchronously, immediately making using of Pipework's multithreaded design.
        if all(
            hasattr(arg, "__iter__") and not hasattr(arg, "__len__") 
            for arg in (*args[:1], *kwargs.values())
        ):
            
            # Predeclare variable to hold asynchronous function with which queue is populated.
            populate : Callable = None
            
            # Use a different asynchronous function, depending on the availability of kwargs.
            if len(kwargs) == 0:

                def populate():

                    for input in args[0]: # args[0] availability guaranted by initial argument check
                        push_object(input, enter_id, True)

            # Handle cases wherein kwargs are available.
            else: # if len(kwargs) > 0:
                    
                # Set-up asynchronous function.
                def populate():

                    # Predeclare variable to hold argument signature, which is deduced only once
                    # to optimize for performance.
                    signature : _ArgsAlias = None

                    # Iterate per 'row' over the data passed.
                    for data in itertools.zip_longest(*args[:1], *kwargs.values()):

                        # Generate argument as needed.
                        if not signature:

                            signature = (
                                Args[*[
                                    Param[type(d), k] 
                                    for d, k in zip(
                                        data, 
                                        (*("input" if len(args) > 0 else ()), *kwargs.keys())
                                    )
                                ]]
                            )

                        # Push row as new object.
                        push_object(Args(data, signature), enter_id, True)

            # Execute asynchronous populate function.
            populate_thread = threading.Thread(target = populate)
            populate_thread.start()

        # Plain objects
        else:

            # Directly push the argument on the queue if only an unnamed argument is available.
            if len(kwargs) == 0:
                push_object(args[0], enter_id, True)

            # Handle cases wherein kwargs are available.
            else: # if len(kwargs) > 0:

                push_object(

                    Args(

                        (*args[:1], *kwargs.values()),

                        Args[
                            *([Param[type(args[0]), "input"]] if len(args) > 0 else ()),
                            *[Param[type(v), k] for k, v in kwargs.items()]
                        ]

                    ),

                    enter_id, True
                )

            # Create mock object for populate_thread.
            populate_thread = collections.namedtuple("Thread", "is_alive")(lambda: False)


        # ##########################################################################################
        # Operate the pipeworks
        # ##########################################################################################

        # Set-up callback to handle errors #########################################################

        # Set-up stack to gather errors.
        error_stack : queue.Queue[__NodeError__] = queue.Queue()

        # Callback
        def get_error_callback(
            node_id : int, 
            args    : list[Any],
            kwargs  : dict[str, Any]
        ):
            
            """
            Generates callback that handles errors occuring in pipework.
            """
            
            def callback(error : BaseException):

                nonlocal error_stack
                error_stack.put(__NodeError__(self, node_id, error, args, kwargs))

            return callback

            # End of inner function 'get_error_callback' ###########################################


        # Set-up callback to handle forwarding in the pipework #####################################

        def get_callback(
            origin_id   : int, 
            connections : list[Connection] = [], 
            return_hints : _ArgsAlias | fArgs = None
        ):

            """
            Generates callback that forwards data within the pipework.
            """

            def callback(result):

                """
                Callback that forwards processed data to the appropriate next nodes.
                """

                # ##################################################################################
                # Access superceding function's variables
                # ##################################################################################

                nonlocal objects_queue
                nonlocal objects_len
                nonlocal objects_len_lock
                nonlocal counters

                # ##################################################################################
                # Argument handling
                # ##################################################################################

                # Skip None objects.
                if result is None:
                    result = iter([])

                # Wrap non-iterable result in iterable.
                elif hasattr(result, "__iter__") and not hasattr(result, "__len__"):
                    pass

                else:
                    result = iter([result])


                # ##################################################################################
                # Forward data
                # ##################################################################################

                # Infinite loop, processing each result item one by one.
                while True:

                    # Attempt to acquire the next item.
                    try:
                        obj = next(result)

                    # Break the loop if no more items are available.
                    except StopIteration:
                        break

                    # Handle errors.
                    except BaseException as error:

                        nonlocal error_stack
                        error_stack.put(__NodeError__(self, node_id, error, [], {}))

                        if (
                            self.ignore_errors is not None 
                            and isinstance(error, self.ignore_errors)
                        ):
                            continue

                        else:
                            return # Further error handling, handles release of objects.

                    # Apply return hints if any are available.
                    if return_hints is not None:

                        if isinstance(return_hints, _ArgsAlias):
                            obj = Args(obj, return_hints)

                        elif isinstance(return_hints, type) and issubclass(return_hints, fArgs):
                            obj = return_hints(*(obj if isinstance(obj, tuple) else (obj,)))

                    # Iterate over each possible node to which the object can be forwarded.
                    for conn in connections:

                        # Check if the output conforms with the conditions set.
                        if conn.where is not None:
                            
                            if isinstance(obj, Args):
                                
                                if conn.where(**obj.kwargs) is False:
                                    continue

                            elif isinstance(obj, fArgs):
                                
                                if conn.where(*obj.args, **obj.kwargs) is False:
                                    continue

                            elif conn.where(obj) is False:
                                continue

                        # Push object to the next connection.
                        push_object(obj, conn.receiver_name_id, conn.nocopy)

                        # Do not pass data to any further connections if the greedy flag has been 
                        # set.
                        if conn.greedy is True:
                            break

                # Release the object.
                release_object(origin_id)

                # End of nested function 'inner' ###################################################

            # Return callback
            return callback
        
            # End of inner function 'postprocess' ##################################################


        # Operate the framework ####################################################################

        # Pre-declare variable to hold eventual errors.
        error : __NodeError__ = None

        # Set-up a multi-thread pool.
        with multiprocessing.pool.ThreadPool(processes = self.processes) as pool:

            # Control ##############################################################################

            # Infinite loop with thread-safe condition checking within the loop.
            while True:

                # Break if an error has occured. 
                try:
                    # Attempt to retrieve error
                    error = error_stack.get_nowait()
                except:
                    pass
                
                if error is not None:

                    if (
                        self.ignore_errors is None 
                        or not isinstance(error.error, self.ignore_errors)
                    ):
                        break

                    else:
                        
                        self.logger.error(error.format_error_message())
                        self.logger.info("Ignoring error, continuing execution")

                        release_object(error.node_id)
                        error = None

                # Get exclusive access to counters
                with objects_len_lock:

                    # Keep running as long as not all data has been processed.
                    if objects_len > 0:
                        pass

                    # Keep running as long as data is being loaded.
                    elif populate_thread.is_alive():
                        pass

                    # Only break when all data has been processed.
                    else:
                        break


                # Object retrieval #################################################################
                
                # Attempt to retrieve next item from the queue.
                try:
                    item: __QueuedItem__ = objects_queue.get(timeout = 1 / 100)

                except:
                    continue # Retry

                # Retrieve object.
                node_id, obj_id = item.node_id, item.obj_id

                with object_handles_lock:
                    obj_handle = object_handles.get(obj_id, None)

                if obj_handle is None:

                    # Skip if no object handle could be retrieved.
                    release_object(node_id, obj_id)
                    continue

                obj : Any = obj_handle.obj


                # Handle exit ######################################################################

                # If the object has been forwarded to the exit, yield it.
                if node_id == exit_id:

                    # Release the object, and decrease the reference count for the object.
                    release_object(node_id, obj_id)
                            
                    # Yield result
                    yield obj if not isinstance(obj, (Args, fArgs)) else obj.kwargs

                    # Go to next iteration.
                    continue


                # Node object retrieval ############################################################

                # Get reference to the node the data has been forwarded to.
                node : Node = self.nodes_by_id.get(node_id, None)

                # Get callable that the node wraps.
                func = node.callable

                # Discard the data if the node forwarded to does not have any processing logic.
                if func is None:

                    # Give warning.
                    self.logger.warning(
                        f"Node with name '{self.names_by_id(node_id)} is not associated with any"
                        f" callable; skipping node;"
                    )

                    # Release the object.
                    release_object(node_id, obj_id)

                    # Continue to next object.
                    continue


                # Handle join behaviour ############################################################

                if node.join is True:

                    # Check if all data has reached the node #######################################

                    # Chech if any data is still being fed to the pipework.
                    if populate_thread.is_alive():

                        # Delay processing.
                        objects_queue.put(item)
                        continue

                    # Iterate over the counters of all preceeding nodes to see if any data is held 
                    # up in the pipework.
                    i = 0
                    for i in range(0, node_id + 1):

                        if i == node_id:
                            break

                        with counters[i].lock:

                            # Processing is delayed if there is but one object held up by any of the
                            # preceeding nodes. All data must pass the previous nodes before any
                            # join is carried out.
                            if counters[i].cnt > 0:
                                break

                    if i != node_id:
                        
                        # Delay processing.
                        objects_queue.put(item)
                        time.sleep(1 / 100) # Do not hog cycles

                        continue


                    # Join data ####################################################################

                    # Get number of objects to join.
                    num_objects = 0
                    with counters[node_id].lock:
                        num_objects = counters[node_id].cnt

                    # Set-up a list to join all data together.
                    objs = [obj]

                    # Iterate over the priority queue until all data has been joined.
                    while len(objs) < num_objects:

                        # Get identifiying information of next object in queue.
                        next_item : __QueuedItem__ = objects_queue.get()
                        next_node_id, next_obj_id = next_item.node_id, next_item.obj_id

                        # Check if the object is assigned to the same node. If not skip it.
                        if next_node_id != node_id:

                            objects_queue.put(next_item)
                            continue

                        # Get object associated with the next item.
                        with object_handles_lock:
                            next_obj_handle = object_handles.get(next_obj_id, None)
                            
                        next_obj : Any = next_obj_handle.obj

                        # Add object to the join list.
                        objs.append(next_obj)

                        # Adjust counters.
                        # Note: we do not do this for the object retrieved in the main loop as we
                        # wish to maintain at least one reference count for this node to represent
                        # the list with joined data.
                        release_object(node_id, next_obj_id)

                        # Release references.
                        next_node_id = None
                        next_obj = None
                        next_item = None

                    # Replace original object.
                    obj = objs

                    # Release references.
                    objs = None


                # Build args and kwargs arguments ##################################################
                    
                # Set-up empty args and kwargs, to be filled and passed to the node.
                args   : list[Any]                  = []
                kwargs : dict[str, list[Any] | Any] = dict()


                ### Handle data not joined #########################################################

                if not node.join:

                    # If an Args-object was passed, pass its inner kwargs to the node.
                    if isinstance(obj, (Args, fArgs)):
                        args = obj.args
                        kwargs = obj.kwargs

                    # Otherwise, append the object to the args list.
                    else:
                        args.append(obj)


                ### Handle joined data #############################################################

                else:

                    # Iterate over the list of objects produced by the the join operation.
                    for i, _obj in enumerate(obj):

                        # Handle Args objects.
                        if isinstance(_obj, (Args, fArgs)):

                            # Iterate over all possible named arguments, old and new.
                            for key in (set(_obj.kwargs.keys()) | set(kwargs.keys())):

                                (
                                    # Retrieve for the named argument a list, or create one. Each of
                                    # this list entries represents a processed object. A None-value
                                    # is assigned when the given object does not specify a value for
                                    # the given argument.
                                    kwargs.setdefault(key, [None] * i)
                                    # Append data.
                                    .append(_obj.kwargs.get(key, None))
                                )

                            # Ensure the args list matches the depth of the kwargs' lists.
                            args.append(None)

                        # Handle non-Args objects.
                        else:

                            # Append the object to the args list.
                            args.append(_obj)

                            # Ensure the kwargs' lists match the depth of the args list.
                            for key in kwargs.keys():
                                kwargs[key].append(None)


                    # See if any non-named arguments were passed, otherwise set args to None.
                    if flatten(args) is None:
                        args = None

                    ### Handle groupby #############################################################

                    if node.join_groupby is not None:

                        # Get indices that share same values for attributes specified by groupby.
                        groupings : dict[Any, list[int]] = {
                            # Index by values of attributes specified by groupby.
                            keys: (
                                # Extract from the itertools groupby the **indices**.
                                [keys_and_values[0] for keys_and_values in grouping]
                            )
                            # Aggregate by values of attributes specified by groupby.
                            for keys, grouping in
                            itertools.groupby(

                                # Sort by values of attributes specified by groupby.
                                sorted(

                                    # Assign identifier to each row.
                                    enumerate(
                                        # Transpose data structure: from columns to rows.
                                        zip(
                                            # Retrieve values for each attributes specified by
                                            # groupby.
                                            *[kwargs.get(key, []) for key in node.join_groupby]
                                        )
                                    ),

                                    # Exclude identifier from comparison.
                                    key = operator.itemgetter(1)
                                ),

                                # Exclude identifier from comparison.
                                key = operator.itemgetter(1)
                            )
                        }

                        # Transform args if needed.
                        if args is not None:

                            args = [
                                # Create lists of lists. The outer list is indexed in correspondence
                                # with the grouping keys. The inner lists represents all inputs 
                                # whereby the payload for the grouping keys was equal.
                                [
                                    (
                                        list(operator.itemgetter(*indices)(args))
                                    ) if len(indices) > 1 else (
                                        [args[indices[0]]]
                                    )
                                    for indices in groupings.values()
                                ]
                            ]

                        # Transform kwargs.
                        kwargs = {
                            # Index by the same keys as the original kwargs argument.
                            key: (
                                # Group values using indices in groupings, applying different logic for
                                # grouping and non-grouping keys.
                                (
                                    # For grouping keys, use the values already included in groupings.
                                    [v[i] for v in groupings.keys()]
                                ) if i is not None else (
                                    # For non-grouping keys, generate a list of lists. The outer list is
                                    # indexed in correspondence with the grouping keys. The inner lists
                                    # represents all inputs for the given parameter whereby the payload
                                    # for the grouping keys was equal.
                                    [
                                        (
                                            list(operator.itemgetter(*indices)(kwargs.get(key)))
                                        ) if len(indices) > 1 else (
                                            [kwargs.get(key)[indices[0]]]
                                        )
                                        for indices in groupings.values()
                                    ]
                                )
                            )
                            # Iterate over each of the keys in the original kwargs argument.
                            for key in kwargs.keys()
                            # Check if the key is included in the grouping. If so, retrieve its 
                            # priority.
                            for i in (
                                next(
                                    (i for i, _key in enumerate(node.join_groupby) if _key == key), 
                                    None
                                ), 
                            )
                        }

                        # Release reference for groupings.
                        groupings = None


                    ### Handle flattening ##########################################################

                    if node.join_flatten is True:

                        ### Where no groupings have been applied ###################################

                        if node.join_groupby is None:

                            # Flatten args.
                            args = flatten(args) if args is not None else None

                            # Flatten kwargs.
                            for key, values in kwargs.items():
                                kwargs[key] = flatten(values)


                        # Where groupings have been applied ########################################

                        else: # if node.join_groupby is not None:

                            # Flatten args.
                            args = [flatten(_args) for _args in args] if args is not None else None

                            # Flatten kwargs.
                            for key, ls in kwargs.items():
                                
                                if key in node.join_groupby:
                                    continue
                                
                                kwargs[key] = flatten(ls)


                    # Wrap args so that the user does not have to unwrap them (so no *args required)
                    args = [args] if args is not None else []


                ### Add eventual self-reference ####################################################

                if node.pass_self_as is not None:
                    kwargs[node.pass_self_as] = node
                    

                # Pass to node #####################################################################

                # Already remove the object from the stack if no other nodes reference it.
                with object_handles_lock and obj_handle.refs_lock:

                    # Update reference count.
                    obj_handle.refs -= 1

                    # Delete the object if it is no longer referenced by any objects.
                    if obj_handle.refs <= 0:
                        del object_handles[obj_id]

                # Process the data via the node.
                pool.apply_async(
                    func, args, kwargs, 

                    callback = (
                        get_callback(
                            origin_id    = node_id, 
                            connections  = self.connections_by_id.get(node_id, []),
                            return_hints = (
                                node.returns 
                                if (
                                    node.returns is not None
                                    and (
                                        isinstance(node.returns, _ArgsAlias) 
                                        or (
                                            isinstance(node.returns, type) 
                                            and issubclass(node.returns, fArgs)
                                        )
                                    )
                                )
                                else None
                            )
                        )
                    ), 

                    error_callback = (
                        get_error_callback(
                            node_id = node_id,
                            args    = args,
                            kwargs  = kwargs
                        )
                    )
                )
            

        # ##########################################################################################
        # Clean up
        # ##########################################################################################

        # Error handling ###########################################################################

        if error is not None: 
            
            raise (error.error) from RuntimeError(
                "An error occurred in a Node\n" + error.format_error_message()
            )
        
        # End of __call__ ##########################################################################


    # ##############################################################################################
    # Decorators
    # ##############################################################################################

    # connect ######################################################################################

    @staticmethod
    def connect(
        input : str = None, 
        output : str = None, 
        where : Callable[[Any], bool] = None, 
        greedy : bool = False
    ):

        """
        Decorator to assign the method of a Pipework-subclass as a node.

        Parameters
        ----------

        input
            The node from which this node receives it input. Can only be defined if `output` has not
            been defined. Either `input` or `output` must be defined.

        output
            The node to which this node forwards its input. Can only be defined if `input` has not
            been defined. Either `input` or `output` must be defined.

        where
            A function that evaluates the input received, returning a boolean that states whether or
            not this input should be forwarded to the next node. For example::

                @Pipework.connect(output = "process_str", where = lambda self, x: isinstance(x, str))
                @Pipework.connect(output = "process_num", where = lambda self, x: isinstance(x, numbers.Number))
                def example(self, _):
                
                    yield 123              # Processed by 'process_num'
                    yield "a"              # Processed by 'process_str'
                    yield datetime.now()   # Not processed
            
            Stating conditions using the `where`-argument has as benefit that data is not
            unnecessarily duplicated. Everytime data is forwarded in a Pipework, that data is copied
            as to ensure that different nodes, potentially operating in different threads do not 
            modify the same data. The condition stated by `where` is checked before doing so, 
            preventing duplication and reducing memory usage.

        greedy
            Determines whether data is only forwarded using this connection when able (i.e. when the 
            conditions stated by `where` are met), or whether data is also forwarded via any 
            subsequent connections attached to the sender.

            Please note that greedy behaviour is affected by the order by which connections are
            declared. For example::

                @Pipework.connect(output = "step3")
                @Pipework.connect(output = "step2", where = lambda self, x: x < 3, greedy = True)
                @Pipework.connect(output = "step1")
                def step0(self, input):
                
                    for i in range(0, 5):
                        yield i

            In the above example the numbers 1, 2, 3, 4 will all be forwarded to `step1`, whereas
            `step3` will only receive the numbers 3 and 4, with the preceding numbers, 1 and 2,
            being processed by `step2`.
        """

        # ##########################################################################################
        # Argument handling
        # ##########################################################################################

        # input, output
        if (input is None) and (output is None):

            raise TypeError(
                "'connect' expected an argument for either 'input' or 'output', got None;"
            )

        if (input is not None) and (output is not None):

            raise TypeError(
                "'connect' expected an argument for either 'input' or 'output', got an argument for"
                " both;"
            )

        # where, greedy
        if (where is None) and (greedy == True):

            warnings.warn(
                "A greedy connection was defined, but no conditions were stated; data will not be"
                " propogated through any subsequent connections involving this node;"
            )

        
        # ##########################################################################################
        # Delegation
        # ##########################################################################################

        def decorator(func : Callable[[type["Pipework"], Any], Any]):

            # Get function context #################################################################

            # Get class' and method's qualified name.
            cls, method = (
                lambda x: (next(x, None), next(x, None))
            )(iter(func.__qualname__.split(".")))

            # Check if names were succesfully retrieved.
            if not cls or not method:

                raise TypeError(
                    "Class' and method's qualified name could not be retrieved; decorator was"
                    " likely applied to a function instead of a method;"
                )
            
            # Determine the sending and receiving node #############################################

            sender, receiver = None, None

            if input is not None:

                sender = input
                receiver = method

            else: # if output is not None:

                sender = method
                receiver = output
                
            # Add connection to global routing map #################################################
            (
                Pipework
                .__connections__
                .setdefault(f"{func.__module__}.{cls}", [])
                .append(
                    Connection(
                        input = sender,
                        output = receiver,

                        where = where,
                        greedy = greedy
                    )
                )
            )

            # Return the function unchanged ########################################################

            return func

        return decorator
    
        # End of decorator 'connect' ###############################################################
    

    # join #########################################################################################
    
    @staticmethod
    def join(
        groupby : list[str] = None, 
        flatten : bool = False
    ):

        """
        Set-up node to join all received data together before processing it. For example::

            def step0(self, _):
            
                yield 1
                yield 2
                yield 3

            @Pipework.join
            @Pipework.connect(input = "step0")
            def step1(self, inputs):
            
                return sum(inputs) # Result: 6

        Without the `join` decorator `step1` would process each input generated by `step0` 
        separately, each attempt resulting in an error as the sum function cannot iterate over an 
        integer. With the `join` decorator, the inputs from `step0` are grouped in a list before
        being passed to `step1`, where the preceeding inputs are collectively processed, with a
        sum being run over the list.

        Parameters
        ----------

        groupby
            Parameters by which to group the inputs for the other parameters. By default a join 
            loads each parameter with a list consisting of one entry for each input received. These
            lists are indexed by the order in which the inputs were processed. Accordingly, for any 
            sending node, all the data sent by that node may be found by accessing the arguments at 
            the same index. By stating a `groupby`, a different logic is applied. Firstly, the 
            parameters included in the `groupby` are deduplicated, so that each combination of the 
            given arguments is unique. Secondly, the parameters **not** included in the `groupby` 
            are loaded as lists of lists. Their outer lists' indices corresponds with the indices of
            the parameters included in the `groupby`. Their inner lists' meanwhile represent an 
            aggregation of all the inputs sharing the same values for the parameters included in the 
            `groupby`. Consider the following example::

                @Pipework.connect(input = "enter")
                def gen(self, _):
                    yield from (random.randint(1, 100) for _ in range(0, 100))

                @Pipework.connect(input = "gen")
                def pow(self, x) -> Args[Param[int, "x"], Param[int, "y"]]:
                    return (x, x ** 2)

                @Pipework.connect(input = "pow")
                @Pipework.connect(input = "exit")
                @Pipework.join(groupby = ["x"]):
                def final(self, x : list[int], y : list[list[int]]):
                    return zip(x, next(z for ls in y for z in ls if z, None))

        flatten
            Flag that indicates whether any grouped input should be flattened or not. When input is
            flattened, a singular value is chosen for each non-grouping parameter. Accordingly, the
            example for `groupby` could also have been inplemented as follows::

                @Pipework.connect(input = "enter")
                def gen(self, _):
                    yield from (random.randint(1, 100) for _ in range(0, 100))

                @Pipework.connect(input = "gen")
                def pow(self, x) -> Args[Param[int, "x"], Param[int, "y"]]:
                    return x ** 2

                @Pipework.connect(input = "pow")
                @Pipework.connect(input = "exit")
                @Pipework.join(groupby = ["x"], flatten = True):
                def final(self, x : list[int], y : list[int]):
                    return zip(x, y)
        
        Notes
        -----

        * Joins are only carried out when all data in the pipeline has reached or passed the node 
          set-up to join data. If any data is still being processed by any previous nodes, 
          processing by this node is delayed. This also includes data fed to the `enter` node, 
          meaning if data is streamed into the pipework, joins are delayed until all data had been 
          put into the pipework. Due to this joining is *incompatible* with infinite generators.

        """

        # ##########################################################################################
        # Argument handling
        # ##########################################################################################

        # groupby ##################################################################################

        if groupby is not None:

            # Check if a list was passed.
            if not isinstance(groupby, list):

                raise TypeError(
                    f"Object of type '{type(groupby)}' was passed for 'groupby' where list of"
                    f" strings was expected instead;"
                )

            # Check if the list consists of strings.
            for i, obj in enumerate(groupby):

                if not isinstance(obj, str):

                    raise TypeError(
                        f"Object of type '{type(obj)}' was passed for 'groupby' at index '{i}' of"
                        f" given list; an object of type 'str' was expected instead;"
                    )
            
            
        # flatten ##################################################################################

        if flatten is not None:

            # Check if a boolean was passed.
            if not (flatten == True or flatten == False):

                raise TypeError(
                    f"Object of type '{type(flatten)}' was passed for 'flatten' where boolean was"
                    f" expected instead;"
                )


        # ##########################################################################################
        # Delegation
        # ##########################################################################################

        def decorator(func : Callable[[type["Pipework"], Any], Any]):

            # Annotate the given function.
            func.join = True
            func.join_groupby = groupby
            func.join_flatten = flatten

            # Return annotated function

        return decorator
    
        # End of decorator 'join' ##################################################################
    

    # mixin ########################################################################################

    @staticmethod
    def mixin(node : Node):

        """
        Replaces the decorated method with the given :py:class:`Node`, allowing to mix in 
        runtime-defined nodes in class-defined pipeworks::

            sqrt = Node(
                lambda x: math.sqrt(x)
            )

            class Example(Pipework):
            
                @Pipework.connect(input = "enter")
                def pow(self, x : int)
                    return x ** 2

                @Pipework.connect(input = "mul")
                @Pipework.connect(output = "exit")
                @Pipework.mixin(sqrt)
                def sqrt(): 
                    pass

        """

        # ##########################################################################################
        # Argument handling
        # ##########################################################################################

        # node #####################################################################################

        # Type check
        if not isinstance(node, Node):

            raise TypeError(
                f"Object of type '{type(node)}' was passed where object of type 'Node' was"
                f" expected;"
            )
        
        # Check if the given node has not already been mixed in.
        if hasattr(node, "__mixed_in__"):

            raise RuntimeError(
                "Given node has already been mixed in elsewhere; perhaps you are reusing an"
                " instance?"
            )
        
        # Assign flag to signify that the given node has been mixed.
        node.__mixed_in__ = True


        # ##########################################################################################
        # Delegation
        # ##########################################################################################

        def decorator(func : Callable[[type["Pipework"], Any], Any]):

            # Copy original function's attributes to given node.
            functools.update_wrapper(
                node, func, assigned = ("__module__", "__name__", "__qualname__", "__doc__")
            )

            # Return node as replacement for the original function.
            return node
        
        return decorator
    
        # End of decorator 'mixin' #################################################################


# End of File ######################################################################################