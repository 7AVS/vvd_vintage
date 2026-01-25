# DrawIO Toolkit - User Guide

## What This Does

**Two Capabilities:**

1. **CREATE** DrawIO diagrams using visual frameworks and brand guidelines
2. **CONVERT** DrawIO diagrams to PowerPoint with native editable shapes (not images)

---

# PART 1: CREATING DrawIO Diagrams

## Design Guidelines

This folder contains visual frameworks for creating professional DrawIO diagrams:

| File | Purpose |
|------|---------|
| `VISUAL_FRAMEWORK_EXECUTIVE.md` | Slide layouts for executive audiences |
| `VISUAL_FRAMEWORK_TECHNICAL.md` | Slide layouts for technical audiences |
| `RBC_COLOR_SCHEME.md` | Brand colors (hex codes, usage rules) |

## Quick Reference: Key Colors

| Color | Hex | Use For |
|-------|-----|---------|
| Dark Blue | #003168 | Primary containers, headers |
| Ocean | #0091DA | Secondary containers, "how" sections |
| Warm Yellow | #FFC72C | Highlights, "why" sections |
| Tundra | #07AFBF | Status, progress indicators |
| Sunburst | #FCA311 | Calls to action, "next" sections |
| Cool White | #E7EEF1 | Backgrounds |

## Creating Diagrams

Tell Claude:
- "Create a DrawIO for [topic] using the executive framework"
- "Design a technical diagram for [topic]"
- "Use the visual framework to create slides for [topic]"

Claude will reference the VISUAL_FRAMEWORK files to create properly structured diagrams.

---

# PART 2: CONVERTING DrawIO to PowerPoint

## Quick Start

### Prerequisites
```bash
pip install python-pptx
```

### Steps

1. **Copy your DrawIO file** into this folder (`drawio/`)

2. **Tell Claude:** "Convert [filename].drawio to PowerPoint"

3. **Claude will:**
   - Run the Read Agent (parses your file)
   - Run the Layout Agent (calculates positions)
   - Generate the PowerPoint

4. **Open the `.pptx` file** in PowerPoint

---

## How Conversion Works

```
Your .drawio file
       │
       ▼
┌──────────────────┐
│   READ AGENT     │  ← Parses XML, extracts structure
│                  │
│ Output:          │
│ read_output.json │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  LAYOUT AGENT    │  ← Calculates positions for PowerPoint
│                  │
│ Input:           │
│ - read_output    │
│ - config.json    │
│                  │
│ Output:          │
│ layout_output    │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  converter.py    │  ← Generates the PPTX file
│                  │
│ Output:          │
│ your_file.pptx   │
└──────────────────┘
```

---

## Manual Steps (If You Want Control)

### Step 1: Run Read Agent

Tell Claude:
```
Run the read agent on [your_file.drawio]
```

This creates `read_output.json` with all your diagram elements.

### Step 2: (Optional) Adjust Configuration

Edit `config.json` to change:
- Target dimensions
- Spacing rules
- Font sizes

### Step 3: Run Layout Agent

Tell Claude:
```
Run the layout agent
```

This creates `layout_output.json` with calculated positions.

### Step 4: Generate PowerPoint

```bash
python converter.py layout_output.json my_presentation.pptx
```

---

## Configuration (config.json)

### Target Dimensions

```json
{
  "work_area": {
    "width": 1100,
    "height": 600
  }
}
```

This is the rectangle where your content will fit. Larger = more breathing room but potentially smaller elements.

### Slide Settings

```json
{
  "slide": {
    "width": 1200,
    "height": 675,
    "offset_x": 50,
    "offset_y": 40
  }
}
```

Standard 16:9 PowerPoint slide. The offset positions your content on the slide.

### Spacing Rules

```json
{
  "spacing": {
    "min_gap": 10,
    "container_padding": 8,
    "section_gap": 15
  }
}
```

- `min_gap`: Minimum space between any two elements
- `container_padding`: Space inside containers (around children)
- `section_gap`: Space between major sections

### Font Scaling

```json
{
  "text": {
    "min_font_size": 6,
    "max_font_size": 24,
    "scale_factor": 0.85
  }
}
```

- `min_font_size`: Never shrink text below this
- `scale_factor`: How much to reduce fonts (0.85 = 15% smaller)

---

## Common Commands

| You Say | Claude Does |
|---------|-------------|
| "Convert X.drawio to PowerPoint" | Full conversion |
| "Run read agent on X.drawio" | Parse only |
| "Run layout agent" | Calculate positions |
| "Parse X for conversion" | Same as read agent |
| "Calculate layout" | Same as layout agent |

---

## Troubleshooting

### Elements overlap
- Increase `min_gap` in config.json
- Reduce `work_area` dimensions (forces more compression)
- Check if source DrawIO has overlaps

### Text too small to read
- Increase `min_font_size` in config.json
- Reduce number of elements in your DrawIO

### Colors look wrong
- DrawIO colors should be hex format: `#RRGGBB`
- Check your DrawIO for unusual color values

### PowerPoint won't open the file
- Run `python converter.py` and check for errors
- Verify `layout_output.json` is valid JSON

### Missing elements
- Check `read_output.json` - are all elements there?
- If not, your DrawIO may have unsupported elements

---

## What Gets Converted

| DrawIO | PowerPoint |
|--------|------------|
| Rectangles | Editable shapes |
| Rounded rectangles | Editable shapes |
| Text | Editable text boxes |
| Arrows | Connector lines |
| Colors | Preserved |
| Borders | Preserved |
| Dashed lines | Preserved |
| Fonts | Preserved |

## What Doesn't Convert Perfectly

| DrawIO | PowerPoint Result |
|--------|-------------------|
| Curved arrows | Straight lines |
| Complex connectors | Simplified |
| Embedded images | Not supported |
| Gradients | Solid colors |
| Groups | Flattened |

---

## File Structure

```
drawio/
├── GUIDE.md                        ← You are here
├── README.md                       ← Technical documentation
├── config.json                     ← Your settings
├── converter.py                    ← Python script
├── RBC_COLOR_SCHEME.md             ← Brand colors
├── VISUAL_FRAMEWORK_EXECUTIVE.md   ← Executive slide patterns
├── VISUAL_FRAMEWORK_TECHNICAL.md   ← Technical slide patterns
├── prompts/
│   ├── read_agent.txt              ← Read Agent instructions
│   └── layout_agent.txt            ← Layout Agent instructions
└── [your files]
    ├── input.drawio
    ├── read_output.json            ← Created by Read Agent
    ├── layout_output.json          ← Created by Layout Agent
    └── output.pptx                 ← Final PowerPoint
```

---

## Tips

1. **Start simple** - Test with a simple DrawIO first before complex diagrams

2. **Check the JSON** - If something looks wrong, check `read_output.json` and `layout_output.json` to see what the agents produced

3. **Iterate** - If spacing is off, adjust `config.json` and run the Layout Agent again (no need to re-run Read Agent)

4. **Manual touch-up** - For complex diagrams, expect to do minor adjustments in PowerPoint after conversion

---

## Getting Help

If Claude doesn't recognize your commands, try:
- "Look at the DrawIO toolkit in CLAUDE.md"
- "Read the prompts in drawio/prompts/"
- "Help me convert [file].drawio to PowerPoint"
- "Create a diagram using the visual framework"
