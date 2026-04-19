#!/usr/bin/env python3
"""
Migrate art projects from index.html into individual Jekyll _projects/*.html files.
"""

import os
import re

with open("index.html", "r", encoding="utf-8") as f:
    raw = f.read()


def find_tag_end(html, start):
    """Given position of '<' of an opening tag, find the position after its
    matching closing tag. Handles nested same-tag elements."""
    m = re.match(r'<(\w+)', html[start:])
    if not m:
        return start + 1
    tagname = m.group(1).lower()
    void_tags = {'img','br','hr','input','meta','link','source','track',
                 'wbr','area','col','embed','param'}
    if tagname in void_tags:
        return html.index('>', start) + 1

    # Find end of opening tag to start searching AFTER it
    open_tag_end = html.index('>', start) + 1

    depth = 1  # we are inside the opening tag
    pos = open_tag_end
    open_pat = re.compile(r'<' + tagname + r'(\s|>|/)', re.IGNORECASE)
    close_pat = re.compile(r'</' + tagname + r'\s*>', re.IGNORECASE)

    while pos < len(html):
        om = open_pat.search(html, pos)
        cm = close_pat.search(html, pos)
        if cm is None:
            break
        if om is not None and om.start() < cm.start():
            depth += 1
            pos = om.end()
        else:
            depth -= 1
            if depth == 0:
                return cm.end()
            pos = cm.end()
    return len(html)


def get_attr(tag_html, attr):
    m = re.search(r'\b' + attr + r'\s*=\s*["\']([^"\']*)["\']', tag_html, re.IGNORECASE)
    return m.group(1) if m else ""


def get_classes(tag_html):
    cls = get_attr(tag_html, "class")
    return cls.split() if cls else []


def get_id(tag_html):
    return get_attr(tag_html, "id")


def find_first_child_text(inner_html, classname):
    """Find text inside first element with given class."""
    pat = re.compile(
        r'<(\w+)[^>]*\bclass\s*=\s*["\'][^"\']*\b' + re.escape(classname) + r'\b[^"\']*["\'][^>]*>',
        re.IGNORECASE)
    m = pat.search(inner_html)
    if not m:
        return ""
    tag_start = m.start()
    tag_end = find_tag_end(inner_html, tag_start)
    open_end = inner_html.index('>', tag_start) + 1
    inner = inner_html[open_end:tag_end]
    close_m = re.search(r'</\w+\s*>\s*$', inner)
    if close_m:
        inner = inner[:close_m.start()]
    return inner.strip()


def strip_html_tags(text):
    return re.sub(r'<[^>]+>', '', text).strip()


def find_coverimg_src(inner_html):
    m = re.search(r'<img[^>]*\bclass\s*=\s*["\'][^"\']*\bcoverimg\b[^"\']*["\'][^>]*>',
                  inner_html, re.IGNORECASE)
    if not m:
        return ""
    return get_attr(m.group(0), "src")


def extract_body(inner_html):
    """Return everything after the last of desctitle/descmedia/descyear/coverimg elements."""
    last_end = 0
    for classname in ['desctitle', 'descmedia', 'descyear']:
        pat = re.compile(
            r'<(\w+)[^>]*\bclass\s*=\s*["\'][^"\']*\b' + re.escape(classname) + r'\b[^"\']*["\'][^>]*>',
            re.IGNORECASE)
        for m in pat.finditer(inner_html):
            end = find_tag_end(inner_html, m.start())
            if end > last_end:
                last_end = end
    # Also skip the coverimg <img>
    coverimg_pat = re.compile(r'<img[^>]*\bcoverimg\b[^>]*>', re.IGNORECASE)
    for m in coverimg_pat.finditer(inner_html):
        end = m.end()
        if end > last_end:
            last_end = end
    if last_end == 0:
        return inner_html
    return inner_html[last_end:].strip()


def yaml_str(s):
    if not s:
        return '""'
    escaped = s.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped}"'


# ---------------------------------------------------------------------------
# Find <div id="projects"> and extract its inner content
# ---------------------------------------------------------------------------
projects_m = re.search(r'<div\s+id\s*=\s*["\']projects["\'][^>]*>', raw, re.IGNORECASE)
if not projects_m:
    raise RuntimeError("Could not find <div id='projects'>")

projects_div_start = projects_m.start()
projects_div_end = find_tag_end(raw, projects_div_start)
projects_inner = raw[projects_m.end():projects_div_end]

# Strip final </div>
close_m = re.search(r'\s*</div\s*>\s*$', projects_inner)
if close_m:
    projects_inner = projects_inner[:close_m.start()]

# ---------------------------------------------------------------------------
# Walk top-level <div class="project ..."> children
# ---------------------------------------------------------------------------
os.makedirs("_projects", exist_ok=True)

order = 0
pos = 0
project_pat = re.compile(
    r'<div\b[^>]*\bclass\s*=\s*["\'][^"\']*\bproject\b[^"\']*["\'][^>]*>',
    re.IGNORECASE)

while pos < len(projects_inner):
    m = project_pat.search(projects_inner, pos)
    if not m:
        break

    tag_open = m.group(0)
    div_start = m.start()
    div_end = find_tag_end(projects_inner, div_start)

    classes = get_classes(tag_open)
    pid = get_id(tag_open)

    # Skip bio, contact, topmenu
    if pid in ('bio', 'contact') or 'topmenu' in classes:
        pos = div_end
        continue

    if not pid:
        pos = div_end
        continue

    # Inner HTML of the project div (strip outer closing </div>)
    open_tag_end = projects_inner.index('>', div_start) + 1
    inner = projects_inner[open_tag_end:div_end]
    close_m2 = re.search(r'\s*</div\s*>\s*$', inner)
    if close_m2:
        inner = inner[:close_m2.start()]

    # Extract front matter fields
    title = strip_html_tags(find_first_child_text(inner, 'desctitle'))
    media = strip_html_tags(find_first_child_text(inner, 'descmedia'))
    year  = strip_html_tags(find_first_child_text(inner, 'descyear'))
    cover_image = find_coverimg_src(inner)
    tags = [c for c in classes if c != 'project']
    body = extract_body(inner)

    tags_yaml = "[" + ", ".join(tags) + "]" if tags else "[]"

    front_matter = (
        f"---\n"
        f"title: {yaml_str(title)}\n"
        f"media: {yaml_str(media)}\n"
        f"year: {yaml_str(year)}\n"
        f"cover_image: \"{cover_image}\"\n"
        f"tags: {tags_yaml}\n"
        f"order: {order}\n"
        f"render_with_liquid: false\n"
        f"---\n"
    )

    out_path = f"_projects/{pid}.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(front_matter)
        f.write("\n")
        f.write(body)
        f.write("\n")

    print(f"[{order:3d}] {pid:35s}  tags={tags_yaml}")
    order += 1
    pos = div_end

print(f"\nDone. {order} project files written to _projects/")
