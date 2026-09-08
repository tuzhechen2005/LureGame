import bpy
for a in ['rock_moss_set_01','tree_small_02','grass_medium_01']:
 bpy.ops.wm.open_mainfile(filepath='D:/LureGame/ArtSource/Nature/'+a+'/'+a+'.blend')
 print('ASSET',a)
 for o in bpy.data.objects:
  if o.type=='MESH':print('MESH',o.name,len(o.data.vertices),tuple(o.dimensions),[m.name if m else '-' for m in o.data.materials],[(m.name,m.type) for m in o.modifiers])
 for m in bpy.data.materials:
  if m.use_nodes:print('MAT',m.name,[(n.name,n.image.filepath if n.image else '') for n in m.node_tree.nodes if n.type=='TEX_IMAGE'])
