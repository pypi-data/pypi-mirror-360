import inspect

import ufl
from ufl import replace, zero
from ufl.algorithms.ad import expand_derivatives
from ufl.core.expr import Expr

from .geometry.domain import Domain
from .geometry.primitive_base import SDF


class BoundaryCondition:
    def __init__(self, value):
        self.value = value

    def __call__(self, *args, **kwds):
        return self.value(*args, **kwds)


class BndValue(BoundaryCondition):
    def __init__(self, value):
        if isinstance(value, ufl.core.expr.Expr):
            super().__init__(lambda t, x, u: value)
        else:
            num_args = len(inspect.signature(value).parameters)
            if num_args == 1:
                super().__init__(lambda t, x, u: value(x))
            elif num_args == 2:
                super().__init__(lambda t, x, u: value(t, x))
            elif num_args == 3:
                super().__init__(value)
            # elif num_args == 4:
            #     self.SPLIT = True
            #     super().__init__(lambda t, x, u: value(t, x, u, n, n))
            else:
                raise ValueError(f"Boundary has {num_args} arguments.")


class BndFlux_v(BoundaryCondition):
    pass


class BndFlux_c(BoundaryCondition):
    pass


def classify_boundary(boundary_dict):

    boundary_flux_cs = {}  # Fluxes for the advection term
    boundary_flux_vs = {}  # Fluxes for the diffusion term
    boundary_values = {}  # Boundary values for Dirichlet

    for k, f in boundary_dict.items():

        if isinstance(k, (Expr, str)):
            ids = [k]
        elif callable(k):
            ids = [k]
        else:
            try:
                ids = []
                for kk in k:
                    ids += [kk]
            except TypeError:
                ids = [k]

        if isinstance(f, (tuple, list)):
            assert len(f) == 2, "too many boundary fluxes provided"
            if isinstance(f[0], BndFlux_v) and isinstance(f[1], BndFlux_c):
                boundary_flux_vs.update([(kk, f[0]) for kk in ids])
                boundary_flux_cs.update([(kk, f[1]) for kk in ids])

            elif isinstance(f[0], BndFlux_c) and isinstance(f[1], BndFlux_v):
                boundary_flux_vs.update([(kk, f[1]) for kk in ids])
                boundary_flux_cs.update([(kk, f[0]) for kk in ids])

            else:
                raise ValueError("Need AFlux and DFlux")

        elif isinstance(f, BndFlux_v):
            boundary_flux_vs.update([(kk, f) for kk in ids])

        elif isinstance(f, BndFlux_c):
            boundary_flux_cs.update([(kk, f) for kk in ids])

        elif isinstance(f, BndValue):
            boundary_values.update([(kk, f) for kk in ids])

        else:
            raise NotImplementedError(f"unknown boundary type {k} : {f}")

    return boundary_flux_cs, boundary_flux_vs, boundary_values


def boundary_validation(Model, override_boundary_dict=None):
    if override_boundary_dict is not None:
        boundary_dict = override_boundary_dict
    else:
        boundary_dict = Model.boundary

    hasFlux_c = hasattr(Model, "F_c")
    hasFlux_v = hasattr(Model, "F_v")

    boundary_flux_cs, boundary_flux_vs, boundary_values = classify_boundary(
        boundary_dict
    )

    if hasFlux_c and hasFlux_v:
        assert len(boundary_flux_cs) == len(
            boundary_flux_vs
        ), "two bulk fluxes given, but one boundary fluxes provided"

    if not hasFlux_c:
        assert len(boundary_flux_cs) == 0, "No bulk Advection, but boundary flux given"

    if not hasFlux_v:
        assert len(boundary_flux_vs) == 0, "No bulk diffusion, but boundary flux given"

    assert boundary_values.keys().isdisjoint(boundary_flux_cs)
    assert boundary_values.keys().isdisjoint(boundary_flux_vs)

    return boundary_flux_cs, boundary_flux_vs, boundary_values


class BoundaryTerms:
    def __init__(self, Model, domainDescription):
        self.Model = Model

        if isinstance(domainDescription, Domain):
            self.domain = domainDescription
        else:
            self.domain = Domain(domainDescription)

        condition = lambda k: isinstance(k, str) or isinstance(k, SDF)
        self.diffuse = {k: v for k, v in Model.boundary.items() if condition(k)}
        self.physical = {k: v for k, v in Model.boundary.items() if not condition(k)}

        self.boundary_flux_cs, self.boundary_flux_vs, self.boundary_values = (
            boundary_validation(self.Model, override_boundary_dict=self.diffuse)
        )

        self.bV_weight = []
        self.bF_weight = []

        for model_key in self.boundary_values.keys():
            phi_i_proj = self.domain.bndProjSDFs(model_key)
            self.bV_weight.append(phi_i_proj)

        for model_key in {*self.boundary_flux_cs.keys(), *self.boundary_flux_vs.keys()}:
            phi_i_proj = self.domain.bndProjSDFs(model_key)
            self.bF_weight.append(phi_i_proj)

        if not self.boundary_values:
            self.BndValueExt = None

        if not self.boundary_flux_vs:
            self.BndFlux_vExt = None

    def _dbc_total_weight(self, x):
        weight = 1e-10
        for w_func in self.bV_weight:
            weight += w_func(x)
        return weight
    def _total_weight(self, x):
        weight = 1e-10  # tol
        for w_func in self.bV_weight + self.bF_weight:
            weight += w_func(x)
        return weight

    def _boundary_extend(self, g, x):
        g_tmp = expand_derivatives(g)
        return replace(g_tmp, {x: self.domain.boundary_projection(x)})

    # perhaps switch methods around so that BndValueExt is setup and then
    # jumpD does sum(w)*U - BndValueExt. But then the exception needs to be caught...
    def jumpV(self, t, x, U, U1=None):
        jdv = zero(U.ufl_shape)

        if U1 is None:
            U1 = U

        for g_func, w_func in zip(self.boundary_values.values(), self.bV_weight):
            g_tmp = g_func(t, x, U)  # g_func is a callable from self.boundary_values
            g_ext = self._boundary_extend(g_tmp, x)
            jdv += w_func(x) * (U1 - g_ext)

        return jdv / self._total_weight(x)

    def BndValueExt(self, t, x, U):
        # called if self.BndValueExt was not set to None in __init__
        z = zero(U.ufl_shape)
        return -self.jumpV(t, x, U, z)

    def jumpFv(self, t, x, U, DU, Fv):
        # (sigma.n-gN)*ds(N) = - wN ( sigma.Dphi + gN|Dphi| )
        #   = wN ( (-sigma.Dphi) - gN(t,x,-Dphi/|Dphi|)|Dphi| )
        #   = wN ( sigma.sn - gN(t,x,sn) ) with sn = -Dphi
        jdf = zero(U.ufl_shape)

        fv_scaled = Fv * self.domain.scaled_normal(x)
        for g_func, w_func in zip(self.boundary_flux_vs.values(), self.bF_weight):
            g_tmp = g_func(t, x, U, DU, self.domain.normal(x))
            g_ext = self._boundary_extend(g_tmp, x)
            jdf += w_func(x) * (fv_scaled - g_ext * self.domain.surface_delta(x))

        return jdf / self._total_weight(x)
        # return jdf * (self._dbc_total_weight(x) / self._total_weight(x))

    def BndFlux_vExt(self, t, x, U, DU):
        # called if self.BndFlux_vExt was not set to None in __init__
        z = zero(DU.ufl_shape)
        return -self.jumpFv(t, x, U, DU, z)

    def BndFlux_cExt(self, t, x, U):
        jda = zero(U.ufl_shape)

        for g_func, w_func in zip(self.boundary_flux_cs.values(), self.bF_weight):
            g_tmp = g_func(t, x, U, self.domain.normal(x))
            g_ext = self._boundary_extend(g_tmp, x)
            jda += w_func(x) * -g_ext * self.domain.surface_delta(x)

        return -jda / self._total_weight(x)
