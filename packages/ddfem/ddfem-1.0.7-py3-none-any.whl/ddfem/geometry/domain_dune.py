import time

import dune.ufl
from dune.fem.function import gridFunction
from dune.fem import adapt, mark, markNeighbors
from dune.fem.view import adaptiveLeafGridView, filteredGridView
from dune.grid import cartesianDomain, Marker
from dune.alugrid import aluConformGrid as GridView
from dune.fem.utility import FemThreadPoolExecutor
import ufl

from .domain import Domain
from .. import GridView

class DomainDune(Domain):
    def __init__(self, omega, domain, *,
                 filterTolerance=0,
                 factor=0, refinements=0,
                 adaptLevels=0):
        super().__init__(omega)
        if not hasattr(omega.epsilon,"value"):
            omega.epsilon = dune.ufl.Constant(omega.epsilon,name="epsilon")
        self.gridView = GridView(domain, omega,
                              filterTolerance=filterTolerance,
                              factor=factor,refinements=refinements,
                              adaptLevels=adaptLevels)
        dims = (self.gridView.dimGrid, self.gridView.dimWorld)
        self.x = ufl.SpatialCoordinate(dune.ufl.domain(dims))
        self.fullSDF = self.gridFunction(self.omega(self.x), name="full-sdf")
        self._phi = None
        self._bndProj = None
        self._extProj = None
        self._bndProjSDFs = {}
        self._chi = None

        """
        print("Setting up projections",flush=True)
        with FemThreadPoolExecutor(max_workers=8) as executor:
            executor.submit( self.boundary_projection, self.x )
            executor.submit( self.external_projection, self.x )
            executor.submit( self.phi, self.x )
            executor.submit( self.chi, self.x )
            for child in self.omega:
                executor.submit( self.generate_projSDF, child )
        print("done",flush=True)
        """

    def gridFunction(self, expr, name):
        start_ = time.time()
        gf = gridFunction(expr, name=name, gridView=self.gridView)
        # print(f"{name} setup: {time.time() - start_}")
        return gf

    def phi(self, x):
        if self._phi is None:
            p = super().phi(self.x)
            self._phi = self.gridFunction(p, "phidomain")

        return self._phi

    def chi(self, x):
        return super().chi(self.x)
        if self._chi is None:
            p = super().chi(self.x)
            self._chi = self.gridFunction(p, "chidomain")

        return self._chi

    def boundary_projection(self, x):
        if self._bndProj is None:
            p = super().boundary_projection(self.x)
            self._bndProj = self.gridFunction(p, "bndproj")

        return self._bndProj

    def external_projection(self, x):
        if self._extProj is None:
            p = super().external_projection(self.x)
            self._extProj = self.gridFunction(p, "extproj")

        return self._extProj

    def generate_projSDF(self, sdf):
        projSDF = self._bndProjSDFs.get(sdf.name)
        if projSDF is None:
            projSDF = super().generate_projSDF(sdf)
            gf = self.gridFunction(projSDF(self.x), f"sdfproj{sdf.name}")
            self._bndProjSDFs[sdf.name] = lambda x: gf
            projSDF = self._bndProjSDFs[sdf.name]
        return projSDF

    def _adapt(self, level, lowerTol=-0.1, upperTol=0.1):
        for _ in range(level):
            def mark(e):
                v = self.fullSDF(e, self.gridView.dimension * [1.0 / 3.0])
                return (
                    Marker.refine
                    if v > lowerTol and v < upperTol
                    else Marker.keep
                )
            self.gridView.hierarchicalGrid.adapt(mark)
            lowerTol /= 2
            upperTol /= 2
