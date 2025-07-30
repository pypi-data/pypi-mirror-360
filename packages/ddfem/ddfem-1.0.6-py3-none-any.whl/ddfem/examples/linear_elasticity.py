from dune.ufl import Constant
from ufl import Identity, as_vector, div, grad, sym, tr, zero

from ddfem.boundary import BndFlux_v, BndValue


def leModel():
    class Model:
        dimRange = 2
        lamb = Constant(0.1, name="Lame_1")
        mu = Constant(1, name="Lame_2")
        rho = Constant(1 / 1000, name="density")
        g = Constant(9.8, name="gravity")

        outFactor_i = Constant(1, "outFactor")

        vd = Constant([0, 0], "stationary")
        vn = Constant([0, 0], "traction")

        I = Identity(dimRange)

        def sigma(U, DU):
            return Model.lamb * tr(sym(DU)) * Model.I + 2 * Model.mu * sym(DU)

        def F_v(t, x, U, DU):
            return Model.sigma(U, DU)

        def S_i(t, x, U, DU):
            return as_vector([0.0, -Model.rho * Model.g])

        valD = lambda t, x, U: Model.vd

        valN = lambda t, x, U, DU, n: Model.vn

        # boundary = {
        #     "left": BndValue(valD),
        #     "other": BndFlux_v(valN),
        # }
        boundary = {
            "left": BndValue(valD),
            "right": BndFlux_v(valN),
            "bulk": BndFlux_v(valN),
        }

    return Model
