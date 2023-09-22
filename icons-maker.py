#!/usr/bin/env python
# coding: utf-8

# In[63]:


from PIL import Image, ImageFont, ImageDraw,features,ImageEnhance,ImageFilter,ImageChops
import os
import glob
from os.path import join, dirname, abspath
import json
import math
import time, sys

# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%

def ProgressBar(Total, Progress, BarLength=20, ProgressIcon="#", BarIcon="-"):
    try:
        # You can't have a progress bar with zero or negative length.
        if BarLength <1:
            BarLength = 20
        # Use status variable for going to the next line after progress completion.
        Status = ""
        # Calcuting progress between 0 and 1 for percentage.
        Progress = float(Progress) / float(Total)
        # Doing this conditions at final progressing.
        if Progress >= 1.:
            Progress = 1
            Status = "\r\n"    # Going to the next line
        # Calculating how many places should be filled
        Block = int(round(BarLength * Progress))
        # Show this
        Bar = "[{}] {:.0f}% {}".format(ProgressIcon * Block + BarIcon * (BarLength - Block), round(Progress * 100, 0), Status)
        return Bar
    except:
        return "ERROR"

def ShowBar(Bar):
    sys.stdout.write(Bar)
    sys.stdout.flush()

#function to display text character by character and apply a tracking if needed
def draw_text_psd_style(draw, xy, text, font, tracking=0, leading=None, **kwargs):
    """
    usage: draw_text_psd_style(draw, (0, 0), "Test", 
                tracking=-0.1, leading=32, fill="Blue")

    Leading is measured from the baseline of one line of text to the
    baseline of the line above it. Baseline is the invisible line on which most
    letters—that is, those without descenders—sit. The default auto-leading
    option sets the leading at 120% of the type size (for example, 12‑point
    leading for 10‑point type).

    Tracking is measured in 1/1000 em, a unit of measure that is relative to 
    the current type size. In a 6 point font, 1 em equals 6 points; 
    in a 10 point font, 1 em equals 10 points. Tracking
    is strictly proportional to the current type size.
    """
    def stutter_chunk(lst, size, overlap=0, default=None):
        for i in range(0, len(lst), size - overlap):
            r = list(lst[i:i + size])
            while len(r) < size:
                r.append(default)
            yield r
    x, y = xy
    font_size = font.size
    lines = text.splitlines()
    if leading is None:
        leading = font.size * 1.2
    for line in lines:
        for a, b in stutter_chunk(line, 2, 1, ' '):
            w = font.getlength(a + b) - font.getlength(b)
            # dprint("[debug] kwargs")
           # print("[debug] kwargs:{}".format(kwargs))
                
            draw.text((x, y), a, font=font, **kwargs)
            x += w + (tracking / 1000) * font_size
        y += leading
        x = xy[0]



#function to compute ideal (largest) size of text according to the space & font
def optimize_fontsize(img,text,minsize,maxsize,style,font):

    """
    usage: optimize_fontsize(img,mytext,32,64,"group","Arial")

    img: refers to the destination img, particularly its size
    text: the input text to compute
    minsize: the mimimum size font in points. you may want this to ensure minimum readability
    maxsize: the maximum size font in points. you may want this to ensure big texts are cohesive
    style: icon style, according to it, margins are added to ensure space for the outline
    font: the font name to estimate the size to
    """
    
    fontsize = minsize
    fontx = ImageFont.truetype(os.path.join(font), size=minsize)
    draw = ImageDraw.Draw(img)
    draw.font=fontx #police de base de l'objet + antialiasing
    draw.fontmode="L"
    
    width=draw.textlength(text=text,font=fontx)

    if style=="group":
        margin=int(img.width*0.2)
    else:
        margin=int(img.width*0.0625)
    
    while 1 :
        fontx = ImageFont.truetype(os.path.join(font), size=fontsize)
        width=draw.textlength(text=text,font=fontx)
        if width>=img.width-margin or fontsize>=maxsize:
                break
        fontsize+=1
   
    yoffset=maxsize-fontsize
    #print(text+":"+str(fontsize)+":"+str(yoffset))

    return fontsize-1,yoffset



def getColors(hexaCol):
    """ Returns prefered text colors duplets according to a color"""
    color = hexaCol[1:] #check that prm exists

    #first, colors are converted from HEX to integer
    rY = int(color[0:2], base=16)
    gY = int(color[2:4], base=16)
    bY = int(color[4:6], base=16)

    #luminance is calculated, this formula is derived from luminance common definitions
    lumi=rY * 0.2126 + gY * 0.7152 + bY * 0.0722

    if lumi > 160:
        return ("#000000","#090909") #too bright? dark colors
    else: 
        return ("#ffffff","#fafafa") #dark? white colors


""" GLOBAL PARAMETERS SECTION """

#full color index in  Logic Pro X : not used, for future usage, all columns & lines are matching position of each color in the Logic Pro color grid + 5 shades of grey
#remove colors in the list if you want to create less variations
logicColors=[ 
    "#c03c1b","#c15a1d","#c27b21","#c4a326","#c8c82b","#a8c72a","#89c82a","#6dc829","#4bc83d","#4dc860","#50c982","#53caa6","#58cac9","#4da6c8","#4a99cd","#4b85d2","#4d6dd4","#4e4ed7","#624bd4","#7645d1","#8c3bcf","#9e26c7","#c024c7","#c020a3",
    "#9c3c23","#9c5224","#9d6a25","#a08727","#a2a22b","#8ba22a","#74a22a","#5fa32b","#41a33c","#41a357","#42a36f","#44a389","#47a4a3","#3f8aa2","#417fa5","#4672aa","#4860ad","#4a4aaf","#5847ac","#6741a9","#783ba9","#8328a2","#9c27a2","#9c2387",
    "#783826","#794626","#7a5727","#7b6a28","#7d7d2a","#6d7d2a","#5e7d29","#4f7d29","#377e37","#387e4a","#387e5b","#397e6c","#397f7e","#356d7e","#3a6680","#3e5c82","#3f5085","#414084","#4b3e84","#553b82","#613782","#68287d","#79277d","#78266b",
    "#552e23","#563724","#574124","#584d25","#595825","#4f5925","#465926","#3c5926","#2d592d","#2d5939","#2d5944","#2d594f","#2e595a","#2b4f59","#2f4c5b","#33465d","#333e5e","#34345e","#3b335e","#42315e","#472e5b","#4c2458","#562458","#56234e",
    "#000000","#333333","#666666","#999999","#CCCCCC","#FFFFFF"
]
colorList=[]

#global size of images. Everything is calculated accordingly
imgSize=64 

#reference font. Font has to be present in C:\Windows\Fonts or Font directory on Mac. CASE SENSITIVE.
#condensed bold fonts lead to better results : Avenir Next, Futura Medium Condensed, Arial Narrow Bold, DIN Condensed Bold, Hattenschweiler,...
#resource about how fonts are handled : https://pillow.readthedocs.io/en/stable/reference/ImageFont.html
fontRef='Avenir Next Condensed.ttc' 
#fontRef="HATTEN.TTF"

#overlay picture (inner shadow / emboss). This image has to exist matching the exact size of the output (eg. emboss512.png, emboss64.png).
#if the overlay image size doesn't match the icon size, the script will drop an error.
#some examples are provided (png + psd files)
overlay=Image.open('emboss'+str(imgSize)+'.png').convert("RGBA")
                  

#if set to 0, only the color associated in the icon definition list is generated. 
#if set to 1, the icon will be generated for each Logic color. BEWARE, it takes far more resources & size on disk. In this case, text color is adapted against each color luminance (black vs white text)
generateAllColors=0

""" END OF PARAMETERS"""


if not os.path.exists("icons"+str(imgSize)): #create the icons dir if not exists
   os.makedirs("icons"+str(imgSize))


for f in glob.glob("icons"+str(imgSize)+"/*.png"): #purge des images
    os.remove(f)


#opening the icon list
f = open('tracks.json')
data=json.load(f)
f.close() #closing the file

countTracks=len(data['tracks'])



for idxi,i in enumerate(data['tracks'],start=1): #browsing each track (line)
    text=i["main"] #main text for icon (1st line, best btw 2 & 4 chars)
    style=i["style"] #style : normal (0), or groupe (has outline) for ensembles, or folder pour Logic folders (lower height)
    
    for text2 in i["sub"]: #browsing variations within tracks, filling 2nd line

        color1='#ffffff' #setting text colors for main line & 2nd line
        color2='#fafafa'

        if generateAllColors==1: #retrieving icon background color
            colorList=logicColors    
        else:
            if len(colorList)==0:
                colorList.append(i["color"]) #in standard mode (icons only generated in their associated color), a 1 item list is created. If empty, 1 color is added. Once not empty, color is updated
            else:
                colorList[0]=i["color"]

        
        ShowBar("\rGenerating icons: " +ProgressBar(countTracks,idxi))
        time.sleep(0.001)
        
        countColors=len(colorList)
        
        for idxc,bgcolor in enumerate(colorList,start=1):
            
            if "invert" in i: #if inverted (e.g. hi luminance background), alternate colors for the 2 lines.
                color1='#000000'
                color2='#090909'
    
            
            if style=="folder": #if folder, height is reduced to 70%
                imgheight=int(imgSize*0.6875)
            else:
                imgheight=imgSize
    
            dst_img = Image.new('RGBA', (imgSize,imgheight),(0,0,0,0))
            draw = ImageDraw.Draw(dst_img)
    
            if generateAllColors==1: #if icons are generated in all colors, then the text color is automatically calculated
                (color1,color2)=getColors(bgcolor)
    
            
            radius=int(imgSize*0.109375) #radius for rounded corners
            
            draw.rounded_rectangle(xy=[(0,0),(imgSize,imgheight)],radius=radius,fill=bgcolor) #drawing icon background
            
            (size1,yoffset1) = optimize_fontsize(dst_img,text,int(imgSize*0.375),int(imgSize*0.5625),style,fontRef) #calculating ideal font sizes
            (size2,yoffset2) = optimize_fontsize(dst_img,text2,int(imgSize*0.25),int(imgSize*0.375),style,fontRef)
    
            font1 = ImageFont.truetype(os.path.join(fontRef), size=size1)
            font2 = ImageFont.truetype(os.path.join(fontRef), size=size2)
    
            draw.font=font1 #base font + activating anti aliasing
            draw.fontmode="L"
    
    
            text2length=draw.textlength(text=text2,font=font2)
            text2offset=dst_img.width-text2length-int(imgSize*0.03125) #calculating right justification for 2nd line
    
            if style=="group":
                text2offset-int(imgSize*0.03125) #for group tracks, adjusting offset to avoid overlapping on the outline
            
            draw_text_psd_style(draw, xy=(int(imgSize*0.05), yoffset1*imgheight/imgSize), font=font1,text=text, 
                            tracking=0, leading=10, fill=color1) #drawing 1st line
            
            if style!="folder": #pas de 2ème ligne pour les folder
                draw_text_psd_style(draw, xy=(text2offset, int(imgSize*0.53125)+yoffset2), font=font2,text=text2, 
                            tracking=0, leading=10, fill=color2) #and 2nd line (folders don't have 2nd line)
    
            outlineWidth=int(imgSize*0.03125) #calculating outline width
            
            if style!=0: #for group & folder tracks, drawing the outline
                draw.rounded_rectangle(xy=[(0,0),(imgSize-(outlineWidth/2),imgheight-(outlineWidth/2))],radius=(radius-outlineWidth),fill=None,outline=color1,width=outlineWidth)     
    
            
            if style==0:
                dst_img=ImageChops.multiply(overlay,dst_img) #adding internal shadow overlay
            
            dst_img = ImageEnhance.Sharpness(dst_img).enhance(2) #sharpening enhancement
            
            dst_img.save("icons"+str(imgSize)+"/"+text+"-"+text2+"-"+bgcolor+'.png',"PNG") #each icon is saved according to the main text, sub text & color

print("\rFinished")




