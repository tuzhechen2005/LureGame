from pathlib import Path
p=Path('D:/LureGame/Tools/import_assets.py');s=p.read_text(encoding='utf-8-sig');s=s.replace("lerp.set_editor_property('const_a',.28)","lerp.set_editor_property('const_a',.64)")
s=s.replace('-0.23*cos(a)-0.12*cos(b)-0.045*cos(c)','-0.11*cos(a)-0.07*cos(b)-0.025*cos(c)').replace('-0.19*cos(a)+0.14*cos(b)-0.055*cos(c)','-0.10*cos(a)+0.08*cos(b)-0.035*cos(c)')
s=s.replace('float a=sin(P.x*.007+sin(P.y*.012))*sin(P.y*.009);float b=sin(P.x*.19)*sin(P.y*.24);return lerp(float3(.08,.095,.04),float3(.22,.19,.105),saturate(.5+a*.32+b*.09));', '''struct FN{float h(float2 p){return frac(sin(dot(p,float2(127.1,311.7)))*43758.5453);}float n(float2 p){float2 i=floor(p),f=frac(p);f=f*f*(3-2*f);return lerp(lerp(h(i),h(i+float2(1,0)),f.x),lerp(h(i+float2(0,1)),h(i+1),f.x),f.y);}};FN g;float v=g.n(P.xy*.015)*.65+g.n(P.xy*.13)*.25+g.n(P.xy*.65)*.1;return lerp(float3(.07,.078,.031),float3(.20,.16,.083),v);''')
p.write_text(s,encoding='utf-8')
