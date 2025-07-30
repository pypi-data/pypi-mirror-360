#ifndef GUARD_a46a988b5d8571e80fd401a36d7341b7
#define GUARD_a46a988b5d8571e80fd401a36d7341b7

#define USING_DUNE_PYTHON 1
#include <config.h>
#include <dune/alugrid/dgf.hh>
#include <dune/alugrid/grid.hh>
#include <dune/fem/gridpart/adaptiveleafgridpart.hh>
#include <dune/fem/gridpart/filter/simple.hh>
#include <dune/fem/gridpart/filteredgridpart.hh>
#include <dune/fempy/py/gridview.hh>
#include <dune/python/grid/gridview.hh>
#include <dune/python/grid/hierarchical.hh>
#include <dune/fem/function/localfunction/bindable.hh>
#include <dune/fem/common/intersectionside.hh>
#include <dune/python/pybind11/pybind11.h>
#include <dune/python/pybind11/extensions.h>
#include <dune/fempy/py/grid/gridpart.hh>
#include <dune/common/exceptions.hh>
#include <dune/fempy/py/ufllocalfunction.hh>

namespace UFLLocalFunctions_a46a988b5d8571e80fd401a36d7341b7
{

  // UFLLocalFunction
// ----------------

template< class GridPart >
struct UFLLocalFunction
  : public Dune::Fem::BindableGridFunctionWithSpace<GridPart,Dune::Dim<1>>
{
  typedef GridPart GridPartType;
  typedef typename GridPartType::GridViewType GridView;
  typedef typename GridView::ctype ctype;
  typedef Dune::Fem::BindableGridFunctionWithSpace<GridPart,Dune::Dim<1>> BaseType;
  typedef Dune::Fem::GridFunctionSpace<GridPartType,Dune::Dim<1>> FunctionSpaceType;
  typedef typename GridPartType::template Codim< 0 >::EntityType EntityType;
  typedef typename GridPartType::IntersectionType IntersectionType;
  typedef typename EntityType::Geometry Geometry;
  typedef typename Geometry::GlobalCoordinate GlobalCoordinateType;
  typedef Dune::Fem::IntersectionSide Side;
  typedef std::tuple<> ConstantTupleType;
  typedef std::tuple<> CoefficientTupleType;
  static constexpr bool gridPartValid = true;
  template< std::size_t i >
  using CoefficientType = std::tuple_element_t< i, CoefficientTupleType >;
  template< std::size_t i >
  using ConstantType = typename std::tuple_element_t< i, ConstantTupleType >::element_type;
  using BaseType::entity;
  using BaseType::geometry;

  UFLLocalFunction ( const GridPartType &gridPart, const std::string &name, int order, const Dune::Fem::ParameterReader &parameter = Dune::Fem::Parameter::container() )
    : BaseType(gridPart,name,order)
  {}

  void bind ( const IntersectionType &intersection, Side side )
  {
    BaseType::bind(intersection, side);
  }

  void bind ( const EntityType &entity )
  {
    BaseType::bind(entity);
  }

  void unbind ()
  {
    BaseType::unbind();
  }

  template< class Point >
  void evaluate ( const Point &x, typename FunctionSpaceType::RangeType &result ) const
  {
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp2 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp3 = tmp2 + tmp1;
    const auto tmp4 = 1e-10 + tmp3;
    const auto tmp5 = std::sqrt( tmp4 );
    const auto tmp6 = -1 + tmp5;
    result[ 0 ] = tmp6;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp2 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp3 = tmp2 + tmp1;
    const auto tmp4 = 1e-10 + tmp3;
    const auto tmp5 = std::sqrt( tmp4 );
    const auto tmp6 = 2 * tmp5;
    const auto tmp7 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp8 = tmp7 / tmp6;
    const auto tmp9 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp10 = tmp9 / tmp6;
    (result[ 0 ])[ 0 ] = tmp8;
    (result[ 0 ])[ 1 ] = tmp10;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp2 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp3 = tmp2 + tmp1;
    const auto tmp4 = 1e-10 + tmp3;
    const auto tmp5 = std::sqrt( tmp4 );
    const auto tmp6 = 2 * tmp5;
    const auto tmp7 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp8 = tmp7 / tmp6;
    const auto tmp9 = 2 * tmp8;
    const auto tmp10 = tmp9 * tmp8;
    const auto tmp11 = -1 * tmp10;
    const auto tmp12 = 2 + tmp11;
    const auto tmp13 = tmp12 / tmp6;
    const auto tmp14 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp15 = tmp14 / tmp6;
    const auto tmp16 = 2 * tmp15;
    const auto tmp17 = tmp16 * tmp8;
    const auto tmp18 = -1 * tmp17;
    const auto tmp19 = tmp18 / tmp6;
    const auto tmp20 = tmp9 * tmp15;
    const auto tmp21 = -1 * tmp20;
    const auto tmp22 = tmp21 / tmp6;
    const auto tmp23 = tmp16 * tmp15;
    const auto tmp24 = -1 * tmp23;
    const auto tmp25 = 2 + tmp24;
    const auto tmp26 = tmp25 / tmp6;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp13;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp19;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp22;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp26;
  }

  template< std::size_t i >
  const ConstantType< i > &constant () const
  {
    return *std::get< i >( constants_ );
  }

  template< std::size_t i >
  ConstantType< i > &constant ()
  {
    return *std::get< i >( constants_ );
  }
  ConstantTupleType constants_;
  std::tuple<  > coefficients_;
};

} // namespace UFLLocalFunctions_a46a988b5d8571e80fd401a36d7341b7

PYBIND11_MODULE( localfunction_a46a988b5d8571e80fd401a36d7341b7_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef UFLLocalFunctions_a46a988b5d8571e80fd401a36d7341b7::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_a46a988b5d8571e80fd401a36d7341b7::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_a46a988b5d8571e80fd401a36d7341b7_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
