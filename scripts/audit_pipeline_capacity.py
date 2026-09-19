"""Read-only numerical/provenance audit, writing its result inside the new study."""
import ast
import csv
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pa_milky.config import PROJECT_ROOT, config_from_payload
from pa_milky.provenance import engine_digest, input_digest, sha256_file
from report_names import report_path, verified

OUT=PROJECT_ROOT/'results/comparisons/legacy_25k_vs_50k/pipeline_capacity'


def main(folder=OUT):
    out=PROJECT_ROOT/folder
    contract=json.loads((out/'contract.json').read_text(encoding='utf-8'))
    study=json.loads((out/'study.json').read_text(encoding='utf-8'))
    rows=[json.loads(x) for x in (out/'checkpoint.jsonl').read_text(encoding='utf-8').splitlines()]
    assert len(rows)==len({tuple(r['job']) for r in rows})==study['unique_simulations']
    for r in rows:
        assert abs(r['ongoing']+r['terminal']-r['total'])<.005
        assert abs(r['ending_cash']-r['contributions']-r['total'])<.005
        assert abs(r['spend']-r['evaluation_fees']-r['activation_fees'])<.005
        assert r['accounts']+r['spares_at_end']==r['activated']
        assert r['deaths']==r['accounts']-r['alive']
        assert r['replacements_filled']+r['replacements_unfilled']==r['deaths']
        assert r['peak_subscriptions']<=r['concurrency']
        assert r['next_check_service'] is None or 0<=r['next_check_service']<=1
    with (out/'reserve_search.csv').open(encoding='utf-8',newline='') as f:
        search={tuple(json.loads(r['job'])) for r in csv.DictReader(f)}
    assert len(search)==study['search_rows']
    for j in search:
        other='legacy_50k' if j[0]=='legacy_25k' else 'legacy_25k'
        assert (other,*j[1:]) in search
    assert contract['engine']==engine_digest()
    for payload in contract['configs'].values():
        assert input_digest(config_from_payload(payload))==contract['inputs']
    assert verified(PROJECT_ROOT/'scripts/study_legacy_pipeline_capacity.py',contract['runner_sha256'])
    for name,digest in contract['prior_checkpoints'].items():
        assert sha256_file(out.parent/name/'checkpoint.jsonl')==digest
    preserved=json.loads((out/'preservation_check.json').read_text(encoding='utf-8'))
    assert preserved['all_unchanged']
    correction=out/'csv_header_fix_provenance.json'
    if correction.exists():
        record=json.loads(correction.read_text(encoding='utf-8'))
        old=out/'runner_before_csv_header_fix.py'
        current=PROJECT_ROOT/'scripts/study_legacy_pipeline_capacity.py'
        assert sha256_file(old)==record['old_runner_sha256']
        assert verified(current,record['new_runner_sha256'])
        def numerical_ast(path):
            tree=ast.parse(path.read_text(encoding='utf-8'))
            tree.body=[n for n in tree.body if not isinstance(n,ast.FunctionDef) or n.name!='csv_write']
            return ast.dump(tree,include_attributes=False)
        assert numerical_ast(old)==numerical_ast(current)
    summary={'all_checks_passed':True,'unique_simulations':len(rows),'paired_search_rows':len(search),
             'historical_controls':study['controls'],'earlier_files_preserved':preserved['protected_files'],
             'current_engine_and_inputs_match':True,
             'presentation_sources':{p.name:sha256_file(p) for p in [PROJECT_ROOT/'scripts/explain_legacy_pipeline_capacity.py',
                                       PROJECT_ROOT/'scripts/plot_legacy_pipeline_capacity.py']},
             'generated_artifacts':{p.name:sha256_file(p) for p in (report_path(out,'FINDINGS.generated.md'),out/'capacity_frontier.svg',out/'capacity_frontier.png')
                                    if p.exists()}}
    (out/'AUDIT.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main(*sys.argv[1:])
