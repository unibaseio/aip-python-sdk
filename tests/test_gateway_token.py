"""The gateway token from POST /agents/register must ride on job-queue polls.

Once an agent has used its token the gateway refuses token-less poll/complete
for that queue, which is what stops other people from taking its jobs.
"""
import asyncio

import httpx

from aip_sdk.a2a.server import A2AServer

AGENT = "56:0x8004:7"


def _server() -> A2AServer:
    srv = A2AServer.__new__(A2AServer)  # skip the HTTP app setup; only polling state matters
    srv.registration_config = {"gateway_url": "http://gw", "handle": "h"}
    srv._gateway_tokens = {AGENT: "tok"}
    srv._should_poll = True
    return srv


def _run_one_poll(monkeypatch, srv, use_job_queue):
    seen = {}
    real = httpx.AsyncClient

    def handler(request):
        seen["token"] = request.headers.get("X-Agent-Token")
        srv._should_poll = False
        return httpx.Response(200, json={"job_id": None})

    monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: real(transport=httpx.MockTransport(handler), **kw))
    asyncio.run(srv._gateway_polling_loop(AGENT, 56, use_job_queue))
    return seen["token"]


def test_job_poll_sends_the_agent_token(monkeypatch):
    assert _run_one_poll(monkeypatch, _server(), use_job_queue=True) == "tok"


def test_task_queue_poll_does_not(monkeypatch):
    assert _run_one_poll(monkeypatch, _server(), use_job_queue=False) is None
