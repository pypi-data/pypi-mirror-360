"""Module with stereo matching interfaces."""

from typing import Callable

from mynd.image import Image
from mynd.utils.containers import Pair


StereoMatcher = Callable[[Image, Image], Pair[Image]]
