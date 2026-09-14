import unreal as u
path='/Game/FirstPerson/AuthoredLegacy/'
mesh=u.load_asset(path+'SK_AuthoredFishingRig');animation=u.load_asset(path+'A_AuthoredReel')
skeleton=mesh.get_editor_property('skeleton')
assert skeleton and animation.get_editor_property('skeleton')==skeleton
mapping={'OliveJacket':'M_PBR_Jacket','AnatomicalSkin':'M_AnatomicalSkin','Metal_001':'M_PBR_Metal',
         'Rubber':'Rubber','Cork':'M_PBR_Cork','Carbon':'M_PBR_Carbon','Gold':'Gold','Metal':'M_PBR_Metal','BassBelly':'BassBelly'}
slots=mesh.get_editor_property('materials')
for i,slot in enumerate(slots):
    name=str(slot.material_slot_name);material=u.load_asset('/Game/LureArt/'+mapping[name]);assert material,name
    if isinstance(material,u.Material):
        material.set_editor_property('used_with_skeletal_mesh',True)
        u.MaterialEditingLibrary.recompile_material(material);u.EditorAssetLibrary.save_loaded_asset(material)
    slot.material_interface=material;slots[i]=slot
mesh.set_editor_property('materials',slots)
assert u.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
for slot in mesh.get_editor_property('materials'):
    assert slot.material_interface,str(slot.material_slot_name)
    print('RIG_MATERIAL',slot.material_slot_name,slot.material_interface.get_path_name())
print('RIG_ASSET_FINALIZE_PASS',skeleton.get_path_name(),animation.get_play_length())
