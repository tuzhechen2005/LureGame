import unreal as u
a=u.AssetToolsHelpers.get_asset_tools();t=u.AssetImportTask();t.filename='D:/epic/UE_5.8/Engine/Content/Slate/Fonts/DroidSansFallback.ttf';t.destination_path='/Game/UI';t.destination_name='Chinese';t.automated=True;t.save=True;t.factory=u.FontFileImportFactory();a.import_asset_tasks([t]);print('FONT_IMPORTED',t.imported_object_paths)
