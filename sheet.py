import os
import shutil
import hashlib
from PIL import Image, ImageDraw, ImageFont
import stories

# --- Font Helper & Cache ---
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

_font_cache = {}
def F(path, size):
    key = (path, round(float(size), 1))
    if key not in _font_cache:
        try:
            _font_cache[key] = ImageFont.truetype(path, float(size))
        except Exception:
            _font_cache[key] = ImageFont.load_default()
    return _font_cache[key]

def wrap(text, font, max_width):
    words = text.split()
    if not words:
        return [""]
    lines = []
    current_line = []
    for word in words:
        test_line = " ".join(current_line + [word])
        try:
            w = font.getlength(test_line)
        except AttributeError:
            w = font.font.getsize(test_line)[0] if hasattr(font, 'font') else len(test_line) * 6
        if w <= max_width or not current_line:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def get_fitted_tile_desc(desc, max_width, max_lines=3):
    for size in [9.5, 9.0, 8.5, 8.0]:
        font = F(FONT_SANS, size)
        lines = wrap(desc, font, max_width)
        if len(lines) <= max_lines:
            return font, lines
    font = F(FONT_SANS, 8.0)
    lines = wrap(desc, font, max_width)
    return font, lines[:max_lines]

def get_fitted_lead_desc(desc, max_width, max_height, max_lines=5):
    for size in [10.5, 10.0, 9.5, 9.0, 8.5, 8.0]:
        font = F(FONT_SANS, size)
        lines = wrap(desc, font, max_width)
        total_h = len(lines) * (size + 3)
        if total_h <= max_height and len(lines) <= max_lines:
            return font, lines
    font = F(FONT_SANS, 8.0)
    lines = wrap(desc, font, max_width)
    return font, lines[:max_lines]

def wrap_also_paragraph_full(headline, desc, font_size, max_width):
    fb = F(FONT_SANS_BOLD, font_size)
    fr = F(FONT_SANS, font_size)
    
    h_words = headline.split()
    d_words = desc.split()
    tokens = [(w, True) for w in h_words] + [("—", True)] + [(w, False) for w in d_words]
    
    lines = []
    current_line = []
    
    for token, is_bold in tokens:
        font = fb if is_bold else fr
        test_line = current_line + [(token, is_bold)]
        test_str = " ".join([t[0] for t in test_line])
        try:
            w = font.getlength(test_str)
        except AttributeError:
            w = len(test_str) * 5.5
            
        if w <= max_width or not current_line:
            current_line.append((token, is_bold))
        else:
            lines.append(current_line)
            current_line = [(token, is_bold)]
    if current_line:
        lines.append(current_line)
    return lines

def get_fitted_also_item_3col(headline, desc, max_width, max_lines=3):
    for size in [9.0, 8.5, 8.0, 7.5]:
        lines = wrap_also_paragraph_full(headline, desc, size, max_width)
        if len(lines) <= max_lines:
            return size, lines
    size = 7.5
    lines = wrap_also_paragraph_full(headline, desc, size, max_width)
    return size, lines[:max_lines]

# --- ASCII Landmask for Map ---
ASCII_LAND = [
    "################################################################################################",
    "################################################################################################",
    "################################################################################################",
    "###  ###################   ######################################   ############################",
    "###  #################       ##################################       ##########################",
    "###   ##############           ###############################         #########################",
    "###     ##########               ############################           ########################",
    "###                               #########################               ######################",
    "###       #####                     #####################                   ####################",
    "###       ###                         #################                       ##################",
    "##                                     ###############                         #################",
    "##                                       ###########                            #################",
    "##                                        #########                              #################",
    "##                                         ######                                ################",
    "##           ###                             ##                                  #################",
    "##         ######                                                                #################",
    "##        ########                                                               ################",
    "##       ##########                                                             ##################",
    "##      ############                                                            ##################",
    "##      #############                                                           ##################",
    "###    ###############                                                         ###################",
    "###    ################                                                       ####################",
    "###   #################                                                      #####################",
    "####  ##################                                                    ######################",
    "#### ###################                                                   #######################",
    "########################                                                  ########################",
    "#########################                                                #########################",
    "##########################                                              ##########################",
    "###########################                                            ###########################",
    "############################                                          ############################",
    "#############################                                        #############################",
    "##############################                                      ##############################",
    "###############################                                    ###############################",
    "################################                                  ################################",
    "#################################                                #################################",
    "##################################                              ##################################",
    "###################################                            ###################################",
    "####################################                          ####################################",
    "#####################################                        #####################################",
    "######################################                      ######################################",
    "#######################################                    #######################################",
    "########################################                  ########################################",
    "#########################################                #########################################",
    "################################################################################################"
]

# --- Icon Renderer ---
def draw_icon(draw, key, cx, cy, size, colour=(255, 255, 255)):
    r = size / 2.0
    k = key.lower().strip()
    
    if k == "leaf":
        draw.ellipse([cx - r*0.6, cy - r*0.8, cx + r*0.6, cy + r*0.8], outline=colour, width=2)
        draw.line([cx - r*0.4, cy + r*0.6, cx + r*0.4, cy - r*0.6], fill=colour, width=2)
    elif k == "building":
        draw.rectangle([cx - r*0.6, cy - r*0.8, cx + r*0.6, cy + r*0.8], outline=colour, width=2)
        draw.rectangle([cx - r*0.3, cy - r*0.5, cx - r*0.1, cy - r*0.2], fill=colour)
        draw.rectangle([cx + r*0.1, cy - r*0.5, cx + r*0.3, cy - r*0.2], fill=colour)
        draw.rectangle([cx - r*0.3, cy - r*0.0, cx - r*0.1, cy + r*0.3], fill=colour)
        draw.rectangle([cx + r*0.1, cy - r*0.0, cx + r*0.3, cy + r*0.3], fill=colour)
    elif k == "flame":
        draw.polygon([
            (cx, cy - r*0.9),
            (cx + r*0.7, cy + r*0.6),
            (cx - r*0.7, cy + r*0.6)
        ], outline=colour, width=2)
        draw.ellipse([cx - r*0.3, cy, cx + r*0.3, cy + r*0.6], fill=colour)
    elif k == "badge":
        draw.polygon([
            (cx, cy - r*0.8),
            (cx + r*0.7, cy - r*0.3),
            (cx + r*0.5, cy + r*0.8),
            (cx - r*0.5, cy + r*0.8),
            (cx - r*0.7, cy - r*0.3)
        ], outline=colour, width=2)
        draw.rectangle([cx - r*0.2, cy - r*0.1, cx + r*0.2, cy + r*0.3], fill=colour)
    elif k == "chart":
        draw.line([cx - r*0.7, cy + r*0.7, cx - r*0.7, cy - r*0.7], fill=colour, width=2)
        draw.line([cx - r*0.7, cy + r*0.7, cx + r*0.7, cy + r*0.7], fill=colour, width=2)
        draw.line([cx - r*0.5, cy + r*0.2, cx - r*0.2, cy - r*0.1], fill=colour, width=2)
        draw.line([cx - r*0.2, cy - r*0.1, cx + r*0.1, cy + r*0.3], fill=colour, width=2)
        draw.line([cx + r*0.1, cy + r*0.3, cx + r*0.5, cy - r*0.5], fill=colour, width=2)
    elif k == "hands":
        draw.arc([cx - r*0.8, cy - r*0.5, cx, cy + r*0.5], start=270, end=90, fill=colour, width=2)
        draw.arc([cx, cy - r*0.5, cx + r*0.8, cy + r*0.5], start=90, end=270, fill=colour, width=2)
        draw.line([cx - r*0.3, cy, cx + r*0.3, cy], fill=colour, width=2)
    elif k == "cap":
        draw.polygon([
            (cx, cy - r*0.6),
            (cx + r*0.8, cy),
            (cx, cy + r*0.5),
            (cx - r*0.8, cy)
        ], outline=colour, width=2)
        draw.line([cx + r*0.3, cy + r*0.25, cx + r*0.6, cy + r*0.6], fill=colour, width=2)
    elif k == "lock":
        draw.rectangle([cx - r*0.6, cy - r*0.1, cx + r*0.6, cy + r*0.7], outline=colour, width=2)
        draw.arc([cx - r*0.4, cy - r*0.8, cx + r*0.4, cy], start=180, end=360, fill=colour, width=2)
        draw.ellipse([cx - r*0.15, cy + r*0.2, cx + r*0.15, cy + r*0.4], fill=colour)
    elif k == "factory":
        draw.rectangle([cx - r*0.7, cy - r*0.2, cx + r*0.7, cy + r*0.7], outline=colour, width=2)
        draw.polygon([(cx - r*0.5, cy - r*0.2), (cx - r*0.3, cy - r*0.7), (cx - r*0.1, cy - r*0.2)], outline=colour, width=2)
        draw.polygon([(cx + r*0.1, cy - r*0.2), (cx + r*0.3, cy - r*0.6), (cx + r*0.5, cy - r*0.2)], outline=colour, width=2)
    elif k == "boat":
        draw.polygon([
            (cx - r*0.8, cy + r*0.2),
            (cx + r*0.8, cy + r*0.2),
            (cx + r*0.5, cy + r*0.7),
            (cx - r*0.5, cy + r*0.7)
        ], outline=colour, width=2)
        draw.line([cx, cy + r*0.2, cx, cy - r*0.7], fill=colour, width=2)
        draw.polygon([(cx, cy - r*0.7), (cx + r*0.5, cy - r*0.3), (cx, cy - r*0.1)], fill=colour)
    elif k == "planet":
        draw.ellipse([cx - r*0.5, cy - r*0.5, cx + r*0.5, cy + r*0.5], outline=colour, width=2)
        draw.ellipse([cx - r*0.9, cy - r*0.2, cx + r*0.9, cy + r*0.2], outline=colour, width=1)
    elif k == "dna":
        draw.line([cx - r*0.4, cy - r*0.7, cx + r*0.4, cy + r*0.7], fill=colour, width=2)
        draw.line([cx + r*0.4, cy - r*0.7, cx - r*0.4, cy + r*0.7], fill=colour, width=2)
        draw.ellipse([cx - r*0.5, cy - r*0.7, cx - r*0.3, cy - r*0.5], fill=colour)
        draw.ellipse([cx + r*0.3, cy - r*0.7, cx + r*0.5, cy - r*0.5], fill=colour)
        draw.ellipse([cx - r*0.5, cy + r*0.5, cx - r*0.3, cy + r*0.7], fill=colour)
        draw.ellipse([cx + r*0.3, cy + r*0.5, cx + r*0.5, cy + r*0.7], fill=colour)
    elif k == "drone":
        draw.line([cx - r*0.7, cy - r*0.7, cx + r*0.7, cy + r*0.7], fill=colour, width=2)
        draw.line([cx - r*0.7, cy + r*0.7, cx + r*0.7, cy - r*0.7], fill=colour, width=2)
        draw.ellipse([cx - r*0.3, cy - r*0.3, cx + r*0.3, cy + r*0.3], fill=colour)
        draw.ellipse([cx - r*0.8, cy - r*0.8, cx - r*0.5, cy - r*0.5], outline=colour, width=1)
        draw.ellipse([cx + r*0.5, cy - r*0.8, cx + r*0.8, cy - r*0.5], outline=colour, width=1)
        draw.ellipse([cx - r*0.8, cy + r*0.5, cx - r*0.5, cy + r*0.8], outline=colour, width=1)
        draw.ellipse([cx + r*0.5, cy + r*0.5, cx + r*0.8, cy + r*0.8], outline=colour, width=1)
    elif k == "ship":
        draw.polygon([
            (cx - r*0.9, cy), (cx + r*0.9, cy),
            (cx + r*0.6, cy + r*0.6), (cx - r*0.6, cy + r*0.6)
        ], outline=colour, width=2)
        draw.rectangle([cx - r*0.3, cy - r*0.6, cx + r*0.3, cy], outline=colour, width=2)
        draw.rectangle([cx - r*0.1, cy - r*0.9, cx + r*0.1, cy - r*0.6], fill=colour)
    elif k == "missile":
        draw.polygon([
            (cx + r*0.8, cy - r*0.8),
            (cx - r*0.8, cy + r*0.8),
            (cx - r*0.4, cy + r*0.4)
        ], fill=colour)
        draw.line([cx - r*0.8, cy + r*0.8, cx - r*0.4, cy + r*0.7], fill=colour, width=3)
    elif k == "aid":
        draw.rectangle([cx - r*0.6, cy - r*0.6, cx + r*0.6, cy + r*0.6], outline=colour, width=2)
        draw.rectangle([cx - r*0.2, cy - r*0.4, cx + r*0.2, cy + r*0.4], fill=colour)
        draw.rectangle([cx - r*0.4, cy - r*0.2, cx + r*0.4, cy + r*0.2], fill=colour)
    elif k == "eye":
        draw.arc([cx - r*0.8, cy - r*0.5, cx + r*0.8, cy + r*0.5], start=0, end=180, fill=colour, width=2)
        draw.arc([cx - r*0.8, cy - r*0.5, cx + r*0.8, cy + r*0.5], start=180, end=360, fill=colour, width=2)
        draw.ellipse([cx - r*0.3, cy - r*0.3, cx + r*0.3, cy + r*0.3], fill=colour)
    elif k == "tv":
        draw.rectangle([cx - r*0.8, cy - r*0.6, cx + r*0.8, cy + r*0.3], outline=colour, width=2)
        draw.line([cx - r*0.4, cy + r*0.6, cx, cy + r*0.3], fill=colour, width=2)
        draw.line([cx + r*0.4, cy + r*0.6, cx, cy + r*0.3], fill=colour, width=2)
    elif k == "flag":
        draw.line([cx - r*0.5, cy - r*0.8, cx - r*0.5, cy + r*0.8], fill=colour, width=2)
        draw.polygon([
            (cx - r*0.5, cy - r*0.8),
            (cx + r*0.7, cy - r*0.5),
            (cx - r*0.5, cy - r*0.2)
        ], fill=colour)
    elif k == "heart":
        draw.polygon([
            (cx, cy + r*0.7),
            (cx - r*0.8, cy - r*0.2),
            (cx - r*0.4, cy - r*0.8),
            (cx, cy - r*0.3),
            (cx + r*0.4, cy - r*0.8),
            (cx + r*0.8, cy - r*0.2)
        ], fill=colour)
    elif k == "gavel":
        draw.line([cx - r*0.6, cy + r*0.6, cx + r*0.6, cy - r*0.6], fill=colour, width=3)
        draw.rectangle([cx + r*0.3, cy - r*0.8, cx + r*0.8, cy - r*0.3], outline=colour, width=2)
    elif k == "plane":
        draw.polygon([
            (cx, cy - r*0.8),
            (cx + r*0.2, cy - r*0.2),
            (cx + r*0.8, cy + r*0.3),
            (cx + r*0.2, cy + r*0.3),
            (cx, cy + r*0.6),
            (cx - r*0.2, cy + r*0.3),
            (cx - r*0.8, cy + r*0.3),
            (cx - r*0.2, cy - r*0.2)
        ], fill=colour)
    elif k == "bolt":
        draw.polygon([
            (cx + r*0.2, cy - r*0.9),
            (cx - r*0.6, cy + r*0.1),
            (cx, cy + r*0.1),
            (cx - r*0.2, cy + r*0.9),
            (cx + r*0.6, cy - r*0.1),
            (cx, cy - r*0.1)
        ], fill=colour)
    elif k == "cross":
        draw.rectangle([cx - r*0.25, cy - r*0.7, cx + r*0.25, cy + r*0.7], fill=colour)
        draw.rectangle([cx - r*0.7, cy - r*0.25, cx + r*0.7, cy + r*0.25], fill=colour)
    elif k == "wave":
        draw.arc([cx - r*0.8, cy - r*0.5, cx, cy + r*0.5], start=0, end=180, fill=colour, width=2)
        draw.arc([cx, cy - r*0.5, cx + r*0.8, cy + r*0.5], start=180, end=360, fill=colour, width=2)
        draw.arc([cx - r*0.4, cy, cx + r*0.4, cy + r*0.8], start=0, end=180, fill=colour, width=2)
    elif k == "rain":
        draw.line([cx - r*0.5, cy - r*0.5, cx + r*0.5, cy - r*0.5], fill=colour, width=2)
        draw.line([cx - r*0.4, cy - r*0.2, cx - r*0.5, cy + r*0.2], fill=colour, width=2)
        draw.line([cx, cy - r*0.2, cx - r*0.1, cy + r*0.2], fill=colour, width=2)
        draw.line([cx + r*0.4, cy - r*0.2, cx + r*0.3, cy + r*0.2], fill=colour, width=2)
    elif k == "rig":
        draw.line([cx - r*0.6, cy + r*0.7, cx + r*0.6, cy + r*0.7], fill=colour, width=3)
        draw.line([cx - r*0.4, cy + r*0.7, cx - r*0.2, cy - r*0.7], fill=colour, width=2)
        draw.line([cx + r*0.4, cy + r*0.7, cx + r*0.2, cy - r*0.7], fill=colour, width=2)
        draw.line([cx - r*0.4, cy - r*0.2, cx + r*0.4, cy - r*0.2], fill=colour, width=2)
    elif k == "taxi":
        draw.rectangle([cx - r*0.7, cy - r*0.3, cx + r*0.7, cy + r*0.5], outline=colour, width=2)
        draw.ellipse([cx - r*0.5, cy + r*0.3, cx - r*0.2, cy + r*0.8], fill=colour)
        draw.ellipse([cx + r*0.2, cy + r*0.3, cx + r*0.5, cy + r*0.8], fill=colour)
    elif k == "bone":
        draw.ellipse([cx - r*0.7, cy - r*0.6, cx - r*0.3, cy - r*0.2], fill=colour)
        draw.ellipse([cx + r*0.3, cy - r*0.6, cx + r*0.7, cy - r*0.2], fill=colour)
        draw.ellipse([cx - r*0.7, cy + r*0.2, cx - r*0.3, cy + r*0.6], fill=colour)
        draw.ellipse([cx + r*0.3, cy + r*0.2, cx + r*0.7, cy + r*0.6], fill=colour)
        draw.line([cx - r*0.4, cy - r*0.4, cx + r*0.4, cy + r*0.4], fill=colour, width=3)
    elif k == "car":
        draw.rectangle([cx - r*0.8, cy - r*0.1, cx + r*0.8, cy + r*0.5], outline=colour, width=2)
        draw.polygon([(cx - r*0.4, cy - r*0.1), (cx - r*0.2, cy - r*0.7), (cx + r*0.2, cy - r*0.7), (cx + r*0.4, cy - r*0.1)], fill=colour)
        draw.ellipse([cx - r*0.5, cy + r*0.3, cx - r*0.2, cy + r*0.7], fill=colour)
        draw.ellipse([cx + r*0.2, cy + r*0.3, cx + r*0.5, cy + r*0.7], fill=colour)
    elif k == "ball":
        draw.ellipse([cx - r*0.7, cy - r*0.7, cx + r*0.7, cy + r*0.7], outline=colour, width=2)
        draw.arc([cx - r*0.7, cy - r*0.7, cx + r*0.7, cy + r*0.7], start=30, end=150, fill=colour, width=2)
        draw.arc([cx - r*0.7, cy - r*0.7, cx + r*0.7, cy + r*0.7], start=210, end=330, fill=colour, width=2)
    elif k == "knight":
        draw.polygon([
            (cx - r*0.5, cy + r*0.7),
            (cx + r*0.5, cy + r*0.7),
            (cx + r*0.4, cy + r*0.2),
            (cx + r*0.6, cy - r*0.2),
            (cx + r*0.3, cy - r*0.7),
            (cx - r*0.2, cy - r*0.5),
            (cx - r*0.5, cy - r*0.2)
        ], fill=colour)
    else:
        draw.ellipse([cx - r*0.5, cy - r*0.5, cx + r*0.5, cy + r*0.5], outline=colour, width=2)
        draw.ellipse([cx - r*0.15, cy - r*0.15, cx + r*0.15, cy + r*0.15], fill=colour)

def draw_banner_pill(draw, x, py, region, icon_key, label_text, font_size=8.5, box_w=12, pill_h=14):
    col = stories.REGION_COLOURS.get(region, (84, 94, 106))
    f_pill = F(FONT_SANS_BOLD, font_size)
    try:
        lw = f_pill.getlength(label_text)
    except AttributeError:
        lw = len(label_text) * 5
    pill_w = box_w + 4 + lw + 6
    draw.rounded_rectangle([x, py, x + pill_w, py + pill_h], radius=pill_h/2, fill=col)
    draw_icon(draw, icon_key, x + box_w/2, py + pill_h/2, box_w - 4, colour=(255, 255, 255))
    draw.text((x + box_w + 3, py + (pill_h - font_size)/2 - 1), label_text, fill=(255, 255, 255), font=f_pill)
    return pill_w

# --- Main Render Function ---
def render():
    img = Image.new("RGB", (1024, 1024), (12, 34, 38))
    draw = ImageDraw.Draw(img)
    
    sheet_box = [14, 14, 1010, 1010]
    draw.rounded_rectangle(sheet_box, radius=8, fill=(247, 241, 228), outline=None)
    
    INK = (32, 36, 42)
    GOLD_DARK = (150, 95, 10)
    RED = (179, 35, 27)
    SLATE = (110, 115, 125)
    LAND_COLOUR = (214, 196, 150)
    
    y = 18 # start inside sheet top
    
    # 1. MASTHEAD (rebalanced ≤92px)
    f_mast_sub = F(FONT_SANS_BOLD, 8.5)
    draw.text((32, y), "THE WORLD'S NEWS IN ONE PICTURE", fill=RED, font=f_mast_sub)
    count_w = f_mast_sub.getlength(stories.COUNT_LINE) if hasattr(f_mast_sub, 'getlength') else len(stories.COUNT_LINE)*6
    draw.text((992 - count_w, y), stories.COUNT_LINE, fill=SLATE, font=f_mast_sub)
    y += 13
    
    f_paper = F(FONT_SERIF_BOLD, 34)
    paper_w = f_paper.getlength(stories.PAPER_NAME) if hasattr(f_paper, 'getlength') else len(stories.PAPER_NAME)*18
    draw.text((1024/2 - paper_w/2, y), stories.PAPER_NAME, fill=INK, font=f_paper)
    y += 38
    
    draw.line([(32, y), (992, y)], fill=INK, width=2)
    y += 3
    draw.line([(32, y), (992, y)], fill=INK, width=1)
    y += 4
    
    f_date = F(FONT_SERIF_BOLD, 13.5)
    date_w = f_date.getlength(stories.DATE_LINE) if hasattr(f_date, 'getlength') else len(stories.DATE_LINE)*7.5
    draw.text((1024/2 - date_w/2, y), stories.DATE_LINE, fill=INK, font=f_date)
    y += 17
    
    f_tagline = F(FONT_SANS, 8.0)
    tagline_text = "The day's world news, summed up in one picture"
    tag_w = f_tagline.getlength(tagline_text) if hasattr(f_tagline, 'getlength') else len(tagline_text)*5
    draw.text((1024/2 - tag_w/2, y), tagline_text, fill=SLATE, font=f_tagline)
    y += 12
    # Total masthead height: 18 to y (~87px, <=92px)
    
    # 2. BREAKING STRIP (27px)
    breaking_box = [32, y, 992, y + 27]
    draw.rectangle(breaking_box, fill=RED)
    f_break = F(FONT_SANS_BOLD, 9.5)
    break_text = f"BREAKING — {stories.BREAKING}"
    draw.text((42, y + 7), break_text, fill=(255, 255, 255), font=f_break)
    y += 27 + 6
    
    # 3. LEADS ROW (stories 1–3, ≤200px)
    left_margin = 32
    usable_width = 992 - left_margin * 2 # 928
    gutter = 16
    col_width = (usable_width - gutter * 2) / 3
    col_w = int(col_width)
    
    for i in range(3):
        story = stories.MAINS[i]
        col_x = left_margin + i * (col_w + gutter)
        
        panel_box = [col_x, y, col_x + col_w, y + 76]
        base_col = stories.REGION_COLOURS.get(story["region"], (84, 94, 106))
        bg_col = (int(base_col[0]*0.4 + 200*0.6), int(base_col[1]*0.4 + 200*0.6), int(base_col[2]*0.4 + 200*0.6))
        draw.rectangle(panel_box, fill=bg_col)
        
        draw_icon(draw, story["icon"], col_x + col_w/2, y + 38, 32, colour=(255, 255, 255))
        
        circ_r = 8
        circ_cx = col_x + 12
        circ_cy = y + 12
        draw.ellipse([circ_cx - circ_r, circ_cy - circ_r, circ_cx + circ_r, circ_cy + circ_r], fill=(255, 255, 255))
        f_num = F(FONT_SANS_BOLD, 8.5)
        draw.text((circ_cx - 3.5, circ_cy - 5), str(story["n"]), fill=INK, font=f_num)
        
        py = y + 79
        f_head = F(FONT_SANS_BOLD, 14)
        lines = wrap(story["headline"], f_head, col_w)
        for l in lines[:3]:
            draw.text((col_x, py), l, fill=INK, font=f_head)
            py += 17
            
        py += 2
        pill_h = 15
        draw_banner_pill(draw, col_x, py, story["region"], story["icon"], story["label"], font_size=9, box_w=14, pill_h=pill_h)
        py += pill_h + 2
        
        remaining_lead_h = (y + 196) - py
        desc_font, desc_lines = get_fitted_lead_desc(story["desc"], col_w, remaining_lead_h, max_lines=5)
        for dl in desc_lines:
            draw.text((col_x, py), dl, fill=INK, font=desc_font)
            py += desc_font.size + 2.0
            
    y += 198
    draw.line([(32, y), (992, y)], fill=SLATE, width=1)
    y += 6
    
    # 4. TILES GRID (stories 4–13, 5 cols × 2 rows)
    tile_cols = 5
    tile_gutter = 10
    tile_width = (usable_width - tile_gutter * (tile_cols - 1)) / tile_cols
    tile_w = int(tile_width)
    
    tiles_data = stories.MAINS[3:13]
    tile_fit_report = []
    tile_row_h = 110
    
    for idx, story in enumerate(tiles_data):
        r_i = idx // tile_cols # 0 or 1
        c_i = idx % tile_cols # 0 to 4
        tx = left_margin + c_i * (tile_w + tile_gutter)
        ty = y + r_i * tile_row_h
        row_bottom = ty + tile_row_h
        
        # 1. Panel (26px tall)
        t_panel = [tx, ty, tx + tile_w, ty + 26]
        base_col = stories.REGION_COLOURS.get(story["region"], (84, 94, 106))
        bg_col = (int(base_col[0]*0.4 + 200*0.6), int(base_col[1]*0.4 + 200*0.6), int(base_col[2]*0.4 + 200*0.6))
        draw.rectangle(t_panel, fill=bg_col)
        
        draw_icon(draw, story["icon"], tx + tile_w/2, ty + 13, 16, colour=(255, 255, 255))
        
        circ_r = 7.0
        circ_cx = tx + 9
        circ_cy = ty + 9
        draw.ellipse([circ_cx - circ_r, circ_cy - circ_r, circ_cx + circ_r, circ_cy + circ_r], fill=(255, 255, 255))
        f_tnum = F(FONT_SANS_BOLD, 8)
        draw.text((circ_cx - 3, circ_cy - 4.5), str(story["n"]), fill=INK, font=f_tnum)
        
        # 2. Headline (bold 11.5px, <=2 lines)
        tpy = ty + 28
        f_thead = F(FONT_SANS_BOLD, 11.5)
        t_lines = wrap(story["headline"], f_thead, tile_w)
        for tl in t_lines[:2]:
            draw.text((tx, tpy), tl, fill=INK, font=f_thead)
            tpy += 13.5
            
        # 3. Pill (14px tall)
        tpy += 2
        pill_h = 14
        draw_banner_pill(draw, tx, tpy, story["region"], story["icon"], story["label"], font_size=8, box_w=12, pill_h=pill_h)
        tpy += pill_h + 2
        
        # 4. Desc (max 3 lines, start 9.5px down to 8.0px in 0.5px steps)
        desc_font, td_lines = get_fitted_tile_desc(story["desc"], tile_w, max_lines=3)
        tile_fit_report.append((story["n"], desc_font.size, len(td_lines)))
        for tdl in td_lines:
            draw.text((tx, tpy), tdl, fill=INK, font=desc_font)
            tpy += desc_font.size + 1.5
            
        assert tpy <= row_bottom, f"ASSERTION FAILED: Tile {story['n']} desc bottom {tpy} exceeds row bottom {row_bottom}"
            
    y += tile_row_h * 2
    draw.line([(32, y), (992, y)], fill=SLATE, width=1)
    y += 6
    
    # 5. DAY IN NUMBERS band (52px)
    draw.line([(32, y), (992, y)], fill=SLATE, width=1)
    y += 2
    band_y = y
    band_h = 52
    
    f_num_hdr = F(FONT_SANS_BOLD, 9)
    draw.text((32, band_y + 16), "THE DAY IN NUMBERS", fill=RED, font=f_num_hdr)
    
    stats_start_x = 180
    stats_width = 992 - stats_start_x
    col_w_stat = stats_width / 8
    
    f_sval = F(FONT_SERIF_BOLD, 18)
    f_scap = F(FONT_SANS, 8.5)
    
    for s_idx, (val_str, desc_str) in enumerate(stories.NUMBERS):
        sx = stats_start_x + s_idx * col_w_stat
        draw.text((sx, band_y + 2), val_str, fill=GOLD_DARK, font=f_sval)
        s_lines = wrap(desc_str, f_scap, col_w_stat - 4)
        sy = band_y + 23
        for sl in s_lines[:3]:
            draw.text((sx, sy), sl, fill=INK, font=f_scap)
            sy += 9.5
            
    y += band_h + 2
    draw.line([(32, y), (992, y)], fill=SLATE, width=1)
    y += 6
    
    # 6. BOTTOM ROW: map left (~350px), ALSO right (three columns, 7 rows)
    bottom_start_y = y
    footer_y = 984
    bottom_row_h = footer_y - 12 - bottom_start_y
    
    map_x = 32
    map_w = 340
    also_x = map_x + map_w + 16 # 388
    also_w = 992 - also_x # 604
    
    draw.text((map_x, bottom_start_y), "WHERE IT HAPPENED", fill=RED, font=f_num_hdr)
    draw.text((also_x, bottom_start_y), "ALSO ON SUNDAY 22 NOVEMBER", fill=RED, font=f_num_hdr)
    
    map_top_y = bottom_start_y + 16
    map_h = bottom_row_h - 16
    
    map_box = [map_x, map_top_y, map_x + map_w, map_top_y + map_h - 22]
    draw.rectangle(map_box, fill=(240, 234, 218), outline=SLATE, width=1)
    
    land_rows = ASCII_LAND
    rows_n = len(land_rows)
    cols_n = len(land_rows[0])
    cell_w = map_w / cols_n
    cell_h = (map_h - 22) / rows_n
    
    for r_idx, r_str in enumerate(land_rows):
        for c_idx, char in enumerate(r_str):
            if char == '#':
                px = map_x + c_idx * cell_w + cell_w/2
                py = map_top_y + r_idx * cell_h + cell_h/2
                draw.ellipse([px-1, py-1, px+1, py+1], fill=LAND_COLOUR)
                
    def lonlat_to_xy(lon, lat):
        nx = (lon + 180.0) / 360.0
        ny = (83.0 - lat) / (83.0 - (-58.0))
        return map_x + nx * map_w, map_top_y + ny * (map_h - 22)
        
    all_stories_map = stories.MAINS + stories.BRIEFS
    for s in all_stories_map:
        if "pin" in s:
            lon, lat = s["pin"]
            px, py = lonlat_to_xy(lon, lat)
            col = stories.REGION_COLOURS.get(s["region"], (84, 94, 106))
            if s["n"] <= 13:
                draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=col, outline=(255,255,255), width=1)
            else:
                draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=col)
                
    my = map_top_y + map_h - 20
    f_map_cap = F(FONT_SANS, 7.5)
    draw.text((map_x, my), "Pins: stories 1–13 · dots: 14–33 · pin 11: ESA Darmstadt", fill=SLATE, font=f_map_cap)
    my += 10
    
    regions_list = list(stories.REGION_COLOURS.keys())
    lx = map_x
    ly = my
    for idx, reg in enumerate(regions_list):
        col = stories.REGION_COLOURS[reg]
        draw.ellipse([lx, ly + 2, lx + 5, ly + 7], fill=col)
        draw.text((lx + 8, ly), reg, fill=INK, font=f_map_cap)
        w_approx = len(reg) * 4 + 10
        lx += w_approx + 4
        if lx > map_x + map_w - 20 and idx < len(regions_list) - 1:
            lx = map_x
            ly += 9
            
    # --- ALSO BLOCK (THREE columns, 7 rows, stories 14–33) ---
    also_briefs = stories.BRIEFS # 20 items (14 to 33)
    also_gutter_col = 14
    col_w_also = (also_w - also_gutter_col * 2) / 3.0
    
    also_header_h = 16
    also_available_h = bottom_row_h - also_header_h
    row_pitch = also_available_h / 7.0
    
    also_top_y = bottom_start_y + also_header_h
    also_fit_report = []
    
    for idx, story in enumerate(also_briefs):
        c_idx = idx // 7 # 0, 1, or 2 (7 items per column)
        r_idx = idx % 7 # 0 to 6
        if c_idx > 2:
            break
        column_x = also_x + c_idx * (col_w_also + also_gutter_col)
        ay = also_top_y + r_idx * row_pitch
        row_band_bottom = ay + row_pitch
        
        # 1. Marker line (14px tall) holding number circle and banner pill side by side
        circle_width = 14
        gap1 = 4
        circ_d = circle_width
        circ_r = circ_d / 2.0
        circ_cx = column_x + circ_r
        circ_cy = ay + 7
        
        col = stories.REGION_COLOURS.get(story["region"], (84, 94, 106))
        
        pill_x = column_x + circ_d + gap1
        label_text = story["label"]
        f_apill = F(FONT_SANS_BOLD, 8)
        try:
            lw = f_apill.getlength(label_text)
        except AttributeError:
            lw = len(label_text) * 5
        box_w = 11
        pill_w = box_w + 4 + lw + 6
        pill_h = 14
        pill_y = ay
        
        # Draw number circle
        draw.ellipse([circ_cx - circ_r, circ_cy - circ_r, circ_cx + circ_r, circ_cy + circ_r], fill=col)
        f_anum = F(FONT_SANS_BOLD, 8)
        draw.text((circ_cx - 3, circ_cy - 4.5), str(story["n"]), fill=(255, 255, 255), font=f_anum)
        
        # Draw banner pill
        draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=pill_h/2, fill=col)
        draw_icon(draw, story["icon"], pill_x + box_w/2, pill_y + pill_h/2, box_w - 4, colour=(255, 255, 255))
        draw.text((pill_x + box_w + 3, pill_y + (pill_h - 8)/2 - 1), label_text, fill=(255, 255, 255), font=f_apill)
        
        # 2. Below the marker line: paragraph (headline bold + " — " + desc regular) in full column width
        # First baseline starts below pill's bottom edge + 2px
        text_start_y = pill_y + pill_h + 2
        
        f_size, lines = get_fitted_also_item_3col(story["headline"], story["desc"], col_w_also, max_lines=3)
        also_fit_report.append((story["n"], f_size, len(lines)))
        
        fb = F(FONT_SANS_BOLD, f_size)
        fr = F(FONT_SANS, f_size)
        line_height = f_size + 1.5
        
        text_y = text_start_y
        for l_idx, line_tokens in enumerate(lines):
            curr_x = column_x
            curr_y = text_y + l_idx * line_height
            for token, is_bold in line_tokens:
                f_current = fb if is_bold else fr
                draw.text((curr_x, curr_y), token, fill=INK, font=f_current)
                try:
                    tw = f_current.getlength(token + " ")
                except AttributeError:
                    tw = len(token + " ") * 5.5
                curr_x += tw
                
        item_bottom = text_y + len(lines) * line_height
        assert item_bottom <= row_band_bottom + 4, f"ASSERTION FAILED: ALSO item {story['n']} bottom {item_bottom} exceeds row band bottom {row_band_bottom}"
        
    # Print Fit Reports to stdout
    print("=== TILE FIT REPORT (Stories 4–13) ===")
    for n, fsz, lcnt in tile_fit_report:
        print(f"Story {n:2d}: font size {fsz}px, lines {lcnt}")
        
    print("\n=== ALSO FIT REPORT (Stories 14–33) ===")
    for n, fsz, lcnt in also_fit_report:
        print(f"Story {n:2d}: font size {fsz}px, lines {lcnt}")
            
    # 7. FOOTER
    draw.line([(32, footer_y - 5), (992, footer_y - 5)], fill=SLATE, width=1)
    
    f_foot = None
    for f_sz in [9.0, 8.5, 8.0]:
        f_cand = F(FONT_SANS, f_sz)
        try:
            w = f_cand.getlength(stories.SOURCES)
        except AttributeError:
            w = len(stories.SOURCES) * 5
        if w <= 960:
            f_foot = f_cand
            break
    if f_foot is None:
        f_foot = F(FONT_SANS, 8.0)
        
    foot_w = f_foot.getlength(stories.SOURCES) if hasattr(f_foot, 'getlength') else len(stories.SOURCES)*5
    draw.text((1024/2 - foot_w/2, footer_y), stories.SOURCES, fill=SLATE, font=f_foot)
    
    final_cursor_y = footer_y + 14
    max_allowed_y = 1002
    if final_cursor_y > max_allowed_y:
        overflow = final_cursor_y - max_allowed_y
        print(f"ASSERTION FAILED: Final cursor y = {final_cursor_y} exceeds max allowed y = {max_allowed_y} by {overflow}px!")
        raise AssertionError(f"Layout overflow by {overflow}px")
        
    return img

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img = render()
    
    entry_path = os.path.join(base_dir, "entry.png")
    img.save(entry_path, "PNG", optimize=True)
    
    crop_also = (380, 710, 1010, 980)
    cropped_also = img.crop(crop_also)
    zoom_also = cropped_also.resize((cropped_also.width * 2, cropped_also.height * 2), Image.Resampling.NEAREST)
    zoom_also.save("/tmp/news22-also-zoom.png", "PNG")
    
    crop_tiles = (25, 350, 1000, 600)
    cropped_tiles = img.crop(crop_tiles)
    zoom_tiles = cropped_tiles.resize((cropped_tiles.width * 2, cropped_tiles.height * 2), Image.Resampling.NEAREST)
    zoom_tiles.save("/tmp/news22-tiles-zoom.png", "PNG")
    
    with open(entry_path, "rb") as f:
        data = f.read()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Invalid PNG signature")
        
    print(f"\nentry.png generated successfully. Size: {len(data)} bytes, Dimensions: {img.size}")
    print("Zoom crops saved to /tmp/news22-also-zoom.png and /tmp/news22-tiles-zoom.png")

if __name__ == "__main__":
    main()
