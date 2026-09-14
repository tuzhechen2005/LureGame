"""Run inside Unreal Editor after build_encounter_audio.py has produced the WAVs."""

from pathlib import Path
import unreal


SOURCE = Path(unreal.Paths.project_dir()).resolve() / "ArtSource" / "Audio" / "Encounter"
NAMES = ("HookSet", "DragRun", "LineStrain", "Escape", "Trophy")
DESTINATION = "/Game/Audio"


def main():
    # Validate the complete input set before starting the asset import.
    missing = [str(SOURCE / (name + ".wav")) for name in NAMES
               if not (SOURCE / (name + ".wav")).is_file()]
    if missing:
        raise RuntimeError("Missing encounter audio: " + ", ".join(missing))
    tasks = []
    for name in NAMES:
        task = unreal.AssetImportTask()
        task.set_editor_property("filename", str(SOURCE / (name + ".wav")))
        task.set_editor_property("destination_path", DESTINATION)
        task.set_editor_property("destination_name", name)
        task.set_editor_property("automated", True)
        task.set_editor_property("replace_existing", True)
        task.set_editor_property("save", True)
        tasks.append(task)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    for name, task in zip(NAMES, tasks):
        if not task.get_editor_property("imported_object_paths"):
            raise RuntimeError("Encounter audio import failed: " + name)
        asset_path = DESTINATION + "/" + name
        asset = unreal.load_asset(asset_path)
        if not isinstance(asset, unreal.SoundWave):
            raise RuntimeError("Expected a SoundWave at " + asset_path)
        asset.set_editor_property("looping", name == "DragRun")
        if name == "DragRun":
            asset.set_editor_property("virtualization_mode", unreal.VirtualizationMode.PLAY_WHEN_SILENT)
        if not unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False):
            raise RuntimeError("Could not save encounter audio: " + asset_path)
        unreal.log("ENCOUNTER_AUDIO_IMPORTED " + asset_path + " looping=" + str(name == "DragRun"))
    unreal.log("ENCOUNTER_AUDIO_IMPORT_COMPLETE")


if __name__ == "__main__":
    main()
