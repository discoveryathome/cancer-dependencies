"""Render the all-target support audit; no outcomes or extra model selection."""
import os
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / 'setup/matplotlib-cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

result = json.loads((HERE / 'diagnostic.json').read_text())
frozen = json.loads((ROOT / 'research/transfer-trial-20261021/run/frozen.json').read_text())
targets = frozen['protocol']['targets']
fig, ax = plt.subplots(figsize=(10.5, 6.7))
ys = np.arange(len(targets))[::-1]
for i, (y, target) in enumerate(zip(ys, targets)):
    rule = result['rules'][target]
    d = rule['decomposition']
    lo, hi = d['composition_reference_count_interval95']
    ax.plot([lo, hi], [y, y], color='#b2bac4', linewidth=5, solid_capstyle='round',
            label='Composition-only reference: middle 95% of simulations' if i == 0 else None)
    ax.scatter(d['composition_reference_expected_left_count'], y, color='#4b5563', s=28, zorder=3,
               label='Expected using historical expression within each lineage' if i == 0 else None)
    ax.scatter(d['observed_common_left_count'], y, color='#1768ac', marker='D', s=48, zorder=4,
               label='Observed in the 77 organoids' if i == 0 else None)
ax.set_yticks(ys, [f"{t}  ({result['rules'][t]['feature'].removeprefix('expr:')})" for t in targets])
ax.set_xlabel('Models below or equal to the frozen expression threshold (out of 77)')
ax.set_xlim(-2, 79)
ax.set_xticks([0, 15, 30, 45, 60, 77])
ax.grid(axis='x', color='#e4e7ec')
ax.set_axisbelow(True)
ax.spines[['top', 'right', 'left']].set_visible(False)
ax.tick_params(axis='y', length=0)
ax.set_title('Lineage composition does not explain several rule-support failures', loc='left', fontsize=14, pad=18)
ax.legend(loc='upper center', bbox_to_anchor=(.5, -.14), frameon=False, fontsize=9)
fig.text(.02, .02, 'Outcome-free exploratory diagnostic. Reference ranges are unadjusted simulations, not evidence of causality or discovery.', fontsize=8, color='#555')
fig.subplots_adjust(left=.23, right=.97, top=.88, bottom=.25)
fig.savefig(HERE / 'rule-support.png', dpi=160)
fig.savefig(HERE / 'rule-support.svg')
svg = HERE / 'rule-support.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
print('Wrote rule-support.png and rule-support.svg')
