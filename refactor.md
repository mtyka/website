# Jekyll Refactoring Plan

## Overview

The core insight is that `all.js` needs **zero changes** — it works purely by querying `.project`
divs in the DOM. If Jekyll generates the exact same DOM, the existing JS routing, filtering, and
lazy-loading continues to work identically. The refactoring is entirely about moving content into
structured files while using Liquid templates to regenerate the same HTML at build time.

---

## Target Directory Structure

```
/
├── _config.yml
├── _layouts/
│   └── main.html             # Full page shell (replaces everything in index.html)
├── _includes/
│   ├── styles.html           # The entire <style> block
│   ├── header.html           # The #header div (nav links)
│   ├── analytics.html        # The Google Analytics <script> block
│   ├── bio.html              # Contents of <div id="bio">
│   └── contact.html          # Contents of <div id="contact">
├── _projects/                # One file per art project
│   ├── ubiquitin.html
│   ├── tears.html
│   └── ... (~60 files)
├── _data/
│   └── topmenu.yml           # The 6 top-level category cards
├── index.html                # Minimal: just front matter pointing to layout
├── all.js                    # Unchanged
├── pics/                     # Unchanged (miketyka.png, mike.jpg)
└── projects/                 # Unchanged (all image assets)
```

---

## Step 1 — `_config.yml`

```yaml
title: Mike Tyka
url: "http://www.miketyka.com"
permalink: /

collections:
  projects:
    output: false      # No individual project pages generated
    sort_by: order     # Preserve current display order
```

The `sort_by: order` is critical — it matches the current DOM order, which determines menu
sequencing in each category.

---

## Step 2 — `index.html` (new, minimal)

```yaml
---
layout: main
---
```

That's the entire file. Everything lives in the layout.

---

## Step 3 — `_layouts/main.html`

This replaces the current `index.html`, broken into logical sections:

```html
<!DOCTYPE html><html>
<head>
<meta name="viewport" content="width=device-width, ...">
<script src="all.js"></script>
{% include analytics.html %}
{% include styles.html %}
</head>
<body>
  <div id="reel" class="reel" onload="interpretUrlState()">
    {% include header.html %}

    <div id="spinner"></div>

    <div id="toplevel">
      <hr>
      <div id="topleveltable"></div>
      <hr>
    </div>

    <div id="menu" class="hidden">
      <hr>
      <div id="menutable"></div>
      <hr>
    </div>

    <div id="projects">

      {% for project in site.projects %}
      <div class="project {{ project.tags | join: ' ' }}" id="{{ project.slug }}">
        <img src="{{ project.cover_image }}" class="coverimg hidden">
        <div class="desctitle">{{ project.title }}</div>
        <div class="descmedia">{{ project.media }}</div>
        <div class="descyear">{{ project.year }}</div>
        {{ project.content }}
      </div>
      {% endfor %}

      <div class="project" id="bio">
        {% include bio.html %}
      </div>

      <div class="project" id="contact">
        {% include contact.html %}
      </div>

      {% for item in site.data.topmenu %}
      <div class="project topmenu" id="{{ item.id }}">
        <div class="crop">
          <img class="image coverimg" src="{{ item.cover_image }}">
        </div>
        <div class="descmedia">{{ item.label }}</div>
      </div>
      {% endfor %}

    </div><!-- #projects -->

    <div class="hidden">
      <div id="defaultbox" class="box">
        <div class="crop"><img class="coverimg" src=""></div>
      </div>
    </div>

  </div><!-- #reel -->
</body>
</html>
```

The `{{ project.content }}` outputs the file body verbatim. `{{ project.slug }}` is Jekyll's
built-in filename-without-extension, eliminating the need for a redundant `project_id` field.

---

## Step 4 — `_data/topmenu.yml`

```yaml
- id: molecule
  label: Molecular Sculpture
  cover_image: projects/ubiquitin.jpg
- id: deepdream
  label: "AI: Deepdream"
  cover_image: projects/neuralart.jpg
- id: faces
  label: AI Portraits
  cover_image: projects/faces.jpg
- id: sculpture
  label: Sculpture
  cover_image: projects/sculpture.jpg
- id: animation
  label: AI Animation
  cover_image: projects/eons/stillframe.jpg
- id: collaborations
  label: Collaborations
  cover_image: projects/groovikscube/cube15_big.jpg
```

---

## Step 5 — `_projects/` file format

Each project becomes a `.html` file (`.html` rather than `.md` to guarantee the body is never
Markdown-processed — iframes, `data-src` attributes, and HTML entities pass through unchanged).

### Front matter fields

| Field        | Notes |
|--------------|-------|
| `title`      | The `.desctitle` text |
| `media`      | The `.descmedia` text (materials/medium) |
| `year`       | The `.descyear` text |
| `cover_image`| Path to thumbnail image used in menu cards |
| `tags`       | YAML list of CSS class names (e.g. `[copper, molecule]`) |
| `order`      | Integer controlling display order within category menus |

### Body

Raw HTML of everything that currently appears inside the project `<div>` after the `descyear`
div — the `imagebox`, `desctext`, embedded iframes, and `<hr>` separators, exactly as they
appear today.

### Example — `_projects/ubiquitin.html`

```yaml
---
title: '"Angel of Death" - Ubiquitin'
media: "Copper, Steel - 9\"x9\"x16\""
year: "2011"
cover_image: projects/ubiquitin.jpg
tags: [copper, molecule]
order: 1
---

<div class="imagebox">
  <hr>
  <img data-src="projects/ubiquitin/ubiquitin_5_big.jpg" class="image">
  <div class="desctext image">
    <img data-src="projects/ubiquitin/ubiquitin_6_big.jpg" class="image wide">
    <br>Life is a dynamic equilibrium...
  </div>
  <hr>
  <img data-src="projects/ubiquitin/ubiquitin_3_big.jpg" class="image">
  <img data-src="projects/ubiquitin/ubiquitin_7_big.jpg" class="image">
  <hr>
</div>
```

### Example — `_projects/eons.html` (with iframes)

```yaml
---
title: EONS
media: "Neural net, video animation"
year: "2019"
cover_image: projects/eons/stillframe.jpg
tags: [digital, animation]
order: 51
---

<div class="imagebox">
  <iframe src="https://player.vimeo.com/video/334026838?..." ...></iframe>
  ...
</div>
```

The `.html` extension on project files means Jekyll renders them through Liquid by default.
Add `render_with_liquid: false` to the front matter of any project file that happens to
contain curly braces in its text content.

---

## Step 6 — `_includes/` files

- **`_includes/styles.html`** — cut-and-paste the entire `<style>` block from `index.html`. No changes.
- **`_includes/analytics.html`** — cut-and-paste the Google Analytics `<script>` block. No changes.
- **`_includes/header.html`** — cut-and-paste the `<div id="header">` block. No changes.
- **`_includes/bio.html`** — the inner HTML of `<div id="bio">`. No changes.
- **`_includes/contact.html`** — the inner HTML of `<div id="contact">`. No changes.

---

## Step 7 — Migration Execution

The mechanical migration is done by a Python script (`migrate.py`) that:

1. Parses `index.html` with BeautifulSoup
2. Finds every `<div class="project ...">` that is a direct child of `<div id="projects">`
3. Skips `id="bio"`, `id="contact"`, and `class="topmenu"` divs (handled separately)
4. For each project div:
   - Extracts `id` → filename slug
   - Extracts classes → `tags` list (minus `project` itself)
   - Extracts `.desctitle`, `.descmedia`, `.descyear`, `.coverimg[src]`
   - Assigns `order` = its index in the file
   - Writes front matter + body as `_projects/<id>.html`

---

## Edge Cases to Handle Manually

| Project | Issue |
|---------|-------|
| `kiss` | `desctitle`, `descmedia`, `descyear` are nested inside `.desctext` instead of being siblings |
| `whitechen` | Uses a bare `<div>` instead of `<div class="imagebox">` |
| `savior` | `.desctext` contains an inline `<img>` that is also lazy-loaded |
| `blingee`, `butoh` | YouTube iframes mixed with regular images |
| `groovikscube`, `usandthem` | YouTube iframes, `videobox` class |
| Projects with `{{ }}` in text | Add `render_with_liquid: false` to front matter |

---

## What Does NOT Change

- `all.js` — zero modifications required
- All CSS — moved to `_includes/styles.html`, not edited
- `projects/` image directory — untouched
- `pics/` directory — untouched
- URL scheme (`?p=id`, `?s=classname`) — identical since HTML structure is identical
- The visual design — pixel-identical, since the CSS and all class names are preserved exactly

---

## Build and Deploy

```bash
bundle exec jekyll build   # outputs to _site/
```

The `_site/index.html` should be diff-comparable to the original `index.html` (modulo
whitespace and attribute ordering). A diff between the two is the recommended verification
step before going live.
