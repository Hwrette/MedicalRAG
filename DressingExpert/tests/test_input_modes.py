"""Tests for the manual/image input collection boundary (no Gemini API required)."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from DressingExpert.dressingExpert import run
from DressingExpert.input_modes import collect_measurements


def scripted_input(values):
    iterator = iter(values)
    return lambda prompt='': next(iterator)


class InputModeTests(unittest.TestCase):
    def test_manual_three_days_reaches_temporal_analysis(self):
        answers = [
            '3',
            'n', '6.2', '37.0', '500',
            '2', 'n', '6.4', '37.2', '700',
            '3', 'n', '6.8', '37.4', '900',
        ]
        raw, history, details = collect_measurements(
            'manual', input_fn=scripted_input(answers), output_fn=lambda _: None
        )
        self.assertEqual(len(history), 2)
        self.assertEqual(raw['measurement_day'], 3)
        self.assertEqual([x['measurement_day'] for x in history], [1, 2])
        self.assertEqual(raw['ph_value'], 6.8)
        self.assertFalse(details)
        result = run(raw=raw, history=history)
        self.assertEqual(result['algorithm_results']['ph']['status'], 'calculated')
        self.assertIsNotNone(result['algorithm_results']['temperature']['slope_deviation'])

    def test_manual_skipped_days_and_dressing_change(self):
        answers = [
            '2',
            'n', '6.2', '37', '500',
            '5', 'y', '6.5', '37.5', '700',
        ]
        raw, history, _ = collect_measurements(
            'manual', input_fn=scripted_input(answers), output_fn=lambda _: None
        )
        self.assertEqual(raw['measurement_day'], 5)
        self.assertEqual(raw['day_since_change'], 1)
        self.assertTrue(raw['dressing_change_event'])
        self.assertEqual(history[0]['day_since_change'], 1)

    def test_reject_duplicate_day_and_non_finite_manual_values(self):
        answers = [
            '2',
            'n', 'nan', '6.5', '36.8', '500',
            '1', '2', 'n', 'inf', '6.8', '37.0', '700',
        ]
        messages = []
        raw, history, _ = collect_measurements(
            'manual', input_fn=scripted_input(answers), output_fn=messages.append
        )
        self.assertEqual(raw['measurement_day'], 2)
        self.assertEqual(raw['ph_value'], 6.8)
        self.assertEqual(history[0]['ph_value'], 6.5)
        self.assertTrue(any('유한한 숫자' in message for message in messages))

    def test_image_missing_calibration_does_not_invent_values(self):
        image_result = {
            'input_values': {
                'ph_value': 6.5, 'temperature_value': None, 'co2_value': None
            },
            'patches': {
                'btb': {'value': 6.5, 'status': 'matched', 'rgb_median': [1, 2, 3]},
                'temperature': {'value': None, 'status': 'calibration_missing', 'rgb_median': [4, 5, 6]},
                'phenol_red': {'value': None, 'status': 'calibration_missing', 'rgb_median': [7, 8, 9]},
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / 'day1.png'
            image_path.write_bytes(b'fixture')
            with patch('DressingExpert.input_modes._read_image', return_value=image_result):
                raw, history, details = collect_measurements(
                    'image',
                    input_fn=scripted_input(['1', 'n', str(image_path), '', '']),
                    output_fn=lambda _: None,
                )
        self.assertIsNone(raw['temperature_value'])
        self.assertIsNone(raw['co2_value'])
        self.assertEqual(history, [])
        self.assertEqual(details[0]['manual_fallback_fields'], [])
        result = run(raw=raw, history=history)
        self.assertEqual(result['final_assessment'], 'insufficient_evidence')

    def test_image_missing_calibration_can_use_declared_manual_reading(self):
        image_result = {
            'input_values': {'ph_value': 6.5, 'temperature_value': None, 'co2_value': None},
            'patches': {
                'btb': {'value': 6.5, 'status': 'matched'},
                'temperature': {'value': None, 'status': 'calibration_missing'},
                'phenol_red': {'value': None, 'status': 'calibration_missing'},
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            image_path = Path(directory) / 'day1.png'
            image_path.write_bytes(b'fixture')
            with patch('DressingExpert.input_modes._read_image', return_value=image_result):
                raw, _, details = collect_measurements(
                    'image',
                    input_fn=scripted_input(['1', 'n', str(image_path), '37.2', '800']),
                    output_fn=lambda _: None,
                )
        self.assertEqual(raw['temperature_value'], 37.2)
        self.assertEqual(raw['co2_value'], 800)
        self.assertEqual(set(details[0]['manual_fallback_fields']),
                         {'temperature_value', 'co2_value'})


if __name__ == '__main__':
    unittest.main()
