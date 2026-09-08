import json
from pathlib import Path
p=Path('D:/LureGame/ArtSource/HumanBase');v=[list(map(float,l.split()[1:4])) for l in (p/'base.obj').read_text(encoding='utf-8').splitlines() if l.startswith('v ')]
s=json.loads((p/'default.mhskel').read_text(encoding='utf-8'));
for name in ['lowerarm01.R','lowerarm02.R','wrist.R','finger1-1.R','finger2-1.R','finger2-3.R','finger5-1.R']:
 b=s['bones'][name]
 print(name,[(key,[round(sum(v[i][k] for i in s['joints'][b[key]])/len(s['joints'][b[key]]),3) for k in range(3)]) for key in ['head','tail']])

