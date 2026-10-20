import pathlib
import pandas as pd
ROOT=pathlib.Path(__file__).resolve().parents[1]

def test_cancer_eligibility_and_separate_assays():
    metadata=pd.read_csv(ROOT/'data/model-metadata.csv').set_index('ModelID')
    primary=pd.read_csv(ROOT/'data/panel/primary.csv'); sanger=pd.read_csv(ROOT/'data/panel/sanger.csv')
    for frame in [primary,sanger]:
        m=metadata.loc[frame.model_id]
        assert m.OncotreePrimaryDisease.notna().all()
        assert not (m.OncotreePrimaryDisease=='Non-Cancerous').any()
        assert m.EngineeredModel.isna().all()
        assert not frame.group.duplicated().any()
    assert set(primary.library)=={'Avana'}
    assert set(sanger.library)=={'KY'}
    assert not set(primary.group)&set(sanger.loc[sanger.partition=='external','group'])
    assert not set(primary.loc[primary.partition=='development','group'])&set(primary.loc[primary.partition=='final','group'])
