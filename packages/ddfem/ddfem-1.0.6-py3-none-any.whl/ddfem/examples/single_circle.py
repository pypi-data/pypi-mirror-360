import numpy as np
try:
    import pygmsh
except ImportError:
    pygmsh = None

try:
    import dune
except ImportError:
    print("""
Example code requires dune to run. To install run
pip install dune-fem
    """)

from ddfem import geometry as gm
from ddfem.geometry.domain_dune import DomainDune

from dune.alugrid import aluConformGrid as leafGridView
from dune.fem.view import adaptiveLeafGridView
from dune.grid import cartesianDomain
from dune.ufl import Constant, Space

from ufl import SpatialCoordinate, sqrt

def getDomain(initialRefine, version, inverted, adaptLevels=0, epsFactor=4.5):

    shiftx, shifty = sqrt(2) * 1e-6, sqrt(3) * 1e-6
    domain_range = [[-0.5 + shiftx, -0.5 + shifty], [0.5 + shiftx, 0.5 + shifty]]
    initial_gridsize = [75 * 2**initialRefine] * 2
    h = sqrt(
        ((domain_range[1][0] - domain_range[0][0]) / initial_gridsize[0]) ** 2
        + ((domain_range[1][1] - domain_range[0][1]) / initial_gridsize[1]) ** 2
    )
    epsilon = Constant(epsFactor * h * 0.5 ** (adaptLevels / 2), "epsilon")

    print(f"h={h * 0.5 ** (adaptLevels / 2)}, epsilon={epsilon.value}")

    circles = [
        [0.3, [0.15, 0.15], "b1"],
        [0.3, [-0.15, -0.15], "b2"],
        [0.4, [0, 0], "b3"],
    ]

    b = [gm.Ball(c[0], c[1], epsilon=epsilon, name=c[2]) for c in circles]
    sdfs = [b[0] | b[1], b[2]]
    sdfs[0].name = "sides"
    sdfs[1].name = "ends"
    omega = b[2] # sdfs[0] & sdfs[1]
    if inverted:
        omega = omega.invert()
    omega.name = "full"

    x = SpatialCoordinate(Space(2))
    sdf = omega(x)

    def spacing(x, y):
        r_min = 2*epsilon.value
        r_max = 32 * epsilon.value
        dist = np.abs(sdf((x, y)))
        if dist <= r_min:
            return geom.characteristic_length_min
        elif dist >= r_max:
            return geom.characteristic_length_max
        else:
            # Linear
            m = (geom.characteristic_length_max - geom.characteristic_length_min) / (
                r_max - r_min
            )
            return m * (dist - r_min) + geom.characteristic_length_min

    if version == "cartesian":
        domain = cartesianDomain(*domain_range, initial_gridsize)

    elif version == "fitted":
        if pygmsh is None:
            raise AttributeError("'fitted' requires install pygmsh")
        with pygmsh.occ.Geometry() as geom:
            geom.characteristic_length_max = h
            geom.characteristic_length_min = h

            disks = geom.add_disk([circles[2][1][0], circles[2][1][1], 0.0], circles[2][0])
                    # [geom.add_disk([c[1][0], c[1][1], 0.0], c[0]) for c in circles]

            # ds = geom.boolean_union([disks[0], disks[1]])
            shape = disks # geom.boolean_intersection([ds, disks[2]])
            if inverted:
                rectangle = geom.add_rectangle(
                    [domain_range[0][0], domain_range[0][1], 0.0],
                    domain_range[1][0] - domain_range[0][0],
                    domain_range[1][1] - domain_range[0][1],
                )
                geom.boolean_difference(rectangle, shape)

            geom.set_mesh_size_callback(
                lambda dim, tag, x, y, z, lc: spacing(x, y),
                ignore_other_mesh_sizes=True,
            )
            mesh = geom.generate_mesh()
            points, cells = mesh.points, mesh.cells_dict
            domain = {
                "vertices": points[:, :2].astype(float),
                "simplices": cells["triangle"].astype(int),
            }

    elif version == "adaptive":
        if pygmsh is None:
            raise AttributeError("'adaptive' requires install pygmsh")
        with pygmsh.occ.Geometry() as geom:
            geom.characteristic_length_max = h
            geom.characteristic_length_min = h

            geom.add_rectangle(
                [domain_range[0][0], domain_range[0][1], 0.0],
                domain_range[1][0] - domain_range[0][0],
                domain_range[1][1] - domain_range[0][1],
            )

            geom.set_mesh_size_callback(
                lambda dim, tag, x, y, z, lc: spacing(x, y),
                ignore_other_mesh_sizes=True,
            )
            mesh = geom.generate_mesh()
            points, cells = mesh.points, mesh.cells_dict
            domain = {
                "vertices": points[:, :2].astype(float),
                "simplices": cells["triangle"].astype(int),
            }

    gridView = adaptiveLeafGridView(leafGridView(domain))

    domain = DomainDune(omega, gridView)
    domain.adapt(level=adaptLevels)
    gridView.plot()

    return gridView, domain
