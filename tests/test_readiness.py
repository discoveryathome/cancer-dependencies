import copy,json,sys,tempfile
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import readiness as r
from reserve_cohort import components
def test_positive_and_incomplete_or_forged_candidates():
    original=json.loads((r.OUT/'candidates/SMARCA2.json').read_text());assert r.verify(r.OUT/'candidates/SMARCA2.json')['valid']
    mutations=[]
    bad=copy.deepcopy(original);bad['folds'].pop();mutations.append(bad)
    bad=copy.deepcopy(original);bad['folds'][0]['test_ids']=bad['folds'][1]['test_ids'];mutations.append(bad)
    bad=copy.deepcopy(original);bad['metrics']['mse']=0.;mutations.append(bad)
    bad=copy.deepcopy(original);bad['folds'][0]['model']['features'][0]='y:SMARCA2';mutations.append(bad)
    bad=copy.deepcopy(original);bad['folds'][0]['model']['scale'][0]=0.;mutations.append(bad)
    bad=copy.deepcopy(original);bad['folds'][0]['train_groups']=bad['folds'][1]['train_groups'];mutations.append(bad)
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'bad.json'
        for bad in mutations:
            p.write_text(json.dumps(bad))
            with pytest.raises(ValueError):r.verify(p)
def test_development_excludes_historical_final():
    _,frame,lock=r.load_development();assert len(frame)==773
    assert not set(frame.group)&set(lock['excluded_final_groups'])
    from prepare_development import main
    main()  # Exact CSV cells, not a tolerance-based numerical equivalence claim.
def test_training_fold_refit_rejects_consistently_rescored_forgery():
    p=r.OUT/'starter.json';assert r.verify(p,refit=True)['valid']
    d=json.loads(p.read_text());d['folds'][0]['model']['intercept']+=.01
    _,frame,_=r.load_development();ref=json.loads((r.OUT/'baselines/SMARCA2.json').read_text())
    d['metrics']=r.summarize(frame,'SMARCA2',d['folds'],ref['folds'])
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'bad.json';path.write_text(json.dumps(d));assert r.verify(path)['valid']
        with pytest.raises(ValueError,match='refit differs'):r.verify(path,refit=True)
def test_identity_union_catches_transitive_aliases_and_empty_values():
    rows=[{'ModelID':'old','RRID':'r1','COSMICID':'123.0'}, {'ModelID':'new','COSMICID':'123','PatientID':'p1'}, {'ModelID':'new2','PatientID':'p1'}, {'ModelID':'separate','RRID':''}]
    c=components(rows);assert c[0]==c[1]==c[2] and c[3]!=c[0]
