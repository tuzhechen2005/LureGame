import unreal as u
mesh = u.load_asset('/Game/FirstPerson/SK_FishingArms')
c = u.new_object(u.SkeletalMeshComponent)
c.set_skeletal_mesh_asset(mesh)
names = [str(c.get_bone_name(i)) for i in range(c.get_num_bones())]
for name in ['wrist_R', 'wrist_L', 'lowerarm01_R', 'lowerarm01_L']:
    assert name in names, name
print('ARM_SKELETON_VERIFIED', c.get_num_bones(), mesh.get_path_name())
