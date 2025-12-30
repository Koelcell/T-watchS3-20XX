import board

import displayio
import terminalio
import time
import rtc
import adafruit_focaltouch
import busio
import microcontroller
import gc
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.roundrect import RoundRect
import json
import storage

# 1. Initialize I2C
touch_i2c = busio.I2C(microcontroller.pin.GPIO40, microcontroller.pin.GPIO39)
sensor_i2c = busio.I2C(microcontroller.pin.GPIO11, microcontroller.pin.GPIO10)

def get_battery_percent():
    if sensor_i2c.try_lock():
        try:
            sensor_i2c.writeto(0x34, bytes([0xA4]))
            result = bytearray(1)
            sensor_i2c.readfrom_into(0x34, result)
            return max(0, min(100, result[0]))
        except: return 0
        finally: sensor_i2c.unlock()
    return 0

# 2. Setup Display
display = board.DISPLAY
root_group = displayio.Group()
display.root_group = root_group

bg_color = 0x05070A
bg_palette = displayio.Palette(1)
bg_palette[0] = bg_color
bg_bitmap = displayio.Bitmap(1, 1, 1)

ORANGE = 0xFF8C00
DARK_GREEN = 0x006400
GRAY = 0x808080

try:
    custom_font = bitmap_font.load_font("/fonts/scientificaBold-11.bdf")
except:
    custom_font = terminalio.FONT


main_group = displayio.Group()
root_group.append(main_group)
bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, width=240, height=240)
main_group.append(bg_sprite)

edge_outline = Rect(0, 0, 240, 240, fill=None, outline=DARK_GREEN, stroke=4)
main_group.append(edge_outline)



timer_page = displayio.Group()
timer_bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, width=240, height=240)
timer_page.append(timer_bg_sprite)
timer_outline = Rect(0, 0, 240, 240, fill=None, outline=0xFF0000, stroke=4)
timer_page.append(timer_outline)
timer_page.hidden = True
root_group.append(timer_page)

settings_page = displayio.Group()
settings_bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, width=240, height=240)
settings_page.append(settings_bg_sprite)
settings_outline = Rect(0, 0, 240, 240, fill=None, outline=DARK_GREEN, stroke=4)
settings_page.append(settings_outline)

# Settings UI - Arrow Controls
# Labels (Enlarged and using custom font)
text_label = label.Label(custom_font, text="TXT", color=0xFFFFFF, scale=3)
text_label.anchor_point, text_label.anchored_position = (0.5, 0.0), (50, 8)
outl_label = label.Label(custom_font, text="OUT", color=0xFFFFFF, scale=3)
outl_label.anchor_point, outl_label.anchored_position = (0.5, 0.0), (125, 8)
brgt_label = label.Label(custom_font, text="DIM", color=0xFFFFFF, scale=3)
brgt_label.anchor_point, brgt_label.anchored_position = (0.5, 0.0), (200, 8)
settings_page.append(text_label); settings_page.append(outl_label); settings_page.append(brgt_label)

# Up Arrows (Moved down by 10 to y=50, scale reduced to 3)
up_txt = label.Label(custom_font, text="^", color=ORANGE, scale=3, x=42, y=50)
up_out = label.Label(custom_font, text="^", color=ORANGE, scale=3, x=117, y=50)
up_brt = label.Label(custom_font, text="^", color=ORANGE, scale=3, x=192, y=50)
settings_page.append(up_txt); settings_page.append(up_out); settings_page.append(up_brt)

# Previews (Moved up to y=62)
text_color_preview = Rect(30, 62, 40, 40, fill=ORANGE, outline=DARK_GREEN, stroke=2)
outline_color_preview = Rect(105, 62, 40, 40, fill=DARK_GREEN, outline=DARK_GREEN, stroke=2)
bright_preview = Rect(180, 62, 40, 40, fill=0xFFFFFF, outline=DARK_GREEN, stroke=2)
settings_page.append(text_color_preview); settings_page.append(outline_color_preview); settings_page.append(bright_preview)

# Down Arrows (Moved up by 10 to y=115, scale reduced to 3)
dn_txt = label.Label(custom_font, text="v", color=ORANGE, scale=3, x=42, y=115)
dn_out = label.Label(custom_font, text="v", color=ORANGE, scale=3, x=117, y=115)
dn_brt = label.Label(custom_font, text="v", color=ORANGE, scale=3, x=192, y=115)
settings_page.append(dn_txt); settings_page.append(dn_out); settings_page.append(dn_brt)

# Return Area Indicator ([X] in bottom right, [SET] in bottom left)
return_label = label.Label(custom_font, text="[X]", color=ORANGE, scale=2, x=207, y=223)
settings_page.append(return_label)
set_btn = label.Label(custom_font, text="[SET]", color=ORANGE, scale=3, x=10, y=215)
settings_page.append(set_btn)

settings_page.hidden = True
root_group.append(settings_page)

calendar_page = displayio.Group()
calendar_bg = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, width=240, height=240)
calendar_page.append(calendar_bg)
calendar_outline = Rect(0, 0, 240, 240, fill=None, outline=DARK_GREEN, stroke=4)
calendar_page.append(calendar_outline)
calendar_title = label.Label(terminalio.FONT, text="CALENDAR", color=ORANGE, scale=2, x=70, y=20)
calendar_page.append(calendar_title)

# Calendar Grid Setup
days_header = ["M", "T", "W", "T", "F", "S", "S"]
for i, d in enumerate(days_header):
    l = label.Label(terminalio.FONT, text=d, color=GRAY, scale=1, x=25 + i*30, y=50)
    calendar_page.append(l)

cal_labels = []
for row in range(6):
    for col in range(7):
        idx = row * 7 + col
        l = label.Label(terminalio.FONT, text="", color=0xFFFFFF, scale=2, x=20 + col*30, y=85 + row*25)
        calendar_page.append(l)
        cal_labels.append(l)

cal_highlight = Rect(15, 75, 25, 22, fill=None, outline=ORANGE, stroke=1)
calendar_page.append(cal_highlight)
cal_highlight.hidden = True

# Calendar Return Icon [X]
cal_return_label = label.Label(custom_font, text="[X]", color=ORANGE, scale=2, x=207, y=223)
calendar_page.append(cal_return_label)

# Extra Page UI (3x3 Grid)
extra_page = displayio.Group()
extra_bg = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, width=240, height=240)
extra_page.append(extra_bg)
extra_grid_lines = []
for i in range(1, 3):
    v_line = Rect(i * 80 - 2, 0, 5, 240, fill=DARK_GREEN)
    h_line = Rect(0, i * 80 - 2, 240, 5, fill=DARK_GREEN)
    extra_page.append(v_line); extra_page.append(h_line)
    extra_grid_lines.extend([v_line, h_line])
extra_outline = Rect(0, 0, 240, 240, fill=None, outline=DARK_GREEN, stroke=5)
extra_page.append(extra_outline)
extra_return_label = label.Label(custom_font, text="[X]", color=ORANGE, scale=2, x=207, y=223)
extra_page.append(extra_return_label)
extra_calc_btn = label.Label(custom_font, text="[CALC]", color=ORANGE, scale=2, x=10, y=35)
extra_page.append(extra_calc_btn)
extra_dice_btn = label.Label(custom_font, text="[DICE]", color=ORANGE, scale=2, x=90, y=35)
extra_page.append(extra_dice_btn)
extra_8ball_btn = label.Label(custom_font, text="[8B]", color=ORANGE, scale=2, x=170, y=35)
extra_page.append(extra_8ball_btn)
extra_page.hidden = True
root_group.append(extra_page)

# Magic 8-Ball Page UI
eight_ball_page = displayio.Group()
ball_bg = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, width=240, height=240)
eight_ball_page.append(ball_bg)
ball_outline = Rect(0, 0, 240, 240, fill=None, outline=DARK_GREEN, stroke=4)
eight_ball_page.append(ball_outline)

# The Ball
ball_circle = Circle(120, 110, 80, fill=0x000000, outline=DARK_GREEN)
eight_ball_page.append(ball_circle)
ball_8 = label.Label(custom_font, text="8", color=0xFFFFFF, scale=5, x=105, y=100)
eight_ball_page.append(ball_8)

ball_msg = label.Label(terminalio.FONT, text="TAP ME", color=ORANGE, scale=2, x=75, y=210)
eight_ball_page.append(ball_msg)

ball_return_label = label.Label(custom_font, text="[X]", color=ORANGE, scale=2, x=207, y=223)
eight_ball_page.append(ball_return_label)
eight_ball_page.hidden = True
root_group.append(eight_ball_page)

# Dice Roller Page UI
dice_page = displayio.Group()
dice_bg = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, width=240, height=240)
dice_page.append(dice_bg)
dice_outline = Rect(0, 0, 240, 240, fill=None, outline=DARK_GREEN, stroke=4)
dice_page.append(dice_outline)

# Helper to Creating Visual Dice
def create_die(x, y):
    g = displayio.Group(x=x, y=y)
    face = RoundRect(0, 0, 70, 70, 10, fill=None, outline=DARK_GREEN, stroke=2)
    g.append(face)
    pips = []
    # 7 pips needed for 1-6 layouts: TL, TR, ML, C, MR, BL, BR
    pos = [(15,15),(55,15),(15,35),(35,35),(55,35),(15,55),(55,55)]
    for px, py in pos:
        p = Circle(px, py, 6, fill=ORANGE)
        p.hidden = True
        g.append(p); pips.append(p)
    return g, face, pips

def set_die_value(pips, val):
    for p in pips: p.hidden = True
    layouts = {
        1: [3],
        2: [0, 6],
        3: [0, 3, 6],
        4: [0, 1, 5, 6],
        5: [0, 1, 3, 5, 6],
        6: [0, 1, 2, 4, 5, 6]
    }
    for idx in layouts.get(val, []): pips[idx].hidden = False

die1_group, die1_face, die1_pips = create_die(40, 75)
die2_group, die2_face, die2_pips = create_die(130, 75)
dice_page.append(die1_group); dice_page.append(die2_group)

roll_btn = label.Label(custom_font, text="[ROLL]", color=ORANGE, scale=3, x=72, y=180)
dice_page.append(roll_btn)

d_return_label = label.Label(custom_font, text="[X]", color=ORANGE, scale=2, x=207, y=223)
dice_page.append(d_return_label)
dice_page.hidden = True
root_group.append(dice_page)

# Calculator Page UI
calc_page = displayio.Group()
calc_bg = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, width=240, height=240)
calc_page.append(calc_bg)
calc_outline = Rect(0, 0, 240, 240, fill=None, outline=DARK_GREEN, stroke=4)
calc_page.append(calc_outline)

calc_display = label.Label(custom_font, text="0", color=0xFFFFFF, scale=3)
calc_display.anchor_point, calc_display.anchored_position = (1.0, 0.0), (230, 10)
calc_page.append(calc_display)

# Calculator Keys (Grid 4x4)
calc_keys = ["7", "8", "9", "/", "4", "5", "6", "*", "1", "2", "3", "-", "0", "C", "=", "+"]
calc_labels = []
for i, key in enumerate(calc_keys):
    row, col = i // 4, i % 4
    l = label.Label(custom_font, text=key, color=ORANGE, scale=3, x=20 + col * 55, y=80 + row * 45)
    calc_page.append(l); calc_labels.append(l)

c_return_label = label.Label(custom_font, text="[X]", color=ORANGE, scale=2, x=207, y=223)
calc_page.append(c_return_label)
calc_page.hidden = True
root_group.append(calc_page)

# Calendar Month Navigation Arrows
cal_prev_month = label.Label(custom_font, text="<", color=ORANGE, scale=2, x=35, y=20)
cal_next_month = label.Label(custom_font, text=">", color=ORANGE, scale=2, x=190, y=20)
cal_prev_box = Rect(25, 10, 40, 25, fill=None, outline=DARK_GREEN, stroke=1)
cal_next_box = Rect(175, 10, 40, 25, fill=None, outline=DARK_GREEN, stroke=1)
calendar_page.append(cal_prev_month); calendar_page.append(cal_next_month)
calendar_page.append(cal_prev_box); calendar_page.append(cal_next_box)

set_page = displayio.Group()
set_bg = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette, width=240, height=240)
set_page.append(set_bg)
set_outline = Rect(0, 0, 240, 240, fill=None, outline=DARK_GREEN, stroke=4)
set_page.append(set_outline)

# Date/Time Set UI - Reordered: HR MI DA MO YEAR
set_h_label = label.Label(custom_font, text="00", color=0xFFFFFF, scale=2, x=10, y=80)
set_mi_label = label.Label(custom_font, text="00", color=0xFFFFFF, scale=2, x=55, y=80)
set_d_label = label.Label(custom_font, text="01", color=0xFFFFFF, scale=2, x=100, y=80)
set_mo_label = label.Label(custom_font, text="01", color=0xFFFFFF, scale=2, x=145, y=80)
set_y_label = label.Label(custom_font, text="2025", color=0xFFFFFF, scale=2, x=185, y=80)
set_page.append(set_h_label); set_page.append(set_mi_label); set_page.append(set_d_label); set_page.append(set_mo_label); set_page.append(set_y_label)

# Headers
set_h1 = label.Label(terminalio.FONT, text="HR", color=GRAY, x=10, y=20)
set_h2 = label.Label(terminalio.FONT, text="MI", color=GRAY, x=55, y=20)
set_h3 = label.Label(terminalio.FONT, text="DA", color=GRAY, x=100, y=20)
set_h4 = label.Label(terminalio.FONT, text="MO", color=GRAY, x=145, y=20)
set_h5 = label.Label(terminalio.FONT, text="YEAR", color=GRAY, x=185, y=20)
set_page.append(set_h1); set_page.append(set_h2); set_page.append(set_h3); set_page.append(set_h4); set_page.append(set_h5)

# Arrows
set_up_h = label.Label(custom_font, text="^", color=ORANGE, scale=2, x=10, y=50)
set_up_mi = label.Label(custom_font, text="^", color=ORANGE, scale=2, x=55, y=50)
set_up_d = label.Label(custom_font, text="^", color=ORANGE, scale=2, x=100, y=50)
set_up_mo = label.Label(custom_font, text="^", color=ORANGE, scale=2, x=145, y=50)
set_up_y = label.Label(custom_font, text="^", color=ORANGE, scale=2, x=195, y=50)
set_page.append(set_up_h); set_page.append(set_up_mi); set_page.append(set_up_d); set_page.append(set_up_mo); set_page.append(set_up_y)

set_dn_h = label.Label(custom_font, text="v", color=ORANGE, scale=2, x=10, y=110)
set_dn_mi = label.Label(custom_font, text="v", color=ORANGE, scale=2, x=55, y=110)
set_dn_d = label.Label(custom_font, text="v", color=ORANGE, scale=2, x=100, y=110)
set_dn_mo = label.Label(custom_font, text="v", color=ORANGE, scale=2, x=145, y=110)
set_dn_y = label.Label(custom_font, text="v", color=ORANGE, scale=2, x=195, y=110)
set_page.append(set_dn_h); set_page.append(set_dn_mi); set_page.append(set_dn_d); set_page.append(set_dn_mo); set_page.append(set_dn_y)

save_btn = label.Label(custom_font, text="[SAVE]", color=ORANGE, scale=3, x=65, y=180)
set_page.append(save_btn)
set_return_label = label.Label(custom_font, text="[X]", color=ORANGE, scale=2, x=207, y=223)
set_page.append(set_return_label)

set_page.hidden = True
root_group.append(set_page)

calendar_page.hidden = True
root_group.append(calendar_page)




def create_double_outline_label(text, x, y, scale, main_color, anchor=(0.5, 0.5), has_green=True, has_black=True):
    group = displayio.Group()
    layers = []
    if has_green:
        green_offs = [(-12,0),(12,0),(0,-12),(0,12),(-12,-12),(12,12),(-12,12),(12,-12)]
        for ox, oy in green_offs:
            l = label.Label(custom_font, text=text, color=DARK_GREEN, scale=scale)
            l.anchor_point, l.anchored_position = anchor, (x + ox, y + oy)
            group.append(l); layers.append(l)
    if has_black:
        black_offs = [(-8,0),(8,0),(0,-8),(0,8),(-8,-8),(8,8),(-8,8),(8,-8)]
        for ox, oy in black_offs:
            l = label.Label(custom_font, text=text, color=0x000000, scale=scale)
            l.anchor_point, l.anchored_position = anchor, (x + ox, y + oy)
            group.append(l); layers.append(l)
    main_l = label.Label(custom_font, text=text, color=main_color, scale=scale)
    main_l.anchor_point, main_l.anchored_position = anchor, (x, y)
    group.append(main_l)
    return group, main_l, layers

def update_all_colors():
    # Update main clock labels
    h_main.color = current_text_color
    m_main.color = current_text_color
    s_main.color = current_text_color
    c_main.color = current_text_color
    for l in h_layers[:8]: l.color = current_outline_color
    for l in m_layers[:8]: l.color = current_outline_color
    for l in c_layers[:8]: l.color = current_outline_color
    # Update timer labels
    t_m_label.color = current_text_color
    t_s_label.color = current_text_color
    t_c_main.color = current_text_color
    for l in t_m_layers[:8]: l.color = current_outline_color
    for l in t_s_layers[:8]: l.color = current_outline_color
    for l in t_c_layers[:8]: l.color = current_outline_color
    # Update date labels
    date_label.color = current_text_color
    date_num_label.color = current_text_color
    # Update outlines
    edge_outline.outline = current_outline_color
    sec_rect.outline = current_outline_color
    # Update battery
    batt_outline.outline = current_text_color
    batt_tip.fill = current_text_color
    # Update settings UI
    settings_outline.outline = current_outline_color
    text_color_preview.outline = current_outline_color
    outline_color_preview.outline = current_outline_color
    bright_preview.outline = current_outline_color
    up_txt.color = current_text_color
    up_out.color = current_text_color
    up_brt.color = current_text_color
    dn_txt.color = current_text_color
    dn_out.color = current_text_color
    dn_brt.color = current_text_color
    # Update timer arrows
    up_m.color = current_text_color
    dn_m.color = current_text_color
    up_s.color = current_text_color
    dn_s.color = current_text_color
    # Update timer boxes
    up_m_box.outline = current_outline_color
    dn_m_box.outline = current_outline_color
    up_s_box.outline = current_outline_color
    dn_s_box.outline = current_outline_color
    # Update settings and timer return area
    return_label.color = current_text_color
    t_return_label.color = current_text_color
    cal_return_label.color = current_text_color
    set_btn.color = current_text_color
    # Update timer mode buttons
    t_plus_btn.color = current_text_color
    t_minus_btn.color = current_text_color
    t_reset_btn.color = current_text_color
    t_plus_box.outline = current_outline_color
    t_minus_box.outline = current_outline_color
    t_reset_box.outline = current_outline_color
    # Update set page
    set_outline.outline = current_outline_color
    set_y_label.color = current_text_color
    set_mo_label.color = current_text_color
    set_d_label.color = current_text_color
    set_h_label.color = current_text_color
    set_mi_label.color = current_text_color
    save_btn.color = current_text_color
    set_return_label.color = current_text_color
    for arrow in [set_up_y, set_up_mo, set_up_d, set_up_h, set_up_mi, set_dn_y, set_dn_mo, set_dn_d, set_dn_h, set_dn_mi]:
        arrow.color = current_text_color
    # Update calendar
    calendar_outline.outline = current_outline_color
    calendar_title.color = current_text_color
    cal_highlight.outline = current_text_color
    cal_prev_month.color = current_text_color
    cal_next_month.color = current_text_color
    cal_prev_box.outline = current_outline_color
    cal_next_box.outline = current_outline_color
    # Update extra page
    extra_outline.outline = current_outline_color
    extra_return_label.color = current_text_color
    extra_calc_btn.color = current_text_color
    for line in extra_grid_lines: line.fill = current_outline_color
    # Update calc page
    calc_outline.outline = current_outline_color
    calc_display.color = current_text_color
    c_return_label.color = current_text_color
    for l in calc_labels: l.color = current_text_color
    # Update dice page
    dice_outline.outline = current_outline_color
    die1_face.outline = current_outline_color
    die2_face.outline = current_outline_color
    for p in die1_pips + die2_pips: p.fill = current_text_color
    roll_btn.color = current_text_color
    d_return_label.color = current_text_color
    extra_dice_btn.color = current_text_color
    # Update 8-ball page
    ball_outline.outline = current_outline_color
    ball_circle.outline = current_outline_color
    ball_msg.color = current_text_color
    ball_return_label.color = current_text_color
    extra_8ball_btn.color = current_text_color

# Main Clock UI
h_group, h_main, h_layers = create_double_outline_label("00", 60, 88, 9, ORANGE)
c_group, c_main, c_layers = create_double_outline_label(":", 129, 88, 9, ORANGE)
m_group, m_main, m_layers = create_double_outline_label("00", 189, 88, 9, ORANGE)

# Seconds Container - Left side 2px closer to center (x=89), width reduced (w=64) to keep right edge fixed
sec_bg_x, sec_bg_y, sec_bg_w, sec_bg_h = 89, 138, 64, 48
sec_rect = Rect(sec_bg_x, sec_bg_y, sec_bg_w, sec_bg_h, fill=0x000000, outline=DARK_GREEN, stroke=4)
s_group, s_main, s_layers = create_double_outline_label("00", 123, 162, 6, ORANGE, has_green=False, has_black=False)

main_group.append(h_group); main_group.append(c_group); main_group.append(m_group)
main_group.append(sec_rect); main_group.append(s_group)



# Timer Page UI
t_m_group, t_m_label, t_m_layers = create_double_outline_label("00", 60, 88, 9, ORANGE)
t_c_group, t_c_main, t_c_layers = create_double_outline_label(":", 129, 88, 9, ORANGE)
t_s_group, t_s_label, t_s_layers = create_double_outline_label("00", 189, 88, 9, ORANGE)
timer_page.append(t_m_group); timer_page.append(t_c_group); timer_page.append(t_s_group)

up_m = label.Label(custom_font, text="^", color=ORANGE, scale=3, x=52, y=29)
dn_m = label.Label(custom_font, text="v", color=ORANGE, scale=3, x=52, y=142)
up_s = label.Label(custom_font, text="^", color=ORANGE, scale=3, x=172, y=29)
dn_s = label.Label(custom_font, text="v", color=ORANGE, scale=3, x=172, y=142)
timer_page.append(up_m); timer_page.append(dn_m); timer_page.append(up_s); timer_page.append(dn_s)

# Timer Arrow Outlines
up_m_box = Rect(0, 4, 120, 40, fill=None, outline=DARK_GREEN, stroke=1)
dn_m_box = Rect(0, 132, 120, 40, fill=None, outline=DARK_GREEN, stroke=1)
up_s_box = Rect(120, 4, 120, 40, fill=None, outline=DARK_GREEN, stroke=1)
dn_s_box = Rect(120, 132, 120, 40, fill=None, outline=DARK_GREEN, stroke=1)
timer_page.append(up_m_box); timer_page.append(dn_m_box); timer_page.append(up_s_box); timer_page.append(dn_s_box)

# Timer Mode Buttons (+, -, R) - MASSIVE (63x63) touching
t_minus_box = Rect(5, 172, 63, 63, fill=None, outline=DARK_GREEN, stroke=1)
t_minus_btn = label.Label(custom_font, text="-", color=ORANGE, scale=3, x=36, y=203)
t_plus_box = Rect(68, 172, 63, 63, fill=None, outline=DARK_GREEN, stroke=1)
t_plus_btn = label.Label(custom_font, text="+", color=ORANGE, scale=3, x=99, y=203)
t_reset_box = Rect(131, 172, 63, 63, fill=None, outline=DARK_GREEN, stroke=1)
t_reset_btn = label.Label(custom_font, text="R", color=ORANGE, scale=3, x=162, y=203)
timer_page.append(t_minus_box); timer_page.append(t_minus_btn)
timer_page.append(t_plus_box); timer_page.append(t_plus_btn)
timer_page.append(t_reset_box); timer_page.append(t_reset_btn)

# Timer Return Icon [X]
t_return_label = label.Label(custom_font, text="[X]", color=ORANGE, scale=2, x=207, y=223)
timer_page.append(t_return_label)

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
date_label = label.Label(custom_font, text="", color=ORANGE, scale=3)
date_label.anchor_point, date_label.anchored_position = (0.0, 1.0), (8, 231)
main_group.append(date_label)

date_num_label = label.Label(custom_font, text="", color=ORANGE, scale=3)
date_num_label.anchor_point, date_num_label.anchored_position = (0.5, 1.0), (120, 233)
main_group.append(date_num_label)



bar_w, bar_h, bar_x, bar_y = 12, 30, 221, 202
batt_group = displayio.Group()
batt_outline = Rect(bar_x, bar_y, bar_w, bar_h, fill=None, outline=ORANGE, stroke=1)
batt_tip = Rect(bar_x + 3, bar_y - 2, 6, 2, fill=ORANGE)
batt_fill = Rect(bar_x + 2, bar_y + bar_h - 3, bar_w - 4, 1, fill=ORANGE)
batt_group.append(batt_outline); batt_group.append(batt_tip); batt_group.append(batt_fill)
main_group.append(batt_group)

r = rtc.RTC()
try: ft = adafruit_focaltouch.Adafruit_FocalTouch(touch_i2c, address=0x38)
except: ft = None

current_page = "clock"; display.brightness = 0.25
last_interaction = time.monotonic(); TIMEOUT = 5.0
touch_debounced = False; last_batt_check = -60; last_day = -1
timer_min, timer_sec = 0, 0; timer_running = False; last_timer_tick = 0
timer_direction = -1  # -1 for countdown, 1 for count-up
set_val = [2025, 1, 1, 0, 0] # Y, M, D, H, M
cal_view_year, cal_view_month = 2025, 1
calc_input = "0"; calc_op = ""; calc_total = 0; calc_new_num = True
eight_ball_answers = ["YES", "NO", "MAYBE", "ASK AGAIN", "SOON", "NEVER", "NOPE", "SURE"]

# Color settings
current_text_color = ORANGE
current_outline_color = DARK_GREEN
color_palette = [0xFF0000, 0xFF4500, 0xFF8C00, 0xFFD700, 0xFFFF00, 0x006400, 0x00FFFF, 0x0000FF, 0x8B00FF, 0xFF00FF, 0xFF1493, 0xFFFFFF]
text_color_index = 2  # Start at orange
outline_color_index = 5  # Start at green-ish
current_brightness = 0.25

def load_settings():
    global current_text_color, current_outline_color, text_color_index, outline_color_index, current_brightness
    try:
        with open("/settings.json", "r") as f:
            s = json.load(f)
            text_color_index = s.get("text_index", 2)
            outline_color_index = s.get("outline_index", 5)
            current_brightness = s.get("brightness", 0.25)
            current_text_color = color_palette[text_color_index]
            current_outline_color = color_palette[outline_color_index]
            display.brightness = current_brightness
            # Update visuals
            b_val = int(current_brightness * 255)
            bright_preview.fill = (b_val << 16) | (b_val << 8) | b_val
            text_color_preview.fill = current_text_color
            outline_color_preview.fill = current_outline_color
    except: pass

def save_settings():
    try:
        with open("/settings.json", "w") as f:
            json.dump({"text_index": text_color_index, "outline_index": outline_color_index, "brightness": current_brightness}, f)
    except: pass

load_settings()
update_all_colors()

dragging_text_slider = False
dragging_outline_slider = False
dragging_bright_slider = False

def update_calendar():
    global cal_view_year, cal_view_month
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    calendar_title.text = "{} {:04d}".format(months[cal_view_month-1], cal_view_year)
    
    # Accurate first day of month weekday calculation
    # tm_wday: 0 is Monday
    t_struct = (cal_view_year, cal_view_month, 1, 0, 0, 0, -1, -1, -1)
    first_day_dt = time.localtime(time.mktime(t_struct))
    first_day_wday = first_day_dt.tm_wday
    
    days_in_month = 31
    if cal_view_month in [4, 6, 9, 11]: days_in_month = 30
    elif cal_view_month == 2:
        days_in_month = 29 if (cal_view_year % 4 == 0 and (cal_view_year % 100 != 0 or cal_view_year % 400 == 0)) else 28
        
    curr = time.localtime()
    cal_highlight.hidden = True
    for i in range(42):
        day_num = i - first_day_wday + 1
        if 1 <= day_num <= days_in_month:
            cal_labels[i].text = str(day_num)
            if day_num == curr.tm_mday and cal_view_month == curr.tm_mon and cal_view_year == curr.tm_year:
                cal_highlight.x = 18 + (i % 7) * 30
                cal_highlight.y = 75 + (i // 7) * 25
                cal_highlight.hidden = False
        else:
            cal_labels[i].text = ""

gc.collect()

while True:
    now = time.monotonic()
    points = ft.touches if ft else []
    if points:
        if not touch_debounced:
            p = points[0]; tx, ty = p['x'], p['y']
            if display.brightness < 0.1:
                display.brightness = current_brightness; last_interaction = now
            else:
                if current_page == "clock" and ty < 50:
                    main_group.hidden, timer_page.hidden, settings_page.hidden, calendar_page.hidden, extra_page.hidden = True, True, True, True, False
                    current_page = "extra"; last_interaction = now
                elif current_page == "clock" and 57 < ty < 119:
                    main_group.hidden, timer_page.hidden, settings_page.hidden, calendar_page.hidden = True, False, True, True
                    current_page = "timer"; last_interaction = now
                elif current_page == "clock" and (100 < tx < 140 and ty >= 119 and ty <= 200):
                    display.brightness = 0.0; current_page = "clock"
                    main_group.hidden, timer_page.hidden, settings_page.hidden = False, True, True
                elif current_page == "clock" and tx > 120 and ty > 200:
                    main_group.hidden, timer_page.hidden, settings_page.hidden, calendar_page.hidden = True, True, False, True
                    current_page = "settings"; last_interaction = now
                elif current_page == "clock" and tx < 80 and ty > 200:
                    curr_t = time.localtime()
                    cal_view_year, cal_view_month = curr_t.tm_year, curr_t.tm_mon
                    update_calendar()
                    main_group.hidden, timer_page.hidden, settings_page.hidden, calendar_page.hidden = True, True, True, False
                    current_page = "calendar"; last_interaction = now
                elif current_page == "extra":
                    last_interaction = now
                    if tx > 180 and ty > 180: # Return area [X]
                        current_page = "clock"
                        main_group.hidden, extra_page.hidden = False, True
                    elif tx < 80 and ty < 80: # CALC button
                        current_page = "calc"
                        extra_page.hidden, calc_page.hidden = True, False
                    elif 80 < tx < 160 and ty < 80: # DICE button
                        current_page = "dice"
                        extra_page.hidden, dice_page.hidden = True, False
                    elif 160 < tx and ty < 80: # 8BALL button
                        current_page = "8ball"
                        extra_page.hidden, eight_ball_page.hidden = True, False
                elif current_page == "8ball":
                    last_interaction = now
                    if tx > 180 and ty > 180: # Return area [X]
                        current_page = "clock"
                        main_group.hidden, timer_page.hidden, settings_page.hidden, calendar_page.hidden, extra_page.hidden, calc_page.hidden, dice_page.hidden, eight_ball_page.hidden = False, True, True, True, True, True, True, True
                    elif 40 < tx < 200 and 30 < ty < 190: # Tap Ball
                        import random
                        ball_8.hidden = True
                        for _ in range(6):
                            ball_msg.text = "THINKING"
                            display.refresh(); time.sleep(0.1)
                            ball_msg.text = ""
                            display.refresh(); time.sleep(0.1)
                        ball_msg.text = random.choice(eight_ball_answers)
                        ball_msg.x = 120 - (len(ball_msg.text) * 6)
                        ball_8.hidden = False
                elif current_page == "dice":
                    last_interaction = now
                    if tx > 180 and ty > 180: # Return area [X]
                        current_page = "clock"
                        main_group.hidden, timer_page.hidden, settings_page.hidden, calendar_page.hidden, extra_page.hidden, calc_page.hidden, dice_page.hidden, eight_ball_page.hidden = False, True, True, True, True, True, True, True
                    elif 50 < tx < 190 and 150 < ty < 220: # ROLL
                        import random
                        for _ in range(5): # Shake animation
                            set_die_value(die1_pips, random.randint(1, 6))
                            set_die_value(die2_pips, random.randint(1, 6))
                            display.refresh()
                            time.sleep(0.05)
                elif current_page == "calc":
                    last_interaction = now
                    if tx > 180 and ty > 180: # Return area [X]
                        current_page = "clock"
                        main_group.hidden, timer_page.hidden, settings_page.hidden, calendar_page.hidden, extra_page.hidden, calc_page.hidden, dice_page.hidden, eight_ball_page.hidden = False, True, True, True, True, True, True, True
                    elif ty > 50:
                        col, row = (tx - 10) // 55, (ty - 55) // 45
                        col = max(0, min(3, col)); row = max(0, min(3, row))
                        key = calc_keys[row * 4 + col]
                        if key.isdigit():
                            if calc_new_num: calc_input = key; calc_new_num = False
                            else: calc_input += key
                        elif key == "C": calc_input = "0"; calc_total = 0; calc_op = ""; calc_new_num = True
                        elif key == "=":
                            try:
                                if calc_op == "+": calc_total += float(calc_input)
                                elif calc_op == "-": calc_total -= float(calc_input)
                                elif calc_op == "*": calc_total *= float(calc_input)
                                elif calc_op == "/": calc_total /= float(calc_input)
                                else: calc_total = float(calc_input)
                                calc_input = str(int(calc_total)) if calc_total == int(calc_total) else "{:.2f}".format(calc_total)
                                calc_op = ""; calc_new_num = True
                            except: calc_input = "Error"; calc_new_num = True
                        else: # Operators
                            try:
                                if calc_op == "+": calc_total += float(calc_input)
                                elif calc_op == "-": calc_total -= float(calc_input)
                                elif calc_op == "*": calc_total *= float(calc_input)
                                elif calc_op == "/": calc_total /= float(calc_input)
                                else: calc_total = float(calc_input)
                                calc_op = key; calc_new_num = True
                                calc_input = str(int(calc_total)) if calc_total == int(calc_total) else "{:.2f}".format(calc_total)
                            except: calc_input = "Error"; calc_new_num = True
                        calc_display.text = calc_input[:12] # Limit display
                elif current_page == "timer":
                    last_interaction = now
                    if tx > 180 and ty > 180: # Return area [X]
                        current_page = "clock"
                        main_group.hidden, timer_page.hidden, settings_page.hidden = False, True, True
                    elif ty > 172: # Mode/Reset buttons row (Massive buttons)
                        if tx < 68: # Minus (Countdown)
                            timer_direction = -1
                        elif tx < 131: # Plus (Count-up)
                            timer_direction = 1
                        elif tx < 194: # Reset
                            timer_running = False
                            timer_min, timer_sec = 0, 0
                    elif 40 < ty < 136:
                        timer_running = not timer_running; last_timer_tick = now
                    elif not timer_running:
                        if tx < 120:
                            if ty < 22: timer_min = (timer_min + 1) % 60
                            elif ty >= 140: timer_min = (timer_min - 1) % 60
                        else:
                            if ty < 22: timer_sec = (timer_sec + 1) % 60
                            elif ty >= 140: timer_sec = (timer_sec - 1) % 60
                    m_str, s_str = "{:02d}".format(timer_min), "{:02d}".format(timer_sec)
                    t_m_label.text, t_s_label.text = m_str, s_str
                    for l in t_m_layers: l.text = m_str
                    for l in t_s_layers: l.text = s_str
                elif current_page == "settings":
                    last_interaction = now
                    if tx > 180 and ty > 180: # Return area [X]
                        current_page = "clock"
                        main_group.hidden, timer_page.hidden, settings_page.hidden, calendar_page.hidden = False, True, True, True
                    elif tx < 80 and ty > 180: # SET button
                        curr = r.datetime
                        set_val = [curr.tm_year, curr.tm_mon, curr.tm_mday, curr.tm_hour, curr.tm_min]
                        set_y_label.text = str(set_val[0])
                        set_mo_label.text = "{:02d}".format(set_val[1])
                        set_d_label.text = "{:02d}".format(set_val[2])
                        set_h_label.text = "{:02d}".format(set_val[3])
                        set_mi_label.text = "{:02d}".format(set_val[4])
                        settings_page.hidden, set_page.hidden = True, False
                        current_page = "set"
                    else:
                        if tx < 80: # Text Color
                            if ty < 85: text_color_index = (text_color_index + 1) % len(color_palette)
                            elif ty < 170: text_color_index = (text_color_index - 1) % len(color_palette)
                            current_text_color = color_palette[text_color_index]
                            text_color_preview.fill = current_text_color
                        elif tx < 160: # Outline Color
                            if ty < 85: outline_color_index = (outline_color_index + 1) % len(color_palette)
                            elif ty < 170: outline_color_index = (outline_color_index - 1) % len(color_palette)
                            current_outline_color = color_palette[outline_color_index]
                            outline_color_preview.fill = current_outline_color
                        else: # Brightness
                            if ty < 85: current_brightness = min(1.0, current_brightness + 0.25)
                            elif ty < 170: current_brightness = max(0.25, current_brightness - 0.25)
                            display.brightness = current_brightness
                            b_val = int(current_brightness * 255)
                            bright_preview.fill = (b_val << 16) | (b_val << 8) | b_val
                        update_all_colors(); save_settings()
                elif current_page == "set":
                    last_interaction = now
                    if tx > 180 and ty > 180: # Return area [X]
                        current_page = "settings"
                        settings_page.hidden, set_page.hidden = False, True
                    elif 60 < tx < 180 and 160 < ty < 220: # SAVE
                        r.datetime = time.struct_time((set_val[0], set_val[1], set_val[2], set_val[3], set_val[4], 0, -1, -1, -1))
                        current_page = "settings"
                        settings_page.hidden, set_page.hidden = False, True
                    else:
                        col = 0
                        if tx < 50: col = 3 # Hour
                        elif tx < 95: col = 4 # Minute
                        elif tx < 140: col = 2 # Day
                        elif tx < 185: col = 1 # Month
                        else: col = 0 # Year
                        
                        inc = 1 if ty < 80 else -1
                        if col == 3: set_val[3] = (set_val[3] + inc) % 24
                        elif col == 4: set_val[4] = (set_val[4] + inc) % 60
                        elif col == 2: set_val[2] = max(1, min(31, set_val[2] + inc))
                        elif col == 1: set_val[1] = max(1, min(12, set_val[1] + inc))
                        elif col == 0: set_val[0] += inc
                        
                        set_y_label.text = str(set_val[0])
                        set_mo_label.text = "{:02d}".format(set_val[1])
                        set_d_label.text = "{:02d}".format(set_val[2])
                        set_h_label.text = "{:02d}".format(set_val[3])
                        set_mi_label.text = "{:02d}".format(set_val[4])
                elif current_page == "calendar":
                    last_interaction = now
                    if tx > 180 and ty > 180: # Return area [X]
                        current_page = "clock"
                        main_group.hidden, timer_page.hidden, settings_page.hidden, calendar_page.hidden = False, True, True, True
                    elif ty < 45: # Header Area (Navigation)
                        if tx < 80: # Prev Month
                            cal_view_month -= 1
                            if cal_view_month < 1:
                                cal_view_month = 12
                                cal_view_year -= 1
                            update_calendar()
                        elif tx > 160: # Next Month
                            cal_view_month += 1
                            if cal_view_month > 12:
                                cal_view_month = 1
                                cal_view_year += 1
                            update_calendar()
            touch_debounced = True
    else: touch_debounced = False

    if timer_running and now - last_timer_tick >= 1.0:
        if timer_direction == -1: # Count down
            if timer_min == 0 and timer_sec == 0: timer_running = False
            else:
                if timer_sec == 0: timer_min -= 1; timer_sec = 59
                else: timer_sec -= 1
        else: # Count up
            timer_sec += 1
            if timer_sec == 60: timer_sec = 0; timer_min = (timer_min + 1) % 100
            m_str, s_str = "{:02d}".format(timer_min), "{:02d}".format(timer_sec)
            t_m_label.text, t_s_label.text = m_str, s_str
            for l in t_m_layers: l.text = m_str
            for l in t_s_layers: l.text = s_str
        last_timer_tick = now

    if now - last_interaction > TIMEOUT and display.brightness > 0 and not timer_running:
        display.brightness = 0.0; gc.collect()

    if display.brightness > 0:
        if current_page == "clock":
            t = time.localtime()
            h_str, m_str, s_str = "{:02d}".format(t.tm_hour), "{:02d}".format(t.tm_min), "{:02d}".format(t.tm_sec)
            if s_main.text != s_str:
                h_main.text, m_main.text, s_main.text = h_str, m_str, s_str
                for l in h_layers: l.text = h_str
                for l in m_layers: l.text = m_str
                for l in s_layers: l.text = s_str
            if t.tm_mday != last_day:
                date_label.text = "{}".format(days[t.tm_wday][:3])
                date_num_label.text = "{:02d}/{:02d}".format(t.tm_mday, t.tm_mon)
                last_day = t.tm_mday
            if now - last_batt_check > 30:
                level = get_battery_percent()
                new_fill_h = max(1, int((level / 100) * (bar_h - 4)))
                batt_group.remove(batt_fill)
                batt_fill = Rect(bar_x+2, bar_y+(bar_h-2)-new_fill_h, bar_w-4, new_fill_h, fill=ORANGE)
                batt_group.append(batt_fill); last_batt_check = now
            


            time.sleep(0.05)
        else: time.sleep(0.001)
    else: time.sleep(0.1)
