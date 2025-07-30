#ifndef GuardIntegrands_5d65834d43b1dbae0ceafbcc9ec60542v1_3
#define GuardIntegrands_5d65834d43b1dbae0ceafbcc9ec60542v1_3
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
#include <cmath>
#include <tuple>
#include <dune/python/pybind11/pybind11.h>
#include <dune/python/pybind11/extensions.h>
#include <dune/fempy/py/grid/gridpart.hh>
#include <dune/fempy/geometry/edgelength.hh>
#include <dune/fempy/function/virtualizedgridfunction.hh>
#include <dune/fempy/function/simplegridfunction.hh>
#include <dune/fem/misc/gridfunctionview.hh>
#include <dune/fempy/py/integrands.hh>

namespace Integrands_5d65834d43b1dbae0ceafbcc9ec60542v1_3
{




  // Integrands
  // ----------

  template< class GridPart, class Coeffextproj, class Coeffbndproj, class Coeffsdfprojfull, class Coeffphidomain, class CoeffsdfprojfullA >
  struct Integrands
  {
    typedef GridPart GridPartType;
    typedef typename GridPartType::GridViewType GridView;
    typedef typename GridView::ctype ctype;
    typedef typename GridPartType::template Codim< 0 >::EntityType EntityType;
    typedef typename GridPartType::IntersectionType IntersectionType;
    typedef typename EntityType::Geometry Geometry;
    typedef typename Geometry::GlobalCoordinate GlobalCoordinateType;
    typedef Dune::Fem::IntersectionSide Side;
    typedef double Conepsilon;
    typedef std::tuple< std::shared_ptr< Conepsilon > > ConstantTupleType;
    template< std::size_t i >
    using ConstantsRangeType = typename std::tuple_element_t< i, ConstantTupleType >::element_type;
    typedef std::tuple< Dune::Fem::GridFunctionSpace< GridPartType, Dune::FieldVector< double, 2 > >, Dune::Fem::GridFunctionSpace< GridPartType, Dune::FieldVector< double, 2 > >, Dune::Fem::GridFunctionSpace< GridPartType, Dune::FieldVector< double, 1 > >, Dune::Fem::GridFunctionSpace< GridPartType, Dune::FieldVector< double, 1 > >, Dune::Fem::GridFunctionSpace< GridPartType, Dune::FieldVector< double, 1 > > > CoefficientFunctionSpaceTupleType;
    typedef std::tuple< Coeffextproj, Coeffbndproj, Coeffsdfprojfull, Coeffphidomain, CoeffsdfprojfullA > CoefficientTupleType;
    template< std::size_t i >
    using CoefficientFunctionSpaceType = std::tuple_element_t< i, CoefficientFunctionSpaceTupleType >;
    template< std::size_t i >
    using CoefficientRangeType = typename CoefficientFunctionSpaceType< i >::RangeType;
    template< std::size_t i >
    using CoefficientJacobianRangeType = typename CoefficientFunctionSpaceType< i >::JacobianRangeType;
    static constexpr bool gridPartValid = Dune::Fem::checkGridPartValid<GridPartType,Dune::Fem::ConstLocalFunction<Coeffextproj>>() && Dune::Fem::checkGridPartValid<GridPartType,Dune::Fem::ConstLocalFunction<Coeffbndproj>>() && Dune::Fem::checkGridPartValid<GridPartType,Dune::Fem::ConstLocalFunction<Coeffsdfprojfull>>() && Dune::Fem::checkGridPartValid<GridPartType,Dune::Fem::ConstLocalFunction<Coeffphidomain>>() && Dune::Fem::checkGridPartValid<GridPartType,Dune::Fem::ConstLocalFunction<CoeffsdfprojfullA>>();
    template< std::size_t i >
    using CoefficientType = std::tuple_element_t< i, CoefficientTupleType >;
    template< std::size_t i >
    using ConstantType = typename std::tuple_element_t< i, ConstantTupleType >::element_type;

    Integrands ( const Coeffextproj &coeffextproj, const Coeffbndproj &coeffbndproj, const Coeffsdfprojfull &coeffsdfprojfull, const Coeffphidomain &coeffphidomain, const CoeffsdfprojfullA &coeffsdfprojfullA, const Dune::Fem::ParameterReader &parameter = Dune::Fem::Parameter::container() )
      : coefficients_( Dune::Fem::ConstLocalFunction< Coeffextproj >( coeffextproj ), Dune::Fem::ConstLocalFunction< Coeffbndproj >( coeffbndproj ), Dune::Fem::ConstLocalFunction< Coeffsdfprojfull >( coeffsdfprojfull ), Dune::Fem::ConstLocalFunction< Coeffphidomain >( coeffphidomain ), Dune::Fem::ConstLocalFunction< CoeffsdfprojfullA >( coeffsdfprojfullA ) )
    {
      std::get< 0 >( constants_ ) = std::make_shared< Conepsilon >( (Conepsilon(0)) );
    }

    bool init ( const EntityType &entity )
    {
      entity_ = entity;
      std::get< 0 >( coefficients_ ).bind( this->entity() );
      std::get< 1 >( coefficients_ ).bind( this->entity() );
      std::get< 2 >( coefficients_ ).bind( this->entity() );
      std::get< 3 >( coefficients_ ).bind( this->entity() );
      std::get< 4 >( coefficients_ ).bind( this->entity() );
      return true;
    }

    void unbind ()
    {
      std::get< 0 >( coefficients_ ).unbind();
      std::get< 1 >( coefficients_ ).unbind();
      std::get< 2 >( coefficients_ ).unbind();
      std::get< 3 >( coefficients_ ).unbind();
      std::get< 4 >( coefficients_ ).unbind();
    }

    bool init ( const IntersectionType &intersection )
    {
      intersection_ = intersection;
      return (intersection.boundary() && init( intersection.inside() ));
    }
    typedef std::tuple< Dune::FieldVector< double, 1 >, Dune::FieldMatrix< double, 1, 2 > > DomainValueType;
    typedef std::tuple< Dune::FieldVector< double, 1 >, Dune::FieldMatrix< double, 1, 2 > > RangeValueType;
    static constexpr bool _nonlinear = false;

    bool nonlinear () const
    {
      return _nonlinear;
    }

    template< class Point >
    RangeValueType interior ( const Point &x, const DomainValueType &u ) const
    {
      using std::pow;
      using std::sin;
      double tmp0 = constant< 0 >();
      const auto tmp1 = std::pow( tmp0, 3 );
      typename CoefficientFunctionSpaceType< 4 >::RangeType tmp2 = evaluateCoefficient< 4 >( x );
      const auto tmp3 = 1e-10 + tmp2[ 0 ];
      typename CoefficientFunctionSpaceType< 1 >::RangeType tmp4 = evaluateCoefficient< 1 >( x );
      const auto tmp5 = 3.141592653589793 * tmp4[ 1 ];
      const auto tmp6 = std::sin( tmp5 );
      const auto tmp7 = 3.141592653589793 * tmp4[ 0 ];
      const auto tmp8 = std::sin( tmp7 );
      const auto tmp9 = tmp8 * tmp6;
      const auto tmp10 = -1 * tmp9;
      const auto tmp11 = std::get< 0 >( u );
      const auto tmp12 = tmp11[ 0 ] + tmp10;
      const auto tmp13 = tmp2[ 0 ] * tmp12;
      const auto tmp14 = tmp13 / tmp3;
      typename CoefficientFunctionSpaceType< 3 >::RangeType tmp15 = evaluateCoefficient< 3 >( x );
      const auto tmp16 = -1 * tmp15[ 0 ];
      const auto tmp17 = 1 + tmp16;
      const auto tmp18 = tmp17 * tmp14;
      const auto tmp19 = tmp18 / tmp1;
      const auto tmp20 = -1 * tmp19;
      const auto tmp21 = 3 * tmp20;
      const auto tmp22 = -1 * tmp21;
      const auto tmp23 = 0.1 * tmp20;
      const auto tmp24 = 0.01 * tmp11[ 0 ];
      const auto tmp25 = -1 * tmp24;
      typename CoefficientFunctionSpaceType< 0 >::RangeType tmp26 = evaluateCoefficient< 0 >( x );
      const auto tmp27 = tmp26[ 1 ] * tmp26[ 1 ];
      const auto tmp28 = tmp26[ 0 ] * tmp26[ 0 ];
      const auto tmp29 = tmp28 + tmp27;
      const auto tmp30 = -1 * tmp29;
      const auto tmp31 = 1 + tmp30;
      const auto tmp32 = 0.1 * tmp31;
      const auto tmp33 = tmp32 + tmp25;
      const auto tmp34 = tmp15[ 0 ] * tmp33;
      const auto tmp35 = tmp34 + tmp23;
      const auto tmp36 = -1 * tmp35;
      const auto tmp37 = tmp36 + tmp22;
      const auto tmp38 = 3 * tmp26[ 1 ];
      const auto tmp39 = tmp11[ 0 ] * tmp38;
      const auto tmp40 = tmp15[ 0 ] * tmp39;
      const auto tmp41 = -1 * tmp40;
      const auto tmp42 = 0.05 * tmp29;
      const auto tmp43 = -1 * tmp42;
      const auto tmp44 = 0.1 + tmp43;
      const auto tmp45 = std::get< 1 >( u );
      const auto tmp46 = (tmp45[ 0 ])[ 0 ] * tmp44;
      const auto tmp47 = tmp15[ 0 ] * tmp46;
      const auto tmp48 = tmp47 + tmp41;
      const auto tmp49 = -1 * tmp26[ 0 ];
      const auto tmp50 = 3 * tmp49;
      const auto tmp51 = tmp11[ 0 ] * tmp50;
      const auto tmp52 = tmp15[ 0 ] * tmp51;
      const auto tmp53 = -1 * tmp52;
      const auto tmp54 = (tmp45[ 0 ])[ 1 ] * tmp44;
      const auto tmp55 = tmp15[ 0 ] * tmp54;
      const auto tmp56 = tmp55 + tmp53;
      return RangeValueType{ { tmp37 }, { { tmp48, tmp56 } } };
    }

    template< class Point >
    auto linearizedInterior ( const Point &x, const DomainValueType &u ) const
    {
      using std::pow;
      double tmp0 = constant< 0 >();
      const auto tmp1 = std::pow( tmp0, 3 );
      typename CoefficientFunctionSpaceType< 4 >::RangeType tmp2 = evaluateCoefficient< 4 >( x );
      const auto tmp3 = 1e-10 + tmp2[ 0 ];
      const auto tmp4 = tmp2[ 0 ] / tmp3;
      typename CoefficientFunctionSpaceType< 3 >::RangeType tmp5 = evaluateCoefficient< 3 >( x );
      const auto tmp6 = -1 * tmp5[ 0 ];
      const auto tmp7 = 1 + tmp6;
      const auto tmp8 = tmp7 * tmp4;
      const auto tmp9 = tmp8 / tmp1;
      const auto tmp10 = -1 * tmp9;
      const auto tmp11 = 3 * tmp10;
      const auto tmp12 = -1 * tmp11;
      const auto tmp13 = 0.1 * tmp10;
      const auto tmp14 = -0.01 * tmp5[ 0 ];
      const auto tmp15 = tmp14 + tmp13;
      const auto tmp16 = -1 * tmp15;
      const auto tmp17 = tmp16 + tmp12;
      typename CoefficientFunctionSpaceType< 0 >::RangeType tmp18 = evaluateCoefficient< 0 >( x );
      const auto tmp19 = 3 * tmp18[ 1 ];
      const auto tmp20 = tmp5[ 0 ] * tmp19;
      const auto tmp21 = -1 * tmp20;
      const auto tmp22 = -1 * tmp18[ 0 ];
      const auto tmp23 = 3 * tmp22;
      const auto tmp24 = tmp5[ 0 ] * tmp23;
      const auto tmp25 = -1 * tmp24;
      const auto tmp26 = tmp18[ 1 ] * tmp18[ 1 ];
      const auto tmp27 = tmp18[ 0 ] * tmp18[ 0 ];
      const auto tmp28 = tmp27 + tmp26;
      const auto tmp29 = 0.05 * tmp28;
      const auto tmp30 = -1 * tmp29;
      const auto tmp31 = 0.1 + tmp30;
      const auto tmp32 = tmp5[ 0 ] * tmp31;
      return [ tmp17, tmp21, tmp25, tmp32 ] ( const DomainValueType &phi ) {
          return RangeValueType{ { tmp17 * (std::get< 0 >( phi ))[ 0 ] }, { { tmp21 * (std::get< 0 >( phi ))[ 0 ] + tmp32 * ((std::get< 1 >( phi ))[ 0 ])[ 0 ], tmp25 * (std::get< 0 >( phi ))[ 0 ] + tmp32 * ((std::get< 1 >( phi ))[ 0 ])[ 1 ] } } };
        };
    }
    typedef Dune::FieldVector< double, 1 >  RRangeType;
    typedef Dune::FieldMatrix< double, 1, GridPartType::dimension >  RJacobianRangeType;
    typedef Dune::Fem::BoundaryIdProvider< typename GridPartType::GridType > BoundaryIdProviderType;
    typedef std::array<int,1> DirichletComponentType;

    bool hasDirichletBoundary () const
    {
      return true;
    }

    bool isDirichletIntersection ( const IntersectionType &intersection, DirichletComponentType &dirichletComponent ) const
    {
      const int bndId = BoundaryIdProviderType::boundaryId( intersection );
      {
        std::fill( dirichletComponent.begin(), dirichletComponent.end(), bndId );
      }
      switch( bndId )
      {
      default:
        {
          int domainId;
          {
              using std::max;
              using std::min;
              using std::sqrt;
              auto tmp0 = intersection.geometry().center( );
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
              domainId = (tmp38 <= 0.0 ? 1 : 0.0) < 0.5;
              if (domainId)
              {
                std::fill( dirichletComponent.begin(), dirichletComponent.end(), 2 );
                return true;
              }
          }
          return false;
        }
      }
    }

    template< class Point >
    void dirichlet ( int bndId, const Point &x, RRangeType &result ) const
    {
      switch( bndId )
      {
      case 2:
        {
          using std::sin;
          typename CoefficientFunctionSpaceType< 2 >::RangeType tmp0 = evaluateCoefficient< 2 >( x );
          const auto tmp1 = 1e-10 + tmp0[ 0 ];
          typename CoefficientFunctionSpaceType< 1 >::RangeType tmp2 = evaluateCoefficient< 1 >( x );
          const auto tmp3 = 3.141592653589793 * tmp2[ 1 ];
          const auto tmp4 = std::sin( tmp3 );
          const auto tmp5 = 3.141592653589793 * tmp2[ 0 ];
          const auto tmp6 = std::sin( tmp5 );
          const auto tmp7 = tmp6 * tmp4;
          const auto tmp8 = -1 * tmp7;
          const auto tmp9 = tmp0[ 0 ] * tmp8;
          const auto tmp10 = tmp9 / tmp1;
          const auto tmp11 = -1 * tmp10;
          result[ 0 ] = tmp11;
        }
        break;
      default:
        {
          result = RRangeType( 0 );
        }
      }
    }

    template< class Point >
    void dDirichlet ( int bndId, const Point &x, RJacobianRangeType &result ) const
    {
      switch( bndId )
      {
      case 2:
        {
          using std::cos;
          using std::sin;
          typename CoefficientFunctionSpaceType< 2 >::RangeType tmp0 = evaluateCoefficient< 2 >( x );
          const auto tmp1 = 1e-10 + tmp0[ 0 ];
          typename CoefficientFunctionSpaceType< 1 >::RangeType tmp2 = evaluateCoefficient< 1 >( x );
          const auto tmp3 = 3.141592653589793 * tmp2[ 1 ];
          const auto tmp4 = std::sin( tmp3 );
          const auto tmp5 = 3.141592653589793 * tmp2[ 0 ];
          const auto tmp6 = std::sin( tmp5 );
          const auto tmp7 = tmp6 * tmp4;
          const auto tmp8 = -1 * tmp7;
          const auto tmp9 = tmp0[ 0 ] * tmp8;
          const auto tmp10 = tmp9 / tmp1;
          typename CoefficientFunctionSpaceType< 2 >::JacobianRangeType tmp11 = jacobianCoefficient< 2 >( x );
          const auto tmp12 = (tmp11[ 0 ])[ 0 ] * tmp10;
          const auto tmp13 = -1 * tmp12;
          const auto tmp14 = (tmp11[ 0 ])[ 0 ] * tmp8;
          const auto tmp15 = std::cos( tmp5 );
          typename CoefficientFunctionSpaceType< 1 >::JacobianRangeType tmp16 = jacobianCoefficient< 1 >( x );
          const auto tmp17 = 3.141592653589793 * (tmp16[ 0 ])[ 0 ];
          const auto tmp18 = tmp17 * tmp15;
          const auto tmp19 = tmp18 * tmp4;
          const auto tmp20 = std::cos( tmp3 );
          const auto tmp21 = 3.141592653589793 * (tmp16[ 1 ])[ 0 ];
          const auto tmp22 = tmp21 * tmp20;
          const auto tmp23 = tmp22 * tmp6;
          const auto tmp24 = tmp23 + tmp19;
          const auto tmp25 = -1 * tmp24;
          const auto tmp26 = tmp0[ 0 ] * tmp25;
          const auto tmp27 = tmp26 + tmp14;
          const auto tmp28 = tmp27 + tmp13;
          const auto tmp29 = tmp28 / tmp1;
          const auto tmp30 = -1 * tmp29;
          const auto tmp31 = (tmp11[ 0 ])[ 1 ] * tmp10;
          const auto tmp32 = -1 * tmp31;
          const auto tmp33 = (tmp11[ 0 ])[ 1 ] * tmp8;
          const auto tmp34 = 3.141592653589793 * (tmp16[ 0 ])[ 1 ];
          const auto tmp35 = tmp34 * tmp15;
          const auto tmp36 = tmp35 * tmp4;
          const auto tmp37 = 3.141592653589793 * (tmp16[ 1 ])[ 1 ];
          const auto tmp38 = tmp37 * tmp20;
          const auto tmp39 = tmp38 * tmp6;
          const auto tmp40 = tmp39 + tmp36;
          const auto tmp41 = -1 * tmp40;
          const auto tmp42 = tmp0[ 0 ] * tmp41;
          const auto tmp43 = tmp42 + tmp33;
          const auto tmp44 = tmp43 + tmp32;
          const auto tmp45 = tmp44 / tmp1;
          const auto tmp46 = -1 * tmp45;
          (result[ 0 ])[ 0 ] = tmp30;
          (result[ 0 ])[ 1 ] = tmp46;
        }
        break;
      default:
        {
          result = RJacobianRangeType( 0 );
        }
      }
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

    const EntityType &entity () const
    {
      return entity_;
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
    EntityType entity_;
    IntersectionType intersection_;
    ConstantTupleType constants_;
    std::tuple< Dune::Fem::ConstLocalFunction< Coeffextproj >, Dune::Fem::ConstLocalFunction< Coeffbndproj >, Dune::Fem::ConstLocalFunction< Coeffsdfprojfull >, Dune::Fem::ConstLocalFunction< Coeffphidomain >, Dune::Fem::ConstLocalFunction< CoeffsdfprojfullA > > coefficients_;
  };

} // namespace Integrands_5d65834d43b1dbae0ceafbcc9ec60542v1_3

PYBIND11_MODULE( integrands_5d65834d43b1dbae0ceafbcc9ec60542v1_3_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > GridPart;
  typedef Integrands_5d65834d43b1dbae0ceafbcc9ec60542v1_3::Integrands< GridPart, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > > > Integrands;
  if constexpr( Integrands::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<Integrands>(module,"Integrands",Dune::Python::GenerateTypeName("Integrands_5d65834d43b1dbae0ceafbcc9ec60542v1_3::Integrands< GridPart, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > >, Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > > >"), Dune::Python::IncludeFiles({"python/dune/generated/integrands_5d65834d43b1dbae0ceafbcc9ec60542v1_3_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerIntegrands< Integrands >( module, cls );
      cls.def( pybind11::init( [] ( const Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > &coeffextproj, const Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 2 > > &coeffbndproj, const Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > > &coeffsdfprojfull, const Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > > &coeffphidomain, const Dune::FemPy::VirtualizedGridFunction< Dune::FemPy::GridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>, Dune::FieldVector< double, 1 > > &coeffsdfprojfullA ) { return new Integrands( coeffextproj, coeffbndproj, coeffsdfprojfull, coeffphidomain, coeffsdfprojfullA ); } ), pybind11::keep_alive< 1, 2 >(), pybind11::keep_alive< 1, 3 >(), pybind11::keep_alive< 1, 4 >(), pybind11::keep_alive< 1, 5 >(), pybind11::keep_alive< 1, 6 >() );
      cls.def_property( "epsilon", [] ( Integrands &self ) -> Integrands::Conepsilon { return self.conepsilon(); }, [] ( Integrands &self, const Integrands::Conepsilon &v ) { self.conepsilon() = v; } );
      cls.def_property_readonly( "virtualized", [] ( Integrands& ) -> bool { return true;});
      cls.def_property_readonly( "hasDirichletBoundary", [] ( Integrands& ) -> bool { return true;});
  }
}
#endif // GuardIntegrands_5d65834d43b1dbae0ceafbcc9ec60542v1_3
