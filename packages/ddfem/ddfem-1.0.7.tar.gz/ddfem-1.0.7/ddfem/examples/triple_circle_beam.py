import numpy as np

try:
    import pygmsh
except ImportError:
    pygmsh = None

try:
    import dune
except ImportError:
    print(
        """
Example code requires dune to run. To install run
pip install dune-fem
    """
    )

from dune.alugrid import aluConformGrid as leafGridView
from dune.fem import adapt, mark, markNeighbors
from dune.fem.function import gridFunction
from dune.fem.space import lagrange
from dune.fem.utility import gridWidth
from dune.fem.view import adaptiveLeafGridView
from dune.grid import cartesianDomain
from dune.ufl import Constant, Space
from ufl import SpatialCoordinate, as_vector, sqrt

from ddfem import geometry as gm
from ddfem.geometry.domain_dune import DomainDune


def getDomain(initialRefine, version, adaptLevels=0, epsFactor=4.5, dirichlet=True):

    # gm.SDF.smoothing = 50

    shiftx, shifty = sqrt(2) * 1e-6, sqrt(3) * 1e-6

    if dirichlet:
        domain_range = [
            [-0.8 + shiftx, -0.8 + shifty, 0.1],  # -0.5
            [0.8 + shiftx, 0.8 + shifty, 3.3],  #  3.2
        ]
        initial_gridsize = [60, 60, 60]
    else:
        domain_range = [
            [-0.8 + shiftx, -0.8 + shifty, 0.0 - 0.5],
            [0.8 + shiftx, 0.8 + shifty, 3.2 + 0.5],
        ]
        initial_gridsize = [60, 60, 80]
    initial_gridsize = [i * 2**initialRefine for i in initial_gridsize]
    h = sqrt(
        ((domain_range[1][0] - domain_range[0][0]) / initial_gridsize[0]) ** 2
        + ((domain_range[1][1] - domain_range[0][1]) / initial_gridsize[1]) ** 2
        + ((domain_range[1][2] - domain_range[0][2]) / initial_gridsize[2]) ** 2
    )

    def get_eps(h):
        return Constant(epsFactor * h * 0.5 ** (adaptLevels / 3), "epsilon")

    balls = [
        [0.3, [0.15, 0.15], "b1"],
        [0.3, [-0.15, -0.15], "b2"],
        [0.4, [0, 0], "b3"],
    ]

    b = [gm.Ball(c[0], c[1], name=c[2]) for c in balls]
    sdfs = [b[0] | b[1], b[2]]
    face_2d = sdfs[0] & sdfs[1]

    face_2d.name = "beam"

    if dirichlet:
        length = 4
    else:
        length = 3.2
    omega = face_2d.extrude(length, True)
    omega.name = "full"

    h_max = h * 3
    h_min = h / 2
    radius = 3

    x = SpatialCoordinate(Space(3))
    sdf = omega(x)

    def spacing(x, y, z, epsilon):
        r_min = epsilon.value
        r_max = radius * epsilon.value
        dist = np.abs(sdf((x, y, z)))
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
        epsilon = get_eps(h)

    elif version == "fitted":
        if pygmsh is None:
            raise AttributeError("'fitted' requires install pygmsh")
        with pygmsh.occ.Geometry() as geom:
            geom.characteristic_length_max = h_max
            geom.characteristic_length_min = h_min
            epsilon = get_eps(h_min)

            disks = [geom.add_disk([c[1][0], c[1][1], 0.0], c[0]) for c in balls]

            ds = geom.boolean_union([disks[0], disks[1]])
            shape = geom.boolean_intersection([ds, disks[2]])
            geom.extrude(shape, [0, 0, length])

            geom.set_mesh_size_callback(
                lambda dim, tag, x, y, z, lc: spacing(x, y, z, epsilon),
                ignore_other_mesh_sizes=True,
            )
            mesh = geom.generate_mesh()
            points, cells = mesh.points, mesh.cells_dict
            domain = {
                "vertices": points[:,].astype(float),
                "simplices": cells["tetra"].astype(int),
            }

    elif version == "dune_adaptive":
        gridsize = [int(j * h / h_max) for j in initial_gridsize]
        domain = cartesianDomain(*domain_range, gridsize)

    elif version == "gmsh_adaptive":
        if pygmsh is None:
            raise AttributeError("'gmsh_adaptive' requires install pygmsh")
        with pygmsh.occ.Geometry() as geom:
            geom.characteristic_length_max = h_max
            geom.characteristic_length_min = h_min
            epsilon = get_eps(h_min)

            geom.add_box(
                [0.0, 0.0, 0.0],
                [
                    domain_range[1][0] - domain_range[0][0],
                    domain_range[1][1] - domain_range[0][1],
                    domain_range[1][2] - domain_range[0][2],
                ],
            )

            geom.set_mesh_size_callback(
                lambda dim, tag, x, y, z, lc: spacing(x, y, z, epsilon),
                ignore_other_mesh_sizes=True,
            )
            mesh = geom.generate_mesh()
            points, cells = mesh.points, mesh.cells_dict
            domain = {
                "vertices": points[:,].astype(float),
                "simplices": cells["tetra"].astype(int),
            }
    else:
        raise ValueError("invalid mesh type")

    gridView = adaptiveLeafGridView(leafGridView(domain))
    # return gridView, None

    if version == "dune_adaptive":
        # omega.epsilon = get_eps(h)
        omega.epsilon = get_eps(h_min)
        omega.epsilon.value *= radius
        epsilon_value = omega.epsilon.value

        marker = mark

        refinements = int(3 * np.log2(h_max / h_min))
        region = gridFunction(
            omega.phi(x) * (1 - omega.phi(x)), gridView=gridView
        )  # interface

        for j in range(1, refinements + 1):
            print("refining:", j, gridView.size(2), flush=True)
            if gridView.size(2) > 5e5:
                assert j == refinements
                j -= 1
                break
            omega.epsilon.value = epsilon_value * j / refinements
            marker(region, 0.00247262315663, maxLevel=refinements)  # epsilon
            adapt(gridView.hierarchicalGrid)

            # markNeighbors(region, 0.1, maxLevel=refinements)
            # marker(region, 0.2, maxLevel=refinements)
            # adapt(gridView.hierarchicalGrid)
            # omega.epsilon.value = omega.epsilon.value * 2**(-1/3)

        h_min = h_max * 0.5 ** (j / 3)
        epsilon = get_eps(h_min)

    omega.epsilon = epsilon
    domain = omega

    domain = DomainDune(omega, gridView)
    # domain.adapt(level=adaptLevels)

    print(
        f"h_max={h_max}, h_min={h_min * 0.5 ** (adaptLevels / 3)}, epsilon={epsilon.value}"
    )

    return gridView, domain
