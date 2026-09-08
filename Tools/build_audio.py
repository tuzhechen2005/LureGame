import wave, math, random, struct
from pathlib import Path
random.seed(321);out=Path('D:/LureGame/ArtSource/Audio');out.mkdir(exist_ok=True)
def make(name,duration,fn):
 rate=22050;data=bytearray();low=0
 for i in range(int(duration*rate)):
  t=i/rate;noise=random.uniform(-1,1);low=.97*low+.03*noise;x=fn(t,noise,low,duration)
  data+=struct.pack('<h',int(max(-.95,min(.95,x))*32767))
 with wave.open(str(out/(name+'.wav')),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(data)
make('Ambient',24,lambda t,n,l,d: l*.7*(.65+.2*math.sin(t*.8))+n*.015+(.07*math.sin(2*math.pi*(2300*t+50*math.sin(t*24)))*math.exp(-((t%7-2)/.12)**2)))
make('Cast',.6,lambda t,n,l,d:n*.3*math.sin(math.pi*t/d)**2)
make('Splash',.8,lambda t,n,l,d:(n*.22+l*.9)*math.exp(-t*6)+math.sin(t*1500*math.exp(-t*3))*.09*math.exp(-t*8))
make('Bite',.22,lambda t,n,l,d:math.sin(t*2*math.pi*(1100-t*1700))*.3*math.exp(-t*18))
make('Reel',.5,lambda t,n,l,d: (n*.08+math.sin(t*2*math.pi*180)*.03)*(0.5+.5*math.sin(t*2*math.pi*28)))
make('Catch',1,lambda t,n,l,d:sum(math.sin(2*math.pi*f*t)*.055 for f in [523.25,659.25,783.99])*min(1,t*20)*math.exp(-t*3))
print('AUDIO_COMPLETE')
