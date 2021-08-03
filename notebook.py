from PIL import Image
from ipywidgets import Layout
from ipywidgets import Image as IpyImage
import ipywidgets as widgets
from ipycanvas import Canvas, hold_canvas, MultiCanvas
import io, os, math
import numpy as np

### Selecting the Input Image
# Select and display the input image
# When an image is uploaded, the test_data directory will be cleared
# Afterwards, the input image will be copied to directory

seg_dir = ''
test_dir = seg_dir + 'data/test_data/'
file_formats_accept = ['.png', '.jpg', '.jpeg', '.tif']
image_uploader = widgets.FileUpload(accept=','.join(file_formats_accept), multiple=False)

def image_upload(uploader):
    if uploader:
        display('Image selected')
        name = next(iter(uploader.keys()))
        byte_info = uploader[name]['content']
        display(widgets.Image(value=byte_info)) 
        for fname in os.listdir(test_dir): 
            if (fname.endswith(tuple(file_formats_accept))):
                os.remove(test_dir + fname)
        image = Image.open(io.BytesIO(byte_info))
        image.save(test_dir + name)
    else:
        display('Upload an image')
    return uploader
    
def select_input():
    image_display = widgets.interactive(image_upload, uploader = image_uploader)
    display(image_display)

### Image Pre-processing
# Makes sure the image is ready for pre-processing
# Extracts width and height of image

tilesize = 256
width, height, filename = 0, 0, 0

def image_preprocessing():
    global width, height, filename
    if (len(os.listdir(test_dir)) == 1):
        filename = os.listdir(test_dir)[0]
        if (filename.endswith(tuple(file_formats_accept))):
            im = Image.open(test_dir + filename)
            width = im.width
            height = im.height
            im.close()        
        else:
            print("Input must be a valid image.")
    else:
        print("There should be only one input image in the test directory.")

# Canvas variables
canvas_width, canvas_height, center_x, center_y, edge_x, edge_y, multi_canvas, final_canvas = 0, 0, 0, 0, 0, 0, 0, 0

# Other canvas properties
hold_state = 0
circle_button_outer_radius = 9
circle_button_inner_radius = 6
input_image = 0

# Canvas functions
def draw_canvas():
    with hold_canvas(multi_canvas):
        # Green circle
        multi_canvas[1].clear()         
        multi_canvas[1].global_alpha = 0.25
        multi_canvas[1].fill_style = 'green'
        multi_canvas[1].fill_circle(center_x, center_y, math.sqrt(math.pow(center_x-edge_x, 2)+math.pow(center_y-edge_y, 2)))
        
        # Circle buttons
        multi_canvas[2].clear()
        multi_canvas[2].stroke_style = 'red'      
        for i in range(circle_button_inner_radius, circle_button_outer_radius+1):
            multi_canvas[2].stroke_circle(center_x, center_y, i) 
        multi_canvas[2].stroke_style = 'blue'
        for i in range(circle_button_inner_radius, circle_button_outer_radius+1):
            multi_canvas[2].stroke_circle(edge_x, edge_y, i) 
        multi_canvas[2].stroke_style = 'black'
        multi_canvas[2].stroke_circle(center_x, center_y, circle_button_outer_radius) 
        multi_canvas[2].stroke_circle(edge_x, edge_y, circle_button_outer_radius) 
        multi_canvas[2].stroke_circle(center_x, center_y, circle_button_inner_radius) 
        multi_canvas[2].stroke_circle(edge_x, edge_y, circle_button_inner_radius)
        
def handle_mouse_move(xpos, ypos):
    global center_x, center_y, edge_x, edge_y, hold_state
    if (hold_state == 1):
        center_x = xpos
        center_y = ypos
        draw_canvas()
    elif (hold_state == 2):
        edge_x = xpos
        edge_y = ypos
        draw_canvas()
    
def handle_mouse_down(xpos, ypos):
    global center_x, center_y, edge_x, edge_y, hold_state
    if (math.sqrt(math.pow(edge_x-xpos, 2)+math.pow(edge_y-ypos, 2)) <= 15):
        hold_state = 2
    elif (math.sqrt(math.pow(center_x-xpos, 2)+math.pow(center_y-ypos, 2)) <= 15):
        hold_state = 1    
    draw_canvas()
    
def handle_mouse_up(xpos, ypos):
    global hold_state
    hold_state = 0

# Create the canvas
def create_canvas():
    global canvas_width, canvas_height, center_x, center_y, edge_x, edge_y, multi_canvas
    # Canvas dimensions
    canvas_width = 800
    canvas_height = round(height/(width/canvas_width))

    # Coordinates for center of circle
    center_x = canvas_width/2
    center_y = canvas_height/2

    # Coordinates for edge of circle
    edge_x = canvas_width/2 + 200
    edge_y = canvas_height/2

    multi_canvas = MultiCanvas(3, width=canvas_width, height=canvas_height)
    background = IpyImage.from_file(test_dir + filename)
    multi_canvas[0].draw_image(background, 0, 0, width=canvas_width, height=canvas_height)
    
    # Register mouse callback
    multi_canvas[2].on_mouse_move(handle_mouse_move)
    multi_canvas[2].on_mouse_down(handle_mouse_down)
    multi_canvas[2].on_mouse_up(handle_mouse_up)

def remove_bg_noise():
    draw_canvas()
    display(multi_canvas)

# Confirm selection and turn the background noise area green
def confirm_selection():
    global input_image
    radius = math.sqrt(math.pow(center_x-edge_x, 2)+math.pow(center_y-edge_y, 2))
    adjusted_radius = (radius/canvas_width)*width
    adjusted_center_x = (center_x/canvas_width)*width
    adjusted_center_y = (center_y/canvas_height)*height
    bg_noise_arr = np.zeros((height, width, 4), dtype=np.uint8)
    for i in range(height):
        for j in range(width):
            bg_noise_arr[i, j, 1] = 255
            if (math.sqrt(math.pow(i-adjusted_center_y, 2)+math.pow(j-adjusted_center_x, 2)) >= adjusted_radius):
                bg_noise_arr[i, j, 3] = 255  
                
    bg_noise_im = Image.fromarray(bg_noise_arr, 'RGBA')
    input_image = Image.open(test_dir + filename).convert('RGB')
    input_image.paste(bg_noise_im, (0, 0), mask = bg_noise_im)
    input_image.save(test_dir + filename[:-4] + "_noise_removed.png")
    display(input_image)

# Splits up the input image into tiles
def split_input():
    if (split_image(test_dir + filename[:-4] + "_noise_removed.png", tilesize)):            
        os.remove(test_dir + filename)
        os.remove(test_dir + filename[:-4] + "_noise_removed.png")
        print("Image was successfully split")
    
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
        return False        
    im.close()
    return True

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
            
### Resulting Label Mask
fe_image, mg_image = 0, 0

# Concatenates the resulting output tiles
def result_mask():
    global input_image, fe_image, mg_image
    join_image(filename, width, height, tilesize, True) # join original image
    join_image(filename, width, height, tilesize, False) # join output mask
    input_image = Image.open(test_dir + filename, 'r').convert('RGBA')
    output_image = Image.open(test_dir + filename[:-4] + "_OUT.png", 'r').convert('RGBA')

    # Extracting each inclusion mask seperately
    image_data = np.array(output_image)
    r, g, b, alpha = image_data.T

    # Fe Mask (Green)
    fe_data = np.copy(image_data)
    for i in range(height):
        for j in range(width):
            if not (fe_data[i, j, 0] == 0 and fe_data[i, j, 1] == 150 and fe_data[i, j, 2] == 0):
                fe_data[i, j, 3] = 0
    fe_image = Image.fromarray(fe_data)
    fe_image.save(test_dir + filename[:-4] + "_OUT_FE.png")

    # Mg Mask (Blue)
    mg_data = np.copy(image_data)
    for i in range(height):
        for j in range(width):
            if not (fe_data[i, j, 0] == 0 and fe_data[i, j, 1] == 0 and fe_data[i, j, 2] == 255):
                mg_data[i, j, 3] = 0
    mg_image = Image.fromarray(mg_data)
    mg_image.save(test_dir + filename[:-4] + "_OUT_MG.png")
    
def image_blend(opacity, show_fe, show_mg):
    with hold_canvas(final_canvas):
        # Fe Mask (Green)
        final_canvas[1].clear()         
        final_canvas[1].global_alpha = opacity
        if not (show_fe): 
            final_canvas[1].global_alpha = 0
        final_canvas[1].draw_image(IpyImage.from_file(test_dir + filename[:-4] + "_OUT_FE.png"), 0, 0, width=canvas_width, height=canvas_height)
        
        # Mg Mask (Blue)
        final_canvas[2].clear()         
        final_canvas[2].global_alpha = opacity
        if not (show_mg): 
            final_canvas[2].global_alpha = 0
        final_canvas[2].draw_image(IpyImage.from_file(test_dir + filename[:-4] + "_OUT_MG.png"), 0, 0, width=canvas_width, height=canvas_height)
    display(final_canvas)    
    return opacity
    
opacity_slider = widgets.FloatSlider(value=1,
                                     min=0,
                                     max=1,
                                     step=0.05,
                                     description='Opacity:',
                                     disabled=False,
                                     continuous_update=False,
                                     orientation='horizontal',
                                     readout=True,
                                     readout_format='.2f')

fe_checkbox = widgets.Checkbox(value=True,
                               description='Fe (Green)',
                               disabled=False,
                               indent=False)

mg_checkbox = widgets.Checkbox(value=True,
                               description='Mg (Blue)',
                               disabled=False,
                               indent=False)

# Displays the resulting inclusion mask image
# An opacity slider can be used to compare the output with the original image
# The checkboxes can be used to display only a certain type of inclusion
def display_result():
    global height, width, final_canvas, canvas_width, canvas_height
    canvas_width = 1000
    canvas_height = round(height/(width/canvas_width))

    image_overlay = widgets.interactive(image_blend,
                                        opacity = opacity_slider,
                                        show_fe = fe_checkbox,
                                        show_mg = mg_checkbox)

    # Create the canvas
    final_canvas = MultiCanvas(3, width=canvas_width, height=canvas_height)
    background = IpyImage.from_file(test_dir + filename)
    final_canvas[0].draw_image(background, 0, 0, width=canvas_width, height=canvas_height)

    display(image_overlay)

### Correcting Label Mask
option_names = ['Draw: Missing Fe (Red)', 'Draw: Missing Mg (Orange)', 'Draw: Incorrect Label (Purple)', 'Erase']

radio_buttons = widgets.RadioButtons(options=option_names,
                                     description='Type:',
                                     disabled=False)
                                     
correction_canvas = 0
radius = 5
circle_list = []

# Canvas functions
def draw_canvas_final():
    with hold_canvas(correction_canvas):
        # Draw corrections
        correction_canvas[1].clear()    
        for circle in circle_list:
            correction_canvas[1].global_alpha = 1
            if (circle[2] == 'purple'):
                correction_canvas[1].global_alpha = 0.25    
            correction_canvas[1].fill_style = circle[2]
            correction_canvas[1].fill_circle(circle[0], circle[1], radius)
            
def handle_mouse_move_final(xpos, ypos):
    global radio_buttons, hold_state, circle_list    
    if (hold_state == 1):
        found = False
        if (radio_buttons.value == option_names[0]):     
            for circle in circle_list: 
                if circle[0] == round(xpos) and circle[1] == round(ypos):
                    circle[2] = 'red'
                    found = True
            if not (found):
                circle_list.append((round(xpos), round(ypos), 'red'))
        elif (radio_buttons.value == option_names[1]):
            for circle in circle_list:
                if circle[0] == round(xpos) and circle[1] == round(ypos):
                    circle[2] = 'orange'
                    found = True
            if not (found):
                circle_list.append((round(xpos), round(ypos), 'orange'))
        elif (radio_buttons.value == option_names[2]):
            for circle in circle_list:
                if circle[0] == round(xpos) and circle[1] == round(ypos):
                    circle[2] = 'purple'
                    found = True
            if not (found):
                circle_list.append((round(xpos), round(ypos), 'purple'))
        else:
            list_copy = []
            for circle in circle_list:
                if ( math.sqrt(math.pow(circle[0]-xpos, 2)+math.pow(circle[1]-ypos, 2)) > radius):
                    list_copy.append(circle)
            circle_list = list_copy.copy()                    
    draw_canvas_final()
        
def handle_mouse_down_final(xpos, ypos):
    global radio_buttons, hold_state, circle_list    
    hold_state = 1
    found = False
    if (radio_buttons.value == option_names[0]):     
        for circle in circle_list: 
            if circle[0] == round(xpos) and circle[1] == round(ypos):
                circle[2] = 'red'
                found = True
        if not (found):
            circle_list.append((round(xpos), round(ypos), 'red'))
    elif (radio_buttons.value == option_names[1]):
        for circle in circle_list:
            if circle[0] == round(xpos) and circle[1] == round(ypos):
                circle[2] = 'orange'
                found = True
        if not (found):
            circle_list.append((round(xpos), round(ypos), 'orange'))
    elif (radio_buttons.value == option_names[2]):
        for circle in circle_list:
            if circle[0] == round(xpos) and circle[1] == round(ypos):
                circle[2] = 'purple'
                found = True
        if not (found):
            circle_list.append((round(xpos), round(ypos), 'purple'))
    else:
        list_copy = []
        for circle in circle_list:
            if ( math.sqrt(math.pow(circle[0]-xpos, 2)+math.pow(circle[1]-ypos, 2)) > radius):
                list_copy.append(circle)
        circle_list = list_copy.copy()                    
    draw_canvas_final()

def handle_mouse_up_final(xpos, ypos):
    global hold_state
    hold_state = 0
    draw_canvas_final()

def create_correction_canvas():
    global input_image, correction_canvas, canvas_width, canvas_height, hold_state, fe_image, mg_image
    # Create overlay image
    input_image = Image.open(test_dir + filename).convert('RGB')
    input_image.paste(fe_image, (0, 0), mask = fe_image)
    input_image.paste(mg_image, (0, 0), mask = mg_image)
    input_image.save(test_dir + filename[:-4] + "_overlay.png")

    # Create the canvas
    canvas_width = width/2
    canvas_height = round(height/(width/canvas_width))
    correction_canvas = MultiCanvas(2, width=canvas_width, height=canvas_height)
    background = IpyImage.from_file(test_dir + filename[:-4] + "_overlay.png")
    correction_canvas[0].draw_image(background, 0, 0, width=canvas_width, height=canvas_height)
    correction_canvas[1].sync_image_data = True
    hold_state = 0
    
    correction_canvas[1].on_mouse_move(handle_mouse_move_final)
    correction_canvas[1].on_mouse_down(handle_mouse_down_final)
    correction_canvas[1].on_mouse_up(handle_mouse_up_final)
    
def display_correction_canvas():
    display(radio_buttons)
    draw_canvas_final()
    display(correction_canvas)
    
# Convert the corrections into a numpy array
def convert_correction_canvas():
    correction_canvas_arr = correction_canvas[1].get_image_data()
    correction_arr = np.zeros((height, width, 4), dtype=np.uint8)
    for i in range(correction_canvas_arr.shape[0]):
        for j in range(correction_canvas_arr.shape[1]):
            for k in range(4):
                correction_arr[2*i, 2*j, k] = correction_canvas_arr[i, j, k]
                correction_arr[2*i+1, 2*j, k] = correction_canvas_arr[i, j, k]
                correction_arr[2*i, 2*j+1, k] = correction_canvas_arr[i, j, k]
                correction_arr[2*i+1, 2*j+1, k] = correction_canvas_arr[i, j, k]
    # display(Image.fromarray(correction_arr))
    print("Image was converted into numpy array")
