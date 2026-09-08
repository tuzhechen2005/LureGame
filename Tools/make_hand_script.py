from pathlib import Path
s=Path('D:/LureGame/Tools/build_realistic.py').read_text(encoding='utf-8')
head=s[:s.index("for asset in ['rock_moss_set_01'")]
body=s[s.index("bpy.ops.wm.open_mainfile(filepath=ROOT+'/LureAssets.blend')"):]
body=body.replace('for p in skin.data.polygons:p.use_smooth=True',"skin.data.materials.clear();skin.data.materials.append(bpy.data.materials['Skin'])\n for p in skin.data.polygons:p.use_smooth=True;p.material_index=0")
head=head.replace('manifest={}',"manifest=json.load(open(OUT+'/manifest.json'))")
Path('D:/LureGame/Tools/refine_hands.py').write_text(head+body,encoding='utf-8')
