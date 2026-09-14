import bpy
from pathlib import Path
root=Path('D:/LureGame/ArtSource/StandardArms')
bpy.ops.wm.open_mainfile(filepath=str(root/'StandardReeling.blend'))
s=bpy.context.scene;s.cycles.samples=6
s.render.resolution_x=720;s.render.resolution_y=480
frames=root/'ReelingPreviewFrames';frames.mkdir(exist_ok=True)
for frame in range(1,49,4):
    s.frame_set(frame);s.render.filepath=str(frames/('%02d.png'%frame));bpy.ops.render.render(write_still=True)
print('REEL_PREVIEW_FRAMES_COMPLETE')
