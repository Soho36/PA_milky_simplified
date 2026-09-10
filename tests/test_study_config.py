import copy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from pa_milky.config import PROJECT_ROOT
from pa_milky.study_config import load_study_profile, study_path, study_policies
from pa_milky.policy_study import policies


class TestStudyConfig(unittest.TestCase):
    def test_default_preserves_original_policy_family_and_outputs(self):
        p=load_study_profile('config/studies/legacy_25k.json')
        self.assertEqual(study_policies(p), policies())
        self.assertEqual(p['budgets'], [[1000,0],[1000,200],[5000,0],[5000,200]])
        self.assertEqual(p['max_live_accounts'],20)
        self.assertTrue(study_path(p,'scenario').is_file())
        for name in p['outputs']:
            self.assertTrue((study_path(p,name)/'study.json').is_file())

    def test_placeholder_rejected(self):
        with TemporaryDirectory() as root:
            path=Path(root)/'placeholder.json'
            path.write_text(json.dumps({'schema':'pa_milky.study_profile.v1','status':'placeholder'}))
            with self.assertRaisesRegex(ValueError,'placeholder, not runnable'):
                load_study_profile(path)

    def test_50k_cannot_write_inside_25k_outputs(self):
        p=load_study_profile('config/studies/legacy_50k.json')
        p['outputs']['purchases']='results/study__full_rulebook__RR__account_purchases__cash_budgets/child'
        with TemporaryDirectory() as root:
            path=Path(root)/'bad.json';path.write_text(json.dumps(p))
            with self.assertRaisesRegex(ValueError,'another product'):
                load_study_profile(path)

    def test_distinct_outputs_required(self):
        p=copy.deepcopy(load_study_profile('config/studies/legacy_25k.json'))
        p['outputs']['cadence']=p['outputs']['amount']
        with TemporaryDirectory() as root:
            path=Path(root)/'profile.json';path.write_text(json.dumps(p))
            with self.assertRaisesRegex(ValueError,'distinct output'):
                load_study_profile(path)
