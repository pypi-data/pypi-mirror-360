#ifndef GuardIntegrands_008eefa148b772fa3192dd3c1728c140v1_3
#define GuardIntegrands_008eefa148b772fa3192dd3c1728c140v1_3
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

namespace Integrands_008eefa148b772fa3192dd3c1728c140v1_3
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
      const auto tmp4 = 1e-10 + tmp3;
      const auto tmp5 = std::sqrt( tmp4 );
      const auto tmp6 = 2 * tmp5;
      const auto tmp7 = tmp0[ 1 ] + tmp0[ 1 ];
      const auto tmp8 = tmp7 / tmp6;
      const auto tmp9 = -1 * tmp8;
      const auto tmp10 = -1 + tmp5;
      const auto tmp11 = tmp10 * tmp9;
      const auto tmp12 = tmp0[ 1 ] + tmp11;
      const auto tmp13 = tmp12 * tmp12;
      const auto tmp14 = tmp0[ 0 ] + tmp0[ 0 ];
      const auto tmp15 = tmp14 / tmp6;
      const auto tmp16 = -1 * tmp15;
      const auto tmp17 = tmp10 * tmp16;
      const auto tmp18 = tmp0[ 0 ] + tmp17;
      const auto tmp19 = tmp18 * tmp18;
      const auto tmp20 = tmp19 + tmp13;
      const auto tmp21 = 1e-10 + tmp20;
      const auto tmp22 = std::sqrt( tmp21 );
      const auto tmp23 = -1 + tmp22;
      const auto tmp24 = 3 * tmp23;
      const auto tmp25 = tmp24 / 0.225;
      const auto tmp26 = std::tanh( tmp25 );
      const auto tmp27 = -1 * tmp26;
      const auto tmp28 = 1 + tmp27;
      const auto tmp29 = 0.5 * tmp28;
      const auto tmp30 = -1 * tmp29;
      const auto tmp31 = 1 + tmp30;
      const auto tmp32 = tmp31 * tmp29;
      const auto tmp33 = 1e-10 + tmp32;
      const auto tmp34 = 3.141592653589793 * tmp12;
      const auto tmp35 = std::sin( tmp34 );
      const auto tmp36 = 3.141592653589793 * tmp18;
      const auto tmp37 = std::sin( tmp36 );
      const auto tmp38 = tmp37 * tmp35;
      const auto tmp39 = -1 * tmp38;
      const auto tmp40 = std::get< 0 >( u );
      const auto tmp41 = tmp40[ 0 ] + tmp39;
      const auto tmp42 = tmp41 * tmp32;
      const auto tmp43 = tmp42 / tmp33;
      const auto tmp44 = 3 * tmp10;
      const auto tmp45 = tmp44 / 0.225;
      const auto tmp46 = std::tanh( tmp45 );
      const auto tmp47 = -1 * tmp46;
      const auto tmp48 = 1 + tmp47;
      const auto tmp49 = 0.5 * tmp48;
      const auto tmp50 = 0.9999999999 * tmp49;
      const auto tmp51 = 1e-10 + tmp50;
      const auto tmp52 = -1 * tmp51;
      const auto tmp53 = 1 + tmp52;
      const auto tmp54 = tmp53 * tmp43;
      const auto tmp55 = tmp54 / 0.011390625000000001;
      const auto tmp56 = -1 * tmp55;
      const auto tmp57 = 3 * tmp56;
      const auto tmp58 = -1 * tmp57;
      const auto tmp59 = 0.1 * tmp56;
      const auto tmp60 = 0.01 * tmp40[ 0 ];
      const auto tmp61 = -1 * tmp60;
      const auto tmp62 = -1 * (tmp10 <= 0.0 ? 1 : 0.0);
      const auto tmp63 = 1 + tmp62;
      const auto tmp64 = tmp63 * tmp11;
      const auto tmp65 = tmp0[ 1 ] + tmp64;
      const auto tmp66 = tmp65 * tmp65;
      const auto tmp67 = tmp63 * tmp17;
      const auto tmp68 = tmp0[ 0 ] + tmp67;
      const auto tmp69 = tmp68 * tmp68;
      const auto tmp70 = tmp69 + tmp66;
      const auto tmp71 = -1 * tmp70;
      const auto tmp72 = 1 + tmp71;
      const auto tmp73 = 0.1 * tmp72;
      const auto tmp74 = tmp73 + tmp61;
      const auto tmp75 = tmp74 * tmp51;
      const auto tmp76 = tmp75 + tmp59;
      const auto tmp77 = -1 * tmp76;
      const auto tmp78 = tmp77 + tmp58;
      const auto tmp79 = 3 * tmp65;
      const auto tmp80 = tmp40[ 0 ] * tmp79;
      const auto tmp81 = tmp51 * tmp80;
      const auto tmp82 = -1 * tmp81;
      const auto tmp83 = 0.05 * tmp70;
      const auto tmp84 = -1 * tmp83;
      const auto tmp85 = 0.1 + tmp84;
      const auto tmp86 = std::get< 1 >( u );
      const auto tmp87 = (tmp86[ 0 ])[ 0 ] * tmp85;
      const auto tmp88 = tmp51 * tmp87;
      const auto tmp89 = tmp88 + tmp82;
      const auto tmp90 = -1 * tmp68;
      const auto tmp91 = 3 * tmp90;
      const auto tmp92 = tmp40[ 0 ] * tmp91;
      const auto tmp93 = tmp51 * tmp92;
      const auto tmp94 = -1 * tmp93;
      const auto tmp95 = (tmp86[ 0 ])[ 1 ] * tmp85;
      const auto tmp96 = tmp51 * tmp95;
      const auto tmp97 = tmp96 + tmp94;
      return RangeValueType{ { tmp78 }, { { tmp89, tmp97 } } };
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
      const auto tmp4 = 1e-10 + tmp3;
      const auto tmp5 = std::sqrt( tmp4 );
      const auto tmp6 = 2 * tmp5;
      const auto tmp7 = tmp0[ 1 ] + tmp0[ 1 ];
      const auto tmp8 = tmp7 / tmp6;
      const auto tmp9 = -1 * tmp8;
      const auto tmp10 = -1 + tmp5;
      const auto tmp11 = tmp10 * tmp9;
      const auto tmp12 = tmp0[ 1 ] + tmp11;
      const auto tmp13 = tmp12 * tmp12;
      const auto tmp14 = tmp0[ 0 ] + tmp0[ 0 ];
      const auto tmp15 = tmp14 / tmp6;
      const auto tmp16 = -1 * tmp15;
      const auto tmp17 = tmp10 * tmp16;
      const auto tmp18 = tmp0[ 0 ] + tmp17;
      const auto tmp19 = tmp18 * tmp18;
      const auto tmp20 = tmp19 + tmp13;
      const auto tmp21 = 1e-10 + tmp20;
      const auto tmp22 = std::sqrt( tmp21 );
      const auto tmp23 = -1 + tmp22;
      const auto tmp24 = 3 * tmp23;
      const auto tmp25 = tmp24 / 0.225;
      const auto tmp26 = std::tanh( tmp25 );
      const auto tmp27 = -1 * tmp26;
      const auto tmp28 = 1 + tmp27;
      const auto tmp29 = 0.5 * tmp28;
      const auto tmp30 = -1 * tmp29;
      const auto tmp31 = 1 + tmp30;
      const auto tmp32 = tmp31 * tmp29;
      const auto tmp33 = 1e-10 + tmp32;
      const auto tmp34 = tmp32 / tmp33;
      const auto tmp35 = 3 * tmp10;
      const auto tmp36 = tmp35 / 0.225;
      const auto tmp37 = std::tanh( tmp36 );
      const auto tmp38 = -1 * tmp37;
      const auto tmp39 = 1 + tmp38;
      const auto tmp40 = 0.5 * tmp39;
      const auto tmp41 = 0.9999999999 * tmp40;
      const auto tmp42 = 1e-10 + tmp41;
      const auto tmp43 = -1 * tmp42;
      const auto tmp44 = 1 + tmp43;
      const auto tmp45 = tmp44 * tmp34;
      const auto tmp46 = tmp45 / 0.011390625000000001;
      const auto tmp47 = -1 * tmp46;
      const auto tmp48 = 3 * tmp47;
      const auto tmp49 = -1 * tmp48;
      const auto tmp50 = 0.1 * tmp47;
      const auto tmp51 = -0.01 * tmp42;
      const auto tmp52 = tmp51 + tmp50;
      const auto tmp53 = -1 * tmp52;
      const auto tmp54 = tmp53 + tmp49;
      const auto tmp55 = -1 * (tmp10 <= 0.0 ? 1 : 0.0);
      const auto tmp56 = 1 + tmp55;
      const auto tmp57 = tmp56 * tmp11;
      const auto tmp58 = tmp0[ 1 ] + tmp57;
      const auto tmp59 = 3 * tmp58;
      const auto tmp60 = tmp42 * tmp59;
      const auto tmp61 = -1 * tmp60;
      const auto tmp62 = tmp56 * tmp17;
      const auto tmp63 = tmp0[ 0 ] + tmp62;
      const auto tmp64 = -1 * tmp63;
      const auto tmp65 = 3 * tmp64;
      const auto tmp66 = tmp42 * tmp65;
      const auto tmp67 = -1 * tmp66;
      const auto tmp68 = tmp58 * tmp58;
      const auto tmp69 = tmp63 * tmp63;
      const auto tmp70 = tmp69 + tmp68;
      const auto tmp71 = 0.05 * tmp70;
      const auto tmp72 = -1 * tmp71;
      const auto tmp73 = 0.1 + tmp72;
      const auto tmp74 = tmp73 * tmp42;
      return [ tmp54, tmp61, tmp67, tmp74 ] ( const DomainValueType &phi ) {
          return RangeValueType{ { tmp54 * (std::get< 0 >( phi ))[ 0 ] }, { { tmp61 * (std::get< 0 >( phi ))[ 0 ] + tmp74 * ((std::get< 1 >( phi ))[ 0 ])[ 0 ], tmp67 * (std::get< 0 >( phi ))[ 0 ] + tmp74 * ((std::get< 1 >( phi ))[ 0 ])[ 1 ] } } };
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
              using std::sqrt;
              auto tmp0 = intersection.geometry().center( );
              const auto tmp1 = tmp0[ 1 ] * tmp0[ 1 ];
              const auto tmp2 = tmp0[ 0 ] * tmp0[ 0 ];
              const auto tmp3 = tmp2 + tmp1;
              const auto tmp4 = 1e-10 + tmp3;
              const auto tmp5 = std::sqrt( tmp4 );
              const auto tmp6 = -1 + tmp5;
              domainId = (tmp6 <= 0.0 ? 1 : 0.0) < 0.5;
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
          using std::sqrt;
          using std::tanh;
          auto tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
          const auto tmp1 = tmp0[ 1 ] * tmp0[ 1 ];
          const auto tmp2 = tmp0[ 0 ] * tmp0[ 0 ];
          const auto tmp3 = tmp2 + tmp1;
          const auto tmp4 = 1e-10 + tmp3;
          const auto tmp5 = std::sqrt( tmp4 );
          const auto tmp6 = 2 * tmp5;
          const auto tmp7 = tmp0[ 1 ] + tmp0[ 1 ];
          const auto tmp8 = tmp7 / tmp6;
          const auto tmp9 = -1 * tmp8;
          const auto tmp10 = -1 + tmp5;
          const auto tmp11 = tmp10 * tmp9;
          const auto tmp12 = tmp0[ 1 ] + tmp11;
          const auto tmp13 = tmp12 * tmp12;
          const auto tmp14 = tmp0[ 0 ] + tmp0[ 0 ];
          const auto tmp15 = tmp14 / tmp6;
          const auto tmp16 = -1 * tmp15;
          const auto tmp17 = tmp10 * tmp16;
          const auto tmp18 = tmp0[ 0 ] + tmp17;
          const auto tmp19 = tmp18 * tmp18;
          const auto tmp20 = tmp19 + tmp13;
          const auto tmp21 = 1e-10 + tmp20;
          const auto tmp22 = std::sqrt( tmp21 );
          const auto tmp23 = -1 + tmp22;
          const auto tmp24 = 3 * tmp23;
          const auto tmp25 = tmp24 / 0.225;
          const auto tmp26 = std::tanh( tmp25 );
          const auto tmp27 = -1 * tmp26;
          const auto tmp28 = 1 + tmp27;
          const auto tmp29 = 0.5 * tmp28;
          const auto tmp30 = -1 * tmp29;
          const auto tmp31 = 1 + tmp30;
          const auto tmp32 = tmp31 * tmp29;
          const auto tmp33 = 1e-10 + tmp32;
          const auto tmp34 = 3.141592653589793 * tmp12;
          const auto tmp35 = std::sin( tmp34 );
          const auto tmp36 = 3.141592653589793 * tmp18;
          const auto tmp37 = std::sin( tmp36 );
          const auto tmp38 = tmp37 * tmp35;
          const auto tmp39 = -1 * tmp38;
          const auto tmp40 = tmp32 * tmp39;
          const auto tmp41 = tmp40 / tmp33;
          const auto tmp42 = -1 * tmp41;
          result[ 0 ] = tmp42;
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
          using std::cosh;
          using std::pow;
          using std::sin;
          using std::sqrt;
          using std::tanh;
          auto tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
          const auto tmp1 = tmp0[ 1 ] * tmp0[ 1 ];
          const auto tmp2 = tmp0[ 0 ] * tmp0[ 0 ];
          const auto tmp3 = tmp2 + tmp1;
          const auto tmp4 = 1e-10 + tmp3;
          const auto tmp5 = std::sqrt( tmp4 );
          const auto tmp6 = 2 * tmp5;
          const auto tmp7 = tmp0[ 1 ] + tmp0[ 1 ];
          const auto tmp8 = tmp7 / tmp6;
          const auto tmp9 = -1 * tmp8;
          const auto tmp10 = -1 + tmp5;
          const auto tmp11 = tmp10 * tmp9;
          const auto tmp12 = tmp0[ 1 ] + tmp11;
          const auto tmp13 = tmp12 * tmp12;
          const auto tmp14 = tmp0[ 0 ] + tmp0[ 0 ];
          const auto tmp15 = tmp14 / tmp6;
          const auto tmp16 = -1 * tmp15;
          const auto tmp17 = tmp10 * tmp16;
          const auto tmp18 = tmp0[ 0 ] + tmp17;
          const auto tmp19 = tmp18 * tmp18;
          const auto tmp20 = tmp19 + tmp13;
          const auto tmp21 = 1e-10 + tmp20;
          const auto tmp22 = std::sqrt( tmp21 );
          const auto tmp23 = -1 + tmp22;
          const auto tmp24 = 3 * tmp23;
          const auto tmp25 = tmp24 / 0.225;
          const auto tmp26 = std::tanh( tmp25 );
          const auto tmp27 = -1 * tmp26;
          const auto tmp28 = 1 + tmp27;
          const auto tmp29 = 0.5 * tmp28;
          const auto tmp30 = -1 * tmp29;
          const auto tmp31 = 1 + tmp30;
          const auto tmp32 = tmp31 * tmp29;
          const auto tmp33 = 1e-10 + tmp32;
          const auto tmp34 = 3.141592653589793 * tmp12;
          const auto tmp35 = std::sin( tmp34 );
          const auto tmp36 = 3.141592653589793 * tmp18;
          const auto tmp37 = std::sin( tmp36 );
          const auto tmp38 = tmp37 * tmp35;
          const auto tmp39 = -1 * tmp38;
          const auto tmp40 = tmp32 * tmp39;
          const auto tmp41 = tmp40 / tmp33;
          const auto tmp42 = 2.0 * tmp25;
          const auto tmp43 = std::cosh( tmp42 );
          const auto tmp44 = 1.0 + tmp43;
          const auto tmp45 = std::cosh( tmp25 );
          const auto tmp46 = 2.0 * tmp45;
          const auto tmp47 = tmp46 / tmp44;
          const auto tmp48 = std::pow( tmp47, 2 );
          const auto tmp49 = 2 * tmp22;
          const auto tmp50 = tmp9 * tmp15;
          const auto tmp51 = 2 * tmp15;
          const auto tmp52 = tmp51 * tmp8;
          const auto tmp53 = -1 * tmp52;
          const auto tmp54 = tmp53 / tmp6;
          const auto tmp55 = -1 * tmp54;
          const auto tmp56 = tmp10 * tmp55;
          const auto tmp57 = tmp56 + tmp50;
          const auto tmp58 = tmp12 * tmp57;
          const auto tmp59 = tmp58 + tmp58;
          const auto tmp60 = tmp16 * tmp15;
          const auto tmp61 = tmp51 * tmp15;
          const auto tmp62 = -1 * tmp61;
          const auto tmp63 = 2 + tmp62;
          const auto tmp64 = tmp63 / tmp6;
          const auto tmp65 = -1 * tmp64;
          const auto tmp66 = tmp10 * tmp65;
          const auto tmp67 = tmp66 + tmp60;
          const auto tmp68 = 1 + tmp67;
          const auto tmp69 = tmp68 * tmp18;
          const auto tmp70 = tmp69 + tmp69;
          const auto tmp71 = tmp70 + tmp59;
          const auto tmp72 = tmp71 / tmp49;
          const auto tmp73 = 3 * tmp72;
          const auto tmp74 = tmp73 / 0.225;
          const auto tmp75 = tmp74 * tmp48;
          const auto tmp76 = -1 * tmp75;
          const auto tmp77 = 0.5 * tmp76;
          const auto tmp78 = tmp31 * tmp77;
          const auto tmp79 = -1 * tmp77;
          const auto tmp80 = tmp29 * tmp79;
          const auto tmp81 = tmp80 + tmp78;
          const auto tmp82 = tmp81 * tmp41;
          const auto tmp83 = -1 * tmp82;
          const auto tmp84 = tmp81 * tmp39;
          const auto tmp85 = std::cos( tmp36 );
          const auto tmp86 = 3.141592653589793 * tmp68;
          const auto tmp87 = tmp86 * tmp85;
          const auto tmp88 = tmp87 * tmp35;
          const auto tmp89 = std::cos( tmp34 );
          const auto tmp90 = 3.141592653589793 * tmp57;
          const auto tmp91 = tmp90 * tmp89;
          const auto tmp92 = tmp91 * tmp37;
          const auto tmp93 = tmp92 + tmp88;
          const auto tmp94 = -1 * tmp93;
          const auto tmp95 = tmp94 * tmp32;
          const auto tmp96 = tmp95 + tmp84;
          const auto tmp97 = tmp96 + tmp83;
          const auto tmp98 = tmp97 / tmp33;
          const auto tmp99 = -1 * tmp98;
          const auto tmp100 = tmp16 * tmp8;
          const auto tmp101 = 2 * tmp8;
          const auto tmp102 = tmp101 * tmp15;
          const auto tmp103 = -1 * tmp102;
          const auto tmp104 = tmp103 / tmp6;
          const auto tmp105 = -1 * tmp104;
          const auto tmp106 = tmp10 * tmp105;
          const auto tmp107 = tmp106 + tmp100;
          const auto tmp108 = tmp18 * tmp107;
          const auto tmp109 = tmp108 + tmp108;
          const auto tmp110 = tmp9 * tmp8;
          const auto tmp111 = tmp101 * tmp8;
          const auto tmp112 = -1 * tmp111;
          const auto tmp113 = 2 + tmp112;
          const auto tmp114 = tmp113 / tmp6;
          const auto tmp115 = -1 * tmp114;
          const auto tmp116 = tmp10 * tmp115;
          const auto tmp117 = tmp116 + tmp110;
          const auto tmp118 = 1 + tmp117;
          const auto tmp119 = tmp118 * tmp12;
          const auto tmp120 = tmp119 + tmp119;
          const auto tmp121 = tmp120 + tmp109;
          const auto tmp122 = tmp121 / tmp49;
          const auto tmp123 = 3 * tmp122;
          const auto tmp124 = tmp123 / 0.225;
          const auto tmp125 = tmp124 * tmp48;
          const auto tmp126 = -1 * tmp125;
          const auto tmp127 = 0.5 * tmp126;
          const auto tmp128 = tmp31 * tmp127;
          const auto tmp129 = -1 * tmp127;
          const auto tmp130 = tmp29 * tmp129;
          const auto tmp131 = tmp130 + tmp128;
          const auto tmp132 = tmp131 * tmp41;
          const auto tmp133 = -1 * tmp132;
          const auto tmp134 = tmp131 * tmp39;
          const auto tmp135 = 3.141592653589793 * tmp107;
          const auto tmp136 = tmp135 * tmp85;
          const auto tmp137 = tmp136 * tmp35;
          const auto tmp138 = 3.141592653589793 * tmp118;
          const auto tmp139 = tmp138 * tmp89;
          const auto tmp140 = tmp139 * tmp37;
          const auto tmp141 = tmp140 + tmp137;
          const auto tmp142 = -1 * tmp141;
          const auto tmp143 = tmp142 * tmp32;
          const auto tmp144 = tmp143 + tmp134;
          const auto tmp145 = tmp144 + tmp133;
          const auto tmp146 = tmp145 / tmp33;
          const auto tmp147 = -1 * tmp146;
          (result[ 0 ])[ 0 ] = tmp99;
          (result[ 0 ])[ 1 ] = tmp147;
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

} // namespace Integrands_008eefa148b772fa3192dd3c1728c140v1_3

PYBIND11_MODULE( integrands_008eefa148b772fa3192dd3c1728c140v1_3_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > GridPart;
  typedef Integrands_008eefa148b772fa3192dd3c1728c140v1_3::Integrands< GridPart > Integrands;
  if constexpr( Integrands::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<Integrands>(module,"Integrands",Dune::Python::GenerateTypeName("Integrands_008eefa148b772fa3192dd3c1728c140v1_3::Integrands< GridPart >"), Dune::Python::IncludeFiles({"python/dune/generated/integrands_008eefa148b772fa3192dd3c1728c140v1_3_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerIntegrands< Integrands >( module, cls );
      cls.def( pybind11::init( [] () { return new Integrands(); } ) );
      cls.def_property_readonly( "virtualized", [] ( Integrands& ) -> bool { return true;});
      cls.def_property_readonly( "hasDirichletBoundary", [] ( Integrands& ) -> bool { return true;});
  }
}
#endif // GuardIntegrands_008eefa148b772fa3192dd3c1728c140v1_3
