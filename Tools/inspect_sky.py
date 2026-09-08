import unreal as u
m=u.load_asset('/Engine/EngineSky/M_Sky_Panning_Clouds2');print('SKY_SCALARS',u.MaterialEditingLibrary.get_scalar_parameter_names(m));print('SKY_VECTORS',u.MaterialEditingLibrary.get_vector_parameter_names(m))
