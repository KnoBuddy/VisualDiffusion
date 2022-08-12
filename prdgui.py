from tkinter import *
import sys
import os
import json5 as json
import shutil
import threading
import shlex
import subprocess
from time import *
from PIL import Image

if os.path.exists('gui_settings.json'):
    try:
        json_set = json.load(open('gui_settings.json'))
        print("GUI settings loaded")
    except:
        print("Error loading gui_settings.json")
        print("Loading from settings.json...")
        json_set = json.load(open('settings.json'))
else:
    json_set = json.load(open('settings.json'))
    print("Default settings loaded")

default_prompt = ["A beautiful painting of a Castle in the Scottish Highlands, underexposed and overcast:1", "by Banksy, Beeple, and Bob Ross:0.75", "trending on ArtStation, vibrant:0.5", "bokeh, blur, dof, depth of field:-1"]
    

is_running = False
has_run = False

class Redirect():

    def __init__(self, widget, autoscroll=True):
        self.widget = widget
        self.autoscroll = autoscroll

    def write(self, text):
        self.widget.insert('end', text)
        if self.autoscroll:
            self.widget.see("end")  # autoscroll
        
    def flush(self):
        pass


def get_num(derp):
    num = IntVar()
    num.set(json_set[derp])
    return num

def get_text(derp):
    try:
        text = StringVar()
        text.set(json_set[derp])
        return text
    except:
        return ''

def get_prompt(x, i):
    try:
        text = StringVar()
        text.set(json_set['text_prompts'][x][i])
        return text
    except:
        return ''

def get_prompt_step(x):
    try:
        text = StringVar()
        text.set(json_set['text_prompts'][x])
        return text
    except:
        return ''

path = './'

def save_text():
    x = batch_name_text.get()
    json_set['batch_name'] = x
    x = n_batches_text.get()
    json_set['n_batches'] = int(float(x))
    x = steps_text.get()
    json_set['steps'] = int(x)
    x = height_text.get()
    json_set['height'] = int(x)
    x = width_text.get()
    json_set['width'] = int(x)
    x = clip_guidance_scale_text.get()
    if x != 'auto':
        json_set['clip_guidance_scale'] = int(x)
    else:
        json_set['clip_guidance_scale'] = x
    x = skip_steps_text.get()
    json_set['skip_steps'] = int(x)
    x = use_secondary_model_text.get()
    json_set['use_secondary_model'] = x
    x = vitb32_text.get()
    json_set['ViTB32'] = float(x)
    x = vitb16_text.get()
    json_set['ViTB16'] = float(x)
    x = vitl14_text.get()
    json_set['ViTL14'] = float(x)
    x = vitl14_336_text.get()
    json_set['ViTL14_336'] = float(x)
    x = rn101_text.get()
    json_set['RN101'] = float(x)
    x = rn50_text.get()
    json_set['RN50'] = float(x)
    x = rn50x4_text.get()
    json_set['RN50x4'] = float(x)
    x = rn50x16_text.get()
    json_set['RN50x16'] = float(x)
    x = rn50x64_text.get()
    json_set['RN50x64'] = float(x)
    x = eta_text.get()
    json_set['eta'] = x
    x = sampling_mode_text.get()
    json_set['sampling_mode'] = x
    x = set_seed_text.get()
    json_set['set_seed'] = x
    json_set['display_rate'] = 1
    x = diffusion_model_text.get()
    json_set['diffusion_model'] = x
    x = symm_loss_scale_text.get()
    json_set['symm_loss_scale'] = int(float(x))
    x = symmetry_loss_v_text.get()
    json_set['symmetry_loss_v'] = x
    x = symmetry_loss_h_text.get()
    json_set['symmetry_loss_h'] = x
    x = symm_switch_text.get()
    json_set['symm_switch'] = x
    x = init_image_text.get()
    if not x:
        json_set['init_image'] = None
    elif x == 'None':
        json_set['init_image'] = None
    else:
        json_set['init_image'] = x
    x = extra_args_text.get()
    json_set['extra_args'] = x
    global prompt_text_box
    try:
        for i in range(len(prompt_text_box)):
            i = str(i)
            global tempprompts
            tempprompts = []
            for j in range(len(prompt_text_box[i])):
                x = prompt_text_box[i][j].get()
                if x != '':
                    tempprompts.append(x)
                else:
                    prompt_text_box[i][j].destroy()
                    prompt_text_box_label[i][j].destroy()
                    prompt_text_box[i].pop(j)
                    prompt_text_box_label[i].pop(j)
            json_set['text_prompts'][i] = tempprompts
    except:
        json_set['text_prompts']['0'] = default_prompt
    if json_set['text_prompts']['0'] == []:
        json_set['text_prompts']['0'] = default_prompt
        get_prompts()
    with open("gui_settings.json", "w+", encoding="utf-8") as outfile:
        json.dump(json_set, outfile, ensure_ascii=False, indent=4)

def run_thread():
    if has_run == False:
        show_image()
    save_text()
    if is_running == False:
        canvas.itemconfig(image_container, image='')
        global runThread
        runThread = threading.Thread(target=do_run)
        runThread.start()
    else:
        print("Already running")

def do_run():
    global is_running
    p = subprocess.Popen(shlex.split('python prd.py -s gui_settings.json '+extra_args_text.get()), stdout=subprocess.PIPE, text=True)
    while p.poll() is None:
       msg = p.stdout.readline().split()
       if msg:
            print(' '.join(msg))
    window.update()
    start = time()
    last_update= time()
    while (time() - start) <= 5:
        current = time()
        if (current-last_update)> 0.025 and is_running == True:
            last_update = current
            window.update()
        else:
            pass
    
    # Alternative method to run PRD
    # os.system('python prd.py -s gui_settings.json '+extra_args_text.get())

def show_image():
    if is_running == True:
        return
    else:
        shutil.copyfile('progress.png', 'progress_done.png')
        master_frame.pack()
        im = Image.open('progress_done.png')
        global h
        global w
        h = im.size[1]
        w = im.size[0]
        global image_window
        image_window = Frame(right_frame, width=w, height=h)
        image_window.pack()
        global canvas
        canvas = Canvas(image_window, width=w, height=h)
        global img
        global image_container
        img = PhotoImage(file="progress_done.png")
        image_container = canvas.create_image(0,0, anchor="nw",image=img)
        canvas.pack()
        updater()   

def updater():
    window.after(1000, refresh_image)

def refresh_image():
    global is_running
    updater()
    if runThread.is_alive():
        is_running = True
        try:
            im = Image.open('progress.png')
            global h
            global w
            if h != im.size[1] or w != im.size[0]:
                h = im.size[1]
                w = im.size[0]
                image_window.config(width=w, height=h)
            global img
            global image_container
            global canvas
            img = PhotoImage(file="progress.png")
            canvas.config(width=w, height=h)
            canvas.itemconfig(image_container, image = img)
            canvas.pack()
            global has_run
            has_run = True
        except:
            pass
    else:
        is_running = False
        try:
            shutil.copyfile('progress.png', 'progress_done.png')
            im = Image.open('progress_done.png')
            if h != im.size[1] or w != im.size[0]:
                h = im.size[1]
                w = im.size[0]
                image_window.config(width=w, height=h)
            img = PhotoImage(file="progress_done.png")
            canvas.config(width=w, height=h)
            canvas.itemconfig(image_container, image = img)
            canvas.pack()
        except:
            pass

window = Tk()

master_frame = Frame(bg='Light Blue', bd=3, relief=RIDGE)
master_frame.pack(fill=BOTH, expand=1)

left_frame = Frame(master_frame)
left_frame.pack(side=LEFT, fill=BOTH, expand=1)

left_frame1 = Frame(left_frame, bg='Light Blue', bd=3, relief=RIDGE)
left_frame1.grid(row=0, column=0, sticky=N+S+E+W)

left_frame2 = Frame(left_frame, height=100)
left_frame2 .grid(row=1, column=0, sticky=N+S+E+W)

right_frame = Frame(master_frame)
right_frame.pack(side=RIGHT, fill=BOTH, expand=1)

frame1 = Frame(left_frame1, bg='Light Green', bd=2, relief=FLAT)
frame1.grid(row=0, column=0, sticky=NSEW)

frame2 = Frame(left_frame1, bg='Light Yellow', bd=2, relief=FLAT)
frame2.grid(row=1, column=0, sticky=NSEW)

frame2_sub1 = Frame(frame2, bg='Light Yellow', bd=2, relief=FLAT)
frame2_sub1.grid(row=0, column=0, sticky=NSEW)

frame2_sub2 = Frame(frame2, bg='Light Yellow', bd=2, relief=FLAT)
frame2_sub2.grid(row=1, column=0, sticky=NSEW)

frame3 = Frame(left_frame1, bg='Light Blue', bd=2, relief=FLAT)
frame3.grid(row=2, column=0, sticky=NSEW)

frame3_sub1 = Frame(frame3, bg='Light Blue', bd=2, relief=FLAT)
frame3_sub1.grid(row=0, column=0, sticky=NSEW)

frame3_sub2 = Frame(frame3, bg='Light Blue', bd=2, relief=FLAT)
frame3_sub2.grid(row=1, column=0, sticky=NSEW)

# Text Prompts

current_step = '0'
derp = 0
prompt_text_box_label = {}
prompt_text_box_label['0'] = {}
prompt_text_box = {}
prompt_text_box['0'] = {}
prompt_text = json_set['text_prompts']

def get_prompts():
    global prompt_text
    prompt_text = json_set['text_prompts']
    if prompt_text["0"] == []:
        prompt_text["0"] = default_prompt
    for x in range(len(prompt_text)):
        x = str(x)
        for i in range(len(prompt_text[x])):
            prompt_text_box_label[x][i] = Label(frame3_sub2, text="Prompt " +str(i+1)+":")
            prompt_text_box_label[x][i].pack(anchor=NW, padx=2, pady=5)
            j = get_prompt(x, i)
            if j != "" or '' or None:
                prompt_text_box[x][i] = Entry(frame3_sub2, textvariable=get_prompt(x, i), width=150)
                prompt_text_box[x][i].pack(anchor=NW, padx=2, pady=5)
            


get_prompts()

def new_prompt():
    global prompt_text
    global current_step
    derp = len(prompt_text[current_step])
    prompt_text[current_step].append("")
    prompt_text_box_label[current_step][derp] = Label(frame3_sub2, text="Prompt " +str(derp+1)+":")
    prompt_text_box_label[current_step][derp].pack(anchor=NW, padx=2, pady=5)
    prompt_text_box[current_step][derp] = Entry(frame3_sub2, textvariable='', width=150)
    prompt_text_box[current_step][derp].pack(anchor=NW, padx=2, pady=5)



new_prompt_button = Button(frame3_sub1, text="New Prompt", command=new_prompt)
new_prompt_button.grid(row=0, column=0, sticky=NW)

steps = Label(frame1, text='Steps:')
steps.grid(row=1, column=0, pady=5, padx=2, sticky=NW)

steps_text = Entry(frame1, textvariable=get_text('steps'), width=8)
steps_text.grid(row=1, column=1, pady=5, padx=2, sticky=NW)

height = Label(frame1, text='Height:')
height.grid(row=1, column=2, pady=5, padx=2, sticky=NW)

height_text = Entry(frame1, textvariable=get_text('height'), width=8)
height_text.grid(row=1, column=3, pady=5, padx=2, sticky=NW)

width = Label(frame1, text='Width:')
width.grid(row=1, column=4, pady=5, padx=2, sticky=NW)

width_text = Entry(frame1, textvariable=get_text('width'), width=12)
width_text.grid(row=1, column=5, pady=5, padx=2, sticky=NW)

clip_guidance_scale = Label(frame1, text='Clip Guidance Scale:')
clip_guidance_scale.grid(row=2, column=0, pady=5, padx=2, sticky=NW)

clip_guidance_scale_text = Entry(frame1, textvariable=get_text('clip_guidance_scale'), width=8)
clip_guidance_scale_text.grid(row=2, column=1, pady=5, padx=2, sticky=NW)

skip_steps = Label(frame1, text='Skip Steps:')
skip_steps.grid(row=2, column=2, pady=5, padx=2, sticky=NW)

skip_steps_text = Entry(frame1, textvariable=get_text('skip_steps'), width=8)
skip_steps_text.grid(row=2, column=3, pady=5, padx=2, sticky=NW)

eta = Label(frame1, text='ETA:')
eta.grid(row=3, column=0, pady=5, padx=2, sticky=NW)

eta_text = Entry(frame1, textvariable=get_text('eta'), width=8)
eta_text.grid(row=3, column=1, pady=5, padx=2, sticky=NW)

use_secondary_model_text = get_num('use_secondary_model')
use_secondary_model = Checkbutton(frame2_sub1, text='Use Secondary Model', variable=use_secondary_model_text)
use_secondary_model.grid(row=5, column=4, pady=5, padx=2, sticky=NW)

vitb32_text = get_num('ViTB32')
vitb32_check = Checkbutton(frame2_sub1, text='ViTB32', variable=vitb32_text)
if vitb32_text.get() == 1:
    vitb32_check.select()
else:
    vitb32_check.deselect()
vitb32_check.grid(row=4, column=0, pady=5, padx=2, sticky=NW)

vitb16_text = get_num('ViTB16')
vitb16_check = Checkbutton(frame2_sub1, text='ViTB16', variable=vitb16_text)
if vitb16_text.get() == 1:
    vitb16_check.select()
else:
    vitb16_check.deselect()
vitb16_check.grid(row=4, column=1, pady=5, padx=2, sticky=NW)

vitl14_text = get_num('ViTL14')
vitl14_check = Checkbutton(frame2_sub1, text='ViTL14', variable=vitl14_text)
if vitl14_text.get() == 1:
    vitl14_check.select()
else:
    vitl14_check.deselect()
vitl14_check.grid(row=4, column=2, pady=5, padx=2, sticky=NW)

vitl14_336_text = get_num('ViTL14_336')
vitl14_336_check = Checkbutton(frame2_sub1, text='ViTL14_336', variable=vitl14_336_text)
if vitl14_336_text.get() == 1:
    vitl14_336_check.select()
else:
    vitl14_336_check.deselect()
vitl14_336_check.grid(row=4, column=3, pady=5, padx=2, sticky=NW)

rn101_text = get_num('RN101')
rn101_check = Checkbutton(frame2_sub1, text='RN101', variable=rn101_text)
if rn101_text.get() == 1:
    rn101_check.select()
else:
    rn101_check.deselect()
rn101_check.grid(row=4, column=4, pady=5, padx=2, sticky=NW)

rn50_text = get_num('RN50')
rn50_check = Checkbutton(frame2_sub1, text='RN50', variable=rn50_text)
if rn50_text.get() == 1:
    rn50_check.select()
else:
    rn50_check.deselect()
rn50_check.grid(row=5, column=0, pady=5, padx=2, sticky=NW)

rn50x4_text = get_num('RN50x4')
rn50x4_check = Checkbutton(frame2_sub1, text='RN50x4', variable=rn50x4_text)
if rn50x4_text.get() == 1:
    rn50x4_check.select()
else:
    rn50x4_check.deselect()
rn50x4_check.grid(row=5, column=1, pady=5, padx=2, sticky=NW)

rn50x16_text = get_num('RN50x16')
rn50x16_check = Checkbutton(frame2_sub1, text='RN50x16', variable=rn50x16_text)
if rn50x16_text.get() == 1:
    rn50x16_check.select()
else:
    rn50x16_check.deselect()
rn50x16_check.grid(row=5, column=2, pady=5, padx=2, sticky=NW)

rn50x64_text = get_num('RN50x64')
rn50x64_check = Checkbutton(frame2_sub1, text='RN50x64', variable=rn50x64_text)
if rn50x64_text.get() == 1:
    rn50x64_check.select()
else:
    rn50x64_check.deselect()
rn50x64_check.grid(row=5, column=3, pady=5, padx=2, sticky=NW)

sampling_mode = Label(frame1, text='Sampling Mode:')
sampling_mode.grid(row=2, column=6, pady=5, padx=2, sticky=NW)

sampling_mode_text = get_text('sampling_mode')
sampling_mode_drop = OptionMenu(frame1, sampling_mode_text, 'ddim', 'plms')
sampling_mode_drop.grid(row=2, column=7, pady=5, padx=2, sticky=NW)

batch_name = Label(frame1, text='Batch Name:')
batch_name.grid(row=2, column=4, pady=5, padx=2, sticky=NW)

batch_name_text = Entry(frame1, textvariable=get_text('batch_name'), width=10)
batch_name_text.grid(row=2, column=5, pady=5, padx=2, sticky=NW)

n_batches = Label(frame1, text='Number of Batches:')
n_batches.grid(row=3, column=4, pady=5, padx=2, sticky=NW)

n_batches_text = Entry(frame1, textvariable=get_text('n_batches'), width=12)
n_batches_text.grid(row=3, column=5, pady=5, padx=2, sticky=NW)

init_image = Label(frame1, text='Init Image:')
init_image.grid(row=3, column=6, pady=5, padx=2, sticky=NW)

init_image_text = Entry(frame1, textvariable=get_text('init_image'), width=48)
init_image_text.grid(row=3, column=7, pady=5, padx=2, sticky=NW)

diffusion_model = Label(frame1, text='Diffusion Model:')
diffusion_model.grid(row=1, column=6, pady=5, padx=2, sticky=NW)

diffusion_model_text = get_text('diffusion_model')
diffusion_model_drop = OptionMenu(
    frame1, diffusion_model_text, '512x512_diffusion_uncond_finetune_008100',
    '256x256_openai_comics_faces_by_alex_spirin', '256x256_diffusion_uncond',
    'pixel_art_diffusion_hard_256', 'pixel_art_diffusion_soft_256',
    'pixelartdiffusion4k', 'portrait_generator_v001', 'watercolordiffusion',
    'watercolordiffusion_2', 'PulpSciFiDiffusion',
    'FeiArt_Handpainted_CG_Diffusion', 'IsometricDiffusionRevrart512px')
diffusion_model_drop.grid(row=1, column=7, pady=5, padx=2, sticky=NW)

set_seed = Label(frame1, text='Set Seed:')
set_seed.grid(row=3, column=2, pady=5, padx=2, sticky=NW)

set_seed_text = Entry(frame1, textvariable=get_text('set_seed'), width=12)
set_seed_text.grid(row=3, column=3, pady=5, padx=2, sticky=NW)

symmetry_loss_v_text = get_num('symmetry_loss_v')
symmetry_loss_v_check = Checkbutton(frame2_sub1, text='Vertical Symmetry', variable=symmetry_loss_v_text)
if symmetry_loss_v_text.get() == 1:
    symmetry_loss_v_check.select()
else:
    symmetry_loss_v_check.deselect()
symmetry_loss_v_check.grid(row=4, column=8, pady=5, padx=2, sticky=NW)

symmetry_loss_h_text = get_num('symmetry_loss_h')
symmetry_loss_h_check = Checkbutton(frame2_sub1, text='Horizontal Symmetry', variable=symmetry_loss_h_text)
if symmetry_loss_h_text.get() == 1:
    symmetry_loss_h_check.select()
else:
    symmetry_loss_h_check.deselect()
symmetry_loss_h_check.grid(row=5, column=8, pady=5, padx=2, sticky=NW)

symm_loss_scale = Label(frame2_sub1, text='Symmetry Scale:')
symm_loss_scale.grid(row=5, column=9, pady=5, padx=2, sticky=NW)

symm_loss_scale_text = Entry(frame2_sub1, textvariable=get_text('symm_loss_scale'), width=12)
symm_loss_scale_text.grid(row=5, column=10, pady=5, padx=2, sticky=NW)

symm_switch = Label(frame2_sub1, text='Symmetry Switch:')
symm_switch.grid(row=4, column=9, pady=5, padx=2, sticky=NW)

symm_switch_text = Entry(frame2_sub1, textvariable=get_text('symm_switch'), width=12)
symm_switch_text.grid(row=4, column=10, pady=5, padx=2, sticky=NW)

extra_args = Label(frame2_sub2, text='Extra Args: (Advanced use only. Ex: --gobig)')
extra_args.grid(row=9, column=0, pady=5, padx=2, sticky=NW)

extra_args_text = Entry(frame2_sub2, textvariable=get_text('extra_args'), width=150)
extra_args_text.grid(row=10, column=0, pady=5, padx=2, sticky=NW)

save = Button(frame2_sub1,text='Save Settings', command=save_text).grid(row=4, column=11, pady=5, padx=2)
run = Button(frame2_sub1,text='Run', command=run_thread).grid(row=5, column=11, pady=5, padx=2)

frame = Frame(left_frame2, height=150)
frame.pack_propagate(0)
frame.pack(expand=True, fill='both')

text = Text(frame, height=150)
text.pack(side='left', fill='both', expand=True)

scrollbar = Scrollbar(frame)
scrollbar.pack(side='right', fill='y')

text['yscrollcommand'] = scrollbar.set
scrollbar['command'] = text.yview

old_stdout = sys.stdout    
sys.stdout = Redirect(text)

window.title('ProgRockDiffusion (PRD GUI): '+json_set['batch_name'])

window.mainloop()

# - after close window -

sys.stdout = old_stdout
