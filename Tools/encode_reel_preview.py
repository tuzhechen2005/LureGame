from pathlib import Path
from PIL import Image

root = Path('D:/LureGame/ArtSource/RiggedArms')
files = sorted((root / 'ReelFrames').glob('frame_*.png'))
assert len(files) == 48, len(files)
frames = [Image.open(path).convert('RGB') for path in files]
frames[0].save(root / 'ReelStudy.gif', save_all=True, append_images=frames[1:],
               duration=42, loop=0, optimize=False)
print('REEL_PREVIEW_ENCODED', len(frames))
