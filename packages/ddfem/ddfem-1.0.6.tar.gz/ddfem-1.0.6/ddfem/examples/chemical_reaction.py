from dune.ufl import Constant
from ufl import as_vector, conditional, dot, grad, outer, zero

from ddfem.boundary import BndFlux_c, BndFlux_v, BndValue


def crModel():
    class PotentialModel:
        dimRange = 1
        outFactor_i = Constant(1, "outFactor")

        def F_v(t, x, U, DU):
            return DU

        def S_e(t, x, U, DU):
            return as_vector([-1])

        def valD(t, x, U):
            return zero(1)

        boundary = {
            "full": BndValue(valD),
        }

    class ChemModel:
        dimRange = 3

        dt = Constant(0.05, "dt")
        diff = Constant(1e-3, "diff")  # this is about the boundary for stability
        # outFactor_i = diff

        P1 = as_vector([-0.25, -0.25])  # midpoint of first source (close to boundary)
        P2 = as_vector([0.25, 0.25])  # midpoint of second source (close to boundary)

        u_h_n = None
        dpsi_h = None

        def setup(u_h, DDMPotentialModel, psi_h):
            ChemModel.u_h_n = u_h.copy(name="u_h_n")
            ChemModel.u_h_n.interpolate(zero(ChemModel.dimRange))

            ChemModel.dpsi_h = lambda x: DDMPotentialModel.sigma(
                0, x, psi_h, grad(psi_h)
            )

        def f1(x):
            q = x - ChemModel.P1
            return conditional(dot(q, q) < 0.04**2, 5, 0)

        def f2(x):
            q = x - ChemModel.P2
            return conditional(dot(q, q) < 0.04**2, 5, 0)

        def f(t, x):
            return conditional(
                t < 10,
                as_vector([ChemModel.f1(x), ChemModel.f2(x), 0]),
                as_vector([0, 0, 0]),
            )

        def r(U):
            return 10 * as_vector([U[0] * U[1], U[0] * U[1], -2 * U[0] * U[1]])

        def F_v(t, x, U, DU):
            return ChemModel.diff * DU

        def velocity(x):
            return as_vector([-ChemModel.dpsi_h(x)[0, 1], ChemModel.dpsi_h(x)[0, 0]])

        def F_c(t, x, U):
            return outer(U, ChemModel.velocity(x))

        def S_i(t, x, U, DU):
            return -(U - ChemModel.u_h_n) / ChemModel.dt

        def S_e(t, x, U, DU):
            return ChemModel.f(t, x) - ChemModel.r(ChemModel.u_h_n)

        # boundary = {"full": BndValue(lambda t, x, U: zero(3))}

        boundary = {
            "full": [
                BndFlux_c(lambda t, x, U, n: zero(ChemModel.dimRange)),
                BndFlux_v(lambda t, x, U, DU, n: zero(ChemModel.dimRange)),
            ]
        }

    return PotentialModel, ChemModel
