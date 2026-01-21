"""
================================================================================
File: RBC_COLOR_SCHEME.md
Purpose: RBC Brand Color Reference for VVD Analysis Visualizations
Author: VVD Analytics Team
Date: June 30, 2025

Description:
    Official RBC brand color palettes for use in data visualizations,
    presentations, and digital products. Use these hex codes and names
    to ensure brand consistency.
================================================================================
"""

# RBC Brand Colour Reference

This document summarizes the official RBC brand colour palettes for use in data visualizations, presentations, and digital products. Use these hex codes and names to ensure brand consistency.

## Primary Colours

| Name | Hex | RGB | CMYK | Pantone | Description |
|------|-----|-----|------|---------|-------------|
| Bright Blue | #0051A5 | 0,81,165 | 100,60,0,6 | 286 | Primary blue for print and digital ads |
| Bright Blue Tint 1 | #006AC3 | 0,106,195 | 90,48,0,0 | 285 | Primary blue for RBC websites/mobile apps |
| Dark Blue | #003168 | 0,49,104 | 100,60,0,40 | 288 | For High Net Worth/Enterprise |
| Warm Yellow | #FFC72C | 255,199,44 | 0,21,90,0 | 123 | Core yellow accent |
| Cool White | #E7EEF1 | 231,238,241 | 3,0,0,5 | - | Core background colour |

## Accent Colours (Mass)

| Name | Hex | RGB | CMYK | Pantone |
|------|-----|-----|------|---------|
| Ocean | #0091DA | 0,145,218 | 89,18,0,0 | 2192 |
| Sand | #B58500 | 181,133,0 | 6,32,100,24 | 125 |
| Sky | #C1B5E0 | 193,181,224 | 68,3,0,0 | 298 |
| Sunburst | #FCA311 | 252,163,17 | 0,40,99,0 | 137 |
| Gray | #9EA2A2 | 158,162,162 | 19,12,13,34 | 422 |

## Accent Colours (HNW)

| Name | Hex | RGB | CMYK | Pantone |
|------|-----|-----|------|---------|
| Tundra | #07AFBF | 7,175,191 | 133,175,191 | - |
| Light Gray | #C7B5A5 | 199,181,165 | 193,181,165 | - |
| Beige | #B98970 | 185,137,112 | 184,169,112 | - |

## Charts & Graphs Colours

### Primary Chart Colors
| Name | Hex | RGB | Pantone | CMYK |
|------|-----|-----|---------|------|
| Bright Blue | #0051A5 | 0,81,165 | 286 | 100,60,0,6 |
| Dark Blue | #003168 | 0,49,104 | 288 | 100,60,0,40 |
| Warm Yellow | #FFC72C | 255,199,44 | 123 | 0,21,90,0 |
| Tundra | #07AFBF | 7,175,191 | - | 35,8,17 |
| Apple | #AABAA | 170,186,170 | 550 | 29,3,100,14 |
| Sunburst | #FCA311 | 252,163,17 | 137 | 0,45,95,0 |
| Carbon | #969299 | 150,146,153 | 7544 | 10,10,40 |
| Seaweed | #508086 | 80,128,134 | 7475 | 60,12,20,35 |
| Sky | #615E50 | 97,94,80 | - | 68,0,0,0 |
| Light Gray | #C1B5A5 | 193,181,165 | Warm Gray 4 | 0,15,21 |
| Beige | #B98970 | 185,137,112 | 4515 | 5,9,47,23 |
| Slate Gray | #676E6F | 103,110,111 | - | 40,30,22,60 |

## Usage Notes

### For Data Visualizations:
1. **Primary series**: Use Bright Blue (#0051A5) for the most important data series
2. **Secondary series**: Use accent colors in order: Ocean, Warm Yellow, Tundra, Sky
3. **Comparison/Control**: Use Cool White (#E7EEF1) or Gray (#9EA2A2)
4. **Highlights**: Use Warm Yellow (#FFC72C) for emphasis
5. **Background**: Use Cool White (#E7EEF1) or white

### Best Practices:
- Maximum 5-6 colors per chart for clarity
- Use color-blind friendly combinations when possible
- Ensure sufficient contrast for accessibility
- Use consistent colors across related charts

### Python Implementation Example:
```python
# RBC Color Palette for matplotlib/seaborn
RBC_COLORS = {
    'bright_blue': '#0051A5',
    'bright_blue_tint': '#006AC3',
    'dark_blue': '#003168',
    'warm_yellow': '#FFC72C',
    'cool_white': '#E7EEF1',
    'ocean': '#0091DA',
    'sand': '#B58500',
    'sky': '#C1B5E0',
    'sunburst': '#FCA311',
    'gray': '#9EA2A2',
    'tundra': '#07AFBF',
    'light_gray': '#C7B5A5',
    'beige': '#B98970'
}

# Recommended chart color sequence
RBC_CHART_COLORS = [
    '#0051A5',  # Bright Blue
    '#FFC72C',  # Warm Yellow
    '#0091DA',  # Ocean
    '#07AFBF',  # Tundra
    '#FCA311',  # Sunburst
    '#C1B5E0',  # Sky
    '#003168',  # Dark Blue
    '#B58500'   # Sand
]

# Set as default for matplotlib
import matplotlib.pyplot as plt
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=RBC_CHART_COLORS)
```

### Reference
Based on official RBC Brand Guidelines documentation.