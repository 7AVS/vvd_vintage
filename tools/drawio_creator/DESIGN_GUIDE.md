# DrawIO Design Guide

Actionable rules for creating professional DrawIO diagrams. Every rule is specific and implementable.

---

## Design Modes

This guide supports **three visual modes**. When the user requests a diagram, ask which mode (or default to Standard).

| Mode | Trigger Phrase | What It Looks Like |
|------|---------------|-------------------|
| **Standard** | "draw", "create a diagram" (default) | Full RBC color palette, professional styling |
| **Print** | "printer friendly", "black and white", "print mode" | Grayscale only, uses fill density + line weight + shape variation to differentiate |
| **Sketch** | "sketch", "napkin", "quick diagram", "simple" | Bare-bones outlines, no fills, minimal styling, intentionally low-fidelity |

Sections 1-10 apply to **Standard mode**. Sections 11-12 define **Print** and **Sketch** modes respectively. Section 13 is a quick-reference for all style strings across all three modes.

---

## 1. XML Boilerplate

Every generated `.drawio` file must start with this structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" agent="AI-Generated" version="24.0.0" type="device">
  <diagram id="unique-id" name="Page-1">
    <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1"
                  tooltips="1" connect="1" arrows="1" fold="1" page="1"
                  pageScale="1" pageWidth="1100" pageHeight="850"
                  background="#ffffff" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- Content cells here -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

**Page sizes:**
- Standard landscape: 1100 x 850
- Wide landscape (presentations): 1584 x 1080
- Tall/vertical flows: 850 x 1100

---

## 2. Style Presets

Copy-paste these style strings when generating DrawIO XML:

### Shapes

```
# Standard process box
rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;fontColor=#333333;

# Rounded process box
rounded=1;arcSize=40;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;fontColor=#333333;

# Decision diamond
shape=rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=14;fontColor=#333333;

# Database cylinder
shape=cylinder3;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;fontColor=#333333;boundedLbl=1;size=15;labelBackgroundColor=none;

# Start/End ellipse
shape=ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=14;fontColor=#333333;

# External system (dashed)
rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=14;fontColor=#333333;dashed=1;

# Container/swimlane
swimlane;startSize=40;fillColor=#f5f5f5;strokeColor=#999999;fontSize=16;fontStyle=1;fontColor=#333333;rounded=1;arcSize=8;swimlaneLine=0;

# Title text (no border)
text;html=1;align=left;verticalAlign=top;whiteSpace=wrap;rounded=0;fontSize=20;fontStyle=1;fontColor=#333333;fillColor=none;strokeColor=none;
```

### Connectors

```
# Primary flow (solid)
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#666666;strokeWidth=2;fontSize=11;labelBackgroundColor=#ffffff;

# Secondary flow (dashed)
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#999999;strokeWidth=2;dashed=1;dashPattern=8 8;fontSize=11;labelBackgroundColor=#ffffff;

# Data flow (thin, open arrow)
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#6c8ebf;strokeWidth=1;endArrow=open;endFill=0;fontSize=11;labelBackgroundColor=#ffffff;

# Dependency (dotted, thin)
edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#999999;strokeWidth=1;dashed=1;dashPattern=2 4;fontSize=11;labelBackgroundColor=#ffffff;
```

---

## 3. Shape Sizing

| Shape Type | Width | Height | Use Case |
|-----------|-------|--------|----------|
| Standard process box | 160 | 80 | Actions, services, components |
| Small label box | 120 | 60 | Short labels, simple text |
| Large component | 200 | 120 | Components needing description |
| Decision diamond | 120 | 80 | Yes/No branches |
| Database cylinder | 80 | 100 | Data stores, caches, queues |
| Start/End circle | 60 | 60 | Terminators, connectors |
| Person shape | 80 | 100 | Actors, users |

**Rules:**
- Same-type shapes must have identical dimensions
- Minimum shape size: 60 x 40
- Container inner padding: 20-30px from edge to children
- Container header height: 40px for swimlane title

---

## 4. Default Color Palette (Colorblind-Safe)

For non-branded diagrams, use these high-contrast defaults:

| Role | fillColor | strokeColor | When to Use |
|------|-----------|-------------|-------------|
| Primary/active | #dae8fc | #6c8ebf | Main process elements |
| Secondary/support | #d5e8d4 | #82b366 | Supporting elements |
| Warning/attention | #fff2cc | #d6b656 | Decisions, alerts |
| Danger/error | #f8cecc | #b85450 | Error states, problems |
| External/inactive | #f5f5f5 | #666666 | External systems, grey elements |
| Container bg | #f5f5f5 or none | #999999 | Group backgrounds |

**Color rules:**
- Max 5 categorical colors per diagram (excluding black/white/grey)
- Every color must have a documented meaning
- Include a legend when using more than 2 colors
- Never rely on color alone to convey meaning
- Use `fontColor=#333333` (not pure black) for softer contrast
- No gradients (`gradientColor=none`), no glass (`glass=0`), no shadows (`shadow=0`)

---

## 5. Shape Conventions

| Shape | DrawIO Style | Use When |
|-------|-------------|----------|
| Rectangle | `rounded=0;` | Tasks, services, modules (default) |
| Rounded rectangle | `rounded=1;arcSize=40;` | Start/end, softer look |
| Diamond | `shape=rhombus;` | Yes/No decisions |
| Cylinder | `shape=cylinder3;` | Databases, storage, queues |
| Ellipse | `shape=ellipse;` | Start/end terminators |
| Cloud | `shape=cloud;` | External/third-party services |
| Container | `swimlane;` or `container=1;` | Logical grouping |

**Rule:** Max 4 shape types per diagram (excluding containers).

---

## 6. Connector Rules

- **Default routing:** `edgeStyle=orthogonalEdgeStyle` (clean right angles)
- **Corners:** `rounded=1` (softened bends)
- **Stroke:** `strokeWidth=2`, `strokeColor=#666666` (lighter than shapes)
- **Labels:** `fontSize=11`, `labelBackgroundColor=#ffffff`
- **Avoid** bidirectional arrows (ambiguous) -- use two unidirectional arrows
- **Crossing lines:** Use `jumpStyle=arc;jumpSize=6;` if unavoidable
- **Flow:** Pick one direction (L-to-R or T-to-B) and stick to it

### Line Meanings

| Meaning | Style |
|---------|-------|
| Primary/active flow | Solid, 2px |
| Optional/secondary | Dashed 8-8, 2px |
| Weak dependency | Dotted 2-4, 1px |
| Data flow | Solid, 1px, open arrow |

---

## 7. Layout Patterns

### Left-to-Right Flow (Processes)
- All shapes at same Y coordinate
- Consistent X spacing: 220px (160px width + 60px gap)

### Top-to-Bottom Hierarchy (Architecture)
- Parent centered above children
- Y spacing: 120-160px between levels
- Children evenly distributed on X axis

### Grid Layout (Comparison/Dashboard)
- Consistent column widths and row heights
- Column gap: 40-60px, row gap: 40-60px
- All boxes identical size within grid

### Container Layout
- Padding: 20-30px all sides
- Header: 40px height
- Space between children: 40px
- Space between containers: 80px

---

## 8. XML Reference

### Vertex (shape)
```xml
<mxCell id="2" value="Process Name"
        style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;"
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="160" height="80" as="geometry"/>
</mxCell>
```

### Edge (connector)
```xml
<mxCell id="3" value=""
        style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#666666;strokeWidth=2;"
        edge="1" parent="1" source="2" target="4">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

### Container with child
```xml
<mxCell id="5" value="Group Name"
        style="swimlane;startSize=40;fillColor=#f5f5f5;strokeColor=#999999;fontSize=16;fontStyle=1;"
        vertex="1" parent="1">
  <mxGeometry x="50" y="50" width="400" height="300" as="geometry"/>
</mxCell>
<mxCell id="6" value="Child Shape"
        style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;"
        vertex="1" parent="5">
  <mxGeometry x="30" y="60" width="160" height="80" as="geometry"/>
</mxCell>
```

Note: Child geometry is relative to parent container origin.

### ID Rules
- `id="0"` -- root cell (mandatory)
- `id="1"` -- default layer, `parent="0"` (mandatory)
- Content IDs start at `2`, increment sequentially
- String IDs OK for readability: `id="process-1"`, `id="db-users"`

### Style String Format
- Semicolon-delimited: `key1=value1;key2=value2;`
- Always end with trailing semicolon
- Always include `html=1;` and `whiteSpace=wrap;`
- Hex colors with `#`: `fillColor=#dae8fc`
- Booleans: `0` or `1`
- Font style bitmask: 0=normal, 1=bold, 2=italic, 3=bold+italic, 4=underline

### HTML in Values
When `html=1` in style: `value="&lt;b&gt;Title&lt;/b&gt;&lt;br&gt;Description"`

---

## 9. Professional Quality Checklist

Run this before delivering any diagram:

| Check | Pass | Fail |
|-------|------|------|
| All shapes grid-snapped (multiples of 10) | Aligned | Random positions |
| Consistent dimensions per shape type | Uniform | Every shape different |
| Uniform spacing (40-60px elements, 80px groups) | Even gaps | Random distances |
| 3-5 purposeful colors with legend | Coded | Rainbow, no legend |
| 1 font family, 2-3 sizes, clear hierarchy | Clean | Multiple fonts |
| No shadows, gradients, 3D, glass | Flat | Effects everywhere |
| Orthogonal connectors, consistent routing | Clean | Mixed styles |
| Single flow direction (L-R or T-B) | Consistent | Arrows everywhere |
| Deliberate whitespace | Breathing room | Crammed or wasteful |
| Every shape labeled | Readable | Unlabeled shapes |
| Legend present (if color-coded) | Documented | Missing |

---

## 10. The 15 Non-Negotiable Rules

1. Grid-snap everything (coordinates/dimensions in multiples of 10)
2. `shadow=0` always, at model and cell level
3. Max 5 categorical colors, each with documented meaning
4. One font family (Helvetica or Arial)
5. Max 3 font sizes (title, body, annotation)
6. Same shape type = same dimensions
7. Min 40px between elements, 80px between groups
8. Orthogonal edge routing with rounded corners
9. Connectors lighter than shapes (#666666 vs shape strokes)
10. Always include `whiteSpace=wrap;html=1;` in every shape
11. One flow direction per diagram (L-R or T-B, never mixed)
12. No gradients, glass, or 3D effects -- flat design only
13. Include legend when using color/line-style coding
14. Container borders subtler than content borders
15. Every element earns its place -- if removing it changes nothing, remove it

---

## 11. Print Mode (Black & White)

Designed for grayscale printing. Every distinction survives monochrome output at 300 DPI. Based on ISO 128 line conventions, ASME Y14.2 weight ratios, and WCAG 2.1 non-text contrast requirements.

### Grayscale Palette

| Role | Name | Hex | Use Case |
|------|------|-----|----------|
| Background | White | `#FFFFFF` | Page background |
| Fill Level 1 | Ghost Gray | `#F2F2F2` | Subtle grouping, container bg |
| Fill Level 2 | Light Gray | `#D9D9D9` | Secondary elements |
| Fill Level 3 | Medium Gray | `#B3B3B3` | Standard element fill |
| Fill Level 4 | Steel Gray | `#808080` | Emphasized elements |
| Fill Level 5 | Dark Gray | `#4D4D4D` | High-emphasis, headers |
| Maximum | Black | `#000000` | Text, primary borders |

**Text color rule:** Black `#000000` on fills lighter than Steel. White `#FFFFFF` on Steel and darker.

### Line Styles (replace color-coding)

| Line Name | DrawIO Style | Meaning |
|-----------|-------------|---------|
| Solid | `dashed=0;` | Primary flow |
| Long dash | `dashed=1;fixDash=1;dashPattern=8 8;` | Conditional/optional |
| Short dash | `dashed=1;fixDash=1;dashPattern=4 4;` | Alternatives |
| Dotted | `dashed=1;fixDash=1;dashPattern=2 2;` | Implied/future |
| Dash-dot | `dashed=1;fixDash=1;dashPattern=8 4 2 4;` | References |

Always use `fixDash=1` for print -- prevents dash patterns from scaling with stroke width.

### Line Weights

| Weight | strokeWidth | Purpose |
|--------|------------|---------|
| Hairline | 1 | Annotations, minor links |
| Standard | 2 | Default connections |
| Bold | 3 | Primary flow, emphasis |
| Heavy | 4 | Boundaries, group outlines |

### Hatching (Pattern Fills)

DrawIO supports pattern fills via the sketch engine. Use `jiggle=0;curveFitting=1;` for clean engineering-style hatching without the hand-drawn look.

| Pattern | Style Fragment |
|---------|---------------|
| Light hatch | `sketch=1;fillStyle=hachure;hachureGap=12;hachureAngle=45;fillWeight=1;jiggle=0;curveFitting=1;` |
| Medium hatch | `sketch=1;fillStyle=hachure;hachureGap=8;hachureAngle=45;fillWeight=1;jiggle=0;curveFitting=1;` |
| Dense hatch | `sketch=1;fillStyle=hachure;hachureGap=4;hachureAngle=45;fillWeight=1;jiggle=0;curveFitting=1;` |
| Cross hatch | `sketch=1;fillStyle=cross-hatch;hachureGap=8;fillWeight=1;jiggle=0;curveFitting=1;` |
| Dot fill | `sketch=1;fillStyle=dots;hachureGap=10;fillWeight=2;jiggle=0;curveFitting=1;` |

**Limitation:** Pattern fills require `sketch=1`. No native hatch without it (DrawIO GitHub #753).

### Print Mode: Differentiation Strategy (5 types without color)

| Type | Shape | Fill | Border | Weight | Preset Name |
|------|-------|------|--------|--------|-------------|
| A | Rectangle | White #FFFFFF | Solid black | 3px bold | `PRINT_PRIMARY` |
| B | Rectangle | Light #D9D9D9 | Solid black | 2px standard | `PRINT_SECONDARY` |
| C | Rectangle | Hachure | Solid black | 2px standard | `PRINT_HATCH` |
| D | Diamond | White #FFFFFF | Solid black | 3px bold | `PRINT_DECISION` |
| E | Ellipse | Medium #B3B3B3 | Solid black | 2px standard | `PRINT_TERMINAL` |

Each type differs by at least TWO visual variables (shape + fill, or shape + weight).

### Print Mode: Shape Style Strings

```
# Primary box (white, bold border)
PRINT_PRIMARY: rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=3;fontFamily=Helvetica;fontSize=11;fontColor=#000000;fontStyle=1;

# Secondary box (light gray)
PRINT_SECONDARY: rounded=0;whiteSpace=wrap;html=1;fillColor=#D9D9D9;strokeColor=#000000;strokeWidth=2;fontFamily=Helvetica;fontSize=11;fontColor=#000000;fontStyle=0;

# Tertiary box (medium gray)
PRINT_TERTIARY: rounded=0;whiteSpace=wrap;html=1;fillColor=#B3B3B3;strokeColor=#000000;strokeWidth=1;fontFamily=Helvetica;fontSize=11;fontColor=#000000;fontStyle=0;

# Dark emphasis (dark fill, white text)
PRINT_EMPHASIS: rounded=0;whiteSpace=wrap;html=1;fillColor=#4D4D4D;strokeColor=#000000;strokeWidth=3;fontFamily=Helvetica;fontSize=11;fontColor=#FFFFFF;fontStyle=1;

# De-emphasized (ghost gray, thin gray border)
PRINT_GHOST: rounded=0;whiteSpace=wrap;html=1;fillColor=#F2F2F2;strokeColor=#808080;strokeWidth=1;fontFamily=Helvetica;fontSize=9;fontColor=#808080;fontStyle=2;

# Decision diamond
PRINT_DECISION: shape=rhombus;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=3;fontFamily=Helvetica;fontSize=11;fontColor=#000000;fontStyle=1;

# Start/End terminal
PRINT_TERMINAL: shape=ellipse;whiteSpace=wrap;html=1;fillColor=#B3B3B3;strokeColor=#000000;strokeWidth=2;fontFamily=Helvetica;fontSize=11;fontColor=#000000;fontStyle=1;

# Hatched box (engineering-style diagonal lines)
PRINT_HATCH: rounded=0;whiteSpace=wrap;html=1;sketch=1;fillStyle=hachure;hachureGap=8;hachureAngle=45;fillWeight=1;jiggle=0;curveFitting=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=2;fontFamily=Helvetica;fontSize=11;fontColor=#000000;

# Cross-hatched box
PRINT_CROSSHATCH: rounded=0;whiteSpace=wrap;html=1;sketch=1;fillStyle=cross-hatch;hachureGap=8;fillWeight=1;jiggle=0;curveFitting=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=2;fontFamily=Helvetica;fontSize=11;fontColor=#000000;

# Container/group
PRINT_GROUP: rounded=1;whiteSpace=wrap;html=1;fillColor=#F2F2F2;strokeColor=#808080;strokeWidth=2;dashed=1;fixDash=1;dashPattern=12 4;fontFamily=Helvetica;fontSize=14;fontColor=#000000;fontStyle=1;verticalAlign=top;container=1;collapsible=0;
```

### Print Mode: Connector Style Strings

```
# Primary flow (solid, bold)
PRINT_CONN_PRIMARY: edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=3;dashed=0;endArrow=block;endFill=1;

# Secondary flow (dashed)
PRINT_CONN_SECONDARY: edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=2;dashed=1;fixDash=1;dashPattern=8 8;endArrow=block;endFill=1;

# Conditional (dotted, thin)
PRINT_CONN_CONDITIONAL: edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=1;dashed=1;fixDash=1;dashPattern=2 2;endArrow=open;endFill=0;

# Reference (dash-dot)
PRINT_CONN_REFERENCE: edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#000000;strokeWidth=2;dashed=1;fixDash=1;dashPattern=8 4 2 4;endArrow=open;endFill=0;
```

---

## 12. Sketch Mode (Napkin-Style)

Radical reduction. Bare-bones outlines, no fills, minimal styling. Communicates "this is a concept" not "this is finished." Inspired by low-fidelity wireframing (Nielsen Norman Group, Balsamiq).

**This is NOT DrawIO's built-in `sketch=1` mode** -- that looks too polished. This is simpler.

### Core Principles

- `fillColor=none` -- transparent, not white. Shapes are just outlines.
- `strokeColor=#333333` -- off-black signals "draft." Pure black signals "final."
- `strokeWidth=1` -- thinnest visible line. No emphasis anywhere.
- Rectangles and lines only. No fancy shapes.
- No rounded corners, no fills, no shadows, no gradients.
- Max 2 font sizes (11pt body, 14pt bold headers).
- Max 2 connector types (solid primary, dashed optional).

### Sketch Mode: Shape Style Strings

```
# Standard box (the only shape you need 90% of the time)
SKETCH_BOX: rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#333333;strokeWidth=1;fontFamily=Helvetica;fontSize=11;fontColor=#333333;fontStyle=0;shadow=0;glass=0;

# Header box (use sparingly for one level of emphasis)
SKETCH_HEADER: rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#333333;strokeWidth=1;fontFamily=Helvetica;fontSize=14;fontColor=#333333;fontStyle=1;shadow=0;glass=0;

# Container/group (lighter, dashed, recedes behind content)
SKETCH_GROUP: rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#AAAAAA;strokeWidth=1;dashed=1;fixDash=1;dashPattern=4 4;fontFamily=Helvetica;fontSize=9;fontColor=#AAAAAA;fontStyle=2;verticalAlign=top;shadow=0;glass=0;container=1;collapsible=0;

# Floating annotation (no border, just text)
SKETCH_NOTE: rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=none;strokeWidth=0;fontFamily=Helvetica;fontSize=9;fontColor=#999999;fontStyle=2;shadow=0;glass=0;
```

### Sketch Mode: Connector Style Strings

```
# Primary flow
SKETCH_CONN_PRIMARY: edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#333333;strokeWidth=1;dashed=0;endArrow=block;endFill=1;fontSize=9;fontColor=#333333;

# Optional/secondary
SKETCH_CONN_OPTIONAL: edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#333333;strokeWidth=1;dashed=1;fixDash=1;dashPattern=4 4;endArrow=open;endFill=0;fontSize=9;fontColor=#333333;
```

Two connector types maximum. If you need more, you've outgrown Sketch mode -- switch to Standard or Print.

### What NOT to Use in Sketch Mode

| Avoid | Why |
|-------|-----|
| Any `fillColor` (except `none`) | Fills imply finished design |
| `rounded=1` | Adds visual complexity for zero gain |
| `shadow=1`, `glass=1`, `sketch=1` | Decoration signals polish |
| `gradientColor` | Decoration |
| `strokeWidth` > 1 | Thick lines imply emphasis |
| `fontSize` > 14 or < 9 | Keep the range tight |
| Diamonds, hexagons, cylinders, ellipses | Rectangles only |

### Intentional Simple vs Lazy

The difference is **consistency**. A napkin sketch with uniform 1px borders, aligned boxes, even spacing, and clear labels reads as "I chose this fidelity deliberately." Random sizes, misaligned boxes, and missing labels reads as "I ran out of time."

---

## 13. Quick Reference: All Mode Style Strings

### Standard Mode (RBC Color)

| Preset | Key Style Properties |
|--------|---------------------|
| Process box | `fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;` |
| Decision | `shape=rhombus;fillColor=#fff2cc;strokeColor=#d6b656;` |
| Database | `shape=cylinder3;fillColor=#dae8fc;strokeColor=#6c8ebf;` |
| Start/End | `shape=ellipse;fillColor=#d5e8d4;strokeColor=#82b366;` |
| External | `fillColor=#f5f5f5;strokeColor=#666666;dashed=1;` |
| Container | `swimlane;fillColor=#f5f5f5;strokeColor=#999999;` |
| Primary connector | `strokeColor=#666666;strokeWidth=2;` |

### Print Mode (Grayscale)

| Preset | Key Style Properties |
|--------|---------------------|
| Primary box | `fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=3;` |
| Secondary box | `fillColor=#D9D9D9;strokeColor=#000000;strokeWidth=2;` |
| Emphasis box | `fillColor=#4D4D4D;strokeColor=#000000;fontColor=#FFFFFF;` |
| Hatched box | `sketch=1;fillStyle=hachure;hachureGap=8;jiggle=0;` |
| Decision | `shape=rhombus;fillColor=#FFFFFF;strokeWidth=3;` |
| Primary connector | `strokeColor=#000000;strokeWidth=3;` |
| Dashed connector | `strokeColor=#000000;strokeWidth=2;dashed=1;dashPattern=8 8;` |

### Sketch Mode (Napkin)

| Preset | Key Style Properties |
|--------|---------------------|
| Standard box | `fillColor=none;strokeColor=#333333;strokeWidth=1;fontSize=11;` |
| Header box | `fillColor=none;strokeColor=#333333;strokeWidth=1;fontSize=14;fontStyle=1;` |
| Group | `fillColor=none;strokeColor=#AAAAAA;dashed=1;fontSize=9;fontStyle=2;` |
| Note | `strokeColor=none;fontSize=9;fontColor=#999999;fontStyle=2;` |
| Primary connector | `strokeColor=#333333;strokeWidth=1;` |
