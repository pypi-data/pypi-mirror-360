from ufl import (
    as_matrix,
    as_vector,
    conditional,
    cos,
    grad,
    max_value,
    min_value,
    pi,
    sin,
    tanh,
)

from .helpers import smax_value, smin_value, ufl_length

ORIGIN = as_vector([0, 0])


class SDF:
    def __init__(self, epsilon=None, name=None, children=None):
        self._epsilon = epsilon
        self.child_sdf = children if children else []

        self.name = name
        if self.name is None:
            self.name = repr(self)

    @property
    def epsilon(self):
        return self._epsilon

    @epsilon.setter
    def epsilon(self, eps):
        self._epsilon = eps
        for child in self.child_sdf:
            child.epsilon = eps

    def _repr_core(self):
        return f"epsilon={self.epsilon}, name={self.name}, children={self.child_sdf}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self._repr_core()})"

    def sdf(self, x):
        raise NotImplementedError

    def __call__(self, x):
        return self.sdf(x)

    def search(self, child_name):
        if self.name == child_name:
            return self

        queue = self.child_sdf.copy()

        while queue:
            current_child = queue.pop(0)

            if current_child.name == child_name:
                return current_child

            for child in current_child.child_sdf:
                queue.append(child)

        return None

    def phi(self, x, epsilon=None):
        if not epsilon:
            epsilon = self.epsilon
            assert self.epsilon, "Must define epsilon"
        return 0.5 * (1 - tanh((3 * self.sdf(x) / epsilon)))

    def chi(self, x):
        return conditional(self.sdf(x) <= 0, 1, 0)

    def projection(self, x):
        return -grad(self.sdf(x)) * self.sdf(x)

    def boundary_projection(self, x):
        return x + self.projection(x)

    def external_projection(self, x):
        # return self.chi(x) * x + self.boundary_projection(x) * (1 - self.chi(x))
        return x + self.projection(x) * (1 - self.chi(x))

    def union(self, other):
        return Union(self, other)

    def subtraction(self, other):
        return Subtraction(self, other)

    def intersection(self, other):
        return Intersection(self, other)

    def xor(self, other):
        return Xor(self, other)

    def scale(self, sc):
        return Scale(self, sc)

    def invert(self):
        return Invert(self)

    def rotate(self, angle, radians=True):
        return Rotate(self, angle, radians)

    def translate(self, vector):
        return Translate(self, vector)

    def round(self, sc):
        return Round(self, sc)

    def extrude(self, length, split_ends=False):
        if split_ends:
            from .plane import Plane

            ext = Extrusion(self, length * 2, name=f"{self.name}_ext")
            ext = Translate(ext, [0, 0, -length / 2], name=f"{self.name}_sides")
            bot = Plane([0, 0, -1], 0, name=f"{self.name}_bot")
            top = Plane([0, 0, 1], -length, name=f"{self.name}_top")
            z_interval = bot & top
            ext = ext & z_interval
        else:
            return Extrusion(self, length, name=f"{self.name}_ext")
        return ext

    def revolve(self, offset=0, axis="x"):
        return Revolution(self, offset, axis)

    def __or__(self, other):
        return self.union(other)

    def __and__(self, other):
        return self.intersection(other)

    def __sub__(self, other):
        return self.subtraction(other)

    def __xor__(self, other):
        return self.xor(other)

    def __mul__(self, other):
        return self.scale(other)

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return self.scale(other)
        raise TypeError(f"Cannot multiply a SDF with {type(other)}")

    # possibly use a 'Constant' but then multiple changes will influence previous usage?
    smoothing = None

    def max_value(a, b):
        if SDF.smoothing is None:
            return max_value(a, b)
        else:
            return smax_value(a, b, SDF.smoothing)

    def min_value(a, b):
        if SDF.smoothing is None:
            return min_value(a, b)
        else:
            return smin_value(a, b, SDF.smoothing)


class BaseOperator(SDF):
    def __init__(self, children, epsilon=None, *args, **kwargs):

        if not epsilon and all(child.epsilon for child in children):
            epsilon = children[0].epsilon
            for child in children:
                epsilon = max_value(epsilon, child.epsilon)

        super().__init__(children=children, epsilon=epsilon, *args, **kwargs)

    def __getitem__(self, key):
        return self.child_sdf[key]


class Union(BaseOperator):
    """Union of two SDFs (OR) - not perfect(negative)"""

    def __init__(self, sdf1, sdf2, *args, **kwargs):
        super().__init__(children=[sdf1, sdf2], *args, **kwargs)

    def sdf(self, x):
        return SDF.min_value(self.child_sdf[0].sdf(x), self.child_sdf[1].sdf(x))


class Subtraction(BaseOperator):
    """Subtraction of two SDFs (difference) - not perfect"""

    def __init__(self, sdf1, sdf2, *args, **kwargs):
        super().__init__(children=[sdf1, sdf2], *args, **kwargs)

    def sdf(self, x):
        return SDF.max_value(self.child_sdf[0].sdf(x), -self.child_sdf[1].sdf(x))


class Intersection(BaseOperator):
    """Intersection of two SDFs (AND) - not perfect"""

    def __init__(self, sdf1, sdf2, *args, **kwargs):
        super().__init__(children=[sdf1, sdf2], *args, **kwargs)

    def sdf(self, x):
        return SDF.max_value(self.child_sdf[0].sdf(x), self.child_sdf[1].sdf(x))


class Xor(BaseOperator):
    """Xor of two SDFs (AND) - perfect"""

    def __init__(self, sdf1, sdf2, *args, **kwargs):
        super().__init__(children=[sdf1, sdf2], *args, **kwargs)

    def sdf(self, x):
        a_x = self.child_sdf[0].sdf(x)
        b_x = self.child_sdf[1].sdf(x)
        return SDF.max_value(SDF.min_value(a_x, b_x), -SDF.max_value(a_x, b_x))


class Invert(BaseOperator):
    """Inverts SDF"""

    def __init__(self, sdf1, *args, **kwargs):
        super().__init__(children=[sdf1], *args, **kwargs)

    def sdf(self, x):
        return -self.child_sdf[0].sdf(x)


class Scale(BaseOperator):
    """Scales SDF"""

    def __init__(self, sdf1, scale, *args, **kwargs):
        if not isinstance(scale, (int, float)):
            raise TypeError(f"Cannot scale a SDF with {type(scale)}")
        elif not scale > 0:
            raise ValueError("Cannot scale a SDF with nonpositive")
        else:
            self.scale = scale

        super().__init__(children=[sdf1], *args, **kwargs)

    def sdf(self, x):
        return self.child_sdf[0].sdf(x / self.scale) * self.scale

    def __repr__(self):
        return f"Scale({self.scale}, {self._repr_core()})"


class Rotate(BaseOperator):
    """Rotates SDF, counterclockwise of orgin"""

    def __init__(self, sdf1, angle, radians=True, *args, **kwargs):
        if not radians:
            angle *= pi / 180
        self.angle = angle

        super().__init__(children=[sdf1], *args, **kwargs)

    def sdf(self, x):
        c = cos(self.angle)
        s = sin(self.angle)

        r = as_matrix(((c, -s), (s, c)))
        return self.child_sdf[0].sdf(r.T * x)

    def __repr__(self):
        return f"Rotate({self.angle}, {self._repr_core()})"


class Translate(BaseOperator):
    """Translates SDF"""

    def __init__(self, sdf1, vec, *args, **kwargs):
        if isinstance(vec, (list, tuple)):
            vec = as_vector(vec)
        self.vec = vec

        super().__init__(children=[sdf1], *args, **kwargs)

    def sdf(self, x):
        return self.child_sdf[0].sdf(x - self.vec)

    def __repr__(self):
        return f"Translate({self.vec}, {self._repr_core()})"


class Round(BaseOperator):
    """Rounds SDF"""

    def __init__(self, sdf1, scale, *args, **kwargs):
        assert scale > 0
        self._scale = scale  # careful not to overwrite SDF.scale here

        super().__init__(children=[sdf1], *args, **kwargs)

    def sdf(self, x):
        return self.child_sdf[0].sdf(x) - self._scale

    def __repr__(self):
        return f"Round({self._scale}, {self._repr_core()})"


class Extrusion(BaseOperator):
    """Extrude SDF"""

    def __init__(self, sdf1, extrude_length, *args, **kwargs):
        self.extrude_length = extrude_length

        super().__init__(children=[sdf1], *args, **kwargs)

    def sdf(self, x):
        d = self.child_sdf[0].sdf(as_vector([x[0], x[1]]))
        w = abs(x[2]) - self.extrude_length
        return SDF.min_value(SDF.max_value(d, w), 0) + ufl_length(
            as_vector([SDF.max_value(d, 0), SDF.max_value(w, 0)])
        )

    def __repr__(self):
        return f"Extrusion({self.extrude_length}, {self._repr_core()})"


class Revolution(BaseOperator):
    """Revolve SDF"""

    def __init__(self, sdf1, offset, axis, *args, **kwargs):
        self.offset = offset
        assert axis in ["x", "y"], "Can only revolve around the x or y axis"
        self.axis = axis

        super().__init__(children=[sdf1], *args, **kwargs)

    def sdf(self, x):
        if self.axis == "x":
            q = as_vector([x[0], ufl_length(as_vector([x[1], x[2]])) - self.offset])
        elif self.axis == "y":
            q = as_vector([ufl_length(as_vector([x[0], x[2]])) - self.offset, x[1]])
        return self.child_sdf[0].sdf(q)

    def __repr__(self):
        return f"Revolution({self.offset}, {self._repr_core()})"
