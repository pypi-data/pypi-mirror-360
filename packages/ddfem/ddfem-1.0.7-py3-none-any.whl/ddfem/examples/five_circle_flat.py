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

from dune.fem.function import gridFunction
from dune.fem.space import lagrange
from dune.grid import cartesianDomain
from dune.ufl import Constant, Space
from ufl import SpatialCoordinate, sqrt

from ddfem import geometry as gm
from ddfem import GridView
from ddfem.geometry.domain_dune import DomainDune


def getDomain(
    initialRefine,
    version,
    adaptLevels=0,
    epsFactor=4.5,
    smoothing=None,
    *args,
    **kwargs,
):

    gm.SDF.smoothing = smoothing
    shiftx, shifty = sqrt(2) * 1e-6, sqrt(3) * 1e-6
    domain_range = [[-1.7 + shiftx, -1.3 + shifty], [1.7 + shiftx, 1.3 + shifty]]
    initial_gridsize = [170 * 2**initialRefine, 130 * 2**initialRefine]
    h = sqrt(
        ((domain_range[1][0] - domain_range[0][0]) / initial_gridsize[0]) ** 2
        + ((domain_range[1][1] - domain_range[0][1]) / initial_gridsize[1]) ** 2
    )

    def get_eps(h):
        return Constant(epsFactor * h * 0.5 ** (adaptLevels / 2), "epsilon")

    balls = [
        [1, [0, 0], "Center"],
        [0.5, [0, 0.8], "TopCut"],
        [0.5, [0, -0.8], "BotCut"],
        [0.5, [1, 0], "RightAdd"],
        [0.5, [-1, 0], "LeftAdd"],
        [1.4, [0, 0], "Cutoff"],
    ]

    b = [gm.Ball(c[0], c[1], name=c[2]) for c in balls]
    # omega = (b[0] - b[1] - b[2] | b[3] | b[4]) & b[5]

    bulk = b[0] - b[1] - b[2] | b[3] | b[4]
    bulk.name = "bulk"

    left_cutoff = b[5] | gm.Plane([-1, 0], -0.4)
    left_cutoff.name = "left"
    right_cutoff = b[5] | gm.Plane([1, 0], -0.4)
    right_cutoff.name = "right"

    cutoff = left_cutoff & right_cutoff  # b[5]

    omega = bulk & cutoff
    omega.name = "full"

    h_max = h * 3
    h_min = h / 2
    radius = 5

    x = SpatialCoordinate(Space(2))
    sdf = omega(x)

    def spacing(x, y, epsilon):
        r_min = epsilon.value
        r_max = radius * epsilon.value
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

    omega.epsilon = get_eps(h)

    if version == "cartesian":
        domain = cartesianDomain(*domain_range, initial_gridsize)

    elif version == "fitted":
        if pygmsh is None:
            raise AttributeError("'fitted' requires install pygmsh")
        with pygmsh.occ.Geometry() as geom:
            geom.characteristic_length_max = h_max
            geom.characteristic_length_min = h_min

            disks = [geom.add_disk([c[1][0], c[1][1], 0.0], c[0]) for c in balls]

            disk_removed1 = geom.boolean_difference(disks[0], disks[1])
            disk_removed2 = geom.boolean_difference(disk_removed1, disks[2])

            disk_add = geom.boolean_union([disk_removed2, disks[3], disks[4]])
            shape = geom.boolean_intersection([disk_add, disks[5]])

            geom.set_mesh_size_callback(
                lambda dim, tag, x, y, z, lc: spacing(x, y, omega.epsilon),
                ignore_other_mesh_sizes=True,
            )
            mesh = geom.generate_mesh()
            points, cells = mesh.points, mesh.cells_dict
            domain = {
                "vertices": points[:, :2].astype(float),
                "simplices": cells["triangle"].astype(int),
            }

    elif version == "dune_adaptive":
        gridsize = [int(j * h / h_max) for j in initial_gridsize]
        domain = cartesianDomain(*domain_range, gridsize)

    elif version == "gmsh_adaptive":
        # in this version we need to adapt the epsilon since using the
        # coarse grid h is not really useful
        if pygmsh is None:
            raise AttributeError("'gmsh_adaptive' requires install pygmsh")
        with pygmsh.occ.Geometry() as geom:
            geom.characteristic_length_max = h_max
            geom.characteristic_length_min = h_min

            geom.add_rectangle(
                [domain_range[0][0], domain_range[0][1], 0.0],
                domain_range[1][0] - domain_range[0][0],
                domain_range[1][1] - domain_range[0][1],
            )

            geom.set_mesh_size_callback(
                lambda dim, tag, x, y, z, lc: spacing(x, y, omega.epsilon),
                ignore_other_mesh_sizes=True,
            )
            mesh = geom.generate_mesh()
            points, cells = mesh.points, mesh.cells_dict
            domain = {
                "vertices": points[:, :2].astype(float),
                "simplices": cells["triangle"].astype(int),
            }
    else:
        raise ValueError("invalid mesh type")

    if not version == "dune_adaptive":
        gridView = GridView(domain)
    else:
        refinements = int(2 * np.log2(h_max / h_min))
        gridView = GridView(domain,omega,
                      factor=radius,
                      refinements=refinements,
                      adaptLevels=adaptLevels)
        h_min = h_max * 0.5 ** (refinements / 2)
        omega.epsilon.value = get_eps(h_min)

    domain = DomainDune(omega, gridView)

    print(
        f"h_max={h_max}, h_min={h_min * 0.5 ** (adaptLevels / 2)}, epsilon={omega.epsilon.value}"
    )

    return gridView, domain
