import unreal as u
lib=u.MaterialEditingLibrary;m=u.load_asset('/Game/LureArt/M_LakeWater')
for n in lib.get_material_expressions(m):
 if isinstance(n,u.MaterialExpressionCustom):
  code=n.get_editor_property('code')
  if 'normalize' in code:
   code=code.replace('0.11','0.035').replace('0.10','0.031').replace('0.07','0.026').replace('0.08','0.027').replace('0.025','0.009').replace('0.035','0.012')
   n.set_editor_property('code',code)
rough=lib.create_material_expression(m,u.MaterialExpressionConstant,0,0);rough.set_editor_property('r',.24);lib.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
color=lib.create_material_expression(m,u.MaterialExpressionConstant3Vector,0,0);color.set_editor_property('constant',u.LinearColor(.015,.055,.039,1));lib.connect_material_property(color,'',u.MaterialProperty.MP_BASE_COLOR)
p=lib.create_material_expression(m,u.MaterialExpressionWorldPosition,0,0);c=lib.create_material_expression(m,u.MaterialExpressionCameraPositionWS,0,0);f=lib.create_material_expression(m,u.MaterialExpressionFresnel,0,0)
alpha=lib.create_material_expression(m,u.MaterialExpressionCustom,0,0);alpha.set_editor_property('code','if(C.z<0) return .985; return lerp(.58,.96,saturate(length(C-P)/2200.))*(.92+.08*F);');alpha.set_editor_property('output_type',u.CustomMaterialOutputType.CMOT_FLOAT1)
inputs=[]
for name,src in [('P',p),('C',c),('F',f)]:
 a=u.CustomInput();a.set_editor_property('input_name',name);inputs.append(a)
alpha.set_editor_property('inputs',inputs)
for name,src in [('P',p),('C',c),('F',f)]:assert lib.connect_material_expressions(src,'',alpha,name)
lib.connect_material_property(alpha,'',u.MaterialProperty.MP_OPACITY);lib.recompile_material(m);u.EditorAssetLibrary.save_loaded_asset(m);print('COVE_WATER_REFINED')
