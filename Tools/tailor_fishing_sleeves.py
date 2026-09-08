import bpy,bmesh,math
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='D:/LureGame/ArtSource/Anatomical/FishingHands.blend')
cloth=bpy.data.materials.new('OliveJacket');cloth.use_nodes=True;p=next(n for n in cloth.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(.065,.083,.043,1);p.inputs['Roughness'].default_value=.86
for name,mirror in [('SM_AnatomicalRight',1),('SM_AnatomicalLeft',-1)]:
 hand=bpy.data.objects[name];sleeve=hand.copy();sleeve.data=hand.data.copy();bpy.context.scene.collection.objects.link(sleeve);sleeve.name='Sleeve';wrist=Vector((-.025,.080*mirror,-.012));axis=(Vector((-.42,.15*mirror,-.25))-wrist).normalized()
 bm=bmesh.new();bm.from_mesh(sleeve.data)
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=wrist+axis*.065,plane_no=axis,clear_inner=True,clear_outer=False,dist=.00001)
 for v in bm.verts:
  q=v.co-wrist;t=q.dot(axis);rad=q-axis*t
  if rad.length>.0001:
   theta=math.atan2(rad.y,rad.z);fold=.0035*math.sin(t*145+theta*2)*(.4+.6*math.sin(t*25)**2)
   v.co+=rad.normalized()*(.004+fold)
 bm.to_mesh(sleeve.data);bm.free();sleeve.data.materials.clear();sleeve.data.materials.append(cloth)
 for poly in sleeve.data.polygons:poly.material_index=0;poly.use_smooth=True
 bpy.ops.object.select_all(action='DESELECT');sleeve.select_set(True);bpy.context.view_layer.objects.active=sleeve
 mod=sleeve.modifiers.new('Cloth thickness','SOLIDIFY');mod.thickness=.0015
 hand.select_set(True);bpy.context.view_layer.objects.active=hand
 bpy.ops.export_scene.fbx(filepath='D:/LureGame/ArtSource/Anatomical/'+name+'.fbx',use_selection=True,object_types={'MESH'},axis_forward='Y',axis_up='Z',mesh_smooth_type='FACE')
bpy.ops.wm.save_as_mainfile(filepath='D:/LureGame/ArtSource/Anatomical/FishingHandsWithSleeves.blend')
print('TAILORED_HANDS_COMPLETE')
