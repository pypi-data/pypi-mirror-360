# Pypeworks

Pypeworks is an open-source framework for implementing parallelized dataflows in Python. 


## Install

Pypeworks is available through the PyPI repository and can be installed using `pip`:

```bash
pip install pypeworks
```

## Quick start

Pypeworks' central concept is that of the `Pipework`. A pipework may be defined as a directed
acylic graph, wherein each `Node` serves as a processing unit, taking in data, transforming it, and 
forwarding it to the next node, until the exit node is reached.

Pypeworks offers two ways to set-up a `Pipework`. A pipework may be instantiated and constructed on
the fly:

```python
from pypeworks import (
    Pipework, 
    Node,
    Connection
)

pipework = (

   Pipework(

      min = Node(
         lambda xs: ("min", min(xs))
      ),

      mean = Node(
         lambda xs: ("mean", sum(xs) / len(xs))
      ),

      max = Node(
         lambda xs: ("max", max(xs))
      ),

      connections = [
         Connection( "enter" , "min"  ),
         Connection( "enter" , "mean" ),
         Connection( "enter" , "max"  ),
         Connection( "min"   , "exit" ),
         Connection( "mean"  , "exit" ),
         Connection( "max"   , "exit" )
      ]

   )

)

print(
   dict(
      pipework([1, 2, 3, 4, 5, 6, 7, 8])
   )
) # {'max': 8, 'mean': 4.5, 'min': 1}
```

Alternatively, a pipework may be implemented as a templatable, reusable class:

```python
from pypeworks import (
   Pipework
)

class Pipework(Pipework):

   @Pipework.connect(input = "enter")
   @Pipework.connect(output = "exit")
   def min(self, xs : list[int]):
      return ("min", min(xs))

   @Pipework.connect(input = "enter")
   @Pipework.connect(output = "exit")
   def mean(self, xs : list[int]):
      return ("mean", sum(xs) / len(xs))

   @Pipework.connect(input = "enter")
   @Pipework.connect(output = "exit")
   def max(self, xs : list[int]):
      return ("max", max(xs))

print(
   dict(
      Pipework()([1, 2, 3, 4, 5, 6, 7, 8])
   )
) # {'max': 8, 'mean': 4.5, 'min': 1}
```

