from ufl import as_vector, cos, dot, max_value, min_value, sin

from .helpers import ufl_clamp, ufl_cross, ufl_length, ufl_sign
from .primitive_base import ORIGIN, SDF


class Pie(SDF):
    def __init__(self, radius, angle, *args, **kwargs):
        self.radius = radius
        self.angle = angle  # angle of cicle (not opening)

        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"Pie({self.radius}, {self.angle}, {self._repr_core()})"

    def sdf(self, x):
        # Note: Ignores z
        x0_abs = abs(x[0])
        coords = as_vector([x0_abs, x[1]])

        circle_dist = ufl_length(coords) - self.radius

        trig = as_vector([sin(self.angle / 2), cos(self.angle / 2)])

        # projection of coords on to trig, clamped to within circle
        proj = ufl_clamp(dot(coords, trig), 0, self.radius) * trig
        rejc = coords - proj
        edge_dist = ufl_length(rejc) * ufl_sign(ufl_cross(coords, trig))

        return max_value(circle_dist, edge_dist)
