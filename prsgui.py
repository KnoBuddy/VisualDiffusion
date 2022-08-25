from encodings import utf_8
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from xmlrpc.client import Boolean
import collections
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

default_prompt = "A beautiful painting of a Castle in the Scottish Highlands, underexposed and overcast, by Banksy, Beeple, and Bob Ross, trending on ArtStation, vibrant"

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

def load_txt_file():
    global prompt_list
    global batches_list
    prompt_list = {}
    batches_list = {}
    if os.path.exists(prompts_file):
        try:
            with open(prompts_file) as f:
                # Count how many times the each different prompt is repeated in the file
                c = collections.Counter(f.readlines())
                i = 0
                for k, v in sorted(c.items(), key=lambda x: x[0]):
                    prompt_list[i] = k.strip()
                    batches_list[i] = int(v)
                    i += 1
                print(prompt_list)
                print("Prompts loaded", file = sys.stdout)
        except:
            print("Error loading prompts.txt", file = sys.stdout)
            print("Loading from Defaults...", file = sys.stdout)
            prompt_list[0] = default_prompt

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
    global use_jpg
    global prompts_file
    global json_set
    # Set Variables
    # batch_name, width, height, steps, scale, seed, 
    # n_batches, n_samples, n_iter, n_rows, init_image, init_strength,
    # gobig_maximize, gobig_overlap, plms, eta, from_file, cool_down
    load_txt_file()
    load_json_file()
    batch_name = json_set['batch_name']
    width = json_set['width']
    height = json_set['height']
    steps = json_set['steps']
    scale = json_set['scale']
    seed = json_set['seed']
    n_batches = json_set['n_batches']
    n_samples = json_set['n_samples']
    n_iter = json_set['n_iter']
    n_rows = json_set['n_rows']
    init_image = json_set['init_image']
    init_strength = json_set['init_strength']
    gobig_maximize = json_set['gobig_maximize']
    gobig_overlap = json_set['gobig_overlap']
    plms = json_set['plms']
    eta = json_set['eta']
    from_file = json_set['from_file']
    cool_down = json_set['cool_down']
    use_jpg = json_set['use_jpg']


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
    window.title('VisualDiffusion (a GUI for ProgRock-Stable): '+batch_name+' '+gui_settings)

    
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
    global batch_name_str
    global width_entry
    global width_str
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
    global gobig_maximize_str
    global gobig_overlap_entry
    global plms_entry
    global eta_entry
    global from_file_entry
    global cool_down_entry
    global use_jpg_str

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
    width_str.set(width)
    width_label = ttk.Label(basic_settings_entry_frame, text='Width:')
    width_label.grid(row=0, column=0, sticky=NW)
    width_entry = Entry(basic_settings_entry_frame, textvariable=width_str)
    width_entry.grid(row=0, column=1, sticky=NW)
    # Draw Height Entry
    height_str = StringVar()
    height_str.set(height)
    height_label = ttk.Label(basic_settings_entry_frame, text='Height:')
    height_label.grid(row=0, column=2, sticky=NW)
    height_entry = Entry(basic_settings_entry_frame, textvariable=height_str)
    height_entry.grid(row=0, column=3, sticky=NW)
    # Draw Steps Entry
    steps_str = StringVar()
    steps_str.set(steps)
    steps_label = ttk.Label(basic_settings_entry_frame, text='Steps:')
    steps_label.grid(row=0, column=4, sticky=NW)
    steps_entry = Entry(basic_settings_entry_frame, textvariable=steps_str)
    steps_entry.grid(row=0, column=5, sticky=NW)
    # Draw Batches Entry
    n_batches_str = StringVar()
    n_batches_str.set(n_batches)
    n_batches_label = ttk.Label(basic_settings_entry_frame, text='Batches:')
    n_batches_label.grid(row=1, column=0, sticky=NW)
    n_batches_entry = Entry(basic_settings_entry_frame, textvariable=n_batches_str)
    n_batches_entry.grid(row=1, column=1, sticky=NW)
    # Draw Scale Entry
    scale_str = StringVar()
    scale_str.set(scale)
    scale_label = ttk.Label(basic_settings_entry_frame, text='Scale:')
    scale_label.grid(row=1, column=4, sticky=NW)
    scale_entry = Entry(basic_settings_entry_frame, textvariable=scale_str)
    scale_entry.grid(row=1, column=5, sticky=NW)
    # Draw Seed Entry
    seed_str = StringVar()
    seed_str.set(seed)
    seed_label = ttk.Label(basic_settings_entry_frame, text='Seed:')
    seed_label.grid(row=1, column=2, sticky=NW)
    seed_entry = Entry(basic_settings_entry_frame, textvariable=seed_str)
    seed_entry.grid(row=1, column=3, sticky=NW)
    # Draw gobig_maximize Checkbutton
    gobig_maximize_str = BooleanVar()
    gobig_maximize_str.set(gobig_maximize)
    gobig_maximize_checkbutton = ttk.Checkbutton(basic_settings_entry_frame, text='GoBig Maximize', variable=gobig_maximize_str)
    gobig_maximize_checkbutton.grid(row=0, column=7, sticky=NW)
    # Draw gobig_overlap Entry
    gobig_overlap_str = StringVar()
    gobig_overlap_str.set(gobig_overlap)
    gobig_overlap_label = ttk.Label(basic_settings_entry_frame, text='Gobig Overlap:')
    gobig_overlap_label.grid(row=1, column=7, sticky=NW)
    gobig_overlap_entry = Entry(basic_settings_entry_frame, textvariable=gobig_overlap_str)
    gobig_overlap_entry.grid(row=1, column=8, sticky=NW)
    # Draw plms Entry
    plms_str = StringVar()
    plms_str.set(plms)
    plms_label = ttk.Label(basic_settings_entry_frame, text='PLMS:')
    plms_label.grid(row=3, column=2, sticky=NW)
    plms_entry = Entry(basic_settings_entry_frame, textvariable=plms_str)
    plms_entry.grid(row=3, column=3, sticky=NW)
    # Draw eta Entry
    eta_str = StringVar()
    eta_str.set(eta)
    eta_label = ttk.Label(basic_settings_entry_frame, text='ETA:')
    eta_label.grid(row=3, column=0, sticky=NW)
    eta_entry = Entry(basic_settings_entry_frame, textvariable=eta_str)
    eta_entry.grid(row=3, column=1, sticky=NW)
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
    use_jpg_checkbutton.grid(row=3, column=10, sticky=NW)
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
        prompt_batches[i] = IntVar()
        prompt_batches[i].set(batches_list[i])
        prompt_batches_label[i] = Label(prompt_text_batches_frame, text='Batches:', anchor=NW)
        prompt_batches_label[i].pack(side=TOP, fill='both', expand=True)
        prompt_batches_entry[i] = Entry(prompt_text_batches_frame, textvariable=prompt_batches[i], width=10)
        prompt_batches_entry[i].pack(side=TOP, fill='both', expand=True)

def save_prompts():
    cleanup()
    # Get Entry Boxes and save to prompt_list
    for i in range(len(prompt_list)):
        prompt_list[i] = prompt[i].get()
    batch_name = batch_name_str.get()
    n_iter = 1
    width = int(width_entry.get())
    height = int(height_entry.get())
    steps = int(steps_entry.get())
    scale = float(scale_entry.get())
    seed = get_int_or_rdm(seed_entry.get())
    n_batches = 1
    n_samples = 1
    n_rows = 1
    init_image = None
    init_strength = 0.62
    gobig_maximize = bool(gobig_maximize_str.get())
    gobig_overlap = int(gobig_overlap_entry.get())
    plms = bool(plms_entry.get())
    eta = float(eta_entry.get())
    from_file = 'prompts.txt'
    cool_down = float(cool_down_entry.get())
    use_jpg = bool(use_jpg_str.get())

    # Save Prompt List to prompt.txt
    with open('prompts.txt', 'w+') as f:
        for i in range(len(prompt_list)):
            t = 0
            # Remove (, ),  and ' from prompt
            tmp = prompt_list[i].replace('(', '')
            tmp = tmp.replace(')', '')
            tmp = tmp.replace("'", '')
            # Write the prompt on a line repeated on a new line until the amount of lines reaches the batch number
            while t < prompt_batches[i].get():
                f.write(tmp+'\n')
                t += 1
        f.close()
    # Save Settings to prompt_N.json
    i = 0
    json_set = {'prompt': list(prompt_list), 'batch_name': batch_name, 'width': width, 'height': height, 'steps': steps, 'scale': scale, 'seed': seed, 'n_batches': n_batches, 'n_samples': n_samples, 'n_iter': n_iter, 'n_rows': n_rows, 'init_image': init_image, 'init_strength': init_strength, 'gobig_maximize': gobig_maximize, 'gobig_overlap': gobig_overlap, 'plms': plms, 'eta': eta, 'from_file': from_file, 'cool_down': cool_down, 'use_jpg': use_jpg}
    with open('./settings/'+gui_settings, 'w+', encoding='utf_8') as f:
        json.dump(json_set, f, ensure_ascii=False, indent=4)
    window.title('VisualDiffusion (a GUI for ProgRock-Stable): '+batch_name+' '+gui_settings)


def delete_prompt():
    # Delete Prompt Label Entry Box
    global prompt_list
    global prompt_label
    global prompt_entry
    global prompt_batches_label
    global prompt_batches_entry
    global prompt_text_frame
    del prompt_list[len(prompt_list)-1]
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
    global prompt
    global prompt_list
    global prompt_label
    global prompt_entry
    global prompt_batches_label
    global prompt_batches_entry
    global prompt_text_frame
    global prompt_batches_frame
    prompt_list[len(prompt_list)] = ''
    prompt[len(prompt_list)-1] = StringVar()
    prompt[len(prompt_list)-1].set(default_prompt)
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
            if prompt_entry[i] == prompt_entry[len(prompt_entry)-1]:
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
    p = subprocess.Popen(shlex.split('python prs.py -s ./settings/'+gui_settings))

def get_int_or_rdm(x):
    # Check if str is random or if integer
    if x == 'random':
        return str(x)
    elif x.isdigit():
        return int(x)
    else:
        return 'random'

set_variables()
draw_main_window()


mainloop()
