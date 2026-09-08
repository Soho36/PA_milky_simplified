"""Shared study settings, independent of the simulation's scenario schema."""
import argparse
import hashlib
import json
from pathlib import Path
from .config import PROJECT_ROOT
from .policy import WithdrawalPolicy


def load_study_profile(path=None):
    if path is None:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('--study', default='config/studies/legacy_25k.json')
        path = parser.parse_known_args()[0].study
    path = Path(path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    raw = path.read_bytes()
    profile = json.loads(raw)
    if profile.get('schema') != 'pa_milky.study_profile.v1':
        raise ValueError('Unsupported study profile schema')
    if profile.get('status') != 'ready':
        raise ValueError(f'{path.name} is a placeholder, not runnable; verify its product and rulebook first')
    if profile['workers'] < 1 or profile['max_live_accounts'] < 1:
        raise ValueError('Workers and live-account cap must be positive')
    if len(set(profile['outputs'].values())) != len(profile['outputs']):
        raise ValueError('Each study must have a distinct output directory')
    profile['_source'] = str(path.resolve())
    profile['_sha256'] = hashlib.sha256(raw).hexdigest()
    return profile


def study_path(profile, name):
    value = profile['scenario'] if name == 'scenario' else profile['outputs'][name]
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def study_policies(profile):
    return [WithdrawalPolicy.from_payload(p) for p in profile['amount']['policies']]


def profile_provenance(profile):
    return {'path': profile['_source'], 'sha256': profile['_sha256'],
            'settings': {k:v for k,v in profile.items() if not k.startswith('_')}}
