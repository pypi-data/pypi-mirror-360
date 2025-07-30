from . import geometry
from . import transformers
from . import boundary
from .model2ufl import model2ufl
from .plot import plotSolution

# a utility method to construct a suitable grid
def GridView(domain, omega=None, *,
                filterTolerance=0,
                factor=0, refinements=0,
                adaptLevels=0):
    import dune.ufl
    from dune.fem.function import gridFunction
    from dune.fem import adapt, mark, markNeighbors
    from dune.fem.view import adaptiveLeafGridView, filteredGridView
    from dune.grid import cartesianDomain, Marker
    from dune.alugrid import aluConformGrid as GridView
    import ufl
    if hasattr(domain,"indexSet"):
        return domain
    if type(domain) == list:
        domain = cartesianDomain(*domain)
    gridView = adaptiveLeafGridView( GridView(domain) )
    dims = (gridView.dimGrid, gridView.dimWorld)
    x = ufl.SpatialCoordinate(dune.ufl.domain(dims))

    if omega and factor>0 and refinements>0:
        startEps = omega.epsilon.value * factor
        region = gridFunction(
            omega.phi(x) * (1 - omega.phi(x)), gridView=gridView
        )  # interface
        for j in range(1, refinements + 1):
            omega.epsilon.value = startEps * j / refinements
            mark(region, 0.00247262315663, maxLevel=refinements)  # 1 epsilon
            adapt(gridView.hierarchicalGrid)
        omega.epsilon.value = startEps/factor * 0.5**(refinements/dims[0])
    if adaptLevels>0:
        sd = gridFunction(omega(x), gridView=gridView)
        bary = dims[0] * [1.0 / (dims[0]+1)]
        lowerTol=-0.1
        upperTol=0.1
        for _ in range(adaptLevels):
            def markStrategy(e):
                v = sd(e, bary)
                return (
                    Marker.refine
                    if v > lowerTol and v < upperTol
                    else Marker.keep
                )
            gridView.hierarchicalGrid.adapt(markStrategy)
            lowerTol /= 2
            upperTol /= 2

    if filterTolerance<0:
        return gridView
    if omega and filterTolerance>0:
        sd = gridFunction(omega(x), gridView=gridView)
        bary = dims[0] * [1.0 / (dims[0]+1)]
        filter = lambda e: 1 if sd(e, bary) < filterTolerance else 2
    else:
        filter = lambda e: 1
    return filteredGridView(
               gridView, filter, domainId=1, useFilteredIndexSet=True)

def solve(uflModel, domain):
    # we use a Lagrange space
    from dune.fem.space import lagrange
    # and the build-in solver
    from dune.fem.scheme import galerkin

    gridView = GridView(domain)
    space = lagrange(gridView, dimRange=1)
    scheme = galerkin(uflModel, space=space,
                      solver=("suitesparse","umfpack"))
    uh = space.interpolate(0,name="ddm")
    scheme.solve(target=uh)
    return uh
