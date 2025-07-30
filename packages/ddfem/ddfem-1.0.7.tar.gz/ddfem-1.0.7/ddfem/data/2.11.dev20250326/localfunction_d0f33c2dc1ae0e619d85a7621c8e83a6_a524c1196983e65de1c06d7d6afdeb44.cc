#ifndef GUARD_d0f33c2dc1ae0e619d85a7621c8e83a6
#define GUARD_d0f33c2dc1ae0e619d85a7621c8e83a6

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

namespace UFLLocalFunctions_d0f33c2dc1ae0e619d85a7621c8e83a6
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
    const auto tmp1 = 0.8 + tmp0[ 1 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -0.5 + tmp6;
    const auto tmp8 = -1 * tmp7;
    const auto tmp9 = -0.8 + tmp0[ 1 ];
    const auto tmp10 = tmp9 * tmp9;
    const auto tmp11 = tmp3 + tmp10;
    const auto tmp12 = 1e-10 + tmp11;
    const auto tmp13 = std::sqrt( tmp12 );
    const auto tmp14 = -0.5 + tmp13;
    const auto tmp15 = -1 * tmp14;
    const auto tmp16 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp17 = tmp3 + tmp16;
    const auto tmp18 = 1e-10 + tmp17;
    const auto tmp19 = std::sqrt( tmp18 );
    const auto tmp20 = -1 + tmp19;
    const auto tmp21 = std::max( tmp20, tmp15 );
    const auto tmp22 = std::max( tmp21, tmp8 );
    result[ 0 ] = tmp22;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::max;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = 0.8 + tmp0[ 1 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -0.5 + tmp6;
    const auto tmp8 = -1 * tmp7;
    const auto tmp9 = -0.8 + tmp0[ 1 ];
    const auto tmp10 = tmp9 * tmp9;
    const auto tmp11 = tmp3 + tmp10;
    const auto tmp12 = 1e-10 + tmp11;
    const auto tmp13 = std::sqrt( tmp12 );
    const auto tmp14 = -0.5 + tmp13;
    const auto tmp15 = -1 * tmp14;
    const auto tmp16 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp17 = tmp3 + tmp16;
    const auto tmp18 = 1e-10 + tmp17;
    const auto tmp19 = std::sqrt( tmp18 );
    const auto tmp20 = -1 + tmp19;
    const auto tmp21 = std::max( tmp20, tmp15 );
    const auto tmp22 = 2 * tmp19;
    const auto tmp23 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp24 = tmp23 / tmp22;
    const auto tmp25 = tmp24 * (tmp20 > tmp15 ? 1 : 0.0);
    const auto tmp26 = 2 * tmp13;
    const auto tmp27 = tmp23 / tmp26;
    const auto tmp28 = -1 * tmp27;
    const auto tmp29 = -1 * (tmp20 > tmp15 ? 1 : 0.0);
    const auto tmp30 = 1.0 + tmp29;
    const auto tmp31 = tmp30 * tmp28;
    const auto tmp32 = tmp31 + tmp25;
    const auto tmp33 = tmp32 * (tmp21 > tmp8 ? 1 : 0.0);
    const auto tmp34 = 2 * tmp6;
    const auto tmp35 = tmp23 / tmp34;
    const auto tmp36 = -1 * tmp35;
    const auto tmp37 = -1 * (tmp21 > tmp8 ? 1 : 0.0);
    const auto tmp38 = 1.0 + tmp37;
    const auto tmp39 = tmp38 * tmp36;
    const auto tmp40 = tmp39 + tmp33;
    const auto tmp41 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp42 = tmp41 / tmp22;
    const auto tmp43 = tmp42 * (tmp20 > tmp15 ? 1 : 0.0);
    const auto tmp44 = tmp9 + tmp9;
    const auto tmp45 = tmp44 / tmp26;
    const auto tmp46 = -1 * tmp45;
    const auto tmp47 = tmp30 * tmp46;
    const auto tmp48 = tmp47 + tmp43;
    const auto tmp49 = tmp48 * (tmp21 > tmp8 ? 1 : 0.0);
    const auto tmp50 = tmp1 + tmp1;
    const auto tmp51 = tmp50 / tmp34;
    const auto tmp52 = -1 * tmp51;
    const auto tmp53 = tmp38 * tmp52;
    const auto tmp54 = tmp53 + tmp49;
    (result[ 0 ])[ 0 ] = tmp40;
    (result[ 0 ])[ 1 ] = tmp54;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::max;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = 0.8 + tmp0[ 1 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -0.5 + tmp6;
    const auto tmp8 = -1 * tmp7;
    const auto tmp9 = -0.8 + tmp0[ 1 ];
    const auto tmp10 = tmp9 * tmp9;
    const auto tmp11 = tmp3 + tmp10;
    const auto tmp12 = 1e-10 + tmp11;
    const auto tmp13 = std::sqrt( tmp12 );
    const auto tmp14 = -0.5 + tmp13;
    const auto tmp15 = -1 * tmp14;
    const auto tmp16 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp17 = tmp3 + tmp16;
    const auto tmp18 = 1e-10 + tmp17;
    const auto tmp19 = std::sqrt( tmp18 );
    const auto tmp20 = -1 + tmp19;
    const auto tmp21 = std::max( tmp20, tmp15 );
    const auto tmp22 = 2 * tmp19;
    const auto tmp23 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp24 = tmp23 / tmp22;
    const auto tmp25 = 2 * tmp24;
    const auto tmp26 = tmp25 * tmp24;
    const auto tmp27 = -1 * tmp26;
    const auto tmp28 = 2 + tmp27;
    const auto tmp29 = tmp28 / tmp22;
    const auto tmp30 = tmp29 * (tmp20 > tmp15 ? 1 : 0.0);
    const auto tmp31 = 2 * tmp13;
    const auto tmp32 = tmp23 / tmp31;
    const auto tmp33 = 2 * tmp32;
    const auto tmp34 = tmp33 * tmp32;
    const auto tmp35 = -1 * tmp34;
    const auto tmp36 = 2 + tmp35;
    const auto tmp37 = tmp36 / tmp31;
    const auto tmp38 = -1 * tmp37;
    const auto tmp39 = -1 * (tmp20 > tmp15 ? 1 : 0.0);
    const auto tmp40 = 1.0 + tmp39;
    const auto tmp41 = tmp40 * tmp38;
    const auto tmp42 = tmp41 + tmp30;
    const auto tmp43 = tmp42 * (tmp21 > tmp8 ? 1 : 0.0);
    const auto tmp44 = 2 * tmp6;
    const auto tmp45 = tmp23 / tmp44;
    const auto tmp46 = 2 * tmp45;
    const auto tmp47 = tmp46 * tmp45;
    const auto tmp48 = -1 * tmp47;
    const auto tmp49 = 2 + tmp48;
    const auto tmp50 = tmp49 / tmp44;
    const auto tmp51 = -1 * tmp50;
    const auto tmp52 = -1 * (tmp21 > tmp8 ? 1 : 0.0);
    const auto tmp53 = 1.0 + tmp52;
    const auto tmp54 = tmp53 * tmp51;
    const auto tmp55 = tmp54 + tmp43;
    const auto tmp56 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp57 = tmp56 / tmp22;
    const auto tmp58 = 2 * tmp57;
    const auto tmp59 = tmp58 * tmp24;
    const auto tmp60 = -1 * tmp59;
    const auto tmp61 = tmp60 / tmp22;
    const auto tmp62 = tmp61 * (tmp20 > tmp15 ? 1 : 0.0);
    const auto tmp63 = tmp9 + tmp9;
    const auto tmp64 = tmp63 / tmp31;
    const auto tmp65 = 2 * tmp64;
    const auto tmp66 = tmp65 * tmp32;
    const auto tmp67 = -1 * tmp66;
    const auto tmp68 = tmp67 / tmp31;
    const auto tmp69 = -1 * tmp68;
    const auto tmp70 = tmp40 * tmp69;
    const auto tmp71 = tmp70 + tmp62;
    const auto tmp72 = tmp71 * (tmp21 > tmp8 ? 1 : 0.0);
    const auto tmp73 = tmp1 + tmp1;
    const auto tmp74 = tmp73 / tmp44;
    const auto tmp75 = 2 * tmp74;
    const auto tmp76 = tmp75 * tmp45;
    const auto tmp77 = -1 * tmp76;
    const auto tmp78 = tmp77 / tmp44;
    const auto tmp79 = -1 * tmp78;
    const auto tmp80 = tmp53 * tmp79;
    const auto tmp81 = tmp80 + tmp72;
    const auto tmp82 = tmp25 * tmp57;
    const auto tmp83 = -1 * tmp82;
    const auto tmp84 = tmp83 / tmp22;
    const auto tmp85 = tmp84 * (tmp20 > tmp15 ? 1 : 0.0);
    const auto tmp86 = tmp33 * tmp64;
    const auto tmp87 = -1 * tmp86;
    const auto tmp88 = tmp87 / tmp31;
    const auto tmp89 = -1 * tmp88;
    const auto tmp90 = tmp40 * tmp89;
    const auto tmp91 = tmp90 + tmp85;
    const auto tmp92 = tmp91 * (tmp21 > tmp8 ? 1 : 0.0);
    const auto tmp93 = tmp46 * tmp74;
    const auto tmp94 = -1 * tmp93;
    const auto tmp95 = tmp94 / tmp44;
    const auto tmp96 = -1 * tmp95;
    const auto tmp97 = tmp53 * tmp96;
    const auto tmp98 = tmp97 + tmp92;
    const auto tmp99 = tmp58 * tmp57;
    const auto tmp100 = -1 * tmp99;
    const auto tmp101 = 2 + tmp100;
    const auto tmp102 = tmp101 / tmp22;
    const auto tmp103 = tmp102 * (tmp20 > tmp15 ? 1 : 0.0);
    const auto tmp104 = tmp65 * tmp64;
    const auto tmp105 = -1 * tmp104;
    const auto tmp106 = 2 + tmp105;
    const auto tmp107 = tmp106 / tmp31;
    const auto tmp108 = -1 * tmp107;
    const auto tmp109 = tmp40 * tmp108;
    const auto tmp110 = tmp109 + tmp103;
    const auto tmp111 = tmp110 * (tmp21 > tmp8 ? 1 : 0.0);
    const auto tmp112 = tmp75 * tmp74;
    const auto tmp113 = -1 * tmp112;
    const auto tmp114 = 2 + tmp113;
    const auto tmp115 = tmp114 / tmp44;
    const auto tmp116 = -1 * tmp115;
    const auto tmp117 = tmp53 * tmp116;
    const auto tmp118 = tmp117 + tmp111;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp55;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp81;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp98;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp118;
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

} // namespace UFLLocalFunctions_d0f33c2dc1ae0e619d85a7621c8e83a6

PYBIND11_MODULE( localfunction_d0f33c2dc1ae0e619d85a7621c8e83a6_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef UFLLocalFunctions_d0f33c2dc1ae0e619d85a7621c8e83a6::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_d0f33c2dc1ae0e619d85a7621c8e83a6::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_d0f33c2dc1ae0e619d85a7621c8e83a6_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
