"""History migration must not hide scientific-source changes behind snapshots."""
import hashlib
import json
import pytest
import check_history as history


def fixture(tmp_path,monkeypatch):
    entries=['README.md','DISCOVERY.md','QUICKSTART.md','AGENTS.md','discover.json','discover/catalog.json','discover/priority-log.md']
    archived={}
    for name in entries:
        snapshot='research/program-v2-20261021/historical-entry/'+name
        path=tmp_path/snapshot;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('old '+name)
        archived[name]={'snapshot':snapshot,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    code=tmp_path/'src/science.py';code.parent.mkdir();code.write_text('original scientific source')
    manifest=tmp_path/'research/example-20261021/manifest.json';manifest.parent.mkdir()
    manifest.write_text(json.dumps({'files':{'README.md':archived['README.md']['sha256'],'src/science.py':hashlib.sha256(code.read_bytes()).hexdigest()}}))
    migration=tmp_path/'migration.json';migration.write_text(json.dumps({'archived_entries':archived}))
    monkeypatch.setattr(history,'ROOT',tmp_path);monkeypatch.setattr(history,'MIGRATION',migration);monkeypatch.setattr(history,'PACKAGES',['example'])
    (tmp_path/'README.md').write_text('new program mission')
    return code,migration


def test_entry_revision_passes_but_scientific_change_fails(tmp_path,monkeypatch):
    code,_=fixture(tmp_path,monkeypatch);history.check()
    code.write_text('different scientific source')
    with pytest.raises(ValueError,match='Changed historical evidence'):history.check()


def test_scientific_file_cannot_be_added_to_snapshot_allowlist(tmp_path,monkeypatch):
    _,migration=fixture(tmp_path,monkeypatch)
    data=json.loads(migration.read_text());data['archived_entries']['src/science.py']={}
    migration.write_text(json.dumps(data))
    with pytest.raises(ValueError,match='only declared entry'):history.check()
