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

# Settings UI - Color Sliders
# Text Color Slider (top)
text_color_preview = Rect(20, 30, 40, 40, fill=ORANGE, outline=DARK_GREEN, stroke=2)
settings_page.append(text_color_preview)
text_slider_bg = Rect(20, 85, 200, 20, fill=0x000000, outline=DARK_GREEN, stroke=2)
settings_page.append(text_slider_bg)
text_slider_handle = Rect(20, 83, 10, 24, fill=ORANGE)
settings_page.append(text_slider_handle)
text_label = label.Label(terminalio.FONT, text="Text Color", color=0xFFFFFF, scale=1, x=70, y=45)
settings_page.append(text_label)

# Outline Color Slider (bottom)
outline_color_preview = Rect(20, 130, 40, 40, fill=DARK_GREEN, outline=DARK_GREEN, stroke=2)
settings_page.append(outline_color_preview)
outline_slider_bg = Rect(20, 185, 200, 20, fill=0x000000, outline=DARK_GREEN, stroke=2)
settings_page.append(outline_slider_bg)
outline_slider_handle = Rect(20, 183, 10, 24, fill=ORANGE)
settings_page.append(outline_slider_handle)
outline_label = label.Label(terminalio.FONT, text="Outline Color", color=0xFFFFFF, scale=1, x=70, y=145)
settings_page.append(outline_label)

settings_page.hidden = True
root_group.append(settings_page)

try:
    custom_font = bitmap_font.load_font("/fonts/scientificaBold-11.bdf")
except:
    custom_font = terminalio.FONT



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
    text_slider_bg.outline = current_outline_color
    outline_slider_bg.outline = current_outline_color
    text_color_preview.outline = current_outline_color
    outline_color_preview.outline = current_outline_color
    text_slider_handle.fill = current_text_color
    outline_slider_handle.fill = current_text_color

# Main Clock UI
h_group, h_main, h_layers = create_double_outline_label("00", 60, 88, 9, ORANGE)
c_group, c_main, c_layers = create_double_outline_label(":", 129, 88, 9, ORANGE)
m_group, m_main, m_layers = create_double_outline_label("00", 189, 88, 9, ORANGE)

# Seconds Container - Left side 2px closer to center (x=89), width reduced (w=64) to keep right edge fixed
sec_bg_x, sec_bg_y, sec_bg_w, sec_bg_h = 89, 138, 64, 48
sec_rect = Rect(sec_bg_x, sec_bg_y, sec_bg_w, sec_bg_h, fill=0x000000, outline=DARK_GREEN, stroke=2)
s_group, s_main, s_layers = create_double_outline_label("00", 123, 162, 6, ORANGE, has_green=False, has_black=False)

main_group.append(h_group); main_group.append(c_group); main_group.append(m_group)
main_group.append(sec_rect); main_group.append(s_group)

# Timer Page UI
t_m_group, t_m_label, t_m_layers = create_double_outline_label("00", 60, 88, 9, ORANGE)
t_c_group, t_c_main, t_c_layers = create_double_outline_label(":", 129, 88, 9, ORANGE)
t_s_group, t_s_label, t_s_layers = create_double_outline_label("00", 189, 88, 9, ORANGE)
timer_page.append(t_m_group); timer_page.append(t_c_group); timer_page.append(t_s_group)

up_m = label.Label(terminalio.FONT, text="^", color=0xFF0000, scale=4, x=45, y=40)
dn_m = label.Label(terminalio.FONT, text="v", color=0xFF0000, scale=4, x=45, y=150)
up_s = label.Label(terminalio.FONT, text="^", color=0xFF0000, scale=4, x=174, y=40)
dn_s = label.Label(terminalio.FONT, text="v", color=0xFF0000, scale=4, x=174, y=150)
timer_page.append(up_m); timer_page.append(dn_m); timer_page.append(up_s); timer_page.append(dn_s)

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

current_page = "clock"; display.brightness = 1.0
last_interaction = time.monotonic(); TIMEOUT = 5.0
touch_debounced = False; last_batt_check = -60; last_day = -1
timer_min, timer_sec = 0, 0; timer_running = False; last_timer_tick = 0

# Color settings
current_text_color = ORANGE
current_outline_color = DARK_GREEN
color_palette = [0xFF0000, 0xFF4500, 0xFF8C00, 0xFFD700, 0xFFFF00, 0x00FF00, 0x00FFFF, 0x0000FF, 0x8B00FF, 0xFF00FF, 0xFF1493, 0xFFFFFF]
text_color_index = 2  # Start at orange
outline_color_index = 5  # Start at green-ish
dragging_text_slider = False
dragging_outline_slider = False

gc.collect()

while True:
    now = time.monotonic()
    points = ft.touches if ft else []
    if points:
        if not touch_debounced:
            p = points[0]; tx, ty = p['x'], p['y']
            if display.brightness < 0.1:
                display.brightness = 1.0; last_interaction = now
            else:
                if current_page == "clock" and (100 < tx < 140 and ty >= 80 and ty <= 200):
                    display.brightness = 0.0; current_page = "clock"
                    main_group.hidden, timer_page.hidden, settings_page.hidden = False, True, True
                elif current_page == "clock" and ty < 80:
                    main_group.hidden, timer_page.hidden, settings_page.hidden = True, False, True
                    current_page = "timer"; last_interaction = now
                elif current_page == "clock" and tx > 120 and ty > 200:
                    main_group.hidden, timer_page.hidden, settings_page.hidden = True, True, False
                    current_page = "settings"; last_interaction = now
                elif current_page == "timer":
                    last_interaction = now
                    if ty > 160:
                        current_page = "clock"
                        main_group.hidden, timer_page.hidden, settings_page.hidden = False, True, True
                    elif 40 < ty < 136:
                        timer_running = not timer_running; last_timer_tick = now
                    elif not timer_running:
                        if tx < 120:
                            if ty < 40: timer_min = (timer_min + 1) % 60
                            elif ty >= 140: timer_min = (timer_min - 1) % 60
                        else:
                            if ty < 40: timer_sec = (timer_sec + 1) % 60
                            elif ty >= 140: timer_sec = (timer_sec - 1) % 60
                    m_str, s_str = "{:02d}".format(timer_min), "{:02d}".format(timer_sec)
                    t_m_label.text, t_s_label.text = m_str, s_str
                    for l in t_m_layers: l.text = m_str
                    for l in t_s_layers: l.text = s_str
                elif current_page == "settings":
                    last_interaction = now
                    # Check if touching text color slider area
                    if 20 <= tx <= 220 and 83 <= ty <= 107:
                        dragging_text_slider = True
                        # Calculate color index from slider position
                        slider_pos = max(20, min(210, tx))
                        text_color_index = int((slider_pos - 20) / 190 * (len(color_palette) - 1))
                        current_text_color = color_palette[text_color_index]
                        # Update slider handle position
                        settings_page.remove(text_slider_handle)
                        handle_x = 20 + int(text_color_index / (len(color_palette) - 1) * 190)
                        text_slider_handle = Rect(handle_x, 83, 10, 24, fill=current_text_color)
                        settings_page.append(text_slider_handle)
                        # Update preview square
                        settings_page.remove(text_color_preview)
                        text_color_preview = Rect(20, 30, 40, 40, fill=current_text_color, outline=current_outline_color, stroke=2)
                        settings_page.append(text_color_preview)
                        update_all_colors()
                    # Check if touching outline color slider area
                    elif 20 <= tx <= 220 and 183 <= ty <= 207:
                        dragging_outline_slider = True
                        # Calculate color index from slider position
                        slider_pos = max(20, min(210, tx))
                        outline_color_index = int((slider_pos - 20) / 190 * (len(color_palette) - 1))
                        current_outline_color = color_palette[outline_color_index]
                        # Update slider handle position
                        settings_page.remove(outline_slider_handle)
                        handle_x = 20 + int(outline_color_index / (len(color_palette) - 1) * 190)
                        outline_slider_handle = Rect(handle_x, 183, 10, 24, fill=current_text_color)
                        settings_page.append(outline_slider_handle)
                        # Update preview square
                        settings_page.remove(outline_color_preview)
                        outline_color_preview = Rect(20, 130, 40, 40, fill=current_outline_color, outline=current_outline_color, stroke=2)
                        settings_page.append(outline_color_preview)
                        update_all_colors()
                    elif ty > 200:
                        current_page = "clock"
                        main_group.hidden, timer_page.hidden, settings_page.hidden = False, True, True
            touch_debounced = True
    else: touch_debounced = False

    if timer_running and now - last_timer_tick >= 1.0:
        if timer_min == 0 and timer_sec == 0: timer_running = False
        else:
            if timer_sec == 0: timer_min -= 1; timer_sec = 59
            else: timer_sec -= 1
            m_str, s_str = "{:02d}".format(timer_min), "{:02d}".format(timer_sec)
            t_m_label.text, t_s_label.text = m_str, s_str
            for l in t_m_layers: l.text = m_str
            for l in t_s_layers: l.text = s_str
        last_timer_tick = now

    if now - last_interaction > TIMEOUT and display.brightness > 0 and not timer_running:
        display.brightness = 0.0; current_page = "clock"
        main_group.hidden, timer_page.hidden, settings_page.hidden = False, True, True; gc.collect()

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
