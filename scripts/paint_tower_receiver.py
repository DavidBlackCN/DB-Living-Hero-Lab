"""Fixed-Base visible tower registration; runtime has no color classification."""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
ROOT=Path(__file__).resolve().parents[1]
SIZE=(1672,941)
# Full masonry silhouette, including the hat-adjacent section missed by the old
# x=1056 box and negative spaces between foreground strands. Not a light patch.
# Trace the exposed stone above the hat before following the hat/rose edge.
# The former x=1075 straight cut left a bright masonry wedge at dawn.
OUTLINE=[(924,0),(1075,0),(1075,40),(1079,44),(1079,53),
 (1078,67),(1077,72),(1073,77),(1069,82),(1067,87),(1065,94),
 (1063,98),(1062,195),
 (1050,233),(1039,265),(1026,303),(1022,323),(1000,332),(979,340),
 (954,350),(915,350),(916,309),(922,289),(926,270),(925,241),
 (922,215),(920,185),(923,145),(923,96),(918,78),(917,58),
 (916,39),(926,24)]

def main():
 base=np.asarray(Image.open(ROOT/'public/assets/hero/base/base-albedo.png').convert('RGB'),dtype=np.int16)
 r,g,b=base.transpose(2,0,1)
 # OFFLINE registration aid only. Preserve dark masonry windows: dark pixels
 # are foreground only when connected to the known rose/hair component.
 candidates=((base.max(2)<130)|((r-g>24)&(g<150))).astype(np.uint8)
 roi=np.zeros(SIZE[::-1],np.uint8);roi[85:334,998:1110]=1
 _,labels=cv2.connectedComponents(candidates*roi,connectivity=8)
 label=int(labels[130,1080]);assert label!=0
 foreground=(labels==label).astype(np.uint8)*255
 # Russet vine leaves intruding into the lower tower stay out of stone receiving.
 foliage=((r-g>24)&(g<150)).astype(np.uint8)*255
 foreground=np.maximum(foreground,foliage)
 scale=4
 mask=Image.new('L',(SIZE[0]*scale,SIZE[1]*scale))
 ImageDraw.Draw(mask).polygon([(x*scale,y*scale) for x,y in OUTLINE],fill=255)
 fg=Image.fromarray(foreground).resize(mask.size,Image.Resampling.NEAREST)
 coverage=np.asarray(mask,dtype=np.int16)-np.asarray(fg,dtype=np.int16)
 mask=Image.fromarray(np.uint8(np.clip(coverage,0,255)))
 # Inward-only half-pixel inset protects painted foreground antialiasing.
 mask=mask.filter(ImageFilter.MinFilter(5)).resize(SIZE,Image.Resampling.LANCZOS)
 out=ROOT/'public/assets/hero/lighting/tower-receiver-mask.png';mask.save(out)
 alpha=np.asarray(mask,dtype=float)/255
 overlay=base*(1-alpha[:,:,None]*.45)+np.array([40,255,140])*alpha[:,:,None]*.45
 dest=ROOT/'docs/validation/tower-final';dest.mkdir(exist_ok=True)
 Image.fromarray(np.uint8(overlay)).crop((910,0,1110,370)).resize((600,1110)).save(dest/'receiver-overlay.png')
 print(out,mask.size,'registered pixels',int((alpha>.99).sum()))
if __name__=='__main__':main()
