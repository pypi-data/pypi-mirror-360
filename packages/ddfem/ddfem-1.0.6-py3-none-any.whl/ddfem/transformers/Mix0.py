from ufl import grad, outer

from .transformer_base import transformer

"""
Diffusion:
Paper with sigma = grad(phi u) - grad(phi)g
phi Asigma.(grad(phi v) + grad(phi)v) + 1/4 (Agrad(phi),grad(phi))(u-g)v
= phi Asigma.(phi grad(v) + 2grad(phi)v) + 1/4 (Agrad(phi),grad(phi))(u-g)v
= phi^2 Asigma.grad(v) + 2phi Asigma.grad(phi)v + 1/4 (Agrad(phi),grad(phi))(u-g)v

orig.F_v(u,Du) = A Du
orig.S_i(u,Du) = -div(ADg)

mix0.F_v = phi^2 orig.F_v(u,sigma)
mix0.S_i = phi^2 orig.S_i(u,sigma) - 2phi orig.F_v(u,sigma).grad(phi) - 1/4 F_v(u,grad(phi)(u-g)).grad(phi)

model = mix0.F_v(u,Du).grad(v) - mix0.S_i(u,Du)v
      = phi^2 Asigma.grad(v) + phi^2 div(ADg)v + 2phi Asigma.grad(phi)v + 1/4 Agrad(phi)(u-g).grad(phi)
      = phi Asigma.grad(phi v) - phi Asigma.grad(phi)v + phi^2 div(ADg)v + 2phi Asigma.grad(phi)v
        + 1/4 Agrad(phi).grad(phi)(u-g)
      = phi Asigma.(grad(phi v) + grad(phi)v) + phi^2 div(ADg)v + 1/4 Agrad(phi).grad(phi))(u-g)

Advection:
orig.F_c = bu
orig.S_e = div(bg)

mix0.F_c(u) = phi^2 orig.F_c(u)
            = phi^2 bu
mix0.S_e(u) = phi^2 orig.S_e(u) - phi orig.F_c(u+g).grad(phi)
            = phi^2 div(bg) + phi (u+g) b.grad(phi)

model = - mix0.F_c(u).grad(v) - mix0.S_e(u)v
      = - phi^2 u b.grad(v) - phi^2 div(bg)v - phi (u+g) b.grad(phi)v
      = ( div(phi u phi b) - phi (u+g) b.grad(phi) - phi^2 div(bg) )v
      = ( phi b.grad(phi u) + phi u div(phi b) - phi (u+g) b.grad(phi) - phi^2 div(bg) )v
      = ( phi b.(grad(phi u)-g grad(phi))
          - phi u b.grad(phi) + phi^2 u div(b) + phi u b.grad(phi)
          - phi^2 b.grad(g) - phi^2 g div(b) )v
      = ( phi b.(phi sigma) + phi^2 div(b)(u-g) - phi^2 b.grad(g) )v
      = phi^2 ( b.(sigma - grad(g)) + div(b)(u-g) ) v

paper = phi b . sigma v
      = phi b . [grad(phi u) - g.grad(phi)] v
"""


@transformer
def Mix0DDM(Model):

    class DDModel(Model):
        def sigma(t, x, U, DU=None):
            if not DU:
                DU = grad(U)
            sigma = DU + outer(
                DDModel.BT.jumpV(t, x, U), grad(DDModel.phi(x))
            ) / DDModel.phi(x)
            return sigma

        def S_e_source(t, x, U, DU):
            return DDModel.phi(x) ** 2 * Model.S_e(t, x, U, DDModel.sigma(t, x, U, DU))

        def S_e_convection(t, x, U, DU):
            # unsure if using Model.F_c is the right choice here - works in the linear case.
            convec = (
                DDModel.phi(x)
                * Model.F_c(t, x, 2 * U - DDModel.BT.jumpV(t, x, U))
                * grad(DDModel.phi(x))
            )

            convec -= DDModel.phi(x) * DDModel.BT.BndFlux_cExt(t, x, U)
            return convec

        def S_outside(t, x, U, DU):
            return -(
                DDModel.BT.jumpV(t, x, U)
                * (1 - DDModel.phi(x)) ** 2
                / (DDModel.epsilon**2)
            )

        def S_i_source(t, x, U, DU):
            return DDModel.phi(x) ** 2 * Model.S_i(t, x, U, DDModel.sigma(t, x, U, DU))

        def S_i_diffusion(t, x, U, DU):
            Fv = Model.F_v(t, x, U, DDModel.sigma(t, x, U, DU))
            diffusion = 2 * DDModel.phi(x) * Fv * grad(DDModel.phi(x))

            gp = grad(DDModel.phi(x))
            uogp = outer((DDModel.BT.jumpV(t, x, U)), gp)
            # use of F_v is probably not correct...
            diffusion += (
                # Model.F_v_lin_mult(t, x, U, Mix0DDM.sigma(t,x, U, DU), uogp)
                Model.F_v(t, x, U, uogp)
                * gp
                / 4
            )

            diffusion += DDModel.phi(x) * DDModel.BT.jumpFv(t, x, U, DU, Fv)
            return -diffusion

        def F_c(t, x, U):
            return DDModel.phi(x) ** 2 * Model.F_c(t, x, U)

        def F_v(t, x, U, DU):
            return DDModel.phi(x) ** 2 * Model.F_v(t, x, U, DDModel.sigma(t, x, U, DU))

    return DDModel
