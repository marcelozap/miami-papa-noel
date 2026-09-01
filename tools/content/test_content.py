"""Tests for the Santa content queue. Synthetic data only.

    python -m pytest tools/content/test_content.py -q
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

SCRIPT = Path(__file__).with_name("queue.py")
SPEC = importlib.util.spec_from_file_location("mpn_content_queue", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)

VIDEO = r"D:\santa-videos\example-take-01.mp4"  # synthetic; never read
TOPIC = "how a Santa visit works"

# Monday, so the next Tue/Thu/Sat are Dec 8, 10, 12.
MONDAY = dt.datetime(2026, 12, 7, 9, 0)


class ContentQueueTests(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self._env = mock.patch.dict("os.environ",
                                    {"MPN_CONTENT_DIR": self._tmp.name})
        self._env.start()
        self.store = {"items": {}, "schedule_seq": 0}

    def tearDown(self):
        self._env.stop()
        self._tmp.cleanup()

    def drafted(self, topic=TOPIC):
        return MOD.create_draft(self.store, VIDEO, topic)

    def approved(self, topic=TOPIC):
        item = self.drafted(topic)
        MOD.submit(self.store, item["item_id"])
        MOD.approve(self.store, item["item_id"], "operator")
        return item

    # ------------------------------------------------------- happy path ----

    def test_full_legal_path(self):
        item = self.drafted()
        self.assertEqual(item["state"], MOD.DRAFT)
        MOD.submit(self.store, item["item_id"])
        self.assertEqual(item["state"], MOD.PENDING_APPROVAL)
        MOD.approve(self.store, item["item_id"], "operator")
        self.assertEqual(item["state"], MOD.APPROVED)
        MOD.schedule(self.store, item["item_id"], "operator", now=MONDAY)
        self.assertEqual(item["state"], MOD.SCHEDULED_DRY_RUN)
        self.assertEqual(item["suggested_post_time"], "2026-12-08T10:00:00")
        self.assertEqual(item["approvals"][0]["operator"], "operator")

    def test_item_ids_are_sequential(self):
        ids = [self.drafted()["item_id"] for _ in range(3)]
        self.assertEqual(ids, ["C-001", "C-002", "C-003"])

    def test_video_is_referenced_by_path_only_never_read(self):
        # The path does not exist anywhere; drafting must still succeed
        # because the tool never opens, reads, or copies the video.
        item = MOD.create_draft(self.store,
                                r"Z:\does\not\exist\take-99.mp4", TOPIC)
        self.assertEqual(item["video_path"], r"Z:\does\not\exist\take-99.mp4")

    # -------------------------------------------------- publish blocked ----

    def test_publish_blocked_from_every_state(self):
        for state in MOD.STATES:
            item = self.drafted("topic for state %s" % state)
            item["state"] = state
            with self.assertRaises(MOD.PublishBlockedError):
                MOD.publish(self.store, item["item_id"], "operator")
            self.assertEqual(item["state"], state)  # unchanged

    def test_no_transition_reaches_published(self):
        item = self.drafted()
        for state in MOD.STATES:
            item["state"] = state
            with self.assertRaises(MOD.PublishBlockedError):
                MOD.transition(self.store, item["item_id"], MOD.PUBLISHED,
                               "operator")
        self.assertNotIn((MOD.SCHEDULED_DRY_RUN, MOD.PUBLISHED),
                         MOD.TRANSITIONS)

    def test_publish_refusal_explains_why(self):
        item = self.approved()
        MOD.schedule(self.store, item["item_id"], "operator", now=MONDAY)
        with self.assertRaises(MOD.PublishBlockedError) as ctx:
            MOD.publish(self.store, item["item_id"], "operator")
        msg = str(ctx.exception)
        self.assertIn("credentials", msg)
        self.assertIn("operator approval", msg)
        self.assertIn("post", msg.lower())

    # --------------------------------------------------- forbidden topics --

    def test_each_forbidden_phrase_is_refused(self):
        for phrase in MOD.FORBIDDEN_TOPIC_PHRASES:
            with self.assertRaises(MOD.ForbiddenTopicError):
                MOD.create_draft(self.store, VIDEO,
                                 "a video about %s from last week" % phrase)

    def test_forbidden_phrases_case_and_spacing_insensitive(self):
        with self.assertRaises(MOD.ForbiddenTopicError):
            MOD.create_draft(self.store, VIDEO, "GUARANTEED best Santa")
        with self.assertRaises(MOD.ForbiddenTopicError):
            MOD.create_draft(self.store, VIDEO, "a review   from a parent")
        self.assertEqual(self.store["items"], {})  # nothing was created

    # ---------------------------------------------------------- drafting ---

    def test_bilingual_drafts_contain_public_phone(self):
        item = self.drafted()
        for field in ("script_en", "script_es", "caption_en", "caption_es"):
            self.assertTrue(item[field].strip())
            self.assertIn(MOD.PUBLIC_PHONE, item[field])
            self.assertIn("Miami", item[field])
        self.assertNotEqual(item["script_en"], item["script_es"])
        self.assertNotEqual(item["caption_en"], item["caption_es"])

    def test_drafts_are_deterministic(self):
        a = self.drafted()
        b = self.drafted()
        for field in ("script_en", "script_es", "caption_en", "caption_es"):
            self.assertEqual(a[field], b[field])

    def test_drafts_are_ascii_and_never_mention_other_payment_methods(self):
        item = self.drafted()
        joined = " ".join(item[f] for f in
                          ("script_en", "script_es", "caption_en", "caption_es"))
        joined.encode("ascii")  # raises if any non-ASCII slips in
        for banned in ("venmo", "cashapp", "cash app", "paypal", "stripe",
                       "square", "card", "wire", "guaranteed"):
            self.assertNotIn(banned, joined.lower())

    # ------------------------------------------------------- transitions ---

    def test_schedule_only_from_approved(self):
        item = self.drafted()
        with self.assertRaises(MOD.TransitionError):
            MOD.schedule(self.store, item["item_id"], "operator", now=MONDAY)
        MOD.submit(self.store, item["item_id"])
        with self.assertRaises(MOD.TransitionError):
            MOD.schedule(self.store, item["item_id"], "operator", now=MONDAY)
        MOD.approve(self.store, item["item_id"], "operator")
        MOD.schedule(self.store, item["item_id"], "operator", now=MONDAY)
        self.assertEqual(item["state"], MOD.SCHEDULED_DRY_RUN)
        with self.assertRaises(MOD.TransitionError):  # no double schedule
            MOD.schedule(self.store, item["item_id"], "operator", now=MONDAY)

    def test_approve_requires_operator(self):
        item = self.drafted()
        MOD.submit(self.store, item["item_id"])
        with self.assertRaises(MOD.TransitionError):
            MOD.approve(self.store, item["item_id"], "")
        with self.assertRaises(MOD.TransitionError):
            MOD.approve(self.store, item["item_id"], "   ")
        self.assertEqual(item["state"], MOD.PENDING_APPROVAL)
        self.assertEqual(item["approvals"], [])

    def test_illegal_transitions_rejected(self):
        item = self.drafted()
        with self.assertRaises(MOD.TransitionError):  # approve from DRAFT
            MOD.approve(self.store, item["item_id"], "operator")
        MOD.submit(self.store, item["item_id"])
        with self.assertRaises(MOD.TransitionError):  # double submit
            MOD.submit(self.store, item["item_id"])
        MOD.approve(self.store, item["item_id"], "operator")
        with self.assertRaises(MOD.TransitionError):  # submit from APPROVED
            MOD.submit(self.store, item["item_id"])
        with self.assertRaises(MOD.TransitionError):
            MOD.get_item(self.store, "C-999")

    # ---------------------------------------------------------- schedule ---

    def test_schedule_round_robin_is_deterministic(self):
        expected = ["2026-12-08T10:00:00",   # Tue 10:00
                    "2026-12-10T18:00:00",   # Thu 18:00
                    "2026-12-12T10:00:00",   # Sat 10:00
                    "2026-12-15T18:00:00"]   # Tue 18:00
        for want in expected:
            item = self.approved("topic %s" % want)
            MOD.schedule(self.store, item["item_id"], "operator", now=MONDAY)
            self.assertEqual(item["suggested_post_time"], want)

    # --------------------------------------------------------------- log ---

    def test_log_lines_written_for_every_action(self):
        item = self.approved()
        MOD.schedule(self.store, item["item_id"], "operator", now=MONDAY)
        with self.assertRaises(MOD.PublishBlockedError):
            MOD.publish(self.store, item["item_id"], "operator")
        lines = [json.loads(l) for l in
                 MOD.log_path().read_text(encoding="utf-8").splitlines()]
        self.assertEqual([l["action"] for l in lines],
                         ["draft", "submit", "approve", "schedule",
                          "publish-refused"])
        approve_line = lines[2]
        self.assertEqual(approve_line["operator"], "operator")
        self.assertEqual(approve_line["from"], MOD.PENDING_APPROVAL)
        self.assertEqual(approve_line["to"], MOD.APPROVED)


if __name__ == "__main__":
    unittest.main()
