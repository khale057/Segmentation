import sys, os
from PIL import Image
import numpy as np

def make_h(fs, i):
    fs = fs
    images = [Image.open(x) for x in fs]
    widths, heights = zip(*(j.size for j in images))
    total_width = sum(widths)
    max_height = max(heights)
    new_im = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for im in range(len(images)):
        new_im.paste(images[im], (x_offset,0))
        x_offset += images[im].size[0]
    new_im.save('image_'+str(i)+'h.jpg')

# concatenate img vertically
def make_v(fs, img_name):
    fs = fs
    images = [Image.open(x) for x in fs]
    widths, heights = zip(*(j.size for j in images))
    total_width = max(widths)
    max_height = sum(heights)
    new_im = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for im in range(len(images)):
        new_im.paste(images[im], (0,x_offset))
        x_offset += images[im].size[1]
    new_im.save(img_name[:-1]+'.jpg')


f = 'test_data/'
#f = 'ck/vol32_recon_00535_RGB_'
fs = os.listdir(f)
img_name = fs[0][:22]

f+=img_name

for i in np.arange(512, 2304, 256):
  fs = [f+str(i)+'_'+str(j)+'_OUT.png' for j in np.arange(0,2560,256)]
  make_h(fs, i)


fs = ['image_'+str(j)+'h.jpg' for j in np.arange(512, 2304, 256)]
fs.insert(0,'first.jpg')
fs.append('last.jpg')
make_v(fs, img_name)
