# -*- coding: utf-8 -*-

"""
VisualDiffusion, a GUI for running ProgRock Diffusion, by Kyle Steveson (KnoBuddy)
It is dependent upon ProgRock Diffusion being installed. Many thanks to everyone that has contributed to the works here.
--
ProgRock Diffusion
Command line version of Disco Diffusion (v5 Alpha) adapted for command line by Jason Hough (and friends!)
--
Original file is located at
    https://colab.research.google.com/drive/1QGCyDlYneIvv1zFXngfOCCoSUKC6j1ZP
Original notebook by Katherine Crowson (https://github.com/crowsonkb, https://twitter.com/RiversHaveWings). It uses either OpenAI's 256x256 unconditional ImageNet or Katherine Crowson's fine-tuned 512x512 diffusion model (https://github.com/openai/guided-diffusion), together with CLIP (https://github.com/openai/CLIP) to connect text prompts with images.
Modified by Daniel Russell (https://github.com/russelldc, https://twitter.com/danielrussruss) to include (hopefully) optimal params for quick generations in 15-100 timesteps rather than 1000, as well as more robust augmentations.
Further improvements from Dango233 and nsheppard helped improve the quality of diffusion in general, and especially so for shorter runs like this notebook aims to achieve.
Vark added code to load in multiple Clip models at once, which all prompts are evaluated against, which may greatly improve accuracy.
The latest zoom, pan, rotation, and keyframes features were taken from Chigozie Nri's VQGAN Zoom Notebook (https://github.com/chigozienri, https://twitter.com/chigozienri)
Advanced DangoCutn Cutout method is also from Dango223.
Somnai (https://twitter.com/Somnai_dreams) added Diffusion Animation techniques, QoL improvements and various implementations of tech and techniques, mostly listed in the changelog below.
Pixel art models by u/Kaliyuga_ai
Comic faces model by alex_spirin
"""

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import sys
import os
import json5 as json
import shutil
import threading
import shlex
import subprocess
import pathlib
from time import *
from PIL import Image
from PIL import ImageTk


# File Names
gui_settings = 'gui_settings.json'
default_settings = 'settings.json'
progress = 'progress.png'
progress_done = 'progress_done.png'
prd = 'prd.py'

default_prompt = ["A beautiful painting of a Castle in the Scottish Highlands, underexposed and overcast:1", "by Banksy, Beeple, and Bob Ross:0.75", "trending on ArtStation, vibrant:0.5", "bokeh, blur, dof, depth of field:-1"]


# Load Settings from JSON
if os.path.exists(gui_settings):
    try:
        json_set = json.load(open(gui_settings))
        print("GUI settings loaded", file = sys.stdout)
    except:
        print("Error loading gui_settings.json", file = sys.stdout)
        print("Loading from Defaults...", file = sys.stdout)
        json_set = json.load(open(default_settings))
        json_set['text_prompts']['0'] = default_prompt
else:
    json_set = json.load(open(default_settings))
    print("Default settings loaded", file = sys.stdout)

# First Run Check Variables
is_running = False
has_run = False
interrupt = False

args = list(json_set.keys())

#Auto Scrolling Shell Text box class
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
    

def run_thread():
    global is_running
    global has_run
    if is_running == False:
        is_running = True
        has_run = True
        global thread
        thread = threading.Thread(target=do_run)
        thread.start()
    else:
        print("Already Running")

def do_run():
    global is_running
    global has_run
    global thread
    global json_set
    global gui_settings
    global default_settings
    global progress
    global progress_done
    global prd
    # Save Settings to JSON
    save_settings_file()
    # Run PRD
    try:
        print("Running PRD...", file = sys.stdout)
        prd_cmd = "python3 " + prd + " " + gui_settings
        #print("Command: " + prd_cmd, file = sys.stdout)
        prd_args = shlex.split(prd_cmd)
        #print("Args: " + prd_args, file = sys.stdout)
        p = subprocess.Popen(shlex.split('python prd.py -s '+gui_settings), stdout=subprocess.PIPE, text=True)
        updater()
        while p.poll() is None:
            line = p.stdout.readline()
            line = line.strip()
            if line:
                print(line, file = sys.stdout)
    except:
        print("Error running PRD", file = sys.stdout)
        is_running = False
        thread = None
        

def show_image():
    if is_running == True:
        return
    else:
        try:
            shutil.copyfile(progress, progress_done)
        except:
            image = Image.new('RGB', (512, 512), (255, 255, 255))
            image.save(progress)
            image.save(progress_done)
        master_frame.pack()
        im = Image.open(progress_done)
        global h
        global w
        h = im.size[1]
        w = im.size[0]
        global image_window
        image_window = ttk.Frame(image_frame, width=w, height=h)
        image_window.pack()
        global canvas
        canvas = Canvas(image_window, width=w, height=h)
        global img
        global image_container
        try:
            img = PhotoImage(file=progress_done)
        except:
            image = Image.new('RGB', (512, 512), (255, 255, 255))
            image.save(progress_done)
        image_container = canvas.create_image(0,0, anchor="nw",image=img)
        canvas.pack()
        updater()   


# Function to refresh the image in the GUI
def refresh_image():
    global is_running
    updater()
    try:
        if thread.is_alive():
            is_running = True
            try:
                im = Image.open(progress)
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
                shutil.copyfile(progress, progress_done)
                im = Image.open(progress_done)
                if h != im.size[1] or w != im.size[0]:
                    h = im.size[1]
                    w = im.size[0]
                    image_window.config(width=w, height=h)
                img = PhotoImage(file=progress_done)
                canvas.config(width=w, height=h)
                canvas.itemconfig(image_container, image = img)
                canvas.pack()
            except:
                pass
    except:
        is_running = False
        try:
            shutil.copyfile(progress, progress_done)
            im = Image.open(progress_done)
            if h != im.size[1] or w != im.size[0]:
                h = im.size[1]
                w = im.size[0]
                image_window.config(width=w, height=h)
            img = PhotoImage(file=progress_done)
            canvas.config(width=w, height=h)
            canvas.itemconfig(image_container, image = img)
            canvas.pack()
        except:
            pass

def refresh_ui():
    cleanup()
    get_prompts()
    fix_text()
    show_prompt_step('0')

def save_settings_file():
    global interrupt
    interrupt = True
    global json_set
    global gui_settings
    # Save Settings to JSON
    print(gui_settings)
    if prompt_scheduling == True:
        for k in list (json_set['text_prompts']['0'].keys()):
            if json_set['text_prompts']['0'][k] == []:
                del json_set['text_prompts']['0'][k]
                print('ahaha!')
    with open(gui_settings, 'w+', encoding='utf-8') as f:
        json.dump(json_set, f, ensure_ascii=False, indent=4)
    print("Settings saved", file = sys.stdout)
    interrupt = False
    cleanup()
    get_prompts()

def save_as_settings_file():
    global interrupt
    interrupt = True
    global json_set
    global gui_settings
    # Save Settings to JSON
    if prompt_scheduling == True:
        for k in list (json_set['text_prompts']['0'].keys()):
            if json_set['text_prompts']['0'][k] == []:
                del json_set['text_prompts']['0'][k]
                print('ahaha!')
    filename = filedialog.asksaveasfilename(initialdir = "./",title = "Select file",filetypes = (("json files","*.json"),("all files","*.*")))
    gui_settings = filename
    print("Settings saved to: "+gui_settings, file = sys.stdout)
    if filename:
        with open(filename, 'w+', encoding='utf-8') as f:
            json.dump(json_set, f, ensure_ascii=False, indent=4)
        print("Settings saved", file = sys.stdout)
    interrupt = False
    cleanup()
    get_prompts()
    fix_text()


def load_settings_file():
    global interrupt
    interrupt = True
    cleanup()
    global json_set
    # Load Settings from JSON
    filename = filedialog.askopenfilename(initialdir = "./",title = "Select file",filetypes = (("json files","*.json"),("all files","*.*")))
    global gui_settings
    global prompt_text
    gui_settings = os.path.basename(filename)
    if filename:
        try:
            json_set = json.load(open(filename))
            print(filename+' just a test')
            print("Settings loaded", file = sys.stdout)
            print("Settings loaded from: "+gui_settings, file = sys.stdout)
            prompt_text = json_set['text_prompts']['0']
        except:
            print("Error loading settings file", file = sys.stdout)
            print("Loading from Defaults...", file = sys.stdout)
            json_set = json.load(open(default_settings))
    interrupt = False
    set_prompt_text()
    refresh()
    refresh_ui()
    updater()

def open_image_file():
    global json_set
    filename = filedialog.askopenfilename(initialdir = "./",title = "Select file",filetypes = (("png files","*.png"),("all files","*.*")))
    if filename:
        json_set['init_image'] = filename
        global init_image
        init_image.set(filename)
        init_image_label.configure(text=init_image.get())
        print("Image loaded: "+filename, file = sys.stdout)
        refresh()

def clear_init_image():
    global json_set
    json_set['init_image'] = None
    global init_image
    init_image.set(None)
    init_image_label.configure(text=init_image.get())
    print("Image cleared", file = sys.stdout)
    refresh()
    refresh_ui()

def show_advanced_settings():
    if advanced_settings_frame.winfo_viewable():
        advanced_settings_frame.pack_forget()
        clip_model_frame.pack_forget()
        symmetry_frame.pack_forget()
    else:
        advanced_settings_frame.pack(side=TOP, fill=BOTH, padx=2, pady=2)

def show_clip_settings():
    if clip_model_frame.winfo_viewable():
        clip_model_frame.pack_forget()
    else:
        clip_model_frame.pack(side=TOP, fill=BOTH, padx=2, pady=2)

def show_symmetry_settings():
    if symmetry_frame.winfo_viewable():
        symmetry_frame.pack_forget()
    else:
        symmetry_frame.pack(side=TOP, fill=BOTH, padx=2, pady=2)

def refresh():
    # Refresh GUI
    global json_set
    global prompt_scheduling
    global prompt_text
    global prompt_text_vars
    global prompt_steps
    try:
        if ['0'] in json_set['text_prompts']['0']:
            prompt_scheduling = True
            prompt_text = json_set['text_prompts']['0']
            prompt_steps = list(prompt_text.keys())
            print('Prompt Scheduling is enabled', file = sys.stdout)
    except:
        prompt_scheduling = False
        prompt_text = json_set['text_prompts']['0']
        print("Prompt Scheduling is disabled", file = sys.stdout)
    steps.set(json_set['steps'])
    steps_entry.configure(textvariable=steps)
    height.set(json_set['height'])
    height_entry.configure(textvariable=height)
    width.set(json_set['width'])
    width_entry.configure(textvariable=width)
    sampling_mode.set(json_set['sampling_mode'])
    sampling_mode_optionmenu.configure(textvariable=sampling_mode)
    diffusion_model.set(json_set['diffusion_model'])
    diffusion_model_optionmenu.configure(textvariable=diffusion_model)
    
    if json_set['simple_symmetry'] == False:
        simple_symmetry.set(False)
    else:
        simple_symmetry.set(True)
    simple_symmetry_check.configure(variable=simple_symmetry)
    skip_steps.set(json_set['skip_steps'])
    skip_steps_entry.configure(textvariable=skip_steps)
    clip_guidance_scale.set(json_set['clip_guidance_scale'])
    clip_guidance_scale_entry.configure(textvariable=clip_guidance_scale)
    set_seed.set(json_set['set_seed'])
    set_seed_entry.configure(textvariable=set_seed)
    eta.set(json_set['eta'])
    eta_entry.configure(textvariable=eta)
    clamp_max.set(json_set['clamp_max'])
    clamp_max_entry.configure(textvariable=clamp_max)
    cut_overview.set(json_set['cut_overview'])
    cut_overview_entry.configure(textvariable=cut_overview)
    cut_innercut.set(json_set['cut_innercut'])
    cut_innercut_entry.configure(textvariable=cut_innercut)
    cut_ic_pow.set(json_set['cut_ic_pow'])
    cut_ic_pow_entry.configure(textvariable=cut_ic_pow)
    cutn_batches.set(json_set['cutn_batches'])
    cutn_batches_entry.configure(textvariable=cutn_batches)
    n_batches.set(json_set['n_batches'])
    n_batches_entry.configure(textvariable=n_batches)
    use_secondary_model.set(json_set['use_secondary_model'])
    use_secondary_model_check.configure(variable=use_secondary_model)
    fix_brightness_contrast.set(bool(json_set['fix_brightness_contrast']))
    fix_brightness_contrast_check.configure(variable=fix_brightness_contrast)
    cut_heatmaps.set(json_set['cut_heatmaps'])
    cut_heatmaps_check.configure(variable=cut_heatmaps)
    smooth_schedules.set(json_set['smooth_schedules'])
    smooth_schedules_check.configure(variable=smooth_schedules)
    vitb16.set(bool(json_set['ViTB16']))
    vitb16_check.configure(variable=vitb16)
    vitb32.set(bool(json_set['ViTB32']))
    vitb32_check.configure(variable=vitb32)
    vitl14.set(bool(json_set['ViTL14']))
    vitl14_check.configure(variable=vitl14)
    vitl14_336.set(bool(json_set['ViTL14_336']))
    vitl14_336_check.configure(variable=vitl14_336)
    rn101.set(bool(json_set['RN101']))
    rn101_check.configure(variable=rn101)
    rn50.set(bool(json_set['RN50']))
    rn50_check.configure(variable=rn50)
    rn50x4.set(bool(json_set['RN50x4']))
    rn50x4_check.configure(variable=rn50x4)
    rn50x16.set(bool(json_set['RN50x16']))
    rn50x16_check.configure(variable=rn50x16)
    rn50x64.set(bool(json_set['RN50x64']))
    rn50x64_check.configure(variable=rn50x64)
    vitb32_laion2b_e16.set(bool(json_set['ViTB32_laion2b_e16']))
    vitb32_laion2b_e16_check.configure(variable=vitb32_laion2b_e16)
    vitb32_laion400m_e31.set(bool(json_set['ViTB32_laion400m_e31']))
    vitb32_laion400m_e31_check.configure(variable=vitb32_laion400m_e31)
    vitb32_laion400m_32.set(bool(json_set['ViTB32_laion400m_32']))
    vitb32_laion400m_32_check.configure(variable=vitb32_laion400m_32)
    vitb32quickgelu_laion400m_e31.set(bool(json_set['ViTB32quickgelu_laion400m_e31']))
    vitb32quickgelu_laion400m_e31_check.configure(variable=vitb32quickgelu_laion400m_e31)
    vitb32quickgelu_laion400m_e32.set(bool(json_set['ViTB32quickgelu_laion400m_e32']))
    vitb32quickgelu_laion400m_e32_check.configure(variable=vitb32quickgelu_laion400m_e32)
    vitb16_laion400m_e31.set(bool(json_set['ViTB16_laion400m_e31']))
    vitb16_laion400m_e31_check.configure(variable=vitb16_laion400m_e31)
    vitb16_laion400m_e32.set(bool(json_set['ViTB16_laion400m_e32']))
    vitb16_laion400m_e32_check.configure(variable=vitb16_laion400m_e32)
    rn50_yffcc15m.set(bool(json_set['RN50_yffcc15m']))
    rn50_yffcc15m_check.configure(variable=rn50_yffcc15m)
    rn50_cc12m.set(bool(json_set['RN50_cc12m']))
    rn50_cc12m_check.configure(variable=rn50_cc12m)
    rn50_quickgelu_yfcc15m.set(bool(json_set['RN50_quickgelu_yfcc15m']))
    rn50_quickgelu_yfcc15m_check.configure(variable=rn50_quickgelu_yfcc15m)
    rn50_quickgelu_yfcc15m.set(bool(json_set['RN50_quickgelu_yfcc15m']))
    rn50_quickgelu_cc12m_check.configure(variable=rn50_quickgelu_cc12m)
    rn101_yfcc15m.set(bool(json_set['RN101_yfcc15m']))
    rn101_yfcc15m_check.configure(variable=rn101_yfcc15m)
    rn101_quickgelu_yfcc15m.set(bool(json_set['RN101_quickgelu_yfcc15m']))
    rn101_quickgelu_yfcc15m_check.configure(variable=rn101_quickgelu_yfcc15m)
    symm_loss_scale.set(str(json_set['symm_loss_scale']))
    symm_loss_scale_entry.configure(textvariable=symm_loss_scale)
    symmetry_loss_v.set(str(json_set['symmetry_loss_v']))
    symmetry_loss_v_check.configure(textvariable=symmetry_loss_v)
    symmetry_loss_h.set(str(json_set['symmetry_loss_h']))
    symmetry_loss_h_check.configure(textvariable=symmetry_loss_h)
    symm_switch.set(str(json_set['symm_switch']))
    symm_switch_entry.configure(textvariable=symm_switch)
    
def fix_text():
    if prompt_scheduling == True:
        for i in prompt_steps:
            show_prompt_step(i)
            show_prompt_step(current_step)

def updater():
    if interrupt == True:
        return
    global json_set
    window.title('VisualDiffusion (a GUI for ProgRock Diffusion): '+gui_settings)
    steps_text = int(steps_entry.get())
    json_set['steps'] = steps_text
    height_text = int(height_entry.get())
    json_set['height'] = height_text
    width_text = int(width_entry.get())
    json_set['width'] = width_text
    sampling_mode_text = sampling_mode.get()
    json_set['sampling_mode'] = sampling_mode_text
    diffusion_model_text = diffusion_model.get()
    json_set['diffusion_model'] = diffusion_model_text
    skip_steps_text = int(skip_steps_entry.get())
    json_set['skip_steps'] = skip_steps_text
    clip_guidance_scale_text = clip_guidance_scale_entry.get()
    json_set['clip_guidance_scale'] = clip_guidance_scale_text
    set_seed_text = set_seed_entry.get()
    json_set['set_seed'] = set_seed_text
    eta_text = eta_entry.get()
    json_set['eta'] = eta_text
    clamp_max_text = clamp_max_entry.get()
    json_set['clamp_max'] = clamp_max_text
    cut_overview_text = cut_overview_entry.get()
    json_set['cut_overview'] = cut_overview_text
    cut_innercut_text = cut_innercut_entry.get()
    json_set['cut_innercut'] = cut_innercut_text
    cut_ic_pow_text = cut_ic_pow_entry.get()
    json_set['cut_ic_pow'] = cut_ic_pow_text
    cutn_batches_text = int(cutn_batches_entry.get())
    json_set['cutn_batches'] = cutn_batches_text
    n_batches_text = int(n_batches_entry.get())
    json_set['n_batches'] = n_batches_text
    use_secondary_model_text = bool(use_secondary_model.get())
    json_set['use_secondary_model'] = use_secondary_model_text
    fix_brightness_contrast_text = fix_brightness_contrast.get()
    json_set['fix_brightness_contrast'] = fix_brightness_contrast_text
    cut_heatmaps_text = cut_heatmaps.get()
    json_set['cut_heatmaps'] = cut_heatmaps_text
    smooth_schedules_text = smooth_schedules.get()
    json_set['smooth_schedules'] = smooth_schedules_text
    vitb16_text = vitb16.get()
    json_set['ViTB16'] = vitb16_text
    vitb32_text = vitb32.get()
    json_set['ViTB32'] = vitb32_text
    vitl14_text = vitl14.get()
    json_set['ViTL14'] = vitl14_text
    vitl14_336_text = vitl14_336.get()
    json_set['ViTL14_336'] = vitl14_336_text
    rn101_text = rn101.get()
    json_set['RN101'] = rn101_text
    rn50_text = rn50.get()
    json_set['RN50'] = rn50_text
    rn50x4_text = rn50x4.get()
    json_set['RN50x4'] = rn50x4_text
    rn50x16_text = rn50x16.get()
    json_set['RN50x16'] = rn50x16_text
    rn50x64_text = rn50x64.get()
    json_set['RN50x64'] = rn50x64_text
    vitb32_laion2b_e16_text = vitb32_laion2b_e16.get()
    json_set['ViTB32_laion2b_e16'] = vitb32_laion2b_e16_text
    vitb32_laion400m_e31_text = vitb32_laion400m_e31.get()
    json_set['ViTB32_laion400m_e31'] = vitb32_laion400m_e31_text
    vitb32_laion400m_32_text = vitb32_laion400m_32.get()
    json_set['ViTB32_laion400m_32'] = vitb32_laion400m_32_text
    vitb32quickgelu_laion400m_e31_text = vitb32quickgelu_laion400m_e31.get()
    json_set['ViTB32quickgelu_laion400m_e31'] = vitb32quickgelu_laion400m_e31_text
    vitb32quickgelu_laion400m_e32_text = vitb32quickgelu_laion400m_e32.get()
    json_set['ViTB32quickgelu_laion400m_e32'] = vitb32quickgelu_laion400m_e32_text
    vitb16_laion400m_e31_text = vitb16_laion400m_e31.get()
    json_set['ViTB16_laion400m_e31'] = vitb16_laion400m_e31_text
    vitb16_laion400m_e32_text = vitb16_laion400m_e32.get()
    json_set['ViTB16_laion400m_e32'] = vitb16_laion400m_e32_text
    rn50_yffcc15m_text = rn50_yffcc15m.get()
    json_set['RN50_yffcc15m'] = rn50_yffcc15m_text
    rn50_cc12m_text = rn50_cc12m.get()
    json_set['RN50_cc12m'] = rn50_cc12m_text
    rn50_quickgelu_yfcc15m_text = rn50_quickgelu_yfcc15m.get()
    json_set['RN50_quickgelu_yfcc15m'] = rn50_quickgelu_yfcc15m_text
    rn50_quickgelu_cc12m_text = rn50_quickgelu_cc12m.get()
    json_set['RN50_quickgelu_cc12m'] = rn50_quickgelu_cc12m_text
    rn101_yfcc15m_text = rn101_yfcc15m.get()
    json_set['RN101_yfcc15m'] = rn101_yfcc15m_text
    rn101_quickgelu_yfcc15m_text = rn101_quickgelu_yfcc15m.get()
    json_set['RN101_quickgelu_yfcc15m'] = rn101_quickgelu_yfcc15m_text
    symm_loss_scale_text = symm_loss_scale_entry.get()
    json_set['symm_loss_scale'] = symm_loss_scale_text
    symmetry_loss_v_text = symmetry_loss_v.get()
    json_set['symmetry_loss_v'] = symmetry_loss_v_text
    symmetry_loss_h_text = symmetry_loss_h.get()
    json_set['symmetry_loss_h'] = symmetry_loss_h_text
    symm_switch_text = symm_switch_entry.get()
    json_set['symm_switch'] = symm_switch_text
    if prompt_scheduling == True:
        text_prompts_button_frame.grid(row=0, column=0, sticky=NW)
        for i in prompt_steps:
            temp_prompts = []
            for k in prompt_text_entry[i].keys():
                prompt_text_entry_text = prompt_text_vars[i][k].get()
                if prompt_text_entry_text != '':
                    temp_prompts.append(prompt_text_entry_text)
                json_set['text_prompts']['0'][i] = temp_prompts
    else:
        temp_prompts = []
        t = 0
        text_prompts_button_frame.pack_forget()
        for i in prompt_text_entry.keys():
            prompt_text_entry_text = prompt_text_vars[i].get()
            if prompt_text_entry_text != '':
                temp_prompts.append(prompt_text_entry_text)
            json_set['text_prompts']['0'] = temp_prompts
            t += 1
    window.after(1000, refresh_image)

# All the frames, buttons, and text boxes for the GUI
# The frames (left and right) are all packed into the master frame
# The buttons and text boxes are all packed into the left frame
# The image is show in the right frame

# I would like to look into ways of organizing code like this better, but I need to see examples
# of how to do it. To me it seems that if you have to deliberately create each object,
# then I don't know how you'd reduce the length or clean it up.

# Master frame
window = Tk()

# Initialize style
s = ttk.Style()
# Create style used by default for all Frames
s.configure('TFrame', background='Light Blue', borderwidth=1)

# Create separate styles for the other frames
s.configure('Green.TFrame', background='Light Green', relief='ridge')
s.configure('Yellow.TFrame', background='Light Yellow', relief='ridge')
s.configure('Grey.TFrame', background='Light Grey', relief='ridge')
s.configure('Pink.TFrame', background='Pink', relief='ridge')

master_frame = ttk.Frame(window, style='TFrame')
master_frame.pack(fill=BOTH, expand=1)

left_frame = ttk.Frame(master_frame)
left_frame.pack(side=LEFT, fill=BOTH, expand=1)

left_frame_top = ttk.Frame(left_frame)
left_frame_top.pack(side=TOP, fill=BOTH, expand=1)

left_frame_bottom = ttk.Frame(left_frame)
left_frame_bottom.pack(side=BOTTOM, fill=BOTH, expand=1)

right_frame = ttk.Frame(master_frame)
right_frame.pack(side=RIGHT, fill=BOTH, expand=1)

# Left Frame
# Top Frame
basic_settings_frame = ttk.Frame(left_frame_top, style='Green.TFrame')
basic_settings_frame.pack(fill=BOTH,padx=2, pady=2)

# Middle Top Frame
advanced_settings_frame = ttk.Frame(left_frame_top, style='Yellow.TFrame')

# Clip Model Selection Frame
clip_model_frame = ttk.Frame(left_frame_top, style='Yellow.TFrame')
clip_model_top_frame = ttk.Frame(clip_model_frame)
clip_model_top_frame.pack(side=TOP, fill=BOTH, expand=1)
clip_model_bottom_frame = ttk.Frame(clip_model_frame)
clip_model_bottom_frame.pack(side=BOTTOM, fill=BOTH, expand=1)
clip_settings_frame = ttk.Frame(clip_model_top_frame, style='Pink.TFrame')
clip_settings_frame.pack(side=LEFT, fill=BOTH, padx=2, pady=2)
other_settings_frame = ttk.Frame(clip_model_top_frame, style='Green.TFrame')
other_settings_frame.pack(side=LEFT, fill=BOTH, padx=2, pady=2)
laion_settings_frame = ttk.Frame(clip_model_bottom_frame, style='Yellow.TFrame')
laion_settings_frame.pack(side=BOTTOM, fill=BOTH, padx=2, pady=2)

# Symmetry Frame
symmetry_frame = ttk.Frame(left_frame_top, style='Yellow.TFrame')

# Middle Bottom Frame
left_frame_bottom_top = ttk.Frame(left_frame_bottom)
left_frame_bottom_top.pack(side=TOP, fill=BOTH, expand=1)
text_prompts_button_frame = ttk.Frame(left_frame_bottom_top)
text_prompts_button_frame.grid(row=0, column=0, sticky=NW)
text_prompts_frame = ttk.Frame(left_frame_bottom, style='TFrame')
text_prompts_frame.pack(side=TOP, expand=1, fill=BOTH, padx=2, pady=2)

# Bottom Frame
run_frame = ttk.Frame(left_frame_bottom, style='Grey.TFrame')
run_frame.pack(fill=BOTH, expand=1, padx=2, pady=2)
# Right Frame
image_frame = ttk.Frame(right_frame)
image_frame.pack(fill=BOTH, expand=1, padx=2, pady=2)

# Basic Settings Frame
# Steps, Height, Width, Sampling Mode, Diffusion Model, 
# Simple Symmetry, Run_button, Save_button, Save_As_Button, 
# Load_button, Advanced_button, Clip_button, Symmetry_button,
# mask_button
# Settings file name
# Skip_steps, clip_guidance_scale, init_image

# Steps
steps = StringVar()
steps.set(json_set['steps'])
steps_label = ttk.Label(basic_settings_frame, text="Steps")
steps_label.grid(row=0, column=0, sticky=NW, padx=5, pady=2)
steps_entry = ttk.Entry(basic_settings_frame, textvariable=steps, width=10)
steps_entry.grid(row=0, column=1, sticky=NW, padx=5, pady=2)

# Height
height = StringVar()
height.set(json_set['height'])
height_label = ttk.Label(basic_settings_frame, text="Height")
height_label.grid(row=1, column=0, sticky=NW, padx=5, pady=2)
height_entry = ttk.Entry(basic_settings_frame, textvariable=height, width=10)
height_entry.grid(row=1, column=1, sticky=NW, padx=5, pady=2)

# Width
width = StringVar()
width.set(json_set['width'])
width_label = ttk.Label(basic_settings_frame, text="Width")
width_label.grid(row=2, column=0, sticky=NW, padx=5, pady=2)
width_entry = ttk.Entry(basic_settings_frame, textvariable=width, width=10)
width_entry.grid(row=2, column=1, sticky=NW, padx=5, pady=2)

# Sampling Mode
sampling_mode = StringVar()
sampling_mode.set(json_set['sampling_mode'])
sampling_mode_label = ttk.Label(basic_settings_frame, text="Sampling Mode")
sampling_mode_label.grid(row=0, column=2, sticky=NW, padx=5, pady=2)
sampling_mode_optionmenu = ttk.OptionMenu(basic_settings_frame, sampling_mode, json_set['sampling_mode'], 'ddim', 'plms')
sampling_mode_optionmenu.grid(row=0, column=3, sticky=NW, padx=5, pady=2)

# Diffusion Model
diffusion_model = StringVar()
diffusion_model.set(json_set['diffusion_model'])
diffusion_model_label = ttk.Label(basic_settings_frame, text="Diffusion Model")
diffusion_model_label.grid(row=1, column=2, sticky=NW, padx=5, pady=2)
diffusion_model_optionmenu = ttk.OptionMenu(basic_settings_frame, diffusion_model, json_set['diffusion_model'], 
    '512x512_diffusion_uncond_finetune_008100',
    '256x256_openai_comics_faces_by_alex_spirin', '256x256_diffusion_uncond',
    'pixel_art_diffusion_hard_256', 'pixel_art_diffusion_soft_256',
    'pixelartdiffusion4k', 'portrait_generator_v001', 'watercolordiffusion',
    'watercolordiffusion_2', 'PulpSciFiDiffusion',
    'FeiArt_Handpainted_CG_Diffusion', 'IsometricDiffusionRevrart512px')
diffusion_model_optionmenu.grid(row=1, column=3, sticky=NW, padx=5, pady=2)

# Simple Symmetry
simple_symmetry = BooleanVar()
if json_set['simple_symmetry'] == False:
    simple_symmetry.set(False)
else:
    simple_symmetry.set(True)
simple_symmetry_check = ttk.Checkbutton(basic_settings_frame, text="Simple Symmetry", variable=simple_symmetry)
simple_symmetry_check.grid(row=2, column=2, sticky=NW, padx=5, pady=2)

# Skip Steps
skip_steps = StringVar()
skip_steps.set(json_set['skip_steps'])
skip_steps_label = ttk.Label(basic_settings_frame, text="Skip Steps")
skip_steps_label.grid(row=0, column=4, sticky=NW, padx=5, pady=2)
skip_steps_entry = ttk.Entry(basic_settings_frame, textvariable=skip_steps, width=10)
skip_steps_entry.grid(row=0, column=5, sticky=NW, padx=5, pady=2)

# Clip Guidance Scale
clip_guidance_scale = StringVar()
clip_guidance_scale.set(json_set['clip_guidance_scale'])
clip_guidance_scale_label = ttk.Label(basic_settings_frame, text="Clip Guidance Scale")
clip_guidance_scale_label.grid(row=1, column=4, sticky=NW, padx=5, pady=2)
clip_guidance_scale_entry = ttk.Entry(basic_settings_frame, textvariable=clip_guidance_scale, width=10)
clip_guidance_scale_entry.grid(row=1, column=5, sticky=NW, padx=5, pady=2)

# Init Image
init_image = StringVar()
init_image.set(json_set['init_image'])
init_image_label = ttk.Label(basic_settings_frame, text=init_image.get())
init_image_label.grid(row=2, column=3, sticky=NW, padx=5, pady=2)
# Init Image Button
init_image_button = ttk.Button(basic_settings_frame, text="Init Image", command=open_image_file)
init_image_button.grid(row=2, column=5, sticky=NW, padx=5, pady=2)
# Clear Init Image Button
clear_init_image_button = ttk.Button(basic_settings_frame, text="Clear", command=clear_init_image)
clear_init_image_button.grid(row=2, column=4, sticky=NW, padx=5, pady=2)

# Buttons
# Run Button
run_button = ttk.Button(basic_settings_frame, text="Run", command=run_thread)
run_button.grid(row=0, column=6, sticky=NW, padx=5, pady=2)

# Stop Button
refresh_button = ttk.Button(basic_settings_frame, text="Refresh", command=refresh_ui)
refresh_button.grid(row=1, column=6, sticky=NW, padx=5, pady=2)

# Save Button
save_button = ttk.Button(basic_settings_frame, text="Save", command=save_settings_file)
save_button.grid(row=0, column=7, sticky=NW, padx=5, pady=2)

# Save As Button
save_as_button = ttk.Button(basic_settings_frame, text="Save As", command=save_as_settings_file)
save_as_button.grid(row=1, column=7, sticky=NW, padx=5, pady=2)

# Load Button
load_button = ttk.Button(basic_settings_frame, text="Load", command=load_settings_file)
load_button.grid(row=2, column=7, sticky=NW, padx=5, pady=2)

# Advanced Button
advanced_button = ttk.Button(basic_settings_frame, text="Advanced", command=show_advanced_settings)
advanced_button.grid(row=2, column=6, sticky=NW, padx=5, pady=2)

# Symmetry Button

# Advanced Settings Frame
# set_seed, eta, clamp_max,
# cut_overview, cut_innercut, cut_ic_pow, 
# cutn_batches, n_batches, 
# symm_loss_scale, symm_switch, symmetry_loss_h, symmetry_loss_v,
# fix_brightness_contrast, cut_heatmaps, smooth_schedules

# Set Seed
set_seed = StringVar()
set_seed.set(json_set['set_seed'])
set_seed_label = ttk.Label(advanced_settings_frame, text="Set Seed")
set_seed_label.grid(row=0, column=0, sticky=NW, padx=5, pady=2)
set_seed_entry = ttk.Entry(advanced_settings_frame, textvariable=set_seed, width=12)
set_seed_entry.grid(row=0, column=1, sticky=NW, padx=5, pady=2)

# Eta
eta = StringVar()
eta.set(json_set['eta'])
eta_label = ttk.Label(advanced_settings_frame, text="Eta")
eta_label.grid(row=1, column=0, sticky=NW, padx=5, pady=2)
eta_entry = ttk.Entry(advanced_settings_frame, textvariable=eta, width=12)
eta_entry.grid(row=1, column=1, sticky=NW, padx=5, pady=2)

# Clamp Max
clamp_max = StringVar()
clamp_max.set(json_set['clamp_max'])
clamp_max_label = ttk.Label(advanced_settings_frame, text="Clamp Max")
clamp_max_label.grid(row=2, column=0, sticky=NW, padx=5, pady=2)
clamp_max_entry = ttk.Entry(advanced_settings_frame, textvariable=clamp_max, width=12)
clamp_max_entry.grid(row=2, column=1, sticky=NW, padx=5, pady=2)

# Cut Overview
cut_overview = StringVar()
cut_overview.set(json_set['cut_overview'])
cut_overview_label = ttk.Label(advanced_settings_frame, text="Cut Overview")
cut_overview_label.grid(row=0, column=2, sticky=NW, padx=5, pady=2)
cut_overview_entry = ttk.Entry(advanced_settings_frame, textvariable=cut_overview, width=20)
cut_overview_entry.grid(row=0, column=3, sticky=NW, padx=5, pady=2)

# Cut Innercut
cut_innercut = StringVar()
cut_innercut.set(json_set['cut_innercut'])
cut_innercut_label = ttk.Label(advanced_settings_frame, text="Cut Innercut")
cut_innercut_label.grid(row=1, column=2, sticky=NW, padx=5, pady=2)
cut_innercut_entry = ttk.Entry(advanced_settings_frame, textvariable=cut_innercut, width=20)
cut_innercut_entry.grid(row=1, column=3, sticky=NW, padx=5, pady=2)

# Cut IC Pow
cut_ic_pow = StringVar()
cut_ic_pow.set(json_set['cut_ic_pow'])
cut_ic_pow_label = ttk.Label(advanced_settings_frame, text="Cut IC Pow")
cut_ic_pow_label.grid(row=2, column=2, sticky=NW, padx=5, pady=2)
cut_ic_pow_entry = ttk.Entry(advanced_settings_frame, textvariable=cut_ic_pow, width=20)
cut_ic_pow_entry.grid(row=2, column=3, sticky=NW, padx=5, pady=2)

#Cutn Batches
cutn_batches = IntVar()
cutn_batches.set(json_set['cutn_batches'])
cutn_batches_label = ttk.Label(advanced_settings_frame, text="Cutn Batches")
cutn_batches_label.grid(row=0, column=4, sticky=NW, padx=5, pady=2)
cutn_batches_entry = ttk.Entry(advanced_settings_frame, textvariable=cutn_batches, width=6)
cutn_batches_entry.grid(row=0, column=5, sticky=NW, padx=5, pady=2)

# N Batches
n_batches = IntVar()
n_batches.set(json_set['n_batches'])
n_batches_label = ttk.Label(advanced_settings_frame, text="N Batches")
n_batches_label.grid(row=1, column=4, sticky=NW, padx=5, pady=2)
n_batches_entry = ttk.Entry(advanced_settings_frame, textvariable=n_batches, width=6)
n_batches_entry.grid(row=1, column=5, sticky=NW, padx=5, pady=2)

# Use Secondary Model
use_secondary_model = BooleanVar()
use_secondary_model.set(json_set['use_secondary_model'])
use_secondary_model_check = ttk.Checkbutton(advanced_settings_frame, text="Use Secondary Model", variable=use_secondary_model)
use_secondary_model_check.grid(row=2, column=4, sticky=NW, padx=5, pady=2)

# Fix Brightness Contrast
fix_brightness_contrast = BooleanVar()
fix_brightness_contrast.set(bool(json_set['fix_brightness_contrast']))
fix_brightness_contrast_check = ttk.Checkbutton(advanced_settings_frame, text="Fix Brightness Contrast", variable=fix_brightness_contrast)
fix_brightness_contrast_check.grid(row=0, column=6, sticky=NW, padx=5, pady=2)

# Cut Heatmaps
cut_heatmaps = BooleanVar()
cut_heatmaps.set(bool(json_set['cut_heatmaps']))
cut_heatmaps_check = ttk.Checkbutton(advanced_settings_frame, text="Cut Heatmaps", variable=cut_heatmaps)
cut_heatmaps_check.grid(row=1, column=6, sticky=NW, padx=5, pady=2)

# Smooth Schedules
smooth_schedules = BooleanVar()
smooth_schedules.set(bool(json_set['smooth_schedules']))
smooth_schedules_check = ttk.Checkbutton(advanced_settings_frame, text="Smooth Schedules", variable=smooth_schedules)
smooth_schedules_check.grid(row=2, column=6, sticky=NW, padx=5, pady=2)

# Clip Button
clip_button = ttk.Button(advanced_settings_frame, text="Clip Settings", command=show_clip_settings)
clip_button.grid(row=0, column=7, sticky=NW, padx=5, pady=2)

# Clip Settings
# ViTB32, ViTB16, ViTL14, ViTL14_336, RN101, RN50, RN50x4, RN50x16, RN50x64, ViTB32_laion2b_e16, 
# ViTB32_laion400m_e31, ViTB32_laion400m_32, ViTB32quickgelu_laion400m_e31, ViTB32quickgelu_laion400m_32,
# ViTB16_laion400m_e31, ViTB16_laion400m_e32, RN50_yffcc15m, RN50_cc12m, RN50_quickgelu_yfcc15m, 
# RN50_quickgelu_cc12m, RN101_yfcc15m, RN101_quickgelu_yfcc15m

vitb32 = BooleanVar()
vitb32.set(bool(json_set['ViTB32']))
vitb32_check = ttk.Checkbutton(clip_settings_frame, text="ViTB32", variable=vitb32)
vitb32_check.grid(row=0, column=0, sticky=NW, padx=5, pady=2)

vitb16 = BooleanVar()
vitb16.set(bool(json_set['ViTB16']))
vitb16_check = ttk.Checkbutton(clip_settings_frame, text="ViTB16", variable=vitb16)
vitb16_check.grid(row=0, column=1, sticky=NW, padx=5, pady=2)

vitl14 = BooleanVar()
vitl14.set(bool(json_set['ViTL14']))
vitl14_check = ttk.Checkbutton(clip_settings_frame, text="ViTL14", variable=vitl14)
vitl14_check.grid(row=0, column=2, sticky=NW, padx=5, pady=2)

vitl14_336 = BooleanVar()
vitl14_336.set(bool(json_set['ViTL14_336']))
vitl14_336_check = ttk.Checkbutton(clip_settings_frame, text="ViTL14_336", variable=vitl14_336)
vitl14_336_check.grid(row=1, column=2, sticky=NW, padx=5, pady=2)

rn101 = BooleanVar()
rn101.set(bool(json_set['RN101']))
rn101_check = ttk.Checkbutton(clip_settings_frame, text="RN101", variable=rn101)
rn101_check.grid(row=2, column=2, sticky=NW, padx=5, pady=2)

rn50 = BooleanVar()
rn50.set(bool(json_set['RN50']))
rn50_check = ttk.Checkbutton(clip_settings_frame, text="RN50", variable=rn50)
rn50_check.grid(row=1, column=0, sticky=NW, padx=5, pady=2)

rn50x4 = BooleanVar()
rn50x4.set(bool(json_set['RN50x4']))
rn50x4_check = ttk.Checkbutton(clip_settings_frame, text="RN50x4", variable=rn50x4)
rn50x4_check.grid(row=1, column=1, sticky=NW, padx=5, pady=2)

rn50x16 = BooleanVar()
rn50x16.set(bool(json_set['RN50x16']))
rn50x16_check = ttk.Checkbutton(clip_settings_frame, text="RN50x16", variable=rn50x16)
rn50x16_check.grid(row=2, column=0, sticky=NW, padx=5, pady=2)

rn50x64 = BooleanVar()
rn50x64.set(bool(json_set['RN50x64']))
rn50x64_check = ttk.Checkbutton(clip_settings_frame, text="RN50x64", variable=rn50x64)
rn50x64_check.grid(row=2, column=1, sticky=NW, padx=5, pady=2)

vitb32_laion2b_e16 = BooleanVar()
vitb32_laion2b_e16.set(bool(json_set['ViTB32_laion2b_e16']))
vitb32_laion2b_e16_check = ttk.Checkbutton(laion_settings_frame, text="ViTB32_laion2b_e16", variable=vitb32_laion2b_e16)
vitb32_laion2b_e16_check.grid(row=0, column=0, sticky=NW, padx=5, pady=2)

vitb32_laion400m_e31 = BooleanVar()
vitb32_laion400m_e31.set(bool(json_set['ViTB32_laion400m_e31']))
vitb32_laion400m_e31_check = ttk.Checkbutton(laion_settings_frame, text="ViTB32_laion400m_e31", variable=vitb32_laion400m_e31)
vitb32_laion400m_e31_check.grid(row=0, column=1, sticky=NW, padx=5, pady=2)

vitb32_laion400m_32 = BooleanVar()     
vitb32_laion400m_32.set(bool(json_set['ViTB32_laion400m_32']))
vitb32_laion400m_32_check = ttk.Checkbutton(laion_settings_frame, text="ViTB32_laion400m_32", variable=vitb32_laion400m_32)
vitb32_laion400m_32_check.grid(row=0, column=2, sticky=NW, padx=5, pady=2)

vitb32quickgelu_laion400m_e31 = BooleanVar()
vitb32quickgelu_laion400m_e31.set(bool(json_set['ViTB32quickgelu_laion400m_e31']))
vitb32quickgelu_laion400m_e31_check = ttk.Checkbutton(laion_settings_frame, text="ViTB32quickgelu_laion400m_e31", variable=vitb32quickgelu_laion400m_e31)
vitb32quickgelu_laion400m_e31_check.grid(row=1, column=0, sticky=NW, padx=5, pady=2)

vitb32quickgelu_laion400m_e32 = BooleanVar()
vitb32quickgelu_laion400m_e32.set(bool(json_set['ViTB32quickgelu_laion400m_e32']))
vitb32quickgelu_laion400m_e32_check = ttk.Checkbutton(laion_settings_frame, text="ViTB32quickgelu_laion400m_e32", variable=vitb32quickgelu_laion400m_e32)
vitb32quickgelu_laion400m_e32_check.grid(row=1, column=1, sticky=NW, padx=5, pady=2)

vitb16_laion400m_e31 = BooleanVar()
vitb16_laion400m_e31.set(bool(json_set['ViTB16_laion400m_e31']))
vitb16_laion400m_e31_check = ttk.Checkbutton(laion_settings_frame, text="ViTB16_laion400m_e31", variable=vitb16_laion400m_e31)
vitb16_laion400m_e31_check.grid(row=1, column=2, sticky=NW, padx=5, pady=2)

vitb16_laion400m_e32 = BooleanVar()
vitb16_laion400m_e32.set(bool(json_set['ViTB16_laion400m_e32']))
vitb16_laion400m_e32_check = ttk.Checkbutton(laion_settings_frame, text="ViTB16_laion400m_e32", variable=vitb16_laion400m_e32)
vitb16_laion400m_e32_check.grid(row=1, column=3, sticky=NW, padx=5, pady=2)

rn50_yffcc15m = BooleanVar()
rn50_yffcc15m.set(bool(json_set['RN50_yffcc15m']))
rn50_yffcc15m_check = ttk.Checkbutton(other_settings_frame, text="RN50_yffcc15m", variable=rn50_yffcc15m)
rn50_yffcc15m_check.grid(row=0, column=0, sticky=NW, padx=5, pady=2)

rn50_cc12m = BooleanVar()
rn50_cc12m.set(bool(json_set['RN50_cc12m']))
rn50_cc12m_check = ttk.Checkbutton(other_settings_frame, text="RN50_cc12m", variable=rn50_cc12m)
rn50_cc12m_check.grid(row=0, column=1, sticky=NW, padx=5, pady=2)

rn50_quickgelu_yfcc15m = BooleanVar()
rn50_quickgelu_yfcc15m.set(bool(json_set['RN50_quickgelu_yfcc15m']))
rn50_quickgelu_yfcc15m_check = ttk.Checkbutton(other_settings_frame, text="RN50_quickgelu_yfcc15m", variable=rn50_quickgelu_yfcc15m)
rn50_quickgelu_yfcc15m_check.grid(row=1, column=0, sticky=NW, padx=5, pady=2)

rn50_quickgelu_cc12m = BooleanVar()
rn50_quickgelu_cc12m.set(bool(json_set['RN50_quickgelu_cc12m']))
rn50_quickgelu_cc12m_check = ttk.Checkbutton(other_settings_frame, text="RN50_quickgelu_cc12m", variable=rn50_quickgelu_cc12m)
rn50_quickgelu_cc12m_check.grid(row=1, column=1, sticky=NW, padx=5, pady=2)

rn101_yfcc15m = BooleanVar()
rn101_yfcc15m.set(bool(json_set['RN101_yfcc15m']))
rn101_yfcc15m_check = ttk.Checkbutton(other_settings_frame, text="RN101_yfcc15m", variable=rn101_yfcc15m)
rn101_yfcc15m_check.grid(row=2, column=0, sticky=NW, padx=5, pady=2)

rn101_quickgelu_yfcc15m = BooleanVar()
rn101_quickgelu_yfcc15m.set(bool(json_set['RN101_quickgelu_yfcc15m']))
rn101_quickgelu_yfcc15m_check = ttk.Checkbutton(other_settings_frame, text="RN101_quickgelu_yfcc15m", variable=rn101_quickgelu_yfcc15m)
rn101_quickgelu_yfcc15m_check.grid(row=2, column=1, sticky=NW, padx=5, pady=2)

# Symmetry Button
symmetry_button = ttk.Button(advanced_settings_frame, text="Symmetry Settings", command=show_symmetry_settings)
symmetry_button.grid(row=1, column=7, sticky=NW, padx=5, pady=2)

# Symmetry Settings
# symmetry_loss_v, symmetry_loss_h, symm_loss_scale, symm_switch
symmetry_loss_v = BooleanVar()
symmetry_loss_v.set(bool(json_set['symmetry_loss_v']))
symmetry_loss_v_check = ttk.Checkbutton(symmetry_frame, text="symmetry_loss_v", variable=symmetry_loss_v)
symmetry_loss_v_check.grid(row=0, column=0, sticky=NW, padx=5, pady=2)

symmetry_loss_h = BooleanVar()
symmetry_loss_h.set(bool(json_set['symmetry_loss_h']))
symmetry_loss_h_check = ttk.Checkbutton(symmetry_frame, text="symmetry_loss_h", variable=symmetry_loss_h)
symmetry_loss_h_check.grid(row=0, column=1, sticky=NW, padx=5, pady=2)

symm_loss_scale = StringVar()
symm_loss_scale.set(json_set['symm_loss_scale'])
symm_loss_scale_label = ttk.Label(symmetry_frame, text="symm_loss_scale")
symm_loss_scale_label.grid(row=0, column=2, sticky=NW, padx=5, pady=2)
symm_loss_scale_entry = ttk.Entry(symmetry_frame, textvariable=symm_loss_scale, width=20)
symm_loss_scale_entry.grid(row=0, column=3, sticky=NW, padx=5, pady=2)

symm_switch = StringVar()
symm_switch.set(json_set['symm_switch'])
symm_switch_label = ttk.Label(symmetry_frame, text="symm_switch")
symm_switch_label.grid(row=0, column=4, sticky=NW, padx=5, pady=2)
symm_switch_entry = ttk.Entry(symmetry_frame, textvariable=symm_switch, width=20)
symm_switch_entry.grid(row=0, column=5, sticky=NW, padx=5, pady=2)


# Text Prompts Frame
# Text Prompts

# Declare the variables for the text prompts
prompt_text_box_label = {}
prompt_text_entry = {}
prompt_text_vars = {}
current_step = '0'

def set_prompt_text():
    global prompt_scheduling
    global prompt_text
    try:
        if json_set['text_prompts']['0']['0']:
            prompt_scheduling = True
            prompt_text = json_set['text_prompts']['0']
            print('Prompt Scheduling is Enabled')
    except:
        prompt_scheduling = False
        prompt_text = []
        prompt_text = json_set['text_prompts']['0']
        print('Prompt Scheduling is Disabled')

def get_prompts():
    global interrupt
    try:
        cleanup()
    except:
        pass
    global prompt_text
    global prompt_steps
    global prompt_scheduling
    global prompt_steps_frame
    global prompt_text_entry
    global prompt_text_vars
    global prompts_frame
    global prompt_step_button
    global new_prompt_button
    # global new_step_button
    set_prompt_text()
    prompts_frame = ttk.Frame(text_prompts_frame)
    prompts_frame.pack(side=TOP, fill=X, expand=True)
    prompts_frame_top = ttk.Frame(prompts_frame, style='Gray.TFrame')
    prompts_frame_top.grid(row=0, column=0, sticky=NW, padx=5, pady=2)
    new_prompt_button = ttk.Button(prompts_frame_top, text="New Prompt", command=new_prompt)
    new_prompt_button.grid(row=0, column=0, sticky=NW, padx=5, pady=2)
    #new_step_button = ttk.Button(prompts_frame_top, text="New Step", command=lambda: new_step(new_step_text.get()))
    #new_step_button.grid(row=0, column=1, sticky=NW, padx=5, pady=2)
    #new_step_text = StringVar()
    #new_step_entry = ttk.Entry(prompts_frame_top, textvariable=new_step_text, width=20)
    #new_step_entry.grid(row=0, column=2, sticky=NW, padx=5, pady=2)
    if prompt_scheduling == True:
        prompt_steps = list(prompt_text.keys())
        prompt_steps_frame = {}
        prompt_step_button = {}
        text_prompts_button_frame.grid(row=0, column=0, sticky=NW, padx=5, pady=2)
        for k in prompt_steps:
            prompt_text_box_label[k] = {}
            prompt_text_entry[k] = {}
            prompt_text_vars[k] = {}
            prompt_step_button[k] = ttk.Button(text_prompts_button_frame, text="Step " + k, command=lambda k=k: show_prompt_step(k))
            prompt_step_button[k].pack(side=LEFT, padx=5, pady=2)
            prompt_steps_frame[k] = ttk.Frame(prompts_frame)
            prompt_steps_frame[k].grid(row=1, column=0, sticky=NW, padx=5, pady=2)
            for j in range(len(prompt_text[k])):
                prompt_text_box_label[k][j] = ttk.Label(prompt_steps_frame[k], text="Prompt " + str(j+1))
                prompt_text_box_label[k][j].pack(side=TOP, anchor=NW, padx=5, pady=2)
                prompt_text_vars[k][j] = StringVar()
                prompt_text_vars[k][j].set(prompt_text[k][j])
                prompt_text_entry[k][j] = Entry(prompt_steps_frame[k], textvariable=prompt_text_vars[k][j], width=150)
                prompt_text_entry[k][j].pack(side=TOP, padx=5, pady=2)
        prompt_steps_frame['0'].grid(row=1, column=0, sticky=NW, padx=5, pady=2)
    else:
        prompt_steps = ['0']
        prompt_steps_frame = {}
        text_prompts_button_frame.grid_forget()
        prompt_steps_frame['0'] = ttk.Frame(prompts_frame)
        t = 0
        for k in prompt_text:
            prompt_text_vars[t] = StringVar()
            prompt_text_vars[t].set(k)
            prompt_text_box_label[t] = ttk.Label(prompt_steps_frame['0'], text="Prompt " + str(t+1)+":")
            prompt_text_box_label[t].pack(side=TOP, anchor=NW, padx=5, pady=2)
            prompt_text_entry[t] = Entry(prompt_steps_frame['0'], textvariable=prompt_text_vars[t], width=150)
            prompt_text_entry[t].pack(side=TOP, anchor=NW, padx=5, pady=2)
            t += 1
        prompt_steps_frame['0'].grid(row=1, column=0, sticky=NW, padx=5, pady=2)
    show_prompt_step(current_step)

def new_prompt():
    global prompt_text_vars
    global prompt_text_entry
    global prompt_text_box_label
    if prompt_scheduling == True:
        prompt_text_vars[current_step][len(prompt_text_vars[current_step])] = StringVar()
        prompt_text_vars[current_step][len(prompt_text_vars[current_step])-1].set('')
        prompt_text_box_label[current_step][len(prompt_text_vars[current_step])-1] = ttk.Label(prompt_steps_frame[current_step], text="Prompt " + str(len(prompt_text_vars[current_step])))
        prompt_text_box_label[current_step][len(prompt_text_vars[current_step])-1].pack(side=TOP, anchor=NW, padx=5, pady=2)
        prompt_text_entry[current_step][len(prompt_text_vars[current_step])-1] = Entry(prompt_steps_frame[current_step], textvariable=prompt_text_vars[current_step][len(prompt_text_vars[current_step])-1], width=150)
        prompt_text_entry[current_step][len(prompt_text_vars[current_step])-1].pack(side=TOP, padx=5, pady=2)
    else:
        prompt_text_vars[len(prompt_text_vars)] = StringVar()
        prompt_text_vars[len(prompt_text_vars)-1].set('')
        prompt_text_box_label[len(prompt_text_vars)-1] = ttk.Label(prompt_steps_frame['0'], text="Prompt " + str(len(prompt_text_vars)))
        prompt_text_box_label[len(prompt_text_vars)-1].pack(side=TOP, anchor=NW, padx=5, pady=2)
        prompt_text_entry[len(prompt_text_vars)-1] = Entry(prompt_steps_frame['0'], textvariable=prompt_text_vars[len(prompt_text_vars)-1], width=150)
        prompt_text_entry[len(prompt_text_vars)-1].pack(side=TOP, padx=5, pady=2)
'''
def new_step(step):
    global prompt_text_vars
    global prompt_text_entry
    global prompt_text_box_label
    global prompt_step_button
    global prompt_steps_frame
    global current_step
    global prompt_steps
    prompt_steps.append(str(len(prompt_steps)))
    prompt_text_vars[str(len(prompt_steps))] = {}
    prompt_text_entry[str(len(prompt_steps))] = {}
    prompt_text_box_label[str(len(prompt_steps))] = {}
    prompt_step_button[str(len(prompt_steps))] = ttk.Button(text_prompts_button_frame, text="Step " + str(step), command=lambda k=str(len(prompt_steps)): show_prompt_step(k))
    prompt_step_button[str(len(prompt_steps))].pack(side=LEFT, padx=5, pady=2)
    prompt_steps_frame[str(len(prompt_steps))] = ttk.Frame(prompts_frame)
    prompt_steps_frame[str(len(prompt_steps))].grid(row=1, column=0, sticky=NW, padx=5, pady=2)
    prompt_text_vars[str(len(prompt_steps))][0] = StringVar()
    prompt_text_vars[str(len(prompt_steps))][0].set('')
    prompt_text_box_label[str(len(prompt_steps))][0] = ttk.Label(prompt_steps_frame[str(len(prompt_steps))], text="Prompt 1")
    prompt_text_box_label[str(len(prompt_steps))][0].pack(side=TOP, anchor=NW, padx=5, pady=2)
    prompt_text_entry[str(len(prompt_steps))][0] = Entry(prompt_steps_frame[str(len(prompt_steps))], textvariable=prompt_text_vars[str(len(prompt_steps))][0], width=150)
    prompt_text_entry[str(len(prompt_steps))][0].pack(side=TOP, padx=5, pady=2)
    show_prompt_step(str(len(prompt_steps)))
'''

def cleanup():
    # Delete the old UI elements and frames
    # Entry, Frame, Label, Button for the text prompts
    global prompt_text_box_label
    global prompt_text_entry
    global prompt_text_vars
    global prompt_steps_frame
    global prompts_frame
    global text_prompts_button_frame
    global prompt_steps
    global prompt_text
    global prompt_scheduling
    new_prompt_button.destroy()
    # new_step_button.destroy()
    prompt_text_vars = {}
    if prompt_scheduling == True:
        for k in prompt_steps:
            for j in prompt_text_box_label[k]:
                prompt_text_box_label[k][j].destroy()
                prompt_text_entry[k][j].destroy()
                prompt_step_button[k].destroy()
                prompt_text_vars = {}
                prompt_steps_frame[k].destroy()
    else:
        for k in prompt_text_box_label:
            try:
                prompt_text_box_label[k].destroy()
                prompt_text_entry[k].destroy()
            except:
                pass
            prompt_text_vars = {}
            prompt_steps_frame['0'].destroy()
    try:
        for i in prompt_steps:
            prompt_step_button[i].destroy()
    except:
        pass
    prompts_frame.destroy()



def show_prompt_step(step):
    global current_step
    try:
        prompt_steps_frame[current_step].grid_forget()
    except:
        pass
    current_step = step
    prompt_steps_frame[current_step].grid(row=1, column=0, sticky=NW, padx=5, pady=2)
    window.update()


get_prompts()
updater()
fix_text()
show_image()

# Run Frame
# Create scrolling text output from the shell
term_frame = ttk.Frame(run_frame, height=150)
term_frame.pack_propagate(0)
term_frame.pack(expand=True, fill='both')

term_text = Text(term_frame, height=150)
term_text.pack(side='left', fill='both', expand=True)

scrollbar = Scrollbar(term_frame)
scrollbar.pack(side='right', fill='y')

term_text['yscrollcommand'] = scrollbar.set
scrollbar['command'] = term_text.yview

old_stdout = sys.stdout    
sys.stdout = Redirect(term_text)





window.mainloop()

# - after close window -

sys.stdout = old_stdout
