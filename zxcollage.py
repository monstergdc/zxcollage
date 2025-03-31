#! /usr/bin/env python
# -*- coding: utf-8 -*-

# big collage from ZX images from ZXArt.ee
# (c)2025 MoNsTeR/GDC, Noniewicz.com, Jakub Noniewicz
# cre: 20250225
# upd: 20250226, 27
# upd: 20250331

# testd with py: 3.8.10, ?

""" TODO:
- opt sort in bars by zx colors (map: 2645) [zxbar]?
xxxxxxx02
xxxxxx026
xxxxx0264
xxxx02645
xxx026450
xx0264500
x02645000
026450000
"""

from PIL import Image, ImageDraw, ImageFont, ImageOps, PngImagePlugin
from pathlib import Path
import os
from datetime import datetime
import random
import numpy as np
import math, string, sys, io, copy
from os import walk
import binascii
import json
from colorthief import ColorThief # for dominant color, https://github.com/fengsp/color-thief-py
import cgi


def get_cgi_par(default=None):
    """ Parse CGI parameters """
    form = cgi.FieldStorage()
    if default == None:
        par = {'size': 'A3-portrait', 'shuffle': True, 'logo': True, 'txt': True, 'zxbar': True}
    else:
        par = default
    if "size" in form:
        par['size'] = form["size"].value
    if "shuffle" in form:
        par['shuffle'] = int(form["shuffle"].value) != 0
    if "logo" in form:
        par['logo'] = int(form["logo"].value) != 0
    if "zxbar" in form:
        par['zxbar'] = int(form["zxbar"].value) != 0
    return par

def gen_desc(will_fit_cnt, n):
    """ Generate text description """
    when = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    s = f'A collage from {will_fit_cnt} of {n} subjectively curated ZX Spectrum images, generated: {when}'
    return s

def append_pnginfo(extra=""):
    """ Append some tags to PNG image """
    x = PngImagePlugin.PngInfo()
    s = 'Concept by Jakub Noniewicz aka MoNsTeR/GDC.'
    if extra != "":
        s += '\r\n' + extra
    x.add_text(key='Title', value='Collage of ZX Spectrum images from https://zxart.ee', zip=False)
    x.add_text(key='Description', value=s, zip=False)
    return x

def im2cgi(im, will_fit_cnt, n):
    """ Output image in CGI mode as bytes to stdout """

    imgByteArr = io.BytesIO()
    ex = gen_desc(will_fit_cnt, n)
    im.save(imgByteArr, format='PNG', pnginfo=append_pnginfo(ex))

    data = imgByteArr.getvalue()
    
    ct = 'image/png'
    sys.stdout.write("Content-Type: "+ct+"\n")
    sys.stdout.write("Content-Length: " + str(len(data)) + "\n") # todo: chk if proper
    #sys.stdout.write("Transfer-Encoding: chunked\n")  # For chunked responses (if supported by the server)
    sys.stdout.write("\n")
    sys.stdout.flush()
    #sys.stdout.write(data) # no?
    #sys.stdout.write(data.decode('utf-8')) # yes? no
    sys.stdout.buffer.write(data) # yes?
    sys.stdout.flush()

def reshape_1d_to_2d(arr, height, width):
    """Reshape a 1D array into a 2D array with given height and width, truncating excess elements."""
    size = height * width
    arr = arr[:size]  # Truncate excess elements
    return arr.reshape(height, width)

def reshape_3d_to_1d(arr):
    """Reshape a 3D array back into a 1D array, preserving row order."""
    return arr.ravel()  # Flatten in row-major order (default)

def enumgfx(foldername, patt):
    """ Enumarete GFX files """
    a = []
    folder = Path(foldername)
    for file in folder.rglob(patt):
        a.append(file)
    return a

def convert(a, folder):
    """ Convert ZX .scr files to .png """
    from pyzx48tools import zxgfx
    zx = zxgfx()
    print(f'converting {len(a)} ZX images to png')
    for one in a:
        #print(one)
        zx.zx2image(fn=one, fn_out=folder+'/'+one.name+'.png')

def getFontSize(fnt, s):
    bbox = fnt.getbbox(s) # Returns (x_min, y_min, x_max, y_max)
    twh = (bbox[2] - bbox[0], bbox[3] - bbox[1]) # Width = x_max - x_min, Height = y_max - y_min
    return twh

def collage(output_mode, size, files, shuffle, logo=True, txt=True, zxbar=True):
    """ Main collage generator """
    bg = (255, 255, 255) # white bg seems best for print
    imout = Image.new('RGB', size, bg)
    draw = ImageDraw.Draw(imout)

    n = len(files)
    mar = 5 # margin around single image
    mar0x = 70 # block margin left/right (readjusted later)
    mar0y = 70 # block margin top/bottom (readjusted later)
    will_fit = ((size[0]-mar0x*2)//(256+mar), (size[1]-mar0y*2)//(192+mar))
    will_fit_cnt0 = will_fit[0]*will_fit[1]
    mar0x = (size[0]-will_fit[0]*(256+mar))//2
    mar0y = (size[1]-will_fit[1]*(192+mar))//2

    # opt empty space at center for logo
    if logo:
        empty_w = 4
        empty_h = 3
        empty_x = (will_fit[0] - empty_w)//2
        empty_y = (will_fit[1] - empty_h)//2
    else:
        empty_w = 0
        empty_h = 0
        empty_x = 0
        empty_y = 0
    will_fit_cnt = will_fit[0]*will_fit[1] - empty_w*empty_h

    if output_mode == 'save':
        print(f"fit: {will_fit[0]} x {will_fit[1]} = {will_fit_cnt0} -> {will_fit_cnt} from {n} mar: {mar0x}/{mar0y}")

    # todo: zx bar opt
    files = reshape_1d_to_2d(np.array(files), will_fit[0], will_fit[1])
    files = reshape_3d_to_1d(files)

    x = mar0x
    y = mar0y
    xc = 0
    yc = 0
    total = 0

    for one in files:
        im = Image.open(one)
        #im.thumbnail((256, 192)) # assume already ok
        imout.paste(im, (x, y))

        if False: # debug print name
            fnt = ImageFont.truetype(font='tahoma.ttf', size=12)
            draw.text((x+2, y+2), one.name, font=fnt, fill=(0, 0, 0))
            draw.text((x+1, y+1), one.name, font=fnt, fill=(255, 255, 255))
            draw.text((x, y), one.name, font=fnt, fill=(255, 255, 0))

        x += 256 + mar
        xc += 1
        total += 1

        # center skip for logo
        if xc >= empty_x and xc < empty_x+empty_w:
            if yc >= empty_y and yc < empty_y+empty_h:
                xc += empty_w
                x += (256 + mar) * empty_w

        if xc >= will_fit[0]:
            x = mar0x
            xc = 0
            y += 192 + mar
            yc += 1
        if total >= will_fit_cnt:
            break

    if logo:
        im = Image.open('./baner2025.png')
        x0 = empty_x * (256+mar) + mar0x
        y0 = empty_y * (192+mar) + mar0y
        x = (empty_w * (256+mar) - im.width)//2
        y = (empty_h * (192+mar) - im.height)//2
        imout.paste(im, (x0+x, y0+y))

    if txt:
        f = './zx1.ttf'
        size = 30
        fill=(56, 56, 56)
        fnt = ImageFont.truetype(font=f, size=size)
        s1 = 'Concept (c)2025 MoNsTeR/GDC, https://Noniewicz.com, images source: https://zxart.ee (batch 2022-10-21)'
        s2 = gen_desc(will_fit_cnt, n)
        twh1 = getFontSize(fnt, s1)
        twh2 = getFontSize(fnt, s2)
        txmar = 8 # extra space
        yy = (mar0y-twh1[1]-twh2[1]-txmar-txmar)//2
        draw.text((mar0x, imout.height-mar0y+yy+0), s1, font=fnt, fill=fill)
        draw.text((mar0x, imout.height-mar0y+yy+twh1[1]+txmar), s2, font=fnt, fill=fill)

    return imout, will_fit_cnt

def all_collages(output_mode, folder, outfolder, sizes, pfx="", shuffle=True, logo=True, txt=True, zxbar=True):
    """ Collage looper per sizes """
    files = enumgfx(folder, "*.png")
    if shuffle:
        random.shuffle(files) # or shuffle
    else:
        files.sort() # or sort
    n = len(files)

    for z in sizes:
        im, will_fit_cnt = collage(output_mode, sizes[z], files, shuffle, logo, txt, zxbar)
        # >>> par proper: s2
        if output_mode == 'save':
            destination = f'{outfolder}/{pfx}{z}.png'
            print(f"saving image: {destination}")
            ex = gen_desc(will_fit_cnt, n)
            im.save(destination, dpi=(300,300), pnginfo=append_pnginfo(ex))
        if output_mode == 'cgi':
            im2cgi(im, will_fit_cnt, n)

def all_sizes():
    return {
        'A3-landscape': (4960, 3507),
        'A3-portrait': (3507, 4960),
        'A2-landscape': (7015, 4960),
        'A2-portrait': (4960, 7015),
        'A1-landscape': (9933, 7015),
        'A1-portrait': (7015, 9933),
        'A0-landscape': (14043, 9933),
        'A0-portrait': (9933, 14043),
    }

if __name__ == '__main__':

    folder = "./allgfx" # source images

    # this would be needed once to generate .png from .scr
    if False:
        os.makedirs(folder, exist_ok=True)
        a = enumgfx("f:/zxart_files_1666370557 [cut]", "*.scr")
        convert(a, folder)

    sizes = all_sizes()
    outfolder = "./generated"
    all_collages('save', folder, outfolder, sizes, pfx="zxcollage-", shuffle=True, logo=True, txt=True, zxbar=True)

# EOF
