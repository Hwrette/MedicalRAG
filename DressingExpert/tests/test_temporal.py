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
        self.assertAlmostEqual(r['risk_score'], 40/1.7 + 150)
        self.assertEqual(r['risk_level'], 'out_of_scale')
        self.assertAlmostEqual(r['trend_slope'], 1.2666666666666666/4.666666666666667)
        self.assertAlmostEqual(r['slope_deviation'], .3-r['trend_slope'])

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
        self.assertIn('Q01',result['fired_rules'])
        self.assertIn('Q02',result['fired_rules'])
        self.assertIn('confirm_measurement',result['actions'])
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
