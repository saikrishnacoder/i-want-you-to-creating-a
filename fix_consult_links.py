import os, re

base = os.path.dirname(os.path.abspath(__file__))

html_files = []
for root, dirs, files in os.walk(base):
    if '.git' in dirs:
        dirs.remove('.git')
    for f in files:
        if f.endswith('.html'):
            html_files.append(os.path.join(root, f))

# Replace consult-trigger links with book-consultation.html
total = 0
for path in html_files:
    rel = os.path.relpath(path, base)
    if rel == 'book-consultation.html':
        continue
    try:
        with open(path, 'r', encoding='latin-1') as fh:
            content = fh.read()
    except:
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                content = fh.read()
        except:
            continue

    orig = content
    
    # Replace <a ... href="javascript:void(0)" class="consult-trigger"> with <a ... href="book-consultation.html">
    # Handle: class="primary-button consult-trigger" and class="consult-trigger" patterns
    
    # Pattern 1: class="primary-button" href="javascript:void(0)" class="consult-trigger"
    content = content.replace(
        'href="javascript:void(0)" class="consult-trigger"',
        'href="book-consultation.html"'
    )
    
    # Pattern 2: class="consult-trigger" href="javascript:void(0)"  
    content = content.replace(
        'class="consult-trigger" href="javascript:void(0)"',
        'href="book-consultation.html"'
    )
    
    # Pattern 3: class="ccv2-book-btn" href="javascript:void(0)" class="consult-trigger"
    # Already handled by pattern 1
    
    # Pattern 4: href='javascript:void(0)' class='consult-trigger' (single quotes)
    content = content.replace(
        "href='javascript:void(0)' class='consult-trigger'",
        "href='book-consultation.html'"
    )
    
    # Remove consult-trigger class from links that now point to the page
    content = content.replace(' class="consult-trigger"', '')
    content = content.replace(" class='consult-trigger'", '')
    
    if content != orig:
        count = orig.count('consult-trigger')
        try:
            with open(path, 'w', encoding='latin-1') as fh:
                fh.write(content)
        except:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(content)
        print(f'{rel}: {count} links updated')
        total += count

print(f'\nTotal: {total} links updated')
