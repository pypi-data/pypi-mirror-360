#ifndef GUARD_b20910b6c8d57cb5e6a7ff4b89b91618
#define GUARD_b20910b6c8d57cb5e6a7ff4b89b91618

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

namespace UFLLocalFunctions_b20910b6c8d57cb5e6a7ff4b89b91618
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
    const auto tmp8 = 3 * tmp7;
    const auto tmp9 = tmp8 / tmp0;
    const auto tmp10 = std::tanh( tmp9 );
    const auto tmp11 = -1 * tmp10;
    const auto tmp12 = 1 + tmp11;
    const auto tmp13 = 0.5 * tmp12;
    const auto tmp14 = -1 * tmp13;
    const auto tmp15 = 1 + tmp14;
    const auto tmp16 = tmp15 * tmp13;
    result[ 0 ] = tmp16;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::cosh;
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
    const auto tmp8 = 3 * tmp7;
    const auto tmp9 = tmp8 / tmp0;
    const auto tmp10 = 2.0 * tmp9;
    const auto tmp11 = std::cosh( tmp10 );
    const auto tmp12 = 1.0 + tmp11;
    const auto tmp13 = std::cosh( tmp9 );
    const auto tmp14 = 2.0 * tmp13;
    const auto tmp15 = tmp14 / tmp12;
    const auto tmp16 = std::pow( tmp15, 2 );
    const auto tmp17 = 2 * tmp6;
    typename CoefficientFunctionSpaceType< 0 >::JacobianRangeType tmp18 = jacobianCoefficient< 0 >( x );
    const auto tmp19 = tmp1[ 1 ] * (tmp18[ 1 ])[ 0 ];
    const auto tmp20 = tmp19 + tmp19;
    const auto tmp21 = tmp1[ 0 ] * (tmp18[ 0 ])[ 0 ];
    const auto tmp22 = tmp21 + tmp21;
    const auto tmp23 = tmp22 + tmp20;
    const auto tmp24 = tmp23 / tmp17;
    const auto tmp25 = 3 * tmp24;
    const auto tmp26 = tmp25 / tmp0;
    const auto tmp27 = tmp26 * tmp16;
    const auto tmp28 = -1 * tmp27;
    const auto tmp29 = 0.5 * tmp28;
    const auto tmp30 = std::tanh( tmp9 );
    const auto tmp31 = -1 * tmp30;
    const auto tmp32 = 1 + tmp31;
    const auto tmp33 = 0.5 * tmp32;
    const auto tmp34 = -1 * tmp33;
    const auto tmp35 = 1 + tmp34;
    const auto tmp36 = tmp35 * tmp29;
    const auto tmp37 = -1 * tmp29;
    const auto tmp38 = tmp33 * tmp37;
    const auto tmp39 = tmp38 + tmp36;
    const auto tmp40 = tmp1[ 1 ] * (tmp18[ 1 ])[ 1 ];
    const auto tmp41 = tmp40 + tmp40;
    const auto tmp42 = tmp1[ 0 ] * (tmp18[ 0 ])[ 1 ];
    const auto tmp43 = tmp42 + tmp42;
    const auto tmp44 = tmp43 + tmp41;
    const auto tmp45 = tmp44 / tmp17;
    const auto tmp46 = 3 * tmp45;
    const auto tmp47 = tmp46 / tmp0;
    const auto tmp48 = tmp47 * tmp16;
    const auto tmp49 = -1 * tmp48;
    const auto tmp50 = 0.5 * tmp49;
    const auto tmp51 = tmp35 * tmp50;
    const auto tmp52 = -1 * tmp50;
    const auto tmp53 = tmp33 * tmp52;
    const auto tmp54 = tmp53 + tmp51;
    (result[ 0 ])[ 0 ] = tmp39;
    (result[ 0 ])[ 1 ] = tmp54;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::cosh;
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
    const auto tmp8 = 3 * tmp7;
    const auto tmp9 = tmp8 / tmp0;
    const auto tmp10 = 2.0 * tmp9;
    const auto tmp11 = std::cosh( tmp10 );
    const auto tmp12 = 1.0 + tmp11;
    const auto tmp13 = std::cosh( tmp9 );
    const auto tmp14 = 2.0 * tmp13;
    const auto tmp15 = tmp14 / tmp12;
    const auto tmp16 = std::pow( tmp15, 2 );
    const auto tmp17 = 2 * tmp6;
    typename CoefficientFunctionSpaceType< 0 >::JacobianRangeType tmp18 = jacobianCoefficient< 0 >( x );
    const auto tmp19 = tmp1[ 1 ] * (tmp18[ 1 ])[ 0 ];
    const auto tmp20 = tmp19 + tmp19;
    const auto tmp21 = tmp1[ 0 ] * (tmp18[ 0 ])[ 0 ];
    const auto tmp22 = tmp21 + tmp21;
    const auto tmp23 = tmp22 + tmp20;
    const auto tmp24 = tmp23 / tmp17;
    const auto tmp25 = 3 * tmp24;
    const auto tmp26 = tmp25 / tmp0;
    const auto tmp27 = tmp26 * tmp16;
    const auto tmp28 = -1 * tmp27;
    const auto tmp29 = 0.5 * tmp28;
    const auto tmp30 = -1 * tmp29;
    const auto tmp31 = tmp30 * tmp29;
    const auto tmp32 = 2 * tmp24;
    const auto tmp33 = tmp32 * tmp24;
    const auto tmp34 = -1 * tmp33;
    typename CoefficientFunctionSpaceType< 0 >::HessianRangeType tmp35 = hessianCoefficient< 0 >( x );
    const auto tmp36 = tmp1[ 1 ] * ((tmp35[ 1 ])[ 0 ])[ 0 ];
    const auto tmp37 = (tmp18[ 1 ])[ 0 ] * (tmp18[ 1 ])[ 0 ];
    const auto tmp38 = tmp37 + tmp36;
    const auto tmp39 = tmp38 + tmp38;
    const auto tmp40 = tmp1[ 0 ] * ((tmp35[ 0 ])[ 0 ])[ 0 ];
    const auto tmp41 = (tmp18[ 0 ])[ 0 ] * (tmp18[ 0 ])[ 0 ];
    const auto tmp42 = tmp41 + tmp40;
    const auto tmp43 = tmp42 + tmp42;
    const auto tmp44 = tmp43 + tmp39;
    const auto tmp45 = tmp44 + tmp34;
    const auto tmp46 = tmp45 / tmp17;
    const auto tmp47 = 3 * tmp46;
    const auto tmp48 = tmp47 / tmp0;
    const auto tmp49 = tmp48 * tmp16;
    const auto tmp50 = std::sinh( tmp9 );
    const auto tmp51 = tmp26 * tmp50;
    const auto tmp52 = 2.0 * tmp51;
    const auto tmp53 = std::sinh( tmp10 );
    const auto tmp54 = 2.0 * tmp26;
    const auto tmp55 = tmp54 * tmp53;
    const auto tmp56 = tmp55 * tmp15;
    const auto tmp57 = -1 * tmp56;
    const auto tmp58 = tmp57 + tmp52;
    const auto tmp59 = tmp58 / tmp12;
    const auto tmp60 = 2 * tmp59;
    const auto tmp61 = tmp60 * tmp15;
    const auto tmp62 = tmp61 * tmp26;
    const auto tmp63 = tmp62 + tmp49;
    const auto tmp64 = -1 * tmp63;
    const auto tmp65 = 0.5 * tmp64;
    const auto tmp66 = -1 * tmp65;
    const auto tmp67 = std::tanh( tmp9 );
    const auto tmp68 = -1 * tmp67;
    const auto tmp69 = 1 + tmp68;
    const auto tmp70 = 0.5 * tmp69;
    const auto tmp71 = tmp70 * tmp66;
    const auto tmp72 = tmp71 + tmp31;
    const auto tmp73 = -1 * tmp70;
    const auto tmp74 = 1 + tmp73;
    const auto tmp75 = tmp74 * tmp65;
    const auto tmp76 = tmp75 + tmp31;
    const auto tmp77 = tmp76 + tmp72;
    const auto tmp78 = tmp1[ 1 ] * (tmp18[ 1 ])[ 1 ];
    const auto tmp79 = tmp78 + tmp78;
    const auto tmp80 = tmp1[ 0 ] * (tmp18[ 0 ])[ 1 ];
    const auto tmp81 = tmp80 + tmp80;
    const auto tmp82 = tmp81 + tmp79;
    const auto tmp83 = tmp82 / tmp17;
    const auto tmp84 = 3 * tmp83;
    const auto tmp85 = tmp84 / tmp0;
    const auto tmp86 = tmp85 * tmp16;
    const auto tmp87 = -1 * tmp86;
    const auto tmp88 = 0.5 * tmp87;
    const auto tmp89 = tmp30 * tmp88;
    const auto tmp90 = 2 * tmp83;
    const auto tmp91 = tmp90 * tmp24;
    const auto tmp92 = -1 * tmp91;
    const auto tmp93 = (tmp18[ 1 ])[ 0 ] * (tmp18[ 1 ])[ 1 ];
    const auto tmp94 = tmp1[ 1 ] * ((tmp35[ 1 ])[ 0 ])[ 1 ];
    const auto tmp95 = tmp94 + tmp93;
    const auto tmp96 = tmp95 + tmp95;
    const auto tmp97 = (tmp18[ 0 ])[ 0 ] * (tmp18[ 0 ])[ 1 ];
    const auto tmp98 = tmp1[ 0 ] * ((tmp35[ 0 ])[ 0 ])[ 1 ];
    const auto tmp99 = tmp98 + tmp97;
    const auto tmp100 = tmp99 + tmp99;
    const auto tmp101 = tmp100 + tmp96;
    const auto tmp102 = tmp101 + tmp92;
    const auto tmp103 = tmp102 / tmp17;
    const auto tmp104 = 3 * tmp103;
    const auto tmp105 = tmp104 / tmp0;
    const auto tmp106 = tmp105 * tmp16;
    const auto tmp107 = tmp85 * tmp50;
    const auto tmp108 = 2.0 * tmp107;
    const auto tmp109 = 2.0 * tmp85;
    const auto tmp110 = tmp109 * tmp53;
    const auto tmp111 = tmp110 * tmp15;
    const auto tmp112 = -1 * tmp111;
    const auto tmp113 = tmp112 + tmp108;
    const auto tmp114 = tmp113 / tmp12;
    const auto tmp115 = 2 * tmp114;
    const auto tmp116 = tmp115 * tmp15;
    const auto tmp117 = tmp116 * tmp26;
    const auto tmp118 = tmp117 + tmp106;
    const auto tmp119 = -1 * tmp118;
    const auto tmp120 = 0.5 * tmp119;
    const auto tmp121 = -1 * tmp120;
    const auto tmp122 = tmp70 * tmp121;
    const auto tmp123 = tmp122 + tmp89;
    const auto tmp124 = -1 * tmp88;
    const auto tmp125 = tmp124 * tmp29;
    const auto tmp126 = tmp74 * tmp120;
    const auto tmp127 = tmp126 + tmp125;
    const auto tmp128 = tmp127 + tmp123;
    const auto tmp129 = tmp32 * tmp83;
    const auto tmp130 = -1 * tmp129;
    const auto tmp131 = tmp1[ 1 ] * ((tmp35[ 1 ])[ 1 ])[ 0 ];
    const auto tmp132 = tmp93 + tmp131;
    const auto tmp133 = tmp132 + tmp132;
    const auto tmp134 = tmp1[ 0 ] * ((tmp35[ 0 ])[ 1 ])[ 0 ];
    const auto tmp135 = tmp97 + tmp134;
    const auto tmp136 = tmp135 + tmp135;
    const auto tmp137 = tmp136 + tmp133;
    const auto tmp138 = tmp137 + tmp130;
    const auto tmp139 = tmp138 / tmp17;
    const auto tmp140 = 3 * tmp139;
    const auto tmp141 = tmp140 / tmp0;
    const auto tmp142 = tmp141 * tmp16;
    const auto tmp143 = tmp61 * tmp85;
    const auto tmp144 = tmp143 + tmp142;
    const auto tmp145 = -1 * tmp144;
    const auto tmp146 = 0.5 * tmp145;
    const auto tmp147 = tmp74 * tmp146;
    const auto tmp148 = tmp147 + tmp89;
    const auto tmp149 = -1 * tmp146;
    const auto tmp150 = tmp70 * tmp149;
    const auto tmp151 = tmp150 + tmp125;
    const auto tmp152 = tmp151 + tmp148;
    const auto tmp153 = tmp124 * tmp88;
    const auto tmp154 = tmp90 * tmp83;
    const auto tmp155 = -1 * tmp154;
    const auto tmp156 = tmp1[ 1 ] * ((tmp35[ 1 ])[ 1 ])[ 1 ];
    const auto tmp157 = (tmp18[ 1 ])[ 1 ] * (tmp18[ 1 ])[ 1 ];
    const auto tmp158 = tmp157 + tmp156;
    const auto tmp159 = tmp158 + tmp158;
    const auto tmp160 = tmp1[ 0 ] * ((tmp35[ 0 ])[ 1 ])[ 1 ];
    const auto tmp161 = (tmp18[ 0 ])[ 1 ] * (tmp18[ 0 ])[ 1 ];
    const auto tmp162 = tmp161 + tmp160;
    const auto tmp163 = tmp162 + tmp162;
    const auto tmp164 = tmp163 + tmp159;
    const auto tmp165 = tmp164 + tmp155;
    const auto tmp166 = tmp165 / tmp17;
    const auto tmp167 = 3 * tmp166;
    const auto tmp168 = tmp167 / tmp0;
    const auto tmp169 = tmp168 * tmp16;
    const auto tmp170 = tmp116 * tmp85;
    const auto tmp171 = tmp170 + tmp169;
    const auto tmp172 = -1 * tmp171;
    const auto tmp173 = 0.5 * tmp172;
    const auto tmp174 = -1 * tmp173;
    const auto tmp175 = tmp70 * tmp174;
    const auto tmp176 = tmp175 + tmp153;
    const auto tmp177 = tmp74 * tmp173;
    const auto tmp178 = tmp177 + tmp153;
    const auto tmp179 = tmp178 + tmp176;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp77;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp128;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp152;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp179;
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

} // namespace UFLLocalFunctions_b20910b6c8d57cb5e6a7ff4b89b91618

PYBIND11_MODULE( localfunction_b20910b6c8d57cb5e6a7ff4b89b91618_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef UFLLocalFunctions_b20910b6c8d57cb5e6a7ff4b89b91618::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_b20910b6c8d57cb5e6a7ff4b89b91618::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_b20910b6c8d57cb5e6a7ff4b89b91618_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order, const Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > &coeffbndproj ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>(gridView),name,order, coeffbndproj); } ), pybind11::keep_alive< 1, 2 >(), pybind11::keep_alive< 1, 3 >() );
      cls.def_property( "epsilon", [] ( LocalFunctionType &self ) -> UFLLocalFunctions_b20910b6c8d57cb5e6a7ff4b89b91618::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > >::Conepsilon { return self.conepsilon(); }, [] ( LocalFunctionType &self, const UFLLocalFunctions_b20910b6c8d57cb5e6a7ff4b89b91618::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > >::Conepsilon &v ) { self.conepsilon() = v; } );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
