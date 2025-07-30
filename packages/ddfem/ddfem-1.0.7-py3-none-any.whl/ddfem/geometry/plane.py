from ufl import as_vector, dot

from .primitive_base import SDF


class Plane(SDF):
    def __init__(self, normal, offset, *args, **kwargs):
        if isinstance(normal, (list, tuple)):
            normal = as_vector(normal)
        self.normal = normal

        self.offset = offset

        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f"Plane({self.normal}, {self.offset}, {self._repr_core()})"

    def sdf(self, x):
        return dot(x, self.normal) + self.offset
