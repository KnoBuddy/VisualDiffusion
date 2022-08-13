# VisualDiffusion
A GUI for text2img diffusion, as a visual alternative to CLI and Jupyter Notebooks.

If you would like support me, the development of this GUI, or maybe you have a feature that you desperately want added, please consider supporting me and this program's development on my [Patreon](https://www.patreon.com/knobuddy).

![image](https://user-images.githubusercontent.com/64171756/184508953-2c790ea0-c86b-4169-8ab9-061b0dae4e90.png)

# Instructions for updating VisualDiffusion
```
cd progrockdiffusion\visualdiffusion
git pull
```

# Instructions for using VisualDiffusion with progrockdiffusion

## Install PRD

Follow the [Instruction Here](https://github.com/lowfuel/progrockdiffusion).
## Install the GUI
```
conda activate progrockdiffusion
cd progrockdiffusion
git clone https://github.com/KnoBuddy/visualdiffusion/
```
### [Windows]
```
conda activate progrockdiffusion
cd progrockdiffusion
python visualdiffusion\prdgui.py
```
### [Linux/MacOS]
```
conda activate progrockdiffusion
cd progrockdiffusion
python3 visualdiffusion\prdgui.py
```
## Open the GUI

Open up a command line window (shell) and activate the conda environment like normal, and then run prdgui.py, from within the progrockdiffusion folder (NOT FROM WITHIN THE VISUAL DIFFUSION FOLDER).
Please read the [settings file](SETTINGS.md) if you are unfamiliar with PRD.

## Tips
You can add as many prompts as you please all with different weights. The "Save Settings" button saves the settings to gui_settings.json.
Make sure you select at least one CLIP Model, as well as all the text boxes having an appropriate value, some can be left empty. I also recommend naming your batch. 
If you need to cancel the render, you will have to kill the shell window you used to open the GUI.

The final text box is for extra shell arguments. They will be parsed after the initial command:
```
python prd.py -s gui_settings.json <YOUR ARGS GO HERE>
```
