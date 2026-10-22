"""One prespecified additive release-bridge sensitivity; Broad is already exposed."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata

from core import dumps, predict, sha256
import transfer_trial as transfer
import expression_bridge as bridge

ROOT, PACKAGE, RUN = bridge.ROOT, bridge.PACKAGE, bridge.RUN


def corrected_predictions(frozen, base, offsets):
    frame = pd.DataFrame(base['rows']).copy()
    genes = frozen['protocol']['predictors']
    if set(offsets) != set(genes) or not np.isfinite(list(offsets.values())).all():
        raise ValueError('Invalid offset panel')
    if len(frame) != 77 or base['excluded'] or not np.isfinite(frame[['expr:'+g for g in genes]].to_numpy()).all():
        raise ValueError('Frozen complete cohort changed')
    for gene in genes:
        frame['expr:'+gene] -= offsets[gene]
    predictions, invariance = {}, {}
    for target in frozen['protocol']['targets']:
        predictions[target], invariance[target] = {}, {}
        for family in transfer.FAMILIES:
            model = frozen['targets'][target]['models'][family]
            y = predict(model, frame)
            predictions[target][family] = y.tolist()
            if family in ['compact_expression_pair', 'strong_expression', 'self_expression']:
                if model['kind'] != 'linear':
                    raise ValueError('Expected frozen linear model')
                before = np.asarray(base['predictions'][target][family])
                difference = y-before
                invariant = np.array_equal(rankdata(before), rankdata(y))
                if not invariant or np.ptp(difference) > 1e-10:
                    raise ValueError('Unexpected rank/constant-shift failure')
                invariance[target][family] = {'ranks_identical':bool(invariant),
                    'prediction_shift':float(np.mean(difference)),
                    'max_shift_deviation':float(np.ptp(difference))}
    return {'rows':frame.to_dict('records'), 'excluded':[], 'predictions':predictions,
            'rank_invariance':invariance,
            'negative_corrected_values':{g:int((frame['expr:'+g]<0).sum()) for g in genes},
            'scale_note':'Offsets map to a model coordinate system; negative corrected numbers are retained, not interpreted as physical negative log2(TPM+1), and no clipping is introduced.'}


def prediction_data(inputs):
    frozen = transfer.load_freeze(RUN)
    audit = bridge.compute(ROOT/'data/raw/robustness-20261021')
    if audit != transfer.read_json(PACKAGE/'audit.json') or not audit['offset_validation']['numerical_gate_passed']:
        raise ValueError('Changed or failed offset audit')
    decision = transfer.read_json(PACKAGE/'decision.json')
    if decision['audit_sha256'] != sha256(PACKAGE/'audit.json'):
        raise ValueError('Decision audit mismatch')
    source = transfer.read_json(ROOT/'research/transfer-results-20261021/source-manifest.json')
    expression = inputs/source['expression_file']
    if sha256(expression) != source['expression_sha256']:
        raise ValueError('Changed organoid expression')
    base = transfer.build_predictions(frozen, expression)
    inherited = transfer.read_json(RUN/'predictions.json')
    if any(base[k] != inherited[k] for k in base):
        raise ValueError('Original predictions no longer reproduce')
    data = corrected_predictions(frozen, base, audit['offsets'])
    data['offsets'] = audit['offsets']
    data['bindings'] = transfer.bind([Path(__file__), ROOT/'src/expression_bridge.py', ROOT/'src/core.py',
        ROOT/'src/transfer_trial.py', PACKAGE/'audit.json', PACKAGE/'protocol.json', PACKAGE/'decision.json',
        RUN/'frozen.json', RUN/'predictions.json', ROOT/'research/transfer-results-20261021/source-manifest.json'])
    data['schema'] = 'additive-bridge-sensitivity-predictions/v1'
    return frozen, base, data, source


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('phase',choices=['predict','score','verify'])
    parser.add_argument('--inputs',type=Path,required=True)
    args=parser.parse_args()
    frozen, base, corrected, source = prediction_data(args.inputs)
    lock = PACKAGE/'predictions.json'
    if args.phase == 'predict':
        transfer.write_new(lock, corrected)
        print('PASS frozen one correction, all77x30 inputs, all12x6 predictions; all36 linear rankings unchanged')
        return
    if transfer.read_json(lock) != corrected:
        raise ValueError('Corrected prediction replay failed')
    response=args.inputs/source['response_file']
    exposure={'predictions_sha256':sha256(lock),'response_sha256':source['response_sha256'],
        'scope':'Same previously exposed Broad77; exploratory only; Sanger untouched'}
    if args.phase == 'score':
        transfer.write_new(PACKAGE/'exposure.json',{'opened_at':transfer.now(),**exposure})
    else:
        recorded=transfer.read_json(PACKAGE/'exposure.json')
        if any(recorded[k]!=v for k,v in exposure.items()):
            raise ValueError('Changed exposure binding')
    if sha256(response)!=source['response_sha256']:
        raise ValueError('Changed responses')
    result={'schema':'additive-bridge-sensitivity-results/v1',
        'uncorrected':transfer.evaluate(frozen,base,response),
        'corrected':transfer.evaluate(frozen,corrected,response),'bindings':exposure}
    if result['uncorrected']['primary'] != result['corrected']['primary']:
        raise ValueError('Unexpected aggregate rank result changed')
    if args.phase == 'verify':
        if result!=transfer.read_json(PACKAGE/'results.json'):
            raise ValueError('Score replay failed')
    else:
        transfer.write_new(PACKAGE/'results.json',result)
    print(dumps({'phase':args.phase,'primary':result['corrected']['primary'],
        'rule_branches':{t:{'before':result['uncorrected']['targets'][t]['rule_branch_support'],
                           'after':r['rule_branch_support']} for t,r in result['corrected']['targets'].items()}}))

if __name__=='__main__': main()
