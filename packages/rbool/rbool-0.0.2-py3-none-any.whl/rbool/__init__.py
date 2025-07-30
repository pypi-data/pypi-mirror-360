"""
Init file that includes the most used classes and functions of the module
"""

from .base import EmptyR1, Future, SubSetR1, WholeR1
from .bool1d import contains, extract_knots, intersect, invert, unite
from .converter import from_any
from .limits import infimum, maximum, minimum, supremum
from .singles import DisjointR1, IntervalR1, SingleValueR1, bigger, lower
from .transform import move, scale

Future.convert = from_any
Future.unite = unite
Future.intersect = intersect
Future.invert = invert
Future.contains = contains
Future.scale = scale
Future.move = move

__version__ = "0.0.2"
