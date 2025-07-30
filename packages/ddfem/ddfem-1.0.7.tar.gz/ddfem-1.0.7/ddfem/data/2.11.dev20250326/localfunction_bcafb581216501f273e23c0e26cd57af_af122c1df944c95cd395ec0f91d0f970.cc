#ifndef GUARD_bcafb581216501f273e23c0e26cd57af
#define GUARD_bcafb581216501f273e23c0e26cd57af

#define USING_DUNE_PYTHON 1
#include <config.h>
#include <dune/alugrid/dgf.hh>
#include <dune/alugrid/grid.hh>
#include <dune/fem/gridpart/adaptiveleafgridpart.hh>
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

namespace UFLLocalFunctions_bcafb581216501f273e23c0e26cd57af
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
  typedef double Conepsilon;
  typedef std::tuple< std::shared_ptr< Conepsilon > > ConstantTupleType;
  template< std::size_t i >
  using ConstantsRangeType = typename std::tuple_element_t< i, ConstantTupleType >::element_type;
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
  {
    std::get< 0 >( constants_ ) = std::make_shared< Conepsilon >( (Conepsilon(0)) );
  }

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
    using std::tanh;
    double tmp0 = constant< 0 >();
    GlobalCoordinateType tmp1 = geometry().global( Dune::Fem::coordinate( x ) );
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
    GlobalCoordinateType tmp1 = geometry().global( Dune::Fem::coordinate( x ) );
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
    const auto tmp50 = tmp1[ 0 ] + tmp1[ 0 ];
    const auto tmp51 = tmp50 / tmp49;
    const auto tmp52 = tmp51 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp53 = 2 * tmp31;
    const auto tmp54 = tmp50 / tmp53;
    const auto tmp55 = -1 * tmp54;
    const auto tmp56 = -1 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp57 = 1.0 + tmp56;
    const auto tmp58 = tmp57 * tmp55;
    const auto tmp59 = tmp58 + tmp52;
    const auto tmp60 = tmp59 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp61 = 2 * tmp24;
    const auto tmp62 = tmp50 / tmp61;
    const auto tmp63 = -1 * tmp62;
    const auto tmp64 = -1 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp65 = 1.0 + tmp64;
    const auto tmp66 = tmp65 * tmp63;
    const auto tmp67 = tmp66 + tmp60;
    const auto tmp68 = tmp67 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp69 = 2 * tmp18;
    const auto tmp70 = tmp14 + tmp14;
    const auto tmp71 = tmp70 / tmp69;
    const auto tmp72 = -1 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp73 = 1.0 + tmp72;
    const auto tmp74 = tmp73 * tmp71;
    const auto tmp75 = tmp74 + tmp68;
    const auto tmp76 = tmp75 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp77 = 2 * tmp12;
    const auto tmp78 = tmp8 + tmp8;
    const auto tmp79 = tmp78 / tmp77;
    const auto tmp80 = -1 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp81 = 1.0 + tmp80;
    const auto tmp82 = tmp81 * tmp79;
    const auto tmp83 = tmp82 + tmp76;
    const auto tmp84 = tmp83 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp85 = -1 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp86 = 1.0 + tmp85;
    const auto tmp87 = tmp86 * tmp51;
    const auto tmp88 = tmp87 + tmp84;
    const auto tmp89 = 3 * tmp88;
    const auto tmp90 = tmp89 / tmp0;
    const auto tmp91 = tmp90 * tmp48;
    const auto tmp92 = -1 * tmp91;
    const auto tmp93 = 0.5 * tmp92;
    const auto tmp94 = std::tanh( tmp41 );
    const auto tmp95 = -1 * tmp94;
    const auto tmp96 = 1 + tmp95;
    const auto tmp97 = 0.5 * tmp96;
    const auto tmp98 = -1 * tmp97;
    const auto tmp99 = 1 + tmp98;
    const auto tmp100 = tmp99 * tmp93;
    const auto tmp101 = -1 * tmp93;
    const auto tmp102 = tmp97 * tmp101;
    const auto tmp103 = tmp102 + tmp100;
    const auto tmp104 = tmp1[ 1 ] + tmp1[ 1 ];
    const auto tmp105 = tmp104 / tmp49;
    const auto tmp106 = tmp105 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp107 = tmp27 + tmp27;
    const auto tmp108 = tmp107 / tmp53;
    const auto tmp109 = -1 * tmp108;
    const auto tmp110 = tmp57 * tmp109;
    const auto tmp111 = tmp110 + tmp106;
    const auto tmp112 = tmp111 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp113 = tmp20 + tmp20;
    const auto tmp114 = tmp113 / tmp61;
    const auto tmp115 = -1 * tmp114;
    const auto tmp116 = tmp65 * tmp115;
    const auto tmp117 = tmp116 + tmp112;
    const auto tmp118 = tmp117 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp119 = tmp104 / tmp69;
    const auto tmp120 = tmp73 * tmp119;
    const auto tmp121 = tmp120 + tmp118;
    const auto tmp122 = tmp121 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp123 = tmp104 / tmp77;
    const auto tmp124 = tmp81 * tmp123;
    const auto tmp125 = tmp124 + tmp122;
    const auto tmp126 = tmp125 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp127 = tmp86 * tmp105;
    const auto tmp128 = tmp127 + tmp126;
    const auto tmp129 = 3 * tmp128;
    const auto tmp130 = tmp129 / tmp0;
    const auto tmp131 = tmp130 * tmp48;
    const auto tmp132 = -1 * tmp131;
    const auto tmp133 = 0.5 * tmp132;
    const auto tmp134 = tmp99 * tmp133;
    const auto tmp135 = -1 * tmp133;
    const auto tmp136 = tmp97 * tmp135;
    const auto tmp137 = tmp136 + tmp134;
    (result[ 0 ])[ 0 ] = tmp103;
    (result[ 0 ])[ 1 ] = tmp137;
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
    GlobalCoordinateType tmp1 = geometry().global( Dune::Fem::coordinate( x ) );
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
    const auto tmp50 = tmp1[ 0 ] + tmp1[ 0 ];
    const auto tmp51 = tmp50 / tmp49;
    const auto tmp52 = tmp51 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp53 = 2 * tmp31;
    const auto tmp54 = tmp50 / tmp53;
    const auto tmp55 = -1 * tmp54;
    const auto tmp56 = -1 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp57 = 1.0 + tmp56;
    const auto tmp58 = tmp57 * tmp55;
    const auto tmp59 = tmp58 + tmp52;
    const auto tmp60 = tmp59 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp61 = 2 * tmp24;
    const auto tmp62 = tmp50 / tmp61;
    const auto tmp63 = -1 * tmp62;
    const auto tmp64 = -1 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp65 = 1.0 + tmp64;
    const auto tmp66 = tmp65 * tmp63;
    const auto tmp67 = tmp66 + tmp60;
    const auto tmp68 = tmp67 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp69 = 2 * tmp18;
    const auto tmp70 = tmp14 + tmp14;
    const auto tmp71 = tmp70 / tmp69;
    const auto tmp72 = -1 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp73 = 1.0 + tmp72;
    const auto tmp74 = tmp73 * tmp71;
    const auto tmp75 = tmp74 + tmp68;
    const auto tmp76 = tmp75 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp77 = 2 * tmp12;
    const auto tmp78 = tmp8 + tmp8;
    const auto tmp79 = tmp78 / tmp77;
    const auto tmp80 = -1 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp81 = 1.0 + tmp80;
    const auto tmp82 = tmp81 * tmp79;
    const auto tmp83 = tmp82 + tmp76;
    const auto tmp84 = tmp83 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp85 = -1 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp86 = 1.0 + tmp85;
    const auto tmp87 = tmp86 * tmp51;
    const auto tmp88 = tmp87 + tmp84;
    const auto tmp89 = 3 * tmp88;
    const auto tmp90 = tmp89 / tmp0;
    const auto tmp91 = tmp90 * tmp48;
    const auto tmp92 = -1 * tmp91;
    const auto tmp93 = 0.5 * tmp92;
    const auto tmp94 = -1 * tmp93;
    const auto tmp95 = tmp94 * tmp93;
    const auto tmp96 = 2 * tmp51;
    const auto tmp97 = tmp96 * tmp51;
    const auto tmp98 = -1 * tmp97;
    const auto tmp99 = 2 + tmp98;
    const auto tmp100 = tmp99 / tmp49;
    const auto tmp101 = tmp100 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp102 = 2 * tmp54;
    const auto tmp103 = tmp102 * tmp54;
    const auto tmp104 = -1 * tmp103;
    const auto tmp105 = 2 + tmp104;
    const auto tmp106 = tmp105 / tmp53;
    const auto tmp107 = -1 * tmp106;
    const auto tmp108 = tmp57 * tmp107;
    const auto tmp109 = tmp108 + tmp101;
    const auto tmp110 = tmp109 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp111 = 2 * tmp62;
    const auto tmp112 = tmp111 * tmp62;
    const auto tmp113 = -1 * tmp112;
    const auto tmp114 = 2 + tmp113;
    const auto tmp115 = tmp114 / tmp61;
    const auto tmp116 = -1 * tmp115;
    const auto tmp117 = tmp65 * tmp116;
    const auto tmp118 = tmp117 + tmp110;
    const auto tmp119 = tmp118 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp120 = 2 * tmp71;
    const auto tmp121 = tmp120 * tmp71;
    const auto tmp122 = -1 * tmp121;
    const auto tmp123 = 2 + tmp122;
    const auto tmp124 = tmp123 / tmp69;
    const auto tmp125 = tmp73 * tmp124;
    const auto tmp126 = tmp125 + tmp119;
    const auto tmp127 = tmp126 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp128 = 2 * tmp79;
    const auto tmp129 = tmp128 * tmp79;
    const auto tmp130 = -1 * tmp129;
    const auto tmp131 = 2 + tmp130;
    const auto tmp132 = tmp131 / tmp77;
    const auto tmp133 = tmp81 * tmp132;
    const auto tmp134 = tmp133 + tmp127;
    const auto tmp135 = tmp134 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp136 = tmp86 * tmp100;
    const auto tmp137 = tmp136 + tmp135;
    const auto tmp138 = 3 * tmp137;
    const auto tmp139 = tmp138 / tmp0;
    const auto tmp140 = tmp139 * tmp48;
    const auto tmp141 = std::sinh( tmp41 );
    const auto tmp142 = tmp90 * tmp141;
    const auto tmp143 = 2.0 * tmp142;
    const auto tmp144 = std::sinh( tmp42 );
    const auto tmp145 = 2.0 * tmp90;
    const auto tmp146 = tmp145 * tmp144;
    const auto tmp147 = tmp146 * tmp47;
    const auto tmp148 = -1 * tmp147;
    const auto tmp149 = tmp148 + tmp143;
    const auto tmp150 = tmp149 / tmp44;
    const auto tmp151 = 2 * tmp150;
    const auto tmp152 = tmp151 * tmp47;
    const auto tmp153 = tmp152 * tmp90;
    const auto tmp154 = tmp153 + tmp140;
    const auto tmp155 = -1 * tmp154;
    const auto tmp156 = 0.5 * tmp155;
    const auto tmp157 = -1 * tmp156;
    const auto tmp158 = std::tanh( tmp41 );
    const auto tmp159 = -1 * tmp158;
    const auto tmp160 = 1 + tmp159;
    const auto tmp161 = 0.5 * tmp160;
    const auto tmp162 = tmp161 * tmp157;
    const auto tmp163 = tmp162 + tmp95;
    const auto tmp164 = -1 * tmp161;
    const auto tmp165 = 1 + tmp164;
    const auto tmp166 = tmp165 * tmp156;
    const auto tmp167 = tmp166 + tmp95;
    const auto tmp168 = tmp167 + tmp163;
    const auto tmp169 = tmp1[ 1 ] + tmp1[ 1 ];
    const auto tmp170 = tmp169 / tmp49;
    const auto tmp171 = tmp170 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp172 = tmp27 + tmp27;
    const auto tmp173 = tmp172 / tmp53;
    const auto tmp174 = -1 * tmp173;
    const auto tmp175 = tmp57 * tmp174;
    const auto tmp176 = tmp175 + tmp171;
    const auto tmp177 = tmp176 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp178 = tmp20 + tmp20;
    const auto tmp179 = tmp178 / tmp61;
    const auto tmp180 = -1 * tmp179;
    const auto tmp181 = tmp65 * tmp180;
    const auto tmp182 = tmp181 + tmp177;
    const auto tmp183 = tmp182 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp184 = tmp169 / tmp69;
    const auto tmp185 = tmp73 * tmp184;
    const auto tmp186 = tmp185 + tmp183;
    const auto tmp187 = tmp186 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp188 = tmp169 / tmp77;
    const auto tmp189 = tmp81 * tmp188;
    const auto tmp190 = tmp189 + tmp187;
    const auto tmp191 = tmp190 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp192 = tmp86 * tmp170;
    const auto tmp193 = tmp192 + tmp191;
    const auto tmp194 = 3 * tmp193;
    const auto tmp195 = tmp194 / tmp0;
    const auto tmp196 = tmp195 * tmp48;
    const auto tmp197 = -1 * tmp196;
    const auto tmp198 = 0.5 * tmp197;
    const auto tmp199 = tmp94 * tmp198;
    const auto tmp200 = 2 * tmp170;
    const auto tmp201 = tmp200 * tmp51;
    const auto tmp202 = -1 * tmp201;
    const auto tmp203 = tmp202 / tmp49;
    const auto tmp204 = tmp203 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp205 = 2 * tmp173;
    const auto tmp206 = tmp205 * tmp54;
    const auto tmp207 = -1 * tmp206;
    const auto tmp208 = tmp207 / tmp53;
    const auto tmp209 = -1 * tmp208;
    const auto tmp210 = tmp57 * tmp209;
    const auto tmp211 = tmp210 + tmp204;
    const auto tmp212 = tmp211 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp213 = 2 * tmp179;
    const auto tmp214 = tmp213 * tmp62;
    const auto tmp215 = -1 * tmp214;
    const auto tmp216 = tmp215 / tmp61;
    const auto tmp217 = -1 * tmp216;
    const auto tmp218 = tmp65 * tmp217;
    const auto tmp219 = tmp218 + tmp212;
    const auto tmp220 = tmp219 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp221 = 2 * tmp184;
    const auto tmp222 = tmp221 * tmp71;
    const auto tmp223 = -1 * tmp222;
    const auto tmp224 = tmp223 / tmp69;
    const auto tmp225 = tmp73 * tmp224;
    const auto tmp226 = tmp225 + tmp220;
    const auto tmp227 = tmp226 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp228 = 2 * tmp188;
    const auto tmp229 = tmp228 * tmp79;
    const auto tmp230 = -1 * tmp229;
    const auto tmp231 = tmp230 / tmp77;
    const auto tmp232 = tmp81 * tmp231;
    const auto tmp233 = tmp232 + tmp227;
    const auto tmp234 = tmp233 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp235 = tmp86 * tmp203;
    const auto tmp236 = tmp235 + tmp234;
    const auto tmp237 = 3 * tmp236;
    const auto tmp238 = tmp237 / tmp0;
    const auto tmp239 = tmp238 * tmp48;
    const auto tmp240 = tmp195 * tmp141;
    const auto tmp241 = 2.0 * tmp240;
    const auto tmp242 = 2.0 * tmp195;
    const auto tmp243 = tmp242 * tmp144;
    const auto tmp244 = tmp243 * tmp47;
    const auto tmp245 = -1 * tmp244;
    const auto tmp246 = tmp245 + tmp241;
    const auto tmp247 = tmp246 / tmp44;
    const auto tmp248 = 2 * tmp247;
    const auto tmp249 = tmp248 * tmp47;
    const auto tmp250 = tmp249 * tmp90;
    const auto tmp251 = tmp250 + tmp239;
    const auto tmp252 = -1 * tmp251;
    const auto tmp253 = 0.5 * tmp252;
    const auto tmp254 = -1 * tmp253;
    const auto tmp255 = tmp161 * tmp254;
    const auto tmp256 = tmp255 + tmp199;
    const auto tmp257 = -1 * tmp198;
    const auto tmp258 = tmp257 * tmp93;
    const auto tmp259 = tmp165 * tmp253;
    const auto tmp260 = tmp259 + tmp258;
    const auto tmp261 = tmp260 + tmp256;
    const auto tmp262 = tmp96 * tmp170;
    const auto tmp263 = -1 * tmp262;
    const auto tmp264 = tmp263 / tmp49;
    const auto tmp265 = tmp264 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp266 = tmp102 * tmp173;
    const auto tmp267 = -1 * tmp266;
    const auto tmp268 = tmp267 / tmp53;
    const auto tmp269 = -1 * tmp268;
    const auto tmp270 = tmp57 * tmp269;
    const auto tmp271 = tmp270 + tmp265;
    const auto tmp272 = tmp271 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp273 = tmp111 * tmp179;
    const auto tmp274 = -1 * tmp273;
    const auto tmp275 = tmp274 / tmp61;
    const auto tmp276 = -1 * tmp275;
    const auto tmp277 = tmp65 * tmp276;
    const auto tmp278 = tmp277 + tmp272;
    const auto tmp279 = tmp278 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp280 = tmp120 * tmp184;
    const auto tmp281 = -1 * tmp280;
    const auto tmp282 = tmp281 / tmp69;
    const auto tmp283 = tmp73 * tmp282;
    const auto tmp284 = tmp283 + tmp279;
    const auto tmp285 = tmp284 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp286 = tmp128 * tmp188;
    const auto tmp287 = -1 * tmp286;
    const auto tmp288 = tmp287 / tmp77;
    const auto tmp289 = tmp81 * tmp288;
    const auto tmp290 = tmp289 + tmp285;
    const auto tmp291 = tmp290 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp292 = tmp86 * tmp264;
    const auto tmp293 = tmp292 + tmp291;
    const auto tmp294 = 3 * tmp293;
    const auto tmp295 = tmp294 / tmp0;
    const auto tmp296 = tmp295 * tmp48;
    const auto tmp297 = tmp152 * tmp195;
    const auto tmp298 = tmp297 + tmp296;
    const auto tmp299 = -1 * tmp298;
    const auto tmp300 = 0.5 * tmp299;
    const auto tmp301 = tmp165 * tmp300;
    const auto tmp302 = tmp301 + tmp199;
    const auto tmp303 = -1 * tmp300;
    const auto tmp304 = tmp161 * tmp303;
    const auto tmp305 = tmp304 + tmp258;
    const auto tmp306 = tmp305 + tmp302;
    const auto tmp307 = tmp257 * tmp198;
    const auto tmp308 = tmp200 * tmp170;
    const auto tmp309 = -1 * tmp308;
    const auto tmp310 = 2 + tmp309;
    const auto tmp311 = tmp310 / tmp49;
    const auto tmp312 = tmp311 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp313 = tmp205 * tmp173;
    const auto tmp314 = -1 * tmp313;
    const auto tmp315 = 2 + tmp314;
    const auto tmp316 = tmp315 / tmp53;
    const auto tmp317 = -1 * tmp316;
    const auto tmp318 = tmp57 * tmp317;
    const auto tmp319 = tmp318 + tmp312;
    const auto tmp320 = tmp319 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp321 = tmp213 * tmp179;
    const auto tmp322 = -1 * tmp321;
    const auto tmp323 = 2 + tmp322;
    const auto tmp324 = tmp323 / tmp61;
    const auto tmp325 = -1 * tmp324;
    const auto tmp326 = tmp65 * tmp325;
    const auto tmp327 = tmp326 + tmp320;
    const auto tmp328 = tmp327 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp329 = tmp221 * tmp184;
    const auto tmp330 = -1 * tmp329;
    const auto tmp331 = 2 + tmp330;
    const auto tmp332 = tmp331 / tmp69;
    const auto tmp333 = tmp73 * tmp332;
    const auto tmp334 = tmp333 + tmp328;
    const auto tmp335 = tmp334 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp336 = tmp228 * tmp188;
    const auto tmp337 = -1 * tmp336;
    const auto tmp338 = 2 + tmp337;
    const auto tmp339 = tmp338 / tmp77;
    const auto tmp340 = tmp81 * tmp339;
    const auto tmp341 = tmp340 + tmp335;
    const auto tmp342 = tmp341 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp343 = tmp86 * tmp311;
    const auto tmp344 = tmp343 + tmp342;
    const auto tmp345 = 3 * tmp344;
    const auto tmp346 = tmp345 / tmp0;
    const auto tmp347 = tmp346 * tmp48;
    const auto tmp348 = tmp249 * tmp195;
    const auto tmp349 = tmp348 + tmp347;
    const auto tmp350 = -1 * tmp349;
    const auto tmp351 = 0.5 * tmp350;
    const auto tmp352 = -1 * tmp351;
    const auto tmp353 = tmp161 * tmp352;
    const auto tmp354 = tmp353 + tmp307;
    const auto tmp355 = tmp165 * tmp351;
    const auto tmp356 = tmp355 + tmp307;
    const auto tmp357 = tmp356 + tmp354;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp168;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp261;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp306;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp357;
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
  ConstantTupleType constants_;
  std::tuple<  > coefficients_;
};

} // namespace UFLLocalFunctions_bcafb581216501f273e23c0e26cd57af

PYBIND11_MODULE( localfunction_bcafb581216501f273e23c0e26cd57af_af122c1df944c95cd395ec0f91d0f970, module )
{
  typedef UFLLocalFunctions_bcafb581216501f273e23c0e26cd57af::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_bcafb581216501f273e23c0e26cd57af::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_bcafb581216501f273e23c0e26cd57af_af122c1df944c95cd395ec0f91d0f970.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > >>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property( "epsilon", [] ( LocalFunctionType &self ) -> UFLLocalFunctions_bcafb581216501f273e23c0e26cd57af::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >::Conepsilon { return self.conepsilon(); }, [] ( LocalFunctionType &self, const UFLLocalFunctions_bcafb581216501f273e23c0e26cd57af::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >::Conepsilon &v ) { self.conepsilon() = v; } );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
