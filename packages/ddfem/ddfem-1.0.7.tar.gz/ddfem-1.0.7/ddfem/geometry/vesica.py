from ufl import as_vector, conditional, sqrt

from .helpers import ufl_length, ufl_sign
from .primitive_base import ORIGIN, SDF


class Vesica(SDF):
    def __init__(self, radius, distance, smooth_radius, *args, **kwargs):
        """Generates sign distance function and domain coordinates for a Vesica.
        i.e. Union of two circles.
        Centred at (0,0)

        Args:
            radius (float,): Radius of each circle.
            distance (float): Distance of circle center from y-axis.
            smooth_radius (float): Smoothing of domain,so no sharp corner when circles connection.
        """
        assert distance != 0, "This is a circle, use Ball class"
        assert distance < radius, "No shape exists, circles cancel each other out"
        assert (
            smooth_radius * distance < 0
        ), "For a smooth edge, smooth_radius needs to be opposite sign of distance"

        self.radius = radius
        self.distance = distance
        self.smooth_radius = smooth_radius

        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"Vesica({self.radius}, {self.distance}, {self.smooth_radius}, {self._repr_core()})"

    def sdf(self, x):
        # Note: Ignores z
        x0_abs = abs(x[0])
        x1_abs = abs(x[1])

        b = sqrt((self.radius + self.smooth_radius) ** 2 - self.distance**2)

        circle_coords = as_vector([x0_abs + self.distance, x[1]])

        return (
            conditional(
                (x1_abs - b) * self.distance > x0_abs * b,
                ufl_length(as_vector([x0_abs, x1_abs - b])) * ufl_sign(self.distance),
                ufl_length(circle_coords) - self.radius - self.smooth_radius,
            )
            + self.smooth_radius
        )
