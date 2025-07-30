from ufl import as_vector, conditional, max_value, min_value

from .helpers import ufl_length
from .primitive_base import ORIGIN, SDF


class Box(SDF):
    def __init__(self, width, height, center=ORIGIN, *args, **kwargs):
        self.width = width
        self.height = height

        if isinstance(center, (list, tuple)):
            center = as_vector(center)
        self.center = center

        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"Box({self.width}, {self.height}, {self.center}, {self._repr_core()})"

    def sdf(self, x):
        # Note: Ignores z
        # shift x
        center_x = x - self.center
        # aux functions
        w0 = abs(center_x[0]) - self.width / 2
        w1 = abs(center_x[1]) - self.height / 2

        g = max_value(w0, w1)

        q = as_vector([max_value(w0, 0), max_value(w1, 0)])

        return conditional(g > 0, ufl_length(q), g)
