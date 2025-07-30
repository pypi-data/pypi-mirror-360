#ifndef GUARD_dd1fb4bd60f2d8b3a062dbbdaedb9fee
#define GUARD_dd1fb4bd60f2d8b3a062dbbdaedb9fee

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

namespace UFLLocalFunctions_dd1fb4bd60f2d8b3a062dbbdaedb9fee
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
    const auto tmp2 = 1 + tmp1[ 0 ];
    const auto tmp3 = tmp2 * tmp2;
    const auto tmp4 = tmp1[ 1 ] * tmp1[ 1 ];
    const auto tmp5 = tmp4 + tmp3;
    const auto tmp6 = 1e-10 + tmp5;
    const auto tmp7 = std::sqrt( tmp6 );
    const auto tmp8 = -0.5 + tmp7;
    const auto tmp9 = -1 + tmp1[ 0 ];
    const auto tmp10 = tmp9 * tmp9;
    const auto tmp11 = tmp4 + tmp10;
    const auto tmp12 = 1e-10 + tmp11;
    const auto tmp13 = std::sqrt( tmp12 );
    const auto tmp14 = -0.5 + tmp13;
    const auto tmp15 = 0.8 + tmp1[ 1 ];
    const auto tmp16 = tmp15 * tmp15;
    const auto tmp17 = tmp1[ 0 ] * tmp1[ 0 ];
    const auto tmp18 = tmp17 + tmp16;
    const auto tmp19 = 1e-10 + tmp18;
    const auto tmp20 = std::sqrt( tmp19 );
    const auto tmp21 = -0.5 + tmp20;
    const auto tmp22 = -1 * tmp21;
    const auto tmp23 = -0.8 + tmp1[ 1 ];
    const auto tmp24 = tmp23 * tmp23;
    const auto tmp25 = tmp17 + tmp24;
    const auto tmp26 = 1e-10 + tmp25;
    const auto tmp27 = std::sqrt( tmp26 );
    const auto tmp28 = -0.5 + tmp27;
    const auto tmp29 = -1 * tmp28;
    const auto tmp30 = tmp17 + tmp4;
    const auto tmp31 = 1e-10 + tmp30;
    const auto tmp32 = std::sqrt( tmp31 );
    const auto tmp33 = -1 + tmp32;
    const auto tmp34 = std::max( tmp33, tmp29 );
    const auto tmp35 = std::max( tmp34, tmp22 );
    const auto tmp36 = std::min( tmp35, tmp14 );
    const auto tmp37 = std::min( tmp36, tmp8 );
    const auto tmp38 = 3 * tmp37;
    const auto tmp39 = tmp38 / tmp0;
    const auto tmp40 = std::tanh( tmp39 );
    const auto tmp41 = -1 * tmp40;
    const auto tmp42 = 1 + tmp41;
    const auto tmp43 = 0.5 * tmp42;
    const auto tmp44 = -1 * tmp43;
    const auto tmp45 = 1 + tmp44;
    const auto tmp46 = tmp45 * tmp43;
    result[ 0 ] = tmp46;
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
    const auto tmp2 = 1 + tmp1[ 0 ];
    const auto tmp3 = tmp2 * tmp2;
    const auto tmp4 = tmp1[ 1 ] * tmp1[ 1 ];
    const auto tmp5 = tmp4 + tmp3;
    const auto tmp6 = 1e-10 + tmp5;
    const auto tmp7 = std::sqrt( tmp6 );
    const auto tmp8 = -0.5 + tmp7;
    const auto tmp9 = -1 + tmp1[ 0 ];
    const auto tmp10 = tmp9 * tmp9;
    const auto tmp11 = tmp4 + tmp10;
    const auto tmp12 = 1e-10 + tmp11;
    const auto tmp13 = std::sqrt( tmp12 );
    const auto tmp14 = -0.5 + tmp13;
    const auto tmp15 = 0.8 + tmp1[ 1 ];
    const auto tmp16 = tmp15 * tmp15;
    const auto tmp17 = tmp1[ 0 ] * tmp1[ 0 ];
    const auto tmp18 = tmp17 + tmp16;
    const auto tmp19 = 1e-10 + tmp18;
    const auto tmp20 = std::sqrt( tmp19 );
    const auto tmp21 = -0.5 + tmp20;
    const auto tmp22 = -1 * tmp21;
    const auto tmp23 = -0.8 + tmp1[ 1 ];
    const auto tmp24 = tmp23 * tmp23;
    const auto tmp25 = tmp17 + tmp24;
    const auto tmp26 = 1e-10 + tmp25;
    const auto tmp27 = std::sqrt( tmp26 );
    const auto tmp28 = -0.5 + tmp27;
    const auto tmp29 = -1 * tmp28;
    const auto tmp30 = tmp17 + tmp4;
    const auto tmp31 = 1e-10 + tmp30;
    const auto tmp32 = std::sqrt( tmp31 );
    const auto tmp33 = -1 + tmp32;
    const auto tmp34 = std::max( tmp33, tmp29 );
    const auto tmp35 = std::max( tmp34, tmp22 );
    const auto tmp36 = std::min( tmp35, tmp14 );
    const auto tmp37 = std::min( tmp36, tmp8 );
    const auto tmp38 = 3 * tmp37;
    const auto tmp39 = tmp38 / tmp0;
    const auto tmp40 = 2.0 * tmp39;
    const auto tmp41 = std::cosh( tmp40 );
    const auto tmp42 = 1.0 + tmp41;
    const auto tmp43 = std::cosh( tmp39 );
    const auto tmp44 = 2.0 * tmp43;
    const auto tmp45 = tmp44 / tmp42;
    const auto tmp46 = std::pow( tmp45, 2 );
    const auto tmp47 = 2 * tmp32;
    typename CoefficientFunctionSpaceType< 0 >::JacobianRangeType tmp48 = jacobianCoefficient< 0 >( x );
    const auto tmp49 = tmp1[ 1 ] * (tmp48[ 1 ])[ 0 ];
    const auto tmp50 = tmp49 + tmp49;
    const auto tmp51 = tmp1[ 0 ] * (tmp48[ 0 ])[ 0 ];
    const auto tmp52 = tmp51 + tmp51;
    const auto tmp53 = tmp52 + tmp50;
    const auto tmp54 = tmp53 / tmp47;
    const auto tmp55 = tmp54 * (tmp33 > tmp29 ? 1 : 0.0);
    const auto tmp56 = 2 * tmp27;
    const auto tmp57 = (tmp48[ 1 ])[ 0 ] * tmp23;
    const auto tmp58 = tmp57 + tmp57;
    const auto tmp59 = tmp52 + tmp58;
    const auto tmp60 = tmp59 / tmp56;
    const auto tmp61 = -1 * tmp60;
    const auto tmp62 = -1 * (tmp33 > tmp29 ? 1 : 0.0);
    const auto tmp63 = 1.0 + tmp62;
    const auto tmp64 = tmp63 * tmp61;
    const auto tmp65 = tmp64 + tmp55;
    const auto tmp66 = tmp65 * (tmp34 > tmp22 ? 1 : 0.0);
    const auto tmp67 = 2 * tmp20;
    const auto tmp68 = (tmp48[ 1 ])[ 0 ] * tmp15;
    const auto tmp69 = tmp68 + tmp68;
    const auto tmp70 = tmp52 + tmp69;
    const auto tmp71 = tmp70 / tmp67;
    const auto tmp72 = -1 * tmp71;
    const auto tmp73 = -1 * (tmp34 > tmp22 ? 1 : 0.0);
    const auto tmp74 = 1.0 + tmp73;
    const auto tmp75 = tmp74 * tmp72;
    const auto tmp76 = tmp75 + tmp66;
    const auto tmp77 = tmp76 * (tmp35 < tmp14 ? 1 : 0.0);
    const auto tmp78 = 2 * tmp13;
    const auto tmp79 = (tmp48[ 0 ])[ 0 ] * tmp9;
    const auto tmp80 = tmp79 + tmp79;
    const auto tmp81 = tmp50 + tmp80;
    const auto tmp82 = tmp81 / tmp78;
    const auto tmp83 = -1 * (tmp35 < tmp14 ? 1 : 0.0);
    const auto tmp84 = 1.0 + tmp83;
    const auto tmp85 = tmp84 * tmp82;
    const auto tmp86 = tmp85 + tmp77;
    const auto tmp87 = tmp86 * (tmp36 < tmp8 ? 1 : 0.0);
    const auto tmp88 = 2 * tmp7;
    const auto tmp89 = (tmp48[ 0 ])[ 0 ] * tmp2;
    const auto tmp90 = tmp89 + tmp89;
    const auto tmp91 = tmp50 + tmp90;
    const auto tmp92 = tmp91 / tmp88;
    const auto tmp93 = -1 * (tmp36 < tmp8 ? 1 : 0.0);
    const auto tmp94 = 1.0 + tmp93;
    const auto tmp95 = tmp94 * tmp92;
    const auto tmp96 = tmp95 + tmp87;
    const auto tmp97 = 3 * tmp96;
    const auto tmp98 = tmp97 / tmp0;
    const auto tmp99 = tmp98 * tmp46;
    const auto tmp100 = -1 * tmp99;
    const auto tmp101 = 0.5 * tmp100;
    const auto tmp102 = std::tanh( tmp39 );
    const auto tmp103 = -1 * tmp102;
    const auto tmp104 = 1 + tmp103;
    const auto tmp105 = 0.5 * tmp104;
    const auto tmp106 = -1 * tmp105;
    const auto tmp107 = 1 + tmp106;
    const auto tmp108 = tmp107 * tmp101;
    const auto tmp109 = -1 * tmp101;
    const auto tmp110 = tmp105 * tmp109;
    const auto tmp111 = tmp110 + tmp108;
    const auto tmp112 = tmp1[ 1 ] * (tmp48[ 1 ])[ 1 ];
    const auto tmp113 = tmp112 + tmp112;
    const auto tmp114 = tmp1[ 0 ] * (tmp48[ 0 ])[ 1 ];
    const auto tmp115 = tmp114 + tmp114;
    const auto tmp116 = tmp115 + tmp113;
    const auto tmp117 = tmp116 / tmp47;
    const auto tmp118 = tmp117 * (tmp33 > tmp29 ? 1 : 0.0);
    const auto tmp119 = (tmp48[ 1 ])[ 1 ] * tmp23;
    const auto tmp120 = tmp119 + tmp119;
    const auto tmp121 = tmp115 + tmp120;
    const auto tmp122 = tmp121 / tmp56;
    const auto tmp123 = -1 * tmp122;
    const auto tmp124 = tmp63 * tmp123;
    const auto tmp125 = tmp124 + tmp118;
    const auto tmp126 = tmp125 * (tmp34 > tmp22 ? 1 : 0.0);
    const auto tmp127 = (tmp48[ 1 ])[ 1 ] * tmp15;
    const auto tmp128 = tmp127 + tmp127;
    const auto tmp129 = tmp115 + tmp128;
    const auto tmp130 = tmp129 / tmp67;
    const auto tmp131 = -1 * tmp130;
    const auto tmp132 = tmp74 * tmp131;
    const auto tmp133 = tmp132 + tmp126;
    const auto tmp134 = tmp133 * (tmp35 < tmp14 ? 1 : 0.0);
    const auto tmp135 = (tmp48[ 0 ])[ 1 ] * tmp9;
    const auto tmp136 = tmp135 + tmp135;
    const auto tmp137 = tmp113 + tmp136;
    const auto tmp138 = tmp137 / tmp78;
    const auto tmp139 = tmp84 * tmp138;
    const auto tmp140 = tmp139 + tmp134;
    const auto tmp141 = tmp140 * (tmp36 < tmp8 ? 1 : 0.0);
    const auto tmp142 = (tmp48[ 0 ])[ 1 ] * tmp2;
    const auto tmp143 = tmp142 + tmp142;
    const auto tmp144 = tmp113 + tmp143;
    const auto tmp145 = tmp144 / tmp88;
    const auto tmp146 = tmp94 * tmp145;
    const auto tmp147 = tmp146 + tmp141;
    const auto tmp148 = 3 * tmp147;
    const auto tmp149 = tmp148 / tmp0;
    const auto tmp150 = tmp149 * tmp46;
    const auto tmp151 = -1 * tmp150;
    const auto tmp152 = 0.5 * tmp151;
    const auto tmp153 = tmp107 * tmp152;
    const auto tmp154 = -1 * tmp152;
    const auto tmp155 = tmp105 * tmp154;
    const auto tmp156 = tmp155 + tmp153;
    (result[ 0 ])[ 0 ] = tmp111;
    (result[ 0 ])[ 1 ] = tmp156;
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
    const auto tmp2 = 1 + tmp1[ 0 ];
    const auto tmp3 = tmp2 * tmp2;
    const auto tmp4 = tmp1[ 1 ] * tmp1[ 1 ];
    const auto tmp5 = tmp4 + tmp3;
    const auto tmp6 = 1e-10 + tmp5;
    const auto tmp7 = std::sqrt( tmp6 );
    const auto tmp8 = -0.5 + tmp7;
    const auto tmp9 = -1 + tmp1[ 0 ];
    const auto tmp10 = tmp9 * tmp9;
    const auto tmp11 = tmp4 + tmp10;
    const auto tmp12 = 1e-10 + tmp11;
    const auto tmp13 = std::sqrt( tmp12 );
    const auto tmp14 = -0.5 + tmp13;
    const auto tmp15 = 0.8 + tmp1[ 1 ];
    const auto tmp16 = tmp15 * tmp15;
    const auto tmp17 = tmp1[ 0 ] * tmp1[ 0 ];
    const auto tmp18 = tmp17 + tmp16;
    const auto tmp19 = 1e-10 + tmp18;
    const auto tmp20 = std::sqrt( tmp19 );
    const auto tmp21 = -0.5 + tmp20;
    const auto tmp22 = -1 * tmp21;
    const auto tmp23 = -0.8 + tmp1[ 1 ];
    const auto tmp24 = tmp23 * tmp23;
    const auto tmp25 = tmp17 + tmp24;
    const auto tmp26 = 1e-10 + tmp25;
    const auto tmp27 = std::sqrt( tmp26 );
    const auto tmp28 = -0.5 + tmp27;
    const auto tmp29 = -1 * tmp28;
    const auto tmp30 = tmp17 + tmp4;
    const auto tmp31 = 1e-10 + tmp30;
    const auto tmp32 = std::sqrt( tmp31 );
    const auto tmp33 = -1 + tmp32;
    const auto tmp34 = std::max( tmp33, tmp29 );
    const auto tmp35 = std::max( tmp34, tmp22 );
    const auto tmp36 = std::min( tmp35, tmp14 );
    const auto tmp37 = std::min( tmp36, tmp8 );
    const auto tmp38 = 3 * tmp37;
    const auto tmp39 = tmp38 / tmp0;
    const auto tmp40 = 2.0 * tmp39;
    const auto tmp41 = std::cosh( tmp40 );
    const auto tmp42 = 1.0 + tmp41;
    const auto tmp43 = std::cosh( tmp39 );
    const auto tmp44 = 2.0 * tmp43;
    const auto tmp45 = tmp44 / tmp42;
    const auto tmp46 = std::pow( tmp45, 2 );
    const auto tmp47 = 2 * tmp32;
    typename CoefficientFunctionSpaceType< 0 >::JacobianRangeType tmp48 = jacobianCoefficient< 0 >( x );
    const auto tmp49 = tmp1[ 1 ] * (tmp48[ 1 ])[ 0 ];
    const auto tmp50 = tmp49 + tmp49;
    const auto tmp51 = tmp1[ 0 ] * (tmp48[ 0 ])[ 0 ];
    const auto tmp52 = tmp51 + tmp51;
    const auto tmp53 = tmp52 + tmp50;
    const auto tmp54 = tmp53 / tmp47;
    const auto tmp55 = tmp54 * (tmp33 > tmp29 ? 1 : 0.0);
    const auto tmp56 = 2 * tmp27;
    const auto tmp57 = (tmp48[ 1 ])[ 0 ] * tmp23;
    const auto tmp58 = tmp57 + tmp57;
    const auto tmp59 = tmp52 + tmp58;
    const auto tmp60 = tmp59 / tmp56;
    const auto tmp61 = -1 * tmp60;
    const auto tmp62 = -1 * (tmp33 > tmp29 ? 1 : 0.0);
    const auto tmp63 = 1.0 + tmp62;
    const auto tmp64 = tmp63 * tmp61;
    const auto tmp65 = tmp64 + tmp55;
    const auto tmp66 = tmp65 * (tmp34 > tmp22 ? 1 : 0.0);
    const auto tmp67 = 2 * tmp20;
    const auto tmp68 = (tmp48[ 1 ])[ 0 ] * tmp15;
    const auto tmp69 = tmp68 + tmp68;
    const auto tmp70 = tmp52 + tmp69;
    const auto tmp71 = tmp70 / tmp67;
    const auto tmp72 = -1 * tmp71;
    const auto tmp73 = -1 * (tmp34 > tmp22 ? 1 : 0.0);
    const auto tmp74 = 1.0 + tmp73;
    const auto tmp75 = tmp74 * tmp72;
    const auto tmp76 = tmp75 + tmp66;
    const auto tmp77 = tmp76 * (tmp35 < tmp14 ? 1 : 0.0);
    const auto tmp78 = 2 * tmp13;
    const auto tmp79 = (tmp48[ 0 ])[ 0 ] * tmp9;
    const auto tmp80 = tmp79 + tmp79;
    const auto tmp81 = tmp50 + tmp80;
    const auto tmp82 = tmp81 / tmp78;
    const auto tmp83 = -1 * (tmp35 < tmp14 ? 1 : 0.0);
    const auto tmp84 = 1.0 + tmp83;
    const auto tmp85 = tmp84 * tmp82;
    const auto tmp86 = tmp85 + tmp77;
    const auto tmp87 = tmp86 * (tmp36 < tmp8 ? 1 : 0.0);
    const auto tmp88 = 2 * tmp7;
    const auto tmp89 = (tmp48[ 0 ])[ 0 ] * tmp2;
    const auto tmp90 = tmp89 + tmp89;
    const auto tmp91 = tmp50 + tmp90;
    const auto tmp92 = tmp91 / tmp88;
    const auto tmp93 = -1 * (tmp36 < tmp8 ? 1 : 0.0);
    const auto tmp94 = 1.0 + tmp93;
    const auto tmp95 = tmp94 * tmp92;
    const auto tmp96 = tmp95 + tmp87;
    const auto tmp97 = 3 * tmp96;
    const auto tmp98 = tmp97 / tmp0;
    const auto tmp99 = tmp98 * tmp46;
    const auto tmp100 = -1 * tmp99;
    const auto tmp101 = 0.5 * tmp100;
    const auto tmp102 = -1 * tmp101;
    const auto tmp103 = tmp102 * tmp101;
    const auto tmp104 = 2 * tmp54;
    const auto tmp105 = tmp104 * tmp54;
    const auto tmp106 = -1 * tmp105;
    typename CoefficientFunctionSpaceType< 0 >::HessianRangeType tmp107 = hessianCoefficient< 0 >( x );
    const auto tmp108 = tmp1[ 1 ] * ((tmp107[ 1 ])[ 0 ])[ 0 ];
    const auto tmp109 = (tmp48[ 1 ])[ 0 ] * (tmp48[ 1 ])[ 0 ];
    const auto tmp110 = tmp109 + tmp108;
    const auto tmp111 = tmp110 + tmp110;
    const auto tmp112 = tmp1[ 0 ] * ((tmp107[ 0 ])[ 0 ])[ 0 ];
    const auto tmp113 = (tmp48[ 0 ])[ 0 ] * (tmp48[ 0 ])[ 0 ];
    const auto tmp114 = tmp113 + tmp112;
    const auto tmp115 = tmp114 + tmp114;
    const auto tmp116 = tmp115 + tmp111;
    const auto tmp117 = tmp116 + tmp106;
    const auto tmp118 = tmp117 / tmp47;
    const auto tmp119 = tmp118 * (tmp33 > tmp29 ? 1 : 0.0);
    const auto tmp120 = 2 * tmp60;
    const auto tmp121 = tmp120 * tmp60;
    const auto tmp122 = -1 * tmp121;
    const auto tmp123 = ((tmp107[ 1 ])[ 0 ])[ 0 ] * tmp23;
    const auto tmp124 = tmp109 + tmp123;
    const auto tmp125 = tmp124 + tmp124;
    const auto tmp126 = tmp115 + tmp125;
    const auto tmp127 = tmp126 + tmp122;
    const auto tmp128 = tmp127 / tmp56;
    const auto tmp129 = -1 * tmp128;
    const auto tmp130 = tmp63 * tmp129;
    const auto tmp131 = tmp130 + tmp119;
    const auto tmp132 = tmp131 * (tmp34 > tmp22 ? 1 : 0.0);
    const auto tmp133 = 2 * tmp71;
    const auto tmp134 = tmp133 * tmp71;
    const auto tmp135 = -1 * tmp134;
    const auto tmp136 = ((tmp107[ 1 ])[ 0 ])[ 0 ] * tmp15;
    const auto tmp137 = tmp109 + tmp136;
    const auto tmp138 = tmp137 + tmp137;
    const auto tmp139 = tmp115 + tmp138;
    const auto tmp140 = tmp139 + tmp135;
    const auto tmp141 = tmp140 / tmp67;
    const auto tmp142 = -1 * tmp141;
    const auto tmp143 = tmp74 * tmp142;
    const auto tmp144 = tmp143 + tmp132;
    const auto tmp145 = tmp144 * (tmp35 < tmp14 ? 1 : 0.0);
    const auto tmp146 = 2 * tmp82;
    const auto tmp147 = tmp146 * tmp82;
    const auto tmp148 = -1 * tmp147;
    const auto tmp149 = ((tmp107[ 0 ])[ 0 ])[ 0 ] * tmp9;
    const auto tmp150 = tmp113 + tmp149;
    const auto tmp151 = tmp150 + tmp150;
    const auto tmp152 = tmp111 + tmp151;
    const auto tmp153 = tmp152 + tmp148;
    const auto tmp154 = tmp153 / tmp78;
    const auto tmp155 = tmp84 * tmp154;
    const auto tmp156 = tmp155 + tmp145;
    const auto tmp157 = tmp156 * (tmp36 < tmp8 ? 1 : 0.0);
    const auto tmp158 = 2 * tmp92;
    const auto tmp159 = tmp158 * tmp92;
    const auto tmp160 = -1 * tmp159;
    const auto tmp161 = ((tmp107[ 0 ])[ 0 ])[ 0 ] * tmp2;
    const auto tmp162 = tmp113 + tmp161;
    const auto tmp163 = tmp162 + tmp162;
    const auto tmp164 = tmp111 + tmp163;
    const auto tmp165 = tmp164 + tmp160;
    const auto tmp166 = tmp165 / tmp88;
    const auto tmp167 = tmp94 * tmp166;
    const auto tmp168 = tmp167 + tmp157;
    const auto tmp169 = 3 * tmp168;
    const auto tmp170 = tmp169 / tmp0;
    const auto tmp171 = tmp170 * tmp46;
    const auto tmp172 = std::sinh( tmp39 );
    const auto tmp173 = tmp98 * tmp172;
    const auto tmp174 = 2.0 * tmp173;
    const auto tmp175 = std::sinh( tmp40 );
    const auto tmp176 = 2.0 * tmp98;
    const auto tmp177 = tmp176 * tmp175;
    const auto tmp178 = tmp177 * tmp45;
    const auto tmp179 = -1 * tmp178;
    const auto tmp180 = tmp179 + tmp174;
    const auto tmp181 = tmp180 / tmp42;
    const auto tmp182 = 2 * tmp181;
    const auto tmp183 = tmp182 * tmp45;
    const auto tmp184 = tmp183 * tmp98;
    const auto tmp185 = tmp184 + tmp171;
    const auto tmp186 = -1 * tmp185;
    const auto tmp187 = 0.5 * tmp186;
    const auto tmp188 = -1 * tmp187;
    const auto tmp189 = std::tanh( tmp39 );
    const auto tmp190 = -1 * tmp189;
    const auto tmp191 = 1 + tmp190;
    const auto tmp192 = 0.5 * tmp191;
    const auto tmp193 = tmp192 * tmp188;
    const auto tmp194 = tmp193 + tmp103;
    const auto tmp195 = -1 * tmp192;
    const auto tmp196 = 1 + tmp195;
    const auto tmp197 = tmp196 * tmp187;
    const auto tmp198 = tmp197 + tmp103;
    const auto tmp199 = tmp198 + tmp194;
    const auto tmp200 = tmp1[ 1 ] * (tmp48[ 1 ])[ 1 ];
    const auto tmp201 = tmp200 + tmp200;
    const auto tmp202 = tmp1[ 0 ] * (tmp48[ 0 ])[ 1 ];
    const auto tmp203 = tmp202 + tmp202;
    const auto tmp204 = tmp203 + tmp201;
    const auto tmp205 = tmp204 / tmp47;
    const auto tmp206 = tmp205 * (tmp33 > tmp29 ? 1 : 0.0);
    const auto tmp207 = (tmp48[ 1 ])[ 1 ] * tmp23;
    const auto tmp208 = tmp207 + tmp207;
    const auto tmp209 = tmp203 + tmp208;
    const auto tmp210 = tmp209 / tmp56;
    const auto tmp211 = -1 * tmp210;
    const auto tmp212 = tmp63 * tmp211;
    const auto tmp213 = tmp212 + tmp206;
    const auto tmp214 = tmp213 * (tmp34 > tmp22 ? 1 : 0.0);
    const auto tmp215 = (tmp48[ 1 ])[ 1 ] * tmp15;
    const auto tmp216 = tmp215 + tmp215;
    const auto tmp217 = tmp203 + tmp216;
    const auto tmp218 = tmp217 / tmp67;
    const auto tmp219 = -1 * tmp218;
    const auto tmp220 = tmp74 * tmp219;
    const auto tmp221 = tmp220 + tmp214;
    const auto tmp222 = tmp221 * (tmp35 < tmp14 ? 1 : 0.0);
    const auto tmp223 = (tmp48[ 0 ])[ 1 ] * tmp9;
    const auto tmp224 = tmp223 + tmp223;
    const auto tmp225 = tmp201 + tmp224;
    const auto tmp226 = tmp225 / tmp78;
    const auto tmp227 = tmp84 * tmp226;
    const auto tmp228 = tmp227 + tmp222;
    const auto tmp229 = tmp228 * (tmp36 < tmp8 ? 1 : 0.0);
    const auto tmp230 = (tmp48[ 0 ])[ 1 ] * tmp2;
    const auto tmp231 = tmp230 + tmp230;
    const auto tmp232 = tmp201 + tmp231;
    const auto tmp233 = tmp232 / tmp88;
    const auto tmp234 = tmp94 * tmp233;
    const auto tmp235 = tmp234 + tmp229;
    const auto tmp236 = 3 * tmp235;
    const auto tmp237 = tmp236 / tmp0;
    const auto tmp238 = tmp237 * tmp46;
    const auto tmp239 = -1 * tmp238;
    const auto tmp240 = 0.5 * tmp239;
    const auto tmp241 = tmp102 * tmp240;
    const auto tmp242 = 2 * tmp205;
    const auto tmp243 = tmp242 * tmp54;
    const auto tmp244 = -1 * tmp243;
    const auto tmp245 = (tmp48[ 1 ])[ 0 ] * (tmp48[ 1 ])[ 1 ];
    const auto tmp246 = tmp1[ 1 ] * ((tmp107[ 1 ])[ 0 ])[ 1 ];
    const auto tmp247 = tmp246 + tmp245;
    const auto tmp248 = tmp247 + tmp247;
    const auto tmp249 = (tmp48[ 0 ])[ 0 ] * (tmp48[ 0 ])[ 1 ];
    const auto tmp250 = tmp1[ 0 ] * ((tmp107[ 0 ])[ 0 ])[ 1 ];
    const auto tmp251 = tmp250 + tmp249;
    const auto tmp252 = tmp251 + tmp251;
    const auto tmp253 = tmp252 + tmp248;
    const auto tmp254 = tmp253 + tmp244;
    const auto tmp255 = tmp254 / tmp47;
    const auto tmp256 = tmp255 * (tmp33 > tmp29 ? 1 : 0.0);
    const auto tmp257 = 2 * tmp210;
    const auto tmp258 = tmp257 * tmp60;
    const auto tmp259 = -1 * tmp258;
    const auto tmp260 = ((tmp107[ 1 ])[ 0 ])[ 1 ] * tmp23;
    const auto tmp261 = tmp245 + tmp260;
    const auto tmp262 = tmp261 + tmp261;
    const auto tmp263 = tmp252 + tmp262;
    const auto tmp264 = tmp263 + tmp259;
    const auto tmp265 = tmp264 / tmp56;
    const auto tmp266 = -1 * tmp265;
    const auto tmp267 = tmp63 * tmp266;
    const auto tmp268 = tmp267 + tmp256;
    const auto tmp269 = tmp268 * (tmp34 > tmp22 ? 1 : 0.0);
    const auto tmp270 = 2 * tmp218;
    const auto tmp271 = tmp270 * tmp71;
    const auto tmp272 = -1 * tmp271;
    const auto tmp273 = ((tmp107[ 1 ])[ 0 ])[ 1 ] * tmp15;
    const auto tmp274 = tmp245 + tmp273;
    const auto tmp275 = tmp274 + tmp274;
    const auto tmp276 = tmp252 + tmp275;
    const auto tmp277 = tmp276 + tmp272;
    const auto tmp278 = tmp277 / tmp67;
    const auto tmp279 = -1 * tmp278;
    const auto tmp280 = tmp74 * tmp279;
    const auto tmp281 = tmp280 + tmp269;
    const auto tmp282 = tmp281 * (tmp35 < tmp14 ? 1 : 0.0);
    const auto tmp283 = 2 * tmp226;
    const auto tmp284 = tmp283 * tmp82;
    const auto tmp285 = -1 * tmp284;
    const auto tmp286 = ((tmp107[ 0 ])[ 0 ])[ 1 ] * tmp9;
    const auto tmp287 = tmp249 + tmp286;
    const auto tmp288 = tmp287 + tmp287;
    const auto tmp289 = tmp248 + tmp288;
    const auto tmp290 = tmp289 + tmp285;
    const auto tmp291 = tmp290 / tmp78;
    const auto tmp292 = tmp84 * tmp291;
    const auto tmp293 = tmp292 + tmp282;
    const auto tmp294 = tmp293 * (tmp36 < tmp8 ? 1 : 0.0);
    const auto tmp295 = 2 * tmp233;
    const auto tmp296 = tmp295 * tmp92;
    const auto tmp297 = -1 * tmp296;
    const auto tmp298 = ((tmp107[ 0 ])[ 0 ])[ 1 ] * tmp2;
    const auto tmp299 = tmp249 + tmp298;
    const auto tmp300 = tmp299 + tmp299;
    const auto tmp301 = tmp248 + tmp300;
    const auto tmp302 = tmp301 + tmp297;
    const auto tmp303 = tmp302 / tmp88;
    const auto tmp304 = tmp94 * tmp303;
    const auto tmp305 = tmp304 + tmp294;
    const auto tmp306 = 3 * tmp305;
    const auto tmp307 = tmp306 / tmp0;
    const auto tmp308 = tmp307 * tmp46;
    const auto tmp309 = tmp237 * tmp172;
    const auto tmp310 = 2.0 * tmp309;
    const auto tmp311 = 2.0 * tmp237;
    const auto tmp312 = tmp311 * tmp175;
    const auto tmp313 = tmp312 * tmp45;
    const auto tmp314 = -1 * tmp313;
    const auto tmp315 = tmp314 + tmp310;
    const auto tmp316 = tmp315 / tmp42;
    const auto tmp317 = 2 * tmp316;
    const auto tmp318 = tmp317 * tmp45;
    const auto tmp319 = tmp318 * tmp98;
    const auto tmp320 = tmp319 + tmp308;
    const auto tmp321 = -1 * tmp320;
    const auto tmp322 = 0.5 * tmp321;
    const auto tmp323 = -1 * tmp322;
    const auto tmp324 = tmp192 * tmp323;
    const auto tmp325 = tmp324 + tmp241;
    const auto tmp326 = -1 * tmp240;
    const auto tmp327 = tmp326 * tmp101;
    const auto tmp328 = tmp196 * tmp322;
    const auto tmp329 = tmp328 + tmp327;
    const auto tmp330 = tmp329 + tmp325;
    const auto tmp331 = tmp104 * tmp205;
    const auto tmp332 = -1 * tmp331;
    const auto tmp333 = tmp1[ 1 ] * ((tmp107[ 1 ])[ 1 ])[ 0 ];
    const auto tmp334 = tmp245 + tmp333;
    const auto tmp335 = tmp334 + tmp334;
    const auto tmp336 = tmp1[ 0 ] * ((tmp107[ 0 ])[ 1 ])[ 0 ];
    const auto tmp337 = tmp249 + tmp336;
    const auto tmp338 = tmp337 + tmp337;
    const auto tmp339 = tmp338 + tmp335;
    const auto tmp340 = tmp339 + tmp332;
    const auto tmp341 = tmp340 / tmp47;
    const auto tmp342 = tmp341 * (tmp33 > tmp29 ? 1 : 0.0);
    const auto tmp343 = tmp120 * tmp210;
    const auto tmp344 = -1 * tmp343;
    const auto tmp345 = ((tmp107[ 1 ])[ 1 ])[ 0 ] * tmp23;
    const auto tmp346 = tmp245 + tmp345;
    const auto tmp347 = tmp346 + tmp346;
    const auto tmp348 = tmp338 + tmp347;
    const auto tmp349 = tmp348 + tmp344;
    const auto tmp350 = tmp349 / tmp56;
    const auto tmp351 = -1 * tmp350;
    const auto tmp352 = tmp63 * tmp351;
    const auto tmp353 = tmp352 + tmp342;
    const auto tmp354 = tmp353 * (tmp34 > tmp22 ? 1 : 0.0);
    const auto tmp355 = tmp133 * tmp218;
    const auto tmp356 = -1 * tmp355;
    const auto tmp357 = ((tmp107[ 1 ])[ 1 ])[ 0 ] * tmp15;
    const auto tmp358 = tmp245 + tmp357;
    const auto tmp359 = tmp358 + tmp358;
    const auto tmp360 = tmp338 + tmp359;
    const auto tmp361 = tmp360 + tmp356;
    const auto tmp362 = tmp361 / tmp67;
    const auto tmp363 = -1 * tmp362;
    const auto tmp364 = tmp74 * tmp363;
    const auto tmp365 = tmp364 + tmp354;
    const auto tmp366 = tmp365 * (tmp35 < tmp14 ? 1 : 0.0);
    const auto tmp367 = tmp146 * tmp226;
    const auto tmp368 = -1 * tmp367;
    const auto tmp369 = ((tmp107[ 0 ])[ 1 ])[ 0 ] * tmp9;
    const auto tmp370 = tmp249 + tmp369;
    const auto tmp371 = tmp370 + tmp370;
    const auto tmp372 = tmp335 + tmp371;
    const auto tmp373 = tmp372 + tmp368;
    const auto tmp374 = tmp373 / tmp78;
    const auto tmp375 = tmp84 * tmp374;
    const auto tmp376 = tmp375 + tmp366;
    const auto tmp377 = tmp376 * (tmp36 < tmp8 ? 1 : 0.0);
    const auto tmp378 = tmp158 * tmp233;
    const auto tmp379 = -1 * tmp378;
    const auto tmp380 = ((tmp107[ 0 ])[ 1 ])[ 0 ] * tmp2;
    const auto tmp381 = tmp249 + tmp380;
    const auto tmp382 = tmp381 + tmp381;
    const auto tmp383 = tmp335 + tmp382;
    const auto tmp384 = tmp383 + tmp379;
    const auto tmp385 = tmp384 / tmp88;
    const auto tmp386 = tmp94 * tmp385;
    const auto tmp387 = tmp386 + tmp377;
    const auto tmp388 = 3 * tmp387;
    const auto tmp389 = tmp388 / tmp0;
    const auto tmp390 = tmp389 * tmp46;
    const auto tmp391 = tmp183 * tmp237;
    const auto tmp392 = tmp391 + tmp390;
    const auto tmp393 = -1 * tmp392;
    const auto tmp394 = 0.5 * tmp393;
    const auto tmp395 = tmp196 * tmp394;
    const auto tmp396 = tmp395 + tmp241;
    const auto tmp397 = -1 * tmp394;
    const auto tmp398 = tmp192 * tmp397;
    const auto tmp399 = tmp398 + tmp327;
    const auto tmp400 = tmp399 + tmp396;
    const auto tmp401 = tmp326 * tmp240;
    const auto tmp402 = tmp242 * tmp205;
    const auto tmp403 = -1 * tmp402;
    const auto tmp404 = tmp1[ 1 ] * ((tmp107[ 1 ])[ 1 ])[ 1 ];
    const auto tmp405 = (tmp48[ 1 ])[ 1 ] * (tmp48[ 1 ])[ 1 ];
    const auto tmp406 = tmp405 + tmp404;
    const auto tmp407 = tmp406 + tmp406;
    const auto tmp408 = tmp1[ 0 ] * ((tmp107[ 0 ])[ 1 ])[ 1 ];
    const auto tmp409 = (tmp48[ 0 ])[ 1 ] * (tmp48[ 0 ])[ 1 ];
    const auto tmp410 = tmp409 + tmp408;
    const auto tmp411 = tmp410 + tmp410;
    const auto tmp412 = tmp411 + tmp407;
    const auto tmp413 = tmp412 + tmp403;
    const auto tmp414 = tmp413 / tmp47;
    const auto tmp415 = tmp414 * (tmp33 > tmp29 ? 1 : 0.0);
    const auto tmp416 = tmp257 * tmp210;
    const auto tmp417 = -1 * tmp416;
    const auto tmp418 = ((tmp107[ 1 ])[ 1 ])[ 1 ] * tmp23;
    const auto tmp419 = tmp405 + tmp418;
    const auto tmp420 = tmp419 + tmp419;
    const auto tmp421 = tmp411 + tmp420;
    const auto tmp422 = tmp421 + tmp417;
    const auto tmp423 = tmp422 / tmp56;
    const auto tmp424 = -1 * tmp423;
    const auto tmp425 = tmp63 * tmp424;
    const auto tmp426 = tmp425 + tmp415;
    const auto tmp427 = tmp426 * (tmp34 > tmp22 ? 1 : 0.0);
    const auto tmp428 = tmp270 * tmp218;
    const auto tmp429 = -1 * tmp428;
    const auto tmp430 = ((tmp107[ 1 ])[ 1 ])[ 1 ] * tmp15;
    const auto tmp431 = tmp405 + tmp430;
    const auto tmp432 = tmp431 + tmp431;
    const auto tmp433 = tmp411 + tmp432;
    const auto tmp434 = tmp433 + tmp429;
    const auto tmp435 = tmp434 / tmp67;
    const auto tmp436 = -1 * tmp435;
    const auto tmp437 = tmp74 * tmp436;
    const auto tmp438 = tmp437 + tmp427;
    const auto tmp439 = tmp438 * (tmp35 < tmp14 ? 1 : 0.0);
    const auto tmp440 = tmp283 * tmp226;
    const auto tmp441 = -1 * tmp440;
    const auto tmp442 = ((tmp107[ 0 ])[ 1 ])[ 1 ] * tmp9;
    const auto tmp443 = tmp409 + tmp442;
    const auto tmp444 = tmp443 + tmp443;
    const auto tmp445 = tmp407 + tmp444;
    const auto tmp446 = tmp445 + tmp441;
    const auto tmp447 = tmp446 / tmp78;
    const auto tmp448 = tmp84 * tmp447;
    const auto tmp449 = tmp448 + tmp439;
    const auto tmp450 = tmp449 * (tmp36 < tmp8 ? 1 : 0.0);
    const auto tmp451 = tmp295 * tmp233;
    const auto tmp452 = -1 * tmp451;
    const auto tmp453 = ((tmp107[ 0 ])[ 1 ])[ 1 ] * tmp2;
    const auto tmp454 = tmp409 + tmp453;
    const auto tmp455 = tmp454 + tmp454;
    const auto tmp456 = tmp407 + tmp455;
    const auto tmp457 = tmp456 + tmp452;
    const auto tmp458 = tmp457 / tmp88;
    const auto tmp459 = tmp94 * tmp458;
    const auto tmp460 = tmp459 + tmp450;
    const auto tmp461 = 3 * tmp460;
    const auto tmp462 = tmp461 / tmp0;
    const auto tmp463 = tmp462 * tmp46;
    const auto tmp464 = tmp318 * tmp237;
    const auto tmp465 = tmp464 + tmp463;
    const auto tmp466 = -1 * tmp465;
    const auto tmp467 = 0.5 * tmp466;
    const auto tmp468 = -1 * tmp467;
    const auto tmp469 = tmp192 * tmp468;
    const auto tmp470 = tmp469 + tmp401;
    const auto tmp471 = tmp196 * tmp467;
    const auto tmp472 = tmp471 + tmp401;
    const auto tmp473 = tmp472 + tmp470;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp199;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp330;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp400;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp473;
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

} // namespace UFLLocalFunctions_dd1fb4bd60f2d8b3a062dbbdaedb9fee

PYBIND11_MODULE( localfunction_dd1fb4bd60f2d8b3a062dbbdaedb9fee_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef UFLLocalFunctions_dd1fb4bd60f2d8b3a062dbbdaedb9fee::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_dd1fb4bd60f2d8b3a062dbbdaedb9fee::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_dd1fb4bd60f2d8b3a062dbbdaedb9fee_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order, const Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > &coeffbndproj ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>(gridView),name,order, coeffbndproj); } ), pybind11::keep_alive< 1, 2 >(), pybind11::keep_alive< 1, 3 >() );
      cls.def_property( "epsilon", [] ( LocalFunctionType &self ) -> UFLLocalFunctions_dd1fb4bd60f2d8b3a062dbbdaedb9fee::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > >::Conepsilon { return self.conepsilon(); }, [] ( LocalFunctionType &self, const UFLLocalFunctions_dd1fb4bd60f2d8b3a062dbbdaedb9fee::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > >::Conepsilon &v ) { self.conepsilon() = v; } );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
