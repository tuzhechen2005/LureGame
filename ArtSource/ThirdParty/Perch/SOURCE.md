# Fish Perch — holmen

Author source: https://blendswap.com/blend/8888
License: CC0 1.0 (public domain); original archive license is in BLENDSWAP_LICENSE.txt.
Pinned redistribution: https://github.com/frankiezafe/Fish-shader/blob/6a1c64975cd266a00797199dd7aca9ec4af72348/addons/fish-shader/assets/67777_Fish_Perch.zip

The original .blend is preserved. Prepared copies were opened with --disable-autoexec; no source scripts executed.
The original fish, inner eyes and outer eyes are preserved in the static exports; rig/lattice/mirror evaluation is baked in rest pose.
Full fish length is 40 cm, mouth +X, dorsal fin +Z. See perch_metadata.json for tail pivot, bounds and slots.
Legacy Cycles shaders were replaced with simplified PBR; source packed image pixels are retained.
The old image named normal was used as displacement in the original graph; an OpenGL normal is derived from its luminance.
The source rig is not exported; tail movement is a separate static mesh pivot.

Run: D:/blender.exe --background --disable-autoexec "D:/LureGame/ArtSource/ThirdParty/Perch/Fish Perch.blend" --python D:/LureGame/Tools/prepare_perch.py -- prepare
Unreal import script is Tools/import_perch.py; it is not run by this preparation task.
