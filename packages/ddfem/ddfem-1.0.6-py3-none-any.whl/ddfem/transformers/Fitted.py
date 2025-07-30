from functools import reduce

from ufl import conditional, eq, grad, min_value

from ..boundary import BndFlux_c, BndFlux_v, BndValue, boundary_validation
from ..geometry.domain import Domain
from ..geometry.primitive_base import SDF
from .transformer_base import pretransformer


def Fitted(OriginalModel, domainDescription):

    if isinstance(domainDescription, Domain):
        domain = domainDescription
    else:
        domain = Domain(domainDescription)

    condition = lambda k: isinstance(k, str) or isinstance(k, SDF)

    class Fitted(OriginalModel):
        def sigma(t, x, U, DU=None):
            if DU:
                return DU
            return grad(U)

        diffuse = {k: v for k, v in OriginalModel.boundary.items() if condition(k)}
        boundary = {k: v for k, v in OriginalModel.boundary.items() if not condition(k)}

        bndSDFs = {k: domain.bndSDFs(k) for k in diffuse.keys()}

        boundary_flux_cs, boundary_flux_vs, boundary_values = boundary_validation(
            OriginalModel, override_boundary_dict=diffuse
        )

        def make_boundary_function(key, mv, bndSDFs=bndSDFs):
            sdf = bndSDFs[key]
            closest_sdf = lambda x: reduce(
                min_value,
                ([abs(v(x)) for b, v in bndSDFs.items()]),
            )

            boundary_map = lambda x: conditional(eq(closest_sdf(x), abs(sdf(x))), 1, 0)

            if isinstance(mv, BndFlux_v):
                return BndFlux_v(
                    lambda t, x, u, DU, n: boundary_map(x) * mv(t, x, u, DU, n),
                )

            elif isinstance(mv, BndFlux_c):
                return BndFlux_c(
                    lambda t, x, u, n: boundary_map(x) * mv(t, x, u, n),
                )

        def make_boundary_conditional(key, bndSDFs=bndSDFs, tol=1e-2):
            sdf = bndSDFs[key]
            return lambda x: abs(sdf(x)) < tol

        for bc_key, bc_value in boundary_values.items():
            boundary[make_boundary_conditional(bc_key)] = bc_value

        for bc_key in boundary_flux_cs.keys() | boundary_flux_vs.keys():
            if bc_key in boundary_flux_cs and bc_key in boundary_flux_vs:
                af = make_boundary_function(bc_key, boundary_flux_cs[bc_key])
                df = make_boundary_function(bc_key, boundary_flux_vs[bc_key])
                boundary[make_boundary_conditional(bc_key)] = [af, df]

            elif bc_key in boundary_flux_cs and bc_key not in boundary_flux_vs:
                af = make_boundary_function(bc_key, boundary_flux_cs[bc_key])
                boundary[make_boundary_conditional(bc_key)] = af

            elif bc_key not in boundary_flux_cs and bc_key in boundary_flux_vs:
                df = make_boundary_function(bc_key, boundary_flux_vs[bc_key])
                boundary[make_boundary_conditional(bc_key)] = df
            else:
                raise ValueError()

    return Fitted
