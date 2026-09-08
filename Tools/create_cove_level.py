import unreal as u,json
root='/Game/LureArt';at=u.AssetToolsHelpers.get_asset_tools()
t=u.AssetImportTask();t.filename='D:/LureGame/ArtSource/Cove/SM_CoveTerrain.fbx';t.destination_path=root;t.automated=True;t.replace_existing=True;t.save=True
opts=u.FbxImportUI();opts.import_mesh=True;opts.import_materials=False;opts.import_textures=False;opts.static_mesh_import_data.combine_meshes=True;t.options=opts;at.import_asset_tasks([t])
world=u.EditorLoadingAndSavingUtils.new_blank_map(False)
sub=u.get_editor_subsystem(u.EditorActorSubsystem)
cls=u.load_class(None,'/Script/LureGame.CoveEnvironment')
env=sub.spawn_actor_from_class(cls,u.Vector(0,0,0));env.set_actor_label('Cove — Blender authored environment')
env.get_editor_property('terrain').set_static_mesh(u.load_asset(root+'/SM_CoveTerrain'))
groups={c.get_name():c for c in env.get_editor_property('groups')}
for c in groups.values():c.clear_instances()
data=json.load(open('D:/LureGame/ArtSource/Cove/placements.json'))
for item in data:
 if item['asset'] not in groups:continue
 tr=u.Transform(location=u.Vector(*item['location']),rotation=u.Rotator(*item['rotation']),scale=u.Vector(*item['scale']))
 groups[item['asset']].add_instance(tr,False)
print('PLACEMENT_COUNTS',[(n,c.get_instance_count()) for n,c in groups.items()])
sun=sub.spawn_actor_from_class(u.DirectionalLight,u.Vector(0,0,2000),u.Rotator(-24,-95,0));sun.set_actor_label('Sun')
lc=sun.get_component_by_class(u.DirectionalLightComponent);lc.set_mobility(u.ComponentMobility.MOVABLE);lc.set_intensity(30000);lc.set_atmosphere_sun_light(True)
sky=sub.spawn_actor_from_class(u.SkyAtmosphere,u.Vector(0,0,0));sky.set_actor_label('Physical atmosphere')
fill=sub.spawn_actor_from_class(u.SkyLight,u.Vector(0,0,0));sc=fill.get_component_by_class(u.SkyLightComponent);sc.set_mobility(u.ComponentMobility.MOVABLE);sc.set_intensity(1);sc.set_editor_property('real_time_capture',True)
fog=sub.spawn_actor_from_class(u.ExponentialHeightFog,u.Vector(0,0,-50));fc=fog.get_component_by_class(u.ExponentialHeightFogComponent);fc.set_fog_density(.004);fc.set_fog_height_falloff(.2)
post=sub.spawn_actor_from_class(u.PostProcessVolume,u.Vector(0,0,0));post.set_editor_property('unbound',True)
settings=post.get_editor_property('settings');settings.set_editor_property('override_auto_exposure_bias',True);settings.set_editor_property('auto_exposure_bias',-.3);settings.set_editor_property('override_motion_blur_amount',True);settings.set_editor_property('motion_blur_amount',0);post.set_editor_property('settings',settings)
u.EditorLoadingAndSavingUtils.save_map(world,'/Game/Maps/Cove')
print('COVE_LEVEL_SAVED')
