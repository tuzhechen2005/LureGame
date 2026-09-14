from PIL import Image
from pathlib import Path
root=Path('D:/LureGame/ArtSource/StandardArms')
frames=[Image.open(path).convert('RGB') for path in sorted((root/'ReelingPreviewFrames').glob('*.png'))]
assert len(frames)==12
frames[0].save(root/'StandardReelingPreview.gif',save_all=True,append_images=frames[1:],duration=167,loop=0)
print(root/'StandardReelingPreview.gif')
