import json, pathlib, urllib.request, concurrent.futures, hashlib
ROOT=pathlib.Path('D:/LureGame/ArtSource')
jobs=[]
for asset,res in [('rock_moss_set_01','2k'),('tree_small_02','2k'),('grass_medium_01','2k')]:
 data=json.loads((ROOT/(asset+'.json')).read_text(encoding='utf-8-sig'))
 info=data['blend'][res]['blend']; dest=ROOT/'Nature'/asset
 jobs.append((info,dest/(asset+'.blend')))
 for path,item in info.get('include',{}).items():jobs.append((item,dest/path))
def fetch(job):
 info,path=job;path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists() and hashlib.md5(path.read_bytes()).hexdigest()==info['md5']:return
 req=urllib.request.Request(info['url'],headers={'User-Agent':'Wildwater-local-art-production/1.0'})
 with urllib.request.urlopen(req,timeout=120) as r,path.open('wb') as out:
  while chunk:=r.read(1024*1024):out.write(chunk)
 assert hashlib.md5(path.read_bytes()).hexdigest()==info['md5'],path
 print('DOWNLOADED',path.name,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(fetch,jobs))
