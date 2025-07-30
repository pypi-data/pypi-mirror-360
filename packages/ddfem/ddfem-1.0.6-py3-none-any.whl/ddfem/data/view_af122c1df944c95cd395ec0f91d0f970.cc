#ifndef Guard_view_af122c1df944c95cd395ec0f91d0f970
#define Guard_view_af122c1df944c95cd395ec0f91d0f970

#include <config.h>

#define USING_DUNE_PYTHON 1

#include <dune/alugrid/dgf.hh>
#include <dune/alugrid/grid.hh>
#include <dune/fem/gridpart/adaptiveleafgridpart.hh>
#include <dune/fempy/py/gridview.hh>
#include <dune/python/grid/gridview.hh>
#include <dune/python/grid/hierarchical.hh>

#include <dune/python/common/typeregistry.hh>
#include <dune/python/pybind11/pybind11.h>
#include <dune/python/pybind11/stl.h>

PYBIND11_MODULE( view_af122c1df944c95cd395ec0f91d0f970, module )
{
  using pybind11::operator""_a;
  pybind11::module cls0 = module;
  {
    using DuneType = Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > >;
    auto cls = Dune::Python::insertClass< DuneType >( cls0, "GridView",pybind11::dynamic_attr(), Dune::Python::GenerateTypeName("Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > >"), Dune::Python::IncludeFiles{"dune/alugrid/dgf.hh","dune/alugrid/grid.hh","dune/fem/gridpart/adaptiveleafgridpart.hh","dune/fempy/py/gridview.hh","dune/python/grid/gridview.hh","dune/python/grid/hierarchical.hh"}).first;
    Dune::Python::registerGridView( cls0, cls );
    
    Dune::FemPy::registerGridView ( cls );
    cls.def( pybind11::pickle(
      [](const pybind11::object &self) {
    
                auto& gv = self.cast<DuneType&>();
                std::ostringstream stream;
                Dune::Fem::StandardOutStream outStream(stream);
                gv.indexSet().write( outStream );
                pybind11::bytes s(stream.str());
                /* Return a tuple that fully encodes the state of the object */
                pybind11::dict d;
                if (pybind11::hasattr(self, "__dict__")) {
                  d = self.attr("__dict__");
                }
                return pybind11::make_tuple(gv.grid(),s,d);
          }
    , [](pybind11::tuple t) {
    
                if (t.size() != 3)
                    throw std::runtime_error("Invalid state in AdaptGV with "+std::to_string(t.size())+"arguments!");
                pybind11::handle pyHg = t[0];
                auto& hg = pyHg.cast<typename DuneType::GridType&>();
                /* Create a new C++ instance */
                DuneType* gv = new DuneType(hg);
                pybind11::bytes state(t[1]);
                std::istringstream stream( state );
                Dune::Fem::StandardInStream inStream(stream);
                gv->indexSet().read( inStream );
                auto py_state = t[2].cast<pybind11::dict>();
                return std::make_pair(gv, py_state);
          }
    ), pybind11::keep_alive<1,2>(), pybind11::prepend() );
  }
}
#endif