from PIL import Image
import os, math

test_dir = "data/test_data/"

# Splits an image into tiles
# Works with images of any size as long as the
# dimensions are divisible by the tilesize
def split_image(filename, tilesize):
    im = Image.open(filename)
    width = im.width
    height = im.height
    if (width % tilesize == 0 and height % tilesize == 0):
        if (width > height):
            digits = int(math.log10(width))+1
        else:
            digits = int(math.log10(height))+1
        num_rows = width / tilesize
        num_cols = height / tilesize
        tiles_num = num_rows * num_cols
        for j in range(0, height, tilesize):
            for i in range(0, width, tilesize):
                area = (i, j, i + tilesize, j + tilesize)
                image = im.crop(area)
                image.save(filename + "_" + str(j).zfill(digits) + "_" + str(i).zfill(digits) + ".png")
    else:
        print("Error: Image cannot be divided by %s evenly" % tilesize)
    im.close()

# Joins the tiles back into a combined image
# If output is true, then it will join the output label mask image
# Otherwise, it will join the original image
def join_image(filename, width, height, tilesize, output=True):
    if (output):
        tiles = [tilename for tilename in os.listdir(test_dir) 
        if tilename[-7:] == "OUT.png" and 
        tilename[:len(filename)-4] == filename[:-4]]         
    else:
        tiles = [tilename for tilename in os.listdir(test_dir) 
        if tilename[-4:] == ".png" and 
        tilename[-5].isdigit() and
        tilename[:len(filename)-4] == filename[:-4]] 
    
    num_rows = int(height / tilesize)
    num_cols = int(width / tilesize)
    
    # joining horizontally
    for i in range(num_rows):
        fs = tiles[num_cols*i:num_cols*(i+1)]
        images = [Image.open(test_dir + x) for x in fs]
        new_im = Image.new('RGB', (num_cols*tilesize, tilesize))
        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset,0))
            x_offset += im.size[0]
        new_im.save(test_dir + "v_" + str(i) + ".png")
    
    # joining vertically
    for i in range(num_rows):
        horizontal_strips = [stripname for stripname in os.listdir(test_dir) if stripname[:2] == "v_"]
        images = [Image.open(test_dir + x) for x in horizontal_strips]
        new_im = Image.new('RGB', (num_cols*tilesize, num_rows*tilesize))
        x_offset = 0
        for im in range(len(images)):
            new_im.paste(images[im], (0,x_offset))
            x_offset += images[im].size[1]  
        if (output):
            new_im.save(test_dir + filename[:-4] + "_OUT.png")
        else:
            new_im.save(test_dir + filename)
    
    # deleting the leftover horizontal strips
    for image in horizontal_strips:
        if os.path.exists(test_dir + image):
            os.remove(test_dir + image)
            