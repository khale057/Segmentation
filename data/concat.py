import sys, os
from PIL import Image

# image pathes to be concatenated into a whole image.
tt = 'data/test_data/' 
tt_i = tt+'vol55_recon_00936_RGB_'

size = 256

def make(i):
    fs = [tt_i+str(i)+'_'+str(k)+'.png' for k in np.arange(0,2560, size)] # get paths to all images to be merged
    images = [Image.open(x) for x in fs]
    total_width = 2560
    max_height = size
    new_im = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset,0))
        x_offset += im.size[0]
    new_im.save(tt+'v_'+str(i)+'.png')


# concatenate img vertically
def make_f():
    fs = [tt+'v_'+str(k)+'.png' for k in np.arange(10)] 
    images = [Image.open(x) for x in fs]
    total_width = 2560
    max_height = 2560
    new_im = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for im in range(len(images)):
        new_im.paste(images[im], (0,x_offset))
        x_offset += images[im].size[1]
    new_im.save(tt_i+'prediction.png')

for i in np.range(0,2560,size):
    make(i)
make_f()