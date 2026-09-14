# Quality reassessment — 2026-09-11

## Gameplay checkpoint — 2026-09-14

The active work has moved to encounter gameplay at the user's request. Read
`Encounter-20260914.md` for implementation, verification and remaining work.
The right-hand side angle is fixed at the 2026-09-13 setting; do not reopen old
arm experiments as a prerequisite for gameplay work.

## Current state — 2026-09-12

The default gameplay pawn now uses a skeletal first-person rig from
`/Game/FirstPerson/AuthoredLegacy`; the former static arm meshes remain only as
a missing-asset fallback. The visible mesh is the licensed human source fitted
to the authored skeleton, with weighted jacket sleeves and forearm twist.
The right hand is oriented with its back toward the camera; the left follows
the transverse crank. The handle and both arms share the same skeletal asset.
The procedural blank, guides and fishing line follow that rig's rod markers.

The current reproducible pipeline is documented in
`ArtSource/StandardArms/README.md`. Older studies below are historical and must
not overwrite the active sources. Actual standalone-engine evidence is
`Saved/AuthoredRig-Ready.png` and `Saved/AuthoredRig-ReelA/ReelB.png`.
`AuthoredRigRuntime.log` reports an animation pass: left wrist travel 10.899 cm,
right wrist drift 0.01369 cm and rod drift 0.00001 cm over a half cycle. The
runtime camera reference and 210 cm rod length also match the export contract.
These checks establish animation integration, not final visual quality.

Still incomplete: convincing finger-surface contact, refined wrist/cloth shape,
authored casting/recovery animation, physical mouse/focus verification, fish
quality and final scene quality. The existing packaged release remains stale.

Export/import failures corrected in this pass: inherited root transforms on
static equipment markers, mixed mesh object transforms, unsaved generated
skeleton assets, and material-array changes that were not written back by index.
The legacy FBX importer still reports regenerated bind-pose warnings; the
round-trip Blender render and fresh-process Unreal captures are the relevant
evidence for the resulting pose. Do not claim a warning-free import.

Regression verification after the integration: `AuthoredRigInputCheck.log`
records 21 simulated-input passes and zero failures. The smoke scenario now
explicitly aims at the stocked centre of the lake instead of inheriting the
presentation camera yaw. Its full-strength cast lands at approximately
(5520, 0, 0), 156 cm from a fish. `AuthoredRigSmokeCheck.log` records ten passes
through cast, natural AI pursuit/bite, missed bite, strike, landing, reset and
line break. No bite/fight state is injected for the natural-bite assertions.
This controlled scenario does not establish bite frequency at arbitrary spots.

## Decision

Input consistency fix: MoveForward/MoveRight now block motion during the existing fixed-camera observation mode. RunInputTest covers V enter/exit, W/S/A/D suppression/restoration and mouse yaw/pitch plus camera restoration. ObserveInputCheck.log records 21 PASS and zero failures; Editor build succeeded. This remains simulated input and does not prove physical Windows mouse capture/focus.

Standard reeling study: preserved the authored right grip; mirrored its skeletal deformation for the left grasp and solved both elbows from shoulder/elbow/wrist joint heads (FBX display-bone tails do not identify anatomical joints). The first placement exceeded reach by up to 12 cm; lifting equipment 20 cm and moving it 4 cm toward the body removed the unreachable condition. StandardReeling.blend contains 49 keyed frames; playback contact-center error is below 0.002 mm. This measures a fitted grip center, not fingertip contact. Twelve-frame continuous preview is StandardReelingPreview.gif. Still requires closer finger/knob fit, realistic replacement geometry and actual Unreal integration. No final grip acceptance is asserted.

Standard grasp replacement: exported the official MF_Pistol_Idle_ADS animation and bound it to the same Manny skeleton in Blender. Removed only animation object-transform tracks because they applied an extra FBX unit conversion; retained pose-bone tracks and source object transform. Side render OfficialGrasp_Side.png shows an intact authored wrist/forearm relationship. `fit_standard_rod_grip.py` rotates the entire arm at its shoulder, retains the authored finger pose, and fits a rod cylinder to the right grasp. StandardRodGrip.blend is an isolated arms-only study. StandardRodGrip_Side.png shows improved right grip continuity, but the left hand still uses the unsupported pistol support pose and must be replaced. No gameplay arm replacement or final visual acceptance is claimed.

Independent axis audit found no mirrored FBX conversion: reimported RodHandle has identity world transform, long rear grip -25 to -6 cm, fore grip +9 to +18 cm. C++ rod blank starts at +18 cm. The previous speculation that the whole equipment axis was reversed is unsupported and must not guide further edits.

Ripple update: `refine_lake_ripples.py` replaces the periodic three-wave normal with eight dispersed directions and disables under-resolved fine WPO on the lake grid. Actual screenshot LakeRipples-Actual-20260912.png shows the large parallel bands removed and more coherent tree reflections. Prior water state is saved as M_LakeWater_PreRippleSpectrum. The capture was deliberately stopped after obtaining the required lake evidence; this was not a complete gameplay or performance run. Wind/weather scaling and temporal shimmer remain unverified.

Water update: `use_single_layer_lake.py` switches M_LakeWater to opaque Single Layer Water, supplies absorption/scattering coefficients and preserves the ripple normal. Prior material is retained as M_LakeWater_PreSingleLayer. Actual runtime capture SingleLayerLake-Actual-20260912.png shows blue-green water and visible shoreline/tree reflection, but repetitive parallel ripples remain. Full capture process exited successfully. This is a water shading improvement only; rejected static game arms and pale vegetation are still plainly visible.

Imported the installed Epic High/Characters template resources to Content/Characters with their original package paths. `inspect_standard_hand_rig.py` successfully loaded SK_Mannequin (a Skeleton, despite its filename) and CR_Mannequin_Body, verified both arm chains, and recorded finger bones/control names in StandardRigInspection.json. Inspection exited with zero errors/warnings. This establishes available standard rig controls, not an accepted fishing pose. Existing pawn remains unchanged by this template import.

The equipment-height/elbow-plane sweep (`solve_grip_reach.py`) also failed: at +0.22 m the measured bends remain about 59 degrees right and 101 degrees left. `GripReach_FirstPerson.png` is rejected. Stop tuning this custom MakeHuman palm-frame rig. Inspect the locally installed Unreal first-person template and its standard skeleton/control rig as the replacement foundation; do not confuse a mannequin with the required final realistic skin/clothing.

2026-09-12: inspected the actual Deckee reference photo locally (GripReference-Deckee.jpg), not just search captions. The side-grip replacement was rendered from first-person, side and front views in SideGripOrientationStudy.blend. SideGrip_Side.png exposes severe wrist flexion; SideGrip_Front.png shows an unclosed left grip. This attempt also fails. Do not export it or spend further work on finger details until forearm-to-palm alignment is solved together with equipment placement.

Photo source: https://community.deckee.com/topic/94302-article-effective-casting-with-spinning-outfits/ . The downloaded photograph is a visual reference only, not licensed game artwork or a distributable asset.

User rejected both hands as reverse grips after the pinch study. All previous grip poses are rejected, including PinchFitStudy. Do not build further detail on their palm orientation or reuse their arbitrary grip offsets as an anatomical reference.

Reference: Shimano's beginner rod guide, https://fish.shimano.com/ja-JP/content/beginners/fishingtackle/rod/index.html (section ロッドの持ち方), illustrates holding the reel foot between fingers. This validates a contact relationship, not the existing rig's orientation. Obtain and inspect the visual reference before another orientation change.

The current first-person arms fail visual acceptance. Stop polishing the static-mesh arm implementation and stop full-cove captures for arm adjustments. Do not describe the skeletal study as a finished replacement.

## Evidence

- The game still uses static-mesh arms. The weighted skeletal mesh and reel animation are isolated studies, not an integrated gameplay solution.
- `ArtSource/RiggedArms/AnatomicalChainReview.png` shows excessive wrist flexion, uncertain finger contact, and ragged shoulder cuts. Successful IK endpoint tests do not validate anatomy or a convincing grip.
- `ArtSource/RiggedArms/AnatomicalChainCheckpoint.blend` preserves the live study and auxiliary-bone IK locks without overwriting the user's Blender file.
- Lighting and shader changes have not brought the actual scene close to the concept. The existing packaged release does not represent the latest work.

## Replacement workflow

1. Establish a fixed first-person camera and correctly scaled rod/reel. Fit the right palm to the handle and left fingers to the crank knob before solving the arms. Derive elbow placement and forearm rotation from these contacts; do not force wrist rotations independently of arm anatomy.
2. Validate one neutral grip in plain lighting from first-person and side views. Require a plausible wrist, opposed thumb, and no obvious intersection. Freeze lighting during this work.
3. Validate one full reel rotation and a cast/recovery motion. Hands must maintain intended contact, elbows must bend naturally, and the mesh must not collapse. Only then create weighted sleeves and final materials.
4. Integrate the accepted skeletal asset and animations into Unreal. Capture the actual gameplay camera; Blender renders alone cannot pass the milestone.
5. Resume water, fish, and scene work only after the arm milestone. Keep separate acceptance evidence for each system.

## Stop rules

- After two failed visual attempts at the same defect, stop parameter tweaking and inspect the underlying rig, coordinate frames, weights, or source asset.
- Do not equate build success, import success, endpoint precision, or animation duration with visual quality.
- Do not regenerate concept art, run full-scene captures, or rebuild unrelated materials to diagnose hand contact.
- If the source rig cannot produce an acceptable neutral grip within a bounded pass, report that limitation and evaluate a purpose-built first-person arm asset with verified usage rights instead of extending the procedural workaround indefinitely.

## Next accepted deliverable

One convincing first-person neutral grip, plus a short full-crank animation using the same rig and equipment. No claim of final game quality until these are visibly correct in Unreal.

## Weighted clothing

`Tools/build_weighted_sleeves.py` builds two sleeves from the rest-pose arm mesh, preserving interpolated bone weights at the wrist cut. Each has 473 weighted vertices, a 1.5 mm cloth shell and a closed shoulder boundary. `WeightedSleeveStudy.blend` contains the result. First-person quarter-cycle captures are `SleevedGrip_01/13/25/37.png`; frames 1 and 25 were visually inspected. Sleeves follow the arms in these poses, but their folds are still simple, hands remain clay-shaded, and the grip is not accepted. This is an isolated asset study, not an updated packaged game.

## Rig diagnosis and saved experiments

- Measured frame 1 before correction: right forearm-to-middle-finger-base direction 44 degrees, left 107.9 degrees. The left elbow folded toward the wrong side.
- Adjusting IK pole angles to R 30 / L 150 degrees brings the left angle to 52.8 degrees. This alone does not solve the grip (`ElbowPlaneStudy.blend`).
- Rotating each wrist toward its evaluated forearm direction leaves a 20-degree angle in the neutral-pose experiment (`NeutralWristStudy.blend`, `NeutralWristReview.png`). Twenty degrees is an experiment setting, not an anatomical acceptance standard.
- Visual inspection shows reduced wrist folding but displaced finger contact. The current hand controls constrain wrist position, not the actual palm/knob contact point. Next implementation must preserve equipment contact while solving wrist placement and orientation together. Do not export this pose as an accepted gameplay animation.
- `Tools/solve_arm_contacts.py` now derives wrist targets from equipment anchors and local grip offsets over 49 frames. `ContactAnchorStudy.blend` saves this experiment. Numerical anchor error is below 0.001 mm; this does not verify finger-surface contact.
- Fixed a scene-evaluation error discovered when quarter-cycle images were identical: updating the active default scene's view layer reset shared objects to its frame. The solver now updates the review scene's own view layer. Left wrist positions at frames 1/13/25/37 are distinct and follow the crank.
- `GripFirstPerson_01/13/25/37.png` use an isolated eye camera. Grip shape and thumb opposition remain visually inadequate; do not accept or integrate this animation yet.
- Rendering shared objects also requires the review scene to be the window's active scene during capture, restored afterward. Corrected quarter-cycle captures exposed an invalid crank axis: the original crank rotated around the rod's longitudinal X axis.
- `correct_study_crank_axis.py` moves the lever into XZ and animates local Y, the transverse spindle direction. The knob's world X now stays at 0.048 m throughout the cycle instead of crossing the rod. `TransverseCrankStudy.blend` and `TransverseCrank_01/13/25/37.png` preserve the result. The half-cycle image no longer shows the left arm crossing over the right, but hand contact and the unfinished spindle geometry still fail final acceptance. Unreal crank geometry and animation must be updated together when the replacement asset is ready.
- Built a connected spindle, lever, knob axle and round grip with `build_transverse_crank.py`, exported as `SM_ReelCrank_Transverse.fbx`, and imported successfully into Unreal (see `ImportTransverseCrank.log`). `LureWorld.cpp` now selects this mesh, rotates around Y using Pitch, and calculates the knob position at local `(4.485,-7,-3.1)` cm. The Y sign follows the existing FBX import convention. This corrects the mechanical axis in the game source; it does not replace the static arms or establish in-game visual acceptance.
