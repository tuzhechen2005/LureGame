import bpy,os,json,pathlib
root=pathlib.Path('D:/LureGame/ArtSource');out=root/'Realistic';manifest=json.loads((out/'manifest.json').read_text())
groups={
 'rock_moss_set_01':('rock_moss_set_01','rock_moss_set_01'),
 'tree_small_02_branches':('tree_small_02','tree_small_02_branch'),
 'tree_small_02_leaves':('tree_small_02','tree_small_02_leaves'),
 'tree_small_02_trunk':('tree_small_02','tree_small_02'),
 'grass_medium_01':('grass_medium_01','grass_medium_01')}
for mat,(asset,prefix) in groups.items():
 maps={}
 for kind,suffix in [('diff','diff'),('rough','rough'),('normal','nor_gl'),('alpha','alpha')]:
  files=list((root/'Nature'/asset/'textures').glob(prefix+'_'+suffix+'_2k.*'))
  if not files:continue
  file=files[0];im=bpy.data.images.load(str(file),check_existing=False)
  if kind!='diff':im.colorspace_settings.name='Non-Color'
  print('LOADING',file,tuple(im.size),len(im.pixels),flush=True)
  _=im.pixels[0]
  im.filepath_raw=str(out/(file.stem+'.png'));im.file_format='PNG';im.save();maps[kind]=file.stem
 manifest[mat]=maps
(out/'manifest.json').write_text(json.dumps(manifest,indent=2));print('SCAN_TEXTURES_CONVERTED')
