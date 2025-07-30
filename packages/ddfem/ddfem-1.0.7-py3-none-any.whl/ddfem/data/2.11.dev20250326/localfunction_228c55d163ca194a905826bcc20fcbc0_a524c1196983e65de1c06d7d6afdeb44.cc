#ifndef GUARD_228c55d163ca194a905826bcc20fcbc0
#define GUARD_228c55d163ca194a905826bcc20fcbc0

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
#include <dune/fempy/function/virtualizedgridfunction.hh>
#include <dune/fempy/py/ufllocalfunction.hh>

namespace UFLLocalFunctions_228c55d163ca194a905826bcc20fcbc0
{

  // UFLLocalFunction
// ----------------

template< class GridPart, class Coeffbndproj >
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
  typedef double Conepsilon;
  typedef std::tuple< std::shared_ptr< Conepsilon > > ConstantTupleType;
  template< std::size_t i >
  using ConstantsRangeType = typename std::tuple_element_t< i, ConstantTupleType >::element_type;
  typedef std::tuple< Dune::Fem::GridFunctionSpace< GridPartType, Dune::FieldVector< double, 2 > > > CoefficientFunctionSpaceTupleType;
  typedef std::tuple< Coeffbndproj > CoefficientTupleType;
  template< std::size_t i >
  using CoefficientFunctionSpaceType = std::tuple_element_t< i, CoefficientFunctionSpaceTupleType >;
  template< std::size_t i >
  using CoefficientRangeType = typename CoefficientFunctionSpaceType< i >::RangeType;
  template< std::size_t i >
  using CoefficientJacobianRangeType = typename CoefficientFunctionSpaceType< i >::JacobianRangeType;
  static constexpr bool gridPartValid = Dune::Fem::checkGridPartValid<GridPartType,Dune::Fem::ConstLocalFunction<Coeffbndproj>>();
  template< std::size_t i >
  using CoefficientType = std::tuple_element_t< i, CoefficientTupleType >;
  template< std::size_t i >
  using ConstantType = typename std::tuple_element_t< i, ConstantTupleType >::element_type;
  using BaseType::entity;
  using BaseType::geometry;

  UFLLocalFunction ( const GridPartType &gridPart, const std::string &name, int order, const Coeffbndproj &coeffbndproj, const Dune::Fem::ParameterReader &parameter = Dune::Fem::Parameter::container() )
    : BaseType(gridPart,name,order),
      coefficients_( Dune::Fem::ConstLocalFunction< Coeffbndproj >( coeffbndproj ) )
  {
    std::get< 0 >( constants_ ) = std::make_shared< Conepsilon >( (Conepsilon(0)) );
  }

  void bind ( const IntersectionType &intersection, Side side )
  {
    BaseType::bind(intersection, side);
    std::get< 0 >( coefficients_ ).bind( this->entity() );
  }

  void bind ( const EntityType &entity )
  {
    BaseType::bind(entity);
    std::get< 0 >( coefficients_ ).bind( this->entity() );
  }

  void unbind ()
  {
    BaseType::unbind();
    std::get< 0 >( coefficients_ ).unbind();
  }

  template< class Point >
  void evaluate ( const Point &x, typename FunctionSpaceType::RangeType &result ) const
  {
    using std::max;
    using std::min;
    using std::sqrt;
    using std::tanh;
    double tmp0 = constant< 0 >();
    typename CoefficientFunctionSpaceType< 0 >::RangeType tmp1 = evaluateCoefficient< 0 >( x );
    const auto tmp2 = tmp1[ 1 ] * tmp1[ 1 ];
    const auto tmp3 = tmp1[ 0 ] * tmp1[ 0 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -1.4 + tmp6;
    const auto tmp8 = 1 + tmp1[ 0 ];
    const auto tmp9 = tmp8 * tmp8;
    const auto tmp10 = tmp2 + tmp9;
    const auto tmp11 = 1e-10 + tmp10;
    const auto tmp12 = std::sqrt( tmp11 );
    const auto tmp13 = -0.5 + tmp12;
    const auto tmp14 = -1 + tmp1[ 0 ];
    const auto tmp15 = tmp14 * tmp14;
    const auto tmp16 = tmp2 + tmp15;
    const auto tmp17 = 1e-10 + tmp16;
    const auto tmp18 = std::sqrt( tmp17 );
    const auto tmp19 = -0.5 + tmp18;
    const auto tmp20 = 0.8 + tmp1[ 1 ];
    const auto tmp21 = tmp20 * tmp20;
    const auto tmp22 = tmp3 + tmp21;
    const auto tmp23 = 1e-10 + tmp22;
    const auto tmp24 = std::sqrt( tmp23 );
    const auto tmp25 = -0.5 + tmp24;
    const auto tmp26 = -1 * tmp25;
    const auto tmp27 = -0.8 + tmp1[ 1 ];
    const auto tmp28 = tmp27 * tmp27;
    const auto tmp29 = tmp3 + tmp28;
    const auto tmp30 = 1e-10 + tmp29;
    const auto tmp31 = std::sqrt( tmp30 );
    const auto tmp32 = -0.5 + tmp31;
    const auto tmp33 = -1 * tmp32;
    const auto tmp34 = -1 + tmp6;
    const auto tmp35 = std::max( tmp34, tmp33 );
    const auto tmp36 = std::max( tmp35, tmp26 );
    const auto tmp37 = std::min( tmp36, tmp19 );
    const auto tmp38 = std::min( tmp37, tmp13 );
    const auto tmp39 = std::max( tmp38, tmp7 );
    const auto tmp40 = 3 * tmp39;
    const auto tmp41 = tmp40 / tmp0;
    const auto tmp42 = std::tanh( tmp41 );
    const auto tmp43 = -1 * tmp42;
    const auto tmp44 = 1 + tmp43;
    const auto tmp45 = 0.5 * tmp44;
    const auto tmp46 = -1 * tmp45;
    const auto tmp47 = 1 + tmp46;
    const auto tmp48 = tmp47 * tmp45;
    result[ 0 ] = tmp48;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::cosh;
    using std::max;
    using std::min;
    using std::pow;
    using std::sqrt;
    using std::tanh;
    double tmp0 = constant< 0 >();
    typename CoefficientFunctionSpaceType< 0 >::RangeType tmp1 = evaluateCoefficient< 0 >( x );
    const auto tmp2 = tmp1[ 1 ] * tmp1[ 1 ];
    const auto tmp3 = tmp1[ 0 ] * tmp1[ 0 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -1.4 + tmp6;
    const auto tmp8 = 1 + tmp1[ 0 ];
    const auto tmp9 = tmp8 * tmp8;
    const auto tmp10 = tmp2 + tmp9;
    const auto tmp11 = 1e-10 + tmp10;
    const auto tmp12 = std::sqrt( tmp11 );
    const auto tmp13 = -0.5 + tmp12;
    const auto tmp14 = -1 + tmp1[ 0 ];
    const auto tmp15 = tmp14 * tmp14;
    const auto tmp16 = tmp2 + tmp15;
    const auto tmp17 = 1e-10 + tmp16;
    const auto tmp18 = std::sqrt( tmp17 );
    const auto tmp19 = -0.5 + tmp18;
    const auto tmp20 = 0.8 + tmp1[ 1 ];
    const auto tmp21 = tmp20 * tmp20;
    const auto tmp22 = tmp3 + tmp21;
    const auto tmp23 = 1e-10 + tmp22;
    const auto tmp24 = std::sqrt( tmp23 );
    const auto tmp25 = -0.5 + tmp24;
    const auto tmp26 = -1 * tmp25;
    const auto tmp27 = -0.8 + tmp1[ 1 ];
    const auto tmp28 = tmp27 * tmp27;
    const auto tmp29 = tmp3 + tmp28;
    const auto tmp30 = 1e-10 + tmp29;
    const auto tmp31 = std::sqrt( tmp30 );
    const auto tmp32 = -0.5 + tmp31;
    const auto tmp33 = -1 * tmp32;
    const auto tmp34 = -1 + tmp6;
    const auto tmp35 = std::max( tmp34, tmp33 );
    const auto tmp36 = std::max( tmp35, tmp26 );
    const auto tmp37 = std::min( tmp36, tmp19 );
    const auto tmp38 = std::min( tmp37, tmp13 );
    const auto tmp39 = std::max( tmp38, tmp7 );
    const auto tmp40 = 3 * tmp39;
    const auto tmp41 = tmp40 / tmp0;
    const auto tmp42 = 2.0 * tmp41;
    const auto tmp43 = std::cosh( tmp42 );
    const auto tmp44 = 1.0 + tmp43;
    const auto tmp45 = std::cosh( tmp41 );
    const auto tmp46 = 2.0 * tmp45;
    const auto tmp47 = tmp46 / tmp44;
    const auto tmp48 = std::pow( tmp47, 2 );
    const auto tmp49 = 2 * tmp6;
    typename CoefficientFunctionSpaceType< 0 >::JacobianRangeType tmp50 = jacobianCoefficient< 0 >( x );
    const auto tmp51 = tmp1[ 1 ] * (tmp50[ 1 ])[ 0 ];
    const auto tmp52 = tmp51 + tmp51;
    const auto tmp53 = tmp1[ 0 ] * (tmp50[ 0 ])[ 0 ];
    const auto tmp54 = tmp53 + tmp53;
    const auto tmp55 = tmp54 + tmp52;
    const auto tmp56 = tmp55 / tmp49;
    const auto tmp57 = tmp56 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp58 = 2 * tmp31;
    const auto tmp59 = (tmp50[ 1 ])[ 0 ] * tmp27;
    const auto tmp60 = tmp59 + tmp59;
    const auto tmp61 = tmp54 + tmp60;
    const auto tmp62 = tmp61 / tmp58;
    const auto tmp63 = -1 * tmp62;
    const auto tmp64 = -1 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp65 = 1.0 + tmp64;
    const auto tmp66 = tmp65 * tmp63;
    const auto tmp67 = tmp66 + tmp57;
    const auto tmp68 = tmp67 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp69 = 2 * tmp24;
    const auto tmp70 = (tmp50[ 1 ])[ 0 ] * tmp20;
    const auto tmp71 = tmp70 + tmp70;
    const auto tmp72 = tmp54 + tmp71;
    const auto tmp73 = tmp72 / tmp69;
    const auto tmp74 = -1 * tmp73;
    const auto tmp75 = -1 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp76 = 1.0 + tmp75;
    const auto tmp77 = tmp76 * tmp74;
    const auto tmp78 = tmp77 + tmp68;
    const auto tmp79 = tmp78 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp80 = 2 * tmp18;
    const auto tmp81 = (tmp50[ 0 ])[ 0 ] * tmp14;
    const auto tmp82 = tmp81 + tmp81;
    const auto tmp83 = tmp52 + tmp82;
    const auto tmp84 = tmp83 / tmp80;
    const auto tmp85 = -1 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp86 = 1.0 + tmp85;
    const auto tmp87 = tmp86 * tmp84;
    const auto tmp88 = tmp87 + tmp79;
    const auto tmp89 = tmp88 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp90 = 2 * tmp12;
    const auto tmp91 = (tmp50[ 0 ])[ 0 ] * tmp8;
    const auto tmp92 = tmp91 + tmp91;
    const auto tmp93 = tmp52 + tmp92;
    const auto tmp94 = tmp93 / tmp90;
    const auto tmp95 = -1 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp96 = 1.0 + tmp95;
    const auto tmp97 = tmp96 * tmp94;
    const auto tmp98 = tmp97 + tmp89;
    const auto tmp99 = tmp98 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp100 = -1 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp101 = 1.0 + tmp100;
    const auto tmp102 = tmp101 * tmp56;
    const auto tmp103 = tmp102 + tmp99;
    const auto tmp104 = 3 * tmp103;
    const auto tmp105 = tmp104 / tmp0;
    const auto tmp106 = tmp105 * tmp48;
    const auto tmp107 = -1 * tmp106;
    const auto tmp108 = 0.5 * tmp107;
    const auto tmp109 = std::tanh( tmp41 );
    const auto tmp110 = -1 * tmp109;
    const auto tmp111 = 1 + tmp110;
    const auto tmp112 = 0.5 * tmp111;
    const auto tmp113 = -1 * tmp112;
    const auto tmp114 = 1 + tmp113;
    const auto tmp115 = tmp114 * tmp108;
    const auto tmp116 = -1 * tmp108;
    const auto tmp117 = tmp112 * tmp116;
    const auto tmp118 = tmp117 + tmp115;
    const auto tmp119 = tmp1[ 1 ] * (tmp50[ 1 ])[ 1 ];
    const auto tmp120 = tmp119 + tmp119;
    const auto tmp121 = tmp1[ 0 ] * (tmp50[ 0 ])[ 1 ];
    const auto tmp122 = tmp121 + tmp121;
    const auto tmp123 = tmp122 + tmp120;
    const auto tmp124 = tmp123 / tmp49;
    const auto tmp125 = tmp124 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp126 = (tmp50[ 1 ])[ 1 ] * tmp27;
    const auto tmp127 = tmp126 + tmp126;
    const auto tmp128 = tmp122 + tmp127;
    const auto tmp129 = tmp128 / tmp58;
    const auto tmp130 = -1 * tmp129;
    const auto tmp131 = tmp65 * tmp130;
    const auto tmp132 = tmp131 + tmp125;
    const auto tmp133 = tmp132 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp134 = (tmp50[ 1 ])[ 1 ] * tmp20;
    const auto tmp135 = tmp134 + tmp134;
    const auto tmp136 = tmp122 + tmp135;
    const auto tmp137 = tmp136 / tmp69;
    const auto tmp138 = -1 * tmp137;
    const auto tmp139 = tmp76 * tmp138;
    const auto tmp140 = tmp139 + tmp133;
    const auto tmp141 = tmp140 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp142 = (tmp50[ 0 ])[ 1 ] * tmp14;
    const auto tmp143 = tmp142 + tmp142;
    const auto tmp144 = tmp120 + tmp143;
    const auto tmp145 = tmp144 / tmp80;
    const auto tmp146 = tmp86 * tmp145;
    const auto tmp147 = tmp146 + tmp141;
    const auto tmp148 = tmp147 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp149 = (tmp50[ 0 ])[ 1 ] * tmp8;
    const auto tmp150 = tmp149 + tmp149;
    const auto tmp151 = tmp120 + tmp150;
    const auto tmp152 = tmp151 / tmp90;
    const auto tmp153 = tmp96 * tmp152;
    const auto tmp154 = tmp153 + tmp148;
    const auto tmp155 = tmp154 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp156 = tmp101 * tmp124;
    const auto tmp157 = tmp156 + tmp155;
    const auto tmp158 = 3 * tmp157;
    const auto tmp159 = tmp158 / tmp0;
    const auto tmp160 = tmp159 * tmp48;
    const auto tmp161 = -1 * tmp160;
    const auto tmp162 = 0.5 * tmp161;
    const auto tmp163 = tmp114 * tmp162;
    const auto tmp164 = -1 * tmp162;
    const auto tmp165 = tmp112 * tmp164;
    const auto tmp166 = tmp165 + tmp163;
    (result[ 0 ])[ 0 ] = tmp118;
    (result[ 0 ])[ 1 ] = tmp166;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::cosh;
    using std::max;
    using std::min;
    using std::pow;
    using std::sinh;
    using std::sqrt;
    using std::tanh;
    double tmp0 = constant< 0 >();
    typename CoefficientFunctionSpaceType< 0 >::RangeType tmp1 = evaluateCoefficient< 0 >( x );
    const auto tmp2 = tmp1[ 1 ] * tmp1[ 1 ];
    const auto tmp3 = tmp1[ 0 ] * tmp1[ 0 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -1.4 + tmp6;
    const auto tmp8 = 1 + tmp1[ 0 ];
    const auto tmp9 = tmp8 * tmp8;
    const auto tmp10 = tmp2 + tmp9;
    const auto tmp11 = 1e-10 + tmp10;
    const auto tmp12 = std::sqrt( tmp11 );
    const auto tmp13 = -0.5 + tmp12;
    const auto tmp14 = -1 + tmp1[ 0 ];
    const auto tmp15 = tmp14 * tmp14;
    const auto tmp16 = tmp2 + tmp15;
    const auto tmp17 = 1e-10 + tmp16;
    const auto tmp18 = std::sqrt( tmp17 );
    const auto tmp19 = -0.5 + tmp18;
    const auto tmp20 = 0.8 + tmp1[ 1 ];
    const auto tmp21 = tmp20 * tmp20;
    const auto tmp22 = tmp3 + tmp21;
    const auto tmp23 = 1e-10 + tmp22;
    const auto tmp24 = std::sqrt( tmp23 );
    const auto tmp25 = -0.5 + tmp24;
    const auto tmp26 = -1 * tmp25;
    const auto tmp27 = -0.8 + tmp1[ 1 ];
    const auto tmp28 = tmp27 * tmp27;
    const auto tmp29 = tmp3 + tmp28;
    const auto tmp30 = 1e-10 + tmp29;
    const auto tmp31 = std::sqrt( tmp30 );
    const auto tmp32 = -0.5 + tmp31;
    const auto tmp33 = -1 * tmp32;
    const auto tmp34 = -1 + tmp6;
    const auto tmp35 = std::max( tmp34, tmp33 );
    const auto tmp36 = std::max( tmp35, tmp26 );
    const auto tmp37 = std::min( tmp36, tmp19 );
    const auto tmp38 = std::min( tmp37, tmp13 );
    const auto tmp39 = std::max( tmp38, tmp7 );
    const auto tmp40 = 3 * tmp39;
    const auto tmp41 = tmp40 / tmp0;
    const auto tmp42 = 2.0 * tmp41;
    const auto tmp43 = std::cosh( tmp42 );
    const auto tmp44 = 1.0 + tmp43;
    const auto tmp45 = std::cosh( tmp41 );
    const auto tmp46 = 2.0 * tmp45;
    const auto tmp47 = tmp46 / tmp44;
    const auto tmp48 = std::pow( tmp47, 2 );
    const auto tmp49 = 2 * tmp6;
    typename CoefficientFunctionSpaceType< 0 >::JacobianRangeType tmp50 = jacobianCoefficient< 0 >( x );
    const auto tmp51 = tmp1[ 1 ] * (tmp50[ 1 ])[ 0 ];
    const auto tmp52 = tmp51 + tmp51;
    const auto tmp53 = tmp1[ 0 ] * (tmp50[ 0 ])[ 0 ];
    const auto tmp54 = tmp53 + tmp53;
    const auto tmp55 = tmp54 + tmp52;
    const auto tmp56 = tmp55 / tmp49;
    const auto tmp57 = tmp56 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp58 = 2 * tmp31;
    const auto tmp59 = (tmp50[ 1 ])[ 0 ] * tmp27;
    const auto tmp60 = tmp59 + tmp59;
    const auto tmp61 = tmp54 + tmp60;
    const auto tmp62 = tmp61 / tmp58;
    const auto tmp63 = -1 * tmp62;
    const auto tmp64 = -1 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp65 = 1.0 + tmp64;
    const auto tmp66 = tmp65 * tmp63;
    const auto tmp67 = tmp66 + tmp57;
    const auto tmp68 = tmp67 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp69 = 2 * tmp24;
    const auto tmp70 = (tmp50[ 1 ])[ 0 ] * tmp20;
    const auto tmp71 = tmp70 + tmp70;
    const auto tmp72 = tmp54 + tmp71;
    const auto tmp73 = tmp72 / tmp69;
    const auto tmp74 = -1 * tmp73;
    const auto tmp75 = -1 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp76 = 1.0 + tmp75;
    const auto tmp77 = tmp76 * tmp74;
    const auto tmp78 = tmp77 + tmp68;
    const auto tmp79 = tmp78 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp80 = 2 * tmp18;
    const auto tmp81 = (tmp50[ 0 ])[ 0 ] * tmp14;
    const auto tmp82 = tmp81 + tmp81;
    const auto tmp83 = tmp52 + tmp82;
    const auto tmp84 = tmp83 / tmp80;
    const auto tmp85 = -1 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp86 = 1.0 + tmp85;
    const auto tmp87 = tmp86 * tmp84;
    const auto tmp88 = tmp87 + tmp79;
    const auto tmp89 = tmp88 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp90 = 2 * tmp12;
    const auto tmp91 = (tmp50[ 0 ])[ 0 ] * tmp8;
    const auto tmp92 = tmp91 + tmp91;
    const auto tmp93 = tmp52 + tmp92;
    const auto tmp94 = tmp93 / tmp90;
    const auto tmp95 = -1 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp96 = 1.0 + tmp95;
    const auto tmp97 = tmp96 * tmp94;
    const auto tmp98 = tmp97 + tmp89;
    const auto tmp99 = tmp98 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp100 = -1 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp101 = 1.0 + tmp100;
    const auto tmp102 = tmp101 * tmp56;
    const auto tmp103 = tmp102 + tmp99;
    const auto tmp104 = 3 * tmp103;
    const auto tmp105 = tmp104 / tmp0;
    const auto tmp106 = tmp105 * tmp48;
    const auto tmp107 = -1 * tmp106;
    const auto tmp108 = 0.5 * tmp107;
    const auto tmp109 = -1 * tmp108;
    const auto tmp110 = tmp109 * tmp108;
    const auto tmp111 = 2 * tmp56;
    const auto tmp112 = tmp111 * tmp56;
    const auto tmp113 = -1 * tmp112;
    typename CoefficientFunctionSpaceType< 0 >::HessianRangeType tmp114 = hessianCoefficient< 0 >( x );
    const auto tmp115 = tmp1[ 1 ] * ((tmp114[ 1 ])[ 0 ])[ 0 ];
    const auto tmp116 = (tmp50[ 1 ])[ 0 ] * (tmp50[ 1 ])[ 0 ];
    const auto tmp117 = tmp116 + tmp115;
    const auto tmp118 = tmp117 + tmp117;
    const auto tmp119 = tmp1[ 0 ] * ((tmp114[ 0 ])[ 0 ])[ 0 ];
    const auto tmp120 = (tmp50[ 0 ])[ 0 ] * (tmp50[ 0 ])[ 0 ];
    const auto tmp121 = tmp120 + tmp119;
    const auto tmp122 = tmp121 + tmp121;
    const auto tmp123 = tmp122 + tmp118;
    const auto tmp124 = tmp123 + tmp113;
    const auto tmp125 = tmp124 / tmp49;
    const auto tmp126 = tmp125 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp127 = 2 * tmp62;
    const auto tmp128 = tmp127 * tmp62;
    const auto tmp129 = -1 * tmp128;
    const auto tmp130 = ((tmp114[ 1 ])[ 0 ])[ 0 ] * tmp27;
    const auto tmp131 = tmp116 + tmp130;
    const auto tmp132 = tmp131 + tmp131;
    const auto tmp133 = tmp122 + tmp132;
    const auto tmp134 = tmp133 + tmp129;
    const auto tmp135 = tmp134 / tmp58;
    const auto tmp136 = -1 * tmp135;
    const auto tmp137 = tmp65 * tmp136;
    const auto tmp138 = tmp137 + tmp126;
    const auto tmp139 = tmp138 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp140 = 2 * tmp73;
    const auto tmp141 = tmp140 * tmp73;
    const auto tmp142 = -1 * tmp141;
    const auto tmp143 = ((tmp114[ 1 ])[ 0 ])[ 0 ] * tmp20;
    const auto tmp144 = tmp116 + tmp143;
    const auto tmp145 = tmp144 + tmp144;
    const auto tmp146 = tmp122 + tmp145;
    const auto tmp147 = tmp146 + tmp142;
    const auto tmp148 = tmp147 / tmp69;
    const auto tmp149 = -1 * tmp148;
    const auto tmp150 = tmp76 * tmp149;
    const auto tmp151 = tmp150 + tmp139;
    const auto tmp152 = tmp151 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp153 = 2 * tmp84;
    const auto tmp154 = tmp153 * tmp84;
    const auto tmp155 = -1 * tmp154;
    const auto tmp156 = ((tmp114[ 0 ])[ 0 ])[ 0 ] * tmp14;
    const auto tmp157 = tmp120 + tmp156;
    const auto tmp158 = tmp157 + tmp157;
    const auto tmp159 = tmp118 + tmp158;
    const auto tmp160 = tmp159 + tmp155;
    const auto tmp161 = tmp160 / tmp80;
    const auto tmp162 = tmp86 * tmp161;
    const auto tmp163 = tmp162 + tmp152;
    const auto tmp164 = tmp163 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp165 = 2 * tmp94;
    const auto tmp166 = tmp165 * tmp94;
    const auto tmp167 = -1 * tmp166;
    const auto tmp168 = ((tmp114[ 0 ])[ 0 ])[ 0 ] * tmp8;
    const auto tmp169 = tmp120 + tmp168;
    const auto tmp170 = tmp169 + tmp169;
    const auto tmp171 = tmp118 + tmp170;
    const auto tmp172 = tmp171 + tmp167;
    const auto tmp173 = tmp172 / tmp90;
    const auto tmp174 = tmp96 * tmp173;
    const auto tmp175 = tmp174 + tmp164;
    const auto tmp176 = tmp175 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp177 = tmp101 * tmp125;
    const auto tmp178 = tmp177 + tmp176;
    const auto tmp179 = 3 * tmp178;
    const auto tmp180 = tmp179 / tmp0;
    const auto tmp181 = tmp180 * tmp48;
    const auto tmp182 = std::sinh( tmp41 );
    const auto tmp183 = tmp105 * tmp182;
    const auto tmp184 = 2.0 * tmp183;
    const auto tmp185 = std::sinh( tmp42 );
    const auto tmp186 = 2.0 * tmp105;
    const auto tmp187 = tmp186 * tmp185;
    const auto tmp188 = tmp187 * tmp47;
    const auto tmp189 = -1 * tmp188;
    const auto tmp190 = tmp189 + tmp184;
    const auto tmp191 = tmp190 / tmp44;
    const auto tmp192 = 2 * tmp191;
    const auto tmp193 = tmp192 * tmp47;
    const auto tmp194 = tmp193 * tmp105;
    const auto tmp195 = tmp194 + tmp181;
    const auto tmp196 = -1 * tmp195;
    const auto tmp197 = 0.5 * tmp196;
    const auto tmp198 = -1 * tmp197;
    const auto tmp199 = std::tanh( tmp41 );
    const auto tmp200 = -1 * tmp199;
    const auto tmp201 = 1 + tmp200;
    const auto tmp202 = 0.5 * tmp201;
    const auto tmp203 = tmp202 * tmp198;
    const auto tmp204 = tmp203 + tmp110;
    const auto tmp205 = -1 * tmp202;
    const auto tmp206 = 1 + tmp205;
    const auto tmp207 = tmp206 * tmp197;
    const auto tmp208 = tmp207 + tmp110;
    const auto tmp209 = tmp208 + tmp204;
    const auto tmp210 = tmp1[ 1 ] * (tmp50[ 1 ])[ 1 ];
    const auto tmp211 = tmp210 + tmp210;
    const auto tmp212 = tmp1[ 0 ] * (tmp50[ 0 ])[ 1 ];
    const auto tmp213 = tmp212 + tmp212;
    const auto tmp214 = tmp213 + tmp211;
    const auto tmp215 = tmp214 / tmp49;
    const auto tmp216 = tmp215 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp217 = (tmp50[ 1 ])[ 1 ] * tmp27;
    const auto tmp218 = tmp217 + tmp217;
    const auto tmp219 = tmp213 + tmp218;
    const auto tmp220 = tmp219 / tmp58;
    const auto tmp221 = -1 * tmp220;
    const auto tmp222 = tmp65 * tmp221;
    const auto tmp223 = tmp222 + tmp216;
    const auto tmp224 = tmp223 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp225 = (tmp50[ 1 ])[ 1 ] * tmp20;
    const auto tmp226 = tmp225 + tmp225;
    const auto tmp227 = tmp213 + tmp226;
    const auto tmp228 = tmp227 / tmp69;
    const auto tmp229 = -1 * tmp228;
    const auto tmp230 = tmp76 * tmp229;
    const auto tmp231 = tmp230 + tmp224;
    const auto tmp232 = tmp231 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp233 = (tmp50[ 0 ])[ 1 ] * tmp14;
    const auto tmp234 = tmp233 + tmp233;
    const auto tmp235 = tmp211 + tmp234;
    const auto tmp236 = tmp235 / tmp80;
    const auto tmp237 = tmp86 * tmp236;
    const auto tmp238 = tmp237 + tmp232;
    const auto tmp239 = tmp238 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp240 = (tmp50[ 0 ])[ 1 ] * tmp8;
    const auto tmp241 = tmp240 + tmp240;
    const auto tmp242 = tmp211 + tmp241;
    const auto tmp243 = tmp242 / tmp90;
    const auto tmp244 = tmp96 * tmp243;
    const auto tmp245 = tmp244 + tmp239;
    const auto tmp246 = tmp245 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp247 = tmp101 * tmp215;
    const auto tmp248 = tmp247 + tmp246;
    const auto tmp249 = 3 * tmp248;
    const auto tmp250 = tmp249 / tmp0;
    const auto tmp251 = tmp250 * tmp48;
    const auto tmp252 = -1 * tmp251;
    const auto tmp253 = 0.5 * tmp252;
    const auto tmp254 = tmp109 * tmp253;
    const auto tmp255 = 2 * tmp215;
    const auto tmp256 = tmp255 * tmp56;
    const auto tmp257 = -1 * tmp256;
    const auto tmp258 = (tmp50[ 1 ])[ 0 ] * (tmp50[ 1 ])[ 1 ];
    const auto tmp259 = tmp1[ 1 ] * ((tmp114[ 1 ])[ 0 ])[ 1 ];
    const auto tmp260 = tmp259 + tmp258;
    const auto tmp261 = tmp260 + tmp260;
    const auto tmp262 = (tmp50[ 0 ])[ 0 ] * (tmp50[ 0 ])[ 1 ];
    const auto tmp263 = tmp1[ 0 ] * ((tmp114[ 0 ])[ 0 ])[ 1 ];
    const auto tmp264 = tmp263 + tmp262;
    const auto tmp265 = tmp264 + tmp264;
    const auto tmp266 = tmp265 + tmp261;
    const auto tmp267 = tmp266 + tmp257;
    const auto tmp268 = tmp267 / tmp49;
    const auto tmp269 = tmp268 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp270 = 2 * tmp220;
    const auto tmp271 = tmp270 * tmp62;
    const auto tmp272 = -1 * tmp271;
    const auto tmp273 = ((tmp114[ 1 ])[ 0 ])[ 1 ] * tmp27;
    const auto tmp274 = tmp258 + tmp273;
    const auto tmp275 = tmp274 + tmp274;
    const auto tmp276 = tmp265 + tmp275;
    const auto tmp277 = tmp276 + tmp272;
    const auto tmp278 = tmp277 / tmp58;
    const auto tmp279 = -1 * tmp278;
    const auto tmp280 = tmp65 * tmp279;
    const auto tmp281 = tmp280 + tmp269;
    const auto tmp282 = tmp281 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp283 = 2 * tmp228;
    const auto tmp284 = tmp283 * tmp73;
    const auto tmp285 = -1 * tmp284;
    const auto tmp286 = ((tmp114[ 1 ])[ 0 ])[ 1 ] * tmp20;
    const auto tmp287 = tmp258 + tmp286;
    const auto tmp288 = tmp287 + tmp287;
    const auto tmp289 = tmp265 + tmp288;
    const auto tmp290 = tmp289 + tmp285;
    const auto tmp291 = tmp290 / tmp69;
    const auto tmp292 = -1 * tmp291;
    const auto tmp293 = tmp76 * tmp292;
    const auto tmp294 = tmp293 + tmp282;
    const auto tmp295 = tmp294 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp296 = 2 * tmp236;
    const auto tmp297 = tmp296 * tmp84;
    const auto tmp298 = -1 * tmp297;
    const auto tmp299 = ((tmp114[ 0 ])[ 0 ])[ 1 ] * tmp14;
    const auto tmp300 = tmp262 + tmp299;
    const auto tmp301 = tmp300 + tmp300;
    const auto tmp302 = tmp261 + tmp301;
    const auto tmp303 = tmp302 + tmp298;
    const auto tmp304 = tmp303 / tmp80;
    const auto tmp305 = tmp86 * tmp304;
    const auto tmp306 = tmp305 + tmp295;
    const auto tmp307 = tmp306 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp308 = 2 * tmp243;
    const auto tmp309 = tmp308 * tmp94;
    const auto tmp310 = -1 * tmp309;
    const auto tmp311 = ((tmp114[ 0 ])[ 0 ])[ 1 ] * tmp8;
    const auto tmp312 = tmp262 + tmp311;
    const auto tmp313 = tmp312 + tmp312;
    const auto tmp314 = tmp261 + tmp313;
    const auto tmp315 = tmp314 + tmp310;
    const auto tmp316 = tmp315 / tmp90;
    const auto tmp317 = tmp96 * tmp316;
    const auto tmp318 = tmp317 + tmp307;
    const auto tmp319 = tmp318 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp320 = tmp101 * tmp268;
    const auto tmp321 = tmp320 + tmp319;
    const auto tmp322 = 3 * tmp321;
    const auto tmp323 = tmp322 / tmp0;
    const auto tmp324 = tmp323 * tmp48;
    const auto tmp325 = tmp250 * tmp182;
    const auto tmp326 = 2.0 * tmp325;
    const auto tmp327 = 2.0 * tmp250;
    const auto tmp328 = tmp327 * tmp185;
    const auto tmp329 = tmp328 * tmp47;
    const auto tmp330 = -1 * tmp329;
    const auto tmp331 = tmp330 + tmp326;
    const auto tmp332 = tmp331 / tmp44;
    const auto tmp333 = 2 * tmp332;
    const auto tmp334 = tmp333 * tmp47;
    const auto tmp335 = tmp334 * tmp105;
    const auto tmp336 = tmp335 + tmp324;
    const auto tmp337 = -1 * tmp336;
    const auto tmp338 = 0.5 * tmp337;
    const auto tmp339 = -1 * tmp338;
    const auto tmp340 = tmp202 * tmp339;
    const auto tmp341 = tmp340 + tmp254;
    const auto tmp342 = -1 * tmp253;
    const auto tmp343 = tmp342 * tmp108;
    const auto tmp344 = tmp206 * tmp338;
    const auto tmp345 = tmp344 + tmp343;
    const auto tmp346 = tmp345 + tmp341;
    const auto tmp347 = tmp111 * tmp215;
    const auto tmp348 = -1 * tmp347;
    const auto tmp349 = tmp1[ 1 ] * ((tmp114[ 1 ])[ 1 ])[ 0 ];
    const auto tmp350 = tmp258 + tmp349;
    const auto tmp351 = tmp350 + tmp350;
    const auto tmp352 = tmp1[ 0 ] * ((tmp114[ 0 ])[ 1 ])[ 0 ];
    const auto tmp353 = tmp262 + tmp352;
    const auto tmp354 = tmp353 + tmp353;
    const auto tmp355 = tmp354 + tmp351;
    const auto tmp356 = tmp355 + tmp348;
    const auto tmp357 = tmp356 / tmp49;
    const auto tmp358 = tmp357 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp359 = tmp127 * tmp220;
    const auto tmp360 = -1 * tmp359;
    const auto tmp361 = ((tmp114[ 1 ])[ 1 ])[ 0 ] * tmp27;
    const auto tmp362 = tmp258 + tmp361;
    const auto tmp363 = tmp362 + tmp362;
    const auto tmp364 = tmp354 + tmp363;
    const auto tmp365 = tmp364 + tmp360;
    const auto tmp366 = tmp365 / tmp58;
    const auto tmp367 = -1 * tmp366;
    const auto tmp368 = tmp65 * tmp367;
    const auto tmp369 = tmp368 + tmp358;
    const auto tmp370 = tmp369 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp371 = tmp140 * tmp228;
    const auto tmp372 = -1 * tmp371;
    const auto tmp373 = ((tmp114[ 1 ])[ 1 ])[ 0 ] * tmp20;
    const auto tmp374 = tmp258 + tmp373;
    const auto tmp375 = tmp374 + tmp374;
    const auto tmp376 = tmp354 + tmp375;
    const auto tmp377 = tmp376 + tmp372;
    const auto tmp378 = tmp377 / tmp69;
    const auto tmp379 = -1 * tmp378;
    const auto tmp380 = tmp76 * tmp379;
    const auto tmp381 = tmp380 + tmp370;
    const auto tmp382 = tmp381 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp383 = tmp153 * tmp236;
    const auto tmp384 = -1 * tmp383;
    const auto tmp385 = ((tmp114[ 0 ])[ 1 ])[ 0 ] * tmp14;
    const auto tmp386 = tmp262 + tmp385;
    const auto tmp387 = tmp386 + tmp386;
    const auto tmp388 = tmp351 + tmp387;
    const auto tmp389 = tmp388 + tmp384;
    const auto tmp390 = tmp389 / tmp80;
    const auto tmp391 = tmp86 * tmp390;
    const auto tmp392 = tmp391 + tmp382;
    const auto tmp393 = tmp392 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp394 = tmp165 * tmp243;
    const auto tmp395 = -1 * tmp394;
    const auto tmp396 = ((tmp114[ 0 ])[ 1 ])[ 0 ] * tmp8;
    const auto tmp397 = tmp262 + tmp396;
    const auto tmp398 = tmp397 + tmp397;
    const auto tmp399 = tmp351 + tmp398;
    const auto tmp400 = tmp399 + tmp395;
    const auto tmp401 = tmp400 / tmp90;
    const auto tmp402 = tmp96 * tmp401;
    const auto tmp403 = tmp402 + tmp393;
    const auto tmp404 = tmp403 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp405 = tmp101 * tmp357;
    const auto tmp406 = tmp405 + tmp404;
    const auto tmp407 = 3 * tmp406;
    const auto tmp408 = tmp407 / tmp0;
    const auto tmp409 = tmp408 * tmp48;
    const auto tmp410 = tmp193 * tmp250;
    const auto tmp411 = tmp410 + tmp409;
    const auto tmp412 = -1 * tmp411;
    const auto tmp413 = 0.5 * tmp412;
    const auto tmp414 = tmp206 * tmp413;
    const auto tmp415 = tmp414 + tmp254;
    const auto tmp416 = -1 * tmp413;
    const auto tmp417 = tmp202 * tmp416;
    const auto tmp418 = tmp417 + tmp343;
    const auto tmp419 = tmp418 + tmp415;
    const auto tmp420 = tmp342 * tmp253;
    const auto tmp421 = tmp255 * tmp215;
    const auto tmp422 = -1 * tmp421;
    const auto tmp423 = tmp1[ 1 ] * ((tmp114[ 1 ])[ 1 ])[ 1 ];
    const auto tmp424 = (tmp50[ 1 ])[ 1 ] * (tmp50[ 1 ])[ 1 ];
    const auto tmp425 = tmp424 + tmp423;
    const auto tmp426 = tmp425 + tmp425;
    const auto tmp427 = tmp1[ 0 ] * ((tmp114[ 0 ])[ 1 ])[ 1 ];
    const auto tmp428 = (tmp50[ 0 ])[ 1 ] * (tmp50[ 0 ])[ 1 ];
    const auto tmp429 = tmp428 + tmp427;
    const auto tmp430 = tmp429 + tmp429;
    const auto tmp431 = tmp430 + tmp426;
    const auto tmp432 = tmp431 + tmp422;
    const auto tmp433 = tmp432 / tmp49;
    const auto tmp434 = tmp433 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp435 = tmp270 * tmp220;
    const auto tmp436 = -1 * tmp435;
    const auto tmp437 = ((tmp114[ 1 ])[ 1 ])[ 1 ] * tmp27;
    const auto tmp438 = tmp424 + tmp437;
    const auto tmp439 = tmp438 + tmp438;
    const auto tmp440 = tmp430 + tmp439;
    const auto tmp441 = tmp440 + tmp436;
    const auto tmp442 = tmp441 / tmp58;
    const auto tmp443 = -1 * tmp442;
    const auto tmp444 = tmp65 * tmp443;
    const auto tmp445 = tmp444 + tmp434;
    const auto tmp446 = tmp445 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp447 = tmp283 * tmp228;
    const auto tmp448 = -1 * tmp447;
    const auto tmp449 = ((tmp114[ 1 ])[ 1 ])[ 1 ] * tmp20;
    const auto tmp450 = tmp424 + tmp449;
    const auto tmp451 = tmp450 + tmp450;
    const auto tmp452 = tmp430 + tmp451;
    const auto tmp453 = tmp452 + tmp448;
    const auto tmp454 = tmp453 / tmp69;
    const auto tmp455 = -1 * tmp454;
    const auto tmp456 = tmp76 * tmp455;
    const auto tmp457 = tmp456 + tmp446;
    const auto tmp458 = tmp457 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp459 = tmp296 * tmp236;
    const auto tmp460 = -1 * tmp459;
    const auto tmp461 = ((tmp114[ 0 ])[ 1 ])[ 1 ] * tmp14;
    const auto tmp462 = tmp428 + tmp461;
    const auto tmp463 = tmp462 + tmp462;
    const auto tmp464 = tmp426 + tmp463;
    const auto tmp465 = tmp464 + tmp460;
    const auto tmp466 = tmp465 / tmp80;
    const auto tmp467 = tmp86 * tmp466;
    const auto tmp468 = tmp467 + tmp458;
    const auto tmp469 = tmp468 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp470 = tmp308 * tmp243;
    const auto tmp471 = -1 * tmp470;
    const auto tmp472 = ((tmp114[ 0 ])[ 1 ])[ 1 ] * tmp8;
    const auto tmp473 = tmp428 + tmp472;
    const auto tmp474 = tmp473 + tmp473;
    const auto tmp475 = tmp426 + tmp474;
    const auto tmp476 = tmp475 + tmp471;
    const auto tmp477 = tmp476 / tmp90;
    const auto tmp478 = tmp96 * tmp477;
    const auto tmp479 = tmp478 + tmp469;
    const auto tmp480 = tmp479 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp481 = tmp101 * tmp433;
    const auto tmp482 = tmp481 + tmp480;
    const auto tmp483 = 3 * tmp482;
    const auto tmp484 = tmp483 / tmp0;
    const auto tmp485 = tmp484 * tmp48;
    const auto tmp486 = tmp334 * tmp250;
    const auto tmp487 = tmp486 + tmp485;
    const auto tmp488 = -1 * tmp487;
    const auto tmp489 = 0.5 * tmp488;
    const auto tmp490 = -1 * tmp489;
    const auto tmp491 = tmp202 * tmp490;
    const auto tmp492 = tmp491 + tmp420;
    const auto tmp493 = tmp206 * tmp489;
    const auto tmp494 = tmp493 + tmp420;
    const auto tmp495 = tmp494 + tmp492;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp209;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp346;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp419;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp495;
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

  const Conepsilon &conepsilon () const
  {
    return *std::get< 0 >( constants_ );
  }

  Conepsilon &conepsilon ()
  {
    return *std::get< 0 >( constants_ );
  }

  template< std::size_t i, class Point >
  typename CoefficientFunctionSpaceType< i >::RangeType evaluateCoefficient ( const Point &x ) const
  {
    typename CoefficientFunctionSpaceType< i >::RangeType result;
    std::get< i >( coefficients_ ).evaluate( x, result );;
    return result;
  }

  template< std::size_t i, class Point >
  typename CoefficientFunctionSpaceType< i >::JacobianRangeType jacobianCoefficient ( const Point &x ) const
  {
    typename CoefficientFunctionSpaceType< i >::JacobianRangeType result;
    std::get< i >( coefficients_ ).jacobian( x, result );;
    return result;
  }

  template< std::size_t i, class Point >
  typename CoefficientFunctionSpaceType< i >::HessianRangeType hessianCoefficient ( const Point &x ) const
  {
    typename CoefficientFunctionSpaceType< i >::HessianRangeType result;
    std::get< i >( coefficients_ ).hessian( x, result );;
    return result;
  }
  ConstantTupleType constants_;
  std::tuple< Dune::Fem::ConstLocalFunction< Coeffbndproj > > coefficients_;
};

} // namespace UFLLocalFunctions_228c55d163ca194a905826bcc20fcbc0

PYBIND11_MODULE( localfunction_228c55d163ca194a905826bcc20fcbc0_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef UFLLocalFunctions_228c55d163ca194a905826bcc20fcbc0::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_228c55d163ca194a905826bcc20fcbc0::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_228c55d163ca194a905826bcc20fcbc0_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order, const Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > &coeffbndproj ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>(gridView),name,order, coeffbndproj); } ), pybind11::keep_alive< 1, 2 >(), pybind11::keep_alive< 1, 3 >() );
      cls.def_property( "epsilon", [] ( LocalFunctionType &self ) -> UFLLocalFunctions_228c55d163ca194a905826bcc20fcbc0::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > >::Conepsilon { return self.conepsilon(); }, [] ( LocalFunctionType &self, const UFLLocalFunctions_228c55d163ca194a905826bcc20fcbc0::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > >::Conepsilon &v ) { self.conepsilon() = v; } );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
