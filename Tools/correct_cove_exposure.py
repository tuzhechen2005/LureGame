import unreal as u
world=u.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Cove')
sub=u.get_editor_subsystem(u.EditorActorSubsystem)
for a in sub.get_all_level_actors():
 if isinstance(a,u.PostProcessVolume):
  s=a.get_editor_property('settings')
  for k,v in [('override_auto_exposure_min_brightness',True),('override_auto_exposure_max_brightness',True),('auto_exposure_min_brightness',-4.),('auto_exposure_max_brightness',20.),('override_auto_exposure_speed_up',True),('override_auto_exposure_speed_down',True),('auto_exposure_speed_up',5.),('auto_exposure_speed_down',5.)]:s.set_editor_property(k,v)
  a.set_editor_property('settings',s)
u.EditorLoadingAndSavingUtils.save_map(world,'/Game/Maps/Cove');print('COVE_EXPOSURE_CORRECTED')
