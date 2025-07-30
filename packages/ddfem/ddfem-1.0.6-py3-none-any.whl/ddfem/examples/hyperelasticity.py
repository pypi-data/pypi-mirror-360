from dune.ufl import Constant
from ufl import (
    Identity,
    as_vector,
    conditional,
    det,
    diff,
    div,
    dot,
    grad,
    ln,
    nabla_div,
    nabla_grad,
    outer,
    replace,
    sym,
    tr,
    variable,
    zero,
)
from ufl.algorithms.ad import expand_derivatives

from ddfem.boundary import BndFlux_v, BndValue


def hyModel():
    # https://jsdokken.com/dolfinx-tutorial/chapter2/hyperelasticity.html
    class Model:
        dimRange = 2
        rho = Constant(1000, name="density")  # kg/m3
        g = Constant(9.8, name="gravity")  # m/s2

        body = Constant([0.0, -rho * g], "body")  # N/m3
        vd = Constant([0, 0], "fixedboundary")
        T = Constant([0, 0], "traction")  # Pa

        outFactor_i = Constant(1, "outFactor")

        # Elasticity parameters
        # https://www.efunda.com/formulae/solid_mechanics/mat_mechanics/calc_elastic_constants.cfm
        E = 1e7  # Young modulus ; Pa
        nu = 0.4  # Poisson ratio ;
        lamb = Constant(E * nu / ((1 + nu) * (1 - 2 * nu)), name="Lame_1")  # Pa
        mu = Constant(E / (2 * (1 + nu)), name="Lame_2")  # i.e. Shear modulus ; Pa

        def P(U, DU):
            I = Identity(Model.dimRange)
            # Stress
            # Hyper-elasticity, (compressible neo-Hookean model)
            F = variable(I + grad(U))  # Deformation gradient
            C = F.T * F  # Right Cauchy-Green tensor
            J = det(F)
            Ic = tr(C)  # First Invariant
            mu = Model.mu
            lamb = Model.lamb
            psi = (mu / 2) * (Ic - 3) - mu * ln(J) + (lamb / 2) * (ln(J)) ** 2

            p = diff(psi, F)
            p = expand_derivatives(p)
            p = replace(p, {F: I + DU})
            # p = replace(p, {F: I + grad(U)})

            # Linear-elasticity
            # p = lamb * tr(sym(DU)) * I + 2 * mu * sym(DU)

            return p

        def F_v(t, x, U, DU):
            return Model.P(U, DU)

        def S_i(t, x, U, DU):
            return Model.body

        valD = lambda t, x, U: Model.vd

        valN = lambda t, x, U, DU, n: Model.T

        boundary = {
            "left": BndValue(valD),
            "other": BndFlux_v(valN),
        }
        # boundary = {
        #     "left": BndValue(valD),
        #     "right": BndFlux_v(valN),
        #     "bulk": BndFlux_v(valN),
        # }

    return Model
