import sys,glob,os
from PIL import Image
base=sys.argv[1]; cols=int(sys.argv[2]) if len(sys.argv)>2 else 5
fs=sorted(glob.glob(os.path.join('pdf',base+'_p*.png')))
ims=[Image.open(f) for f in fs]; w,h=ims[0].size
rows=(len(ims)+cols-1)//cols
sheet=Image.new('RGB',(cols*w+ (cols+1)*6, rows*h+(rows+1)*6),'#888')
for i,im in enumerate(ims): sheet.paste(im,(6+(i%cols)*(w+6),6+(i//cols)*(h+6)))
out=os.path.join('pdf','sheet_'+base+'.png'); sheet.save(out); print(out, sheet.size)
