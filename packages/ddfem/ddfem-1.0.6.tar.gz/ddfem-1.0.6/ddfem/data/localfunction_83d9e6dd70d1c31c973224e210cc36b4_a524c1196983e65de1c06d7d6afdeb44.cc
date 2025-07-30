#ifndef GUARD_83d9e6dd70d1c31c973224e210cc36b4
#define GUARD_83d9e6dd70d1c31c973224e210cc36b4

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

namespace UFLLocalFunctions_83d9e6dd70d1c31c973224e210cc36b4
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
    const auto tmp46 = 0.9999999999 * tmp45;
    const auto tmp47 = 1e-10 + tmp46;
    result[ 0 ] = tmp47;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::cosh;
    using std::max;
    using std::min;
    using std::pow;
    using std::sqrt;
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
    const auto tmp94 = 0.9999999999 * tmp93;
    const auto tmp95 = tmp1[ 1 ] + tmp1[ 1 ];
    const auto tmp96 = tmp95 / tmp49;
    const auto tmp97 = tmp96 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp98 = tmp27 + tmp27;
    const auto tmp99 = tmp98 / tmp53;
    const auto tmp100 = -1 * tmp99;
    const auto tmp101 = tmp57 * tmp100;
    const auto tmp102 = tmp101 + tmp97;
    const auto tmp103 = tmp102 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp104 = tmp20 + tmp20;
    const auto tmp105 = tmp104 / tmp61;
    const auto tmp106 = -1 * tmp105;
    const auto tmp107 = tmp65 * tmp106;
    const auto tmp108 = tmp107 + tmp103;
    const auto tmp109 = tmp108 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp110 = tmp95 / tmp69;
    const auto tmp111 = tmp73 * tmp110;
    const auto tmp112 = tmp111 + tmp109;
    const auto tmp113 = tmp112 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp114 = tmp95 / tmp77;
    const auto tmp115 = tmp81 * tmp114;
    const auto tmp116 = tmp115 + tmp113;
    const auto tmp117 = tmp116 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp118 = tmp86 * tmp96;
    const auto tmp119 = tmp118 + tmp117;
    const auto tmp120 = 3 * tmp119;
    const auto tmp121 = tmp120 / tmp0;
    const auto tmp122 = tmp121 * tmp48;
    const auto tmp123 = -1 * tmp122;
    const auto tmp124 = 0.5 * tmp123;
    const auto tmp125 = 0.9999999999 * tmp124;
    (result[ 0 ])[ 0 ] = tmp94;
    (result[ 0 ])[ 1 ] = tmp125;
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
    const auto tmp52 = 2 * tmp51;
    const auto tmp53 = tmp52 * tmp51;
    const auto tmp54 = -1 * tmp53;
    const auto tmp55 = 2 + tmp54;
    const auto tmp56 = tmp55 / tmp49;
    const auto tmp57 = tmp56 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp58 = 2 * tmp31;
    const auto tmp59 = tmp50 / tmp58;
    const auto tmp60 = 2 * tmp59;
    const auto tmp61 = tmp60 * tmp59;
    const auto tmp62 = -1 * tmp61;
    const auto tmp63 = 2 + tmp62;
    const auto tmp64 = tmp63 / tmp58;
    const auto tmp65 = -1 * tmp64;
    const auto tmp66 = -1 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp67 = 1.0 + tmp66;
    const auto tmp68 = tmp67 * tmp65;
    const auto tmp69 = tmp68 + tmp57;
    const auto tmp70 = tmp69 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp71 = 2 * tmp24;
    const auto tmp72 = tmp50 / tmp71;
    const auto tmp73 = 2 * tmp72;
    const auto tmp74 = tmp73 * tmp72;
    const auto tmp75 = -1 * tmp74;
    const auto tmp76 = 2 + tmp75;
    const auto tmp77 = tmp76 / tmp71;
    const auto tmp78 = -1 * tmp77;
    const auto tmp79 = -1 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp80 = 1.0 + tmp79;
    const auto tmp81 = tmp80 * tmp78;
    const auto tmp82 = tmp81 + tmp70;
    const auto tmp83 = tmp82 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp84 = 2 * tmp18;
    const auto tmp85 = tmp14 + tmp14;
    const auto tmp86 = tmp85 / tmp84;
    const auto tmp87 = 2 * tmp86;
    const auto tmp88 = tmp87 * tmp86;
    const auto tmp89 = -1 * tmp88;
    const auto tmp90 = 2 + tmp89;
    const auto tmp91 = tmp90 / tmp84;
    const auto tmp92 = -1 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp93 = 1.0 + tmp92;
    const auto tmp94 = tmp93 * tmp91;
    const auto tmp95 = tmp94 + tmp83;
    const auto tmp96 = tmp95 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp97 = 2 * tmp12;
    const auto tmp98 = tmp8 + tmp8;
    const auto tmp99 = tmp98 / tmp97;
    const auto tmp100 = 2 * tmp99;
    const auto tmp101 = tmp100 * tmp99;
    const auto tmp102 = -1 * tmp101;
    const auto tmp103 = 2 + tmp102;
    const auto tmp104 = tmp103 / tmp97;
    const auto tmp105 = -1 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp106 = 1.0 + tmp105;
    const auto tmp107 = tmp106 * tmp104;
    const auto tmp108 = tmp107 + tmp96;
    const auto tmp109 = tmp108 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp110 = -1 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp111 = 1.0 + tmp110;
    const auto tmp112 = tmp111 * tmp56;
    const auto tmp113 = tmp112 + tmp109;
    const auto tmp114 = 3 * tmp113;
    const auto tmp115 = tmp114 / tmp0;
    const auto tmp116 = tmp115 * tmp48;
    const auto tmp117 = tmp51 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp118 = -1 * tmp59;
    const auto tmp119 = tmp67 * tmp118;
    const auto tmp120 = tmp119 + tmp117;
    const auto tmp121 = tmp120 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp122 = -1 * tmp72;
    const auto tmp123 = tmp80 * tmp122;
    const auto tmp124 = tmp123 + tmp121;
    const auto tmp125 = tmp124 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp126 = tmp93 * tmp86;
    const auto tmp127 = tmp126 + tmp125;
    const auto tmp128 = tmp127 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp129 = tmp106 * tmp99;
    const auto tmp130 = tmp129 + tmp128;
    const auto tmp131 = tmp130 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp132 = tmp111 * tmp51;
    const auto tmp133 = tmp132 + tmp131;
    const auto tmp134 = 3 * tmp133;
    const auto tmp135 = tmp134 / tmp0;
    const auto tmp136 = std::sinh( tmp41 );
    const auto tmp137 = tmp135 * tmp136;
    const auto tmp138 = 2.0 * tmp137;
    const auto tmp139 = std::sinh( tmp42 );
    const auto tmp140 = 2.0 * tmp135;
    const auto tmp141 = tmp140 * tmp139;
    const auto tmp142 = tmp141 * tmp47;
    const auto tmp143 = -1 * tmp142;
    const auto tmp144 = tmp143 + tmp138;
    const auto tmp145 = tmp144 / tmp44;
    const auto tmp146 = 2 * tmp145;
    const auto tmp147 = tmp146 * tmp47;
    const auto tmp148 = tmp147 * tmp135;
    const auto tmp149 = tmp148 + tmp116;
    const auto tmp150 = -1 * tmp149;
    const auto tmp151 = 0.5 * tmp150;
    const auto tmp152 = 0.9999999999 * tmp151;
    const auto tmp153 = tmp1[ 1 ] + tmp1[ 1 ];
    const auto tmp154 = tmp153 / tmp49;
    const auto tmp155 = 2 * tmp154;
    const auto tmp156 = tmp155 * tmp51;
    const auto tmp157 = -1 * tmp156;
    const auto tmp158 = tmp157 / tmp49;
    const auto tmp159 = tmp158 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp160 = tmp27 + tmp27;
    const auto tmp161 = tmp160 / tmp58;
    const auto tmp162 = 2 * tmp161;
    const auto tmp163 = tmp162 * tmp59;
    const auto tmp164 = -1 * tmp163;
    const auto tmp165 = tmp164 / tmp58;
    const auto tmp166 = -1 * tmp165;
    const auto tmp167 = tmp67 * tmp166;
    const auto tmp168 = tmp167 + tmp159;
    const auto tmp169 = tmp168 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp170 = tmp20 + tmp20;
    const auto tmp171 = tmp170 / tmp71;
    const auto tmp172 = 2 * tmp171;
    const auto tmp173 = tmp172 * tmp72;
    const auto tmp174 = -1 * tmp173;
    const auto tmp175 = tmp174 / tmp71;
    const auto tmp176 = -1 * tmp175;
    const auto tmp177 = tmp80 * tmp176;
    const auto tmp178 = tmp177 + tmp169;
    const auto tmp179 = tmp178 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp180 = tmp153 / tmp84;
    const auto tmp181 = 2 * tmp180;
    const auto tmp182 = tmp181 * tmp86;
    const auto tmp183 = -1 * tmp182;
    const auto tmp184 = tmp183 / tmp84;
    const auto tmp185 = tmp93 * tmp184;
    const auto tmp186 = tmp185 + tmp179;
    const auto tmp187 = tmp186 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp188 = tmp153 / tmp97;
    const auto tmp189 = 2 * tmp188;
    const auto tmp190 = tmp189 * tmp99;
    const auto tmp191 = -1 * tmp190;
    const auto tmp192 = tmp191 / tmp97;
    const auto tmp193 = tmp106 * tmp192;
    const auto tmp194 = tmp193 + tmp187;
    const auto tmp195 = tmp194 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp196 = tmp111 * tmp158;
    const auto tmp197 = tmp196 + tmp195;
    const auto tmp198 = 3 * tmp197;
    const auto tmp199 = tmp198 / tmp0;
    const auto tmp200 = tmp199 * tmp48;
    const auto tmp201 = tmp154 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp202 = -1 * tmp161;
    const auto tmp203 = tmp67 * tmp202;
    const auto tmp204 = tmp203 + tmp201;
    const auto tmp205 = tmp204 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp206 = -1 * tmp171;
    const auto tmp207 = tmp80 * tmp206;
    const auto tmp208 = tmp207 + tmp205;
    const auto tmp209 = tmp208 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp210 = tmp93 * tmp180;
    const auto tmp211 = tmp210 + tmp209;
    const auto tmp212 = tmp211 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp213 = tmp106 * tmp188;
    const auto tmp214 = tmp213 + tmp212;
    const auto tmp215 = tmp214 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp216 = tmp111 * tmp154;
    const auto tmp217 = tmp216 + tmp215;
    const auto tmp218 = 3 * tmp217;
    const auto tmp219 = tmp218 / tmp0;
    const auto tmp220 = tmp219 * tmp136;
    const auto tmp221 = 2.0 * tmp220;
    const auto tmp222 = 2.0 * tmp219;
    const auto tmp223 = tmp222 * tmp139;
    const auto tmp224 = tmp223 * tmp47;
    const auto tmp225 = -1 * tmp224;
    const auto tmp226 = tmp225 + tmp221;
    const auto tmp227 = tmp226 / tmp44;
    const auto tmp228 = 2 * tmp227;
    const auto tmp229 = tmp228 * tmp47;
    const auto tmp230 = tmp229 * tmp135;
    const auto tmp231 = tmp230 + tmp200;
    const auto tmp232 = -1 * tmp231;
    const auto tmp233 = 0.5 * tmp232;
    const auto tmp234 = 0.9999999999 * tmp233;
    const auto tmp235 = tmp52 * tmp154;
    const auto tmp236 = -1 * tmp235;
    const auto tmp237 = tmp236 / tmp49;
    const auto tmp238 = tmp237 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp239 = tmp60 * tmp161;
    const auto tmp240 = -1 * tmp239;
    const auto tmp241 = tmp240 / tmp58;
    const auto tmp242 = -1 * tmp241;
    const auto tmp243 = tmp67 * tmp242;
    const auto tmp244 = tmp243 + tmp238;
    const auto tmp245 = tmp244 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp246 = tmp73 * tmp171;
    const auto tmp247 = -1 * tmp246;
    const auto tmp248 = tmp247 / tmp71;
    const auto tmp249 = -1 * tmp248;
    const auto tmp250 = tmp80 * tmp249;
    const auto tmp251 = tmp250 + tmp245;
    const auto tmp252 = tmp251 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp253 = tmp87 * tmp180;
    const auto tmp254 = -1 * tmp253;
    const auto tmp255 = tmp254 / tmp84;
    const auto tmp256 = tmp93 * tmp255;
    const auto tmp257 = tmp256 + tmp252;
    const auto tmp258 = tmp257 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp259 = tmp100 * tmp188;
    const auto tmp260 = -1 * tmp259;
    const auto tmp261 = tmp260 / tmp97;
    const auto tmp262 = tmp106 * tmp261;
    const auto tmp263 = tmp262 + tmp258;
    const auto tmp264 = tmp263 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp265 = tmp111 * tmp237;
    const auto tmp266 = tmp265 + tmp264;
    const auto tmp267 = 3 * tmp266;
    const auto tmp268 = tmp267 / tmp0;
    const auto tmp269 = tmp268 * tmp48;
    const auto tmp270 = tmp147 * tmp219;
    const auto tmp271 = tmp270 + tmp269;
    const auto tmp272 = -1 * tmp271;
    const auto tmp273 = 0.5 * tmp272;
    const auto tmp274 = 0.9999999999 * tmp273;
    const auto tmp275 = tmp155 * tmp154;
    const auto tmp276 = -1 * tmp275;
    const auto tmp277 = 2 + tmp276;
    const auto tmp278 = tmp277 / tmp49;
    const auto tmp279 = tmp278 * (tmp34 > tmp33 ? 1 : 0.0);
    const auto tmp280 = tmp162 * tmp161;
    const auto tmp281 = -1 * tmp280;
    const auto tmp282 = 2 + tmp281;
    const auto tmp283 = tmp282 / tmp58;
    const auto tmp284 = -1 * tmp283;
    const auto tmp285 = tmp67 * tmp284;
    const auto tmp286 = tmp285 + tmp279;
    const auto tmp287 = tmp286 * (tmp35 > tmp26 ? 1 : 0.0);
    const auto tmp288 = tmp172 * tmp171;
    const auto tmp289 = -1 * tmp288;
    const auto tmp290 = 2 + tmp289;
    const auto tmp291 = tmp290 / tmp71;
    const auto tmp292 = -1 * tmp291;
    const auto tmp293 = tmp80 * tmp292;
    const auto tmp294 = tmp293 + tmp287;
    const auto tmp295 = tmp294 * (tmp36 < tmp19 ? 1 : 0.0);
    const auto tmp296 = tmp181 * tmp180;
    const auto tmp297 = -1 * tmp296;
    const auto tmp298 = 2 + tmp297;
    const auto tmp299 = tmp298 / tmp84;
    const auto tmp300 = tmp93 * tmp299;
    const auto tmp301 = tmp300 + tmp295;
    const auto tmp302 = tmp301 * (tmp37 < tmp13 ? 1 : 0.0);
    const auto tmp303 = tmp189 * tmp188;
    const auto tmp304 = -1 * tmp303;
    const auto tmp305 = 2 + tmp304;
    const auto tmp306 = tmp305 / tmp97;
    const auto tmp307 = tmp106 * tmp306;
    const auto tmp308 = tmp307 + tmp302;
    const auto tmp309 = tmp308 * (tmp38 > tmp7 ? 1 : 0.0);
    const auto tmp310 = tmp111 * tmp278;
    const auto tmp311 = tmp310 + tmp309;
    const auto tmp312 = 3 * tmp311;
    const auto tmp313 = tmp312 / tmp0;
    const auto tmp314 = tmp313 * tmp48;
    const auto tmp315 = tmp229 * tmp219;
    const auto tmp316 = tmp315 + tmp314;
    const auto tmp317 = -1 * tmp316;
    const auto tmp318 = 0.5 * tmp317;
    const auto tmp319 = 0.9999999999 * tmp318;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp152;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp234;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp274;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp319;
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

} // namespace UFLLocalFunctions_83d9e6dd70d1c31c973224e210cc36b4

PYBIND11_MODULE( localfunction_83d9e6dd70d1c31c973224e210cc36b4_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef UFLLocalFunctions_83d9e6dd70d1c31c973224e210cc36b4::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_83d9e6dd70d1c31c973224e210cc36b4::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_83d9e6dd70d1c31c973224e210cc36b4_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property( "epsilon", [] ( LocalFunctionType &self ) -> UFLLocalFunctions_83d9e6dd70d1c31c973224e210cc36b4::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > >::Conepsilon { return self.conepsilon(); }, [] ( LocalFunctionType &self, const UFLLocalFunctions_83d9e6dd70d1c31c973224e210cc36b4::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > >::Conepsilon &v ) { self.conepsilon() = v; } );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
