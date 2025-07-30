#ifndef GuardIntegrands_3bde0abfafcf45a3cff4d1029568ab5cv1_3
#define GuardIntegrands_3bde0abfafcf45a3cff4d1029568ab5cv1_3
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
#include <dune/fempy/py/integrands.hh>

namespace Integrands_3bde0abfafcf45a3cff4d1029568ab5cv1_3
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
      using std::sin;
      using std::sqrt;
      using std::tanh;
      GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
      const auto tmp1 = tmp0[ 1 ] * tmp0[ 1 ];
      const auto tmp2 = tmp0[ 0 ] * tmp0[ 0 ];
      const auto tmp3 = tmp2 + tmp1;
      const auto tmp4 = std::sqrt( tmp3 );
      const auto tmp5 = 2 * tmp4;
      const auto tmp6 = tmp0[ 1 ] + tmp0[ 1 ];
      const auto tmp7 = tmp6 / tmp5;
      const auto tmp8 = -1 * tmp7;
      const auto tmp9 = -1 + tmp4;
      const auto tmp10 = tmp9 * tmp8;
      const auto tmp11 = tmp0[ 1 ] + tmp10;
      const auto tmp12 = 3.141592653589793 * tmp11;
      const auto tmp13 = std::sin( tmp12 );
      const auto tmp14 = tmp0[ 0 ] + tmp0[ 0 ];
      const auto tmp15 = tmp14 / tmp5;
      const auto tmp16 = -1 * tmp15;
      const auto tmp17 = tmp9 * tmp16;
      const auto tmp18 = tmp0[ 0 ] + tmp17;
      const auto tmp19 = 3.141592653589793 * tmp18;
      const auto tmp20 = std::sin( tmp19 );
      const auto tmp21 = tmp20 * tmp13;
      const auto tmp22 = -1 * tmp21;
      const auto tmp23 = std::get< 0 >( u );
      const auto tmp24 = tmp23[ 0 ] + tmp22;
      const auto tmp25 = -3.1 * tmp24;
      const auto tmp26 = 3 * tmp9;
      const auto tmp27 = tmp26 / 0.225;
      const auto tmp28 = std::tanh( tmp27 );
      const auto tmp29 = -1 * tmp28;
      const auto tmp30 = 1 + tmp29;
      const auto tmp31 = 0.5 * tmp30;
      const auto tmp32 = -1 * tmp31;
      const auto tmp33 = 1 + tmp32;
      const auto tmp34 = tmp33 * tmp25;
      const auto tmp35 = tmp34 / 0.011390625000000001;
      const auto tmp36 = 0.01 * tmp23[ 0 ];
      const auto tmp37 = -1 * tmp36;
      const auto tmp38 = -1 * (tmp9 <= 0.0 ? 1 : 0.0);
      const auto tmp39 = 1 + tmp38;
      const auto tmp40 = tmp39 * tmp10;
      const auto tmp41 = tmp0[ 1 ] + tmp40;
      const auto tmp42 = tmp41 * tmp41;
      const auto tmp43 = tmp39 * tmp17;
      const auto tmp44 = tmp0[ 0 ] + tmp43;
      const auto tmp45 = tmp44 * tmp44;
      const auto tmp46 = tmp45 + tmp42;
      const auto tmp47 = -1 * tmp46;
      const auto tmp48 = 1 + tmp47;
      const auto tmp49 = 0.1 * tmp48;
      const auto tmp50 = tmp49 + tmp37;
      const auto tmp51 = tmp50 * tmp31;
      const auto tmp52 = tmp51 + tmp35;
      const auto tmp53 = -1 * tmp52;
      const auto tmp54 = 3 * tmp41;
      const auto tmp55 = tmp23[ 0 ] * tmp54;
      const auto tmp56 = tmp31 * tmp55;
      const auto tmp57 = -1 * tmp56;
      const auto tmp58 = 0.05 * tmp46;
      const auto tmp59 = -1 * tmp58;
      const auto tmp60 = 0.1 + tmp59;
      const auto tmp61 = tmp60 * tmp31;
      const auto tmp62 = std::get< 1 >( u );
      const auto tmp63 = (tmp62[ 0 ])[ 0 ] * tmp61;
      const auto tmp64 = tmp63 + tmp57;
      const auto tmp65 = -1 * tmp44;
      const auto tmp66 = 3 * tmp65;
      const auto tmp67 = tmp23[ 0 ] * tmp66;
      const auto tmp68 = tmp31 * tmp67;
      const auto tmp69 = -1 * tmp68;
      const auto tmp70 = (tmp62[ 0 ])[ 1 ] * tmp61;
      const auto tmp71 = tmp70 + tmp69;
      return RangeValueType{ { tmp53 }, { { tmp64, tmp71 } } };
    }

    template< class Point >
    auto linearizedInterior ( const Point &x, const DomainValueType &u ) const
    {
      using std::sqrt;
      using std::tanh;
      GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
      const auto tmp1 = tmp0[ 1 ] * tmp0[ 1 ];
      const auto tmp2 = tmp0[ 0 ] * tmp0[ 0 ];
      const auto tmp3 = tmp2 + tmp1;
      const auto tmp4 = std::sqrt( tmp3 );
      const auto tmp5 = -1 + tmp4;
      const auto tmp6 = 3 * tmp5;
      const auto tmp7 = tmp6 / 0.225;
      const auto tmp8 = std::tanh( tmp7 );
      const auto tmp9 = -1 * tmp8;
      const auto tmp10 = 1 + tmp9;
      const auto tmp11 = 0.5 * tmp10;
      const auto tmp12 = -1 * tmp11;
      const auto tmp13 = 1 + tmp12;
      const auto tmp14 = -3.1 * tmp13;
      const auto tmp15 = tmp14 / 0.011390625000000001;
      const auto tmp16 = -0.01 * tmp11;
      const auto tmp17 = tmp16 + tmp15;
      const auto tmp18 = -1 * tmp17;
      const auto tmp19 = 2 * tmp4;
      const auto tmp20 = tmp0[ 1 ] + tmp0[ 1 ];
      const auto tmp21 = tmp20 / tmp19;
      const auto tmp22 = -1 * tmp21;
      const auto tmp23 = tmp5 * tmp22;
      const auto tmp24 = -1 * (tmp5 <= 0.0 ? 1 : 0.0);
      const auto tmp25 = 1 + tmp24;
      const auto tmp26 = tmp25 * tmp23;
      const auto tmp27 = tmp0[ 1 ] + tmp26;
      const auto tmp28 = 3 * tmp27;
      const auto tmp29 = tmp28 * tmp11;
      const auto tmp30 = -1 * tmp29;
      const auto tmp31 = tmp0[ 0 ] + tmp0[ 0 ];
      const auto tmp32 = tmp31 / tmp19;
      const auto tmp33 = -1 * tmp32;
      const auto tmp34 = tmp5 * tmp33;
      const auto tmp35 = tmp25 * tmp34;
      const auto tmp36 = tmp0[ 0 ] + tmp35;
      const auto tmp37 = -1 * tmp36;
      const auto tmp38 = 3 * tmp37;
      const auto tmp39 = tmp11 * tmp38;
      const auto tmp40 = -1 * tmp39;
      const auto tmp41 = tmp27 * tmp27;
      const auto tmp42 = tmp36 * tmp36;
      const auto tmp43 = tmp42 + tmp41;
      const auto tmp44 = 0.05 * tmp43;
      const auto tmp45 = -1 * tmp44;
      const auto tmp46 = 0.1 + tmp45;
      const auto tmp47 = tmp46 * tmp11;
      return [ tmp18, tmp30, tmp40, tmp47 ] ( const DomainValueType &phi ) {
          return RangeValueType{ { tmp18 * (std::get< 0 >( phi ))[ 0 ] }, { { tmp30 * (std::get< 0 >( phi ))[ 0 ] + tmp47 * ((std::get< 1 >( phi ))[ 0 ])[ 0 ], tmp40 * (std::get< 0 >( phi ))[ 0 ] + tmp47 * ((std::get< 1 >( phi ))[ 0 ])[ 1 ] } } };
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
          using std::sqrt;
          auto tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
          const auto tmp1 = tmp0[ 1 ] * tmp0[ 1 ];
          const auto tmp2 = tmp0[ 0 ] * tmp0[ 0 ];
          const auto tmp3 = tmp2 + tmp1;
          const auto tmp4 = std::sqrt( tmp3 );
          const auto tmp5 = 2 * tmp4;
          const auto tmp6 = tmp0[ 1 ] + tmp0[ 1 ];
          const auto tmp7 = tmp6 / tmp5;
          const auto tmp8 = -1 * tmp7;
          const auto tmp9 = -1 + tmp4;
          const auto tmp10 = tmp9 * tmp8;
          const auto tmp11 = tmp0[ 1 ] + tmp10;
          const auto tmp12 = 3.141592653589793 * tmp11;
          const auto tmp13 = std::sin( tmp12 );
          const auto tmp14 = tmp0[ 0 ] + tmp0[ 0 ];
          const auto tmp15 = tmp14 / tmp5;
          const auto tmp16 = -1 * tmp15;
          const auto tmp17 = tmp9 * tmp16;
          const auto tmp18 = tmp0[ 0 ] + tmp17;
          const auto tmp19 = 3.141592653589793 * tmp18;
          const auto tmp20 = std::sin( tmp19 );
          const auto tmp21 = tmp20 * tmp13;
          result[ 0 ] = tmp21;
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
          using std::sqrt;
          auto tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
          const auto tmp1 = tmp0[ 1 ] * tmp0[ 1 ];
          const auto tmp2 = tmp0[ 0 ] * tmp0[ 0 ];
          const auto tmp3 = tmp2 + tmp1;
          const auto tmp4 = std::sqrt( tmp3 );
          const auto tmp5 = 2 * tmp4;
          const auto tmp6 = tmp0[ 1 ] + tmp0[ 1 ];
          const auto tmp7 = tmp6 / tmp5;
          const auto tmp8 = -1 * tmp7;
          const auto tmp9 = -1 + tmp4;
          const auto tmp10 = tmp9 * tmp8;
          const auto tmp11 = tmp0[ 1 ] + tmp10;
          const auto tmp12 = 3.141592653589793 * tmp11;
          const auto tmp13 = std::sin( tmp12 );
          const auto tmp14 = tmp0[ 0 ] + tmp0[ 0 ];
          const auto tmp15 = tmp14 / tmp5;
          const auto tmp16 = -1 * tmp15;
          const auto tmp17 = tmp9 * tmp16;
          const auto tmp18 = tmp0[ 0 ] + tmp17;
          const auto tmp19 = 3.141592653589793 * tmp18;
          const auto tmp20 = std::cos( tmp19 );
          const auto tmp21 = tmp16 * tmp15;
          const auto tmp22 = 2 * tmp15;
          const auto tmp23 = tmp22 * tmp15;
          const auto tmp24 = -1 * tmp23;
          const auto tmp25 = 2 + tmp24;
          const auto tmp26 = tmp25 / tmp5;
          const auto tmp27 = -1 * tmp26;
          const auto tmp28 = tmp9 * tmp27;
          const auto tmp29 = tmp28 + tmp21;
          const auto tmp30 = 1 + tmp29;
          const auto tmp31 = 3.141592653589793 * tmp30;
          const auto tmp32 = tmp31 * tmp20;
          const auto tmp33 = tmp32 * tmp13;
          const auto tmp34 = std::sin( tmp19 );
          const auto tmp35 = std::cos( tmp12 );
          const auto tmp36 = tmp8 * tmp15;
          const auto tmp37 = tmp22 * tmp7;
          const auto tmp38 = -1 * tmp37;
          const auto tmp39 = tmp38 / tmp5;
          const auto tmp40 = -1 * tmp39;
          const auto tmp41 = tmp9 * tmp40;
          const auto tmp42 = tmp41 + tmp36;
          const auto tmp43 = 3.141592653589793 * tmp42;
          const auto tmp44 = tmp43 * tmp35;
          const auto tmp45 = tmp44 * tmp34;
          const auto tmp46 = tmp45 + tmp33;
          const auto tmp47 = tmp16 * tmp7;
          const auto tmp48 = 2 * tmp7;
          const auto tmp49 = tmp48 * tmp15;
          const auto tmp50 = -1 * tmp49;
          const auto tmp51 = tmp50 / tmp5;
          const auto tmp52 = -1 * tmp51;
          const auto tmp53 = tmp9 * tmp52;
          const auto tmp54 = tmp53 + tmp47;
          const auto tmp55 = 3.141592653589793 * tmp54;
          const auto tmp56 = tmp55 * tmp20;
          const auto tmp57 = tmp56 * tmp13;
          const auto tmp58 = tmp8 * tmp7;
          const auto tmp59 = tmp48 * tmp7;
          const auto tmp60 = -1 * tmp59;
          const auto tmp61 = 2 + tmp60;
          const auto tmp62 = tmp61 / tmp5;
          const auto tmp63 = -1 * tmp62;
          const auto tmp64 = tmp9 * tmp63;
          const auto tmp65 = tmp64 + tmp58;
          const auto tmp66 = 1 + tmp65;
          const auto tmp67 = 3.141592653589793 * tmp66;
          const auto tmp68 = tmp67 * tmp35;
          const auto tmp69 = tmp68 * tmp34;
          const auto tmp70 = tmp69 + tmp57;
          (result[ 0 ])[ 0 ] = tmp46;
          (result[ 0 ])[ 1 ] = tmp70;
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

} // namespace Integrands_3bde0abfafcf45a3cff4d1029568ab5cv1_3

PYBIND11_MODULE( integrands_3bde0abfafcf45a3cff4d1029568ab5cv1_3_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > GridPart;
  typedef Integrands_3bde0abfafcf45a3cff4d1029568ab5cv1_3::Integrands< GridPart > Integrands;
  if constexpr( Integrands::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<Integrands>(module,"Integrands",Dune::Python::GenerateTypeName("Integrands_3bde0abfafcf45a3cff4d1029568ab5cv1_3::Integrands< GridPart >"), Dune::Python::IncludeFiles({"python/dune/generated/integrands_3bde0abfafcf45a3cff4d1029568ab5cv1_3_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerIntegrands< Integrands >( module, cls );
      cls.def( pybind11::init( [] () { return new Integrands(); } ) );
      cls.def_property_readonly( "virtualized", [] ( Integrands& ) -> bool { return true;});
      cls.def_property_readonly( "hasDirichletBoundary", [] ( Integrands& ) -> bool { return true;});
  }
}
#endif // GuardIntegrands_3bde0abfafcf45a3cff4d1029568ab5cv1_3
