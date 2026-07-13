import unittest

from peter_companion import ExecutionMode, GateStatus, InteractionMode, route_request


class RouterTests(unittest.TestCase):
    def test_default_interaction_mode(self):
        self.assertEqual(route_request("今天幫我整理會議內容").interaction_mode, InteractionMode.VOICE_COMPANION)

    def test_quiet_mode_exact_phrase(self):
        self.assertEqual(route_request("安靜慢慢來，我們一次一個").interaction_mode, InteractionMode.QUIET_SLOW)

    def test_quiet_mode_not_too_much(self):
        self.assertEqual(route_request("不要一次太多，先做一件").interaction_mode, InteractionMode.QUIET_SLOW)

    def test_default_execution_is_planning(self):
        self.assertEqual(route_request("幫我規劃影片").execution_mode, ExecutionMode.PLANNING)

    def test_formal_trigger_without_gates_stays_locked(self):
        d = route_request("【正式生成影片】")
        self.assertEqual(d.execution_mode, ExecutionMode.PLANNING)
        self.assertEqual(len(d.missing_gates), 3)

    def test_formal_trigger_with_partial_gates_stays_locked(self):
        d = route_request("【正式生成影片】", GateStatus(script_final=True, storyboard_final=True))
        self.assertEqual(d.execution_mode, ExecutionMode.PLANNING)
        self.assertEqual(d.missing_gates, ("生成確認門",))

    def test_formal_trigger_with_all_gates_passes(self):
        d = route_request("【正式生成影片】", GateStatus(True, True, True))
        self.assertEqual(d.execution_mode, ExecutionMode.FORMAL_GENERATION)

    def test_similar_phrase_does_not_trigger(self):
        d = route_request("正式生成影片")
        self.assertEqual(d.execution_mode, ExecutionMode.PLANNING)
        self.assertFalse(d.formal_trigger_present)

    def test_cloud_intent_defaults_private(self):
        d = route_request("把 PDF 和 Excel 上傳雲端資料夾")
        self.assertTrue(d.cloud_intent)
        self.assertFalse(d.supervisor_access)
        self.assertTrue(any("維持私人" in n for n in d.notices))

    def test_explicit_supervisor_consent(self):
        self.assertTrue(route_request("我同意把報表分享給主管查看").supervisor_access)

    def test_supervisor_negative_overrides_positive_word(self):
        self.assertFalse(route_request("可以整理報表，但不要分享給主管").supervisor_access)

    def test_supervisor_ambiguous_is_not_consent(self):
        self.assertFalse(route_request("主管可能之後需要這份報表").supervisor_access)

    def test_codex_candidate(self):
        self.assertTrue(route_request("請用 Codex 修正 Apps Script 並跑測試").codex_candidate)

    def test_non_codex_request(self):
        self.assertFalse(route_request("幫我整理今天的想法").codex_candidate)

    def test_password_value_triggers_safety_stop(self):
        self.assertTrue(route_request("我的密碼是 abcdef1234").safety_stop)

    def test_password_policy_discussion_does_not_trigger(self):
        self.assertFalse(route_request("請提醒我不要上傳密碼或 API 金鑰").safety_stop)

    def test_api_key_value_triggers_safety_stop(self):
        self.assertTrue(route_request("API_KEY=abcdefghijk12345").safety_stop)

    def test_private_key_triggers_safety_stop(self):
        self.assertTrue(route_request("-----BEGIN PRIVATE KEY-----").safety_stop)

    def test_safety_stop_blocks_formal_generation(self):
        d = route_request("【正式生成影片】 API_KEY=abcdefghijk12345", GateStatus(True, True, True))
        self.assertEqual(d.execution_mode, ExecutionMode.PLANNING)
        self.assertTrue(d.safety_stop)

    def test_long_voice_style_input(self):
        d = route_request("今天結束後把報表整理好，分別放到資料夾，先不要分享給主管，程式錯誤交給 Codex 測試。")
        self.assertTrue(d.cloud_intent)
        self.assertTrue(d.codex_candidate)
        self.assertFalse(d.supervisor_access)

    def test_voice_and_execution_layers_are_independent(self):
        d = route_request("安靜慢慢來。【正式生成影片】", GateStatus(True, True, True))
        self.assertEqual(d.interaction_mode, InteractionMode.QUIET_SLOW)
        self.assertEqual(d.execution_mode, ExecutionMode.FORMAL_GENERATION)

    def test_empty_text_uses_defaults(self):
        d = route_request("")
        self.assertEqual(d.interaction_mode, InteractionMode.VOICE_COMPANION)
        self.assertEqual(d.execution_mode, ExecutionMode.PLANNING)

    def test_non_string_rejected(self):
        with self.assertRaises(TypeError):
            route_request(None)  # type: ignore[arg-type]

    def test_gate_missing_order_is_stable(self):
        gates = GateStatus(script_final=False, storyboard_final=True, generation_confirmed=False)
        self.assertEqual(gates.missing, ("腳本定稿門", "生成確認門"))


if __name__ == "__main__":
    unittest.main()
