#ifndef GUARD_762aa49bc5a47ad3d8d8bbde36b42ee5
#define GUARD_762aa49bc5a47ad3d8d8bbde36b42ee5

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

namespace UFLLocalFunctions_762aa49bc5a47ad3d8d8bbde36b42ee5
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
    const auto tmp2 = -0.4 + tmp1[ 0 ];
    const auto tmp3 = tmp1[ 1 ] * tmp1[ 1 ];
    const auto tmp4 = tmp1[ 0 ] * tmp1[ 0 ];
    const auto tmp5 = tmp4 + tmp3;
    const auto tmp6 = 1e-10 + tmp5;
    const auto tmp7 = std::sqrt( tmp6 );
    const auto tmp8 = -1.4 + tmp7;
    const auto tmp9 = std::min( tmp8, tmp2 );
    const auto tmp10 = -1 * tmp1[ 0 ];
    const auto tmp11 = -0.4 + tmp10;
    const auto tmp12 = std::min( tmp8, tmp11 );
    const auto tmp13 = std::max( tmp12, tmp9 );
    const auto tmp14 = 1 + tmp1[ 0 ];
    const auto tmp15 = tmp14 * tmp14;
    const auto tmp16 = tmp3 + tmp15;
    const auto tmp17 = 1e-10 + tmp16;
    const auto tmp18 = std::sqrt( tmp17 );
    const auto tmp19 = -0.5 + tmp18;
    const auto tmp20 = -1 + tmp1[ 0 ];
    const auto tmp21 = tmp20 * tmp20;
    const auto tmp22 = tmp3 + tmp21;
    const auto tmp23 = 1e-10 + tmp22;
    const auto tmp24 = std::sqrt( tmp23 );
    const auto tmp25 = -0.5 + tmp24;
    const auto tmp26 = 0.8 + tmp1[ 1 ];
    const auto tmp27 = tmp26 * tmp26;
    const auto tmp28 = tmp4 + tmp27;
    const auto tmp29 = 1e-10 + tmp28;
    const auto tmp30 = std::sqrt( tmp29 );
    const auto tmp31 = -0.5 + tmp30;
    const auto tmp32 = -1 * tmp31;
    const auto tmp33 = -0.8 + tmp1[ 1 ];
    const auto tmp34 = tmp33 * tmp33;
    const auto tmp35 = tmp4 + tmp34;
    const auto tmp36 = 1e-10 + tmp35;
    const auto tmp37 = std::sqrt( tmp36 );
    const auto tmp38 = -0.5 + tmp37;
    const auto tmp39 = -1 * tmp38;
    const auto tmp40 = -1 + tmp7;
    const auto tmp41 = std::max( tmp40, tmp39 );
    const auto tmp42 = std::max( tmp41, tmp32 );
    const auto tmp43 = std::min( tmp42, tmp25 );
    const auto tmp44 = std::min( tmp43, tmp19 );
    const auto tmp45 = std::max( tmp44, tmp13 );
    const auto tmp46 = 3 * tmp45;
    const auto tmp47 = tmp46 / tmp0;
    const auto tmp48 = std::tanh( tmp47 );
    const auto tmp49 = -1 * tmp48;
    const auto tmp50 = 1 + tmp49;
    const auto tmp51 = 0.5 * tmp50;
    const auto tmp52 = 0.9999999999 * tmp51;
    const auto tmp53 = 1e-10 + tmp52;
    result[ 0 ] = tmp53;
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
    const auto tmp2 = -0.4 + tmp1[ 0 ];
    const auto tmp3 = tmp1[ 1 ] * tmp1[ 1 ];
    const auto tmp4 = tmp1[ 0 ] * tmp1[ 0 ];
    const auto tmp5 = tmp4 + tmp3;
    const auto tmp6 = 1e-10 + tmp5;
    const auto tmp7 = std::sqrt( tmp6 );
    const auto tmp8 = -1.4 + tmp7;
    const auto tmp9 = std::min( tmp8, tmp2 );
    const auto tmp10 = -1 * tmp1[ 0 ];
    const auto tmp11 = -0.4 + tmp10;
    const auto tmp12 = std::min( tmp8, tmp11 );
    const auto tmp13 = std::max( tmp12, tmp9 );
    const auto tmp14 = 1 + tmp1[ 0 ];
    const auto tmp15 = tmp14 * tmp14;
    const auto tmp16 = tmp3 + tmp15;
    const auto tmp17 = 1e-10 + tmp16;
    const auto tmp18 = std::sqrt( tmp17 );
    const auto tmp19 = -0.5 + tmp18;
    const auto tmp20 = -1 + tmp1[ 0 ];
    const auto tmp21 = tmp20 * tmp20;
    const auto tmp22 = tmp3 + tmp21;
    const auto tmp23 = 1e-10 + tmp22;
    const auto tmp24 = std::sqrt( tmp23 );
    const auto tmp25 = -0.5 + tmp24;
    const auto tmp26 = 0.8 + tmp1[ 1 ];
    const auto tmp27 = tmp26 * tmp26;
    const auto tmp28 = tmp4 + tmp27;
    const auto tmp29 = 1e-10 + tmp28;
    const auto tmp30 = std::sqrt( tmp29 );
    const auto tmp31 = -0.5 + tmp30;
    const auto tmp32 = -1 * tmp31;
    const auto tmp33 = -0.8 + tmp1[ 1 ];
    const auto tmp34 = tmp33 * tmp33;
    const auto tmp35 = tmp4 + tmp34;
    const auto tmp36 = 1e-10 + tmp35;
    const auto tmp37 = std::sqrt( tmp36 );
    const auto tmp38 = -0.5 + tmp37;
    const auto tmp39 = -1 * tmp38;
    const auto tmp40 = -1 + tmp7;
    const auto tmp41 = std::max( tmp40, tmp39 );
    const auto tmp42 = std::max( tmp41, tmp32 );
    const auto tmp43 = std::min( tmp42, tmp25 );
    const auto tmp44 = std::min( tmp43, tmp19 );
    const auto tmp45 = std::max( tmp44, tmp13 );
    const auto tmp46 = 3 * tmp45;
    const auto tmp47 = tmp46 / tmp0;
    const auto tmp48 = 2.0 * tmp47;
    const auto tmp49 = std::cosh( tmp48 );
    const auto tmp50 = 1.0 + tmp49;
    const auto tmp51 = std::cosh( tmp47 );
    const auto tmp52 = 2.0 * tmp51;
    const auto tmp53 = tmp52 / tmp50;
    const auto tmp54 = std::pow( tmp53, 2 );
    const auto tmp55 = 2 * tmp7;
    const auto tmp56 = tmp1[ 0 ] + tmp1[ 0 ];
    const auto tmp57 = tmp56 / tmp55;
    const auto tmp58 = tmp57 * (tmp40 > tmp39 ? 1 : 0.0);
    const auto tmp59 = 2 * tmp37;
    const auto tmp60 = tmp56 / tmp59;
    const auto tmp61 = -1 * tmp60;
    const auto tmp62 = -1 * (tmp40 > tmp39 ? 1 : 0.0);
    const auto tmp63 = 1.0 + tmp62;
    const auto tmp64 = tmp63 * tmp61;
    const auto tmp65 = tmp64 + tmp58;
    const auto tmp66 = tmp65 * (tmp41 > tmp32 ? 1 : 0.0);
    const auto tmp67 = 2 * tmp30;
    const auto tmp68 = tmp56 / tmp67;
    const auto tmp69 = -1 * tmp68;
    const auto tmp70 = -1 * (tmp41 > tmp32 ? 1 : 0.0);
    const auto tmp71 = 1.0 + tmp70;
    const auto tmp72 = tmp71 * tmp69;
    const auto tmp73 = tmp72 + tmp66;
    const auto tmp74 = tmp73 * (tmp42 < tmp25 ? 1 : 0.0);
    const auto tmp75 = 2 * tmp24;
    const auto tmp76 = tmp20 + tmp20;
    const auto tmp77 = tmp76 / tmp75;
    const auto tmp78 = -1 * (tmp42 < tmp25 ? 1 : 0.0);
    const auto tmp79 = 1.0 + tmp78;
    const auto tmp80 = tmp79 * tmp77;
    const auto tmp81 = tmp80 + tmp74;
    const auto tmp82 = tmp81 * (tmp43 < tmp19 ? 1 : 0.0);
    const auto tmp83 = 2 * tmp18;
    const auto tmp84 = tmp14 + tmp14;
    const auto tmp85 = tmp84 / tmp83;
    const auto tmp86 = -1 * (tmp43 < tmp19 ? 1 : 0.0);
    const auto tmp87 = 1.0 + tmp86;
    const auto tmp88 = tmp87 * tmp85;
    const auto tmp89 = tmp88 + tmp82;
    const auto tmp90 = tmp89 * (tmp44 > tmp13 ? 1 : 0.0);
    const auto tmp91 = -1 * (tmp44 > tmp13 ? 1 : 0.0);
    const auto tmp92 = 1.0 + tmp91;
    const auto tmp93 = tmp57 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp94 = -1 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp95 = 1.0 + tmp94;
    const auto tmp96 = -1 * tmp95;
    const auto tmp97 = tmp96 + tmp93;
    const auto tmp98 = tmp97 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp99 = -1 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp100 = 1.0 + tmp99;
    const auto tmp101 = tmp57 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp102 = -1 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp103 = 1.0 + tmp102;
    const auto tmp104 = tmp103 + tmp101;
    const auto tmp105 = tmp104 * tmp100;
    const auto tmp106 = tmp105 + tmp98;
    const auto tmp107 = tmp106 * tmp92;
    const auto tmp108 = tmp107 + tmp90;
    const auto tmp109 = 3 * tmp108;
    const auto tmp110 = tmp109 / tmp0;
    const auto tmp111 = tmp110 * tmp54;
    const auto tmp112 = -1 * tmp111;
    const auto tmp113 = 0.5 * tmp112;
    const auto tmp114 = 0.9999999999 * tmp113;
    const auto tmp115 = tmp1[ 1 ] + tmp1[ 1 ];
    const auto tmp116 = tmp115 / tmp55;
    const auto tmp117 = tmp116 * (tmp40 > tmp39 ? 1 : 0.0);
    const auto tmp118 = tmp33 + tmp33;
    const auto tmp119 = tmp118 / tmp59;
    const auto tmp120 = -1 * tmp119;
    const auto tmp121 = tmp63 * tmp120;
    const auto tmp122 = tmp121 + tmp117;
    const auto tmp123 = tmp122 * (tmp41 > tmp32 ? 1 : 0.0);
    const auto tmp124 = tmp26 + tmp26;
    const auto tmp125 = tmp124 / tmp67;
    const auto tmp126 = -1 * tmp125;
    const auto tmp127 = tmp71 * tmp126;
    const auto tmp128 = tmp127 + tmp123;
    const auto tmp129 = tmp128 * (tmp42 < tmp25 ? 1 : 0.0);
    const auto tmp130 = tmp115 / tmp75;
    const auto tmp131 = tmp79 * tmp130;
    const auto tmp132 = tmp131 + tmp129;
    const auto tmp133 = tmp132 * (tmp43 < tmp19 ? 1 : 0.0);
    const auto tmp134 = tmp115 / tmp83;
    const auto tmp135 = tmp87 * tmp134;
    const auto tmp136 = tmp135 + tmp133;
    const auto tmp137 = tmp136 * (tmp44 > tmp13 ? 1 : 0.0);
    const auto tmp138 = tmp116 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp139 = tmp138 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp140 = tmp116 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp141 = tmp100 * tmp140;
    const auto tmp142 = tmp141 + tmp139;
    const auto tmp143 = tmp142 * tmp92;
    const auto tmp144 = tmp143 + tmp137;
    const auto tmp145 = 3 * tmp144;
    const auto tmp146 = tmp145 / tmp0;
    const auto tmp147 = tmp146 * tmp54;
    const auto tmp148 = -1 * tmp147;
    const auto tmp149 = 0.5 * tmp148;
    const auto tmp150 = 0.9999999999 * tmp149;
    (result[ 0 ])[ 0 ] = tmp114;
    (result[ 0 ])[ 1 ] = tmp150;
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
    const auto tmp2 = -0.4 + tmp1[ 0 ];
    const auto tmp3 = tmp1[ 1 ] * tmp1[ 1 ];
    const auto tmp4 = tmp1[ 0 ] * tmp1[ 0 ];
    const auto tmp5 = tmp4 + tmp3;
    const auto tmp6 = 1e-10 + tmp5;
    const auto tmp7 = std::sqrt( tmp6 );
    const auto tmp8 = -1.4 + tmp7;
    const auto tmp9 = std::min( tmp8, tmp2 );
    const auto tmp10 = -1 * tmp1[ 0 ];
    const auto tmp11 = -0.4 + tmp10;
    const auto tmp12 = std::min( tmp8, tmp11 );
    const auto tmp13 = std::max( tmp12, tmp9 );
    const auto tmp14 = 1 + tmp1[ 0 ];
    const auto tmp15 = tmp14 * tmp14;
    const auto tmp16 = tmp3 + tmp15;
    const auto tmp17 = 1e-10 + tmp16;
    const auto tmp18 = std::sqrt( tmp17 );
    const auto tmp19 = -0.5 + tmp18;
    const auto tmp20 = -1 + tmp1[ 0 ];
    const auto tmp21 = tmp20 * tmp20;
    const auto tmp22 = tmp3 + tmp21;
    const auto tmp23 = 1e-10 + tmp22;
    const auto tmp24 = std::sqrt( tmp23 );
    const auto tmp25 = -0.5 + tmp24;
    const auto tmp26 = 0.8 + tmp1[ 1 ];
    const auto tmp27 = tmp26 * tmp26;
    const auto tmp28 = tmp4 + tmp27;
    const auto tmp29 = 1e-10 + tmp28;
    const auto tmp30 = std::sqrt( tmp29 );
    const auto tmp31 = -0.5 + tmp30;
    const auto tmp32 = -1 * tmp31;
    const auto tmp33 = -0.8 + tmp1[ 1 ];
    const auto tmp34 = tmp33 * tmp33;
    const auto tmp35 = tmp4 + tmp34;
    const auto tmp36 = 1e-10 + tmp35;
    const auto tmp37 = std::sqrt( tmp36 );
    const auto tmp38 = -0.5 + tmp37;
    const auto tmp39 = -1 * tmp38;
    const auto tmp40 = -1 + tmp7;
    const auto tmp41 = std::max( tmp40, tmp39 );
    const auto tmp42 = std::max( tmp41, tmp32 );
    const auto tmp43 = std::min( tmp42, tmp25 );
    const auto tmp44 = std::min( tmp43, tmp19 );
    const auto tmp45 = std::max( tmp44, tmp13 );
    const auto tmp46 = 3 * tmp45;
    const auto tmp47 = tmp46 / tmp0;
    const auto tmp48 = 2.0 * tmp47;
    const auto tmp49 = std::cosh( tmp48 );
    const auto tmp50 = 1.0 + tmp49;
    const auto tmp51 = std::cosh( tmp47 );
    const auto tmp52 = 2.0 * tmp51;
    const auto tmp53 = tmp52 / tmp50;
    const auto tmp54 = std::pow( tmp53, 2 );
    const auto tmp55 = 2 * tmp7;
    const auto tmp56 = tmp1[ 0 ] + tmp1[ 0 ];
    const auto tmp57 = tmp56 / tmp55;
    const auto tmp58 = 2 * tmp57;
    const auto tmp59 = tmp58 * tmp57;
    const auto tmp60 = -1 * tmp59;
    const auto tmp61 = 2 + tmp60;
    const auto tmp62 = tmp61 / tmp55;
    const auto tmp63 = tmp62 * (tmp40 > tmp39 ? 1 : 0.0);
    const auto tmp64 = 2 * tmp37;
    const auto tmp65 = tmp56 / tmp64;
    const auto tmp66 = 2 * tmp65;
    const auto tmp67 = tmp66 * tmp65;
    const auto tmp68 = -1 * tmp67;
    const auto tmp69 = 2 + tmp68;
    const auto tmp70 = tmp69 / tmp64;
    const auto tmp71 = -1 * tmp70;
    const auto tmp72 = -1 * (tmp40 > tmp39 ? 1 : 0.0);
    const auto tmp73 = 1.0 + tmp72;
    const auto tmp74 = tmp73 * tmp71;
    const auto tmp75 = tmp74 + tmp63;
    const auto tmp76 = tmp75 * (tmp41 > tmp32 ? 1 : 0.0);
    const auto tmp77 = 2 * tmp30;
    const auto tmp78 = tmp56 / tmp77;
    const auto tmp79 = 2 * tmp78;
    const auto tmp80 = tmp79 * tmp78;
    const auto tmp81 = -1 * tmp80;
    const auto tmp82 = 2 + tmp81;
    const auto tmp83 = tmp82 / tmp77;
    const auto tmp84 = -1 * tmp83;
    const auto tmp85 = -1 * (tmp41 > tmp32 ? 1 : 0.0);
    const auto tmp86 = 1.0 + tmp85;
    const auto tmp87 = tmp86 * tmp84;
    const auto tmp88 = tmp87 + tmp76;
    const auto tmp89 = tmp88 * (tmp42 < tmp25 ? 1 : 0.0);
    const auto tmp90 = 2 * tmp24;
    const auto tmp91 = tmp20 + tmp20;
    const auto tmp92 = tmp91 / tmp90;
    const auto tmp93 = 2 * tmp92;
    const auto tmp94 = tmp93 * tmp92;
    const auto tmp95 = -1 * tmp94;
    const auto tmp96 = 2 + tmp95;
    const auto tmp97 = tmp96 / tmp90;
    const auto tmp98 = -1 * (tmp42 < tmp25 ? 1 : 0.0);
    const auto tmp99 = 1.0 + tmp98;
    const auto tmp100 = tmp99 * tmp97;
    const auto tmp101 = tmp100 + tmp89;
    const auto tmp102 = tmp101 * (tmp43 < tmp19 ? 1 : 0.0);
    const auto tmp103 = 2 * tmp18;
    const auto tmp104 = tmp14 + tmp14;
    const auto tmp105 = tmp104 / tmp103;
    const auto tmp106 = 2 * tmp105;
    const auto tmp107 = tmp106 * tmp105;
    const auto tmp108 = -1 * tmp107;
    const auto tmp109 = 2 + tmp108;
    const auto tmp110 = tmp109 / tmp103;
    const auto tmp111 = -1 * (tmp43 < tmp19 ? 1 : 0.0);
    const auto tmp112 = 1.0 + tmp111;
    const auto tmp113 = tmp112 * tmp110;
    const auto tmp114 = tmp113 + tmp102;
    const auto tmp115 = tmp114 * (tmp44 > tmp13 ? 1 : 0.0);
    const auto tmp116 = -1 * (tmp44 > tmp13 ? 1 : 0.0);
    const auto tmp117 = 1.0 + tmp116;
    const auto tmp118 = tmp62 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp119 = tmp118 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp120 = tmp62 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp121 = -1 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp122 = 1.0 + tmp121;
    const auto tmp123 = tmp122 * tmp120;
    const auto tmp124 = tmp123 + tmp119;
    const auto tmp125 = tmp124 * tmp117;
    const auto tmp126 = tmp125 + tmp115;
    const auto tmp127 = 3 * tmp126;
    const auto tmp128 = tmp127 / tmp0;
    const auto tmp129 = tmp128 * tmp54;
    const auto tmp130 = tmp57 * (tmp40 > tmp39 ? 1 : 0.0);
    const auto tmp131 = -1 * tmp65;
    const auto tmp132 = tmp73 * tmp131;
    const auto tmp133 = tmp132 + tmp130;
    const auto tmp134 = tmp133 * (tmp41 > tmp32 ? 1 : 0.0);
    const auto tmp135 = -1 * tmp78;
    const auto tmp136 = tmp86 * tmp135;
    const auto tmp137 = tmp136 + tmp134;
    const auto tmp138 = tmp137 * (tmp42 < tmp25 ? 1 : 0.0);
    const auto tmp139 = tmp99 * tmp92;
    const auto tmp140 = tmp139 + tmp138;
    const auto tmp141 = tmp140 * (tmp43 < tmp19 ? 1 : 0.0);
    const auto tmp142 = tmp112 * tmp105;
    const auto tmp143 = tmp142 + tmp141;
    const auto tmp144 = tmp143 * (tmp44 > tmp13 ? 1 : 0.0);
    const auto tmp145 = tmp57 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp146 = -1 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp147 = 1.0 + tmp146;
    const auto tmp148 = -1 * tmp147;
    const auto tmp149 = tmp148 + tmp145;
    const auto tmp150 = tmp149 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp151 = tmp57 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp152 = -1 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp153 = 1.0 + tmp152;
    const auto tmp154 = tmp153 + tmp151;
    const auto tmp155 = tmp154 * tmp122;
    const auto tmp156 = tmp155 + tmp150;
    const auto tmp157 = tmp156 * tmp117;
    const auto tmp158 = tmp157 + tmp144;
    const auto tmp159 = 3 * tmp158;
    const auto tmp160 = tmp159 / tmp0;
    const auto tmp161 = std::sinh( tmp47 );
    const auto tmp162 = tmp160 * tmp161;
    const auto tmp163 = 2.0 * tmp162;
    const auto tmp164 = std::sinh( tmp48 );
    const auto tmp165 = 2.0 * tmp160;
    const auto tmp166 = tmp165 * tmp164;
    const auto tmp167 = tmp166 * tmp53;
    const auto tmp168 = -1 * tmp167;
    const auto tmp169 = tmp168 + tmp163;
    const auto tmp170 = tmp169 / tmp50;
    const auto tmp171 = 2 * tmp170;
    const auto tmp172 = tmp171 * tmp53;
    const auto tmp173 = tmp172 * tmp160;
    const auto tmp174 = tmp173 + tmp129;
    const auto tmp175 = -1 * tmp174;
    const auto tmp176 = 0.5 * tmp175;
    const auto tmp177 = 0.9999999999 * tmp176;
    const auto tmp178 = tmp1[ 1 ] + tmp1[ 1 ];
    const auto tmp179 = tmp178 / tmp55;
    const auto tmp180 = 2 * tmp179;
    const auto tmp181 = tmp180 * tmp57;
    const auto tmp182 = -1 * tmp181;
    const auto tmp183 = tmp182 / tmp55;
    const auto tmp184 = tmp183 * (tmp40 > tmp39 ? 1 : 0.0);
    const auto tmp185 = tmp33 + tmp33;
    const auto tmp186 = tmp185 / tmp64;
    const auto tmp187 = 2 * tmp186;
    const auto tmp188 = tmp187 * tmp65;
    const auto tmp189 = -1 * tmp188;
    const auto tmp190 = tmp189 / tmp64;
    const auto tmp191 = -1 * tmp190;
    const auto tmp192 = tmp73 * tmp191;
    const auto tmp193 = tmp192 + tmp184;
    const auto tmp194 = tmp193 * (tmp41 > tmp32 ? 1 : 0.0);
    const auto tmp195 = tmp26 + tmp26;
    const auto tmp196 = tmp195 / tmp77;
    const auto tmp197 = 2 * tmp196;
    const auto tmp198 = tmp197 * tmp78;
    const auto tmp199 = -1 * tmp198;
    const auto tmp200 = tmp199 / tmp77;
    const auto tmp201 = -1 * tmp200;
    const auto tmp202 = tmp86 * tmp201;
    const auto tmp203 = tmp202 + tmp194;
    const auto tmp204 = tmp203 * (tmp42 < tmp25 ? 1 : 0.0);
    const auto tmp205 = tmp178 / tmp90;
    const auto tmp206 = 2 * tmp205;
    const auto tmp207 = tmp206 * tmp92;
    const auto tmp208 = -1 * tmp207;
    const auto tmp209 = tmp208 / tmp90;
    const auto tmp210 = tmp99 * tmp209;
    const auto tmp211 = tmp210 + tmp204;
    const auto tmp212 = tmp211 * (tmp43 < tmp19 ? 1 : 0.0);
    const auto tmp213 = tmp178 / tmp103;
    const auto tmp214 = 2 * tmp213;
    const auto tmp215 = tmp214 * tmp105;
    const auto tmp216 = -1 * tmp215;
    const auto tmp217 = tmp216 / tmp103;
    const auto tmp218 = tmp112 * tmp217;
    const auto tmp219 = tmp218 + tmp212;
    const auto tmp220 = tmp219 * (tmp44 > tmp13 ? 1 : 0.0);
    const auto tmp221 = tmp183 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp222 = tmp221 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp223 = tmp183 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp224 = tmp122 * tmp223;
    const auto tmp225 = tmp224 + tmp222;
    const auto tmp226 = tmp225 * tmp117;
    const auto tmp227 = tmp226 + tmp220;
    const auto tmp228 = 3 * tmp227;
    const auto tmp229 = tmp228 / tmp0;
    const auto tmp230 = tmp229 * tmp54;
    const auto tmp231 = tmp179 * (tmp40 > tmp39 ? 1 : 0.0);
    const auto tmp232 = -1 * tmp186;
    const auto tmp233 = tmp73 * tmp232;
    const auto tmp234 = tmp233 + tmp231;
    const auto tmp235 = tmp234 * (tmp41 > tmp32 ? 1 : 0.0);
    const auto tmp236 = -1 * tmp196;
    const auto tmp237 = tmp86 * tmp236;
    const auto tmp238 = tmp237 + tmp235;
    const auto tmp239 = tmp238 * (tmp42 < tmp25 ? 1 : 0.0);
    const auto tmp240 = tmp99 * tmp205;
    const auto tmp241 = tmp240 + tmp239;
    const auto tmp242 = tmp241 * (tmp43 < tmp19 ? 1 : 0.0);
    const auto tmp243 = tmp112 * tmp213;
    const auto tmp244 = tmp243 + tmp242;
    const auto tmp245 = tmp244 * (tmp44 > tmp13 ? 1 : 0.0);
    const auto tmp246 = tmp179 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp247 = tmp246 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp248 = tmp179 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp249 = tmp122 * tmp248;
    const auto tmp250 = tmp249 + tmp247;
    const auto tmp251 = tmp250 * tmp117;
    const auto tmp252 = tmp251 + tmp245;
    const auto tmp253 = 3 * tmp252;
    const auto tmp254 = tmp253 / tmp0;
    const auto tmp255 = tmp254 * tmp161;
    const auto tmp256 = 2.0 * tmp255;
    const auto tmp257 = 2.0 * tmp254;
    const auto tmp258 = tmp257 * tmp164;
    const auto tmp259 = tmp258 * tmp53;
    const auto tmp260 = -1 * tmp259;
    const auto tmp261 = tmp260 + tmp256;
    const auto tmp262 = tmp261 / tmp50;
    const auto tmp263 = 2 * tmp262;
    const auto tmp264 = tmp263 * tmp53;
    const auto tmp265 = tmp264 * tmp160;
    const auto tmp266 = tmp265 + tmp230;
    const auto tmp267 = -1 * tmp266;
    const auto tmp268 = 0.5 * tmp267;
    const auto tmp269 = 0.9999999999 * tmp268;
    const auto tmp270 = tmp58 * tmp179;
    const auto tmp271 = -1 * tmp270;
    const auto tmp272 = tmp271 / tmp55;
    const auto tmp273 = tmp272 * (tmp40 > tmp39 ? 1 : 0.0);
    const auto tmp274 = tmp66 * tmp186;
    const auto tmp275 = -1 * tmp274;
    const auto tmp276 = tmp275 / tmp64;
    const auto tmp277 = -1 * tmp276;
    const auto tmp278 = tmp73 * tmp277;
    const auto tmp279 = tmp278 + tmp273;
    const auto tmp280 = tmp279 * (tmp41 > tmp32 ? 1 : 0.0);
    const auto tmp281 = tmp79 * tmp196;
    const auto tmp282 = -1 * tmp281;
    const auto tmp283 = tmp282 / tmp77;
    const auto tmp284 = -1 * tmp283;
    const auto tmp285 = tmp86 * tmp284;
    const auto tmp286 = tmp285 + tmp280;
    const auto tmp287 = tmp286 * (tmp42 < tmp25 ? 1 : 0.0);
    const auto tmp288 = tmp93 * tmp205;
    const auto tmp289 = -1 * tmp288;
    const auto tmp290 = tmp289 / tmp90;
    const auto tmp291 = tmp99 * tmp290;
    const auto tmp292 = tmp291 + tmp287;
    const auto tmp293 = tmp292 * (tmp43 < tmp19 ? 1 : 0.0);
    const auto tmp294 = tmp106 * tmp213;
    const auto tmp295 = -1 * tmp294;
    const auto tmp296 = tmp295 / tmp103;
    const auto tmp297 = tmp112 * tmp296;
    const auto tmp298 = tmp297 + tmp293;
    const auto tmp299 = tmp298 * (tmp44 > tmp13 ? 1 : 0.0);
    const auto tmp300 = tmp272 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp301 = tmp300 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp302 = tmp272 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp303 = tmp122 * tmp302;
    const auto tmp304 = tmp303 + tmp301;
    const auto tmp305 = tmp304 * tmp117;
    const auto tmp306 = tmp305 + tmp299;
    const auto tmp307 = 3 * tmp306;
    const auto tmp308 = tmp307 / tmp0;
    const auto tmp309 = tmp308 * tmp54;
    const auto tmp310 = tmp172 * tmp254;
    const auto tmp311 = tmp310 + tmp309;
    const auto tmp312 = -1 * tmp311;
    const auto tmp313 = 0.5 * tmp312;
    const auto tmp314 = 0.9999999999 * tmp313;
    const auto tmp315 = tmp180 * tmp179;
    const auto tmp316 = -1 * tmp315;
    const auto tmp317 = 2 + tmp316;
    const auto tmp318 = tmp317 / tmp55;
    const auto tmp319 = tmp318 * (tmp40 > tmp39 ? 1 : 0.0);
    const auto tmp320 = tmp187 * tmp186;
    const auto tmp321 = -1 * tmp320;
    const auto tmp322 = 2 + tmp321;
    const auto tmp323 = tmp322 / tmp64;
    const auto tmp324 = -1 * tmp323;
    const auto tmp325 = tmp73 * tmp324;
    const auto tmp326 = tmp325 + tmp319;
    const auto tmp327 = tmp326 * (tmp41 > tmp32 ? 1 : 0.0);
    const auto tmp328 = tmp197 * tmp196;
    const auto tmp329 = -1 * tmp328;
    const auto tmp330 = 2 + tmp329;
    const auto tmp331 = tmp330 / tmp77;
    const auto tmp332 = -1 * tmp331;
    const auto tmp333 = tmp86 * tmp332;
    const auto tmp334 = tmp333 + tmp327;
    const auto tmp335 = tmp334 * (tmp42 < tmp25 ? 1 : 0.0);
    const auto tmp336 = tmp206 * tmp205;
    const auto tmp337 = -1 * tmp336;
    const auto tmp338 = 2 + tmp337;
    const auto tmp339 = tmp338 / tmp90;
    const auto tmp340 = tmp99 * tmp339;
    const auto tmp341 = tmp340 + tmp335;
    const auto tmp342 = tmp341 * (tmp43 < tmp19 ? 1 : 0.0);
    const auto tmp343 = tmp214 * tmp213;
    const auto tmp344 = -1 * tmp343;
    const auto tmp345 = 2 + tmp344;
    const auto tmp346 = tmp345 / tmp103;
    const auto tmp347 = tmp112 * tmp346;
    const auto tmp348 = tmp347 + tmp342;
    const auto tmp349 = tmp348 * (tmp44 > tmp13 ? 1 : 0.0);
    const auto tmp350 = tmp318 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp351 = tmp350 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp352 = tmp318 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp353 = tmp122 * tmp352;
    const auto tmp354 = tmp353 + tmp351;
    const auto tmp355 = tmp354 * tmp117;
    const auto tmp356 = tmp355 + tmp349;
    const auto tmp357 = 3 * tmp356;
    const auto tmp358 = tmp357 / tmp0;
    const auto tmp359 = tmp358 * tmp54;
    const auto tmp360 = tmp264 * tmp254;
    const auto tmp361 = tmp360 + tmp359;
    const auto tmp362 = -1 * tmp361;
    const auto tmp363 = 0.5 * tmp362;
    const auto tmp364 = 0.9999999999 * tmp363;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp177;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp269;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp314;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp364;
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

} // namespace UFLLocalFunctions_762aa49bc5a47ad3d8d8bbde36b42ee5

PYBIND11_MODULE( localfunction_762aa49bc5a47ad3d8d8bbde36b42ee5_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef UFLLocalFunctions_762aa49bc5a47ad3d8d8bbde36b42ee5::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_762aa49bc5a47ad3d8d8bbde36b42ee5::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_762aa49bc5a47ad3d8d8bbde36b42ee5_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property( "epsilon", [] ( LocalFunctionType &self ) -> UFLLocalFunctions_762aa49bc5a47ad3d8d8bbde36b42ee5::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > >::Conepsilon { return self.conepsilon(); }, [] ( LocalFunctionType &self, const UFLLocalFunctions_762aa49bc5a47ad3d8d8bbde36b42ee5::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > >::Conepsilon &v ) { self.conepsilon() = v; } );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
