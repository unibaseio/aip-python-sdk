"""Cross-language wire contract tests (stdlib unittest — no extra deps).

The golden JSON files under contracts/fixtures/ are copied from the Go SDK (the
source of truth) and define the wire format ALL AIP SDKs must serialize to
identically. Run with:

    python -m unittest contracts.test_contracts
"""

import json
import os
import unittest

from aip_sdk.a2a.server import job_completion_body

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def read_fixture(name):
    with open(os.path.join(FIXTURES, name + ".json")) as f:
        return json.load(f)


class JobCompletionContract(unittest.TestCase):
    def test_multichain_completion_matches_fixture(self):
        body = job_completion_body(
            "job-1", "97:reg:demo", {"response": "hello", "task": {}}, 97, None
        )
        # Normalize via JSON round-trip so comparison ignores key order.
        got = json.loads(json.dumps(body))
        self.assertEqual(got, read_fixture("job_completion"))

    def test_failure_completion(self):
        body = job_completion_body("job-2", "56:reg:demo", {"response": "x"}, 56, "boom")
        self.assertEqual(body["status"], "failed")
        self.assertEqual(body["error"], "boom")
        self.assertEqual(body["result"], {})
        self.assertEqual(body["chain_id"], 56)


if __name__ == "__main__":
    unittest.main()
