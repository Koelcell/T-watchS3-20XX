# Lilygo T-Watch S3 2020 - Project Documentation

## Project Overview
Custom watch interface for the Lilygo T-Watch S3 2020 with multiple pages, custom fonts, and interactive color customization.

---

## Current Features

### 📱 **Pages**
1. **Clock Page** (Main)
   - Large time display with hours, minutes, and seconds
   - Date and day of week display
   - Battery indicator
   - Touch interactions for navigation

2. **Timer Page**
   - Countdown timer with minute/second controls
   - Start/stop functionality
   - Up/down buttons for adjusting time

3. **Settings Page**
   - Color customization sliders
   - Preview squares for color selection
   - Interactive UI controls

---

## UI Specifications

### **Clock Page Layout**

#### Time Display
- **Hours & Minutes**: 
  - Font: `scientificaBold-11`
  - Scale: 9
  - Color: Orange (customizable)
  - Position: Hours at (60, 88), Colon at (129, 88), Minutes at (189, 88)
  - Outline: Double outline (Dark Green + Black layers)

- **Seconds**:
  - Font: `scientificaBold-11`
  - Scale: 6
  - Color: Orange (customizable)
  - Position: (123, 162)
  - Container: Black box with dark green outline at (89, 138, 64x48)

#### Date & Day Display
- **Day of Week**:
  - Font: `scientificaBold-11`
  - Scale: 3
  - Color: Orange (customizable)
  - Position: Bottom-left (8, 231)
  - Format: 3-letter abbreviation (e.g., "Mon", "Tue")

- **Date**:
  - Font: `scientificaBold-11`
  - Scale: 3
  - Color: Orange (customizable)
  - Position: Bottom-center (120, 233)
  - Format: DD/MM

#### Battery Indicator
- **Position**: Top-right corner (221, 202)
- **Size**: 12x30 pixels
- **Color**: Orange (customizable)
- **Updates**: Every 30 seconds
- **Fill**: Proportional to battery percentage

#### Border
- **Color**: Dark Green (customizable)
- **Stroke**: 4 pixels
- **Full screen outline**: 240x240

---

### **Timer Page Layout**

#### Timer Display
- **Minutes & Seconds**:
  - Font: `scientificaBold-11`
  - Scale: 9
  - Color: Orange (customizable)
  - Position: Minutes at (60, 88), Colon at (129, 88), Seconds at (189, 88)
  - Outline: Double outline (Dark Green + Black layers)

#### Controls
- **Up/Down Arrows**:
  - Font: terminalio.FONT
  - Scale: 4
  - Color: Red
  - Positions:
    - Up Minutes: (45, 40)
    - Down Minutes: (45, 150)
    - Up Seconds: (174, 40)
    - Down Seconds: (174, 150)

#### Border
- **Color**: Red
- **Stroke**: 4 pixels

---

### **Settings Page Layout**

#### Text Color Slider (Top)
- **Preview Square**:
  - Position: (20, 30)
  - Size: 40x40 pixels
  - Fill: Current text color
  - Outline: White, 2px stroke

- **Label**: "Text Color" at (70, 45)

- **Slider**:
  - Background: (20, 85, 200x20)
  - Handle: 10x24 white rectangle
  - Touch Area: y=83 to y=107, x=20 to x=220

#### Outline Color Slider (Bottom)
- **Preview Square**:
  - Position: (20, 130)
  - Size: 40x40 pixels
  - Fill: Current outline color
  - Outline: White, 2px stroke

- **Label**: "Outline Color" at (70, 145)

- **Slider**:
  - Background: (20, 185, 200x20)
  - Handle: 10x24 white rectangle
  - Touch Area: y=183 to y=207, x=20 to x=220

#### Color Palette
12 colors available:
1. Red (`0xFF0000`)
2. Orange-Red (`0xFF4500`)
3. **Orange** (`0xFF8C00`) - Default text color
4. Gold (`0xFFD700`)
5. Yellow (`0xFFFF00`)
6. **Green** (`0x00FF00`) - Near default outline
7. Cyan (`0x00FFFF`)
8. Blue (`0x0000FF`)
9. Purple (`0x8B00FF`)
10. Magenta (`0xFF00FF`)
11. Pink (`0xFF1493`)
12. White (`0xFFFFFF`)

#### Border
- **Color**: Gray
- **Stroke**: 4 pixels

---

## Touch Interactions

### **Clock Page**
| Touch Area | Action |
|------------|--------|
| Center (100-140, 80-200) | Sleep mode (brightness to 0) |
| Top (ty < 80) | Navigate to Timer page |
| Bottom-right (tx > 120, ty > 200) | Navigate to Settings page |
| Any touch when sleeping | Wake up display |

### **Timer Page**
| Touch Area | Action |
|------------|--------|
| Bottom (ty > 160) | Return to Clock page |
| Center (40 < ty < 136) | Start/Stop timer |
| Top-left (tx < 120, ty < 40) | Increment minutes |
| Bottom-left (tx < 120, ty >= 140) | Decrement minutes |
| Top-right (tx >= 120, ty < 40) | Increment seconds |
| Bottom-right (tx >= 120, ty >= 140) | Decrement seconds |

### **Settings Page**
| Touch Area | Action |
|------------|--------|
| Text slider (20-220, 83-107) | Adjust text color |
| Outline slider (20-220, 183-207) | Adjust outline color |
| Bottom (ty > 200) | Return to Clock page |

---

## Technical Details

### **Display**
- Resolution: 240x240 pixels
- Background color: `0x05070A` (dark blue-black)

### **Fonts**
- Custom font: `/fonts/scientificaBold-11.bdf`
- Fallback: `terminalio.FONT`

### **I2C Configuration**
- Touch I2C: GPIO40 (SCL), GPIO39 (SDA)
- Sensor I2C: GPIO11 (SCL), GPIO10 (SDA)

### **Power Management**
- Auto-sleep timeout: 5 seconds of inactivity
- Sleep mode: Brightness set to 0
- Exception: Timer running prevents auto-sleep

### **Memory Management**
- Garbage collection called on initialization and after sleep

---

## Changelog

### **2025-12-30 02:50 - Dynamic Settings Page Theming**
- 🎨 Settings page now follows the global color theme
- **Outlines**: Page border and slider outlines update with `Outline Color`
- **Handles**: Slider handles update with `Text Color`
- **Colons**: Clock and timer separators (`:`) now update dynamically
- Removed static gray/white elements for a cohesive look

### **2025-12-30 02:02 - Bug Fix: Slider Index Error**
- 🐛 Fixed IndexError on line 255 when using color sliders
- Changed from `.insert(index)` to `.append()` for slider handle and preview updates
- Prevents "index out of range" errors when updating UI elements

### **2025-12-30 01:59 - Settings Page with Color Sliders**
- ✅ Added Settings page with interactive color customization
- ✅ Created two sliders for text and outline colors
- ✅ Added preview squares above each slider
- ✅ Implemented `update_all_colors()` function to apply changes globally
- ✅ Added 12-color palette with smooth slider interaction
- ✅ Real-time color updates across all UI elements

### **2025-12-29 - Previous Session**
- ✅ Adjusted date/day font sizes to scale 3
- ✅ Positioned date and day at bottom of screen
- ✅ Expanded touch areas for better navigation
- ✅ Added touch area on timer page to return to clock
- ✅ Refined UI positioning and spacing

### **Earlier Development**
- ✅ Implemented main clock display with custom font
- ✅ Created timer page with countdown functionality
- ✅ Added battery indicator with percentage display
- ✅ Implemented touch navigation system
- ✅ Added double outline effect for text
- ✅ Set up multi-page architecture

---

## Future Enhancement Ideas
- [ ] Add alarm functionality
- [ ] Implement stopwatch mode
- [ ] Add more color palettes or RGB picker
- [ ] Save color preferences to persistent storage
- [ ] Add brightness control slider
- [ ] Implement step counter (if hardware supports)
- [ ] Add notification display
- [ ] Create custom watch faces

---

## File Structure
```
d:\
├── code.py                    # Main application code
├── TWATCH_CHANGELOG.md        # This documentation file
└── fonts/
    └── scientificaBold-11.bdf # Custom font file
```

---

**Last Updated**: 2025-12-30  
**Device**: Lilygo T-Watch S3 2020  
**Language**: CircuitPython
