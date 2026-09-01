"""Tests for the calls/texts provider adapter layer. Synthetic data only.

    python -m pytest tools/comms/test_comms.py -q

Every phone number, email, address, credential, and lead reference in this
file is invented. The env var is always patched to a temp dir - these tests
never touch the real %LOCALAPPDATA%\\MiamiPapaNoel\\comms\\ state.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

SCRIPT = Path(__file__).with_name("adapter.py")
SPEC = importlib.util.spec_from_file_location("mpn_comms_adapter", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


class CommsAdapterTests(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        # clear=True guarantees TWILIO_* and MPN_COMMS_LIVE are unset.
        self._env = mock.patch.dict("os.environ",
                                    {"MPN_COMMS_DIR": self._tmp.name},
                                    clear=True)
        self._env.start()

    def tearDown(self):
        self._env.stop()
        self._tmp.cleanup()

    def read_events(self):
        path = MOD.events_path()
        if not path.is_file():
            return []
        return [json.loads(line) for line in
                path.read_text(encoding="utf-8").splitlines() if line.strip()]

    # -------------------------------------------------------- redaction ----

    def test_redaction_strips_phone_numbers(self):
        out = MOD.redact("call me back at 305-555-0123 or (786) 555-0199 "
                         "or +1 305.555.0177 or 3055550142")
        self.assertIn("[REDACTED-PHONE]", out)
        for raw in ("305-555-0123", "(786) 555-0199", "305.555.0177",
                    "3055550142", "555-0123", "555-0199"):
            self.assertNotIn(raw, out)
        self.assertIsNone(MOD.PHONE_RE.search(out))

    def test_redaction_strips_email(self):
        out = MOD.redact("send the quote to maria.gonzalez+santa@example.com please")
        self.assertIn("[REDACTED-EMAIL]", out)
        self.assertNotIn("maria.gonzalez", out)
        self.assertNotIn("example.com", out)
        self.assertNotIn("@", out.replace("[REDACTED-EMAIL]", ""))

    def test_redaction_strips_street_address(self):
        out = MOD.redact("party at 8901 NW 33rd Ave, Doral")
        self.assertIn("[REDACTED-ADDRESS]", out)
        self.assertNotIn("8901", out)
        self.assertNotIn("33rd", out)
        out2 = MOD.redact("the house is 742 Evergreen Terrace")
        self.assertIn("[REDACTED-ADDRESS]", out2)
        self.assertNotIn("Evergreen", out2)

    def test_redaction_leaves_clean_text_alone(self):
        text = "asked about pricing for Dec 13, about 60 kids, Doral clubhouse"
        self.assertEqual(MOD.redact(text), text)

    # -------------------------------------------------- recording policy ---

    def test_recording_flag_refused_when_consent_none(self):
        adapter = MOD.NullAdapter()
        with self.assertRaises(MOD.RecordingRefused):
            adapter.simulate_inbound_call("L-014", "asked about pricing",
                                          duration_seconds=60, consent="none",
                                          recording_requested=True)
        self.assertEqual(self.read_events(), [])  # refusal wrote nothing

    def test_recording_refused_even_with_consent_no_live_provider(self):
        adapter = MOD.NullAdapter()
        with self.assertRaises(MOD.RecordingRefused):
            adapter.simulate_inbound_call("L-014", "asked about pricing",
                                          duration_seconds=60,
                                          consent="obtained",
                                          recording_requested=True)
        self.assertEqual(self.read_events(), [])

    def test_recording_field_is_always_not_recorded(self):
        adapter = MOD.NullAdapter()
        sms = adapter.simulate_inbound_sms("L-001", "hello")
        call = adapter.simulate_inbound_call("L-002", "asked about Dec 24",
                                             duration_seconds=95,
                                             consent="obtained")
        self.assertEqual(sms["recording"], "NOT RECORDED")
        self.assertEqual(call["recording"], "NOT RECORDED")
        for event in self.read_events():
            self.assertEqual(event["recording"], "NOT RECORDED")

    def test_append_event_refuses_any_other_recording_value(self):
        event = {"ts": "2026-09-01T10:00:00", "kind": "call_in",
                 "from_ref": "L-003", "redacted_summary": "x",
                 "duration_seconds": 5, "consent": "obtained",
                 "recording": "recording-url://synthetic"}
        with self.assertRaises(MOD.RecordingRefused):
            MOD.append_event(event)
        self.assertEqual(self.read_events(), [])

    # ------------------------------------------------------------ twilio ---

    def test_twilio_adapter_raises_without_creds(self):
        adapter = MOD.TwilioAdapter()
        for call in (lambda: adapter.send_sms("L-001", "draft"),
                     lambda: adapter.place_call("L-001"),
                     lambda: adapter.fetch_inbound_sms(),
                     lambda: adapter.fetch_inbound_calls(),
                     lambda: adapter.start_recording("L-001", "obtained")):
            with self.assertRaises(MOD.ProviderNotConfigured):
                call()

    def test_twilio_adapter_raises_with_partial_configuration(self):
        adapter = MOD.TwilioAdapter()
        with mock.patch.dict("os.environ",
                             {"TWILIO_ACCOUNT_SID": "AC-SYNTHETIC-TEST"}):
            with self.assertRaises(MOD.ProviderNotConfigured):
                adapter.send_sms("L-001", "draft")
        with mock.patch.dict("os.environ",
                             {"TWILIO_ACCOUNT_SID": "AC-SYNTHETIC-TEST",
                              "TWILIO_AUTH_TOKEN": "SYNTHETIC-TOKEN"}):
            # creds without MPN_COMMS_LIVE=1 is still not configured
            with self.assertRaises(MOD.ProviderNotConfigured):
                adapter.place_call("L-001")

    def test_twilio_adapter_not_implemented_even_fully_flagged(self):
        adapter = MOD.TwilioAdapter()
        with mock.patch.dict("os.environ",
                             {"TWILIO_ACCOUNT_SID": "AC-SYNTHETIC-TEST",
                              "TWILIO_AUTH_TOKEN": "SYNTHETIC-TOKEN",
                              "MPN_COMMS_LIVE": "1"}):
            with self.assertRaises(NotImplementedError) as ctx:
                adapter.send_sms("L-001", "draft")
            self.assertIn("tested provider connection", str(ctx.exception))

    # ------------------------------------------------------- null events ---

    def test_null_adapter_logs_valid_jsonl_events(self):
        adapter = MOD.NullAdapter()
        adapter.simulate_inbound_sms("L-014", "asked about Dec 13 pricing")
        adapter.simulate_inbound_call("L-015", "asked about Christmas Eve",
                                      duration_seconds=120, consent="none")
        events = self.read_events()
        self.assertEqual(len(events), 2)
        sms, call = events
        self.assertEqual(sms["kind"], "sms_in")
        self.assertEqual(sms["from_ref"], "L-014")
        self.assertNotIn("duration_seconds", sms)
        self.assertEqual(call["kind"], "call_in")
        self.assertEqual(call["duration_seconds"], 120)
        self.assertEqual(call["consent"], "none")
        for event in events:
            for field in ("ts", "kind", "from_ref", "redacted_summary",
                          "consent", "recording"):
                self.assertIn(field, event)

    def test_events_contain_no_raw_phone_digits_from_summary(self):
        MOD.NullAdapter().simulate_inbound_sms(
            "L-014", "she said call 786-555-0142 or text 7865550142")
        raw = MOD.events_path().read_text(encoding="utf-8")
        self.assertNotIn("786-555-0142", raw)
        self.assertNotIn("7865550142", raw)
        summary = self.read_events()[0]["redacted_summary"]
        self.assertNotIn("7865550142", re.sub(r"\D", "", summary))
        self.assertIn("[REDACTED-PHONE]", summary)

    def test_from_ref_must_never_be_a_phone_number(self):
        adapter = MOD.NullAdapter()
        for bad in ("305-555-0123", "3055550123", "(305) 555-0123", "", "  "):
            with self.assertRaises(MOD.CommsError):
                adapter.simulate_inbound_sms(bad, "hello")
        self.assertEqual(self.read_events(), [])
        adapter.simulate_inbound_sms("L-014", "hello")  # opaque ref is fine
        self.assertEqual(self.read_events()[0]["from_ref"], "L-014")

    def test_negative_duration_refused(self):
        with self.assertRaises(MOD.CommsError):
            MOD.NullAdapter().simulate_inbound_call(
                "L-014", "x", duration_seconds=-5, consent="none")
        self.assertEqual(self.read_events(), [])

    # --------------------------------------------------------------- CLI ---

    def test_cli_simulate_commands_write_valid_jsonl(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc1 = MOD.main(["simulate-inbound-sms", "--from-ref", "L-014",
                            "--summary", "asked about Dec 13"])
            rc2 = MOD.main(["simulate-inbound-call", "--from-ref", "L-015",
                            "--summary", "call me at 305-555-0123",
                            "--duration-seconds", "90",
                            "--consent", "obtained"])
        self.assertEqual((rc1, rc2), (0, 0))
        self.assertIn("DRY RUN", buf.getvalue())
        events = self.read_events()
        self.assertEqual([e["kind"] for e in events], ["sms_in", "call_in"])
        self.assertNotIn("305-555-0123", json.dumps(events))
        self.assertTrue(all(e["recording"] == "NOT RECORDED" for e in events))

    def test_cli_refuses_recording_request_with_consent_none(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = MOD.main(["simulate-inbound-call", "--from-ref", "L-014",
                           "--summary", "x", "--duration-seconds", "30",
                           "--consent", "none", "--recording-requested"])
        self.assertEqual(rc, 2)
        self.assertIn("REFUSED", buf.getvalue())
        self.assertEqual(self.read_events(), [])

    def test_status_states_human_answer_and_no_recording(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = MOD.main(["status"])
        out = buf.getvalue()
        self.assertEqual(rc, 0)
        self.assertIn("NOT CONFIGURED", out)
        self.assertIn("786-975-9557", out)
        self.assertIn("answered by a human", out)
        self.assertIn("no automated calling", out)
        self.assertIn("NOT RECORDED", out)

    def test_state_dir_honours_env_override(self):
        self.assertEqual(MOD.state_dir(), Path(self._tmp.name))
        self.assertEqual(MOD.events_path(),
                         Path(self._tmp.name) / "events.jsonl")


    def test_transcript_is_always_not_transcribed(self):
        a = MOD.NullAdapter()
        ev = a.simulate_inbound_call("L-014", "asks about dec 24", 60,
                                     "obtained")
        self.assertEqual(ev["transcript"], MOD.NOT_TRANSCRIBED)

    def test_transcript_request_refused_without_consent(self):
        a = MOD.NullAdapter()
        with self.assertRaises(MOD.RecordingRefused):
            a.simulate_inbound_call("L-014", "x", 60, "none",
                                    transcript_requested=True)

    def test_transcript_request_refused_even_with_consent(self):
        a = MOD.NullAdapter()
        with self.assertRaises(MOD.RecordingRefused):
            a.simulate_inbound_call("L-014", "x", 60, "obtained",
                                    transcript_requested=True)

    def test_append_event_rejects_foreign_transcript_value(self):
        with self.assertRaises(MOD.RecordingRefused):
            MOD.append_event({"kind": "call_in",
                              "recording": MOD.NOT_RECORDED,
                              "transcript": "full text here"})

if __name__ == "__main__":
    unittest.main()
