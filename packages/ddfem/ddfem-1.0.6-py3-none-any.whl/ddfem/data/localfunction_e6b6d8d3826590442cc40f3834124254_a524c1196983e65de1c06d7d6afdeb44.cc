#ifndef GUARD_e6b6d8d3826590442cc40f3834124254
#define GUARD_e6b6d8d3826590442cc40f3834124254

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

namespace UFLLocalFunctions_e6b6d8d3826590442cc40f3834124254
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
    const auto tmp14 = 3 * tmp13;
    const auto tmp15 = tmp14 / tmp0;
    const auto tmp16 = std::tanh( tmp15 );
    const auto tmp17 = -1 * tmp16;
    const auto tmp18 = 1 + tmp17;
    const auto tmp19 = 0.5 * tmp18;
    const auto tmp20 = -1 * tmp19;
    const auto tmp21 = 1 + tmp20;
    const auto tmp22 = tmp21 * tmp19;
    result[ 0 ] = tmp22;
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
    const auto tmp14 = 3 * tmp13;
    const auto tmp15 = tmp14 / tmp0;
    const auto tmp16 = 2.0 * tmp15;
    const auto tmp17 = std::cosh( tmp16 );
    const auto tmp18 = 1.0 + tmp17;
    const auto tmp19 = std::cosh( tmp15 );
    const auto tmp20 = 2.0 * tmp19;
    const auto tmp21 = tmp20 / tmp18;
    const auto tmp22 = std::pow( tmp21, 2 );
    const auto tmp23 = 2 * tmp7;
    typename CoefficientFunctionSpaceType< 0 >::JacobianRangeType tmp24 = jacobianCoefficient< 0 >( x );
    const auto tmp25 = tmp1[ 1 ] * (tmp24[ 1 ])[ 0 ];
    const auto tmp26 = tmp25 + tmp25;
    const auto tmp27 = tmp1[ 0 ] * (tmp24[ 0 ])[ 0 ];
    const auto tmp28 = tmp27 + tmp27;
    const auto tmp29 = tmp28 + tmp26;
    const auto tmp30 = tmp29 / tmp23;
    const auto tmp31 = tmp30 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp32 = -1 * (tmp24[ 0 ])[ 0 ];
    const auto tmp33 = -1 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp34 = 1.0 + tmp33;
    const auto tmp35 = tmp34 * tmp32;
    const auto tmp36 = tmp35 + tmp31;
    const auto tmp37 = tmp36 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp38 = -1 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp39 = 1.0 + tmp38;
    const auto tmp40 = tmp30 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp41 = -1 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp42 = 1.0 + tmp41;
    const auto tmp43 = (tmp24[ 0 ])[ 0 ] * tmp42;
    const auto tmp44 = tmp43 + tmp40;
    const auto tmp45 = tmp44 * tmp39;
    const auto tmp46 = tmp45 + tmp37;
    const auto tmp47 = 3 * tmp46;
    const auto tmp48 = tmp47 / tmp0;
    const auto tmp49 = tmp48 * tmp22;
    const auto tmp50 = -1 * tmp49;
    const auto tmp51 = 0.5 * tmp50;
    const auto tmp52 = std::tanh( tmp15 );
    const auto tmp53 = -1 * tmp52;
    const auto tmp54 = 1 + tmp53;
    const auto tmp55 = 0.5 * tmp54;
    const auto tmp56 = -1 * tmp55;
    const auto tmp57 = 1 + tmp56;
    const auto tmp58 = tmp57 * tmp51;
    const auto tmp59 = -1 * tmp51;
    const auto tmp60 = tmp55 * tmp59;
    const auto tmp61 = tmp60 + tmp58;
    const auto tmp62 = tmp1[ 1 ] * (tmp24[ 1 ])[ 1 ];
    const auto tmp63 = tmp62 + tmp62;
    const auto tmp64 = tmp1[ 0 ] * (tmp24[ 0 ])[ 1 ];
    const auto tmp65 = tmp64 + tmp64;
    const auto tmp66 = tmp65 + tmp63;
    const auto tmp67 = tmp66 / tmp23;
    const auto tmp68 = tmp67 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp69 = -1 * (tmp24[ 0 ])[ 1 ];
    const auto tmp70 = tmp34 * tmp69;
    const auto tmp71 = tmp70 + tmp68;
    const auto tmp72 = tmp71 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp73 = tmp67 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp74 = (tmp24[ 0 ])[ 1 ] * tmp42;
    const auto tmp75 = tmp74 + tmp73;
    const auto tmp76 = tmp75 * tmp39;
    const auto tmp77 = tmp76 + tmp72;
    const auto tmp78 = 3 * tmp77;
    const auto tmp79 = tmp78 / tmp0;
    const auto tmp80 = tmp79 * tmp22;
    const auto tmp81 = -1 * tmp80;
    const auto tmp82 = 0.5 * tmp81;
    const auto tmp83 = tmp57 * tmp82;
    const auto tmp84 = -1 * tmp82;
    const auto tmp85 = tmp55 * tmp84;
    const auto tmp86 = tmp85 + tmp83;
    (result[ 0 ])[ 0 ] = tmp61;
    (result[ 0 ])[ 1 ] = tmp86;
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
    const auto tmp14 = 3 * tmp13;
    const auto tmp15 = tmp14 / tmp0;
    const auto tmp16 = 2.0 * tmp15;
    const auto tmp17 = std::cosh( tmp16 );
    const auto tmp18 = 1.0 + tmp17;
    const auto tmp19 = std::cosh( tmp15 );
    const auto tmp20 = 2.0 * tmp19;
    const auto tmp21 = tmp20 / tmp18;
    const auto tmp22 = std::pow( tmp21, 2 );
    const auto tmp23 = 2 * tmp7;
    typename CoefficientFunctionSpaceType< 0 >::JacobianRangeType tmp24 = jacobianCoefficient< 0 >( x );
    const auto tmp25 = tmp1[ 1 ] * (tmp24[ 1 ])[ 0 ];
    const auto tmp26 = tmp25 + tmp25;
    const auto tmp27 = tmp1[ 0 ] * (tmp24[ 0 ])[ 0 ];
    const auto tmp28 = tmp27 + tmp27;
    const auto tmp29 = tmp28 + tmp26;
    const auto tmp30 = tmp29 / tmp23;
    const auto tmp31 = tmp30 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp32 = -1 * (tmp24[ 0 ])[ 0 ];
    const auto tmp33 = -1 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp34 = 1.0 + tmp33;
    const auto tmp35 = tmp34 * tmp32;
    const auto tmp36 = tmp35 + tmp31;
    const auto tmp37 = tmp36 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp38 = -1 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp39 = 1.0 + tmp38;
    const auto tmp40 = tmp30 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp41 = -1 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp42 = 1.0 + tmp41;
    const auto tmp43 = (tmp24[ 0 ])[ 0 ] * tmp42;
    const auto tmp44 = tmp43 + tmp40;
    const auto tmp45 = tmp44 * tmp39;
    const auto tmp46 = tmp45 + tmp37;
    const auto tmp47 = 3 * tmp46;
    const auto tmp48 = tmp47 / tmp0;
    const auto tmp49 = tmp48 * tmp22;
    const auto tmp50 = -1 * tmp49;
    const auto tmp51 = 0.5 * tmp50;
    const auto tmp52 = -1 * tmp51;
    const auto tmp53 = tmp52 * tmp51;
    const auto tmp54 = 2 * tmp30;
    const auto tmp55 = tmp54 * tmp30;
    const auto tmp56 = -1 * tmp55;
    typename CoefficientFunctionSpaceType< 0 >::HessianRangeType tmp57 = hessianCoefficient< 0 >( x );
    const auto tmp58 = tmp1[ 1 ] * ((tmp57[ 1 ])[ 0 ])[ 0 ];
    const auto tmp59 = (tmp24[ 1 ])[ 0 ] * (tmp24[ 1 ])[ 0 ];
    const auto tmp60 = tmp59 + tmp58;
    const auto tmp61 = tmp60 + tmp60;
    const auto tmp62 = tmp1[ 0 ] * ((tmp57[ 0 ])[ 0 ])[ 0 ];
    const auto tmp63 = (tmp24[ 0 ])[ 0 ] * (tmp24[ 0 ])[ 0 ];
    const auto tmp64 = tmp63 + tmp62;
    const auto tmp65 = tmp64 + tmp64;
    const auto tmp66 = tmp65 + tmp61;
    const auto tmp67 = tmp66 + tmp56;
    const auto tmp68 = tmp67 / tmp23;
    const auto tmp69 = tmp68 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp70 = -1 * ((tmp57[ 0 ])[ 0 ])[ 0 ];
    const auto tmp71 = tmp34 * tmp70;
    const auto tmp72 = tmp71 + tmp69;
    const auto tmp73 = tmp72 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp74 = tmp68 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp75 = ((tmp57[ 0 ])[ 0 ])[ 0 ] * tmp42;
    const auto tmp76 = tmp75 + tmp74;
    const auto tmp77 = tmp76 * tmp39;
    const auto tmp78 = tmp77 + tmp73;
    const auto tmp79 = 3 * tmp78;
    const auto tmp80 = tmp79 / tmp0;
    const auto tmp81 = tmp80 * tmp22;
    const auto tmp82 = std::sinh( tmp15 );
    const auto tmp83 = tmp48 * tmp82;
    const auto tmp84 = 2.0 * tmp83;
    const auto tmp85 = std::sinh( tmp16 );
    const auto tmp86 = 2.0 * tmp48;
    const auto tmp87 = tmp86 * tmp85;
    const auto tmp88 = tmp87 * tmp21;
    const auto tmp89 = -1 * tmp88;
    const auto tmp90 = tmp89 + tmp84;
    const auto tmp91 = tmp90 / tmp18;
    const auto tmp92 = 2 * tmp91;
    const auto tmp93 = tmp92 * tmp21;
    const auto tmp94 = tmp93 * tmp48;
    const auto tmp95 = tmp94 + tmp81;
    const auto tmp96 = -1 * tmp95;
    const auto tmp97 = 0.5 * tmp96;
    const auto tmp98 = -1 * tmp97;
    const auto tmp99 = std::tanh( tmp15 );
    const auto tmp100 = -1 * tmp99;
    const auto tmp101 = 1 + tmp100;
    const auto tmp102 = 0.5 * tmp101;
    const auto tmp103 = tmp102 * tmp98;
    const auto tmp104 = tmp103 + tmp53;
    const auto tmp105 = -1 * tmp102;
    const auto tmp106 = 1 + tmp105;
    const auto tmp107 = tmp106 * tmp97;
    const auto tmp108 = tmp107 + tmp53;
    const auto tmp109 = tmp108 + tmp104;
    const auto tmp110 = tmp1[ 1 ] * (tmp24[ 1 ])[ 1 ];
    const auto tmp111 = tmp110 + tmp110;
    const auto tmp112 = tmp1[ 0 ] * (tmp24[ 0 ])[ 1 ];
    const auto tmp113 = tmp112 + tmp112;
    const auto tmp114 = tmp113 + tmp111;
    const auto tmp115 = tmp114 / tmp23;
    const auto tmp116 = tmp115 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp117 = -1 * (tmp24[ 0 ])[ 1 ];
    const auto tmp118 = tmp34 * tmp117;
    const auto tmp119 = tmp118 + tmp116;
    const auto tmp120 = tmp119 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp121 = tmp115 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp122 = (tmp24[ 0 ])[ 1 ] * tmp42;
    const auto tmp123 = tmp122 + tmp121;
    const auto tmp124 = tmp123 * tmp39;
    const auto tmp125 = tmp124 + tmp120;
    const auto tmp126 = 3 * tmp125;
    const auto tmp127 = tmp126 / tmp0;
    const auto tmp128 = tmp127 * tmp22;
    const auto tmp129 = -1 * tmp128;
    const auto tmp130 = 0.5 * tmp129;
    const auto tmp131 = tmp52 * tmp130;
    const auto tmp132 = 2 * tmp115;
    const auto tmp133 = tmp132 * tmp30;
    const auto tmp134 = -1 * tmp133;
    const auto tmp135 = (tmp24[ 1 ])[ 0 ] * (tmp24[ 1 ])[ 1 ];
    const auto tmp136 = tmp1[ 1 ] * ((tmp57[ 1 ])[ 0 ])[ 1 ];
    const auto tmp137 = tmp136 + tmp135;
    const auto tmp138 = tmp137 + tmp137;
    const auto tmp139 = (tmp24[ 0 ])[ 0 ] * (tmp24[ 0 ])[ 1 ];
    const auto tmp140 = tmp1[ 0 ] * ((tmp57[ 0 ])[ 0 ])[ 1 ];
    const auto tmp141 = tmp140 + tmp139;
    const auto tmp142 = tmp141 + tmp141;
    const auto tmp143 = tmp142 + tmp138;
    const auto tmp144 = tmp143 + tmp134;
    const auto tmp145 = tmp144 / tmp23;
    const auto tmp146 = tmp145 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp147 = -1 * ((tmp57[ 0 ])[ 0 ])[ 1 ];
    const auto tmp148 = tmp34 * tmp147;
    const auto tmp149 = tmp148 + tmp146;
    const auto tmp150 = tmp149 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp151 = tmp145 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp152 = ((tmp57[ 0 ])[ 0 ])[ 1 ] * tmp42;
    const auto tmp153 = tmp152 + tmp151;
    const auto tmp154 = tmp153 * tmp39;
    const auto tmp155 = tmp154 + tmp150;
    const auto tmp156 = 3 * tmp155;
    const auto tmp157 = tmp156 / tmp0;
    const auto tmp158 = tmp157 * tmp22;
    const auto tmp159 = tmp127 * tmp82;
    const auto tmp160 = 2.0 * tmp159;
    const auto tmp161 = 2.0 * tmp127;
    const auto tmp162 = tmp161 * tmp85;
    const auto tmp163 = tmp162 * tmp21;
    const auto tmp164 = -1 * tmp163;
    const auto tmp165 = tmp164 + tmp160;
    const auto tmp166 = tmp165 / tmp18;
    const auto tmp167 = 2 * tmp166;
    const auto tmp168 = tmp167 * tmp21;
    const auto tmp169 = tmp168 * tmp48;
    const auto tmp170 = tmp169 + tmp158;
    const auto tmp171 = -1 * tmp170;
    const auto tmp172 = 0.5 * tmp171;
    const auto tmp173 = -1 * tmp172;
    const auto tmp174 = tmp102 * tmp173;
    const auto tmp175 = tmp174 + tmp131;
    const auto tmp176 = -1 * tmp130;
    const auto tmp177 = tmp176 * tmp51;
    const auto tmp178 = tmp106 * tmp172;
    const auto tmp179 = tmp178 + tmp177;
    const auto tmp180 = tmp179 + tmp175;
    const auto tmp181 = tmp54 * tmp115;
    const auto tmp182 = -1 * tmp181;
    const auto tmp183 = tmp1[ 1 ] * ((tmp57[ 1 ])[ 1 ])[ 0 ];
    const auto tmp184 = tmp135 + tmp183;
    const auto tmp185 = tmp184 + tmp184;
    const auto tmp186 = tmp1[ 0 ] * ((tmp57[ 0 ])[ 1 ])[ 0 ];
    const auto tmp187 = tmp139 + tmp186;
    const auto tmp188 = tmp187 + tmp187;
    const auto tmp189 = tmp188 + tmp185;
    const auto tmp190 = tmp189 + tmp182;
    const auto tmp191 = tmp190 / tmp23;
    const auto tmp192 = tmp191 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp193 = -1 * ((tmp57[ 0 ])[ 1 ])[ 0 ];
    const auto tmp194 = tmp34 * tmp193;
    const auto tmp195 = tmp194 + tmp192;
    const auto tmp196 = tmp195 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp197 = tmp191 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp198 = ((tmp57[ 0 ])[ 1 ])[ 0 ] * tmp42;
    const auto tmp199 = tmp198 + tmp197;
    const auto tmp200 = tmp199 * tmp39;
    const auto tmp201 = tmp200 + tmp196;
    const auto tmp202 = 3 * tmp201;
    const auto tmp203 = tmp202 / tmp0;
    const auto tmp204 = tmp203 * tmp22;
    const auto tmp205 = tmp93 * tmp127;
    const auto tmp206 = tmp205 + tmp204;
    const auto tmp207 = -1 * tmp206;
    const auto tmp208 = 0.5 * tmp207;
    const auto tmp209 = tmp106 * tmp208;
    const auto tmp210 = tmp209 + tmp131;
    const auto tmp211 = -1 * tmp208;
    const auto tmp212 = tmp102 * tmp211;
    const auto tmp213 = tmp212 + tmp177;
    const auto tmp214 = tmp213 + tmp210;
    const auto tmp215 = tmp176 * tmp130;
    const auto tmp216 = tmp132 * tmp115;
    const auto tmp217 = -1 * tmp216;
    const auto tmp218 = tmp1[ 1 ] * ((tmp57[ 1 ])[ 1 ])[ 1 ];
    const auto tmp219 = (tmp24[ 1 ])[ 1 ] * (tmp24[ 1 ])[ 1 ];
    const auto tmp220 = tmp219 + tmp218;
    const auto tmp221 = tmp220 + tmp220;
    const auto tmp222 = tmp1[ 0 ] * ((tmp57[ 0 ])[ 1 ])[ 1 ];
    const auto tmp223 = (tmp24[ 0 ])[ 1 ] * (tmp24[ 0 ])[ 1 ];
    const auto tmp224 = tmp223 + tmp222;
    const auto tmp225 = tmp224 + tmp224;
    const auto tmp226 = tmp225 + tmp221;
    const auto tmp227 = tmp226 + tmp217;
    const auto tmp228 = tmp227 / tmp23;
    const auto tmp229 = tmp228 * (tmp8 < tmp11 ? 1 : 0.0);
    const auto tmp230 = -1 * ((tmp57[ 0 ])[ 1 ])[ 1 ];
    const auto tmp231 = tmp34 * tmp230;
    const auto tmp232 = tmp231 + tmp229;
    const auto tmp233 = tmp232 * (tmp12 > tmp9 ? 1 : 0.0);
    const auto tmp234 = tmp228 * (tmp8 < tmp2 ? 1 : 0.0);
    const auto tmp235 = ((tmp57[ 0 ])[ 1 ])[ 1 ] * tmp42;
    const auto tmp236 = tmp235 + tmp234;
    const auto tmp237 = tmp236 * tmp39;
    const auto tmp238 = tmp237 + tmp233;
    const auto tmp239 = 3 * tmp238;
    const auto tmp240 = tmp239 / tmp0;
    const auto tmp241 = tmp240 * tmp22;
    const auto tmp242 = tmp168 * tmp127;
    const auto tmp243 = tmp242 + tmp241;
    const auto tmp244 = -1 * tmp243;
    const auto tmp245 = 0.5 * tmp244;
    const auto tmp246 = -1 * tmp245;
    const auto tmp247 = tmp102 * tmp246;
    const auto tmp248 = tmp247 + tmp215;
    const auto tmp249 = tmp106 * tmp245;
    const auto tmp250 = tmp249 + tmp215;
    const auto tmp251 = tmp250 + tmp248;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp109;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp180;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp214;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp251;
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

} // namespace UFLLocalFunctions_e6b6d8d3826590442cc40f3834124254

PYBIND11_MODULE( localfunction_e6b6d8d3826590442cc40f3834124254_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef UFLLocalFunctions_e6b6d8d3826590442cc40f3834124254::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_e6b6d8d3826590442cc40f3834124254::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_e6b6d8d3826590442cc40f3834124254_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order, const Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > &coeffbndproj ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>(gridView),name,order, coeffbndproj); } ), pybind11::keep_alive< 1, 2 >(), pybind11::keep_alive< 1, 3 >() );
      cls.def_property( "epsilon", [] ( LocalFunctionType &self ) -> UFLLocalFunctions_e6b6d8d3826590442cc40f3834124254::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > >::Conepsilon { return self.conepsilon(); }, [] ( LocalFunctionType &self, const UFLLocalFunctions_e6b6d8d3826590442cc40f3834124254::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > >::Conepsilon &v ) { self.conepsilon() = v; } );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
