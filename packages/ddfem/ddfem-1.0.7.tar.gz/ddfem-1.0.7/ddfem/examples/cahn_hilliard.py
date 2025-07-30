from dune.ufl import Constant
from ufl import as_tensor, as_vector, dot, grad, inner, zero

from ddfem.boundary import BndFlux_c, BndFlux_v, BndValue


def chModel():
    class CHModel:
        dimRange = [1, 1]

        M = Constant(1, name="M")
        lmbda = Constant(1.0e-02, name="lmbda")  # surface parameter
        dt = Constant(5.0e-06, name="dt")  # time step
        theta = Constant(
            0.5, name="theta"
        )  # theta=1 -> backward Euler, theta=0.5 -> Crank-Nicolson

        u_h_n = None
        Du_h_n = None

        def setup(u_h, DDMModel):
            CHModel.u_h_n = u_h.copy()
            CHModel.Du_h_n = lambda t, x: DDMModel.sigma(
                t, x, CHModel.u_h_n, grad(CHModel.u_h_n)
            )

        def energy(U, DU):
            C, MU = as_vector([U[0]]), as_vector([U[1]])
            DC, DMU = as_tensor([DU[0, :]]), as_tensor([DU[1, :]])

            f = 100 * dot(C, C) * dot(as_vector([1]) - C, as_vector([1]) - C)

            return CHModel.lmbda / 2 * inner(DC, DC) + f

        def F_v(t, x, U, DU):
            C, MU = as_vector([U[0]]), as_vector([U[1]])
            DC, DMU = as_tensor([DU[0, :]]), as_tensor([DU[1, :]])
            c_h_n, mu_h_n = as_vector([CHModel.u_h_n[0]]), as_vector([CHModel.u_h_n[1]])
            Du_h_n = CHModel.Du_h_n(t, x)
            Dc_h_n, Dmu_h_n = as_vector([Du_h_n[0, :]]), as_vector([Du_h_n[1, :]])

            mu_mid = (1.0 - CHModel.theta) * Dmu_h_n + CHModel.theta * DMU
            concentration_F_v = CHModel.M * mu_mid
            potential_F_v = CHModel.lmbda * DC

            return as_tensor([concentration_F_v[0, :], potential_F_v[0, :]])

        def S_i(t, x, U, DU):
            C, MU = as_vector([U[0]]), as_vector([U[1]])
            DC, DMU = as_tensor([DU[0, :]]), as_tensor([DU[1, :]])
            c_h_n, mu_h_n = as_vector([CHModel.u_h_n[0]]), as_vector([CHModel.u_h_n[1]])

            concentration_S_i = -(C - c_h_n) / CHModel.dt
            potential_S_i = (
                MU - (200 + 400 * dot(C, C)) * C + as_vector([600 * dot(C, C)])
            )

            return as_vector([concentration_S_i[0], potential_S_i[0]])

        def valF_v(t, x, MU, DMU, n):
            return zero(2)

        boundary = {
            "full": BndFlux_v(valF_v),
        }

    return CHModel
