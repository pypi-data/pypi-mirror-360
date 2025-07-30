from dune.ufl import Constant
from ufl import as_vector, conditional, div, dot, grad, outer, sqrt

from ddfem.boundary import BndFlux_c, BndFlux_v, BndValue


def adModel(exact, D, withVelocity, inverted):
    class Model:
        solution = exact
        dimRange = 1
        diffFactor = Constant(D)

        # this should probably be a vector of dimRange and then used by
        # componentwise multiplication with (u-g):
        outFactor_i = diffFactor

        if withVelocity:

            outFactor_e = 1

        def diff(t, x):
            return Model.diffFactor * (1 - 0.5 * dot(x, x))

        def F_v(t, x, U, DU):
            return Model.diff(t, x) * DU

        if withVelocity:

            def b(t, x):
                return Constant([0.9, 0.5]) + 3 * as_vector([x[1], -x[0]])

            def F_c(t, x, U):
                return outer(U, Model.b(t, x))

        if exact:

            def S_i(t, x, U, DU):
                return -div(Model.F_v(t, x, exact(t, x), grad(exact(t, x)))) + (
                    exact(t, x) - U
                )

        if exact and withVelocity:

            def S_e(t, x, U, DU):
                return div(Model.F_c(t, x, exact(t, x)))

        if exact:
            valD = BndValue(lambda t, x: exact(t, x))
            valFv = BndFlux_v(
                lambda t, x, U, DU, n: Model.F_v(t, x, exact(t, x), grad(exact(t, x)))
                * n
            )

            if withVelocity:
                valFc = BndFlux_c(lambda t, x, U, n: Model.F_c(t, x, exact(t, x)) * n)
                valN = [valFc, valFv]
            else:
                valN = valFv

            boundary = {
                "sides": valD,
                "ends": valN,
            }
        else:
            x0 = as_vector([-0.5, -0.5])
            bnd = lambda x: conditional(dot(x - Model.x0, x - Model.x0) < 0.15, 10, 0)
            valD = BndValue(lambda t, x, U: as_vector([Model.bnd(x)]))
            boundary = {"full": valD}

        if inverted:
            for i in range(1, 5):
                boundary[i] = valD

    return Model
