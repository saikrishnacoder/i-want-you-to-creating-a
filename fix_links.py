import os

base = os.path.dirname(os.path.abspath(__file__))

html_files = []
for root, dirs, files in os.walk(base):
    if '.git' in dirs:
        dirs.remove('.git')
    for f in files:
        if f.endswith('.html'):
            html_files.append(os.path.join(root, f))

old_str = 'href="contact.html#form"'
new_str = 'href="javascript:void(0)" class="consult-trigger"'

total = 0
for path in html_files:
    rel = os.path.relpath(path, base)
    try:
        with open(path, 'r', encoding='latin-1') as fh:
            content = fh.read()
    except:
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                content = fh.read()
        except:
            continue

    count = content.count(old_str)
    if count > 0:
        new_content = content.replace(old_str, new_str)
        try:
            with open(path, 'w', encoding='latin-1') as fh:
                fh.write(new_content)
        except:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(new_content)
        print(f'{rel}: {count} links updated')
        total += count

print(f'\nTotal: {total} links updated across {len(html_files)} files')
