from dune.ufl import Constant
from ufl import as_vector, div, exp, grad, inner, sqrt

from ddfem.boundary import BndFlux_v, BndValue


def fhModel(inverted):
    class Model:
        dimRange = 1
        outFactor_i = Constant(1, "outFactor")

        def initial(x):
            return 1 / 2 * (x[0] ** 2 + x[1] ** 2) - 1 / 3 * (x[0] ** 3 - x[1] ** 3) + 1

        def exact(t, x):
            return as_vector([exp(-2 * t) * (Model.initial(x) - 1) + 1])

        def K(U, DU):
            # DU = exp(-2 * t) * (x[0] - x[0]^2, x[1] + x[1]^2)
            return 2 / (1 + sqrt(1 + 4 * sqrt(inner(DU, DU))))

        def F_v(t, x, U, DU):
            return Model.K(U, DU) * DU

        def S_i(t, x, U, DU):
            return -div(
                Model.F_v(t, x, Model.exact(t, x), grad(Model.exact(t, x)))
            ) + as_vector([-2 * exp(-2 * t) * (Model.initial(x) - 1)])

        valD = BndValue(lambda t, x, U: Model.exact(t, x))

        valN = BndFlux_v(
            lambda t, x, U, DU, n: Model.F_v(
                t, x, Model.exact(t, x), grad(Model.exact(t, x))
            )
            * n
        )

        boundary = {
            "sides": valD,
            "ends": valN,
        }

        if inverted:
            for i in range(1, 5):
                boundary[i] = valD

    return Model
