from ufl import as_vector

from .helpers import ufl_length
from .primitive_base import ORIGIN, SDF


class Ball(SDF):
    def __init__(self, radius, center=ORIGIN, *args, **kwargs):
        self.radius = radius

        if isinstance(center, (list, tuple)):
            center = as_vector(center)
        self.center = center

        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"Ball({self.radius}, {self.center}, {self._repr_core()})"

    def sdf(self, x):
        # Note ignore z, if center 2d
        xx = as_vector([x[i] for i in range(len(self.center))])
        center_x = xx - self.center
        return ufl_length(center_x) - self.radius
