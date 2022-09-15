from tkinter import *
from tkinter import ttk
from types import SimpleNamespace
from PIL import Image
import collections
import json5 as json
import os
import subprocess
import threading
import shlex
import glob


# File Names
prompts_file = './settings/prompts.txt'
gui_settings = 'gui_settings.json'
job_file = 'job_cuda_0.json'
default_settings_file = 'settings.json'


default_prompt =    ["A very beautiful symmetric portrait of a :10.0 ",
                    "<Female|Female|Female|Male|Humanoid|Synth|Alien|Primitive>:9.0 ", 
                    " <Warrior|King|Wizard|Giant|Dwarf|Swordsman|Robot|Eternal Being>:10.0 ", 
                    "of <doom|gloom|death|light|the mind|life|grief|joy|sorrow>:6.0 ",
                    "in <Space|the Desert|the Jungle|the Forest|the Mountains|the City|Underwater>:10.0 ",
                    '<overexposed|overcast|sunny|rainy|snowy|clear|bright|gloomy|vibrant|dark|sunspots|colorful>:10.0', 
                    '<steampunk|synthwave|gothic|dark fantasy|cyberpunk|psychedellic|fractal|vector|concept art|graphic art|octane render>:6.5',
                    "<Beeple|Tyler Edlin|Greg Rutkowski|Alex Grey>:6.5",
                    "<Arik Bauer|Thomas Kinkade|Peter Mohrbacher>:11.5", 
                    "trending on ArtStation:15 ", 
                    "trending on <Flickr|ConceptArtWorld|Flickr|500px|Behance|DeviantArt|Pixiv|cgsociety>:7.5",
                    '<magic the gathering|dungeons and dragons|star wars|transhumanism>:7.0', 
                    "<blur|film grain|out of focus>:-2"]

# First Run Check Variables
is_running = False
has_run = False
interrupt = False
prompt_list = []

# Load Settings from JSON
def load_json_file():
    global json_set
    global default_settings
    if not os.path.exists('./settings'):
        os.mkdir('./settings')
    if os.path.exists('./settings/'+gui_settings):
        with open('./settings/'+gui_settings, 'r') as f:
            json_set = json.load(f)
    else: # Load Default Settings
        with open(default_settings_file, 'r') as f:
            default_settings = json.load(f)
            json_set = default_settings
    json_set = SimpleNamespace(**json_set)

def load_txt_file():
    global prompt_weight
    global prompt_list
    global batches_list
    prompt_weight = {}
    prompt_list = {}
    batches_list = {}
    if os.path.exists('./settings/gudpics.txt'):
        try:
            with open('./settings/gudpics.txt') as f:
                # Count how many times the each different prompt is repeated in the file
                c = collections.Counter(f.readlines())
                i = 0
                for k, v in c.items():
                    prompt_list[i] = k.strip()
                    batches_list[i] = int(v)
                    i += 1
                print("Prompts loaded")
        except:
            print("Error loading prompts.txt")
            print("Loading from Defaults...")
            a = f.split(':')
            t = 0
            # Find the first space after the colon
            # and remove the space and everything before it
            del a[-1:]
            for i in a:
                b = i.find(' ')
                a[t] = i[b+1:]
                t += 1
            temp = '\n'.join([i for i in a])
            prompt_list[0] = temp
    else:
        print("No prompts.txt file found")
        # Create default txt file
        with open('./settings/gudpics.txt', 'w') as f:
            for i in range(len(default_prompt)):
                f.write(default_prompt[i])
                f.write('\n')
            print("Created default prompts.txt")
        c = collections.Counter(f.readlines())
        i = 0
        for k, v in c.items():
            prompt_list[i] = k.strip()
            batches_list[i] = int(v)
            i += 1
        print("Prompts loaded")
    for k in prompt_list:
        i = 0
        if ':' in prompt_list[k]:
            a = prompt_list[k].split(':')
            del a[:-1]
            prompt_weight[k] = float(str(a[:1]).strip().replace("'",'').replace('[','').replace(']',''))
            prompt_list[k] = prompt_list[k].split(':', 1)[0]
            i += 1


def set_variables():
    global prompt
    global batch_name
    global width
    global height
    global steps
    global scale
    global seed
    global frozen_seed
    global n_batches
    global n_iter
    global variance
    global init_image
    global init_strength
    global gobig_maximize
    global gobig_overlap
    global method
    global eta
    global from_file
    global cool_down
    global use_jpg
    global save_settings
    global gobig
    global prompts_file
    global json_set
    # Set Variables
    # batch_name, width, height, steps, scale, seed, 
    # n_batches, n_iter, init_image, init_strength,
    # gobig_maximize, gobig_overlap, method, eta, from_file, cool_down
    load_txt_file()
    load_json_file()
    batch_name = json_set.batch_name
    width = json_set.width
    height = json_set.height
    steps = json_set.steps
    scale = json_set.scale
    seed = json_set.seed
    n_iter = json_set.n_iter
    init_image = json_set.init_image
    init_strength = json_set.init_strength
    gobig_maximize = json_set.gobig_maximize
    gobig_overlap = json_set.gobig_overlap
    method = json_set.method
    eta = json_set.eta
    from_file = json_set.from_file
    cool_down = json_set.cool_down
    use_jpg = json_set.use_jpg
    try:
        frozen_seed = json_set.frozen_seed
        save_settings = json_set.save_settings
        variance = json_set.variance
    except:
        frozen_seed = False
        save_settings = False
        variance = 0.1
    try:
        gobig = json_set.gobig
    except:
        gobig = False
    try:
        method = json_set.method
    except:
        method = 'k_dpm_2_ancestral'
    # Count total number of lines in the file
    try:
        with open('./settings/prompts.txt') as f:
            total_lines = sum(1 for line in f)
            n_batches = total_lines
    except:
        n_batches = 1


def draw_main_window():
    global window
    global master_frame
    global main_frame
    global prompt_frame
    global prompt_text_frame
    global progress_frame
    global s
    global prompt
    global prompt_list
    global prompt_label
    global prompt_entry

    # Draw Main Window
    window = Tk()
    window.title('VisualDiffusion (MakeGUDPICS Update for ProgRock-Stable): '+batch_name+' '+gui_settings)

    
    # Add Style for Frames
    s = ttk.Style()
    s.configure('TFrame', background='Light Blue')
    s.configure('Green.TFrame', background='Light Green', relief='ridge')
    
    # Draw Master Frame
    master_frame = ttk.Frame(window, style='TFrame')
    master_frame.pack(fill=BOTH, expand=True)

    # Draw Main Frame
    main_frame = ttk.Frame(master_frame, style='TFrame')
    main_frame.pack(side=LEFT, fill='x', expand=True, anchor=NW)
    
    # Draw Calls
    #set_variables()
    draw_basic()
    draw_prompts()
    draw_progress()
    draw_shell()

def draw_basic():
    global batch_name_str
    global width_scale
    global width_str
    global height_scale
    global steps_scale
    global scale_scale
    global seed_entry
    global n_batches_entry
    global gobig_maximize_str
    global gobig_overlap_entry
    global method_str
    global n_iter_entry
    global cool_down_entry
    global use_jpg_str
    global gobig_str
    global variance_str
    global save_settings_str
    global frozen_seed_str

    # Draw Basic Settings Frame
    basic_settings_frame = ttk.Frame(main_frame, style='TFrame')
    basic_settings_frame.pack(fill='both', expand=True)

    # Draw Basic Buttons Frame
    basic_buttons_frame = ttk.Frame(basic_settings_frame, style='TFrame')
    basic_buttons_frame.pack(side=TOP, fill='both', expand=True)

    # Draw Save Button
    save_button = ttk.Button(basic_buttons_frame, text='Save', command=lambda: save_prompts(True))
    save_button.pack(side=LEFT, fill='both', expand=True)

    # Draw Run Button

    run_button = ttk.Button(basic_buttons_frame, text='Run', command=lambda: save_prompts(False))
    run_button.pack(side=LEFT, fill='both', expand=True)

    # Draw Basic Settings Entry Frame
    basic_settings_entry_frame = ttk.Frame(basic_settings_frame, style='TFrame')
    basic_settings_entry_frame.pack(side=TOP, fill='both', expand=True)
    # Draw Width Entry

    width_str = StringVar()
    width_str.set(width)
    width_label = ttk.Label(basic_settings_entry_frame, text='Width:')
    width_label.grid(row=0, column=2, sticky=NW)
    width_scale = Scale(basic_settings_entry_frame, from_=256, to=1024, orient=HORIZONTAL, variable=width_str, resolution=64, length=118)
    width_scale.grid(row=0, column=3,sticky=NW)
    # Draw Height Entry
    height_str = StringVar()
    height_str.set(height)
    height_label = ttk.Label(basic_settings_entry_frame, text='Height:')
    height_label.grid(row=0, column=0, sticky=NW)
    height_scale = Scale(basic_settings_entry_frame, from_=256, to=1024, orient=HORIZONTAL, variable=height_str, resolution=64, length=118)
    height_scale.grid(row=0, column=1,sticky=NW)
    # Draw Steps Entry
    steps_str = StringVar()
    steps_str.set(steps)
    steps_label = ttk.Label(basic_settings_entry_frame, text='Steps:')
    steps_label.grid(row=1, column=0, sticky=NW)
    steps_scale = Scale(basic_settings_entry_frame, from_=15, to=100, orient=HORIZONTAL, variable=steps_str, resolution=5, length=118)
    steps_scale.grid(row=1, column=1,sticky=NW)
    # Draw Batches Entry
    n_batches_str = StringVar()
    n_batches_str.set(n_batches)
    n_batches_label = ttk.Label(basic_settings_entry_frame, text='Batches:')
    n_batches_label.grid(row=0, column=4, sticky=NW)
    n_batches_entry = Entry(basic_settings_entry_frame, textvariable=n_batches_str)
    n_batches_entry.grid(row=0, column=5, sticky=NW)
    # Draw Variance Entry
    variance_str = StringVar()
    variance_str.set(variance)
    variance_label = ttk.Label(basic_settings_entry_frame, text='Variance:')
    variance_label.grid(row=1, column=9, sticky=NW)
    variance_entry = Entry(basic_settings_entry_frame, textvariable=variance_str)
    variance_entry.grid(row=1, column=10, sticky=NW)
    # Draw Scale Entry
    scale_str = StringVar()
    scale_str.set(scale)
    scale_label = ttk.Label(basic_settings_entry_frame, text='Scale:')
    scale_label.grid(row=1, column=2, sticky=NW)
    scale_scale = Scale(basic_settings_entry_frame, from_=1.0, to=20.0, orient=HORIZONTAL, variable=scale_str, resolution=0.5, length=118)
    scale_scale.grid(row=1, column=3,sticky=NW)
    # Draw n_iter Entry
    n_iter_str = StringVar()
    n_iter_str.set(n_iter)
    n_iter_label = ttk.Label(basic_settings_entry_frame, text='n_iter:')
    n_iter_label.grid(row=1, column=4, sticky=NW)
    n_iter_entry = Entry(basic_settings_entry_frame, textvariable=n_iter_str)
    n_iter_entry.grid(row=1, column=5, sticky=NW)
    # Draw gobig Checkbutton
    gobig_str = BooleanVar()
    gobig_str.set(gobig)
    gobig_checkbutton = ttk.Checkbutton(basic_settings_entry_frame, text='Gobig', variable=gobig_str)
    gobig_checkbutton.grid(row=0, column=7, sticky=NW)
    # Maximize Checkbutton
    gobig_maximize_str = BooleanVar()
    gobig_maximize_str.set(gobig_maximize)
    gobig_maximize_checkbutton = ttk.Checkbutton(basic_settings_entry_frame, text='GoBig Maximize', variable=gobig_maximize_str)
    gobig_maximize_checkbutton.grid(row=0, column=8, sticky=NW)
    # Draw gobig_overlap Entry
    gobig_overlap_str = StringVar()
    gobig_overlap_str.set(gobig_overlap)
    gobig_overlap_label = ttk.Label(basic_settings_entry_frame, text='Gobig Overlap:')
    gobig_overlap_label.grid(row=1, column=7, sticky=NW)
    gobig_overlap_entry = Entry(basic_settings_entry_frame, textvariable=gobig_overlap_str)
    gobig_overlap_entry.grid(row=1, column=8, sticky=NW)
    # Draw method OptionMenu
    # Options: ['k_lms', 'k_dpm_2_ancestral', 'k_dpm_2', 'k_heun', 'k_euler_ancestral', 'k_euler', 'ddim']
    method_str = StringVar()
    method_str.set(method)
    method_label = ttk.Label(basic_settings_entry_frame, text='Diffusion Method:')
    method_label.grid(row=0, column=9, sticky=NW)
    method_optionmenu = OptionMenu(basic_settings_entry_frame, method_str, 'k_lms', 'k_dpm_2_ancestral', 'k_dpm_2', 'k_heun', 'k_euler_ancestral', 'k_euler', 'ddim')
    method_optionmenu.grid(row=0, column=10, sticky=NW)
    # Draw seed Entry
    seed_str = StringVar()
    seed_str.set(seed)
    seed_label = ttk.Label(basic_settings_entry_frame, text='seed:')
    seed_label.grid(row=2, column=4, sticky=NW)
    seed_entry = Entry(basic_settings_entry_frame, textvariable=seed_str)
    seed_entry.grid(row=2, column=5, sticky=NW)
    # Draw cool_down Entry
    cool_down_str = StringVar()
    cool_down_str.set(cool_down)
    cool_down_label = ttk.Label(basic_settings_entry_frame, text='Cool Down:')
    cool_down_label.grid(row=2, column=2, sticky=NW)
    cool_down_entry = Entry(basic_settings_entry_frame, textvariable=cool_down_str)
    cool_down_entry.grid(row=2, column=3, sticky=NW)
    # Draw use_jpg Checkbutton
    use_jpg_str = BooleanVar()
    use_jpg_str.set(use_jpg)
    use_jpg_checkbutton = ttk.Checkbutton(basic_settings_entry_frame, text='Use JPG', variable=use_jpg_str)
    use_jpg_checkbutton.grid(row=2, column=10, sticky=NW)
    # Draw save_settings Checkbutton
    save_settings_str = BooleanVar()
    save_settings_str.set(save_settings)
    save_settings_checkbutton = ttk.Checkbutton(basic_settings_entry_frame, text='Save Settings', variable=save_settings_str)
    save_settings_checkbutton.grid(row=2, column=8, sticky=NW)
    # Draw frozen_seed Checkbutton
    frozen_seed_str = BooleanVar()
    frozen_seed_str.set(frozen_seed)
    frozen_seed_checkbutton = ttk.Checkbutton(basic_settings_entry_frame, text='Frozen Seed', variable=frozen_seed_str)
    frozen_seed_checkbutton.grid(row=2, column=9, sticky=NW)
    # Draw Batch Name Entry
    batch_name_str = StringVar()
    batch_name_str.set(batch_name)
    batch_name_label = ttk.Label(basic_settings_entry_frame, text='Batch Name:')
    batch_name_label.grid(row=2, column=0, sticky=NW)
    batch_name_entry = Entry(basic_settings_entry_frame, textvariable=batch_name_str)
    batch_name_entry.grid(row=2, column=1, sticky=NW)

def draw_prompts():
    global prompt_list
    global batches_list
    global prompt
    global prompt_label
    global prompt_entry
    global prompt_frame
    global prompt_text_frame
    global prompt_button_frame
    global new_prompt_button
    global delete_prompt_button
    global prompt_weight
    global prompt_weight_str
    global prompt_weight_label
    global prompt_weight_scale
    global prompt_text_weights_frame

    # Draw Prompt Frame
    prompt_frame = ttk.Frame(main_frame, style='Green.TFrame')
    prompt_frame.pack(side='top', fill='x', expand=True)

    # Draw Prompt Button Frame
    prompt_button_frame = ttk.Frame(main_frame, style='TFrame')
    prompt_button_frame.pack(side=LEFT, fill='x', expand=True)

    # Draw New Prompt Button
    new_prompt_button = ttk.Button(prompt_button_frame, text='New Prompt', command=new_prompt)
    new_prompt_button.pack(side=LEFT, fill='both', expand=True)

    # Draw Delete Prompt Button
    delete_prompt_button = ttk.Button(prompt_button_frame, text='Delete Prompt', command=delete_prompt)
    delete_prompt_button.pack(side=LEFT, fill='both', expand=True)

    # Draw Prompt Text Frame
    prompt_text_frame = ttk.Frame(prompt_frame, style='TFrame')
    prompt_text_frame.pack(side=RIGHT, fill='both', expand=True)

    # Draw Prompt Text Batches Frame
    prompt_text_weights_frame = ttk.Frame(prompt_text_frame, style='TFrame')
    prompt_text_weights_frame.pack(side=RIGHT, fill='both', expand=True)


    # Draw Text Entry Box(es)
    # Scene/Setting/Medium/Style
    prompt = {}
    prompt_label = {}
    prompt_entry = {}
    prompt_weight_str = {}
    prompt_weight_label = {}
    prompt_weight_scale = {}
    for i in range(len(batches_list)):
        prompt[i] = StringVar()
        prompt[i].set(prompt_list[i])
        prompt_label[i] = Label(prompt_text_frame, text='Prompt '+str(i+1)+':', width=100, anchor=NW)
        prompt_label[i].pack(side=TOP, fill='both', expand=True)
        prompt_entry[i] = Entry(prompt_text_frame, textvariable=prompt[i])
        prompt_entry[i].pack(side=TOP, fill='both', expand=True)
        # Draw Prompt Weight Slider
        prompt_weight_str[i] = DoubleVar()
        prompt_weight_str[i].set(prompt_weight[i])
        prompt_weight_scale[i] = Scale(prompt_text_weights_frame, variable=prompt_weight_str[i], from_=-5, to=15, resolution=0.5, orient=HORIZONTAL, length=200)
        prompt_weight_scale[i].pack(side=TOP, fill='both', expand=True)


def draw_progress():
    global progress_frame
    
    # Draw Progress Frame
    progress_frame = ttk.Frame(master_frame, style='Green.TFrame')
    progress_frame.pack(side=RIGHT, fill='both', expand=True)

def draw_shell():
    global shell_frame

    # Draw Shell Frame
    shell_frame = ttk.Frame(master_frame, style='Green.TFrame')
    shell_frame.pack(side=BOTTOM, fill=BOTH, expand=True)


def save_prompts(save):
    global from_file
    # Get Entry Boxes and save to prompt_list
    for i in range(len(prompt_list)):
        prompt[i].set(prompt_entry[i].get())
        prompt_weight_str[i].set(prompt_weight_scale[i].get())
    batch_name = batch_name_str.get()
    width = int(width_scale.get())
    height = int(height_scale.get())
    steps = int(steps_scale.get())
    scale = float(scale_scale.get())
    frozen_seed = bool(frozen_seed_str.get())
    seed = get_int_or_rdm(seed_entry.get())
    n_batches = 1
    n_iter = int(n_iter_entry.get())
    variance = float(variance_str.get())
    init_image = None
    init_strength = 0.62
    gobig_maximize = bool(gobig_maximize_str.get())
    gobig_overlap = int(gobig_overlap_entry.get())
    method = str(method_str.get())
    from_file = './settings/prompts.txt'
    cool_down = float(cool_down_entry.get())
    use_jpg = bool(use_jpg_str.get())
    save_settings = bool(save_settings_str.get())
    gobig = bool(gobig_str.get())

    # Save Prompt List to prompt.txt
    with open('./settings/prompts.txt', 'w+') as f:
        # Write prompts and weights to file all on single line with a ':' between them
        t = 0
        while t < int(n_batches_entry.get()):
            for i in range(len(prompt_list)):
                f.write(prompt[i].get()+':'+str(prompt_weight_str[i].get()) + ' ')
            f.write('\n')
            t += 1
    with open('./settings/gudpics.txt', 'w') as f:
        for i in range(len(prompt_list)):
            f.write(prompt[i].get()+':'+str(prompt_weight_str[i].get()) + ' ')
            f.write('\n')
    # Save Settings to prompt_N.json
    i = 0
    json_set = {'prompt': prompt_list[0], 'batch_name': batch_name, 'width': width, 'height': height, 'steps': steps, 'scale': scale, 'seed': seed, 'n_batches': n_batches, 'n_iter': n_iter, 'init_image': init_image, 'init_strength': init_strength, 'gobig_maximize': gobig_maximize, 'gobig_overlap': gobig_overlap, 'method': method, 'eta': eta, 'from_file': from_file, 'cool_down': cool_down, 'use_jpg': use_jpg, 'gobig': gobig, 'variance': variance, 'frozen_seed': frozen_seed, 'save_settings': save_settings}
    with open('prompt_'+str(i)+'.json', 'w+') as f:
        json.dump(json_set, f)
        f.close()
    print('Saved Prompts')
    print('Saved Settings')
    if save == True:
        with open('./settings/'+gui_settings, 'w+', encoding='utf_8') as f:
            json.dump(json_set, f, ensure_ascii=False, indent=4)
    else:
        with open('./settings/'+gui_settings, 'w+', encoding='utf_8') as f:
            json.dump(json_set, f, ensure_ascii=False, indent=4)
        with open(job_file, 'w+', encoding='utf_8') as f:
            json.dump(json_set, f, ensure_ascii=False, indent=4)
        print('Running job')
    window.title('VisualDiffusion (MakeGUDPICS Update for ProgRock-Stable): '+batch_name+' '+gui_settings)

def delete_prompt():
    global prompt_list
    global prompt_weight
    global prompt_entry
    global prompt_weight_str
    global prompt_weight_scale
    global prompt_text_frame
    global prompt_text_weights_frame
    global prompt_label
    global prompt_frame
    global prompt_entry
    prompt_label[len(prompt_list)-1].destroy()
    prompt_entry[len(prompt_list)-1].destroy()
    prompt_weight_scale[len(prompt_list)-1].destroy()
    prompt_entry.pop(len(prompt_list)-1)
    prompt_weight_scale.pop(len(prompt_list)-1)
    del prompt_label[len(prompt_list)-1]
    del prompt_list[len(prompt_list)-1]
    print(len(prompt_list))
    prompt_text_frame.pack()
    prompt_text_weights_frame.pack()

def new_prompt():
    # Add New Prompt Label Entry Box
    global prompt
    global prompt_list
    global prompt_label
    global prompt_entry
    global prompt_text_frame
    global prompt_weight_str
    global prompt_weight_scale
    if len(prompt_list) == 0:
        load_txt_file()
        prompt = {}
        prompt_label = {}
        prompt_entry = {}
        prompt_weight_str = {}
        prompt_weight_scale = {}
        for i in range(len(batches_list)):
            prompt[i] = StringVar()
            prompt[i].set(prompt_list[i])
            prompt_label[i] = Label(prompt_text_frame, text='Prompt '+str(i+1)+':', width=100, anchor=NW)
            prompt_label[i].pack(side=TOP, fill='both', expand=True)
            prompt_entry[i] = Entry(prompt_text_frame, textvariable=prompt[i])
            prompt_entry[i].pack(side=TOP, fill='both', expand=True)
            # Draw Prompt Weight Slider
            prompt_weight_str[i] = DoubleVar()
            prompt_weight_str[i].set(prompt_weight[i])
            prompt_weight_scale[i] = Scale(prompt_text_weights_frame, variable=prompt_weight_str[i], from_=-5, to=15, resolution=0.5, orient=HORIZONTAL, length=200)
            prompt_weight_scale[i].pack(side=TOP, fill='both', expand=True)
    else:
        prompt_list[len(prompt_list)] = ''
        prompt[len(prompt_list)-1] = StringVar()
        prompt[len(prompt_list)-1].set('Enter Prompt Here')
        prompt_label[len(prompt_list)-1] = Label(prompt_text_frame, text='Prompt ' + str(len(prompt_list)) + ':' , width=100, anchor=NW)
        prompt_label[len(prompt_list)-1].pack(side='top', fill='both', expand=True)
        prompt_entry[len(prompt_list)-1] = Entry(prompt_text_frame, textvariable=prompt[len(prompt_list)-1])
        prompt_entry[len(prompt_list)-1].pack(side='top', fill='both', expand=True)
        # Draw Prompt Weight Slider
        prompt_weight_str[len(prompt_list)-1] = DoubleVar()
        prompt_weight_str[len(prompt_list)-1].set(1.0)
        prompt_weight_scale[len(prompt_list)-1] = Scale(prompt_text_weights_frame, variable=prompt_weight_str[len(prompt_list)-1], from_=-5, to=15, resolution=0.5, orient=HORIZONTAL, length=200)
        prompt_weight_scale[len(prompt_list)-1].pack(side=TOP, fill='both', expand=True)

def cleanup():
    # Cleanup Prompt Text Frame
    # If prompt_entry is empty, delete prompt_label and prompt_entry
    global prompt_list
    global prompt_label
    global prompt_entry
    global prompt_text_frame
    for i in range(len(prompt_list)):
        if prompt_entry[i].get(1.0, END) == '':
            if prompt_entry[i] == prompt_entry[len(prompt_entry)-1]:
                prompt_label[i].destroy()
                prompt_entry[i].frame.destroy()
                prompt_label.pop(i)
                prompt_entry.pop(i)
                prompt_list.pop(i)

def start_thread():
    global is_running
    global has_run
    if is_running == False:
        is_running = True
        has_run = True
        global thread
        thread = threading.Thread(target=run_prs)
        thread.start()
    else:
        print("Already Running")

def run_prs():
    # Run PRS
    global gobig
    global is_running
    global thread
    global p
    global term_text
    gobig = bool(gobig_str.get())
    if gobig == True:
        print('Running PRS with GoBigMode')
        p = subprocess.Popen(shlex.split('python prs.py --gobig --interactive'))
    else:
        print('Running ProgRock-Stable')
        p = subprocess.Popen(shlex.split('python prs.py --interactive'))

def show_image():
    global sample
    global current_img
    global h
    global w
    global list_of_files
    global image_window
    global canvas
    global image_container
    try:
        if gobig_str.get() == True:
            list_of_files = glob.glob('./out/'+batch_name+'/'+batch_name+'*.png')
            sample = max(list_of_files, key=os.path.getctime)
        else:
            list_of_files = glob.glob('./out/'+batch_name+'/'+batch_name+'*.png')
            # Remove item from list_of_files if it contains 'gobig'
            list_of_files = [i for i in list_of_files if 'gobig' not in i]
            sample = max(list_of_files, key=os.path.getctime)
    except:
        try:
            Image.new('RGB', (1,1), color = 'white').save('./out/'+batch_name+'/'+batch_name+'.png')
            sample = './out/'+batch_name+'/'+batch_name+'.png'
        except:
            pass
    master_frame.pack()
    current_img = Image.open(sample)
    wbase = 756
    h = float(current_img.size[1])
    w = float(current_img.size[0])
    image_window = ttk.Frame(progress_frame, width=w, height=h)
    image_window.pack()
    if h > 756 or w > 756:
        if w > h:
            wbase = 756
            wpercent = (wbase/w)
            hsize = int(h*float(wpercent))
            h = hsize
            w = wbase
        else:
            hbase = 756
            hpercent = (hbase/h)
            wsize = int(w*float(hpercent))
            h = hbase
            w = wsize
        current_img = current_img.resize((int(w),int(h)), Image.Resampling.BICUBIC)
        current_img.save(sample)
    else:
        h = float(current_img.size[1])
        w = float(current_img.size[0])
    current_img = PhotoImage(file=sample, height=int(h), width=int(w))
    canvas = Canvas(image_window, width=w, height=h)
    image_container = canvas.create_image(0,0, anchor="nw",image=current_img)
    canvas.config(width=w, height=h)
    canvas.itemconfig(image_container, image = current_img)
    canvas.pack(expand=YES, fill=BOTH)
    image_window.pack(expand=YES, fill=BOTH)
    progress_frame.pack(expand=YES, fill=BOTH)
    master_frame.pack(expand=YES, fill=BOTH)

# Function to refresh the image in the GUI
def refresh_image():
    global is_running
    global p
    global current_img
    global sample
    global list_of_files
    global h
    global w
    updater()
    try:
        if gobig_str.get() == True:
            list_of_files = glob.glob('./out/'+batch_name+'/'+batch_name+'*.png')
            sample = max(list_of_files, key=os.path.getctime)
        else:
            list_of_files = glob.glob('./out/'+batch_name+'/'+batch_name+'*.png')
            # Remove item from list_of_files if it contains 'gobig'
            list_of_files = [i for i in list_of_files if 'gobig' not in i]
            sample = max(list_of_files, key=os.path.getctime)
    except:
        return
    # Check if thread is still running
    if is_running == True:
        if p.returncode == None:
            try:
                global h
                global w
                global image_container
                global canvas
                global has_run
                current_img = Image.open(sample)
                if h > 756 or w > 756:
                    if w > h:
                        wbase = 756
                        wpercent = (wbase/w)
                        hsize = int(h*float(wpercent))
                        h = hsize
                        w = wbase
                    else:
                        hbase = 756
                        hpercent = (hbase/h)
                        wsize = int(w*float(hpercent))
                        h = hbase
                        w = wsize
                    current_img = current_img.resize((int(w),int(h)), Image.Resampling.BICUBIC)
                    current_img.save(sample)
                else:
                    h = float(current_img.size[1])
                    w = float(current_img.size[0])
                has_run = True
            except:
                pass
    else:
        is_running = False
        try:
            current_img = Image.open(sample)
            if h > 756 or w > 756:
                if w > h:
                    wbase = 756
                    wpercent = (wbase/w)
                    hsize = int(h*float(wpercent))
                    h = hsize
                    w = wbase
                else:
                    hbase = 756
                    hpercent = (hbase/h)
                    wsize = int(w*float(hpercent))
                    h = hbase
                    w = wsize
                current_img = current_img.resize((int(w),int(h)), Image.Resampling.BICUBIC)
                current_img.save(sample)
            else:
                h = float(current_img.size[1])
                w = float(current_img.size[0])
        except:
            pass
    current_img = PhotoImage(file=sample, height=int(h), width=int(w))
    canvas.config(width=w, height=h)
    canvas.itemconfig(image_container, image = current_img)
    canvas.pack(expand=YES, fill=BOTH)
    image_window.pack(expand=YES, fill=BOTH)
    progress_frame.pack(expand=YES, fill=BOTH)
    master_frame.pack(expand=YES, fill=BOTH)
        

def updater():
    global batch_name
    global width
    global height
    global steps
    global scale
    global frozen_seed
    global seed
    global n_batches
    global n_iter
    global variance
    global init_image
    global init_strength
    global gobig_maximize
    global gobig_overlap
    global method
    global from_file
    global cool_down
    global use_jpg
    global save_settings
    global gobig
    batch_name = batch_name_str.get()
    width = int(width_scale.get())
    height = int(height_scale.get())
    steps = int(steps_scale.get())
    scale = float(scale_scale.get())
    frozen_seed = bool(frozen_seed_str.get())
    seed = get_int_or_rdm(seed_entry.get())
    n_batches = 1
    n_iter = int(n_iter_entry.get())
    variance = float(variance_str.get())
    init_image = None
    init_strength = 0.62
    gobig_maximize = bool(gobig_maximize_str.get())
    gobig_overlap = int(gobig_overlap_entry.get())
    method = str(method_str.get())
    from_file = './settings/prompts.txt'
    cool_down = float(cool_down_entry.get())
    use_jpg = bool(use_jpg_str.get())
    save_settings = bool(save_settings_str.get())
    gobig = bool(gobig_str.get())

    window.after(1000, refresh_image)

def get_int_or_rdm(x):
    # Check if str is random or if integer
    if x == 'random':
        return str(x)
    elif x.isdigit():
        return int(x)
    else:
        return 'random'

def update_labels(val):
    global prompt_weight
    global prompt_weight_label
    prompt_weight.set(val)
    prompt_weight_label.config(text='Weight: '+str(prompt_weight.get()))


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

set_variables()
draw_main_window()
show_image()
updater()
window.after(1000, start_thread)
window.mainloop()
    


p.kill()
