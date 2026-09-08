import unreal as u
root='/Game/LureArt/'
for name in ['M_Real_Skin','M_Real_Cork','M_Real_Carbon','M_Real_Jacket','M_Real_Metal','M_BassSkin','M_PerchSkin','M_PikeSkin','M_TroutSkin']:
 path=root+name
 if not u.EditorAssetLibrary.does_asset_exist(path):continue
 refs=u.EditorAssetLibrary.find_package_referencers_for_asset(path,True)
 if not refs:print('RETIRED',name,u.EditorAssetLibrary.delete_asset(path))
 else:print('KEPT_REFERENCED',name,refs)
print('DRAFT_CLEANUP_COMPLETE')
