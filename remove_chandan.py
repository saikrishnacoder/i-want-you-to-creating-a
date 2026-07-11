import os, re

base = os.path.dirname(os.path.abspath(__file__))

# 1. Remove from coaches.html
path = os.path.join(base, 'coaches.html')
with open(path, 'r', encoding='latin-1') as f:
    content = f.read()
content = re.sub(
    r'<article class="coach-card-v2"[^>]*data-coach-id="chandan-mondal">.*?</article>',
    '', content, flags=re.DOTALL
)
with open(path, 'w', encoding='latin-1') as f:
    f.write(content)
print('Removed Chandan Mondal from coaches.html')

# 2. Remove from app.js coach data array
path = os.path.join(base, 'app.js')
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
content = re.sub(r'\s*\{ name: "Chandan Mondal"[^}]*\},?\n?', '\n', content)
content = re.sub(r'\s*"chandan-mondal": \{[^}]*\},?\n?', '\n', content)
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Removed Chandan Mondal from app.js')

# 3. Remove from index.html minds cards
path = os.path.join(base, 'index.html')
with open(path, 'r', encoding='latin-1') as f:
    content = f.read()
# Remove minds-card blocks containing Chandan - they are <div class="minds-card">...</div>...</div>
content = re.sub(
    r'(<div class="minds-card">\s*<div class="minds-card-avatar">.*?</h4>\s*</div>\s*</div>)',
    lambda m: '' if 'Chandan' in m.group(0) else m.group(0),
    content, flags=re.DOTALL
)
with open(path, 'w', encoding='latin-1') as f:
    f.write(content)
print('Removed Chandan Mondal from index.html')

# 4. Delete profile HTML
profile = os.path.join(base, 'coaches', 'chandan-mondal.html')
if os.path.exists(profile):
    os.remove(profile)
    print('Deleted coaches/chandan-mondal.html')
else:
    print('Profile file not found')
