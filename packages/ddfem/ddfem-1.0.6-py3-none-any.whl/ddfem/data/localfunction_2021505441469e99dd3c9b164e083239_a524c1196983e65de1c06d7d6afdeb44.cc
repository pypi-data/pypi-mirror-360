#ifndef GUARD_2021505441469e99dd3c9b164e083239
#define GUARD_2021505441469e99dd3c9b164e083239

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

namespace UFLLocalFunctions_2021505441469e99dd3c9b164e083239
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
    using std::tanh;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp2 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp3 = tmp2 + tmp1;
    const auto tmp4 = 1e-10 + tmp3;
    const auto tmp5 = std::sqrt( tmp4 );
    const auto tmp6 = -1.4 + tmp5;
    const auto tmp7 = 1 + tmp0[ 0 ];
    const auto tmp8 = tmp7 * tmp7;
    const auto tmp9 = tmp1 + tmp8;
    const auto tmp10 = 1e-10 + tmp9;
    const auto tmp11 = std::sqrt( tmp10 );
    const auto tmp12 = -0.5 + tmp11;
    const auto tmp13 = -1 + tmp0[ 0 ];
    const auto tmp14 = tmp13 * tmp13;
    const auto tmp15 = tmp1 + tmp14;
    const auto tmp16 = 1e-10 + tmp15;
    const auto tmp17 = std::sqrt( tmp16 );
    const auto tmp18 = -0.5 + tmp17;
    const auto tmp19 = 0.8 + tmp0[ 1 ];
    const auto tmp20 = tmp19 * tmp19;
    const auto tmp21 = tmp2 + tmp20;
    const auto tmp22 = 1e-10 + tmp21;
    const auto tmp23 = std::sqrt( tmp22 );
    const auto tmp24 = -0.5 + tmp23;
    const auto tmp25 = -1 * tmp24;
    const auto tmp26 = -0.8 + tmp0[ 1 ];
    const auto tmp27 = tmp26 * tmp26;
    const auto tmp28 = tmp2 + tmp27;
    const auto tmp29 = 1e-10 + tmp28;
    const auto tmp30 = std::sqrt( tmp29 );
    const auto tmp31 = -0.5 + tmp30;
    const auto tmp32 = -1 * tmp31;
    const auto tmp33 = -1 + tmp5;
    const auto tmp34 = std::max( tmp33, tmp32 );
    const auto tmp35 = std::max( tmp34, tmp25 );
    const auto tmp36 = std::min( tmp35, tmp18 );
    const auto tmp37 = std::min( tmp36, tmp12 );
    const auto tmp38 = std::max( tmp37, tmp6 );
    const auto tmp39 = 3 * tmp38;
    const auto tmp40 = tmp39 / 0.140625;
    const auto tmp41 = std::tanh( tmp40 );
    const auto tmp42 = -1 * tmp41;
    const auto tmp43 = 1 + tmp42;
    const auto tmp44 = 0.5 * tmp43;
    result[ 0 ] = tmp44;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::cosh;
    using std::max;
    using std::min;
    using std::pow;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp2 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp3 = tmp2 + tmp1;
    const auto tmp4 = 1e-10 + tmp3;
    const auto tmp5 = std::sqrt( tmp4 );
    const auto tmp6 = -1.4 + tmp5;
    const auto tmp7 = 1 + tmp0[ 0 ];
    const auto tmp8 = tmp7 * tmp7;
    const auto tmp9 = tmp1 + tmp8;
    const auto tmp10 = 1e-10 + tmp9;
    const auto tmp11 = std::sqrt( tmp10 );
    const auto tmp12 = -0.5 + tmp11;
    const auto tmp13 = -1 + tmp0[ 0 ];
    const auto tmp14 = tmp13 * tmp13;
    const auto tmp15 = tmp1 + tmp14;
    const auto tmp16 = 1e-10 + tmp15;
    const auto tmp17 = std::sqrt( tmp16 );
    const auto tmp18 = -0.5 + tmp17;
    const auto tmp19 = 0.8 + tmp0[ 1 ];
    const auto tmp20 = tmp19 * tmp19;
    const auto tmp21 = tmp2 + tmp20;
    const auto tmp22 = 1e-10 + tmp21;
    const auto tmp23 = std::sqrt( tmp22 );
    const auto tmp24 = -0.5 + tmp23;
    const auto tmp25 = -1 * tmp24;
    const auto tmp26 = -0.8 + tmp0[ 1 ];
    const auto tmp27 = tmp26 * tmp26;
    const auto tmp28 = tmp2 + tmp27;
    const auto tmp29 = 1e-10 + tmp28;
    const auto tmp30 = std::sqrt( tmp29 );
    const auto tmp31 = -0.5 + tmp30;
    const auto tmp32 = -1 * tmp31;
    const auto tmp33 = -1 + tmp5;
    const auto tmp34 = std::max( tmp33, tmp32 );
    const auto tmp35 = std::max( tmp34, tmp25 );
    const auto tmp36 = std::min( tmp35, tmp18 );
    const auto tmp37 = std::min( tmp36, tmp12 );
    const auto tmp38 = std::max( tmp37, tmp6 );
    const auto tmp39 = 3 * tmp38;
    const auto tmp40 = tmp39 / 0.140625;
    const auto tmp41 = 2.0 * tmp40;
    const auto tmp42 = std::cosh( tmp41 );
    const auto tmp43 = 1.0 + tmp42;
    const auto tmp44 = std::cosh( tmp40 );
    const auto tmp45 = 2.0 * tmp44;
    const auto tmp46 = tmp45 / tmp43;
    const auto tmp47 = std::pow( tmp46, 2 );
    const auto tmp48 = 2 * tmp5;
    const auto tmp49 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp50 = tmp49 / tmp48;
    const auto tmp51 = tmp50 * (tmp33 > tmp32 ? 1 : 0.0);
    const auto tmp52 = 2 * tmp30;
    const auto tmp53 = tmp49 / tmp52;
    const auto tmp54 = -1 * tmp53;
    const auto tmp55 = -1 * (tmp33 > tmp32 ? 1 : 0.0);
    const auto tmp56 = 1.0 + tmp55;
    const auto tmp57 = tmp56 * tmp54;
    const auto tmp58 = tmp57 + tmp51;
    const auto tmp59 = tmp58 * (tmp34 > tmp25 ? 1 : 0.0);
    const auto tmp60 = 2 * tmp23;
    const auto tmp61 = tmp49 / tmp60;
    const auto tmp62 = -1 * tmp61;
    const auto tmp63 = -1 * (tmp34 > tmp25 ? 1 : 0.0);
    const auto tmp64 = 1.0 + tmp63;
    const auto tmp65 = tmp64 * tmp62;
    const auto tmp66 = tmp65 + tmp59;
    const auto tmp67 = tmp66 * (tmp35 < tmp18 ? 1 : 0.0);
    const auto tmp68 = 2 * tmp17;
    const auto tmp69 = tmp13 + tmp13;
    const auto tmp70 = tmp69 / tmp68;
    const auto tmp71 = -1 * (tmp35 < tmp18 ? 1 : 0.0);
    const auto tmp72 = 1.0 + tmp71;
    const auto tmp73 = tmp72 * tmp70;
    const auto tmp74 = tmp73 + tmp67;
    const auto tmp75 = tmp74 * (tmp36 < tmp12 ? 1 : 0.0);
    const auto tmp76 = 2 * tmp11;
    const auto tmp77 = tmp7 + tmp7;
    const auto tmp78 = tmp77 / tmp76;
    const auto tmp79 = -1 * (tmp36 < tmp12 ? 1 : 0.0);
    const auto tmp80 = 1.0 + tmp79;
    const auto tmp81 = tmp80 * tmp78;
    const auto tmp82 = tmp81 + tmp75;
    const auto tmp83 = tmp82 * (tmp37 > tmp6 ? 1 : 0.0);
    const auto tmp84 = -1 * (tmp37 > tmp6 ? 1 : 0.0);
    const auto tmp85 = 1.0 + tmp84;
    const auto tmp86 = tmp85 * tmp50;
    const auto tmp87 = tmp86 + tmp83;
    const auto tmp88 = 3 * tmp87;
    const auto tmp89 = tmp88 / 0.140625;
    const auto tmp90 = tmp89 * tmp47;
    const auto tmp91 = -1 * tmp90;
    const auto tmp92 = 0.5 * tmp91;
    const auto tmp93 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp94 = tmp93 / tmp48;
    const auto tmp95 = tmp94 * (tmp33 > tmp32 ? 1 : 0.0);
    const auto tmp96 = tmp26 + tmp26;
    const auto tmp97 = tmp96 / tmp52;
    const auto tmp98 = -1 * tmp97;
    const auto tmp99 = tmp56 * tmp98;
    const auto tmp100 = tmp99 + tmp95;
    const auto tmp101 = tmp100 * (tmp34 > tmp25 ? 1 : 0.0);
    const auto tmp102 = tmp19 + tmp19;
    const auto tmp103 = tmp102 / tmp60;
    const auto tmp104 = -1 * tmp103;
    const auto tmp105 = tmp64 * tmp104;
    const auto tmp106 = tmp105 + tmp101;
    const auto tmp107 = tmp106 * (tmp35 < tmp18 ? 1 : 0.0);
    const auto tmp108 = tmp93 / tmp68;
    const auto tmp109 = tmp72 * tmp108;
    const auto tmp110 = tmp109 + tmp107;
    const auto tmp111 = tmp110 * (tmp36 < tmp12 ? 1 : 0.0);
    const auto tmp112 = tmp93 / tmp76;
    const auto tmp113 = tmp80 * tmp112;
    const auto tmp114 = tmp113 + tmp111;
    const auto tmp115 = tmp114 * (tmp37 > tmp6 ? 1 : 0.0);
    const auto tmp116 = tmp85 * tmp94;
    const auto tmp117 = tmp116 + tmp115;
    const auto tmp118 = 3 * tmp117;
    const auto tmp119 = tmp118 / 0.140625;
    const auto tmp120 = tmp119 * tmp47;
    const auto tmp121 = -1 * tmp120;
    const auto tmp122 = 0.5 * tmp121;
    (result[ 0 ])[ 0 ] = tmp92;
    (result[ 0 ])[ 1 ] = tmp122;
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
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp2 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp3 = tmp2 + tmp1;
    const auto tmp4 = 1e-10 + tmp3;
    const auto tmp5 = std::sqrt( tmp4 );
    const auto tmp6 = -1.4 + tmp5;
    const auto tmp7 = 1 + tmp0[ 0 ];
    const auto tmp8 = tmp7 * tmp7;
    const auto tmp9 = tmp1 + tmp8;
    const auto tmp10 = 1e-10 + tmp9;
    const auto tmp11 = std::sqrt( tmp10 );
    const auto tmp12 = -0.5 + tmp11;
    const auto tmp13 = -1 + tmp0[ 0 ];
    const auto tmp14 = tmp13 * tmp13;
    const auto tmp15 = tmp1 + tmp14;
    const auto tmp16 = 1e-10 + tmp15;
    const auto tmp17 = std::sqrt( tmp16 );
    const auto tmp18 = -0.5 + tmp17;
    const auto tmp19 = 0.8 + tmp0[ 1 ];
    const auto tmp20 = tmp19 * tmp19;
    const auto tmp21 = tmp2 + tmp20;
    const auto tmp22 = 1e-10 + tmp21;
    const auto tmp23 = std::sqrt( tmp22 );
    const auto tmp24 = -0.5 + tmp23;
    const auto tmp25 = -1 * tmp24;
    const auto tmp26 = -0.8 + tmp0[ 1 ];
    const auto tmp27 = tmp26 * tmp26;
    const auto tmp28 = tmp2 + tmp27;
    const auto tmp29 = 1e-10 + tmp28;
    const auto tmp30 = std::sqrt( tmp29 );
    const auto tmp31 = -0.5 + tmp30;
    const auto tmp32 = -1 * tmp31;
    const auto tmp33 = -1 + tmp5;
    const auto tmp34 = std::max( tmp33, tmp32 );
    const auto tmp35 = std::max( tmp34, tmp25 );
    const auto tmp36 = std::min( tmp35, tmp18 );
    const auto tmp37 = std::min( tmp36, tmp12 );
    const auto tmp38 = std::max( tmp37, tmp6 );
    const auto tmp39 = 3 * tmp38;
    const auto tmp40 = tmp39 / 0.140625;
    const auto tmp41 = 2.0 * tmp40;
    const auto tmp42 = std::cosh( tmp41 );
    const auto tmp43 = 1.0 + tmp42;
    const auto tmp44 = std::cosh( tmp40 );
    const auto tmp45 = 2.0 * tmp44;
    const auto tmp46 = tmp45 / tmp43;
    const auto tmp47 = std::pow( tmp46, 2 );
    const auto tmp48 = 2 * tmp5;
    const auto tmp49 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp50 = tmp49 / tmp48;
    const auto tmp51 = 2 * tmp50;
    const auto tmp52 = tmp51 * tmp50;
    const auto tmp53 = -1 * tmp52;
    const auto tmp54 = 2 + tmp53;
    const auto tmp55 = tmp54 / tmp48;
    const auto tmp56 = tmp55 * (tmp33 > tmp32 ? 1 : 0.0);
    const auto tmp57 = 2 * tmp30;
    const auto tmp58 = tmp49 / tmp57;
    const auto tmp59 = 2 * tmp58;
    const auto tmp60 = tmp59 * tmp58;
    const auto tmp61 = -1 * tmp60;
    const auto tmp62 = 2 + tmp61;
    const auto tmp63 = tmp62 / tmp57;
    const auto tmp64 = -1 * tmp63;
    const auto tmp65 = -1 * (tmp33 > tmp32 ? 1 : 0.0);
    const auto tmp66 = 1.0 + tmp65;
    const auto tmp67 = tmp66 * tmp64;
    const auto tmp68 = tmp67 + tmp56;
    const auto tmp69 = tmp68 * (tmp34 > tmp25 ? 1 : 0.0);
    const auto tmp70 = 2 * tmp23;
    const auto tmp71 = tmp49 / tmp70;
    const auto tmp72 = 2 * tmp71;
    const auto tmp73 = tmp72 * tmp71;
    const auto tmp74 = -1 * tmp73;
    const auto tmp75 = 2 + tmp74;
    const auto tmp76 = tmp75 / tmp70;
    const auto tmp77 = -1 * tmp76;
    const auto tmp78 = -1 * (tmp34 > tmp25 ? 1 : 0.0);
    const auto tmp79 = 1.0 + tmp78;
    const auto tmp80 = tmp79 * tmp77;
    const auto tmp81 = tmp80 + tmp69;
    const auto tmp82 = tmp81 * (tmp35 < tmp18 ? 1 : 0.0);
    const auto tmp83 = 2 * tmp17;
    const auto tmp84 = tmp13 + tmp13;
    const auto tmp85 = tmp84 / tmp83;
    const auto tmp86 = 2 * tmp85;
    const auto tmp87 = tmp86 * tmp85;
    const auto tmp88 = -1 * tmp87;
    const auto tmp89 = 2 + tmp88;
    const auto tmp90 = tmp89 / tmp83;
    const auto tmp91 = -1 * (tmp35 < tmp18 ? 1 : 0.0);
    const auto tmp92 = 1.0 + tmp91;
    const auto tmp93 = tmp92 * tmp90;
    const auto tmp94 = tmp93 + tmp82;
    const auto tmp95 = tmp94 * (tmp36 < tmp12 ? 1 : 0.0);
    const auto tmp96 = 2 * tmp11;
    const auto tmp97 = tmp7 + tmp7;
    const auto tmp98 = tmp97 / tmp96;
    const auto tmp99 = 2 * tmp98;
    const auto tmp100 = tmp99 * tmp98;
    const auto tmp101 = -1 * tmp100;
    const auto tmp102 = 2 + tmp101;
    const auto tmp103 = tmp102 / tmp96;
    const auto tmp104 = -1 * (tmp36 < tmp12 ? 1 : 0.0);
    const auto tmp105 = 1.0 + tmp104;
    const auto tmp106 = tmp105 * tmp103;
    const auto tmp107 = tmp106 + tmp95;
    const auto tmp108 = tmp107 * (tmp37 > tmp6 ? 1 : 0.0);
    const auto tmp109 = -1 * (tmp37 > tmp6 ? 1 : 0.0);
    const auto tmp110 = 1.0 + tmp109;
    const auto tmp111 = tmp110 * tmp55;
    const auto tmp112 = tmp111 + tmp108;
    const auto tmp113 = 3 * tmp112;
    const auto tmp114 = tmp113 / 0.140625;
    const auto tmp115 = tmp114 * tmp47;
    const auto tmp116 = tmp50 * (tmp33 > tmp32 ? 1 : 0.0);
    const auto tmp117 = -1 * tmp58;
    const auto tmp118 = tmp66 * tmp117;
    const auto tmp119 = tmp118 + tmp116;
    const auto tmp120 = tmp119 * (tmp34 > tmp25 ? 1 : 0.0);
    const auto tmp121 = -1 * tmp71;
    const auto tmp122 = tmp79 * tmp121;
    const auto tmp123 = tmp122 + tmp120;
    const auto tmp124 = tmp123 * (tmp35 < tmp18 ? 1 : 0.0);
    const auto tmp125 = tmp92 * tmp85;
    const auto tmp126 = tmp125 + tmp124;
    const auto tmp127 = tmp126 * (tmp36 < tmp12 ? 1 : 0.0);
    const auto tmp128 = tmp105 * tmp98;
    const auto tmp129 = tmp128 + tmp127;
    const auto tmp130 = tmp129 * (tmp37 > tmp6 ? 1 : 0.0);
    const auto tmp131 = tmp110 * tmp50;
    const auto tmp132 = tmp131 + tmp130;
    const auto tmp133 = 3 * tmp132;
    const auto tmp134 = tmp133 / 0.140625;
    const auto tmp135 = std::sinh( tmp40 );
    const auto tmp136 = tmp134 * tmp135;
    const auto tmp137 = 2.0 * tmp136;
    const auto tmp138 = std::sinh( tmp41 );
    const auto tmp139 = 2.0 * tmp134;
    const auto tmp140 = tmp139 * tmp138;
    const auto tmp141 = tmp140 * tmp46;
    const auto tmp142 = -1 * tmp141;
    const auto tmp143 = tmp142 + tmp137;
    const auto tmp144 = tmp143 / tmp43;
    const auto tmp145 = 2 * tmp144;
    const auto tmp146 = tmp145 * tmp46;
    const auto tmp147 = tmp146 * tmp134;
    const auto tmp148 = tmp147 + tmp115;
    const auto tmp149 = -1 * tmp148;
    const auto tmp150 = 0.5 * tmp149;
    const auto tmp151 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp152 = tmp151 / tmp48;
    const auto tmp153 = 2 * tmp152;
    const auto tmp154 = tmp153 * tmp50;
    const auto tmp155 = -1 * tmp154;
    const auto tmp156 = tmp155 / tmp48;
    const auto tmp157 = tmp156 * (tmp33 > tmp32 ? 1 : 0.0);
    const auto tmp158 = tmp26 + tmp26;
    const auto tmp159 = tmp158 / tmp57;
    const auto tmp160 = 2 * tmp159;
    const auto tmp161 = tmp160 * tmp58;
    const auto tmp162 = -1 * tmp161;
    const auto tmp163 = tmp162 / tmp57;
    const auto tmp164 = -1 * tmp163;
    const auto tmp165 = tmp66 * tmp164;
    const auto tmp166 = tmp165 + tmp157;
    const auto tmp167 = tmp166 * (tmp34 > tmp25 ? 1 : 0.0);
    const auto tmp168 = tmp19 + tmp19;
    const auto tmp169 = tmp168 / tmp70;
    const auto tmp170 = 2 * tmp169;
    const auto tmp171 = tmp170 * tmp71;
    const auto tmp172 = -1 * tmp171;
    const auto tmp173 = tmp172 / tmp70;
    const auto tmp174 = -1 * tmp173;
    const auto tmp175 = tmp79 * tmp174;
    const auto tmp176 = tmp175 + tmp167;
    const auto tmp177 = tmp176 * (tmp35 < tmp18 ? 1 : 0.0);
    const auto tmp178 = tmp151 / tmp83;
    const auto tmp179 = 2 * tmp178;
    const auto tmp180 = tmp179 * tmp85;
    const auto tmp181 = -1 * tmp180;
    const auto tmp182 = tmp181 / tmp83;
    const auto tmp183 = tmp92 * tmp182;
    const auto tmp184 = tmp183 + tmp177;
    const auto tmp185 = tmp184 * (tmp36 < tmp12 ? 1 : 0.0);
    const auto tmp186 = tmp151 / tmp96;
    const auto tmp187 = 2 * tmp186;
    const auto tmp188 = tmp187 * tmp98;
    const auto tmp189 = -1 * tmp188;
    const auto tmp190 = tmp189 / tmp96;
    const auto tmp191 = tmp105 * tmp190;
    const auto tmp192 = tmp191 + tmp185;
    const auto tmp193 = tmp192 * (tmp37 > tmp6 ? 1 : 0.0);
    const auto tmp194 = tmp110 * tmp156;
    const auto tmp195 = tmp194 + tmp193;
    const auto tmp196 = 3 * tmp195;
    const auto tmp197 = tmp196 / 0.140625;
    const auto tmp198 = tmp197 * tmp47;
    const auto tmp199 = tmp152 * (tmp33 > tmp32 ? 1 : 0.0);
    const auto tmp200 = -1 * tmp159;
    const auto tmp201 = tmp66 * tmp200;
    const auto tmp202 = tmp201 + tmp199;
    const auto tmp203 = tmp202 * (tmp34 > tmp25 ? 1 : 0.0);
    const auto tmp204 = -1 * tmp169;
    const auto tmp205 = tmp79 * tmp204;
    const auto tmp206 = tmp205 + tmp203;
    const auto tmp207 = tmp206 * (tmp35 < tmp18 ? 1 : 0.0);
    const auto tmp208 = tmp92 * tmp178;
    const auto tmp209 = tmp208 + tmp207;
    const auto tmp210 = tmp209 * (tmp36 < tmp12 ? 1 : 0.0);
    const auto tmp211 = tmp105 * tmp186;
    const auto tmp212 = tmp211 + tmp210;
    const auto tmp213 = tmp212 * (tmp37 > tmp6 ? 1 : 0.0);
    const auto tmp214 = tmp110 * tmp152;
    const auto tmp215 = tmp214 + tmp213;
    const auto tmp216 = 3 * tmp215;
    const auto tmp217 = tmp216 / 0.140625;
    const auto tmp218 = tmp217 * tmp135;
    const auto tmp219 = 2.0 * tmp218;
    const auto tmp220 = 2.0 * tmp217;
    const auto tmp221 = tmp220 * tmp138;
    const auto tmp222 = tmp221 * tmp46;
    const auto tmp223 = -1 * tmp222;
    const auto tmp224 = tmp223 + tmp219;
    const auto tmp225 = tmp224 / tmp43;
    const auto tmp226 = 2 * tmp225;
    const auto tmp227 = tmp226 * tmp46;
    const auto tmp228 = tmp227 * tmp134;
    const auto tmp229 = tmp228 + tmp198;
    const auto tmp230 = -1 * tmp229;
    const auto tmp231 = 0.5 * tmp230;
    const auto tmp232 = tmp51 * tmp152;
    const auto tmp233 = -1 * tmp232;
    const auto tmp234 = tmp233 / tmp48;
    const auto tmp235 = tmp234 * (tmp33 > tmp32 ? 1 : 0.0);
    const auto tmp236 = tmp59 * tmp159;
    const auto tmp237 = -1 * tmp236;
    const auto tmp238 = tmp237 / tmp57;
    const auto tmp239 = -1 * tmp238;
    const auto tmp240 = tmp66 * tmp239;
    const auto tmp241 = tmp240 + tmp235;
    const auto tmp242 = tmp241 * (tmp34 > tmp25 ? 1 : 0.0);
    const auto tmp243 = tmp72 * tmp169;
    const auto tmp244 = -1 * tmp243;
    const auto tmp245 = tmp244 / tmp70;
    const auto tmp246 = -1 * tmp245;
    const auto tmp247 = tmp79 * tmp246;
    const auto tmp248 = tmp247 + tmp242;
    const auto tmp249 = tmp248 * (tmp35 < tmp18 ? 1 : 0.0);
    const auto tmp250 = tmp86 * tmp178;
    const auto tmp251 = -1 * tmp250;
    const auto tmp252 = tmp251 / tmp83;
    const auto tmp253 = tmp92 * tmp252;
    const auto tmp254 = tmp253 + tmp249;
    const auto tmp255 = tmp254 * (tmp36 < tmp12 ? 1 : 0.0);
    const auto tmp256 = tmp99 * tmp186;
    const auto tmp257 = -1 * tmp256;
    const auto tmp258 = tmp257 / tmp96;
    const auto tmp259 = tmp105 * tmp258;
    const auto tmp260 = tmp259 + tmp255;
    const auto tmp261 = tmp260 * (tmp37 > tmp6 ? 1 : 0.0);
    const auto tmp262 = tmp110 * tmp234;
    const auto tmp263 = tmp262 + tmp261;
    const auto tmp264 = 3 * tmp263;
    const auto tmp265 = tmp264 / 0.140625;
    const auto tmp266 = tmp265 * tmp47;
    const auto tmp267 = tmp146 * tmp217;
    const auto tmp268 = tmp267 + tmp266;
    const auto tmp269 = -1 * tmp268;
    const auto tmp270 = 0.5 * tmp269;
    const auto tmp271 = tmp153 * tmp152;
    const auto tmp272 = -1 * tmp271;
    const auto tmp273 = 2 + tmp272;
    const auto tmp274 = tmp273 / tmp48;
    const auto tmp275 = tmp274 * (tmp33 > tmp32 ? 1 : 0.0);
    const auto tmp276 = tmp160 * tmp159;
    const auto tmp277 = -1 * tmp276;
    const auto tmp278 = 2 + tmp277;
    const auto tmp279 = tmp278 / tmp57;
    const auto tmp280 = -1 * tmp279;
    const auto tmp281 = tmp66 * tmp280;
    const auto tmp282 = tmp281 + tmp275;
    const auto tmp283 = tmp282 * (tmp34 > tmp25 ? 1 : 0.0);
    const auto tmp284 = tmp170 * tmp169;
    const auto tmp285 = -1 * tmp284;
    const auto tmp286 = 2 + tmp285;
    const auto tmp287 = tmp286 / tmp70;
    const auto tmp288 = -1 * tmp287;
    const auto tmp289 = tmp79 * tmp288;
    const auto tmp290 = tmp289 + tmp283;
    const auto tmp291 = tmp290 * (tmp35 < tmp18 ? 1 : 0.0);
    const auto tmp292 = tmp179 * tmp178;
    const auto tmp293 = -1 * tmp292;
    const auto tmp294 = 2 + tmp293;
    const auto tmp295 = tmp294 / tmp83;
    const auto tmp296 = tmp92 * tmp295;
    const auto tmp297 = tmp296 + tmp291;
    const auto tmp298 = tmp297 * (tmp36 < tmp12 ? 1 : 0.0);
    const auto tmp299 = tmp187 * tmp186;
    const auto tmp300 = -1 * tmp299;
    const auto tmp301 = 2 + tmp300;
    const auto tmp302 = tmp301 / tmp96;
    const auto tmp303 = tmp105 * tmp302;
    const auto tmp304 = tmp303 + tmp298;
    const auto tmp305 = tmp304 * (tmp37 > tmp6 ? 1 : 0.0);
    const auto tmp306 = tmp110 * tmp274;
    const auto tmp307 = tmp306 + tmp305;
    const auto tmp308 = 3 * tmp307;
    const auto tmp309 = tmp308 / 0.140625;
    const auto tmp310 = tmp309 * tmp47;
    const auto tmp311 = tmp227 * tmp217;
    const auto tmp312 = tmp311 + tmp310;
    const auto tmp313 = -1 * tmp312;
    const auto tmp314 = 0.5 * tmp313;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp150;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp231;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp270;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp314;
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

} // namespace UFLLocalFunctions_2021505441469e99dd3c9b164e083239

PYBIND11_MODULE( localfunction_2021505441469e99dd3c9b164e083239_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef UFLLocalFunctions_2021505441469e99dd3c9b164e083239::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_2021505441469e99dd3c9b164e083239::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_2021505441469e99dd3c9b164e083239_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
