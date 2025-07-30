from ufl import as_matrix, diff, dot, grad, inner, replace, variable, zero
from ufl.algorithms.ad import expand_derivatives

from ..boundary import BndFlux_c, BndFlux_v, BndValue, BoundaryTerms


def pretransformer(Model, domainDescription):
    class DDBase(Model):
        BT = BoundaryTerms(Model, domainDescription)
        boundary = BT.physical
        domain = BT.domain

        hasFlux_c = hasattr(Model, "F_c")
        hasFlux_v = hasattr(Model, "F_v")
        hasSource_i = hasattr(Model, "S_i")
        hasSource_e = hasattr(Model, "S_e")

        hasOutFactor_i = hasattr(Model, "outFactor_i")
        hasOutFactor_e = hasattr(Model, "outFactor_e")

        if BT.BndValueExt is not None:
            boundary[lambda x: DDBase.domain.chi(x) < 0.5] = BndValue(BT.BndValueExt)

            assert (
                hasOutFactor_i or hasOutFactor_e
            ), "Dirichlet boundary requires the attribute outFactor_i or outFactor_e for outside term scaling"
        else:

            if hasFlux_c:
                valFc = BndFlux_c(lambda t, x, U, n: -DDBase.BT.BndFlux_cExt(t, x, U))
            if hasFlux_v:
                valFv = BndFlux_v(
                    lambda t, x, U, DU, n: DDBase.BT.BndFlux_vExt(t, x, U, DU)
                )
            if hasFlux_c and hasFlux_v:
                valN = [valFc, valFv]
            elif hasFlux_c:
                valN = valFc
            elif hasFlux_v:
                valN = valFv
            boundary[lambda x: DDBase.domain.chi(x) < 0.5] = valN

        phi = domain.phi
        epsilon = domain.omega.epsilon
        ep = domain.external_projection

        def sigma(t, x, U, DU=None):
            if DU:
                return DU
            return grad(U)

        if hasSource_e:

            def S_e(t, x, U, DU):
                return replace(
                    expand_derivatives(Model.S_e(t, x, U, DU)),
                    {x: DDBase.ep(x)},
                )

        if hasSource_i:

            def S_i(t, x, U, DU):
                return replace(
                    expand_derivatives(Model.S_i(t, x, U, DU)),
                    {x: DDBase.ep(x)},
                )

        if hasFlux_c:

            def F_c(t, x, U):
                # return Model.F_c(t, DDBase.ep(x), U)

                return replace(
                    expand_derivatives(Model.F_c(t, x, U)),
                    {x: DDBase.ep(x)},
                )

        if hasFlux_v:

            def F_v(t, x, U, DU):
                # return Model.F_v(t, DDBase.ep(x), U, DU)

                return replace(
                    expand_derivatives(Model.F_v(t, x, U, DU)),
                    {x: DDBase.ep(x)},
                )

        # U_t + div[F_c(x,t,U) - F_v(x,t,U,grad[U]) ] = S(x,t,U, grad[U]).

        def F_c_lin(t, x, U):
            U = variable(U)
            d = diff(Model.F_c(t, x, U), U)
            d = expand_derivatives(d)
            return d

        # U.ufl_shape == (1,)
        # F_c(U).ufl_shape == (1, 2,)
        # diff(F_c(U), U).ufl_shape == (1, 2, 1)
        # n.ufl_shape == (2,)
        #
        # s, t = F_c(U).ufl_shape
        # f_c = as_matrix([[dot(d[i, j, :], U) for j in range(t)] for i in range(s)])
        #
        # w, = U.ufl_shape
        # convec = as_vector([dot([f_c[w, :], n) for i in range(w)]) # f_c * n
        #
        # switch order

        def F_c_lin_mult(t, x, U, n):
            G = DDBase.F_c_lin(t, x, U)
            # try:
            #     d = dot(G, n)
            #     print("F_c dot")
            #     return d
            # except:
            m, d, m_ = G.ufl_shape
            return as_matrix(
                [[dot(G[i, :, k], n) for k in range(m_)] for i in range(m)]
            )

        def F_v_lin(t, x, U, DU):
            DU = variable(DU)
            d = diff(Model.F_v(t, x, U, DU), DU)
            d = expand_derivatives(d)
            return d

        def F_v_lin_mult(t, x, U, DU, v):
            G = DDBase.F_v_lin(t, x, U, DU)
            # try:
            #     d = dot(G, v)
            #     print("F_v dot")
            #     return d
            # except:
            m, d = v.ufl_shape
            return as_matrix(
                [[inner(G[i, k, :, :], v) for k in range(d)] for i in range(m)]
            )

    return DDBase


def posttransformer(DDModel):
    class DDM(DDModel):
        if DDModel.hasSource_e or DDModel.hasFlux_c or DDModel.hasOutFactor_e:

            def S_e(t, x, U, DU):
                total = zero(U.ufl_shape)

                if DDModel.hasOutFactor_e:
                    total += DDModel.outFactor_e * DDModel.S_outside(t, x, U, DU)
                if DDModel.hasSource_e:
                    total += DDModel.S_e_source(t, x, U, DU)
                if DDModel.hasFlux_c:
                    total += DDModel.S_e_convection(t, x, U, DU)
                return total

        else:
            try:
                del DDModel.S_e
            except AttributeError:
                pass

        if DDModel.hasSource_i or DDModel.hasFlux_v or DDModel.hasOutFactor_i:

            def S_i(t, x, U, DU):
                total = zero(U.ufl_shape)

                if DDModel.hasOutFactor_i:
                    total += DDModel.outFactor_i * DDModel.S_outside(t, x, U, DU)
                if DDModel.hasSource_i:
                    total += DDModel.S_i_source(t, x, U, DU)
                if DDModel.hasFlux_v:
                    total += DDModel.S_i_diffusion(t, x, U, DU)
                return total

        else:
            try:
                del DDModel.S_i
            except AttributeError:
                pass

        if DDModel.hasFlux_c:

            def F_c(t, x, U):
                return DDModel.F_c(t, x, U)

        else:
            try:
                del DDModel.F_c
            except AttributeError:
                pass

        if DDModel.hasFlux_v:

            def F_v(t, x, U, DU):
                return DDModel.F_v(t, x, U, DU)

        else:
            try:
                del DDModel.F_v
            except AttributeError:
                pass

    return DDM


def transformer(transformer):
    def _transformer(OriginalModel, domainDescription):
        PreModel = pretransformer(OriginalModel, domainDescription)
        Model = transformer(PreModel)
        return posttransformer(Model)

    return _transformer
