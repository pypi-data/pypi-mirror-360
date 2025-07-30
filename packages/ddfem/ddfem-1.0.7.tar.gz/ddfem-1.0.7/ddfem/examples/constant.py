from dune.ufl import Constant
from ufl import as_vector, conditional, div, dot, exp, grad, inner, sqrt, outer, zero
import ufl
from ddfem.boundary import AFluxBC, DFluxBC, ValueBC

def CModel(inverted):
    withAdv = False

    class Model:
        dimRange = 1
        stabFactor = Constant(1)

        def initial(x):
            return 2

        def exact(t, x):
            return as_vector((2+x[0]-x[0],))   # better way of avoiding 'Cannot determine geometric dimension from expression'

        def K(U, DU):
            return 1e-2

        def F_v(t, x, U, DU):
            return Model.K(U, DU) * DU

        if withAdv:
            def F_c(t, x, U):
                return outer(U, as_vector([-2,0.5]) )
  
        if withAdv:
            bndFlux = [ AFluxBC( lambda t,x,U,n: Model.F_c(t,x,U)*n ),
                        DFluxBC( lambda t,x,U,DU,n: Model.F_v(t,x,U,DU)*n ) ]
        else:
            # this works: bndFlux = DFluxBC( lambda t,x,U,DU,n: zero(U.ufl_shape)
            bndFlux = DFluxBC( lambda t,x,U,DU,n: Model.F_v(t,x,U,DU)*n )
        boundary = {
            # "full": ValueBC( lambda t,x,U: as_vector([2.]) ),
            "full": bndFlux
            # "sides": ValueBC( lambda t,x,U: as_vector([2.]) ),
            # "ends": [AFluxBC( lambda t,x,U,n: Model.F_c(t,x,U)*n ),
            #          DFluxBC( lambda t,x,U,DU,n: Model.F_v(t,x,U,DU)*n )]
        }

        if inverted:
            boundary[range(1,5)] = ValueBC( lambda t,x,U: as_vector([2.]) )

    return Model
