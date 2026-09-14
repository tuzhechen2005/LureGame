# Current fishing-arm pipeline

Active sources, in order:

1. `Tools/solve_authored_grasp.py` reads `StandardRodGrip.blend` and writes
   `StandardReeling.blend`. It retains the authored finger articulation, solves
   elbows from joint heads, constrains palm exposure toward the camera, and
   distributes forearm twist. The current solve is recorded in
   `AnatomicalGraspSolve.json`; numerical contact-center accuracy does not prove
   contact between finger skin and equipment.
   `GripArtDirection.json` locks the current placement and explicit hand-roll
   settings so subsequent rebuilding does not run a new pose search. The latest
   user change turns the right hand 20 degrees farther onto its side (-30 to
   -10 degrees); the left remains at -40 degrees.
2. `Tools/rebind_human_to_authored_rig.py` fits the licensed human rest mesh and
   its UVs/weights to semantic Manny joints. It creates weighted sleeves and
   `HumanStandardReeling.blend`.
3. `Tools/export_standard_fishing_rig.py` creates one armature for both hands,
   sleeves, handle and crank. All mesh coordinates share the armature transform.
   Camera/rod marker bones are keyed in armature space to cancel inherited root
   motion. The procedural rod blank remains in C++.
4. `Tools/import_authored_fishing_rig.py` imports through Unreal's legacy FBX
   importer into `/Game/FirstPerson/AuthoredLegacy`, explicitly saves the
   generated skeleton, animation and mesh, and assigns every material slot.
   `SkeletalMaterial` array elements must be written back by index.
5. Build `LureGameEditor`. Normal gameplay now loads this skeletal rig by
   default. `-LureRigReview` records ready/reeling screenshots and verifies that
   the left wrist moves while the right wrist and rod stay steady.

`fit_standard_reeling.py` and earlier `*Study*` files are historical experiments,
not the active build path. Do not rerun them over the current result.

The Unreal render is authoritative for visual acceptance. Hand/finger fit and
wrist shape still need improvement. The current release package has not been
rebuilt. Do not label the project finished or the grasp fully accepted.
