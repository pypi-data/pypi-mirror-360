#ifndef GUARD_0f7b2106478c5d2af781b1f377a180d2
#define GUARD_0f7b2106478c5d2af781b1f377a180d2

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

namespace UFLLocalFunctions_0f7b2106478c5d2af781b1f377a180d2
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
    using std::min;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -1 + tmp0[ 0 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -0.5 + tmp6;
    const auto tmp8 = 0.8 + tmp0[ 1 ];
    const auto tmp9 = tmp8 * tmp8;
    const auto tmp10 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp11 = tmp10 + tmp9;
    const auto tmp12 = 1e-10 + tmp11;
    const auto tmp13 = std::sqrt( tmp12 );
    const auto tmp14 = -0.5 + tmp13;
    const auto tmp15 = -1 * tmp14;
    const auto tmp16 = -0.8 + tmp0[ 1 ];
    const auto tmp17 = tmp16 * tmp16;
    const auto tmp18 = tmp10 + tmp17;
    const auto tmp19 = 1e-10 + tmp18;
    const auto tmp20 = std::sqrt( tmp19 );
    const auto tmp21 = -0.5 + tmp20;
    const auto tmp22 = -1 * tmp21;
    const auto tmp23 = tmp10 + tmp3;
    const auto tmp24 = 1e-10 + tmp23;
    const auto tmp25 = std::sqrt( tmp24 );
    const auto tmp26 = -1 + tmp25;
    const auto tmp27 = std::max( tmp26, tmp22 );
    const auto tmp28 = std::max( tmp27, tmp15 );
    const auto tmp29 = std::min( tmp28, tmp7 );
    result[ 0 ] = tmp29;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::max;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -1 + tmp0[ 0 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -0.5 + tmp6;
    const auto tmp8 = 0.8 + tmp0[ 1 ];
    const auto tmp9 = tmp8 * tmp8;
    const auto tmp10 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp11 = tmp10 + tmp9;
    const auto tmp12 = 1e-10 + tmp11;
    const auto tmp13 = std::sqrt( tmp12 );
    const auto tmp14 = -0.5 + tmp13;
    const auto tmp15 = -1 * tmp14;
    const auto tmp16 = -0.8 + tmp0[ 1 ];
    const auto tmp17 = tmp16 * tmp16;
    const auto tmp18 = tmp10 + tmp17;
    const auto tmp19 = 1e-10 + tmp18;
    const auto tmp20 = std::sqrt( tmp19 );
    const auto tmp21 = -0.5 + tmp20;
    const auto tmp22 = -1 * tmp21;
    const auto tmp23 = tmp10 + tmp3;
    const auto tmp24 = 1e-10 + tmp23;
    const auto tmp25 = std::sqrt( tmp24 );
    const auto tmp26 = -1 + tmp25;
    const auto tmp27 = std::max( tmp26, tmp22 );
    const auto tmp28 = std::max( tmp27, tmp15 );
    const auto tmp29 = 2 * tmp25;
    const auto tmp30 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp31 = tmp30 / tmp29;
    const auto tmp32 = tmp31 * (tmp26 > tmp22 ? 1 : 0.0);
    const auto tmp33 = 2 * tmp20;
    const auto tmp34 = tmp30 / tmp33;
    const auto tmp35 = -1 * tmp34;
    const auto tmp36 = -1 * (tmp26 > tmp22 ? 1 : 0.0);
    const auto tmp37 = 1.0 + tmp36;
    const auto tmp38 = tmp37 * tmp35;
    const auto tmp39 = tmp38 + tmp32;
    const auto tmp40 = tmp39 * (tmp27 > tmp15 ? 1 : 0.0);
    const auto tmp41 = 2 * tmp13;
    const auto tmp42 = tmp30 / tmp41;
    const auto tmp43 = -1 * tmp42;
    const auto tmp44 = -1 * (tmp27 > tmp15 ? 1 : 0.0);
    const auto tmp45 = 1.0 + tmp44;
    const auto tmp46 = tmp45 * tmp43;
    const auto tmp47 = tmp46 + tmp40;
    const auto tmp48 = tmp47 * (tmp28 < tmp7 ? 1 : 0.0);
    const auto tmp49 = 2 * tmp6;
    const auto tmp50 = tmp1 + tmp1;
    const auto tmp51 = tmp50 / tmp49;
    const auto tmp52 = -1 * (tmp28 < tmp7 ? 1 : 0.0);
    const auto tmp53 = 1.0 + tmp52;
    const auto tmp54 = tmp53 * tmp51;
    const auto tmp55 = tmp54 + tmp48;
    const auto tmp56 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp57 = tmp56 / tmp29;
    const auto tmp58 = tmp57 * (tmp26 > tmp22 ? 1 : 0.0);
    const auto tmp59 = tmp16 + tmp16;
    const auto tmp60 = tmp59 / tmp33;
    const auto tmp61 = -1 * tmp60;
    const auto tmp62 = tmp37 * tmp61;
    const auto tmp63 = tmp62 + tmp58;
    const auto tmp64 = tmp63 * (tmp27 > tmp15 ? 1 : 0.0);
    const auto tmp65 = tmp8 + tmp8;
    const auto tmp66 = tmp65 / tmp41;
    const auto tmp67 = -1 * tmp66;
    const auto tmp68 = tmp45 * tmp67;
    const auto tmp69 = tmp68 + tmp64;
    const auto tmp70 = tmp69 * (tmp28 < tmp7 ? 1 : 0.0);
    const auto tmp71 = tmp56 / tmp49;
    const auto tmp72 = tmp53 * tmp71;
    const auto tmp73 = tmp72 + tmp70;
    (result[ 0 ])[ 0 ] = tmp55;
    (result[ 0 ])[ 1 ] = tmp73;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::max;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -1 + tmp0[ 0 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -0.5 + tmp6;
    const auto tmp8 = 0.8 + tmp0[ 1 ];
    const auto tmp9 = tmp8 * tmp8;
    const auto tmp10 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp11 = tmp10 + tmp9;
    const auto tmp12 = 1e-10 + tmp11;
    const auto tmp13 = std::sqrt( tmp12 );
    const auto tmp14 = -0.5 + tmp13;
    const auto tmp15 = -1 * tmp14;
    const auto tmp16 = -0.8 + tmp0[ 1 ];
    const auto tmp17 = tmp16 * tmp16;
    const auto tmp18 = tmp10 + tmp17;
    const auto tmp19 = 1e-10 + tmp18;
    const auto tmp20 = std::sqrt( tmp19 );
    const auto tmp21 = -0.5 + tmp20;
    const auto tmp22 = -1 * tmp21;
    const auto tmp23 = tmp10 + tmp3;
    const auto tmp24 = 1e-10 + tmp23;
    const auto tmp25 = std::sqrt( tmp24 );
    const auto tmp26 = -1 + tmp25;
    const auto tmp27 = std::max( tmp26, tmp22 );
    const auto tmp28 = std::max( tmp27, tmp15 );
    const auto tmp29 = 2 * tmp25;
    const auto tmp30 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp31 = tmp30 / tmp29;
    const auto tmp32 = 2 * tmp31;
    const auto tmp33 = tmp32 * tmp31;
    const auto tmp34 = -1 * tmp33;
    const auto tmp35 = 2 + tmp34;
    const auto tmp36 = tmp35 / tmp29;
    const auto tmp37 = tmp36 * (tmp26 > tmp22 ? 1 : 0.0);
    const auto tmp38 = 2 * tmp20;
    const auto tmp39 = tmp30 / tmp38;
    const auto tmp40 = 2 * tmp39;
    const auto tmp41 = tmp40 * tmp39;
    const auto tmp42 = -1 * tmp41;
    const auto tmp43 = 2 + tmp42;
    const auto tmp44 = tmp43 / tmp38;
    const auto tmp45 = -1 * tmp44;
    const auto tmp46 = -1 * (tmp26 > tmp22 ? 1 : 0.0);
    const auto tmp47 = 1.0 + tmp46;
    const auto tmp48 = tmp47 * tmp45;
    const auto tmp49 = tmp48 + tmp37;
    const auto tmp50 = tmp49 * (tmp27 > tmp15 ? 1 : 0.0);
    const auto tmp51 = 2 * tmp13;
    const auto tmp52 = tmp30 / tmp51;
    const auto tmp53 = 2 * tmp52;
    const auto tmp54 = tmp53 * tmp52;
    const auto tmp55 = -1 * tmp54;
    const auto tmp56 = 2 + tmp55;
    const auto tmp57 = tmp56 / tmp51;
    const auto tmp58 = -1 * tmp57;
    const auto tmp59 = -1 * (tmp27 > tmp15 ? 1 : 0.0);
    const auto tmp60 = 1.0 + tmp59;
    const auto tmp61 = tmp60 * tmp58;
    const auto tmp62 = tmp61 + tmp50;
    const auto tmp63 = tmp62 * (tmp28 < tmp7 ? 1 : 0.0);
    const auto tmp64 = 2 * tmp6;
    const auto tmp65 = tmp1 + tmp1;
    const auto tmp66 = tmp65 / tmp64;
    const auto tmp67 = 2 * tmp66;
    const auto tmp68 = tmp67 * tmp66;
    const auto tmp69 = -1 * tmp68;
    const auto tmp70 = 2 + tmp69;
    const auto tmp71 = tmp70 / tmp64;
    const auto tmp72 = -1 * (tmp28 < tmp7 ? 1 : 0.0);
    const auto tmp73 = 1.0 + tmp72;
    const auto tmp74 = tmp73 * tmp71;
    const auto tmp75 = tmp74 + tmp63;
    const auto tmp76 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp77 = tmp76 / tmp29;
    const auto tmp78 = 2 * tmp77;
    const auto tmp79 = tmp78 * tmp31;
    const auto tmp80 = -1 * tmp79;
    const auto tmp81 = tmp80 / tmp29;
    const auto tmp82 = tmp81 * (tmp26 > tmp22 ? 1 : 0.0);
    const auto tmp83 = tmp16 + tmp16;
    const auto tmp84 = tmp83 / tmp38;
    const auto tmp85 = 2 * tmp84;
    const auto tmp86 = tmp85 * tmp39;
    const auto tmp87 = -1 * tmp86;
    const auto tmp88 = tmp87 / tmp38;
    const auto tmp89 = -1 * tmp88;
    const auto tmp90 = tmp47 * tmp89;
    const auto tmp91 = tmp90 + tmp82;
    const auto tmp92 = tmp91 * (tmp27 > tmp15 ? 1 : 0.0);
    const auto tmp93 = tmp8 + tmp8;
    const auto tmp94 = tmp93 / tmp51;
    const auto tmp95 = 2 * tmp94;
    const auto tmp96 = tmp95 * tmp52;
    const auto tmp97 = -1 * tmp96;
    const auto tmp98 = tmp97 / tmp51;
    const auto tmp99 = -1 * tmp98;
    const auto tmp100 = tmp60 * tmp99;
    const auto tmp101 = tmp100 + tmp92;
    const auto tmp102 = tmp101 * (tmp28 < tmp7 ? 1 : 0.0);
    const auto tmp103 = tmp76 / tmp64;
    const auto tmp104 = 2 * tmp103;
    const auto tmp105 = tmp104 * tmp66;
    const auto tmp106 = -1 * tmp105;
    const auto tmp107 = tmp106 / tmp64;
    const auto tmp108 = tmp73 * tmp107;
    const auto tmp109 = tmp108 + tmp102;
    const auto tmp110 = tmp32 * tmp77;
    const auto tmp111 = -1 * tmp110;
    const auto tmp112 = tmp111 / tmp29;
    const auto tmp113 = tmp112 * (tmp26 > tmp22 ? 1 : 0.0);
    const auto tmp114 = tmp40 * tmp84;
    const auto tmp115 = -1 * tmp114;
    const auto tmp116 = tmp115 / tmp38;
    const auto tmp117 = -1 * tmp116;
    const auto tmp118 = tmp47 * tmp117;
    const auto tmp119 = tmp118 + tmp113;
    const auto tmp120 = tmp119 * (tmp27 > tmp15 ? 1 : 0.0);
    const auto tmp121 = tmp53 * tmp94;
    const auto tmp122 = -1 * tmp121;
    const auto tmp123 = tmp122 / tmp51;
    const auto tmp124 = -1 * tmp123;
    const auto tmp125 = tmp60 * tmp124;
    const auto tmp126 = tmp125 + tmp120;
    const auto tmp127 = tmp126 * (tmp28 < tmp7 ? 1 : 0.0);
    const auto tmp128 = tmp67 * tmp103;
    const auto tmp129 = -1 * tmp128;
    const auto tmp130 = tmp129 / tmp64;
    const auto tmp131 = tmp73 * tmp130;
    const auto tmp132 = tmp131 + tmp127;
    const auto tmp133 = tmp78 * tmp77;
    const auto tmp134 = -1 * tmp133;
    const auto tmp135 = 2 + tmp134;
    const auto tmp136 = tmp135 / tmp29;
    const auto tmp137 = tmp136 * (tmp26 > tmp22 ? 1 : 0.0);
    const auto tmp138 = tmp85 * tmp84;
    const auto tmp139 = -1 * tmp138;
    const auto tmp140 = 2 + tmp139;
    const auto tmp141 = tmp140 / tmp38;
    const auto tmp142 = -1 * tmp141;
    const auto tmp143 = tmp47 * tmp142;
    const auto tmp144 = tmp143 + tmp137;
    const auto tmp145 = tmp144 * (tmp27 > tmp15 ? 1 : 0.0);
    const auto tmp146 = tmp95 * tmp94;
    const auto tmp147 = -1 * tmp146;
    const auto tmp148 = 2 + tmp147;
    const auto tmp149 = tmp148 / tmp51;
    const auto tmp150 = -1 * tmp149;
    const auto tmp151 = tmp60 * tmp150;
    const auto tmp152 = tmp151 + tmp145;
    const auto tmp153 = tmp152 * (tmp28 < tmp7 ? 1 : 0.0);
    const auto tmp154 = tmp104 * tmp103;
    const auto tmp155 = -1 * tmp154;
    const auto tmp156 = 2 + tmp155;
    const auto tmp157 = tmp156 / tmp64;
    const auto tmp158 = tmp73 * tmp157;
    const auto tmp159 = tmp158 + tmp153;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp75;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp109;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp132;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp159;
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

} // namespace UFLLocalFunctions_0f7b2106478c5d2af781b1f377a180d2

PYBIND11_MODULE( localfunction_0f7b2106478c5d2af781b1f377a180d2_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef UFLLocalFunctions_0f7b2106478c5d2af781b1f377a180d2::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_0f7b2106478c5d2af781b1f377a180d2::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_0f7b2106478c5d2af781b1f377a180d2_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
