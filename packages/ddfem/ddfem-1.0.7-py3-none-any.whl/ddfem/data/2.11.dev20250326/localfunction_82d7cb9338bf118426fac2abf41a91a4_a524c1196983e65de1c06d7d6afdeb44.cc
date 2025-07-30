#ifndef GUARD_82d7cb9338bf118426fac2abf41a91a4
#define GUARD_82d7cb9338bf118426fac2abf41a91a4

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

namespace UFLLocalFunctions_82d7cb9338bf118426fac2abf41a91a4
{

  // UFLLocalFunction
// ----------------

template< class GridPart, class Coeffbndproj, class Coeffddm, class Coeffsdfprojfull, class Coeffphidomain >
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
  typedef std::tuple< Dune::Fem::GridFunctionSpace< GridPartType, Dune::FieldVector< double, 2 > >, Dune::Fem::GridFunctionSpace< GridPartType, Dune::FieldVector< double, 1 > >, Dune::Fem::GridFunctionSpace< GridPartType, Dune::FieldVector< double, 1 > >, Dune::Fem::GridFunctionSpace< GridPartType, Dune::FieldVector< double, 1 > > > CoefficientFunctionSpaceTupleType;
  typedef std::tuple< Coeffbndproj, Coeffddm, Coeffsdfprojfull, Coeffphidomain > CoefficientTupleType;
  template< std::size_t i >
  using CoefficientFunctionSpaceType = std::tuple_element_t< i, CoefficientFunctionSpaceTupleType >;
  template< std::size_t i >
  using CoefficientRangeType = typename CoefficientFunctionSpaceType< i >::RangeType;
  template< std::size_t i >
  using CoefficientJacobianRangeType = typename CoefficientFunctionSpaceType< i >::JacobianRangeType;
  static constexpr bool gridPartValid = Dune::Fem::checkGridPartValid<GridPartType,Dune::Fem::ConstLocalFunction<Coeffbndproj>>() && Dune::Fem::checkGridPartValid<GridPartType,Dune::Fem::ConstLocalFunction<Coeffddm>>() && Dune::Fem::checkGridPartValid<GridPartType,Dune::Fem::ConstLocalFunction<Coeffsdfprojfull>>() && Dune::Fem::checkGridPartValid<GridPartType,Dune::Fem::ConstLocalFunction<Coeffphidomain>>();
  template< std::size_t i >
  using CoefficientType = std::tuple_element_t< i, CoefficientTupleType >;
  template< std::size_t i >
  using ConstantType = typename std::tuple_element_t< i, ConstantTupleType >::element_type;
  using BaseType::entity;
  using BaseType::geometry;

  UFLLocalFunction ( const GridPartType &gridPart, const std::string &name, int order, const Coeffbndproj &coeffbndproj, const Coeffddm &coeffddm, const Coeffsdfprojfull &coeffsdfprojfull, const Coeffphidomain &coeffphidomain, const Dune::Fem::ParameterReader &parameter = Dune::Fem::Parameter::container() )
    : BaseType(gridPart,name,order),
      coefficients_( Dune::Fem::ConstLocalFunction< Coeffbndproj >( coeffbndproj ), Dune::Fem::ConstLocalFunction< Coeffddm >( coeffddm ), Dune::Fem::ConstLocalFunction< Coeffsdfprojfull >( coeffsdfprojfull ), Dune::Fem::ConstLocalFunction< Coeffphidomain >( coeffphidomain ) )
  {}

  void bind ( const IntersectionType &intersection, Side side )
  {
    BaseType::bind(intersection, side);
    std::get< 0 >( coefficients_ ).bind( this->entity() );
    std::get< 1 >( coefficients_ ).bind( this->entity() );
    std::get< 2 >( coefficients_ ).bind( this->entity() );
    std::get< 3 >( coefficients_ ).bind( this->entity() );
  }

  void bind ( const EntityType &entity )
  {
    BaseType::bind(entity);
    std::get< 0 >( coefficients_ ).bind( this->entity() );
    std::get< 1 >( coefficients_ ).bind( this->entity() );
    std::get< 2 >( coefficients_ ).bind( this->entity() );
    std::get< 3 >( coefficients_ ).bind( this->entity() );
  }

  void unbind ()
  {
    BaseType::unbind();
    std::get< 0 >( coefficients_ ).unbind();
    std::get< 1 >( coefficients_ ).unbind();
    std::get< 2 >( coefficients_ ).unbind();
    std::get< 3 >( coefficients_ ).unbind();
  }

  template< class Point >
  void evaluate ( const Point &x, typename FunctionSpaceType::RangeType &result ) const
  {
    using std::max;
    using std::min;
    using std::sin;
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
    typename CoefficientFunctionSpaceType< 3 >::RangeType tmp39 = evaluateCoefficient< 3 >( x );
    typename CoefficientFunctionSpaceType< 2 >::RangeType tmp40 = evaluateCoefficient< 2 >( x );
    const auto tmp41 = 1e-10 + tmp40[ 0 ];
    typename CoefficientFunctionSpaceType< 0 >::RangeType tmp42 = evaluateCoefficient< 0 >( x );
    const auto tmp43 = 3.141592653589793 * tmp42[ 1 ];
    const auto tmp44 = std::sin( tmp43 );
    const auto tmp45 = 3.141592653589793 * tmp42[ 0 ];
    const auto tmp46 = std::sin( tmp45 );
    const auto tmp47 = tmp46 * tmp44;
    const auto tmp48 = -1 * tmp47;
    typename CoefficientFunctionSpaceType< 1 >::RangeType tmp49 = evaluateCoefficient< 1 >( x );
    const auto tmp50 = tmp49[ 0 ] + tmp48;
    const auto tmp51 = tmp40[ 0 ] * tmp50;
    const auto tmp52 = tmp51 / tmp41;
    typename CoefficientFunctionSpaceType< 3 >::JacobianRangeType tmp53 = jacobianCoefficient< 3 >( x );
    const auto tmp54 = (tmp53[ 0 ])[ 1 ] * tmp52;
    const auto tmp55 = tmp54 / tmp39[ 0 ];
    typename CoefficientFunctionSpaceType< 1 >::JacobianRangeType tmp56 = jacobianCoefficient< 1 >( x );
    const auto tmp57 = (tmp56[ 0 ])[ 1 ] + tmp55;
    const auto tmp58 = tmp57 * tmp57;
    const auto tmp59 = (tmp53[ 0 ])[ 0 ] * tmp52;
    const auto tmp60 = tmp59 / tmp39[ 0 ];
    const auto tmp61 = (tmp56[ 0 ])[ 0 ] + tmp60;
    const auto tmp62 = tmp61 * tmp61;
    const auto tmp63 = tmp62 + tmp58;
    const auto tmp64 = tmp63 * (tmp38 <= 0.0 ? 1 : 0.0);
    result[ 0 ] = tmp64;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::cos;
    using std::max;
    using std::min;
    using std::sin;
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
    typename CoefficientFunctionSpaceType< 3 >::RangeType tmp39 = evaluateCoefficient< 3 >( x );
    typename CoefficientFunctionSpaceType< 2 >::RangeType tmp40 = evaluateCoefficient< 2 >( x );
    const auto tmp41 = 1e-10 + tmp40[ 0 ];
    typename CoefficientFunctionSpaceType< 0 >::RangeType tmp42 = evaluateCoefficient< 0 >( x );
    const auto tmp43 = 3.141592653589793 * tmp42[ 1 ];
    const auto tmp44 = std::sin( tmp43 );
    const auto tmp45 = 3.141592653589793 * tmp42[ 0 ];
    const auto tmp46 = std::sin( tmp45 );
    const auto tmp47 = tmp46 * tmp44;
    const auto tmp48 = -1 * tmp47;
    typename CoefficientFunctionSpaceType< 1 >::RangeType tmp49 = evaluateCoefficient< 1 >( x );
    const auto tmp50 = tmp49[ 0 ] + tmp48;
    const auto tmp51 = tmp40[ 0 ] * tmp50;
    const auto tmp52 = tmp51 / tmp41;
    typename CoefficientFunctionSpaceType< 3 >::JacobianRangeType tmp53 = jacobianCoefficient< 3 >( x );
    const auto tmp54 = (tmp53[ 0 ])[ 1 ] * tmp52;
    const auto tmp55 = tmp54 / tmp39[ 0 ];
    typename CoefficientFunctionSpaceType< 1 >::JacobianRangeType tmp56 = jacobianCoefficient< 1 >( x );
    const auto tmp57 = (tmp56[ 0 ])[ 1 ] + tmp55;
    const auto tmp58 = (tmp53[ 0 ])[ 0 ] * tmp55;
    const auto tmp59 = -1 * tmp58;
    typename CoefficientFunctionSpaceType< 3 >::HessianRangeType tmp60 = hessianCoefficient< 3 >( x );
    const auto tmp61 = ((tmp60[ 0 ])[ 1 ])[ 0 ] * tmp52;
    typename CoefficientFunctionSpaceType< 2 >::JacobianRangeType tmp62 = jacobianCoefficient< 2 >( x );
    const auto tmp63 = (tmp62[ 0 ])[ 0 ] * tmp52;
    const auto tmp64 = -1 * tmp63;
    const auto tmp65 = (tmp62[ 0 ])[ 0 ] * tmp50;
    const auto tmp66 = std::cos( tmp45 );
    typename CoefficientFunctionSpaceType< 0 >::JacobianRangeType tmp67 = jacobianCoefficient< 0 >( x );
    const auto tmp68 = 3.141592653589793 * (tmp67[ 0 ])[ 0 ];
    const auto tmp69 = tmp68 * tmp66;
    const auto tmp70 = tmp69 * tmp44;
    const auto tmp71 = std::cos( tmp43 );
    const auto tmp72 = 3.141592653589793 * (tmp67[ 1 ])[ 0 ];
    const auto tmp73 = tmp72 * tmp71;
    const auto tmp74 = tmp73 * tmp46;
    const auto tmp75 = tmp74 + tmp70;
    const auto tmp76 = -1 * tmp75;
    const auto tmp77 = (tmp56[ 0 ])[ 0 ] + tmp76;
    const auto tmp78 = tmp40[ 0 ] * tmp77;
    const auto tmp79 = tmp78 + tmp65;
    const auto tmp80 = tmp79 + tmp64;
    const auto tmp81 = tmp80 / tmp41;
    const auto tmp82 = (tmp53[ 0 ])[ 1 ] * tmp81;
    const auto tmp83 = tmp82 + tmp61;
    const auto tmp84 = tmp83 + tmp59;
    const auto tmp85 = tmp84 / tmp39[ 0 ];
    typename CoefficientFunctionSpaceType< 1 >::HessianRangeType tmp86 = hessianCoefficient< 1 >( x );
    const auto tmp87 = ((tmp86[ 0 ])[ 1 ])[ 0 ] + tmp85;
    const auto tmp88 = tmp87 * tmp57;
    const auto tmp89 = tmp57 * tmp87;
    const auto tmp90 = tmp89 + tmp88;
    const auto tmp91 = (tmp53[ 0 ])[ 0 ] * tmp52;
    const auto tmp92 = tmp91 / tmp39[ 0 ];
    const auto tmp93 = (tmp56[ 0 ])[ 0 ] + tmp92;
    const auto tmp94 = (tmp53[ 0 ])[ 0 ] * tmp92;
    const auto tmp95 = -1 * tmp94;
    const auto tmp96 = ((tmp60[ 0 ])[ 0 ])[ 0 ] * tmp52;
    const auto tmp97 = (tmp53[ 0 ])[ 0 ] * tmp81;
    const auto tmp98 = tmp97 + tmp96;
    const auto tmp99 = tmp98 + tmp95;
    const auto tmp100 = tmp99 / tmp39[ 0 ];
    const auto tmp101 = ((tmp86[ 0 ])[ 0 ])[ 0 ] + tmp100;
    const auto tmp102 = tmp101 * tmp93;
    const auto tmp103 = tmp93 * tmp101;
    const auto tmp104 = tmp103 + tmp102;
    const auto tmp105 = tmp104 + tmp90;
    const auto tmp106 = tmp105 * (tmp38 <= 0.0 ? 1 : 0.0);
    const auto tmp107 = (tmp53[ 0 ])[ 1 ] * tmp55;
    const auto tmp108 = -1 * tmp107;
    const auto tmp109 = ((tmp60[ 0 ])[ 1 ])[ 1 ] * tmp52;
    const auto tmp110 = (tmp62[ 0 ])[ 1 ] * tmp52;
    const auto tmp111 = -1 * tmp110;
    const auto tmp112 = (tmp62[ 0 ])[ 1 ] * tmp50;
    const auto tmp113 = 3.141592653589793 * (tmp67[ 0 ])[ 1 ];
    const auto tmp114 = tmp113 * tmp66;
    const auto tmp115 = tmp114 * tmp44;
    const auto tmp116 = 3.141592653589793 * (tmp67[ 1 ])[ 1 ];
    const auto tmp117 = tmp116 * tmp71;
    const auto tmp118 = tmp117 * tmp46;
    const auto tmp119 = tmp118 + tmp115;
    const auto tmp120 = -1 * tmp119;
    const auto tmp121 = (tmp56[ 0 ])[ 1 ] + tmp120;
    const auto tmp122 = tmp40[ 0 ] * tmp121;
    const auto tmp123 = tmp122 + tmp112;
    const auto tmp124 = tmp123 + tmp111;
    const auto tmp125 = tmp124 / tmp41;
    const auto tmp126 = (tmp53[ 0 ])[ 1 ] * tmp125;
    const auto tmp127 = tmp126 + tmp109;
    const auto tmp128 = tmp127 + tmp108;
    const auto tmp129 = tmp128 / tmp39[ 0 ];
    const auto tmp130 = ((tmp86[ 0 ])[ 1 ])[ 1 ] + tmp129;
    const auto tmp131 = tmp130 * tmp57;
    const auto tmp132 = tmp57 * tmp130;
    const auto tmp133 = tmp132 + tmp131;
    const auto tmp134 = (tmp53[ 0 ])[ 1 ] * tmp92;
    const auto tmp135 = -1 * tmp134;
    const auto tmp136 = ((tmp60[ 0 ])[ 0 ])[ 1 ] * tmp52;
    const auto tmp137 = (tmp53[ 0 ])[ 0 ] * tmp125;
    const auto tmp138 = tmp137 + tmp136;
    const auto tmp139 = tmp138 + tmp135;
    const auto tmp140 = tmp139 / tmp39[ 0 ];
    const auto tmp141 = ((tmp86[ 0 ])[ 0 ])[ 1 ] + tmp140;
    const auto tmp142 = tmp141 * tmp93;
    const auto tmp143 = tmp93 * tmp141;
    const auto tmp144 = tmp143 + tmp142;
    const auto tmp145 = tmp144 + tmp133;
    const auto tmp146 = tmp145 * (tmp38 <= 0.0 ? 1 : 0.0);
    (result[ 0 ])[ 0 ] = tmp106;
    (result[ 0 ])[ 1 ] = tmp146;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    DUNE_THROW(Dune::NotImplemented,"hessian method could not be generated for local function (TooHighDerivative('CodeGenerator does not allow for third order derivatives, yet.'))");
    result=typename FunctionSpaceType::HessianRangeType(0);
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
  std::tuple< Dune::Fem::ConstLocalFunction< Coeffbndproj >, Dune::Fem::ConstLocalFunction< Coeffddm >, Dune::Fem::ConstLocalFunction< Coeffsdfprojfull >, Dune::Fem::ConstLocalFunction< Coeffphidomain > > coefficients_;
};

} // namespace UFLLocalFunctions_82d7cb9338bf118426fac2abf41a91a4

PYBIND11_MODULE( localfunction_82d7cb9338bf118426fac2abf41a91a4_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef UFLLocalFunctions_82d7cb9338bf118426fac2abf41a91a4::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_82d7cb9338bf118426fac2abf41a91a4::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_82d7cb9338bf118426fac2abf41a91a4_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order, const Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > &coeffbndproj, const Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > > &coeffddm, const Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > > &coeffsdfprojfull, const Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > > &coeffphidomain ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>(gridView),name,order, coeffbndproj, coeffddm, coeffsdfprojfull, coeffphidomain); } ), pybind11::keep_alive< 1, 2 >(), pybind11::keep_alive< 1, 3 >(), pybind11::keep_alive< 1, 4 >(), pybind11::keep_alive< 1, 5 >(), pybind11::keep_alive< 1, 6 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
