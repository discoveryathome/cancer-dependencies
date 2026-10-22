"""A short, read-only newcomer check."""
import importlib.metadata,json,pathlib,platform,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
print('Python',platform.python_version(),'on',platform.system(),platform.machine())
for name in ['numpy','pandas','scipy','scikit-learn','jsonschema','pytest']:
    try: print(name,importlib.metadata.version(name))
    except importlib.metadata.PackageNotFoundError: raise SystemExit('Missing dependency: '+name)
for name in ['data/panel/primary.csv','data/panel/sanger.csv','data/source-lock.json','config/benchmark.json']:
    p=ROOT/name
    if not p.exists():raise SystemExit('Missing file: '+name)
    print(name,p.stat().st_size,'bytes')
print('GPU not required. Raw downloads not required for compact-panel evaluation.')
print('Authoritative scope: discover/frontier.json. Open to donated sessions; maintainer @Mister-Meeseeks.')
