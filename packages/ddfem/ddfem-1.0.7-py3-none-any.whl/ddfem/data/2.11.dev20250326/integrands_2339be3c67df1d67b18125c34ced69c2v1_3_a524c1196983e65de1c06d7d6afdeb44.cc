#ifndef GuardIntegrands_2339be3c67df1d67b18125c34ced69c2v1_3
#define GuardIntegrands_2339be3c67df1d67b18125c34ced69c2v1_3
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
#include <tuple>
#include <dune/python/pybind11/pybind11.h>
#include <dune/python/pybind11/extensions.h>
#include <dune/fempy/py/grid/gridpart.hh>
#include <dune/fempy/geometry/edgelength.hh>
#include <dune/fempy/py/integrands.hh>

namespace Integrands_2339be3c67df1d67b18125c34ced69c2v1_3
{




  // Integrands
  // ----------

  template< class GridPart >
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
    typedef std::tuple<> ConstantTupleType;
    typedef std::tuple<> CoefficientTupleType;
    static constexpr bool gridPartValid = true;
    template< std::size_t i >
    using CoefficientType = std::tuple_element_t< i, CoefficientTupleType >;
    template< std::size_t i >
    using ConstantType = typename std::tuple_element_t< i, ConstantTupleType >::element_type;

    Integrands ( const Dune::Fem::ParameterReader &parameter = Dune::Fem::Parameter::container() )
    {}

    bool init ( const EntityType &entity )
    {
      entity_ = entity;
      geometry_.emplace( this->entity().geometry() );
      return true;
    }

    void unbind ()
    {}

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
      const auto tmp0 = std::get< 0 >( u );
      const auto tmp1 = 0.01 * tmp0[ 0 ];
      const auto tmp2 = -1 * tmp1;
      GlobalCoordinateType tmp3 = geometry().global( Dune::Fem::coordinate( x ) );
      const auto tmp4 = tmp3[ 1 ] * tmp3[ 1 ];
      const auto tmp5 = tmp3[ 0 ] * tmp3[ 0 ];
      const auto tmp6 = tmp5 + tmp4;
      const auto tmp7 = -1 * tmp6;
      const auto tmp8 = 1 + tmp7;
      const auto tmp9 = 0.1 * tmp8;
      const auto tmp10 = tmp9 + tmp2;
      const auto tmp11 = -1 * tmp10;
      const auto tmp12 = 3 * tmp3[ 1 ];
      const auto tmp13 = tmp0[ 0 ] * tmp12;
      const auto tmp14 = -1 * tmp13;
      const auto tmp15 = 0.05 * tmp6;
      const auto tmp16 = -1 * tmp15;
      const auto tmp17 = 0.1 + tmp16;
      const auto tmp18 = std::get< 1 >( u );
      const auto tmp19 = (tmp18[ 0 ])[ 0 ] * tmp17;
      const auto tmp20 = tmp19 + tmp14;
      const auto tmp21 = -1 * tmp3[ 0 ];
      const auto tmp22 = 3 * tmp21;
      const auto tmp23 = tmp0[ 0 ] * tmp22;
      const auto tmp24 = -1 * tmp23;
      const auto tmp25 = (tmp18[ 0 ])[ 1 ] * tmp17;
      const auto tmp26 = tmp25 + tmp24;
      return RangeValueType{ { tmp11 }, { { tmp20, tmp26 } } };
    }

    template< class Point >
    auto linearizedInterior ( const Point &x, const DomainValueType &u ) const
    {
      GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
      const auto tmp1 = 3 * tmp0[ 1 ];
      const auto tmp2 = -1 * tmp1;
      const auto tmp3 = -1 * tmp0[ 0 ];
      const auto tmp4 = 3 * tmp3;
      const auto tmp5 = -1 * tmp4;
      const auto tmp6 = tmp0[ 1 ] * tmp0[ 1 ];
      const auto tmp7 = tmp0[ 0 ] * tmp0[ 0 ];
      const auto tmp8 = tmp7 + tmp6;
      const auto tmp9 = 0.05 * tmp8;
      const auto tmp10 = -1 * tmp9;
      const auto tmp11 = 0.1 + tmp10;
      return [ tmp11, tmp2, tmp5 ] ( const DomainValueType &phi ) {
          return RangeValueType{ { 0.01 * (std::get< 0 >( phi ))[ 0 ] }, { { tmp2 * (std::get< 0 >( phi ))[ 0 ] + tmp11 * ((std::get< 1 >( phi ))[ 0 ])[ 0 ], tmp5 * (std::get< 0 >( phi ))[ 0 ] + tmp11 * ((std::get< 1 >( phi ))[ 0 ])[ 1 ] } } };
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
          {
            std::fill( dirichletComponent.begin(), dirichletComponent.end(), 1 );
            return true;
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
      default:
        {
          using std::sin;
          auto tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
          const auto tmp1 = 3.141592653589793 * tmp0[ 1 ];
          const auto tmp2 = std::sin( tmp1 );
          const auto tmp3 = 3.141592653589793 * tmp0[ 0 ];
          const auto tmp4 = std::sin( tmp3 );
          const auto tmp5 = tmp4 * tmp2;
          result[ 0 ] = tmp5;
        }
      }
    }

    template< class Point >
    void dDirichlet ( int bndId, const Point &x, RJacobianRangeType &result ) const
    {
      switch( bndId )
      {
      default:
        {
          using std::cos;
          using std::sin;
          auto tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
          const auto tmp1 = 3.141592653589793 * tmp0[ 1 ];
          const auto tmp2 = std::sin( tmp1 );
          const auto tmp3 = 3.141592653589793 * tmp0[ 0 ];
          const auto tmp4 = std::cos( tmp3 );
          const auto tmp5 = 3.141592653589793 * tmp4;
          const auto tmp6 = tmp5 * tmp2;
          const auto tmp7 = std::sin( tmp3 );
          const auto tmp8 = std::cos( tmp1 );
          const auto tmp9 = 3.141592653589793 * tmp8;
          const auto tmp10 = tmp9 * tmp7;
          (result[ 0 ])[ 0 ] = tmp6;
          (result[ 0 ])[ 1 ] = tmp10;
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

    const EntityType &entity () const
    {
      return entity_;
    }

    const Geometry &geometry () const
    {
      return *geometry_;
    }
    EntityType entity_;
    IntersectionType intersection_;
    std::optional< Geometry > geometry_;
    ConstantTupleType constants_;
    std::tuple<  > coefficients_;
  };

} // namespace Integrands_2339be3c67df1d67b18125c34ced69c2v1_3

PYBIND11_MODULE( integrands_2339be3c67df1d67b18125c34ced69c2v1_3_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > GridPart;
  typedef Integrands_2339be3c67df1d67b18125c34ced69c2v1_3::Integrands< GridPart > Integrands;
  if constexpr( Integrands::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<Integrands>(module,"Integrands",Dune::Python::GenerateTypeName("Integrands_2339be3c67df1d67b18125c34ced69c2v1_3::Integrands< GridPart >"), Dune::Python::IncludeFiles({"python/dune/generated/integrands_2339be3c67df1d67b18125c34ced69c2v1_3_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerIntegrands< Integrands >( module, cls );
      cls.def( pybind11::init( [] () { return new Integrands(); } ) );
      cls.def_property_readonly( "virtualized", [] ( Integrands& ) -> bool { return true;});
      cls.def_property_readonly( "hasDirichletBoundary", [] ( Integrands& ) -> bool { return true;});
  }
}
#endif // GuardIntegrands_2339be3c67df1d67b18125c34ced69c2v1_3
