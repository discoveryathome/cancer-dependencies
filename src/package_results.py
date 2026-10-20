"""Complete Discovery@Home package metadata without changing scientific scores."""
import json,pathlib,subprocess
from core import dumps,sha256
ROOT=pathlib.Path(__file__).resolve().parents[1]

def main():
    commit=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    for run,scope in [('initial','Reproduce compact biomarker prediction on a fixed held-out cancer-cell-line benchmark.'),
                      ('contributor-trial','Test early contributor progress, biological priors, home-PC feasibility and featured-pilot suitability.')]:
        folder=ROOT/'research'/run;p=folder/'VERIFY.json';v=json.loads(p.read_text())
        v['commands']=[['.venv/bin/python','src/verify.py',str(p.relative_to(ROOT))],['.venv/bin/python','src/replay_fit.py']]
        v['dependency_pins']={'requirements.lock':sha256(ROOT/'requirements.lock'),'python':'3.12'}
        v['timeout_seconds']={'prediction_verifier':180,'refit_verifier':600,'full_benchmark':3600}
        p.write_text(dumps(v))
        sources={'base_commit':commit,'inputs':v['inputs'],
          'git_blobs':{name:subprocess.check_output(['git','-C',str(ROOT),'hash-object',name],text=True).strip() for name in v['inputs']},
          'artifact_sha256':{p.name:sha256(p) for p in folder.iterdir() if p.suffix in ['.csv','.json'] and p.name not in ['SOURCES.json','TASK.json']}}
        (folder/'SOURCES.json').write_text(dumps(sources))
        task={'card':'none','catalog_revision':1,'scope':scope,'scope_status':'unchanged','outcome':'partial' if run=='contributor-trial' else 'verification',
          'evidence_level':'author-checked','not_checked':['Independent reviewer confirmation','Novel biological mechanism','Clinical relevance or normal-cell selectivity','Fresh contributor without author knowledge'],
          'next_questions':[{'question':'Can an independent contributor reproduce and improve the development result?',
             'why_it_matters':'The setup author is also the trial author; newcomer feasibility and general intelligence benefit remain uncertain.',
             'first_step':'.venv/bin/python src/contribute.py run --target SMARCA2 --artifact research/my-attempt/RESULT.json','blocked_by':'Maintainer consent required before donor intake.'},
            {'question':'Does a candidate survive a genuinely new validation cohort?',
             'why_it_matters':'The public initial test cannot remain independent under repeated adaptive search.',
             'first_step':'Audit a newly released, licensed screen cohort for all identity and source overlap before revealing outcomes.','blocked_by':'Curator ownership and a preregistered validation release.'}],
          'credit':['Codex agent: setup, code and self-run trial; not independent verification.','DepMap, Broad (2024): source data, CC BY 4.0.'],
          'ai_assistance':'Entire implementation and trial performed by the same assistant; no independent sub-agent or human replication.',
          'budget_minutes':60 if run=='contributor-trial' else 0}
        (folder/'TASK.json').write_text(dumps(task))
        text=f'''# {run}: result package

{scope}

Evidence level: author-checked only. Read ../../reports/RESULTS.md for every target,
negative result, complexity and uncertainty, and ../../reports/FEATURED_PILOT_ASSESSMENT.md
for the contributor assessment. Known biological priors are not novel findings.

## Reproduce

From the repository root:

```sh
.venv/bin/python src/verify.py research/{run}/VERIFY.json
.venv/bin/python src/replay_fit.py
```

The first command checks frozen models, complete final cohorts, hashes, predictions and
scores. The second reselects and refits all final baseline and trial models from development.
See ../../README.md for full outer/lineage/null replay commands and limitations.
VERIFY.json records argv commands, input hashes, pins and timeouts; SOURCES.json records
live source hashes and Git blobs. No executable model pickle is loaded.

## Open next questions

See TASK.json. Independent reproduction and fresh-cohort confirmation remain open.
An appointed maintainer must review the evidence before accepting a frontier change or
opening donor intake. The local proposal deliberately has no invented maintainer.

Credit: Codex agent implemented and tested this package. DepMap, Broad (2024),
https://doi.org/10.25452/figshare.plus.25880521.v1 supplied the CC BY 4.0 data.
'''
        (folder/'README.md').write_text(text)
    print('Packaged TASK, SOURCES, VERIFY commands and result READMEs.')
if __name__=='__main__':main()
