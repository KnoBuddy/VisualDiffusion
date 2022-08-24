from encodings import utf_8
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import json5 as json
import os
import sys
import subprocess
import shutil
import threading
import shlex


# File Names
prompts_file = 'prompts.txt'
gui_settings = 'gui_settings.json'
default_settings_file = 'settings.json'
progress = 'progress.png'
progress_done = 'progress_done.png'
prd = 'prd.py'

default_prompt = ["A beautiful painting of a Castle in the Scottish Highlands, underexposed and overcast, by Banksy, Beeple, and Bob Ross, trending on ArtStation, vibrant \n"]

# First Run Check Variables
is_running = False
has_run = False
interrupt = False
prompt_list = []

# Load Settings from JSON
def load_json_file(i):
    global json_set
    global default_settings
    if not os.path.exists('./settings'):
        os.mkdir('./settings')
    if os.path.exists('./settings/prompt_'+str(i)+'.json'):
        with open('./settings/prompt_'+str(i)+'.json', 'r') as f:
            json_set = json.load(f)
    else: # Load Default Settings
        with open(default_settings_file, 'r') as f:
            default_settings = json.load(f)
            json_set = default_settings

def load_txt_file():
    global prompt_list
    global batches_list
    if os.path.exists(prompts_file):
        try:
            with open(prompts_file) as f:
                prompt_list = f.readlines()
                print("Prompts loaded", file = sys.stdout)
        except:
            print("Error loading prompts.txt", file = sys.stdout)
            print("Loading from Defaults...", file = sys.stdout)
            prompt_list = default_prompt

def set_variables():
    global prompt
    global batch_name
    global width
    global height
    global steps
    global scale
    global seed
    global n_batches
    global n_samples
    global n_iter
    global n_rows
    global init_image
    global init_strength
    global gobig_maximize
    global gobig_overlap
    global plms
    global eta
    global from_file
    global cool_down
    global prompts_file
    global json_set
    prompt = {}
    batch_name = {}
    width = {}
    height = {}
    steps = {}
    scale = {}
    seed = {}
    n_batches = {}
    n_samples = {}
    n_iter = {}
    n_rows = {}
    init_image = {}
    init_strength = {}
    gobig_maximize = {}
    gobig_overlap = {}
    plms = {}
    eta = {}
    from_file = {}
    cool_down = {}
    # Set Variables
    # batch_name, width, height, steps, scale, seed, 
    # n_batches, n_samples, n_iter, n_rows, init_image, init_strength,
    # gobig_maximize, gobig_overlap, plms, eta, from_file, cool_down
    # iterate through json_set looking for keys and making a variable set to the value of each key in json_set
    load_txt_file()
    for i in range(len(prompt_list)): 
        # Set Variables
        # batch_name, width, height, steps, scale, seed, 
        # n_batches, n_samples, n_iter, n_rows, init_image, init_strength,
        # gobig_maximize, gobig_overlap, plms, eta, from_file, cool_down
        load_json_file(i)
        prompt[i] = prompt_list[i]
        batch_name[i] = json_set['batch_name']
        width[i] = json_set['width']
        height[i] = json_set['height']
        steps[i] = json_set['steps']
        scale[i] = json_set['scale']
        seed[i] = json_set['seed']
        n_batches[i] = json_set['n_batches']
        n_samples[i] = json_set['n_samples']
        n_iter[i] = json_set['n_iter']
        n_rows[i] = json_set['n_rows']
        init_image[i] = json_set['init_image']
        init_strength[i] = json_set['init_strength']
        gobig_maximize[i] = json_set['gobig_maximize']
        gobig_overlap[i] = json_set['gobig_overlap']
        plms[i] = json_set['plms']
        eta[i] = json_set['eta']
        from_file[i] = json_set['from_file']
        cool_down[i] = json_set['cool_down']

def add_variables():
    global prompt
    global batch_name
    global width
    global height
    global steps
    global scale
    global seed
    global n_batches
    global n_samples
    global n_iter
    global n_rows
    global init_image
    global init_strength
    global gobig_maximize
    global gobig_overlap
    global plms
    global eta
    global from_file
    global cool_down
    global prompts_file
    global json_set
    i = len(prompt)
    prompt[i] = json_set['prompt']
    batch_name[i] = json_set['batch_name']
    width[i] = json_set['width']
    height[i] = json_set['height']
    steps[i] = json_set['steps']
    scale[i] = json_set['scale']
    seed[i] = json_set['seed']
    n_batches[i] = json_set['n_batches']
    n_samples[i] = json_set['n_samples']
    n_iter[i] = json_set['n_iter']
    n_rows[i] = json_set['n_rows']
    init_image[i] = json_set['init_image']
    init_strength[i] = json_set['init_strength']
    gobig_maximize[i] = json_set['gobig_maximize']
    gobig_overlap[i] = json_set['gobig_overlap']
    plms[i] = json_set['plms']
    eta[i] = json_set['eta']
    from_file[i] = json_set['from_file']
    cool_down[i] = json_set['cool_down']

def del_variables():
    global prompt
    global batch_name
    global width
    global height
    global steps
    global scale
    global seed
    global n_batches
    global n_samples
    global n_iter
    global n_rows
    global init_image
    global init_strength
    global gobig_maximize
    global gobig_overlap
    global plms
    global eta
    global from_file
    global cool_down
    global prompts_file
    global json_set
    i = len(prompt)-1
    del prompt[i]
    del batch_name[i]
    del width[i]
    del height[i]
    del steps[i]
    del scale[i]
    del seed[i]
    del n_batches[i]
    del n_samples[i]
    del n_iter[i]
    del n_rows[i]
    del init_image[i]
    del init_strength[i]
    del gobig_maximize[i]
    del gobig_overlap[i]
    del plms[i]
    del eta[i]
    del from_file[i]
    del cool_down[i]


def draw_main_window():
    global window
    global main_frame
    global prompt_frame
    global prompt_text_frame
    global prompt_text_batches_frame
    global progress_frame
    global s
    global prompt
    global prompt_list
    global prompt_label
    global prompt_entry

    # Draw Main Window
    window = Tk()
    
    # Add Style for Frames
    s = ttk.Style()
    s.configure('TFrame', background='Light Blue')
    s.configure('Green.TFrame', background='Light Green', relief='ridge')
    
    # Draw Main Frame
    main_frame = ttk.Frame(window, style='TFrame')
    main_frame.pack(fill='both', expand=True)
    
    # Draw Calls
    #set_variables()
    draw_basic()
    draw_prompts()

def draw_basic():
    global width_entry
    global height_entry
    global steps_entry
    global scale_entry
    global seed_entry
    global n_batches_entry
    global n_samples_entry
    global n_iter_entry
    global n_rows_entry
    global init_image_entry
    global init_strength_entry
    global gobig_maximize_entry
    global gobig_overlap_entry
    global plms_entry
    global eta_entry
    global from_file_entry
    global cool_down_entry

    # Draw Basic Settings Frame
    basic_settings_frame = ttk.Frame(main_frame, style='TFrame')
    basic_settings_frame.pack(fill='both', expand=True)

    # Draw Basic Buttons Frame
    basic_buttons_frame = ttk.Frame(basic_settings_frame, style='TFrame')
    basic_buttons_frame.pack(side=TOP, fill='both', expand=True)

    # Draw Save Button
    save_button = ttk.Button(basic_buttons_frame, text='Save', command=save_prompts)
    save_button.pack(side=LEFT, fill='both', expand=True)

    # Draw Run Button

    run_button = ttk.Button(basic_buttons_frame, text='Run', command=start_thread)
    run_button.pack(side=LEFT, fill='both', expand=True)

    # Draw Basic Settings Entry Frame
    basic_settings_entry_frame = ttk.Frame(basic_settings_frame, style='TFrame')
    basic_settings_entry_frame.pack(side=TOP, fill='both', expand=True)
    # Draw Width Entry

    width_str = StringVar()
    print(width[0])
    width_str.set(width[0])
    width_label = ttk.Label(basic_settings_entry_frame, text='Width:')
    width_label.grid(row=0, column=0, sticky=NW)
    width_entry = Entry(basic_settings_entry_frame, textvariable=width_str)
    width_entry.grid(row=0, column=1, sticky=NW)
    # Draw Height Entry
    height_str = StringVar()
    height_str.set(height[0])
    height_label = ttk.Label(basic_settings_entry_frame, text='Height:')
    height_label.grid(row=0, column=2, sticky=NW)
    height_entry = Entry(basic_settings_entry_frame, textvariable=height_str)
    height_entry.grid(row=0, column=3, sticky=NW)
    # Draw Steps Entry
    steps_str = StringVar()
    steps_str.set(steps[0])
    steps_label = ttk.Label(basic_settings_entry_frame, text='Steps:')
    steps_label.grid(row=0, column=4, sticky=NW)
    steps_entry = Entry(basic_settings_entry_frame, textvariable=steps_str)
    steps_entry.grid(row=0, column=5, sticky=NW)
    # Draw Batches Entry
    n_batches_str = StringVar()
    n_batches_str.set(n_batches[0])
    n_batches_label = ttk.Label(basic_settings_entry_frame, text='Batches:')
    n_batches_label.grid(row=1, column=0, sticky=NW)
    n_batches_entry = Entry(basic_settings_entry_frame, textvariable=n_batches_str)
    n_batches_entry.grid(row=1, column=1, sticky=NW)
    # Draw Scale Entry
    scale_str = StringVar()
    scale_str.set(scale[0])
    scale_label = ttk.Label(basic_settings_entry_frame, text='Scale:')
    scale_label.grid(row=1, column=4, sticky=NW)
    scale_entry = Entry(basic_settings_entry_frame, textvariable=scale_str)
    scale_entry.grid(row=1, column=5, sticky=NW)
    # Draw Seed Entry
    seed_str = StringVar()
    seed_str.set(seed[0])
    seed_label = ttk.Label(basic_settings_entry_frame, text='Seed:')
    seed_label.grid(row=1, column=2, sticky=NW)
    seed_entry = Entry(basic_settings_entry_frame, textvariable=seed_str)
    seed_entry.grid(row=1, column=3, sticky=NW)
    # Draw gobig_maximize Entry
    gobig_maximize_str = StringVar()
    gobig_maximize_str.set(gobig_maximize[0])
    gobig_maximize_label = ttk.Label(basic_settings_entry_frame, text='Gobig Maximize:')
    gobig_maximize_label.grid(row=2, column=0, sticky=NW)
    gobig_maximize_entry = Entry(basic_settings_entry_frame, textvariable=gobig_maximize_str)
    gobig_maximize_entry.grid(row=2, column=1, sticky=NW)
    # Draw gobig_overlap Entry
    gobig_overlap_str = StringVar()
    gobig_overlap_str.set(gobig_overlap[0])
    gobig_overlap_label = ttk.Label(basic_settings_entry_frame, text='Gobig Overlap:')
    gobig_overlap_label.grid(row=2, column=2, sticky=NW)
    gobig_overlap_entry = Entry(basic_settings_entry_frame, textvariable=gobig_overlap_str)
    gobig_overlap_entry.grid(row=2, column=3, sticky=NW)
    # Draw plms Entry
    plms_str = StringVar()
    plms_str.set(plms[0])
    plms_label = ttk.Label(basic_settings_entry_frame, text='PLMS:')
    plms_label.grid(row=2, column=4, sticky=NW)
    plms_entry = Entry(basic_settings_entry_frame, textvariable=plms_str)
    plms_entry.grid(row=2, column=5, sticky=NW)
    # Draw eta Entry
    eta_str = StringVar()
    eta_str.set(eta[0])
    eta_label = ttk.Label(basic_settings_entry_frame, text='ETA:')
    eta_label.grid(row=3, column=0, sticky=NW)
    eta_entry = Entry(basic_settings_entry_frame, textvariable=eta_str)
    eta_entry.grid(row=3, column=1, sticky=NW)
    # Draw cool_down Entry
    cool_down_str = StringVar()
    cool_down_str.set(cool_down[0])
    cool_down_label = ttk.Label(basic_settings_entry_frame, text='Cool Down:')
    cool_down_label.grid(row=3, column=2, sticky=NW)
    cool_down_entry = Entry(basic_settings_entry_frame, textvariable=cool_down_str)
    cool_down_entry.grid(row=3, column=3, sticky=NW)



def draw_prompts():
    global prompt_list
    global batches_list
    global prompt
    global prompt_batches
    global prompt_label
    global prompt_entry
    global prompt_batches_label
    global prompt_batches_entry
    global prompt_frame
    global prompt_text_frame
    global prompt_text_batches_frame
    global prompt_button_frame
    global new_prompt_button
    global save_button
    global delete_prompt_button

    # Draw Prompt Frame
    prompt_frame = ttk.Frame(main_frame, style='Green.TFrame')
    prompt_frame.pack(side='top', fill='both', expand=True)

    # Draw Prompt Button Frame
    prompt_button_frame = ttk.Frame(main_frame, style='TFrame')
    prompt_button_frame.pack(side=LEFT, fill='both', expand=True)

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
    prompt_text_batches_frame = ttk.Frame(prompt_text_frame, style='TFrame')
    prompt_text_batches_frame.pack(side=RIGHT, fill='both', expand=True)

    # Draw Text Entry Box(es)
    prompt = {}
    prompt_label = {}
    prompt_entry = {}
    prompt_batches = {}
    prompt_batches_label = {}
    prompt_batches_entry = {}

    for i in range(len(prompt_list)):
        prompt[i] = StringVar()
        prompt[i].set(prompt_list[i])
        prompt_label[i] = Label(prompt_text_frame, text='Prompt '+str(i+1)+':', anchor=NW)
        prompt_label[i].pack(side=TOP, fill='both', expand=True)
        prompt_entry[i] = Entry(prompt_text_frame, textvariable=prompt[i], width=150)
        prompt_entry[i].pack(side=TOP, fill='both', expand=True)

def save_prompts():
    cleanup()
    # Check how many prompt_N.json files exist
    n = 1
    while os.path.isfile('./settings/prompt_'+str(n)+'.json'):
        n += 1
    # If more than length of prompt_list, delete the extra ones
    if n > len(prompt_list):
        for i in range(n-len(prompt_list)):
            os.remove('./settings/prompt_'+str(i+1)+'.json')
    # Get Entry Boxes and save to prompt_list
    for i in range(len(prompt_entry)):
        prompt_list[i] = prompt_entry[i].get()
        n_iter[i] = 1
        width[i] = int(width_entry.get())
        height[i] = int(height_entry.get())
        steps[i] = int(steps_entry.get())
        scale[i] = float(scale_entry.get())
        seed[i] = seed_entry.get()
        n_batches[i] = int(n_batches_entry.get())
        n_samples[i] = 1
        n_rows[i] = 1
        init_image[i] = None
        init_strength[i] = 0.62
        gobig_maximize[i] = bool(gobig_maximize_entry.get())
        gobig_overlap[i] = int(gobig_overlap_entry.get())
        plms[i] = bool(plms_entry.get())
        eta[i] = float(eta_entry.get())
        from_file[i] = 'prompts.txt'
        cool_down[i] = float(cool_down_entry.get())

    # Save Prompt List to prompt.txt
    with open('prompts.txt', 'w+') as f:
        for i in range(len(prompt_list)):
            f.write(prompt_list[i])
        f.close()
    # Save Settings to prompt_N.json
    i = 0
    json_set = {'prompt': prompt_list[i], 'batch_name': batch_name[i], 'width': width[i], 'height': height[i], 'steps': steps[i], 'scale': scale[i], 'seed': seed[i], 'n_batches': n_batches[i], 'n_samples': n_samples[i], 'n_iter': n_iter[i], 'n_rows': n_rows[i], 'init_image': init_image[i], 'init_strength': init_strength[i], 'gobig_maximize': gobig_maximize[i], 'gobig_overlap': gobig_overlap[i], 'plms': plms[i], 'eta': eta[i], 'from_file': from_file[i], 'cool_down': cool_down[i]}
    with open('./settings/prompt_'+str(i+1)+'.json', 'w+', encoding='utf_8') as f:
        json.dump(json_set, f, ensure_ascii=False, indent=4)

def delete_prompt():
    # Delete Prompt Label Entry Box
    del_variables()
    global prompt_list
    global prompt_label
    global prompt_entry
    global prompt_batches_label
    global prompt_batches_entry
    global prompt_text_frame
    prompt_list.pop()
    prompt_label[len(prompt_list)].destroy()
    prompt_entry[len(prompt_list)].destroy()
    prompt_batches_label[len(prompt_list)].destroy()
    prompt_batches_entry[len(prompt_list)].destroy()
    prompt_label.pop(len(prompt_list))
    prompt_entry.pop(len(prompt_list))
    prompt_batches_label.pop(len(prompt_list))
    prompt_batches_entry.pop(len(prompt_list))

def new_prompt():
    # Add New Prompt Label Entry Box
    load_json_file(0)
    add_variables()
    global prompt
    global prompt_list
    global prompt_label
    global prompt_entry
    global prompt_batches_label
    global prompt_batches_entry
    global prompt_text_frame
    global prompt_batches_frame
    prompt_list.append('')
    prompt[len(prompt_list)-1] = StringVar()
    prompt[len(prompt_list)-1].set(default_prompt[0])
    prompt_batches[len(prompt_list)-1] = IntVar()
    prompt_batches[len(prompt_list)-1].set(1)
    prompt_label[len(prompt_list)-1] = ttk.Label(prompt_text_frame, text='Prompt ' + str(len(prompt_list)) + ':' , width=150)
    prompt_label[len(prompt_list)-1].pack(side='top', fill='both', expand=True)
    prompt_entry[len(prompt_list)-1] = Entry(prompt_text_frame, textvariable=prompt[len(prompt_list)-1], width=150)
    prompt_entry[len(prompt_list)-1].pack(side='top', fill='both', expand=True)
    prompt_batches_label[len(prompt_list)-1] = ttk.Label(prompt_text_batches_frame, text='Batches: ', width=10)
    prompt_batches_label[len(prompt_list)-1].pack(side='top', fill='both', expand=True)
    prompt_batches_entry[len(prompt_list)-1] = Entry(prompt_text_batches_frame, textvariable=prompt_batches[len(prompt_list)-1], width=8)
    prompt_batches_entry[len(prompt_list)-1].pack(side='top', fill='both', expand=True)

def cleanup():
    # Cleanup Prompt Text Frame
    # If prompt_entry is empty, delete prompt_label and prompt_entry
    global prompt_list
    global prompt_label
    global prompt_entry
    global prompt_batches_label
    global prompt_batches_entry
    global prompt_text_frame
    global prompt_text_batches_frame
    for i in range(len(prompt_list)):
        if prompt_entry[i].get() == '':
            prompt_label[i].destroy()
            prompt_entry[i].destroy()
            prompt_batches_label[i].destroy()
            prompt_batches_entry[i].destroy()
            prompt_label.pop(i)
            prompt_entry.pop(i)
            prompt_batches_label.pop(i)
            prompt_batches_entry.pop(i)
            prompt_list.pop(i)
            prompt_batches.pop(i)

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
    save_prompts()
    # Run PRS
    p = subprocess.Popen(shlex.split('python prs.py -s ./settings/prompt_1.json'))

set_variables()
draw_main_window()


mainloop()
