#ifndef GUARD_42ff56710f3bd510798ecabb32a6cbf0
#define GUARD_42ff56710f3bd510798ecabb32a6cbf0

#define USING_DUNE_PYTHON 1
#include <config.h>
#include <dune/alugrid/dgf.hh>
#include <dune/alugrid/grid.hh>
#include <dune/fem/gridpart/adaptiveleafgridpart.hh>
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

namespace UFLLocalFunctions_42ff56710f3bd510798ecabb32a6cbf0
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
    result[ 0 ] = tmp38;
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
    const auto tmp38 = 2 * tmp5;
    const auto tmp39 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp40 = tmp39 / tmp38;
    const auto tmp41 = tmp40 * (tmp33 > tmp32 ? 1 : 0.0);
    const auto tmp42 = 2 * tmp30;
    const auto tmp43 = tmp39 / tmp42;
    const auto tmp44 = -1 * tmp43;
    const auto tmp45 = -1 * (tmp33 > tmp32 ? 1 : 0.0);
    const auto tmp46 = 1.0 + tmp45;
    const auto tmp47 = tmp46 * tmp44;
    const auto tmp48 = tmp47 + tmp41;
    const auto tmp49 = tmp48 * (tmp34 > tmp25 ? 1 : 0.0);
    const auto tmp50 = 2 * tmp23;
    const auto tmp51 = tmp39 / tmp50;
    const auto tmp52 = -1 * tmp51;
    const auto tmp53 = -1 * (tmp34 > tmp25 ? 1 : 0.0);
    const auto tmp54 = 1.0 + tmp53;
    const auto tmp55 = tmp54 * tmp52;
    const auto tmp56 = tmp55 + tmp49;
    const auto tmp57 = tmp56 * (tmp35 < tmp18 ? 1 : 0.0);
    const auto tmp58 = 2 * tmp17;
    const auto tmp59 = tmp13 + tmp13;
    const auto tmp60 = tmp59 / tmp58;
    const auto tmp61 = -1 * (tmp35 < tmp18 ? 1 : 0.0);
    const auto tmp62 = 1.0 + tmp61;
    const auto tmp63 = tmp62 * tmp60;
    const auto tmp64 = tmp63 + tmp57;
    const auto tmp65 = tmp64 * (tmp36 < tmp12 ? 1 : 0.0);
    const auto tmp66 = 2 * tmp11;
    const auto tmp67 = tmp7 + tmp7;
    const auto tmp68 = tmp67 / tmp66;
    const auto tmp69 = -1 * (tmp36 < tmp12 ? 1 : 0.0);
    const auto tmp70 = 1.0 + tmp69;
    const auto tmp71 = tmp70 * tmp68;
    const auto tmp72 = tmp71 + tmp65;
    const auto tmp73 = tmp72 * (tmp37 > tmp6 ? 1 : 0.0);
    const auto tmp74 = -1 * (tmp37 > tmp6 ? 1 : 0.0);
    const auto tmp75 = 1.0 + tmp74;
    const auto tmp76 = tmp75 * tmp40;
    const auto tmp77 = tmp76 + tmp73;
    const auto tmp78 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp79 = tmp78 / tmp38;
    const auto tmp80 = tmp79 * (tmp33 > tmp32 ? 1 : 0.0);
    const auto tmp81 = tmp26 + tmp26;
    const auto tmp82 = tmp81 / tmp42;
    const auto tmp83 = -1 * tmp82;
    const auto tmp84 = tmp46 * tmp83;
    const auto tmp85 = tmp84 + tmp80;
    const auto tmp86 = tmp85 * (tmp34 > tmp25 ? 1 : 0.0);
    const auto tmp87 = tmp19 + tmp19;
    const auto tmp88 = tmp87 / tmp50;
    const auto tmp89 = -1 * tmp88;
    const auto tmp90 = tmp54 * tmp89;
    const auto tmp91 = tmp90 + tmp86;
    const auto tmp92 = tmp91 * (tmp35 < tmp18 ? 1 : 0.0);
    const auto tmp93 = tmp78 / tmp58;
    const auto tmp94 = tmp62 * tmp93;
    const auto tmp95 = tmp94 + tmp92;
    const auto tmp96 = tmp95 * (tmp36 < tmp12 ? 1 : 0.0);
    const auto tmp97 = tmp78 / tmp66;
    const auto tmp98 = tmp70 * tmp97;
    const auto tmp99 = tmp98 + tmp96;
    const auto tmp100 = tmp99 * (tmp37 > tmp6 ? 1 : 0.0);
    const auto tmp101 = tmp75 * tmp79;
    const auto tmp102 = tmp101 + tmp100;
    (result[ 0 ])[ 0 ] = tmp77;
    (result[ 0 ])[ 1 ] = tmp102;
  }

  template< class Point >
  void hessian ( const Point &x, typename FunctionSpaceType::HessianRangeType &result ) const
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
    const auto tmp38 = 2 * tmp5;
    const auto tmp39 = tmp0[ 0 ] + tmp0[ 0 ];
    const auto tmp40 = tmp39 / tmp38;
    const auto tmp41 = 2 * tmp40;
    const auto tmp42 = tmp41 * tmp40;
    const auto tmp43 = -1 * tmp42;
    const auto tmp44 = 2 + tmp43;
    const auto tmp45 = tmp44 / tmp38;
    const auto tmp46 = tmp45 * (tmp33 > tmp32 ? 1 : 0.0);
    const auto tmp47 = 2 * tmp30;
    const auto tmp48 = tmp39 / tmp47;
    const auto tmp49 = 2 * tmp48;
    const auto tmp50 = tmp49 * tmp48;
    const auto tmp51 = -1 * tmp50;
    const auto tmp52 = 2 + tmp51;
    const auto tmp53 = tmp52 / tmp47;
    const auto tmp54 = -1 * tmp53;
    const auto tmp55 = -1 * (tmp33 > tmp32 ? 1 : 0.0);
    const auto tmp56 = 1.0 + tmp55;
    const auto tmp57 = tmp56 * tmp54;
    const auto tmp58 = tmp57 + tmp46;
    const auto tmp59 = tmp58 * (tmp34 > tmp25 ? 1 : 0.0);
    const auto tmp60 = 2 * tmp23;
    const auto tmp61 = tmp39 / tmp60;
    const auto tmp62 = 2 * tmp61;
    const auto tmp63 = tmp62 * tmp61;
    const auto tmp64 = -1 * tmp63;
    const auto tmp65 = 2 + tmp64;
    const auto tmp66 = tmp65 / tmp60;
    const auto tmp67 = -1 * tmp66;
    const auto tmp68 = -1 * (tmp34 > tmp25 ? 1 : 0.0);
    const auto tmp69 = 1.0 + tmp68;
    const auto tmp70 = tmp69 * tmp67;
    const auto tmp71 = tmp70 + tmp59;
    const auto tmp72 = tmp71 * (tmp35 < tmp18 ? 1 : 0.0);
    const auto tmp73 = 2 * tmp17;
    const auto tmp74 = tmp13 + tmp13;
    const auto tmp75 = tmp74 / tmp73;
    const auto tmp76 = 2 * tmp75;
    const auto tmp77 = tmp76 * tmp75;
    const auto tmp78 = -1 * tmp77;
    const auto tmp79 = 2 + tmp78;
    const auto tmp80 = tmp79 / tmp73;
    const auto tmp81 = -1 * (tmp35 < tmp18 ? 1 : 0.0);
    const auto tmp82 = 1.0 + tmp81;
    const auto tmp83 = tmp82 * tmp80;
    const auto tmp84 = tmp83 + tmp72;
    const auto tmp85 = tmp84 * (tmp36 < tmp12 ? 1 : 0.0);
    const auto tmp86 = 2 * tmp11;
    const auto tmp87 = tmp7 + tmp7;
    const auto tmp88 = tmp87 / tmp86;
    const auto tmp89 = 2 * tmp88;
    const auto tmp90 = tmp89 * tmp88;
    const auto tmp91 = -1 * tmp90;
    const auto tmp92 = 2 + tmp91;
    const auto tmp93 = tmp92 / tmp86;
    const auto tmp94 = -1 * (tmp36 < tmp12 ? 1 : 0.0);
    const auto tmp95 = 1.0 + tmp94;
    const auto tmp96 = tmp95 * tmp93;
    const auto tmp97 = tmp96 + tmp85;
    const auto tmp98 = tmp97 * (tmp37 > tmp6 ? 1 : 0.0);
    const auto tmp99 = -1 * (tmp37 > tmp6 ? 1 : 0.0);
    const auto tmp100 = 1.0 + tmp99;
    const auto tmp101 = tmp100 * tmp45;
    const auto tmp102 = tmp101 + tmp98;
    const auto tmp103 = tmp0[ 1 ] + tmp0[ 1 ];
    const auto tmp104 = tmp103 / tmp38;
    const auto tmp105 = 2 * tmp104;
    const auto tmp106 = tmp105 * tmp40;
    const auto tmp107 = -1 * tmp106;
    const auto tmp108 = tmp107 / tmp38;
    const auto tmp109 = tmp108 * (tmp33 > tmp32 ? 1 : 0.0);
    const auto tmp110 = tmp26 + tmp26;
    const auto tmp111 = tmp110 / tmp47;
    const auto tmp112 = 2 * tmp111;
    const auto tmp113 = tmp112 * tmp48;
    const auto tmp114 = -1 * tmp113;
    const auto tmp115 = tmp114 / tmp47;
    const auto tmp116 = -1 * tmp115;
    const auto tmp117 = tmp56 * tmp116;
    const auto tmp118 = tmp117 + tmp109;
    const auto tmp119 = tmp118 * (tmp34 > tmp25 ? 1 : 0.0);
    const auto tmp120 = tmp19 + tmp19;
    const auto tmp121 = tmp120 / tmp60;
    const auto tmp122 = 2 * tmp121;
    const auto tmp123 = tmp122 * tmp61;
    const auto tmp124 = -1 * tmp123;
    const auto tmp125 = tmp124 / tmp60;
    const auto tmp126 = -1 * tmp125;
    const auto tmp127 = tmp69 * tmp126;
    const auto tmp128 = tmp127 + tmp119;
    const auto tmp129 = tmp128 * (tmp35 < tmp18 ? 1 : 0.0);
    const auto tmp130 = tmp103 / tmp73;
    const auto tmp131 = 2 * tmp130;
    const auto tmp132 = tmp131 * tmp75;
    const auto tmp133 = -1 * tmp132;
    const auto tmp134 = tmp133 / tmp73;
    const auto tmp135 = tmp82 * tmp134;
    const auto tmp136 = tmp135 + tmp129;
    const auto tmp137 = tmp136 * (tmp36 < tmp12 ? 1 : 0.0);
    const auto tmp138 = tmp103 / tmp86;
    const auto tmp139 = 2 * tmp138;
    const auto tmp140 = tmp139 * tmp88;
    const auto tmp141 = -1 * tmp140;
    const auto tmp142 = tmp141 / tmp86;
    const auto tmp143 = tmp95 * tmp142;
    const auto tmp144 = tmp143 + tmp137;
    const auto tmp145 = tmp144 * (tmp37 > tmp6 ? 1 : 0.0);
    const auto tmp146 = tmp100 * tmp108;
    const auto tmp147 = tmp146 + tmp145;
    const auto tmp148 = tmp41 * tmp104;
    const auto tmp149 = -1 * tmp148;
    const auto tmp150 = tmp149 / tmp38;
    const auto tmp151 = tmp150 * (tmp33 > tmp32 ? 1 : 0.0);
    const auto tmp152 = tmp49 * tmp111;
    const auto tmp153 = -1 * tmp152;
    const auto tmp154 = tmp153 / tmp47;
    const auto tmp155 = -1 * tmp154;
    const auto tmp156 = tmp56 * tmp155;
    const auto tmp157 = tmp156 + tmp151;
    const auto tmp158 = tmp157 * (tmp34 > tmp25 ? 1 : 0.0);
    const auto tmp159 = tmp62 * tmp121;
    const auto tmp160 = -1 * tmp159;
    const auto tmp161 = tmp160 / tmp60;
    const auto tmp162 = -1 * tmp161;
    const auto tmp163 = tmp69 * tmp162;
    const auto tmp164 = tmp163 + tmp158;
    const auto tmp165 = tmp164 * (tmp35 < tmp18 ? 1 : 0.0);
    const auto tmp166 = tmp76 * tmp130;
    const auto tmp167 = -1 * tmp166;
    const auto tmp168 = tmp167 / tmp73;
    const auto tmp169 = tmp82 * tmp168;
    const auto tmp170 = tmp169 + tmp165;
    const auto tmp171 = tmp170 * (tmp36 < tmp12 ? 1 : 0.0);
    const auto tmp172 = tmp89 * tmp138;
    const auto tmp173 = -1 * tmp172;
    const auto tmp174 = tmp173 / tmp86;
    const auto tmp175 = tmp95 * tmp174;
    const auto tmp176 = tmp175 + tmp171;
    const auto tmp177 = tmp176 * (tmp37 > tmp6 ? 1 : 0.0);
    const auto tmp178 = tmp100 * tmp150;
    const auto tmp179 = tmp178 + tmp177;
    const auto tmp180 = tmp105 * tmp104;
    const auto tmp181 = -1 * tmp180;
    const auto tmp182 = 2 + tmp181;
    const auto tmp183 = tmp182 / tmp38;
    const auto tmp184 = tmp183 * (tmp33 > tmp32 ? 1 : 0.0);
    const auto tmp185 = tmp112 * tmp111;
    const auto tmp186 = -1 * tmp185;
    const auto tmp187 = 2 + tmp186;
    const auto tmp188 = tmp187 / tmp47;
    const auto tmp189 = -1 * tmp188;
    const auto tmp190 = tmp56 * tmp189;
    const auto tmp191 = tmp190 + tmp184;
    const auto tmp192 = tmp191 * (tmp34 > tmp25 ? 1 : 0.0);
    const auto tmp193 = tmp122 * tmp121;
    const auto tmp194 = -1 * tmp193;
    const auto tmp195 = 2 + tmp194;
    const auto tmp196 = tmp195 / tmp60;
    const auto tmp197 = -1 * tmp196;
    const auto tmp198 = tmp69 * tmp197;
    const auto tmp199 = tmp198 + tmp192;
    const auto tmp200 = tmp199 * (tmp35 < tmp18 ? 1 : 0.0);
    const auto tmp201 = tmp131 * tmp130;
    const auto tmp202 = -1 * tmp201;
    const auto tmp203 = 2 + tmp202;
    const auto tmp204 = tmp203 / tmp73;
    const auto tmp205 = tmp82 * tmp204;
    const auto tmp206 = tmp205 + tmp200;
    const auto tmp207 = tmp206 * (tmp36 < tmp12 ? 1 : 0.0);
    const auto tmp208 = tmp139 * tmp138;
    const auto tmp209 = -1 * tmp208;
    const auto tmp210 = 2 + tmp209;
    const auto tmp211 = tmp210 / tmp86;
    const auto tmp212 = tmp95 * tmp211;
    const auto tmp213 = tmp212 + tmp207;
    const auto tmp214 = tmp213 * (tmp37 > tmp6 ? 1 : 0.0);
    const auto tmp215 = tmp100 * tmp183;
    const auto tmp216 = tmp215 + tmp214;
    ((result[ 0 ])[ 0 ])[ 0 ] = tmp102;
    ((result[ 0 ])[ 0 ])[ 1 ] = tmp147;
    ((result[ 0 ])[ 1 ])[ 0 ] = tmp179;
    ((result[ 0 ])[ 1 ])[ 1 ] = tmp216;
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

} // namespace UFLLocalFunctions_42ff56710f3bd510798ecabb32a6cbf0

PYBIND11_MODULE( localfunction_42ff56710f3bd510798ecabb32a6cbf0_af122c1df944c95cd395ec0f91d0f970, module )
{
  typedef UFLLocalFunctions_42ff56710f3bd510798ecabb32a6cbf0::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > > LocalFunctionType;
  if constexpr( LocalFunctionType::gridPartValid )
  {
      auto cls = Dune::Python::insertClass<LocalFunctionType>(module,"UFLLocalFunction",Dune::Python::GenerateTypeName("UFLLocalFunctions_42ff56710f3bd510798ecabb32a6cbf0::UFLLocalFunction< typename Dune::FemPy::GridPart< Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > > > >"), Dune::Python::IncludeFiles({"python/dune/generated/localfunction_42ff56710f3bd510798ecabb32a6cbf0_af122c1df944c95cd395ec0f91d0f970.cc"})).first;
      Dune::FemPy::registerUFLLocalFunction( module, cls );
      cls.def( pybind11::init( [] ( pybind11::object gridView, const std::string &name, int order ) {return new LocalFunctionType( Dune::FemPy::gridPart<Dune::Fem::AdaptiveLeafGridPart< Dune::ALUGrid< 2, 2, Dune::simplex > >>(gridView),name,order); } ), pybind11::keep_alive< 1, 2 >() );
      cls.def_property_readonly( "virtualized", [] ( LocalFunctionType& ) -> bool { return true;});
  }
}

#endif
