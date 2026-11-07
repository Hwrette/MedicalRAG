import itertools
import json
import tempfile
import unittest
from pathlib import Path

from DressingExpert.inference import assess, LEVELS, expression_value
from DressingExpert.dressingExpert import FILES_DIR, load_rules, run

RULES = load_rules(FILES_DIR / 'rules.csv')
VALUES = [(5.5, 6.2, 6.8, 7.5, 8.5), (36, 36.7, 37.2, 37.7, 38.5), (400, 800, 1200, 1800, 3000)]
KEYS = ['ph_value', 'temperature_value', 'co2_value']


def raw(indices=(0, 0, 0), **extra):
    return {**dict(zip(KEYS, [VALUES[i][v] for i, v in enumerate(indices)])), **extra}


def evaluate(data=None, history=None):
    return assess(data or raw(), RULES, history, (36, 40))


class InferenceTests(unittest.TestCase):
    def test_current_demo(self):
        result = run()
        self.assertEqual(result['final_assessment'], 'combined_signal_pattern')
        self.assertIn('review_dressing', result['actions'])
        self.assertNotIn('change_dressing', result['actions'])

    def test_all_125_combinations(self):
        for ranks in itertools.product(range(5), repeat=3):
            with self.subTest(ranks=ranks):
                result = evaluate(raw(ranks))
                self.assertEqual(list(result['indicator_levels'].values()), [LEVELS[r] for r in ranks])
                count = sum(r >= 2 for r in ranks)
                if sum(r >= 3 for r in ranks) >= 2 or (max(ranks) == 4 and count >= 2):
                    expected = 'high_concern_pattern'
                elif count >= 2 and sum(r >= 3 for r in ranks) == 1 and (ranks[0] >= 2 or count == 3):
                    expected = 'strong_combined_signal_pattern'
                elif count >= 2:
                    expected = 'combined_signal_pattern'
                elif count == 1:
                    expected = 'isolated_high_risk_pattern' if max(ranks) == 4 else 'isolated_signal_pattern'
                else:
                    expected = 'observation_pattern' if max(ranks) else 'no_warning_signal_detected'
                self.assertEqual(result['final_assessment'], expected)
                if count == 3:
                    self.assertNotIn('primary_temperature_combination', result['combined_signals'])
                    self.assertNotIn('strong_primary_temperature_combination', result['combined_signals'])
                self.assertNotIn('change_dressing', result['actions'])
                self.assertNotIn('change_and_inspect', result['actions'])

    def test_exact_boundaries(self):
        cases = [('ph_value', 'ph_level', [(0,0),(6,1),(6.5,2),(7,3),(8,4),(14,4)]),
                 ('temperature_value', 'temperature_level', [(36,0),(36.5,0),(37,2),(37.5,3),(38,4),(40,4)]),
                 ('co2_value', 'co2_level', [(0,0),(600,1),(1000,2),(1500,3),(2500,4)])]
        for field, output, cases in cases:
            for value, level in cases:
                with self.subTest(field=field, value=value):
                    self.assertEqual(evaluate(raw(**{field:value}))['indicator_levels'][output], LEVELS[level])

    def test_missing_invalid_and_partial_signals(self):
        for value in (None, 'unknown', '37', True, float('nan'), float('inf'), 35.9, 40.1):
            result = evaluate(raw((4,0,0), temperature_value=value))
            self.assertEqual(result['final_assessment'], 'insufficient_evidence')
            self.assertIn('ph_high_risk_signal', result['individual_signals'])
            self.assertEqual(result['combined_signals'], [])
            self.assertNotIn('isolated_signal_pattern', result['conclusions'])
        for key in ('ph_value',):
            for value in (-0.1,14.1):
                self.assertEqual(evaluate(raw(**{key:value}))['final_assessment'], 'insufficient_evidence')
        self.assertEqual(assess(raw(), RULES)['final_assessment'], 'insufficient_evidence')

    def test_trends_and_discordance(self):
        result = evaluate(raw((2,1,2)), [raw()])
        self.assertEqual(result['trend_results']['co2_trend'], 'strongly_worsening')
        self.assertIn('worsening_pattern', result['conclusions'])
        self.assertIn('recheck_12h', result['actions'])
        improved = evaluate(raw(), [raw((2,2,2))])
        self.assertIn('improving_pattern', improved['conclusions'])
        mixed = evaluate(raw((1,0,0)), [raw((0,1,0))])
        self.assertIn('inconclusive_pattern', mixed['conclusions'])
        self.assertIn('manual_check', mixed['actions'])
        unknown = evaluate()
        self.assertTrue(all(unknown['trend_results'][n+'_trend']=='unknown' for n in ('ph','temperature','co2')))

    def test_persistence_and_invalid_gap(self):
        high = raw((4,0,0))
        repeated = evaluate(high, [high])
        self.assertIn('ph_repeated_warning', repeated['persistence_results'])
        self.assertNotIn('ph_persistent_warning', repeated['persistence_results'])
        persistent = evaluate(high, [high, high])
        self.assertEqual(persistent['final_assessment'], 'high_concern_pattern')
        self.assertNotIn('stable_pattern', persistent['conclusions'])
        interrupted = evaluate(high, [high, raw(ph_value=None)])
        self.assertNotIn('ph_repeated_warning', interrupted['persistence_results'])
        self.assertIn('stable_pattern', evaluate(raw(), [raw(),raw()])['conclusions'])

    def test_dressing_and_clinician_decisions(self):
        result = evaluate(raw((1,0,0), dressing_change_event=True, day_since_start=4, day_since_change=1), [raw()])
        self.assertIn('post_dressing_change_change', result['persistence_results'])
        result = evaluate(raw(clinician_change_approved=True, clinician_inspect_approved=True))
        self.assertIn('A17', result['fired_rules'])
        self.assertIn('A18', result['fired_rules'])
        for data in (raw(day_since_start=0),raw(dressing_change_event='false'),raw(day_since_start=1,day_since_change=2)):
            with self.assertRaises(ValueError): evaluate(data)

    def test_csv_json_and_history_roundtrip(self):
        self.assertEqual(len(RULES),129)
        self.assertEqual(RULES, load_rules(FILES_DIR / 'rules.json'))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'history.json'
            run(raw=raw((2,0,0)), history_path=path, save_history=True)
            result = run(raw=raw((2,0,0)), history_path=path, save_history=True)
            self.assertIn('ph_repeated_warning', result['persistence_results'])
            self.assertNotIn('baseline_only',result['actions'])
            self.assertEqual(len(json.loads(path.read_text())),2)
            run(raw=raw(),history_path=path)
            self.assertEqual(len(json.loads(path.read_text())),2)

    def test_nonfinite_measurement_can_be_recorded(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'history.json'
            result = run(raw=raw(ph_value=float('nan')), history_path=path, save_history=True)
            self.assertEqual(result['final_assessment'], 'insufficient_evidence')
            saved = json.loads(path.read_text())
            self.assertEqual(saved[0]['input_values']['ph_value'], 'nan')
            self.assertNotIn('ph_repeated_warning', run(raw=raw(), history_path=path)['persistence_results'])

    def test_expression_rejects_code_execution(self):
        import ast
        with self.assertRaises(ValueError):
            expression_value(ast.parse('__import__("os").getcwd()',mode='eval'),{})


if __name__ == '__main__': unittest.main()
