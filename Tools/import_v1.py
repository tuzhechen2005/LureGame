import unreal as u,os
# Mesh/material import is reproducible and only imports missing source assets.
exec(open('D:/LureGame/Tools/import_assets.py',encoding='utf-8-sig').read())
a=u.AssetToolsHelpers.get_asset_tools()
for fn in os.listdir('D:/LureGame/ArtSource/Audio'):
 t=u.AssetImportTask();t.filename='D:/LureGame/ArtSource/Audio/'+fn;t.destination_path='/Game/Audio';t.automated=True;t.replace_existing=True;t.save=True;a.import_asset_tasks([t])
 if fn in ['Ambient.wav','Reel.wav']:
  s=u.load_asset('/Game/Audio/'+fn[:-4]);s.set_editor_property('looping',True);u.EditorAssetLibrary.save_loaded_asset(s)
t=u.AssetImportTask();t.filename='D:/epic/UE_5.8/Engine/Content/Slate/Fonts/DroidSansFallback.ttf';t.destination_path='/Game/UI';t.destination_name='Chinese';t.automated=True;t.save=True;t.factory=u.FontFileFaceFactory();a.import_asset_tasks([t]);print('FONT',t.imported_object_paths)
print('V1_IMPORT_COMPLETE')
