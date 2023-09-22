# Python Icons Generator for DAWs
![Screenshot](example.png)

September 2023, v1.0.0
by Loïc Desjardins, loic.desjardins@me.com

Have you ever dreamed of neat track icons in your DAW but were afraid to make them?
Here's a solution : a script batch generating icons according to your tracks!
These icons are espcially for use with DAW : Logic Pro, Cubase, Studio One, Reaper and any DAW that allows you to use custom track icons

# Dependencies
- **Python 3.1** or above
- **Pillow library**  https://pillow.readthedocs.io/en/stable/index.html

# Resources
- **icons-maker.ipynb** : Jupyter-Lab notebook, for users of Jupyter Lab IDE 
- **icons-maker.py** : Python script to execute, see comments inside for settings
- **tracks.json** : list of icons to generate, see comments inside to understand possibilities
- emboss64.png : exemple of 64x64 png to create emboss effect
- emboss128.png : exemple of 128x128 png to create emboss effect


# Installing and executing
- **Copy all resources** in your Python 3.1 enviromnment. I recommend creating a directory for this project
- Make sure that you allow the creation of subdirectories
- **Edit the file tracks.json** with any text editor and adapt it to your needs, following the guidelines described in the script or below
- For Python users : **execute icons-maker.py**
- For JupyterLab users : **open icons-maker.ipynb script and run it**


# License & support
Scripts is ** free to reuse**, but if you plan to release your own version, plesae cite me.
I won't offer any support for this script, and won't consider feature requests.
I might just upload newer version according to my needs.

# track.json editing guidelines

Each line should have the following structure : `{"main":"TPT","sub":["solo 1","solo 2","solo 3","solo 4","solo","a3","a6","bass","piccolo"],"style":0,"color":"#00CBC9","invert":1},`
- **main** : contains the main text of the icon. Mandatory. I advise to stay between 2 and 4 characters.
- **sub** : contains a list of variations in brackets. Each variation will generate an icon, with the main text on top and the smaller variation below . Can be set to [""] if you don't want any variation/subtext. I advise to stay below 8 characters
- **style** : can take 3 values (mandatory) :
-- 0 creates a regular icon
-- "group" creates an icon with an outline. I use this for ensemble libraries
-- "folder" creates a folder icons, especially for Logic Pro. It creates a half height icon with an outline and without any subtext.
- **color** : icon background color encoded as HEX color. Mandatory.
- **invert** : if present and set to 1, then the text will be black, otherwise it is white.

