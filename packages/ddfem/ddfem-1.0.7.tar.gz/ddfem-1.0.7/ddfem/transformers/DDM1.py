from ufl import grad, zero

from .transformer_base import transformer


@transformer
def DDM1(Model):
    class DDModel(Model):
        def S_e_source(t, x, U, DU):
            return DDModel.phi(x) * Model.S_e(t, x, U, DDModel.sigma(t, x, U, DU))

        def S_e_convection(t, x, U, DU):
            return -DDModel.BT.BndFlux_cExt(t, x, U)

        def S_outside(t, x, U, DU):
            return -(
                DDModel.BT.jumpV(t, x, U) * (1 - DDModel.phi(x)) / (DDModel.epsilon**3)
            )

        def S_i_source(t, x, U, DU):
            return DDModel.phi(x) * Model.S_i(t, x, U, DDModel.sigma(t, x, U, DU))

        def S_i_diffusion(t, x, U, DU):
            if DDModel.BT.BndFlux_vExt is not None:
                diffusion = DDModel.BT.BndFlux_vExt(t, x, U, DU)
            else:
                diffusion = zero(U.ufl_shape)
            return diffusion

        def F_c(t, x, U):
            return DDModel.phi(x) * Model.F_c(t, x, U)

        def F_v(t, x, U, DU):
            return DDModel.phi(x) * Model.F_v(t, x, U, DDModel.sigma(t, x, U, DU))

    return DDModel
