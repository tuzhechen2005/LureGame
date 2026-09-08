import unreal as u
for name in ['SM_Birch','SM_Rock','SM_Grass','SM_CoveTerrain','SM_AnatomicalRight']:
 m=u.load_asset('/Game/LureArt/'+name)
 print('SLOTS',name,[(str(s.material_slot_name),s.material_interface.get_name() if s.material_interface else 'NONE') for s in m.static_materials])
m=u.load_asset('/Game/LureArt/M_Shore')
for n in u.MaterialEditingLibrary.get_material_expressions(m):
 print('SHORE_NODE',n.get_class().get_name(),u.MaterialEditingLibrary.get_material_expression_input_names(n))
print('MATERIAL_AUDIT_COMPLETE')
