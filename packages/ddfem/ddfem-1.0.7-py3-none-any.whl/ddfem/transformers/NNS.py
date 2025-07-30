from ufl import as_vector, conditional, dot, grad, sqrt, zero

from .transformer_base import transformer

"""
Paper: using x^- = 1/2(x-|x|), x^+ = 1/2(x+|x|) so that x = x^+ + x^-, i.e., x^+ - x = - x^-
the advection b.grad(u)v is replaced with
phi b.grad(u) v + [b.grad(phi)]^+ (u-g)v
= div(phi bu)v - div(phi b) uv + [b.grad(phi)]^+ (u-g)v
= - phi u b.grad(v) - phi div(b) uv - b.grad(phi) uv + [b.grad(phi)]^+ uv - [b.grad(phi)]^+ gv
= - phi u b.grad(v) - phi div(b) uv + ([b.grad(phi)]^+ - b.grad(phi)) uv - [b.grad(phi)]^+ gv
= - phi u b.grad(v) - phi div(b) uv - [b.grad(phi)]^- uv - [b.grad(phi)]^+ gv

orig.F_c = bu
orig.S_e = div(bg)

ddm2.F_c(u) = phi orig.F_c(u)
            = phi bu
ddm2.S_e(u) = phi orig.S_e(u) + [b.grad(phi)]^- u
            = phi div(bg) + [b.grad(phi)]^- u + [b.grad(phi)]^+ gv

model = - ddm2.F_c(u).grad(v) - ddm2.S_e(u)v
      = - phi u b.grad(v) - phi div(bg)v - [b.grad(phi)]^- uv - [b.grad(phi)]^+ gv
      = div(phi u b)v - phi div(b)gv - phi b.grad(g) v - [b.grad(phi)]^- uv - [b.grad(phi)]^+ gv
      = phi b.grad(u)v + div(phi b)uv - phi div(b)gv - phi b.grad(g) v - [b.grad(phi)]^- uv - [b.grad(phi)]^+ gv
      = phi b.grad(u)v + phi div(b) uv + b.grad(phi)uv - [b.grad(phi)]^- uv - phi div(b)gv - phi b.grad(g) v - [b.grad(phi)]^+ gv
      = phi b.(grad(u) - grad(g)) v + phi div(b) (u-g)v + b.grad(phi)uv - [b.grad(phi)]^- uv - [b.grad(phi)]^+ gv
      = phi b.(grad(u) - grad(g)) v + phi div(b) (u-g)v + [b.grad(phi)]^+ (u-g)v
"""


@transformer
def NDDM(Model):
    class DDModel(Model):
        def S_e_source(t, x, U, DU):
            return DDModel.phi(x) * Model.S_e(t, x, U, DDModel.sigma(t, x, U, DU))

        def S_e_convection(t, x, U, DU):
            if DDModel.BT.BndValueExt is not None:
                direction = Model.F_c_lin_mult(t, x, U, -grad(DDModel.phi(x)))  # fc * n
                flux_u = Model.F_c(t, x, U) * -grad(DDModel.phi(x))
                flux_g = Model.F_c(t, x, DDModel.BT.BndValueExt(t, x, U)) * -grad(
                    DDModel.phi(x)
                )
                convec = []
                for i in range(U.ufl_shape[0]):
                    convec.append(
                        conditional(direction[i, i] > 0, flux_u[i], flux_g[i])
                    )
                convec = -as_vector(convec)
            else:
                convec = zero(U.ufl_shape)

            convec -= DDModel.BT.BndFlux_cExt(t, x, U)
            return convec

        def S_outside(t, x, U, DU):
            return -(
                DDModel.BT.jumpV(t, x, U) * (1 - DDModel.phi(x)) / (DDModel.epsilon**2)
            )

        def S_i_source(t, x, U, DU):
            return DDModel.phi(x) * Model.S_i(t, x, U, DDModel.sigma(t, x, U, DU))

        def S_i_diffusion(t, x, U, DU):
            beta = 3 * (1 - DDModel.phi(x)) / (2 * DDModel.epsilon)
            diffusion = beta * (
                sqrt(dot(grad(DDModel.phi(x)), grad(DDModel.phi(x))))
                * DDModel.BT.jumpV(t, x, U)
            )
            Fv = Model.F_v(t, x, U, DDModel.sigma(t, x, U, DU))
            diffusion += Fv * grad(DDModel.phi(x))
            diffusion += DDModel.BT.jumpFv(t, x, U, DU, Fv)
            return -diffusion

        def F_c(t, x, U):
            return DDModel.phi(x) * Model.F_c(t, x, U)

        def F_v(t, x, U, DU):
            return DDModel.phi(x) * Model.F_v(t, x, U, DDModel.sigma(t, x, U, DU))

    return DDModel
