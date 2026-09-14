import unreal as u
from pathlib import Path
out=Path('D:/LureGame/ArtSource/StandardArms')
animation=u.load_asset('/Game/Characters/Mannequins/Anims/Pistol/MF_Pistol_Idle_ADS')
assert isinstance(animation,u.AnimSequence)
task=u.AssetExportTask();task.object=animation
task.filename=str(out/'PistolGraspReference.fbx');task.automated=True
task.prompt=False;task.replace_identical=True;task.options=u.FbxExportOption()
assert u.Exporter.run_asset_export_task(task)
print('GRASP_REFERENCE_EXPORTED',animation.get_play_length())
