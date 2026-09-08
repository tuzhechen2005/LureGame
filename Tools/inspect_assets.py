import unreal as u
for n in ['SM_WaterGrid','SM_RightArm','SM_RodHandle']:
 a=u.load_asset('/Game/LureArt/'+n);print('ORIGIN',n,a.get_bounds().origin)
