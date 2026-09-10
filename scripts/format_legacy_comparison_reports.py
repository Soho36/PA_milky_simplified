"""Pair existing report tables without rerunning or changing research evidence."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/comparisons/legacy_25k_vs_50k/reserve_by_policy'


def compact(value):
    return value.replace('monthly_current_slot_replacements', 'Monthly + replacements').replace(
        'monthly_one', 'Monthly').replace('weekly_one', 'Weekly').replace('calendar_month', 'monthly')


def pair_table(lines):
    headers = [x.strip() for x in lines[0].strip().strip('|').split('|')]
    if 'Product' not in headers:
        return lines, 0
    records = [dict(zip(headers, [x.strip() for x in line.strip().strip('|').split('|')]))
               for line in lines[2:]]
    keys = (['Withdraw / checks', 'Objective'] if 'Best reserve' in headers else
            ['Budget'] if 'Budget' in headers else
            ['Objective'] if 'Objective' in headers else ['Purchases'])
    groups = {}
    for row in records:
        key = tuple(row[k] for k in keys)
        prod = row['Product'].replace('legacy_', '').upper()
        assert prod in ('25K', '50K')
        assert prod not in groups.setdefault(key, {}), ('duplicate pair', key)
        groups[key][prod] = row
    assert all(set(g) == {'25K', '50K'} for g in groups.values()), 'Unpaired report rows'

    def cells(r):
        if 'Best reserve' in headers:
            reserve = r['Best reserve'] + f" ({r['Equally best reserves']} ties)"
            if r['Boundary tie?'] == 'yes':
                reserve += ' †'
            return [reserve, r['Score'], r['Accounts'] + ' / ' + r['Alive']]
        if 'Purchase fees' in headers:
            return [r['Accounts bought'] + ' — ' + r['Ledger'], r['Purchase fees'],
                    r['Booked deficits not funded by owner'] + ' (' + r['Deficits / total cash'] + ')']
        if 'Inherited total' in headers:
            return [r[k] for k in ('Inherited total', 'Stricter total', 'Change', 'Stricter bought / alive')]
        if keys == ['Purchases']:
            return [r['Selected reserve'] + ' (' + r['Equally best tested reserves'] + ' ties)',
                    r['Ongoing'] + ' / ' + r['Total'], r['Bought / alive']]
        return [compact(r['Purchases']) + '; ' + compact(r.get('Withdraw / checks', r.get('Withdrawal / checks', ''))) + '; reserve ' + r['Reserve'],
                r['Ongoing'] + ' / ' + r['Total'],
                r.get('Bought / alive', r.get('Accounts', '') + ' / ' + r.get('Alive', ''))]

    labels = (['Reserve (ties)', 'Score', 'Bought / alive'] if 'Best reserve' in headers else
              ['Bought / ledger', 'Purchase fees', 'Owner-excluded deficits (ratio)'] if 'Purchase fees' in headers else
              ['Inherited total', 'Stricter total', 'Change', 'Bought / alive'] if 'Inherited total' in headers else
              ['Reserve (ties)', 'Ongoing / total', 'Bought / alive'] if keys == ['Purchases'] else
              ['Policy and reserve', 'Ongoing / total', 'Bought / alive'])
    new_headers = keys + [f'**{p} — {label}**' for p in ('25K', '50K') for label in labels]
    result = ['| ' + ' | '.join(new_headers) + ' |', '| ' + ' | '.join(['---'] * len(new_headers)) + ' |']
    for key, pair in groups.items():
        result.append('| ' + ' | '.join([compact(x) for x in key] + cells(pair['25K']) + cells(pair['50K'])) + ' |')
    return result, len(groups)


def format_report(text):
    lines = text.splitlines()
    output, count, i = [], 0, 0
    while i < len(lines):
        if lines[i].startswith('|') and i + 1 < len(lines) and re.match(r'^\|[ :|-]+\|$', lines[i + 1]):
            end = i + 2
            while end < len(lines) and lines[end].startswith('|'):
                end += 1
            table, pairs = pair_table(lines[i:end])
            output.extend(table)
            count += pairs
            i = end
        else:
            output.append(lines[i])
            i += 1
    note = ('25K is shown on the left and 50K on the right. Each row shares the same comparison labels. '
            '“Bought / alive” means cumulative purchases / ending survivors. Reserve cells retain tie counts; '
            '† marks a tie at a tested range boundary. Cash pairs are ongoing / terminal-inclusive, in USD.')
    if count:
        output[2:2] = [note, '']
    excel = '[Excel workbook — summary, budget comparisons and data](../../../../outputs/01a08833-466a-7372-9c06-5ddf2e946598/Legacy_25K_vs_50K.xlsx)'
    if excel not in output:
        output[2:2] = [excel, '']
    output = [line.replace('(1 ties)', '(1 tie)') for line in output]
    return '\n'.join(output) + '\n', count


def main():
    evidence = ['study.json', 'winner_analysis.json', 'all_settings.csv', 'best_by_policy.csv', 'matched_deltas.csv']
    hashes = {n: hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in evidence}
    result = {'evidence_sha256': hashes, 'reports': {}}
    for name in ('REPORT', 'FINDINGS'):
        generated, reader = OUT/f'{name}.generated.md', OUT/f'{name}.md'
        old = generated.read_text(encoding='utf-8')
        new, pairs = format_report(old)
        mirror = reader.exists() and reader.read_text(encoding='utf-8') == old
        generated.write_text(new, encoding='utf-8')
        if mirror:
            reader.write_text(new, encoding='utf-8')
        blocks = re.findall(r'^\|[^\n]*\*\*25K[^\n]*\n\|[^\n]*\n((?:\|[^\n]*\n)+)', new, re.MULTILINE)
        result['reports'][name] = {'paired_rows': sum(len(b.splitlines()) for b in blocks),
                                  'rows_converted_this_run': pairs, 'reader_copy_refreshed': mirror}
    assert hashes == {n: hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in evidence}
    (OUT/'presentation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result['reports']))


if __name__ == '__main__':
    main()
