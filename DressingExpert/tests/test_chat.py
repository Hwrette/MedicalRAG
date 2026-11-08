import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from DressingExpert.chat import Conversation, Transcript, main, make_system_prompt, BASE_DIR
from langchain_core.documents import Document


class ChatTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.log = Transcript(Path(self.tmp.name))
        self.client = Mock()
        self.client.models.generate_content.return_value = SimpleNamespace(text='설명 답변')
        self.store = Mock()
        self.store.similarity_search.return_value = [Document(page_content='근거 본문', metadata={'source':'source.pdf','page':2})]
        self.loader = Mock(return_value=self.store)
        self.chat = Conversation(self.client, 'test-model', 'few-shot instructions',
            {'expert_input': {'ph_value':6.8}, 'expert_output': {'final_assessment':'test','actions':[]}},
            self.log, self.loader)

    def test_off_has_no_retrieval_and_remembers_dialogue(self):
        self.chat.answer('첫 질문', False)
        self.chat.answer('그 이유는?', False)
        self.loader.assert_not_called()
        request = self.client.models.generate_content.call_args.kwargs
        self.assertEqual(len(request['contents']), 3)
        self.assertIn('few-shot instructions', request['config']['system_instruction'])
        self.assertIn('6.8', request['config']['system_instruction'])
        self.assertNotIn('근거 본문', str(request))

    def test_modes_isolated_and_comparison_does_not_mutate_history(self):
        self.chat.answer('ON 질문', True)
        on_request = self.client.models.generate_content.call_args.kwargs
        self.assertIn('근거 본문', str(on_request))
        self.assertIn('PDF 2쪽', str(on_request))
        self.chat.answer('OFF 질문', False)
        self.assertNotIn('ON 질문', str(self.client.models.generate_content.call_args.kwargs))
        before = {k:list(v) for k,v in self.chat.histories.items()}
        for mode in (False,True):
            self.chat.answer('비교 질문', mode, fresh=True)
            self.assertEqual(len(self.client.models.generate_content.call_args.kwargs['contents']),1)
        self.assertEqual(before, self.chat.histories)
        self.assertIn('근거 본문', self.log.path.read_text())

    def test_failure_is_logged_and_history_not_polluted(self):
        self.loader.side_effect = FileNotFoundError('missing index')
        self.assertIsNone(self.chat.answer('실패 질문', True))
        self.client.models.generate_content.assert_not_called()
        self.assertEqual(self.chat.histories[True], [])
        self.assertIn('실패 질문', self.log.path.read_text())
        self.assertIn('FileNotFoundError', self.log.path.read_text())
        self.assertIsNotNone(self.chat.answer('다시 질문', False))

    def test_cli_commands_and_exit_save_input_and_result(self):
        with patch('sys.argv',['chat.py','--rag','off','--input-mode','json']), \
             patch('DressingExpert.chat.Transcript', return_value=self.log), \
             patch('DressingExpert.chat.genai.Client',return_value=self.client), \
             patch('DressingExpert.chat.InMemoryVectorStore.load',return_value=self.store), \
             patch('DressingExpert.chat.GoogleGenerativeAIEmbeddings'), \
             patch('builtins.input',side_effect=['후속 질문','/rag on','다음 질문','/비교 비교 질문','/초기화','/종료']):
            main()
        saved = self.log.path.read_text()
        for expected in ['실제 전문가 시스템 입력·출력','사용한 퓨샷 프롬프트 전체','/rag on','독립 비교=True','세션 종료']:
            self.assertIn(expected,saved)
        self.client.close.assert_called_once()

    def test_cli_manual_mode_sends_history_to_expert_and_saves_log(self):
        measurements = (
            {'ph_value': 6.8, 'temperature_value': 37.4,
             'co2_value': 800, 'measurement_day': 3,
             'day_since_start': 3, 'day_since_change': 3,
             'dressing_change_event': False},
            [
                {'ph_value': 6.2, 'temperature_value': 37.0, 'co2_value': 500,
                 'measurement_day': 1, 'day_since_start': 1,
                 'day_since_change': 1, 'dressing_change_event': False},
                {'ph_value': 6.5, 'temperature_value': 37.2, 'co2_value': 600,
                 'measurement_day': 2, 'day_since_start': 2,
                 'day_since_change': 2, 'dressing_change_event': False},
            ],
            [],
        )
        with patch('sys.argv', ['chat.py','--rag','off','--input-mode','manual']), \
             patch('DressingExpert.chat.collect_measurements', return_value=measurements) as collector, \
             patch('DressingExpert.chat.Transcript', return_value=self.log), \
             patch('DressingExpert.chat.genai.Client', return_value=self.client), \
             patch('builtins.input', side_effect=['/종료']):
            main()
        collector.assert_called_once()
        self.assertEqual(collector.call_args.args[0], 'manual')
        transcript = self.log.path.read_text()
        self.assertIn('measurement_history', transcript)
        self.assertIn('algorithm_results', transcript)
        self.assertIn('manual', transcript)

    def test_rag_modes_use_identical_system_instructions(self):
        payload = {'expert_input': {'ph_value': 6.8}, 'expert_output': {'final_assessment': 'test'}}
        shared = '공통 역할과 출처 규칙'
        self.assertEqual(make_system_prompt(shared, payload, True),
                         make_system_prompt(shared, payload, False))

    def test_current_few_shot_prompt_uses_co2_field(self):
        prompt = (BASE_DIR / 'files' / 'prompt.txt').read_text(encoding='utf-8')
        self.assertIn('co2_value', prompt)
        self.assertIn('algorithm_results', prompt)
        self.assertNotIn('phenol_red_ph_value', prompt)
        self.assertNotIn('phenol_red_level', prompt)

    def test_invalid_input_json_is_logged_before_inference(self):
        bad_json = Path(self.tmp.name) / 'invalid.json'
        bad_json.write_text('{not a valid JSON', encoding='utf-8')
        with patch('sys.argv', ['chat.py', '--input-mode', 'json', '--data', str(bad_json)]), \
             patch('DressingExpert.chat.Transcript', return_value=self.log), \
             patch('DressingExpert.chat.genai.Client') as api_client:
            main()
        saved = self.log.path.read_text(encoding='utf-8')
        self.assertIn('초기화 또는 전문가 시스템 실행 실패', saved)
        self.assertIn('JSONDecodeError', saved)
        api_client.assert_not_called()

    def test_expert_failure_keeps_input_log(self):
        value = {'ph_value': 6.8, 'temperature_value': 37.2, 'co2_value': 800,
                 'measurement_day': 1, 'day_since_start': 1, 'day_since_change': 1,
                 'dressing_change_event': False}
        with patch('sys.argv', ['chat.py', '--input-mode', 'manual', '--rag', 'off']), \
             patch('DressingExpert.chat.collect_measurements',
                   return_value=(value, [], [])), \
             patch('DressingExpert.chat.run', side_effect=RuntimeError('simulated failure')), \
             patch('DressingExpert.chat.Transcript', return_value=self.log), \
             patch('DressingExpert.chat.genai.Client') as api_client:
            main()
        saved = self.log.path.read_text(encoding='utf-8')
        self.assertIn('입력 방식과 측정값', saved)
        self.assertIn('6.8', saved)
        self.assertIn('초기화 또는 전문가 시스템 실행 실패', saved)
        self.assertIn('RuntimeError', saved)
        api_client.assert_not_called()

    def test_api_client_setup_failure_is_logged(self):
        with patch('sys.argv', ['chat.py', '--input-mode', 'json', '--rag', 'off']), \
             patch('DressingExpert.chat.Transcript', return_value=self.log), \
             patch('DressingExpert.chat.genai.Client', side_effect=RuntimeError('simulated')):
            main()
        saved = self.log.path.read_text(encoding='utf-8')
        self.assertIn('채팅 실행 실패', saved)
        self.assertIn('RuntimeError', saved)
        self.assertIn('세션 종료', saved)


if __name__ == '__main__':
    unittest.main()
