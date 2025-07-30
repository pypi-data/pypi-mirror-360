#ifndef GUARD_1d13146d4bff10e178aba773fe2a9f1d
#define GUARD_1d13146d4bff10e178aba773fe2a9f1d

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

namespace UFLLocalFunctions_1d13146d4bff10e178aba773fe2a9f1d
{

  // UFLLocalFunction
// ----------------

template< class GridPart, class Coeffddm >
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
  typedef std::tuple< Dune::Fem::GridFunctionSpace< GridPartType, Dune::FieldVector< double, 1 > > > CoefficientFunctionSpaceTupleType;
  typedef std::tuple< Coeffddm > CoefficientTupleType;
  template< std::size_t i >
  using CoefficientFunctionSpaceType = std::tuple_element_t< i, CoefficientFunctionSpaceTupleType >;
  template< std::size_t i >
  using CoefficientRangeType = typename CoefficientFunctionSpaceType< i >::RangeType;
  template< std::size_t i >
  using CoefficientJacobianRangeType = typename CoefficientFunctionSpaceType< i >::JacobianRangeType;
  static constexpr bool gridPartValid = Dune::Fem::checkGridPartValid<GridPartType,Dune::Fem::ConstLocalFunction<Coeffddm>>();
  template< std::size_t i >
  using CoefficientType = std::tuple_element_t< i, CoefficientTupleType >;
  template< std::size_t i >
  using ConstantType = typename std::tuple_element_t< i, ConstantTupleType >::element_type;
  using BaseType::entity;
  using BaseType::geometry;

  UFLLocalFunction ( const GridPartType &gridPart, const std::string &name, int order, const Coeffddm &coeffddm, const Dune::Fem::ParameterReader &parameter = Dune::Fem::Parameter::container() )
    : BaseType(gridPart,name,order),
      coefficients_( Dune::Fem::ConstLocalFunction< Coeffddm >( coeffddm ) )
  {}

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
    typename CoefficientFunctionSpaceType< 0 >::JacobianRangeType tmp39 = jacobianCoefficient< 0 >( x );
    const auto tmp40 = (tmp39[ 0 ])[ 1 ] * (tmp39[ 0 ])[ 1 ];
    const auto tmp41 = (tmp39[ 0 ])[ 0 ] * (tmp39[ 0 ])[ 0 ];
    const auto tmp42 = tmp41 + tmp40;
    const auto tmp43 = tmp42 * (tmp38 <= 0.0 ? 1 : 0.0);
    result[ 0 ] = tmp43;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::max;
    using std::min;
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
    typename CoefficientFunctionSpaceType< 0 >::HessianRangeType tmp39 = hessianCoefficient< 0 >( x );
    typename CoefficientFunctionSpaceType< 0 >::JacobianRangeType tmp40 = jacobianCoefficient< 0 >( x );
    const auto tmp41 = (tmp40[ 0 ])[ 1 ] * ((tmp39[ 0 ])[ 1 ])[ 0 ];
    const auto tmp42 = ((tmp39[ 0 ])[ 1 ])[ 0 ] * (tmp40[ 0 ])[ 1 ];
    const auto tmp43 = tmp42 + tmp41;
    const auto tmp44 = (tmp40[ 0 ])[ 0 ] * ((tmp39[ 0 ])[ 0 ])[ 0 ];
    const auto tmp45 = ((tmp39[ 0 ])[ 0 ])[ 0 ] * (tmp40[ 0 ])[ 0 ];
    const auto tmp46 = tmp45 + tmp44;
    const auto tmp47 = tmp46 + tmp43;
    const auto tmp48 = tmp47 * (tmp38 <= 0.0 ? 1 : 0.0);
    const auto tmp49 = (tmp40[ 0 ])[ 1 ] * ((tmp39[ 0 ])[ 1 ])[ 1 ];
    const auto tmp50 = ((tmp39[ 0 ])[ 1 ])[ 1 ] * (tmp40[ 0 ])[ 1 ];
    const auto tmp51 = tmp50 + tmp49;
    const auto tmp52 = (tmp40[ 0 ])[ 0 ] * ((tmp39[ 0 ])[ 0 ])[ 1 ];
    const auto tmp53 = ((tmp39[ 0 ])[ 0 ])[ 1 ] * (tmp40[ 0 ])[ 0 ];
    const auto tmp54 = tmp53 + tmp52;
    const auto tmp55 = tmp54 + tmp51;
    const auto tmp56 = tmp55 * (tmp38 <= 0.0 ? 1 : 0.0);
    (result[ 0 ])[ 0 ] = tmp48;
    (result[ 0 ])[ 1 ] = tmp56;
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
  std::tuple< Dune::Fem::ConstLocalFunction< Coeffddm > > coefficients_;
};

} // namespace UFLLocalFunctions_1d13146d4bff10e178aba773fe2a9f1d

PYBIND11_MODULE( localfunction_1d13146d4bff10e178aba773fe2a9f1d_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef UFLLocalFunctions_1d13146d4bff10e178aba773fe2a9f1d::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_1d13146d4bff10e178aba773fe2a9f1d::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_1d13146d4bff10e178aba773fe2a9f1d_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order, const Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > > &coeffddm ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>(gridView),name,order, coeffddm); } ), pybind11::keep_alive< 1, 2 >(), pybind11::keep_alive< 1, 3 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
