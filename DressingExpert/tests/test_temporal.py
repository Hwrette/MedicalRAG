import json
import tempfile
import unittest
from pathlib import Path
from DressingExpert.temporal import calculate
from DressingExpert.dressingExpert import run, FILES_DIR
from DressingExpert.image_input import match_rgb, validate_layout

CONFIG = json.loads((FILES_DIR / 'algorithm_config.json').read_text())['sensors']['ph']

class TemporalTests(unittest.TestCase):
    def test_formula_and_days(self):
        r = calculate([(1,6),(2,6.2),(4,6.8)], CONFIG)
        self.assertAlmostEqual(r['recent_slope'], .3)
        self.assertAlmostEqual(r['risk_score'], 40/1.7 + 12)
        self.assertEqual(r['risk_level'], 'band_1')
        self.assertAlmostEqual(r['trend_slope'], .2)
        self.assertAlmostEqual(r['slope_deviation'], .3-r['trend_slope'])

    def test_temperature_trend_without_score_weights(self):
        config = json.loads((FILES_DIR / 'algorithm_config.json').read_text())['sensors']['temperature']
        config = {**config, 'alpha': None, 'beta': None}
        for series in [[(1, 37), (2, 37.2)], [(1, 37), (2, 37.2), (3, 40)]]:
            result = calculate(series, config)
            self.assertIsNone(result['risk_score'])
            self.assertIsNone(result['risk_level'])
            self.assertEqual(result['risk_status'], 'weights_unset')
            self.assertIsNotNone(result['recent_slope'])
        self.assertAlmostEqual(result['trend_slope'], .2)
        self.assertAlmostEqual(result['slope_deviation'], 2.6)
        self.assertEqual(result['trend_status'], 'similar_to_trend')

    def test_temperature_simulation_anchors(self):
        config = json.loads((FILES_DIR / 'algorithm_config.json').read_text())['sensors']['temperature']
        for previous, score, level in [(38, 20, 'band_1'), (37, 60, 'band_3')]:
            result = calculate([(1, previous), (2, 38)], config)
            self.assertEqual((result['risk_score'], result['risk_level']), (score, level))
        at_limit = calculate([(1, 39), (2, 40)], config)
        self.assertIsNone(at_limit['risk_score'])
        self.assertEqual(at_limit['risk_level'], 'limit_exceeded')

    def test_temperature_score_reaches_q01_with_valid_measurements(self):
        def reading(day, temp):
            return {'measurement_day': day, 'ph_value': 5.5, 'co2_value': 8.0,
                    'temperature_value': temp}

        for before, now, score, alert in [(38, 38, 20, False), (37, 38, 60, True),
                                          (39, 40, None, True)]:
            with self.subTest(before=before, now=now):
                output = run(raw=reading(2, now), history=[reading(1, before)])
                self.assertEqual(output['algorithm_results']['temperature']['risk_score'], score)
                self.assertFalse(output['facts']['ph_score_alert'])
                self.assertEqual(output['facts']['temperature_score_alert'], alert)
                self.assertEqual('Q01' in output['fired_rules'], alert)
                self.assertEqual('numeric_score_review' in output['conclusions'], alert)
                if alert:
                    self.assertIn('confirm_measurement', output['actions'])

    def test_phenol_red_falling_ph_and_lower_limit(self):
        config = json.loads((FILES_DIR / 'algorithm_config.json').read_text())['sensors']['co2']
        falling = calculate([(1, 7.8), (2, 6.0)], config)
        self.assertAlmostEqual(falling['risk_score'], 152)
        self.assertAlmostEqual(falling['recent_slope'], -1.8)
        self.assertEqual(calculate([(1, 6), (2, 5.5)], config)['risk_level'], 'limit_exceeded')
        output = run(raw={'measurement_day': 2, 'co2_value': 15},
                     history=[{'measurement_day': 1, 'co2_value': 8}])
        self.assertIsNone(output['algorithm_results']['co2']['risk_score'])

    def test_limit_time_and_short_history(self):
        for x in (8.5,9):
            r=calculate([(1,7),(2,x)],CONFIG)
            self.assertIsNone(r['risk_score'])
            self.assertEqual(r['risk_level'],'limit_exceeded')
        self.assertEqual(calculate([(1,6),(1,7)],CONFIG)['status'],'invalid_time_order')
        self.assertEqual(calculate([(2,6),(1,7)],CONFIG)['status'],'invalid_time_order')
        self.assertIsNone(calculate([(1,6),(2,7)],CONFIG)['trend_status'])
        self.assertIsNone(calculate([(1,6)],CONFIG)['risk_score'])

    def test_demo_and_invalid_gap(self):
        history=json.loads((FILES_DIR/'demo_history.json').read_text())
        result=run(history=history)
        self.assertNotIn('Q01',result['fired_rules'])
        self.assertNotIn('Q02',result['fired_rules'])
        self.assertAlmostEqual(result['algorithm_results']['ph']['slope_deviation'], .2)
        self.assertTrue(result['simulation_mode'])
        history[-1]['ph_value']=None
        self.assertIsNone(run(history=history)['algorithm_results']['ph']['risk_score'])

    def test_old_phenol_ph_not_co2(self):
        result=run(raw={'ph_value':6,'temperature_value':37,'phenol_red_ph_value':7})
        self.assertEqual(result['final_assessment'],'insufficient_evidence')
        self.assertTrue(result['facts']['co2_input_invalid'])

    def test_image_mapping_and_missing_calibration(self):
        import cv2
        import numpy as np
        layout=json.loads((FILES_DIR/'image_layout.json').read_text())
        validate_layout(layout)
        self.assertEqual(match_rgb([205,185,120],layout['patches']['btb'])['value'],6)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'input.png'
            cv2.imwrite(str(path),np.full((200,200,3),(120,185,205),dtype=np.uint8))
            result=run(image_path=path,raw={'measurement_day':1})
            self.assertEqual(result['input_values']['ph_value'],6)
            self.assertIsNone(result['input_values']['co2_value'])
            self.assertIsNone(result['input_values']['temperature_value'])
            self.assertEqual(result['final_assessment'],'insufficient_evidence')
