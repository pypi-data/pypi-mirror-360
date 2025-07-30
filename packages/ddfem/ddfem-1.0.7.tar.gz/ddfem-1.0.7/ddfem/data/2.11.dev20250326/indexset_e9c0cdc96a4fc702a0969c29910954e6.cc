#ifndef Guard_indexset_e9c0cdc96a4fc702a0969c29910954e6
#define Guard_indexset_e9c0cdc96a4fc702a0969c29910954e6

#include <config.h>

#define USING_DUNE_PYTHON 1

#include <dune/alugrid/dgf.hh>
#include <dune/alugrid/grid.hh>
#include <dune/fem/gridpart/adaptiveleafgridpart.hh>
#include <dune/fem/gridpart/filter/simple.hh>
#include <dune/fem/gridpart/filteredgridpart.hh>
#include <dune/fempy/py/gridview.hh>
#include <dune/python/grid/gridview.hh>
#include <dune/python/grid/hierarchical.hh>
#include <dune/python/grid/indexset.hh>

#include <dune/python/common/typeregistry.hh>
#include <dune/python/pybind11/pybind11.h>
#include <dune/python/pybind11/stl.h>

PYBIND11_MODULE( indexset_e9c0cdc96a4fc702a0969c29910954e6, module )
{
  using pybind11::operator""_a;
  pybind11::module cls0 = module;
  {
    using DuneType = Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >::IndexSet;
    auto cls = Dune::Python::insertClass< DuneType >( cls0, "GridViewIndexSet", Dune::Python::GenerateTypeName("Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >::IndexSet"), Dune::Python::IncludeFiles{"dune/alugrid/dgf.hh","dune/alugrid/grid.hh","dune/fem/gridpart/adaptiveleafgridpart.hh","dune/fem/gridpart/filter/simple.hh","dune/fem/gridpart/filteredgridpart.hh","dune/fempy/py/gridview.hh","dune/python/grid/gridview.hh","dune/python/grid/hierarchical.hh","dune/python/grid/indexset.hh"}).first;
    Dune::Python::registerGridViewIndexSet( cls0, cls );
  }
}
#endif