import unreal as u

world = u.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Cove')
sub = u.get_editor_subsystem(u.EditorActorSubsystem)
count = 0
for actor in sub.get_all_level_actors():
    if not isinstance(actor, u.PostProcessVolume):
        continue
    settings = actor.get_editor_property('settings')
    settings.set_editor_property('override_lumen_front_layer_translucency_reflections', True)
    settings.set_editor_property('lumen_front_layer_translucency_reflections', True)
    actor.set_editor_property('settings', settings)
    count += 1
assert count > 0
assert u.EditorLoadingAndSavingUtils.save_map(world, '/Game/Maps/Cove')
print('COVE_REFLECTIONS_ENABLED', count)
