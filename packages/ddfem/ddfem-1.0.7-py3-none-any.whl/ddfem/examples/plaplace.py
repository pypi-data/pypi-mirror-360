from dune.ufl import Constant
from ufl import grad, inner

from ddfem.boundary import BndValue


def pModel(power):
    class Model:
        dimRange = 1
        ep = Constant(1e-5, name="ep")
        f = Constant([1], name="f")
        g = Constant([0], name="g")
        p = Constant(power, name="p")  # p for p-Laplacian
        assert p.value > 1 and p.value < 2**16
        outFactor_i = Constant(1, "outFactor")

        def K(u):
            return (Model.ep**2 + inner(grad(u), grad(u))) ** ((Model.p - 2) / 2)

        def F_v(t, x, U, DU):
            return Model.K(U) * DU

        def S_i(t, x, U, DU):
            return Model.f - U

        bc = BndValue(g)
        boundary = {1: bc, 2: bc, 3: bc, 4: bc, "full": bc}

    return Model
