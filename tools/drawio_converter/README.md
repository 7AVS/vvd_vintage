# DrawIO to PowerPoint Converter

Converts DrawIO diagrams to PowerPoint with **native editable shapes** (not images).

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   READ AGENT    │ --> │  LAYOUT AGENT   │ --> │   converter.py  │
│                 │     │                 │     │                 │
│ Parses DrawIO   │     │ Calculates      │     │ Generates PPTX  │
│ Extracts        │     │ positions for   │     │ from layout     │
│ structure       │     │ target canvas   │     │ specification   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
  read_output.json       layout_output.json         output.pptx
                               ▲
                               │
                       ┌───────┴───────┐
                       │  config.json  │
                       └───────────────┘
```

## Files

| File | Purpose |
|------|---------|
| `config.json` | Your settings: work area, spacing rules, priorities |
| `converter.py` | Python script that generates PPTX from layout spec |
| `prompts/` | Agent prompts for Read and Layout agents |

## How to Use

### Step 1: Configure

Edit `config.json` with your target dimensions:

```json
{
  "work_area": {
    "width": 1100,
    "height": 600
  },
  "slide": {
    "width": 1200,
    "height": 675,
    "offset_x": 50,
    "offset_y": 40
  }
}
```

- `work_area`: The rectangle where content will be placed
- `slide`: Full PowerPoint slide dimensions
- `offset_x/y`: Where the work area starts on the slide

### Step 2: Run Read Agent

Give Claude this prompt:

```
You are the READ AGENT. Parse this DrawIO file and extract all elements.

Read: [path to your .drawio file]

Output a JSON with:
- source canvas dimensions
- all elements with: id, type, geometry (x, y, width, height), style, value, semantic_role
- hierarchy description

Save to: read_output.json
```

### Step 3: Run Layout Agent

Give Claude this prompt:

```
You are the LAYOUT AGENT. Calculate positions for the target canvas.

Inputs:
- read_output.json (element data)
- config.json (design rules)

Apply these rules:
- Fit all elements into work_area dimensions
- Maintain minimum spacing between elements
- Scale fonts proportionally (min 6pt)
- Keep children inside containers
- No overlapping

Output: layout_output.json with new x, y, width, height for each element.
```

### Step 4: Generate PowerPoint

```bash
python converter.py layout_output.json output.pptx
```

## Configuration Options

### work_area
The box where content goes. Agents fill this space.

### spacing
```json
{
  "min_gap": 10,           // Minimum space between elements
  "container_padding": 8,  // Space inside containers
  "section_gap": 15        // Space between major sections
}
```

### priority
Order of importance when space is tight:
```json
["title", "subtitle", "main_containers", "modules", "arrows", "legend", "callouts"]
```

Lower priority items may be scaled down or repositioned first.

### overflow_strategy
What to do when content doesn't fit:
- `"scale_down"` - Reduce sizes proportionally
- `"truncate"` - Cut off lowest priority items
- `"split"` - Create multiple slides

### text
```json
{
  "min_font_size": 6,      // Never go below this
  "max_font_size": 24,     // Cap large fonts
  "scale_factor": 0.85     // How much to reduce fonts
}
```

### style
```json
{
  "no_shadows": true,      // Clean text, no effects
  "no_effects": true,
  "preserve_colors": true, // Keep original colors
  "preserve_fonts": true   // Keep original fonts
}
```

## What Gets Converted

| DrawIO Element | PowerPoint Result |
|----------------|-------------------|
| Rectangles | Native shapes (editable) |
| Rounded rectangles | Native shapes (editable) |
| Text boxes | Text boxes (editable) |
| Arrows/connectors | Connector lines |
| Colors | Preserved |
| Fonts | Preserved |
| Borders | Preserved |
| Dashed lines | Preserved |

## Limitations

- **Curved arrows**: Converted to straight lines
- **Complex connectors**: Simplified
- **Embedded images**: Not supported
- **Gradients**: Converted to solid colors
- **Groups**: Flattened (but visual grouping preserved)

## Requirements

```bash
pip install python-pptx
```

## Example

```bash
# 1. Put your DrawIO file in this folder
cp my_diagram.drawio ./

# 2. Ask Claude to run Read Agent on my_diagram.drawio
#    Claude outputs: read_output.json

# 3. Ask Claude to run Layout Agent
#    Claude outputs: layout_output.json

# 4. Generate PowerPoint
python converter.py layout_output.json my_diagram.pptx
```

## Troubleshooting

**Elements overlap:**
- Increase `min_gap` in config.json
- Reduce `work_area` dimensions to give more breathing room
- Check if source DrawIO has overlapping elements

**Text too small:**
- Increase `min_font_size` in config.json
- Reduce number of elements on the slide

**Colors wrong:**
- Check that `preserve_colors` is true
- Verify hex colors in DrawIO are valid (#RRGGBB format)

**File won't open in PowerPoint:**
- Ensure layout_output.json is valid JSON
- Check Python console for errors
