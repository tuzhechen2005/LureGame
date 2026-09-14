# Encounter gameplay checkpoint — 2026-09-14

This checkpoint changes the playable fishing loop. It does not establish final
art quality or prove that the full game is enjoyable over repeated sessions.

## Implemented loop

- Lure presentation tracks intentional retrieve speed, pauses, and fresh twitch
  inputs. Fish can follow, hesitate, commit to attack, or escape.
- The bite window varies by fish. Hook timing changes hook security and score.
- A fight alternates telegraphed side runs, dives, headshakes or jumps with
  recovery windows. Reeling, drag and rod direction influence line damage,
  hook loss, exhaustion and distance gained.
- A/D and W/S override mouse offsets while fighting. Releasing a key restores
  mouse control. Shore movement pauses during the fight and landing window.
- Netting requires Space during a four-second window. Missing it resumes the
  fight. The current netting reach is six metres; a visible net animation has
  not yet been authored.
- Catch rewards include skill grade, score, experience, first species and
  per-species personal bests. These persist with the existing local journal.
- Hook, running drag, line strain, escape and trophy sound assets are imported.
  The drag loop remains active at zero volume so it can resume on a run.

## Evidence

Editor Development build succeeded in `Saved/Logs/EncounterBuild3.txt`.
`EncounterTest.log` passed seven encounter-model assertions: blind hard reeling
breaks the line, responsive control can land all four fish archetypes, steady
retrieval alone does not guarantee a bite, and cadence changes can provoke one.

`Encounter-LureSmokeTest.log` passed the actual pawn loop, including a natural
bite, missed bite, timed strike, controlled fight, netting, rewards and line break.
`Encounter-LureInputTest.log` passed movement/observation and the added regression
checks for keyboard priority, radial distance, airborne landing and missed nets.
`Encounter-LureSessionTest.log` passed discovery, personal best, old-save migration
and persistence of the new reward fields.

`EncounterCapture.log` recorded one cast followed by a natural bite, timed strike,
25.31 seconds of fighting and a landed 1.37 kg bass. Nine actual game frames were
captured to `Saved/Encounter-*.png`. Inputs were scripted; this is not a human
playtest or proof of physical mouse-focus behavior. The fixture never injects a
bite or a hooked fish. The capture used 1664 × 936, offscreen rendering and no sound.

## Remaining quality work

The fish mesh, floating trophy presentation, casting/netting animations and
shoreline interaction remain visibly unfinished. The reward economy currently
records experience but has no progression choices. Repeated encounters reuse
the small existing fish population. Audio has numerical/import checks but needs
subjective listening in the running game. More playtesting is needed to evaluate
readability, effort and reward without automated perfect inputs.

The broader request for a compelling, polished fishing game remains active.

## Playable packaged build

`Release/Encounter-20260914/Windows/LureGame.exe` is the current independent
Windows build. Both project and workspace `PlayGame.cmd` launchers now target
it. The former `Release/Windows` version is preserved. The newest existing
player save was copied from the editor project's SaveGames directory into the
new build only because its destination had no player save.

`EncounterPackage.txt` reports BuildCookRun success. The independent executable
passed 57 assertions across encounter model, pawn loop, inputs and persistence;
see `EncounterPackageTests.txt` and `EncounterPackaged-Lure*.log`.
`EncounterPackagedCapture.log` separately passed the rendered natural-bite-to-
trophy scenario in 40.27 seconds, including a 25.32-second fight. Packaged
screenshots are under `Release/Encounter-20260914/Windows/LureGame/Saved`.
The trophy frame was visually inspected: the HUD and assets load, while the fish
shape and unsupported floating presentation still fall short of the art goal.

Executable SHA-256:
`D5FD3138F5154107250E18CD7DD3697B34CD06334DFB554BF0BC5AD60EF74BFF`.
