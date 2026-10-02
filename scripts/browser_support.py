"""Shared browser capture helpers; outputs belong in ignored artifacts/."""
import os
from PIL import Image, ImageDraw
EDGE = os.environ.get("HERO_BROWSER", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
def contact(pairs, destination, width=720):
    height = round(pairs[0][1].height / pairs[0][1].width * width)
    image = Image.new("RGB", (width * 2, (height + 26) * ((len(pairs) + 1) // 2)), (22, 24, 29))
    pen = ImageDraw.Draw(image)
    for i, (label, frame) in enumerate(pairs):
        x, y = i % 2 * width, i // 2 * (height + 26)
        pen.text((x + 8, y + 6), label, fill="white")
        image.paste(frame.resize((width, height)), (x, y + 26))
    image.save(destination, quality=92)

