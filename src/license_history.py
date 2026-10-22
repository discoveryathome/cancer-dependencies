"""Resolve exact non-scientific documents superseded by license/intake notices."""
import hashlib
from pathlib import Path

# Immutable versions from 730abd211ea8438c42efb6404cb2a465464efd60.
# Scientific source, inputs, results and manifests must never be added here.
SNAPSHOTS = {
    'DATA_LICENSE.md': '83b78613340a45b2fe34140e8512c0d7e4053e46e8fae31c99fa51009cca9491',
    'README.md': '4feb06fe6d1f76387862e27daee2d1dda8640bbc12ba1242e4ce37b270d1b058',
    'QUICKSTART.md': '05252fcd2b47088a267f474393a24adb4e0f5e911379946da8402cee967913f8',
    'src/check_history.py': 'ba39c4a32a03d7454148ad77ebb32d73609831f6d549703f57f3e985c24e46c9',
    'research/program-v2-20261021/check_manifest.py': 'b071bb54a19bdd715c4dfcb06af0fe56ce44fc1ec12237967d4f63f73d3b8854',
}

# Pre-launch entry/declaration versions bound by the program-v2 manifest.
# research_program.py only validates declarations and picks tasks; no scientific
# computation is redirected. No wildcard or arbitrary snapshot fallback is allowed.
LAUNCH_SNAPSHOTS = {
    'AGENTS.md': '71da09d3747389dc9ceaffc659ceccc6fd0cb08cc07b0c98e4c1fd52c2f92c41',
    'DISCOVERY.md': '210df5fd3cf09b8067abc67ff9d6a551d18c4797f81c0c110644052bf5234e5a',
    'discover.json': '744fc223ee00ee494588c2e7d5ebf0320d0ed0c400c5286534ac2b53dbf795ad',
    'discover/catalog.json': '398cf71971019964135fd89907ca607b97cdb79c67dd1d6d3dcff49e2128412d',
    'discover/priority-log.md': '1f3ca9eadd39d26e529117c5bd4af1d058fa2c9f2e0512fb717748c6d652467f',
    'discover/program.json': '63d23c598954c510cef0ba3e781b0f65174e768a52d421ac6cf103e551ed3031',
    'src/research_program.py': 'b273e2809df62b2ceff34a23532795d628aa4953a93c638cbb09829f473c67df',
}


def evidence_path(root: Path, name: str, expected: str) -> Path:
    """Unrecognized hashes/paths always resolve to the actual current file."""
    if name in SNAPSHOTS and expected == SNAPSHOTS[name]:
        path = root / 'research/license-20261022/historical' / name
    elif name in LAUNCH_SNAPSHOTS and expected == LAUNCH_SNAPSHOTS[name]:
        path = root / 'research/launch-20261021/pre-launch-entry' / name
    else:
        return root / name
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError('Changed license-history snapshot: ' + name)
    return path
