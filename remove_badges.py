import os, re

base = os.path.dirname(os.path.abspath(__file__))

# Remove ccv2-highlight-badge spans from coaches.html
path = os.path.join(base, 'coaches.html')
with open(path, 'r', encoding='latin-1') as f:
    content = f.read()

# Remove the badge spans
content = re.sub(r'\s*<span class="ccv2-highlight-badge"[^>]*>.*?</span>', '', content)

with open(path, 'w', encoding='latin-1') as f:
    f.write(content)

print(f"Removed ccv2-highlight-badge spans from coaches.html")

# Also check index.html for coach-hover-tag
path2 = os.path.join(base, 'index.html')
if os.path.exists(path2):
    with open(path2, 'r', encoding='latin-1') as f:
        content2 = f.read()
    if 'coach-hover-tag' in content2:
        content2 = re.sub(r'\s*<span class="coach-hover-tag"[^>]*>.*?</span>', '', content2)
        with open(path2, 'w', encoding='latin-1') as f:
            f.write(content2)
        print(f"Removed coach-hover-tag spans from index.html")
    else:
        print(f"No coach-hover-tag found in index.html")
