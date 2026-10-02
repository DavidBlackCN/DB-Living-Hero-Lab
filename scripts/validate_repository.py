"""Check curated doc links, script imports, and the frozen runtime asset set."""
from pathlib import Path
import ast, hashlib, json, re
ROOT = Path(__file__).resolve().parents[1]
expected = json.loads((ROOT/'sources/runtime-assets.sha256.json').read_text(encoding='utf-8-sig'))
actual = {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'public/assets/hero').rglob('*.png')}
assert actual == expected, 'Runtime asset set or bytes changed; review the intended visual change before updating the manifest'
errors=[]
for p in [ROOT/'README.md',ROOT/'AGENTS.md',*(ROOT/'docs').rglob('*.md')]:
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8-sig')):
  link=link.split('#')[0].strip('<>')
  if not link or re.match(r'[a-zA-Z]+:',link):continue
  if not (p.parent/link).resolve().exists():errors.append(f'{p.relative_to(ROOT)}: {link}')
for p in (ROOT/'scripts').glob('*.py'):
 tree=ast.parse(p.read_text(encoding='utf-8-sig'))
 for node in ast.walk(tree):
  if isinstance(node,ast.ImportFrom) and node.module and node.module.startswith(('validate_','audit_','capture_','browser_support','frozen_baseline')):
   if not (ROOT/'scripts'/f'{node.module}.py').exists():errors.append(f'{p.name}: missing {node.module}')
assert not errors, '\n'.join(errors)
print(f'Passed: {len(actual)} unchanged runtime assets, local doc links and script imports')
