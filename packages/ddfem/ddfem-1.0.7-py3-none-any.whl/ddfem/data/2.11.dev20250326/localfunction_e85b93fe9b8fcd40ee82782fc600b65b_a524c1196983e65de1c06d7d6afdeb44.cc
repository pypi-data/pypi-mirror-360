#ifndef GUARD_e85b93fe9b8fcd40ee82782fc600b65b
#define GUARD_e85b93fe9b8fcd40ee82782fc600b65b

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

namespace UFLLocalFunctions_e85b93fe9b8fcd40ee82782fc600b65b
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
    using std::max;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -0.8 + tmp0[ 1 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -0.5 + tmp6;
    const auto tmp8 = -1 * tmp7;
    const auto tmp9 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp10 = tmp3 + tmp9;
    const auto tmp11 = 1e-10 + tmp10;
    const auto tmp12 = std::sqrt( tmp11 );
    const auto tmp13 = -1 + tmp12;
    const auto tmp14 = std::max( tmp13, tmp8 );
    result[ 0 ] = tmp14;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -0.8 + tmp0[ 1 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -0.5 + tmp6;
    const auto tmp8 = -1 * tmp7;
    const auto tmp9 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp10 = tmp3 + tmp9;
    const auto tmp11 = 1e-10 + tmp10;
    const auto tmp12 = std::sqrt( tmp11 );
    const auto tmp13 = -1 + tmp12;
    const auto tmp14 = 2 * tmp12;
    const auto tmp15 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp16 = tmp15 / tmp14;
    const auto tmp17 = tmp16 * (tmp13 > tmp8 ? 1 : 0.0);
    const auto tmp18 = 2 * tmp6;
    const auto tmp19 = tmp15 / tmp18;
    const auto tmp20 = -1 * tmp19;
    const auto tmp21 = -1 * (tmp13 > tmp8 ? 1 : 0.0);
    const auto tmp22 = 1.0 + tmp21;
    const auto tmp23 = tmp22 * tmp20;
    const auto tmp24 = tmp23 + tmp17;
    const auto tmp25 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp26 = tmp25 / tmp14;
    const auto tmp27 = tmp26 * (tmp13 > tmp8 ? 1 : 0.0);
    const auto tmp28 = tmp1 + tmp1;
    const auto tmp29 = tmp28 / tmp18;
    const auto tmp30 = -1 * tmp29;
    const auto tmp31 = tmp22 * tmp30;
    const auto tmp32 = tmp31 + tmp27;
    (result[ 0 ])[ 0 ] = tmp24;
    (result[ 0 ])[ 1 ] = tmp32;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -0.8 + tmp0[ 1 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -0.5 + tmp6;
    const auto tmp8 = -1 * tmp7;
    const auto tmp9 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp10 = tmp3 + tmp9;
    const auto tmp11 = 1e-10 + tmp10;
    const auto tmp12 = std::sqrt( tmp11 );
    const auto tmp13 = -1 + tmp12;
    const auto tmp14 = 2 * tmp12;
    const auto tmp15 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp16 = tmp15 / tmp14;
    const auto tmp17 = 2 * tmp16;
    const auto tmp18 = tmp17 * tmp16;
    const auto tmp19 = -1 * tmp18;
    const auto tmp20 = 2 + tmp19;
    const auto tmp21 = tmp20 / tmp14;
    const auto tmp22 = tmp21 * (tmp13 > tmp8 ? 1 : 0.0);
    const auto tmp23 = 2 * tmp6;
    const auto tmp24 = tmp15 / tmp23;
    const auto tmp25 = 2 * tmp24;
    const auto tmp26 = tmp25 * tmp24;
    const auto tmp27 = -1 * tmp26;
    const auto tmp28 = 2 + tmp27;
    const auto tmp29 = tmp28 / tmp23;
    const auto tmp30 = -1 * tmp29;
    const auto tmp31 = -1 * (tmp13 > tmp8 ? 1 : 0.0);
    const auto tmp32 = 1.0 + tmp31;
    const auto tmp33 = tmp32 * tmp30;
    const auto tmp34 = tmp33 + tmp22;
    const auto tmp35 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp36 = tmp35 / tmp14;
    const auto tmp37 = 2 * tmp36;
    const auto tmp38 = tmp37 * tmp16;
    const auto tmp39 = -1 * tmp38;
    const auto tmp40 = tmp39 / tmp14;
    const auto tmp41 = tmp40 * (tmp13 > tmp8 ? 1 : 0.0);
    const auto tmp42 = tmp1 + tmp1;
    const auto tmp43 = tmp42 / tmp23;
    const auto tmp44 = 2 * tmp43;
    const auto tmp45 = tmp44 * tmp24;
    const auto tmp46 = -1 * tmp45;
    const auto tmp47 = tmp46 / tmp23;
    const auto tmp48 = -1 * tmp47;
    const auto tmp49 = tmp32 * tmp48;
    const auto tmp50 = tmp49 + tmp41;
    const auto tmp51 = tmp17 * tmp36;
    const auto tmp52 = -1 * tmp51;
    const auto tmp53 = tmp52 / tmp14;
    const auto tmp54 = tmp53 * (tmp13 > tmp8 ? 1 : 0.0);
    const auto tmp55 = tmp25 * tmp43;
    const auto tmp56 = -1 * tmp55;
    const auto tmp57 = tmp56 / tmp23;
    const auto tmp58 = -1 * tmp57;
    const auto tmp59 = tmp32 * tmp58;
    const auto tmp60 = tmp59 + tmp54;
    const auto tmp61 = tmp37 * tmp36;
    const auto tmp62 = -1 * tmp61;
    const auto tmp63 = 2 + tmp62;
    const auto tmp64 = tmp63 / tmp14;
    const auto tmp65 = tmp64 * (tmp13 > tmp8 ? 1 : 0.0);
    const auto tmp66 = tmp44 * tmp43;
    const auto tmp67 = -1 * tmp66;
    const auto tmp68 = 2 + tmp67;
    const auto tmp69 = tmp68 / tmp23;
    const auto tmp70 = -1 * tmp69;
    const auto tmp71 = tmp32 * tmp70;
    const auto tmp72 = tmp71 + tmp65;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp34;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp50;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp60;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp72;
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

} // namespace UFLLocalFunctions_e85b93fe9b8fcd40ee82782fc600b65b

PYBIND11_MODULE( localfunction_e85b93fe9b8fcd40ee82782fc600b65b_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef UFLLocalFunctions_e85b93fe9b8fcd40ee82782fc600b65b::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_e85b93fe9b8fcd40ee82782fc600b65b::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_e85b93fe9b8fcd40ee82782fc600b65b_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
