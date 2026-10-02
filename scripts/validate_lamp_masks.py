from pathlib import Path
import numpy as np
from PIL import Image
SIZE = (2048, 1033)
TIMES = (990, 1050, 1080, 1110, 1200, 1320, 0, 300, 330, 360, 390, 720)
ROOT = Path(__file__).resolve().parents[1]
for mask_name in ("lamp-source-mask.png", "lamp-influence-mask.png"):
    registered = np.asarray(Image.open(ROOT / "public/assets/hero/lighting" / mask_name).convert("RGBA"))
    assert registered.shape == (941, 1672, 4)
    assert not np.any(registered[:, 390:, :2]) and not np.any(registered[548:, :, :2]), "Lamp mask escaped corridor"

# At a horizontal cut through each lantern the source must resolve into three
# separate panes, leaving the dark metal mullions unlit.
source = np.asarray(Image.open(ROOT / "public/assets/hero/lighting/lamp-source-mask.png"))
for channel, row, left, right in ((0, 150, 30, 68), (1, 260, 142, 172)):
    lit = source[row, left:right, channel] > 128
    runs = np.diff(np.r_[False, lit, False].astype(np.int8))
    assert np.count_nonzero(runs == 1) == 3, "Each lamp needs three distinct glass panes"
assert source[150, 63, 0] > 200 and source[150, 64, 0] > 128, "Near right pane still misses its outer edge"
assert source[260, 147, 1] < 32 and source[260, 149, 1] > 200, "Far left pane spills into its metal rim"
assert source[260, 150, 1] > 128 and max(source[260, 151:154, 1]) < 32, "Far left/front mullion disappeared"

print("Lamp registration passed")
