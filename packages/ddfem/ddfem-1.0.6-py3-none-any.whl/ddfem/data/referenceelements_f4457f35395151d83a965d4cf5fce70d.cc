#ifndef Guard_referenceelements_f4457f35395151d83a965d4cf5fce70d
#define Guard_referenceelements_f4457f35395151d83a965d4cf5fce70d

#include <config.h>

#define USING_DUNE_PYTHON 1

#include <dune/python/geometry/referenceelements.hh>

#include <dune/python/common/typeregistry.hh>
#include <dune/python/pybind11/pybind11.h>
#include <dune/python/pybind11/stl.h>

PYBIND11_MODULE( referenceelements_f4457f35395151d83a965d4cf5fce70d, module )
{
  using pybind11::operator""_a;
  pybind11::module cls0 = module;
  {
    using DuneType = Dune::Geo::ReferenceElement<Dune::Geo::ReferenceElementImplementation<double,2> >;
    auto cls = Dune::Python::insertClass< DuneType >( cls0, "ReferenceElements", Dune::Python::GenerateTypeName("Dune::Geo::ReferenceElement<Dune::Geo::ReferenceElementImplementation<double,2> >"), Dune::Python::IncludeFiles{"dune/python/geometry/referenceelements.hh"}).first;
    Dune::Python::registerReferenceElements( cls0, cls );
  }
}
#endif