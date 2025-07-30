#ifndef GUARD_7d81d496538f240d504e5597484ee746
#define GUARD_7d81d496538f240d504e5597484ee746

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

namespace UFLLocalFunctions_7d81d496538f240d504e5597484ee746
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
  typedef std::tuple<> ConstantTupleType;
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
  {}

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
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = 1 + tmp0[ 0 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -0.5 + tmp6;
    const auto tmp8 = -1 + tmp0[ 0 ];
    const auto tmp9 = tmp8 * tmp8;
    const auto tmp10 = tmp3 + tmp9;
    const auto tmp11 = 1e-10 + tmp10;
    const auto tmp12 = std::sqrt( tmp11 );
    const auto tmp13 = -0.5 + tmp12;
    const auto tmp14 = 0.8 + tmp0[ 1 ];
    const auto tmp15 = tmp14 * tmp14;
    const auto tmp16 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp17 = tmp16 + tmp15;
    const auto tmp18 = 1e-10 + tmp17;
    const auto tmp19 = std::sqrt( tmp18 );
    const auto tmp20 = -0.5 + tmp19;
    const auto tmp21 = -1 * tmp20;
    const auto tmp22 = -0.8 + tmp0[ 1 ];
    const auto tmp23 = tmp22 * tmp22;
    const auto tmp24 = tmp16 + tmp23;
    const auto tmp25 = 1e-10 + tmp24;
    const auto tmp26 = std::sqrt( tmp25 );
    const auto tmp27 = -0.5 + tmp26;
    const auto tmp28 = -1 * tmp27;
    const auto tmp29 = tmp16 + tmp3;
    const auto tmp30 = 1e-10 + tmp29;
    const auto tmp31 = std::sqrt( tmp30 );
    const auto tmp32 = -1 + tmp31;
    const auto tmp33 = std::max( tmp32, tmp28 );
    const auto tmp34 = std::max( tmp33, tmp21 );
    const auto tmp35 = std::min( tmp34, tmp13 );
    const auto tmp36 = std::min( tmp35, tmp7 );
    result[ 0 ] = tmp36;
  }

  template< class Point >
  void jacobian ( const Point &x, typename FunctionSpaceType::JacobianRangeType &result ) const
  {
    using std::max;
    using std::min;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = 1 + tmp0[ 0 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -0.5 + tmp6;
    const auto tmp8 = -1 + tmp0[ 0 ];
    const auto tmp9 = tmp8 * tmp8;
    const auto tmp10 = tmp3 + tmp9;
    const auto tmp11 = 1e-10 + tmp10;
    const auto tmp12 = std::sqrt( tmp11 );
    const auto tmp13 = -0.5 + tmp12;
    const auto tmp14 = 0.8 + tmp0[ 1 ];
    const auto tmp15 = tmp14 * tmp14;
    const auto tmp16 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp17 = tmp16 + tmp15;
    const auto tmp18 = 1e-10 + tmp17;
    const auto tmp19 = std::sqrt( tmp18 );
    const auto tmp20 = -0.5 + tmp19;
    const auto tmp21 = -1 * tmp20;
    const auto tmp22 = -0.8 + tmp0[ 1 ];
    const auto tmp23 = tmp22 * tmp22;
    const auto tmp24 = tmp16 + tmp23;
    const auto tmp25 = 1e-10 + tmp24;
    const auto tmp26 = std::sqrt( tmp25 );
    const auto tmp27 = -0.5 + tmp26;
    const auto tmp28 = -1 * tmp27;
    const auto tmp29 = tmp16 + tmp3;
    const auto tmp30 = 1e-10 + tmp29;
    const auto tmp31 = std::sqrt( tmp30 );
    const auto tmp32 = -1 + tmp31;
    const auto tmp33 = std::max( tmp32, tmp28 );
    const auto tmp34 = std::max( tmp33, tmp21 );
    const auto tmp35 = std::min( tmp34, tmp13 );
    const auto tmp36 = 2 * tmp31;
    const auto tmp37 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp38 = tmp37 / tmp36;
    const auto tmp39 = tmp38 * (tmp32 > tmp28 ? 1 : 0.0);
    const auto tmp40 = 2 * tmp26;
    const auto tmp41 = tmp37 / tmp40;
    const auto tmp42 = -1 * tmp41;
    const auto tmp43 = -1 * (tmp32 > tmp28 ? 1 : 0.0);
    const auto tmp44 = 1.0 + tmp43;
    const auto tmp45 = tmp44 * tmp42;
    const auto tmp46 = tmp45 + tmp39;
    const auto tmp47 = tmp46 * (tmp33 > tmp21 ? 1 : 0.0);
    const auto tmp48 = 2 * tmp19;
    const auto tmp49 = tmp37 / tmp48;
    const auto tmp50 = -1 * tmp49;
    const auto tmp51 = -1 * (tmp33 > tmp21 ? 1 : 0.0);
    const auto tmp52 = 1.0 + tmp51;
    const auto tmp53 = tmp52 * tmp50;
    const auto tmp54 = tmp53 + tmp47;
    const auto tmp55 = tmp54 * (tmp34 < tmp13 ? 1 : 0.0);
    const auto tmp56 = 2 * tmp12;
    const auto tmp57 = tmp8 + tmp8;
    const auto tmp58 = tmp57 / tmp56;
    const auto tmp59 = -1 * (tmp34 < tmp13 ? 1 : 0.0);
    const auto tmp60 = 1.0 + tmp59;
    const auto tmp61 = tmp60 * tmp58;
    const auto tmp62 = tmp61 + tmp55;
    const auto tmp63 = tmp62 * (tmp35 < tmp7 ? 1 : 0.0);
    const auto tmp64 = 2 * tmp6;
    const auto tmp65 = tmp1 + tmp1;
    const auto tmp66 = tmp65 / tmp64;
    const auto tmp67 = -1 * (tmp35 < tmp7 ? 1 : 0.0);
    const auto tmp68 = 1.0 + tmp67;
    const auto tmp69 = tmp68 * tmp66;
    const auto tmp70 = tmp69 + tmp63;
    const auto tmp71 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp72 = tmp71 / tmp36;
    const auto tmp73 = tmp72 * (tmp32 > tmp28 ? 1 : 0.0);
    const auto tmp74 = tmp22 + tmp22;
    const auto tmp75 = tmp74 / tmp40;
    const auto tmp76 = -1 * tmp75;
    const auto tmp77 = tmp44 * tmp76;
    const auto tmp78 = tmp77 + tmp73;
    const auto tmp79 = tmp78 * (tmp33 > tmp21 ? 1 : 0.0);
    const auto tmp80 = tmp14 + tmp14;
    const auto tmp81 = tmp80 / tmp48;
    const auto tmp82 = -1 * tmp81;
    const auto tmp83 = tmp52 * tmp82;
    const auto tmp84 = tmp83 + tmp79;
    const auto tmp85 = tmp84 * (tmp34 < tmp13 ? 1 : 0.0);
    const auto tmp86 = tmp71 / tmp56;
    const auto tmp87 = tmp60 * tmp86;
    const auto tmp88 = tmp87 + tmp85;
    const auto tmp89 = tmp88 * (tmp35 < tmp7 ? 1 : 0.0);
    const auto tmp90 = tmp71 / tmp64;
    const auto tmp91 = tmp68 * tmp90;
    const auto tmp92 = tmp91 + tmp89;
    (result[ 0 ])[ 0 ] = tmp70;
    (result[ 0 ])[ 1 ] = tmp92;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
  {
    using std::max;
    using std::min;
    using std::sqrt;
    GlobalCoordinateType tmp0 = geometry().global( Dune::Fem::coordinate( x ) );
    const auto tmp1 = 1 + tmp0[ 0 ];
    const auto tmp2 = tmp1 * tmp1;
    const auto tmp3 = tmp0[ 1 ] * tmp0[ 1 ];
    const auto tmp4 = tmp3 + tmp2;
    const auto tmp5 = 1e-10 + tmp4;
    const auto tmp6 = std::sqrt( tmp5 );
    const auto tmp7 = -0.5 + tmp6;
    const auto tmp8 = -1 + tmp0[ 0 ];
    const auto tmp9 = tmp8 * tmp8;
    const auto tmp10 = tmp3 + tmp9;
    const auto tmp11 = 1e-10 + tmp10;
    const auto tmp12 = std::sqrt( tmp11 );
    const auto tmp13 = -0.5 + tmp12;
    const auto tmp14 = 0.8 + tmp0[ 1 ];
    const auto tmp15 = tmp14 * tmp14;
    const auto tmp16 = tmp0[ 0 ] * tmp0[ 0 ];
    const auto tmp17 = tmp16 + tmp15;
    const auto tmp18 = 1e-10 + tmp17;
    const auto tmp19 = std::sqrt( tmp18 );
    const auto tmp20 = -0.5 + tmp19;
    const auto tmp21 = -1 * tmp20;
    const auto tmp22 = -0.8 + tmp0[ 1 ];
    const auto tmp23 = tmp22 * tmp22;
    const auto tmp24 = tmp16 + tmp23;
    const auto tmp25 = 1e-10 + tmp24;
    const auto tmp26 = std::sqrt( tmp25 );
    const auto tmp27 = -0.5 + tmp26;
    const auto tmp28 = -1 * tmp27;
    const auto tmp29 = tmp16 + tmp3;
    const auto tmp30 = 1e-10 + tmp29;
    const auto tmp31 = std::sqrt( tmp30 );
    const auto tmp32 = -1 + tmp31;
    const auto tmp33 = std::max( tmp32, tmp28 );
    const auto tmp34 = std::max( tmp33, tmp21 );
    const auto tmp35 = std::min( tmp34, tmp13 );
    const auto tmp36 = 2 * tmp31;
    const auto tmp37 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp38 = tmp37 / tmp36;
    const auto tmp39 = 2 * tmp38;
    const auto tmp40 = tmp39 * tmp38;
    const auto tmp41 = -1 * tmp40;
    const auto tmp42 = 2 + tmp41;
    const auto tmp43 = tmp42 / tmp36;
    const auto tmp44 = tmp43 * (tmp32 > tmp28 ? 1 : 0.0);
    const auto tmp45 = 2 * tmp26;
    const auto tmp46 = tmp37 / tmp45;
    const auto tmp47 = 2 * tmp46;
    const auto tmp48 = tmp47 * tmp46;
    const auto tmp49 = -1 * tmp48;
    const auto tmp50 = 2 + tmp49;
    const auto tmp51 = tmp50 / tmp45;
    const auto tmp52 = -1 * tmp51;
    const auto tmp53 = -1 * (tmp32 > tmp28 ? 1 : 0.0);
    const auto tmp54 = 1.0 + tmp53;
    const auto tmp55 = tmp54 * tmp52;
    const auto tmp56 = tmp55 + tmp44;
    const auto tmp57 = tmp56 * (tmp33 > tmp21 ? 1 : 0.0);
    const auto tmp58 = 2 * tmp19;
    const auto tmp59 = tmp37 / tmp58;
    const auto tmp60 = 2 * tmp59;
    const auto tmp61 = tmp60 * tmp59;
    const auto tmp62 = -1 * tmp61;
    const auto tmp63 = 2 + tmp62;
    const auto tmp64 = tmp63 / tmp58;
    const auto tmp65 = -1 * tmp64;
    const auto tmp66 = -1 * (tmp33 > tmp21 ? 1 : 0.0);
    const auto tmp67 = 1.0 + tmp66;
    const auto tmp68 = tmp67 * tmp65;
    const auto tmp69 = tmp68 + tmp57;
    const auto tmp70 = tmp69 * (tmp34 < tmp13 ? 1 : 0.0);
    const auto tmp71 = 2 * tmp12;
    const auto tmp72 = tmp8 + tmp8;
    const auto tmp73 = tmp72 / tmp71;
    const auto tmp74 = 2 * tmp73;
    const auto tmp75 = tmp74 * tmp73;
    const auto tmp76 = -1 * tmp75;
    const auto tmp77 = 2 + tmp76;
    const auto tmp78 = tmp77 / tmp71;
    const auto tmp79 = -1 * (tmp34 < tmp13 ? 1 : 0.0);
    const auto tmp80 = 1.0 + tmp79;
    const auto tmp81 = tmp80 * tmp78;
    const auto tmp82 = tmp81 + tmp70;
    const auto tmp83 = tmp82 * (tmp35 < tmp7 ? 1 : 0.0);
    const auto tmp84 = 2 * tmp6;
    const auto tmp85 = tmp1 + tmp1;
    const auto tmp86 = tmp85 / tmp84;
    const auto tmp87 = 2 * tmp86;
    const auto tmp88 = tmp87 * tmp86;
    const auto tmp89 = -1 * tmp88;
    const auto tmp90 = 2 + tmp89;
    const auto tmp91 = tmp90 / tmp84;
    const auto tmp92 = -1 * (tmp35 < tmp7 ? 1 : 0.0);
    const auto tmp93 = 1.0 + tmp92;
    const auto tmp94 = tmp93 * tmp91;
    const auto tmp95 = tmp94 + tmp83;
    const auto tmp96 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp97 = tmp96 / tmp36;
    const auto tmp98 = 2 * tmp97;
    const auto tmp99 = tmp98 * tmp38;
    const auto tmp100 = -1 * tmp99;
    const auto tmp101 = tmp100 / tmp36;
    const auto tmp102 = tmp101 * (tmp32 > tmp28 ? 1 : 0.0);
    const auto tmp103 = tmp22 + tmp22;
    const auto tmp104 = tmp103 / tmp45;
    const auto tmp105 = 2 * tmp104;
    const auto tmp106 = tmp105 * tmp46;
    const auto tmp107 = -1 * tmp106;
    const auto tmp108 = tmp107 / tmp45;
    const auto tmp109 = -1 * tmp108;
    const auto tmp110 = tmp54 * tmp109;
    const auto tmp111 = tmp110 + tmp102;
    const auto tmp112 = tmp111 * (tmp33 > tmp21 ? 1 : 0.0);
    const auto tmp113 = tmp14 + tmp14;
    const auto tmp114 = tmp113 / tmp58;
    const auto tmp115 = 2 * tmp114;
    const auto tmp116 = tmp115 * tmp59;
    const auto tmp117 = -1 * tmp116;
    const auto tmp118 = tmp117 / tmp58;
    const auto tmp119 = -1 * tmp118;
    const auto tmp120 = tmp67 * tmp119;
    const auto tmp121 = tmp120 + tmp112;
    const auto tmp122 = tmp121 * (tmp34 < tmp13 ? 1 : 0.0);
    const auto tmp123 = tmp96 / tmp71;
    const auto tmp124 = 2 * tmp123;
    const auto tmp125 = tmp124 * tmp73;
    const auto tmp126 = -1 * tmp125;
    const auto tmp127 = tmp126 / tmp71;
    const auto tmp128 = tmp80 * tmp127;
    const auto tmp129 = tmp128 + tmp122;
    const auto tmp130 = tmp129 * (tmp35 < tmp7 ? 1 : 0.0);
    const auto tmp131 = tmp96 / tmp84;
    const auto tmp132 = 2 * tmp131;
    const auto tmp133 = tmp132 * tmp86;
    const auto tmp134 = -1 * tmp133;
    const auto tmp135 = tmp134 / tmp84;
    const auto tmp136 = tmp93 * tmp135;
    const auto tmp137 = tmp136 + tmp130;
    const auto tmp138 = tmp39 * tmp97;
    const auto tmp139 = -1 * tmp138;
    const auto tmp140 = tmp139 / tmp36;
    const auto tmp141 = tmp140 * (tmp32 > tmp28 ? 1 : 0.0);
    const auto tmp142 = tmp47 * tmp104;
    const auto tmp143 = -1 * tmp142;
    const auto tmp144 = tmp143 / tmp45;
    const auto tmp145 = -1 * tmp144;
    const auto tmp146 = tmp54 * tmp145;
    const auto tmp147 = tmp146 + tmp141;
    const auto tmp148 = tmp147 * (tmp33 > tmp21 ? 1 : 0.0);
    const auto tmp149 = tmp60 * tmp114;
    const auto tmp150 = -1 * tmp149;
    const auto tmp151 = tmp150 / tmp58;
    const auto tmp152 = -1 * tmp151;
    const auto tmp153 = tmp67 * tmp152;
    const auto tmp154 = tmp153 + tmp148;
    const auto tmp155 = tmp154 * (tmp34 < tmp13 ? 1 : 0.0);
    const auto tmp156 = tmp74 * tmp123;
    const auto tmp157 = -1 * tmp156;
    const auto tmp158 = tmp157 / tmp71;
    const auto tmp159 = tmp80 * tmp158;
    const auto tmp160 = tmp159 + tmp155;
    const auto tmp161 = tmp160 * (tmp35 < tmp7 ? 1 : 0.0);
    const auto tmp162 = tmp87 * tmp131;
    const auto tmp163 = -1 * tmp162;
    const auto tmp164 = tmp163 / tmp84;
    const auto tmp165 = tmp93 * tmp164;
    const auto tmp166 = tmp165 + tmp161;
    const auto tmp167 = tmp98 * tmp97;
    const auto tmp168 = -1 * tmp167;
    const auto tmp169 = 2 + tmp168;
    const auto tmp170 = tmp169 / tmp36;
    const auto tmp171 = tmp170 * (tmp32 > tmp28 ? 1 : 0.0);
    const auto tmp172 = tmp105 * tmp104;
    const auto tmp173 = -1 * tmp172;
    const auto tmp174 = 2 + tmp173;
    const auto tmp175 = tmp174 / tmp45;
    const auto tmp176 = -1 * tmp175;
    const auto tmp177 = tmp54 * tmp176;
    const auto tmp178 = tmp177 + tmp171;
    const auto tmp179 = tmp178 * (tmp33 > tmp21 ? 1 : 0.0);
    const auto tmp180 = tmp115 * tmp114;
    const auto tmp181 = -1 * tmp180;
    const auto tmp182 = 2 + tmp181;
    const auto tmp183 = tmp182 / tmp58;
    const auto tmp184 = -1 * tmp183;
    const auto tmp185 = tmp67 * tmp184;
    const auto tmp186 = tmp185 + tmp179;
    const auto tmp187 = tmp186 * (tmp34 < tmp13 ? 1 : 0.0);
    const auto tmp188 = tmp124 * tmp123;
    const auto tmp189 = -1 * tmp188;
    const auto tmp190 = 2 + tmp189;
    const auto tmp191 = tmp190 / tmp71;
    const auto tmp192 = tmp80 * tmp191;
    const auto tmp193 = tmp192 + tmp187;
    const auto tmp194 = tmp193 * (tmp35 < tmp7 ? 1 : 0.0);
    const auto tmp195 = tmp132 * tmp131;
    const auto tmp196 = -1 * tmp195;
    const auto tmp197 = 2 + tmp196;
    const auto tmp198 = tmp197 / tmp84;
    const auto tmp199 = tmp93 * tmp198;
    const auto tmp200 = tmp199 + tmp194;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp95;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp137;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp166;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp200;
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
  ConstantTupleType constants_;
  std::tuple<  > coefficients_;
};

} // namespace UFLLocalFunctions_7d81d496538f240d504e5597484ee746

PYBIND11_MODULE( localfunction_7d81d496538f240d504e5597484ee746_a524c1196983e65de1c06d7d6afdeb44, module )
{
  typedef UFLLocalFunctions_7d81d496538f240d504e5597484ee746::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_7d81d496538f240d504e5597484ee746::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true > > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_7d81d496538f240d504e5597484ee746_a524c1196983e65de1c06d7d6afdeb44.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::Fem::FilteredGridPart< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > >, Dune::Fem::SimpleFilter< Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >, true >>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
