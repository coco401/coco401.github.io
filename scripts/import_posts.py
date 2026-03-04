from pathlib import Path
import yaml

src = Path('/tmp/coco-extracted-posts')
repo = Path('/Users/coco/Library/Mobile Documents/com~apple~CloudDocs/Code/coco401.github.io')
dst = repo / 'content' / 'posts'
dst.mkdir(parents=True, exist_ok=True)

for f in sorted(src.glob('*.md')):
    text = f.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        continue

    parts = text.split('---\n', 2)
    if len(parts) < 3:
        continue

    fm_text = parts[1]
    body = parts[2].lstrip('\n')
    data = yaml.safe_load(fm_text) or {}

    clean = {}
    if data.get('title'):
        clean['title'] = data['title']
    if data.get('date'):
        clean['date'] = data['date']
    tags = data.get('tags')
    if tags:
        clean['tags'] = tags

    out = '---\n' + yaml.safe_dump(clean, allow_unicode=True, sort_keys=False).strip() + '\n---\n\n' + body.strip() + '\n'
    out_path = dst / f.name
    out_path.write_text(out, encoding='utf-8')
    print('imported', out_path.name)

index_md = repo / 'content' / 'index.md'
index_md.write_text(
    '---\n'
    'title: 春夏秋冬\n'
    '---\n\n'
    '# 春夏秋冬\n\n'
    '已迁移到 Quartz 4。\n\n'
    '文章列表见 [posts](./posts)。\n',
    encoding='utf-8'
)
print('wrote index.md')
