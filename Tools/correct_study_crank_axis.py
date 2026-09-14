"""Correct only the isolated Blender crank study; game assets are unchanged."""
import bpy
import math
from mathutils import Quaternion

scene = bpy.data.scenes['RiggedArmsReview']
crank = bpy.data.objects['RigStudyCrank']
# The old mesh's lever lay in YZ and rotated around the rod's X axis.
# Move the lever into XZ, outboard along the transverse spindle (Y).
# This is a geometry study, not a finished axle/knob assembly.
if not crank.get('transverse_axis_corrected'):
    crank.data = crank.data.copy()
    for vertex in crank.data.vertices:
        x, y, z = vertex.co
        vertex.co = (y * .65, .07 + x, z)
    crank['transverse_axis_corrected'] = True

base = Quaternion((0, 0, 1), -math.pi / 2)
for frame in range(1, 50):
    crank.rotation_quaternion = base @ Quaternion((0, 1, 0),
                                                  2 * math.pi * (frame - 1) / 48)
    crank.keyframe_insert(data_path='rotation_quaternion', frame=frame)
scene.frame_set(1)
scene.view_layers[0].update()
