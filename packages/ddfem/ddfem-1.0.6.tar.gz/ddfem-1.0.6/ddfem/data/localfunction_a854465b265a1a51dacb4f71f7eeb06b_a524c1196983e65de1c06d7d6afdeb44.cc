#ifndef GUARD_a854465b265a1a51dacb4f71f7eeb06b
#define GUARD_a854465b265a1a51dacb4f71f7eeb06b

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

namespace UFLLocalFunctions_a854465b265a1a51dacb4f71f7eeb06b
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
    using std::tanh;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp2 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp3 = tmp2 + tmp1;
    const auto tmp4 = 1e-10 + tmp3;
    const auto tmp5 = std::sqrt( tmp4 );
    const auto tmp6 = -1 + tmp5;
    const auto tmp7 = 3 * tmp6;
    const auto tmp8 = tmp7 / 0.225;
    const auto tmp9 = std::tanh( tmp8 );
    const auto tmp10 = -1 * tmp9;
    const auto tmp11 = 1 + tmp10;
    const auto tmp12 = 0.5 * tmp11;
    result[ 0 ] = tmp12;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::cosh;
    using std::pow;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp2 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp3 = tmp2 + tmp1;
    const auto tmp4 = 1e-10 + tmp3;
    const auto tmp5 = std::sqrt( tmp4 );
    const auto tmp6 = -1 + tmp5;
    const auto tmp7 = 3 * tmp6;
    const auto tmp8 = tmp7 / 0.225;
    const auto tmp9 = 2.0 * tmp8;
    const auto tmp10 = std::cosh( tmp9 );
    const auto tmp11 = 1.0 + tmp10;
    const auto tmp12 = std::cosh( tmp8 );
    const auto tmp13 = 2.0 * tmp12;
    const auto tmp14 = tmp13 / tmp11;
    const auto tmp15 = std::pow( tmp14, 2 );
    const auto tmp16 = 2 * tmp5;
    const auto tmp17 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp18 = tmp17 / tmp16;
    const auto tmp19 = 3 * tmp18;
    const auto tmp20 = tmp19 / 0.225;
    const auto tmp21 = tmp20 * tmp15;
    const auto tmp22 = -1 * tmp21;
    const auto tmp23 = 0.5 * tmp22;
    const auto tmp24 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp25 = tmp24 / tmp16;
    const auto tmp26 = 3 * tmp25;
    const auto tmp27 = tmp26 / 0.225;
    const auto tmp28 = tmp27 * tmp15;
    const auto tmp29 = -1 * tmp28;
    const auto tmp30 = 0.5 * tmp29;
    (result[ 0 ])[ 0 ] = tmp23;
    (result[ 0 ])[ 1 ] = tmp30;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::cosh;
    using std::pow;
    using std::sinh;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp2 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp3 = tmp2 + tmp1;
    const auto tmp4 = 1e-10 + tmp3;
    const auto tmp5 = std::sqrt( tmp4 );
    const auto tmp6 = -1 + tmp5;
    const auto tmp7 = 3 * tmp6;
    const auto tmp8 = tmp7 / 0.225;
    const auto tmp9 = 2.0 * tmp8;
    const auto tmp10 = std::cosh( tmp9 );
    const auto tmp11 = 1.0 + tmp10;
    const auto tmp12 = std::cosh( tmp8 );
    const auto tmp13 = 2.0 * tmp12;
    const auto tmp14 = tmp13 / tmp11;
    const auto tmp15 = std::pow( tmp14, 2 );
    const auto tmp16 = 2 * tmp5;
    const auto tmp17 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp18 = tmp17 / tmp16;
    const auto tmp19 = 2 * tmp18;
    const auto tmp20 = tmp19 * tmp18;
    const auto tmp21 = -1 * tmp20;
    const auto tmp22 = 2 + tmp21;
    const auto tmp23 = tmp22 / tmp16;
    const auto tmp24 = 3 * tmp23;
    const auto tmp25 = tmp24 / 0.225;
    const auto tmp26 = tmp25 * tmp15;
    const auto tmp27 = 3 * tmp18;
    const auto tmp28 = tmp27 / 0.225;
    const auto tmp29 = std::sinh( tmp8 );
    const auto tmp30 = tmp28 * tmp29;
    const auto tmp31 = 2.0 * tmp30;
    const auto tmp32 = std::sinh( tmp9 );
    const auto tmp33 = 2.0 * tmp28;
    const auto tmp34 = tmp33 * tmp32;
    const auto tmp35 = tmp34 * tmp14;
    const auto tmp36 = -1 * tmp35;
    const auto tmp37 = tmp36 + tmp31;
    const auto tmp38 = tmp37 / tmp11;
    const auto tmp39 = 2 * tmp38;
    const auto tmp40 = tmp39 * tmp14;
    const auto tmp41 = tmp40 * tmp28;
    const auto tmp42 = tmp41 + tmp26;
    const auto tmp43 = -1 * tmp42;
    const auto tmp44 = 0.5 * tmp43;
    const auto tmp45 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp46 = tmp45 / tmp16;
    const auto tmp47 = 2 * tmp46;
    const auto tmp48 = tmp47 * tmp18;
    const auto tmp49 = -1 * tmp48;
    const auto tmp50 = tmp49 / tmp16;
    const auto tmp51 = 3 * tmp50;
    const auto tmp52 = tmp51 / 0.225;
    const auto tmp53 = tmp52 * tmp15;
    const auto tmp54 = 3 * tmp46;
    const auto tmp55 = tmp54 / 0.225;
    const auto tmp56 = tmp55 * tmp29;
    const auto tmp57 = 2.0 * tmp56;
    const auto tmp58 = 2.0 * tmp55;
    const auto tmp59 = tmp58 * tmp32;
    const auto tmp60 = tmp59 * tmp14;
    const auto tmp61 = -1 * tmp60;
    const auto tmp62 = tmp61 + tmp57;
    const auto tmp63 = tmp62 / tmp11;
    const auto tmp64 = 2 * tmp63;
    const auto tmp65 = tmp64 * tmp14;
    const auto tmp66 = tmp65 * tmp28;
    const auto tmp67 = tmp66 + tmp53;
    const auto tmp68 = -1 * tmp67;
    const auto tmp69 = 0.5 * tmp68;
    const auto tmp70 = tmp19 * tmp46;
    const auto tmp71 = -1 * tmp70;
    const auto tmp72 = tmp71 / tmp16;
    const auto tmp73 = 3 * tmp72;
    const auto tmp74 = tmp73 / 0.225;
    const auto tmp75 = tmp74 * tmp15;
    const auto tmp76 = tmp40 * tmp55;
    const auto tmp77 = tmp76 + tmp75;
    const auto tmp78 = -1 * tmp77;
    const auto tmp79 = 0.5 * tmp78;
    const auto tmp80 = tmp47 * tmp46;
    const auto tmp81 = -1 * tmp80;
    const auto tmp82 = 2 + tmp81;
    const auto tmp83 = tmp82 / tmp16;
    const auto tmp84 = 3 * tmp83;
    const auto tmp85 = tmp84 / 0.225;
    const auto tmp86 = tmp85 * tmp15;
    const auto tmp87 = tmp65 * tmp55;
    const auto tmp88 = tmp87 + tmp86;
    const auto tmp89 = -1 * tmp88;
    const auto tmp90 = 0.5 * tmp89;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp44;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp69;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp79;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp90;
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

} // namespace UFLLocalFunctions_a854465b265a1a51dacb4f71f7eeb06b

PYBIND11_MODULE( localfunction_a854465b265a1a51dacb4f71f7eeb06b_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef UFLLocalFunctions_a854465b265a1a51dacb4f71f7eeb06b::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_a854465b265a1a51dacb4f71f7eeb06b::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_a854465b265a1a51dacb4f71f7eeb06b_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
