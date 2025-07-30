#ifndef GUARD_6363af791dde11d699a9a3d876cc5d9a
#define GUARD_6363af791dde11d699a9a3d876cc5d9a

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

namespace UFLLocalFunctions_6363af791dde11d699a9a3d876cc5d9a
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
    const auto tmp1 = -0.4 + tmp0[ 0 ];
    const auto tmp2 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp3 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -1.4 + tmp6;
    const auto tmp8 = std::min( tmp7, tmp1 );
    const auto tmp9 = -1 * tmp0[ 0 ];
    const auto tmp10 = -0.4 + tmp9;
    const auto tmp11 = std::min( tmp7, tmp10 );
    const auto tmp12 = std::max( tmp11, tmp8 );
    const auto tmp13 = 1 + tmp0[ 0 ];
    const auto tmp14 = tmp13 * tmp13;
    const auto tmp15 = tmp2 + tmp14;
    const auto tmp16 = 1e-10 + tmp15;
    const auto tmp17 = std::sqrt( tmp16 );
    const auto tmp18 = -0.5 + tmp17;
    const auto tmp19 = -1 + tmp0[ 0 ];
    const auto tmp20 = tmp19 * tmp19;
    const auto tmp21 = tmp2 + tmp20;
    const auto tmp22 = 1e-10 + tmp21;
    const auto tmp23 = std::sqrt( tmp22 );
    const auto tmp24 = -0.5 + tmp23;
    const auto tmp25 = 0.8 + tmp0[ 1 ];
    const auto tmp26 = tmp25 * tmp25;
    const auto tmp27 = tmp3 + tmp26;
    const auto tmp28 = 1e-10 + tmp27;
    const auto tmp29 = std::sqrt( tmp28 );
    const auto tmp30 = -0.5 + tmp29;
    const auto tmp31 = -1 * tmp30;
    const auto tmp32 = -0.8 + tmp0[ 1 ];
    const auto tmp33 = tmp32 * tmp32;
    const auto tmp34 = tmp3 + tmp33;
    const auto tmp35 = 1e-10 + tmp34;
    const auto tmp36 = std::sqrt( tmp35 );
    const auto tmp37 = -0.5 + tmp36;
    const auto tmp38 = -1 * tmp37;
    const auto tmp39 = -1 + tmp6;
    const auto tmp40 = std::max( tmp39, tmp38 );
    const auto tmp41 = std::max( tmp40, tmp31 );
    const auto tmp42 = std::min( tmp41, tmp24 );
    const auto tmp43 = std::min( tmp42, tmp18 );
    const auto tmp44 = std::max( tmp43, tmp12 );
    result[ 0 ] = tmp44;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::max;
    using std::min;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -0.4 + tmp0[ 0 ];
    const auto tmp2 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp3 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -1.4 + tmp6;
    const auto tmp8 = std::min( tmp7, tmp1 );
    const auto tmp9 = -1 * tmp0[ 0 ];
    const auto tmp10 = -0.4 + tmp9;
    const auto tmp11 = std::min( tmp7, tmp10 );
    const auto tmp12 = std::max( tmp11, tmp8 );
    const auto tmp13 = 1 + tmp0[ 0 ];
    const auto tmp14 = tmp13 * tmp13;
    const auto tmp15 = tmp2 + tmp14;
    const auto tmp16 = 1e-10 + tmp15;
    const auto tmp17 = std::sqrt( tmp16 );
    const auto tmp18 = -0.5 + tmp17;
    const auto tmp19 = -1 + tmp0[ 0 ];
    const auto tmp20 = tmp19 * tmp19;
    const auto tmp21 = tmp2 + tmp20;
    const auto tmp22 = 1e-10 + tmp21;
    const auto tmp23 = std::sqrt( tmp22 );
    const auto tmp24 = -0.5 + tmp23;
    const auto tmp25 = 0.8 + tmp0[ 1 ];
    const auto tmp26 = tmp25 * tmp25;
    const auto tmp27 = tmp3 + tmp26;
    const auto tmp28 = 1e-10 + tmp27;
    const auto tmp29 = std::sqrt( tmp28 );
    const auto tmp30 = -0.5 + tmp29;
    const auto tmp31 = -1 * tmp30;
    const auto tmp32 = -0.8 + tmp0[ 1 ];
    const auto tmp33 = tmp32 * tmp32;
    const auto tmp34 = tmp3 + tmp33;
    const auto tmp35 = 1e-10 + tmp34;
    const auto tmp36 = std::sqrt( tmp35 );
    const auto tmp37 = -0.5 + tmp36;
    const auto tmp38 = -1 * tmp37;
    const auto tmp39 = -1 + tmp6;
    const auto tmp40 = std::max( tmp39, tmp38 );
    const auto tmp41 = std::max( tmp40, tmp31 );
    const auto tmp42 = std::min( tmp41, tmp24 );
    const auto tmp43 = std::min( tmp42, tmp18 );
    const auto tmp44 = 2 * tmp6;
    const auto tmp45 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp46 = tmp45 / tmp44;
    const auto tmp47 = tmp46 * (tmp39 > tmp38 ? 1 : 0.0);
    const auto tmp48 = 2 * tmp36;
    const auto tmp49 = tmp45 / tmp48;
    const auto tmp50 = -1 * tmp49;
    const auto tmp51 = -1 * (tmp39 > tmp38 ? 1 : 0.0);
    const auto tmp52 = 1.0 + tmp51;
    const auto tmp53 = tmp52 * tmp50;
    const auto tmp54 = tmp53 + tmp47;
    const auto tmp55 = tmp54 * (tmp40 > tmp31 ? 1 : 0.0);
    const auto tmp56 = 2 * tmp29;
    const auto tmp57 = tmp45 / tmp56;
    const auto tmp58 = -1 * tmp57;
    const auto tmp59 = -1 * (tmp40 > tmp31 ? 1 : 0.0);
    const auto tmp60 = 1.0 + tmp59;
    const auto tmp61 = tmp60 * tmp58;
    const auto tmp62 = tmp61 + tmp55;
    const auto tmp63 = tmp62 * (tmp41 < tmp24 ? 1 : 0.0);
    const auto tmp64 = 2 * tmp23;
    const auto tmp65 = tmp19 + tmp19;
    const auto tmp66 = tmp65 / tmp64;
    const auto tmp67 = -1 * (tmp41 < tmp24 ? 1 : 0.0);
    const auto tmp68 = 1.0 + tmp67;
    const auto tmp69 = tmp68 * tmp66;
    const auto tmp70 = tmp69 + tmp63;
    const auto tmp71 = tmp70 * (tmp42 < tmp18 ? 1 : 0.0);
    const auto tmp72 = 2 * tmp17;
    const auto tmp73 = tmp13 + tmp13;
    const auto tmp74 = tmp73 / tmp72;
    const auto tmp75 = -1 * (tmp42 < tmp18 ? 1 : 0.0);
    const auto tmp76 = 1.0 + tmp75;
    const auto tmp77 = tmp76 * tmp74;
    const auto tmp78 = tmp77 + tmp71;
    const auto tmp79 = tmp78 * (tmp43 > tmp12 ? 1 : 0.0);
    const auto tmp80 = -1 * (tmp43 > tmp12 ? 1 : 0.0);
    const auto tmp81 = 1.0 + tmp80;
    const auto tmp82 = tmp46 * (tmp7 < tmp10 ? 1 : 0.0);
    const auto tmp83 = -1 * (tmp7 < tmp10 ? 1 : 0.0);
    const auto tmp84 = 1.0 + tmp83;
    const auto tmp85 = -1 * tmp84;
    const auto tmp86 = tmp85 + tmp82;
    const auto tmp87 = tmp86 * (tmp11 > tmp8 ? 1 : 0.0);
    const auto tmp88 = -1 * (tmp11 > tmp8 ? 1 : 0.0);
    const auto tmp89 = 1.0 + tmp88;
    const auto tmp90 = tmp46 * (tmp7 < tmp1 ? 1 : 0.0);
    const auto tmp91 = -1 * (tmp7 < tmp1 ? 1 : 0.0);
    const auto tmp92 = 1.0 + tmp91;
    const auto tmp93 = tmp92 + tmp90;
    const auto tmp94 = tmp93 * tmp89;
    const auto tmp95 = tmp94 + tmp87;
    const auto tmp96 = tmp95 * tmp81;
    const auto tmp97 = tmp96 + tmp79;
    const auto tmp98 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp99 = tmp98 / tmp44;
    const auto tmp100 = tmp99 * (tmp39 > tmp38 ? 1 : 0.0);
    const auto tmp101 = tmp32 + tmp32;
    const auto tmp102 = tmp101 / tmp48;
    const auto tmp103 = -1 * tmp102;
    const auto tmp104 = tmp52 * tmp103;
    const auto tmp105 = tmp104 + tmp100;
    const auto tmp106 = tmp105 * (tmp40 > tmp31 ? 1 : 0.0);
    const auto tmp107 = tmp25 + tmp25;
    const auto tmp108 = tmp107 / tmp56;
    const auto tmp109 = -1 * tmp108;
    const auto tmp110 = tmp60 * tmp109;
    const auto tmp111 = tmp110 + tmp106;
    const auto tmp112 = tmp111 * (tmp41 < tmp24 ? 1 : 0.0);
    const auto tmp113 = tmp98 / tmp64;
    const auto tmp114 = tmp68 * tmp113;
    const auto tmp115 = tmp114 + tmp112;
    const auto tmp116 = tmp115 * (tmp42 < tmp18 ? 1 : 0.0);
    const auto tmp117 = tmp98 / tmp72;
    const auto tmp118 = tmp76 * tmp117;
    const auto tmp119 = tmp118 + tmp116;
    const auto tmp120 = tmp119 * (tmp43 > tmp12 ? 1 : 0.0);
    const auto tmp121 = tmp99 * (tmp7 < tmp10 ? 1 : 0.0);
    const auto tmp122 = tmp121 * (tmp11 > tmp8 ? 1 : 0.0);
    const auto tmp123 = tmp99 * (tmp7 < tmp1 ? 1 : 0.0);
    const auto tmp124 = tmp89 * tmp123;
    const auto tmp125 = tmp124 + tmp122;
    const auto tmp126 = tmp125 * tmp81;
    const auto tmp127 = tmp126 + tmp120;
    (result[ 0 ])[ 0 ] = tmp97;
    (result[ 0 ])[ 1 ] = tmp127;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::max;
    using std::min;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = -0.4 + tmp0[ 0 ];
    const auto tmp2 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp3 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -1.4 + tmp6;
    const auto tmp8 = std::min( tmp7, tmp1 );
    const auto tmp9 = -1 * tmp0[ 0 ];
    const auto tmp10 = -0.4 + tmp9;
    const auto tmp11 = std::min( tmp7, tmp10 );
    const auto tmp12 = std::max( tmp11, tmp8 );
    const auto tmp13 = 1 + tmp0[ 0 ];
    const auto tmp14 = tmp13 * tmp13;
    const auto tmp15 = tmp2 + tmp14;
    const auto tmp16 = 1e-10 + tmp15;
    const auto tmp17 = std::sqrt( tmp16 );
    const auto tmp18 = -0.5 + tmp17;
    const auto tmp19 = -1 + tmp0[ 0 ];
    const auto tmp20 = tmp19 * tmp19;
    const auto tmp21 = tmp2 + tmp20;
    const auto tmp22 = 1e-10 + tmp21;
    const auto tmp23 = std::sqrt( tmp22 );
    const auto tmp24 = -0.5 + tmp23;
    const auto tmp25 = 0.8 + tmp0[ 1 ];
    const auto tmp26 = tmp25 * tmp25;
    const auto tmp27 = tmp3 + tmp26;
    const auto tmp28 = 1e-10 + tmp27;
    const auto tmp29 = std::sqrt( tmp28 );
    const auto tmp30 = -0.5 + tmp29;
    const auto tmp31 = -1 * tmp30;
    const auto tmp32 = -0.8 + tmp0[ 1 ];
    const auto tmp33 = tmp32 * tmp32;
    const auto tmp34 = tmp3 + tmp33;
    const auto tmp35 = 1e-10 + tmp34;
    const auto tmp36 = std::sqrt( tmp35 );
    const auto tmp37 = -0.5 + tmp36;
    const auto tmp38 = -1 * tmp37;
    const auto tmp39 = -1 + tmp6;
    const auto tmp40 = std::max( tmp39, tmp38 );
    const auto tmp41 = std::max( tmp40, tmp31 );
    const auto tmp42 = std::min( tmp41, tmp24 );
    const auto tmp43 = std::min( tmp42, tmp18 );
    const auto tmp44 = 2 * tmp6;
    const auto tmp45 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp46 = tmp45 / tmp44;
    const auto tmp47 = 2 * tmp46;
    const auto tmp48 = tmp47 * tmp46;
    const auto tmp49 = -1 * tmp48;
    const auto tmp50 = 2 + tmp49;
    const auto tmp51 = tmp50 / tmp44;
    const auto tmp52 = tmp51 * (tmp39 > tmp38 ? 1 : 0.0);
    const auto tmp53 = 2 * tmp36;
    const auto tmp54 = tmp45 / tmp53;
    const auto tmp55 = 2 * tmp54;
    const auto tmp56 = tmp55 * tmp54;
    const auto tmp57 = -1 * tmp56;
    const auto tmp58 = 2 + tmp57;
    const auto tmp59 = tmp58 / tmp53;
    const auto tmp60 = -1 * tmp59;
    const auto tmp61 = -1 * (tmp39 > tmp38 ? 1 : 0.0);
    const auto tmp62 = 1.0 + tmp61;
    const auto tmp63 = tmp62 * tmp60;
    const auto tmp64 = tmp63 + tmp52;
    const auto tmp65 = tmp64 * (tmp40 > tmp31 ? 1 : 0.0);
    const auto tmp66 = 2 * tmp29;
    const auto tmp67 = tmp45 / tmp66;
    const auto tmp68 = 2 * tmp67;
    const auto tmp69 = tmp68 * tmp67;
    const auto tmp70 = -1 * tmp69;
    const auto tmp71 = 2 + tmp70;
    const auto tmp72 = tmp71 / tmp66;
    const auto tmp73 = -1 * tmp72;
    const auto tmp74 = -1 * (tmp40 > tmp31 ? 1 : 0.0);
    const auto tmp75 = 1.0 + tmp74;
    const auto tmp76 = tmp75 * tmp73;
    const auto tmp77 = tmp76 + tmp65;
    const auto tmp78 = tmp77 * (tmp41 < tmp24 ? 1 : 0.0);
    const auto tmp79 = 2 * tmp23;
    const auto tmp80 = tmp19 + tmp19;
    const auto tmp81 = tmp80 / tmp79;
    const auto tmp82 = 2 * tmp81;
    const auto tmp83 = tmp82 * tmp81;
    const auto tmp84 = -1 * tmp83;
    const auto tmp85 = 2 + tmp84;
    const auto tmp86 = tmp85 / tmp79;
    const auto tmp87 = -1 * (tmp41 < tmp24 ? 1 : 0.0);
    const auto tmp88 = 1.0 + tmp87;
    const auto tmp89 = tmp88 * tmp86;
    const auto tmp90 = tmp89 + tmp78;
    const auto tmp91 = tmp90 * (tmp42 < tmp18 ? 1 : 0.0);
    const auto tmp92 = 2 * tmp17;
    const auto tmp93 = tmp13 + tmp13;
    const auto tmp94 = tmp93 / tmp92;
    const auto tmp95 = 2 * tmp94;
    const auto tmp96 = tmp95 * tmp94;
    const auto tmp97 = -1 * tmp96;
    const auto tmp98 = 2 + tmp97;
    const auto tmp99 = tmp98 / tmp92;
    const auto tmp100 = -1 * (tmp42 < tmp18 ? 1 : 0.0);
    const auto tmp101 = 1.0 + tmp100;
    const auto tmp102 = tmp101 * tmp99;
    const auto tmp103 = tmp102 + tmp91;
    const auto tmp104 = tmp103 * (tmp43 > tmp12 ? 1 : 0.0);
    const auto tmp105 = -1 * (tmp43 > tmp12 ? 1 : 0.0);
    const auto tmp106 = 1.0 + tmp105;
    const auto tmp107 = tmp51 * (tmp7 < tmp10 ? 1 : 0.0);
    const auto tmp108 = tmp107 * (tmp11 > tmp8 ? 1 : 0.0);
    const auto tmp109 = tmp51 * (tmp7 < tmp1 ? 1 : 0.0);
    const auto tmp110 = -1 * (tmp11 > tmp8 ? 1 : 0.0);
    const auto tmp111 = 1.0 + tmp110;
    const auto tmp112 = tmp111 * tmp109;
    const auto tmp113 = tmp112 + tmp108;
    const auto tmp114 = tmp113 * tmp106;
    const auto tmp115 = tmp114 + tmp104;
    const auto tmp116 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp117 = tmp116 / tmp44;
    const auto tmp118 = 2 * tmp117;
    const auto tmp119 = tmp118 * tmp46;
    const auto tmp120 = -1 * tmp119;
    const auto tmp121 = tmp120 / tmp44;
    const auto tmp122 = tmp121 * (tmp39 > tmp38 ? 1 : 0.0);
    const auto tmp123 = tmp32 + tmp32;
    const auto tmp124 = tmp123 / tmp53;
    const auto tmp125 = 2 * tmp124;
    const auto tmp126 = tmp125 * tmp54;
    const auto tmp127 = -1 * tmp126;
    const auto tmp128 = tmp127 / tmp53;
    const auto tmp129 = -1 * tmp128;
    const auto tmp130 = tmp62 * tmp129;
    const auto tmp131 = tmp130 + tmp122;
    const auto tmp132 = tmp131 * (tmp40 > tmp31 ? 1 : 0.0);
    const auto tmp133 = tmp25 + tmp25;
    const auto tmp134 = tmp133 / tmp66;
    const auto tmp135 = 2 * tmp134;
    const auto tmp136 = tmp135 * tmp67;
    const auto tmp137 = -1 * tmp136;
    const auto tmp138 = tmp137 / tmp66;
    const auto tmp139 = -1 * tmp138;
    const auto tmp140 = tmp75 * tmp139;
    const auto tmp141 = tmp140 + tmp132;
    const auto tmp142 = tmp141 * (tmp41 < tmp24 ? 1 : 0.0);
    const auto tmp143 = tmp116 / tmp79;
    const auto tmp144 = 2 * tmp143;
    const auto tmp145 = tmp144 * tmp81;
    const auto tmp146 = -1 * tmp145;
    const auto tmp147 = tmp146 / tmp79;
    const auto tmp148 = tmp88 * tmp147;
    const auto tmp149 = tmp148 + tmp142;
    const auto tmp150 = tmp149 * (tmp42 < tmp18 ? 1 : 0.0);
    const auto tmp151 = tmp116 / tmp92;
    const auto tmp152 = 2 * tmp151;
    const auto tmp153 = tmp152 * tmp94;
    const auto tmp154 = -1 * tmp153;
    const auto tmp155 = tmp154 / tmp92;
    const auto tmp156 = tmp101 * tmp155;
    const auto tmp157 = tmp156 + tmp150;
    const auto tmp158 = tmp157 * (tmp43 > tmp12 ? 1 : 0.0);
    const auto tmp159 = tmp121 * (tmp7 < tmp10 ? 1 : 0.0);
    const auto tmp160 = tmp159 * (tmp11 > tmp8 ? 1 : 0.0);
    const auto tmp161 = tmp121 * (tmp7 < tmp1 ? 1 : 0.0);
    const auto tmp162 = tmp111 * tmp161;
    const auto tmp163 = tmp162 + tmp160;
    const auto tmp164 = tmp163 * tmp106;
    const auto tmp165 = tmp164 + tmp158;
    const auto tmp166 = tmp47 * tmp117;
    const auto tmp167 = -1 * tmp166;
    const auto tmp168 = tmp167 / tmp44;
    const auto tmp169 = tmp168 * (tmp39 > tmp38 ? 1 : 0.0);
    const auto tmp170 = tmp55 * tmp124;
    const auto tmp171 = -1 * tmp170;
    const auto tmp172 = tmp171 / tmp53;
    const auto tmp173 = -1 * tmp172;
    const auto tmp174 = tmp62 * tmp173;
    const auto tmp175 = tmp174 + tmp169;
    const auto tmp176 = tmp175 * (tmp40 > tmp31 ? 1 : 0.0);
    const auto tmp177 = tmp68 * tmp134;
    const auto tmp178 = -1 * tmp177;
    const auto tmp179 = tmp178 / tmp66;
    const auto tmp180 = -1 * tmp179;
    const auto tmp181 = tmp75 * tmp180;
    const auto tmp182 = tmp181 + tmp176;
    const auto tmp183 = tmp182 * (tmp41 < tmp24 ? 1 : 0.0);
    const auto tmp184 = tmp82 * tmp143;
    const auto tmp185 = -1 * tmp184;
    const auto tmp186 = tmp185 / tmp79;
    const auto tmp187 = tmp88 * tmp186;
    const auto tmp188 = tmp187 + tmp183;
    const auto tmp189 = tmp188 * (tmp42 < tmp18 ? 1 : 0.0);
    const auto tmp190 = tmp95 * tmp151;
    const auto tmp191 = -1 * tmp190;
    const auto tmp192 = tmp191 / tmp92;
    const auto tmp193 = tmp101 * tmp192;
    const auto tmp194 = tmp193 + tmp189;
    const auto tmp195 = tmp194 * (tmp43 > tmp12 ? 1 : 0.0);
    const auto tmp196 = tmp168 * (tmp7 < tmp10 ? 1 : 0.0);
    const auto tmp197 = tmp196 * (tmp11 > tmp8 ? 1 : 0.0);
    const auto tmp198 = tmp168 * (tmp7 < tmp1 ? 1 : 0.0);
    const auto tmp199 = tmp111 * tmp198;
    const auto tmp200 = tmp199 + tmp197;
    const auto tmp201 = tmp200 * tmp106;
    const auto tmp202 = tmp201 + tmp195;
    const auto tmp203 = tmp118 * tmp117;
    const auto tmp204 = -1 * tmp203;
    const auto tmp205 = 2 + tmp204;
    const auto tmp206 = tmp205 / tmp44;
    const auto tmp207 = tmp206 * (tmp39 > tmp38 ? 1 : 0.0);
    const auto tmp208 = tmp125 * tmp124;
    const auto tmp209 = -1 * tmp208;
    const auto tmp210 = 2 + tmp209;
    const auto tmp211 = tmp210 / tmp53;
    const auto tmp212 = -1 * tmp211;
    const auto tmp213 = tmp62 * tmp212;
    const auto tmp214 = tmp213 + tmp207;
    const auto tmp215 = tmp214 * (tmp40 > tmp31 ? 1 : 0.0);
    const auto tmp216 = tmp135 * tmp134;
    const auto tmp217 = -1 * tmp216;
    const auto tmp218 = 2 + tmp217;
    const auto tmp219 = tmp218 / tmp66;
    const auto tmp220 = -1 * tmp219;
    const auto tmp221 = tmp75 * tmp220;
    const auto tmp222 = tmp221 + tmp215;
    const auto tmp223 = tmp222 * (tmp41 < tmp24 ? 1 : 0.0);
    const auto tmp224 = tmp144 * tmp143;
    const auto tmp225 = -1 * tmp224;
    const auto tmp226 = 2 + tmp225;
    const auto tmp227 = tmp226 / tmp79;
    const auto tmp228 = tmp88 * tmp227;
    const auto tmp229 = tmp228 + tmp223;
    const auto tmp230 = tmp229 * (tmp42 < tmp18 ? 1 : 0.0);
    const auto tmp231 = tmp152 * tmp151;
    const auto tmp232 = -1 * tmp231;
    const auto tmp233 = 2 + tmp232;
    const auto tmp234 = tmp233 / tmp92;
    const auto tmp235 = tmp101 * tmp234;
    const auto tmp236 = tmp235 + tmp230;
    const auto tmp237 = tmp236 * (tmp43 > tmp12 ? 1 : 0.0);
    const auto tmp238 = tmp206 * (tmp7 < tmp10 ? 1 : 0.0);
    const auto tmp239 = tmp238 * (tmp11 > tmp8 ? 1 : 0.0);
    const auto tmp240 = tmp206 * (tmp7 < tmp1 ? 1 : 0.0);
    const auto tmp241 = tmp111 * tmp240;
    const auto tmp242 = tmp241 + tmp239;
    const auto tmp243 = tmp242 * tmp106;
    const auto tmp244 = tmp243 + tmp237;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp115;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp165;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp202;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp244;
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

} // namespace UFLLocalFunctions_6363af791dde11d699a9a3d876cc5d9a

PYBIND11_MODULE( localfunction_6363af791dde11d699a9a3d876cc5d9a_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef UFLLocalFunctions_6363af791dde11d699a9a3d876cc5d9a::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_6363af791dde11d699a9a3d876cc5d9a::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_6363af791dde11d699a9a3d876cc5d9a_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
