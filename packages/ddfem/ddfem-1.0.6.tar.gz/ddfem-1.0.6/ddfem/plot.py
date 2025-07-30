from dune.fem.function import gridFunction
from matplotlib import pyplot as plt
from ufl import SpatialCoordinate, triangle


def plotSolution(domain, uh, figsize, **kwargs):
    x = SpatialCoordinate(triangle)
    fig, axs = plt.subplots(1, 2, figsize=[2 * figsize[0], figsize[1]])
    uh.plot(figure=(fig, axs[0]), **kwargs)
    gridFunction(uh * domain.chi(x)).plot(figure=(fig, axs[1]), **kwargs)
    for a in axs:
        gridFunction(domain.phi(x), gridView=uh.space.gridView).plot(
            onlyContours=True,
            contours=[0.5],
            gridLines=None,
            contourWidth=2,
            contourColor="black",
            figure=(fig, a),
        )


def plotSdfTree(SDF, gridView, figsize, maxDepth=None, **kwargs):
    x = SpatialCoordinate(triangle)
    fig, axs = plt.subplots(1, 2, figsize=[2 * figsize[0], figsize[1]])

    gridFunction(SDF(x), gridView=gridView).plot(figure=(fig, axs[0]), **kwargs)

    def plot_recursive(childSDF, depth):
        if maxDepth is not None and depth > maxDepth:
            return

        gridFunction(childSDF(x), gridView=gridView).plot(
            onlyContours=True,
            contours=[0],
            gridLines=None,
            contourWidth=2,
            contourColor="black",
            figure=(fig, axs[0]),
        )

        for child in childSDF.child_sdf:
            plot_recursive(child, depth + 1)

    plot_recursive(SDF, 0)
    gridFunction(SDF(x), gridView=gridView).plot(
        onlyContours=True,
        contours=[0],
        gridLines=None,
        contourWidth=2,
        contourColor="white",
        figure=(fig, axs[0]),
    )
    gridFunction(SDF.phi(x), gridView=gridView).plot(figure=(fig, axs[1]), **kwargs)

def plotBndExt(domain, Model, uh, figsize, t=0, **kwargs):
    from .boundary import BoundaryTerms

    x = SpatialCoordinate(triangle)

    bt = BoundaryTerms(Model, domain)
    bndExt = bt.BndValueExt(t, x, uh)

    fig, axs = plt.subplots(1, figsize=figsize)
    gridFunction(bndExt, gridView=uh.space.gridView).plot(figure=(fig, axs), **kwargs)

    gridFunction(domain(x), gridView=uh.space.gridView).plot(
        onlyContours=True,
        contours=[0],
        gridLines=None,
        contourWidth=2,
        contourColor="black",
        figure=(fig, axs),
    )
