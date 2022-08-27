# VisualDiffusion
A GUI for text2img diffusion, as a visual alternative to CLI and Jupyter Notebooks.

[CLICK HERE FOR PROGROCK DIFFUSION](#instructions-for-using-visualdiffusion-with-progrockdiffusion) or [CLICK HERE FOR PROGROCK-STABLE](#instructions-for-using-visualdiffusion-with-progrock-stable)

If you would like support me, the development of this GUI, or maybe you have a feature that you desperately want added, please consider supporting me and this software's development on my [Patreon](https://www.patreon.com/knobuddy).

# Instructions for updating VisualDiffusion
```
cd progrockdiffusion\visualdiffusion
git pull
```

# Instructions for using VisualDiffusion with progrockdiffusion
![image](https://user-images.githubusercontent.com/64171756/185768885-05d4ea88-e548-4912-b6ab-d3e40a65c4f7.png)
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



# Instructions for using VisualDiffusion with ProgRock-Stable
![image](https://user-images.githubusercontent.com/64171756/187046564-6ce159f9-202b-4b9e-b21a-bbba50e4ad68.png)
## Install PRS

Follow the [Instruction Here](https://github.com/lowfuel/progrock-stable).
## Install the GUI
```
conda activate prs
cd prs
git clone https://github.com/KnoBuddy/visualdiffusion/
```
### [Windows]
```
conda activate prs
cd prs
python visualdiffusion\prsgui.py
```
### [Linux/MacOS]
```
conda activate prs
cd prs
python3 visualdiffusion\prsgui.py
```
## Open the GUI

Open up a command line window (shell) and activate the conda environment like normal, and then run prdgui.py, from within the prs folder (NOT FROM WITHIN THE VISUAL DIFFUSION FOLDER).
Please familiarize yourself with ProgRock-Stable's Settings.

## Tips
You can add as many prompts as you please. The "Save Settings" button saves the settings to gui_settings.json.
Make sure all the text boxes having an appropriate value. I also recommend naming your batch. 
If you need to cancel the render, you will have to kill the shell window you used to open the GUI, or CTRL-C to keyboard exception out.
