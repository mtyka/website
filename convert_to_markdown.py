#!/usr/bin/env python3
"""
Convert _projects/*.html bodies to Markdown.
Keeps <img> and <iframe> tags verbatim; converts text markup to Markdown.
Run with --dry-run to preview without writing.
"""

import os, re, sys

DRY_RUN = '--dry-run' in sys.argv

# Divs whose open+close tags are stripped (content kept)
STRIP_DIV_CLASSES = {'desctext', 'imagebox', 'videobox'}

def strip_wrapper_divs(body):
    """Remove open/close tags for divs we're stripping, tracking nesting."""
    lines = body.split('\n')
    out = []
    # Stack entries: ('strip'|'keep', class_str)
    stack = []

    open_div  = re.compile(r'^\s*<div(\s[^>]*)?>',  re.I)
    close_div = re.compile(r'^\s*</div\s*>',         re.I)
    class_re  = re.compile(r'class=["\']([^"\']*)["\']', re.I)

    for line in lines:
        om = open_div.match(line)
        cm = close_div.match(line)

        if om:
            attrs = om.group(1) or ''
            cm2 = class_re.search(attrs)
            classes = set(cm2.group(1).split()) if cm2 else set()
            if classes & STRIP_DIV_CLASSES and classes <= STRIP_DIV_CLASSES | {'desctext','image'}:
                # Only strip if EVERY class is one we own (so <div class="image"> is kept)
                if classes <= STRIP_DIV_CLASSES:
                    stack.append('strip')
                    continue   # skip the opening tag
                else:
                    stack.append('keep')
            else:
                stack.append('keep')
            out.append(line)
        elif cm:
            if stack:
                kind = stack.pop()
                if kind == 'strip':
                    continue   # skip the closing tag
            out.append(line)
        else:
            out.append(line)

    return '\n'.join(out)


def convert_body(body):
    # 1. Strip wrapper divs
    body = strip_wrapper_divs(body)

    # 2. <center> wrappers
    body = re.sub(r'<center\s*>(.*?)</center\s*>', r'\1', body, flags=re.I|re.S)

    # 3. Bold+italic combined: <i><b>…</b></i> or <b><i>…</i></b>
    body = re.sub(r'<i\s*><b\s*>(.*?)</b\s*></i\s*>', r'***\1***', body, flags=re.I|re.S)
    body = re.sub(r'<b\s*><i\s*>(.*?)</i\s*></b\s*>', r'***\1***', body, flags=re.I|re.S)

    # 4. Bold / italic
    body = re.sub(r'<b\s*>(.*?)</b\s*>', r'**\1**', body, flags=re.I|re.S)
    body = re.sub(r'<i\s*>(.*?)</i\s*>', r'*\1*',   body, flags=re.I|re.S)

    # 5. Links (not inside img/iframe src attrs — those are kept verbatim anyway)
    body = re.sub(r'<a\s+href=["\']([^"\']*)["\'][^>]*>(.*?)</a\s*>',
                  lambda m: f'[{m.group(2).strip()}]({m.group(1)})',
                  body, flags=re.I|re.S)

    # 6. List items and list wrappers
    body = re.sub(r'<li\s*>(.*?)</li\s*>', lambda m: f'- {m.group(1).strip()}', body, flags=re.I|re.S)
    body = re.sub(r'</?ul\s*>', '', body, flags=re.I)

    # 7. <hr> → ---
    body = re.sub(r'\s*<hr\s*/?>\s*', '\n\n---\n\n', body, flags=re.I)

    # 8. <br> variants → paragraph break
    body = re.sub(r'\s*<br\s*/?>\s*', '\n\n', body, flags=re.I)

    # 9. HTML entities for common chars (unescape for cleaner Markdown text)
    body = body.replace('&quot;', '"')
    body = body.replace('&#39;',  "'")
    body = body.replace('&amp;',  '&')
    body = body.replace('&lt;',   '<')
    body = body.replace('&gt;',   '>')

    # 10. Collapse 3+ blank lines → 2
    body = re.sub(r'\n{3,}', '\n\n', body)

    return body.strip()


def split_front_matter(text):
    """Return (front_matter_str, body_str). front_matter includes the --- delimiters."""
    if not text.startswith('---'):
        return '', text
    end = text.index('---', 3)
    fm = text[:end + 3]
    body = text[end + 3:]
    return fm, body


def process_file(path):
    with open(path) as f:
        text = f.read()

    fm, body = split_front_matter(text)
    new_body = convert_body(body)
    result = fm + '\n\n' + new_body + '\n'

    md_path = path.replace('.html', '.md')

    if DRY_RUN:
        print(f'\n{"="*60}')
        print(f'FILE: {path} → {md_path}')
        print('--- BODY BEFORE ---')
        print(body[:800])
        print('--- BODY AFTER ---')
        print(new_body[:800])
    else:
        with open(md_path, 'w') as f:
            f.write(result)
        os.remove(path)
        print(f'Converted: {path} → {md_path}')


def main():
    proj_dir = '_projects'
    files = sorted(f for f in os.listdir(proj_dir) if f.endswith('.html'))
    print(f'{"DRY RUN — " if DRY_RUN else ""}Converting {len(files)} files...')
    for fname in files:
        process_file(os.path.join(proj_dir, fname))
    print(f'\nDone. {len(files)} files {"previewed" if DRY_RUN else "converted"}.')


if __name__ == '__main__':
    main()
