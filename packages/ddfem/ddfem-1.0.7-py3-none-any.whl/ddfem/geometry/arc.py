from ufl import as_vector, conditional, cos, sin

from .helpers import ufl_length
from .primitive_base import ORIGIN, SDF


class Arc(SDF):
    """SDF for an arc:

    Provides the signed distance function for an arc given the
    radius, angle of opening, the width, and the center (which defaults to the origin).
    """

    def __init__(self, radius, angle, width, center=ORIGIN, *args, **kwargs):
        self.radius = radius
        self.angle = angle  # angle of opening
        self.width = width

        if isinstance(center, (list, tuple)):
            center = as_vector(center)
        self.center = center

        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"Arc({self.radius}, {self.angle}, {self.width}, {self.center}, {self._repr_core()})"

    def sdf(self, x):
        # Note: Ignores z
        y0_abs = abs(x[1])
        coords = as_vector([x[0], y0_abs])

        center_radius = self.radius - self.width / 2

        distance = ufl_length(coords) - center_radius

        edge_point = center_radius * as_vector([cos(self.angle), sin(self.angle)])

        left_coords = coords - edge_point

        sign_dist = conditional(
            (sin(self.angle) * x[0]) > (cos(self.angle) * y0_abs),
            ufl_length(left_coords),
            abs(distance),
        )

        sign_dist -= self.width / 2
        return sign_dist
