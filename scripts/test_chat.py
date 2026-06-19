"""
Full regression test suite for POST /chat and POST /chat/stream.

Usage:
    python -m scripts.test_chat                  # run all tests
    python -m scripts.test_chat --only chat      # only /chat tests
    python -m scripts.test_chat --only stream    # only /chat/stream tests
    python -m scripts.test_chat --fail-fast      # stop on first failure

Requirements: pip install httpx
"""

import argparse
import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Literal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import httpx
except ImportError:
    print("Missing dependency: pip install httpx")
    sys.exit(1)

BASE_URL = "http://localhost:8000"
TIMEOUT  = 120.0   # seconds per request
DELAY_MS = 2.0     # seconds between requests to avoid 429 rate limiting

# Phrases that only appear in genuine consent-denied/unauthorized responses
# These must be specific enough to NOT match normal helpful replies
DENIED_PHRASES = [
    "unable to process your request",
    "consent preferences are up to date",
    "consent not granted",
    "patient not found",
    "authorization check failed",
    "we're unable to process",
]

# ──────────────────────────────────────────────────────────────────────────────
# Test definition
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ChatTest:
    name:        str
    message:     str
    patient_id:  str
    tenant_id:   str  = "TENANT001"
    session_id:  str  = "TEST-SESSION"
    endpoint:    Literal["chat", "stream", "both"] = "both"
    expect_intent:   str | None = None   # if set, assert reply intent matches
    expect_keywords: list[str]  = field(default_factory=list)   # words expected in reply
    expect_denied:   bool = False        # True → expect consent-denied response
    tag:         str = ""               # label for grouping output


# ──────────────────────────────────────────────────────────────────────────────
# Test cases
# ──────────────────────────────────────────────────────────────────────────────

TESTS: list[ChatTest] = [

    # ── APPOINTMENT AGENT (PAT001) ────────────────────────────────────────────
    ChatTest("APT-01 Next appointment",
             "When is my next appointment?", "PAT001",
             expect_intent="appointment", expect_keywords=["appointment"],
             tag="appointment"),

    ChatTest("APT-02 Appointment history",
             "Show me all my past appointments", "PAT001",
             expect_intent="appointment", expect_keywords=["appointment"],
             tag="appointment"),

    ChatTest("APT-03 Scheduled appointments",
             "Do I have any upcoming appointments scheduled?", "PAT001",
             expect_intent="appointment", tag="appointment"),

    ChatTest("APT-04 Cancelled appointment",
             "Was my specialist referral appointment cancelled?", "PAT001",
             expect_keywords=["cancel"], tag="appointment"),

    ChatTest("APT-05 Appointment count",
             "How many appointments have I had in total?", "PAT001",
             tag="appointment"),

    ChatTest("APT-06 PAT002 upcoming",
             "When is my next appointment?", "PAT002",
             expect_intent="appointment", tag="appointment"),

    ChatTest("APT-07 Schedule new appointment",
             "I need to schedule an appointment with a specialist", "PAT001",
             expect_intent="appointment", tag="appointment"),

    ChatTest("APT-08 Annual checkup",
             "Did I already have my annual checkup this year?", "PAT001",
             expect_keywords=["annual", "checkup", "appointment"],
             tag="appointment"),

    # ── BILLING AGENT ────────────────────────────────────────────────────────
    ChatTest("BILL-01 Current balance PAT001",
             "What is my current outstanding balance?", "PAT001",
             expect_intent="billing", expect_keywords=["balance"],
             tag="billing"),

    ChatTest("BILL-02 Overdue bills PAT002",
             "Do I have any overdue bills?", "PAT002",
             expect_intent="billing", expect_keywords=["bill"],
             tag="billing"),

    ChatTest("BILL-03 Billing history",
             "Show me my full billing history", "PAT001",
             expect_intent="billing", tag="billing"),

    ChatTest("BILL-04 How much do I owe",
             "How much do I owe in total?", "PAT001",
             expect_intent="billing", expect_keywords=["$"],
             tag="billing"),

    ChatTest("BILL-05 Payment status",
             "Was my cardiology bill paid?", "PAT002",
             expect_keywords=["paid"], tag="billing"),

    ChatTest("BILL-06 Unpaid charges",
             "What charges are still unpaid?", "PAT001",
             expect_intent="billing", tag="billing"),

    ChatTest("BILL-07 Lab charge",
             "I see a charge for a lab test, what is it for?", "PAT001",
             tag="billing"),

    # ── INSURANCE AGENT ──────────────────────────────────────────────────────
    ChatTest("INS-01 Claim denial reason",
             "Why was my insurance claim denied?", "PAT001",
             expect_intent="insurance",
             expect_keywords=["denied", "claim"],
             tag="insurance"),

    ChatTest("INS-02 Claim status EKG PAT002",
             "What is the status of my EKG claim?", "PAT002",
             expect_intent="insurance", expect_keywords=["claim"],
             tag="insurance"),

    ChatTest("INS-03 Insurance plan details PAT001",
             "What insurance plan am I on?", "PAT001",
             expect_intent="insurance",
             expect_keywords=["insurance", "plan"],
             tag="insurance"),

    ChatTest("INS-04 Insurance plan details PAT002",
             "What is my insurance provider?", "PAT002",
             expect_keywords=["Aetna"], tag="insurance"),

    ChatTest("INS-05 Coverage MRI — Pinecone knowledge",
             "Does my insurance cover MRI scans?", "PAT001",
             expect_keywords=["cover", "mri"],
             tag="insurance"),

    ChatTest("INS-06 All claims list",
             "Show me all my insurance claims", "PAT001",
             expect_intent="insurance", tag="insurance"),

    ChatTest("INS-07 Approved claim",
             "Was my lab test claim approved?", "PAT001",
             expect_keywords=["approved"], tag="insurance"),

    ChatTest("INS-08 Paid cardiology claim",
             "Was the cardiology consultation claim paid?", "PAT002",
             expect_keywords=["cardiology", "claim"],
             tag="insurance"),

    # ── REFILL AGENT ─────────────────────────────────────────────────────────
    ChatTest("REF-01 Blood pressure refill",
             "I need a refill for my blood pressure medication", "PAT001",
             expect_intent="refill", tag="refill"),

    ChatTest("REF-02 Prescription refill general",
             "How do I request a prescription refill?", "PAT001",
             tag="refill"),

    ChatTest("REF-03 Controlled substance refill",
             "Can I get a refill without visiting the clinic?", "PAT001",
             tag="refill"),

    # ── CASE AGENT ───────────────────────────────────────────────────────────
    ChatTest("CASE-01 Open cases",
             "What open cases do I have?", "PAT001",
             expect_intent="case", expect_keywords=["case", "open"],
             tag="case"),

    ChatTest("CASE-02 Case summary appeal",
             "Give me a full summary of my claim appeal case", "PAT001",
             expect_intent="case", expect_keywords=["appeal", "claim"],
             tag="case"),

    ChatTest("CASE-03 PAT002 cases",
             "What cases are currently in review for me?", "PAT002",
             expect_intent="case", tag="case"),

    ChatTest("CASE-04 Patient 360 status",
             "Give me a complete overview of my healthcare status", "PAT001",
             expect_intent="case", tag="case"),

    # ── EVENT / TIMELINE AGENT ───────────────────────────────────────────────
    ChatTest("EVT-01 Last 30 days PAT001",
             "What happened in my last 30 days?", "PAT001",
             expect_keywords=["claim"],
             tag="timeline"),

    ChatTest("EVT-02 Full timeline PAT002",
             "Show me my full medical timeline", "PAT002",
             tag="timeline"),

    ChatTest("EVT-03 Why claim denied — root cause",
             "Why was my office visit claim denied?", "PAT001",
             expect_keywords=["denied", "claim"],
             tag="timeline"),

    ChatTest("EVT-04 Lab results",
             "What were my last lab results?", "PAT001",
             expect_keywords=["lab"],
             tag="timeline"),

    ChatTest("EVT-05 Why bill increased",
             "Why did my bill increase after my appointment?", "PAT001",
             tag="timeline"),

    ChatTest("EVT-06 What happened with EKG",
             "What happened during my cardiology visit?", "PAT002",
             expect_keywords=["EKG", "cardiology"],
             tag="timeline"),

    # ── PLANNER MULTI-INTENT ─────────────────────────────────────────────────
    ChatTest("PLN-01 Balance + appointment",
             "What is my balance and when is my next appointment?", "PAT001",
             expect_keywords=["balance", "appointment"],
             tag="planner"),

    ChatTest("PLN-02 Cases + billing",
             "What open cases do I have and what do I owe?", "PAT001",
             tag="planner"),

    ChatTest("PLN-03 Full patient summary",
             "Give me a complete summary: appointments, balance, open cases, and any claims",
             "PAT001", tag="planner"),

    ChatTest("PLN-04 Status of everything",
             "What is my current health status, billing status, and any pending claims?",
             "PAT002", tag="planner"),

    # ── KNOWLEDGE / PINECONE RETRIEVAL ───────────────────────────────────────
    ChatTest("KNW-01 Prior auth process",
             "How do I get prior authorization for a specialist visit?", "PAT001",
             expect_keywords=["prior", "authorization"],
             tag="knowledge"),

    ChatTest("KNW-02 Appeal process",
             "How do I appeal a denied insurance claim?", "PAT001",
             expect_keywords=["appeal"],
             tag="knowledge"),

    ChatTest("KNW-03 Cancellation policy",
             "What is the cancellation policy for appointments?", "PAT001",
             expect_keywords=["cancel", "hours"],
             tag="knowledge"),

    ChatTest("KNW-04 Preventive care coverage",
             "Is preventive care covered by my insurance?", "PAT001",
             tag="knowledge"),

    ChatTest("KNW-05 HIPAA rights",
             "What are my rights under HIPAA?", "PAT001",
             expect_keywords=["HIPAA", "health", "information"],
             tag="knowledge"),

    ChatTest("KNW-06 Pay bill options",
             "How can I pay my medical bill?", "PAT001",
             tag="knowledge"),

    # ── AUTHORIZATION / CONSENT ──────────────────────────────────────────────
    ChatTest("AUTH-01 Consent revoked PAT003",
             "When is my next appointment?", "PAT003",
             expect_denied=True, tag="auth"),

    ChatTest("AUTH-02 Unknown patient",
             "What is my balance?", "PAT999",
             expect_denied=True, tag="auth"),

    ChatTest("AUTH-03 Missing patient ID",
             "Show me my appointments", "",
             expect_denied=True, tag="auth"),

    # ── RISK / ESCALATION ────────────────────────────────────────────────────
    ChatTest("RISK-01 Health concern",
             "I have been having severe chest pain for the past hour", "PAT001",
             tag="risk"),

    ChatTest("RISK-02 Emergency symptoms",
             "I think I am having a stroke, what should I do?", "PAT001",
             tag="risk"),

    # ── EDGE CASES ───────────────────────────────────────────────────────────
    ChatTest("EDGE-01 Very short message",
             "help", "PAT001",
             tag="edge"),

    ChatTest("EDGE-02 Greeting",
             "Hello, how are you?", "PAT001",
             tag="edge"),

    ChatTest("EDGE-03 Unrelated question",
             "What is the weather like today?", "PAT001",
             tag="edge"),

    ChatTest("EDGE-04 Long complex message",
             "I had an appointment with Dr. Smith last month and afterward I received two bills, "
             "one for the office visit and one for lab work. The lab bill was partially paid by "
             "insurance but the office visit claim was denied. I want to understand why and what "
             "my current total balance is, and also whether I have any upcoming appointments.",
             "PAT001", tag="edge"),

    ChatTest("EDGE-05 Non-English message",
             "¿Cuándo es mi próxima cita?", "PAT001",
             tag="edge"),
]

# Stream-only tests (20+)
STREAM_TESTS: list[ChatTest] = [
    ChatTest("STR-01 Next appointment",
             "When is my next appointment?", "PAT001",
             endpoint="stream", tag="stream"),
    ChatTest("STR-02 Balance",
             "What is my current balance?", "PAT001",
             endpoint="stream", tag="stream"),
    ChatTest("STR-03 Claim denial",
             "Why was my claim denied?", "PAT001",
             endpoint="stream", tag="stream"),
    ChatTest("STR-04 Lab results",
             "What were my last lab results?", "PAT001",
             endpoint="stream", tag="stream"),
    ChatTest("STR-05 Insurance plan",
             "What insurance plan am I on?", "PAT001",
             endpoint="stream", tag="stream"),
    ChatTest("STR-06 Open cases",
             "What open cases do I have?", "PAT001",
             endpoint="stream", tag="stream"),
    ChatTest("STR-07 Timeline",
             "Show me my medical timeline", "PAT001",
             endpoint="stream", tag="stream"),
    ChatTest("STR-08 Prior auth",
             "How do I get prior authorization?", "PAT001",
             endpoint="stream", tag="stream"),
    ChatTest("STR-09 Billing history",
             "Show me my billing history", "PAT001",
             endpoint="stream", tag="stream"),
    ChatTest("STR-10 Overdue bills PAT002",
             "Do I have overdue bills?", "PAT002",
             endpoint="stream", tag="stream"),
    ChatTest("STR-11 EKG claim PAT002",
             "What is the status of my EKG claim?", "PAT002",
             endpoint="stream", tag="stream"),
    ChatTest("STR-12 Cardiology visit PAT002",
             "What happened during my cardiology visit?", "PAT002",
             endpoint="stream", tag="stream"),
    ChatTest("STR-13 Refill request",
             "I need a prescription refill", "PAT001",
             endpoint="stream", tag="stream"),
    ChatTest("STR-14 Appeal process",
             "How do I appeal a denied claim?", "PAT001",
             endpoint="stream", tag="stream"),
    ChatTest("STR-15 Patient 360",
             "Give me a complete overview of my status", "PAT001",
             endpoint="stream", tag="stream"),
    ChatTest("STR-16 Consent denied PAT003",
             "What are my appointments?", "PAT003",
             endpoint="stream", expect_denied=True, tag="stream"),
    ChatTest("STR-17 Multi-intent",
             "What is my balance and next appointment?", "PAT001",
             endpoint="stream", tag="stream"),
    ChatTest("STR-18 HIPAA rights",
             "What are my HIPAA rights?", "PAT001",
             endpoint="stream", tag="stream"),
    ChatTest("STR-19 Risk escalation",
             "I am having severe chest pain right now", "PAT001",
             endpoint="stream", tag="stream"),
    ChatTest("STR-20 PAT002 full summary",
             "Give me a full summary of my healthcare status", "PAT002",
             endpoint="stream", tag="stream"),
    ChatTest("STR-21 Unknown patient",
             "What is my balance?", "PAT999",
             endpoint="stream", expect_denied=True, tag="stream"),
    ChatTest("STR-22 Cancellation policy",
             "What is your cancellation policy?", "PAT001",
             endpoint="stream", tag="stream"),
]


# ──────────────────────────────────────────────────────────────────────────────
# Result tracking
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class TestResult:
    test:        ChatTest
    endpoint:    str
    passed:      bool
    reply:       str   = ""
    intent:      str   = ""
    status_code: int   = 0
    duration_ms: float = 0.0
    error:       str   = ""
    failures:    list[str] = field(default_factory=list)


# ──────────────────────────────────────────────────────────────────────────────
# Assertion helpers
# ──────────────────────────────────────────────────────────────────────────────

def check_result(test: ChatTest, reply: str, intent: str, endpoint: str) -> list[str]:
    """Return list of failure messages (empty = passed)."""
    failures = []
    reply_lower = reply.lower()

    if not reply or len(reply.strip()) < 5:
        failures.append("Empty or very short reply")
        return failures

    if test.expect_denied:
        if not any(p in reply_lower for p in DENIED_PHRASES):
            failures.append(
                f"Expected consent-denied message, got: {reply[:120]}"
            )
    else:
        if test.expect_intent and intent and intent != test.expect_intent:
            failures.append(
                f"Intent mismatch: expected '{test.expect_intent}', got '{intent}'"
            )

        for kw in test.expect_keywords:
            if kw.lower() not in reply_lower:
                failures.append(f"Expected keyword '{kw}' not found in reply")

    return failures


# ──────────────────────────────────────────────────────────────────────────────
# HTTP runners
# ──────────────────────────────────────────────────────────────────────────────

async def run_chat(client: httpx.AsyncClient, test: ChatTest, base_url: str) -> TestResult:
    payload = {
        "message":    test.message,
        "patient_id": test.patient_id,
        "tenant_id":  test.tenant_id,
        "session_id": test.session_id,
    }
    t0 = time.perf_counter()
    try:
        resp = await client.post(f"{base_url}/chat", json=payload, timeout=TIMEOUT)
        duration_ms = (time.perf_counter() - t0) * 1000
        data = resp.json()
        reply  = data.get("reply", "")
        intent = data.get("intent", "")
        failures = check_result(test, reply, intent, "chat")
        return TestResult(
            test=test, endpoint="chat",
            passed=resp.status_code == 200 and not failures,
            reply=reply, intent=intent,
            status_code=resp.status_code,
            duration_ms=duration_ms,
            failures=failures,
        )
    except Exception as exc:
        duration_ms = (time.perf_counter() - t0) * 1000
        return TestResult(test=test, endpoint="chat", passed=False,
                          duration_ms=duration_ms, error=str(exc),
                          failures=[f"Exception: {exc}"])


async def run_stream(client: httpx.AsyncClient, test: ChatTest, base_url: str) -> TestResult:
    payload = {
        "message":    test.message,
        "patient_id": test.patient_id,
        "tenant_id":  test.tenant_id,
        "session_id": test.session_id,
    }
    t0 = time.perf_counter()
    try:
        async with client.stream("POST", f"{base_url}/chat/stream",
                                 json=payload, timeout=TIMEOUT) as resp:
            chunks = []
            async for chunk in resp.aiter_text():
                chunks.append(chunk)
        duration_ms = (time.perf_counter() - t0) * 1000
        reply = "".join(chunks).strip()
        failures = check_result(test, reply, "", "stream")
        return TestResult(
            test=test, endpoint="stream",
            passed=resp.status_code == 200 and not failures,
            reply=reply, status_code=resp.status_code,
            duration_ms=duration_ms, failures=failures,
        )
    except Exception as exc:
        duration_ms = (time.perf_counter() - t0) * 1000
        return TestResult(test=test, endpoint="stream", passed=False,
                          duration_ms=duration_ms, error=str(exc),
                          failures=[f"Exception: {exc}"])


# ──────────────────────────────────────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────────────────────────────────────

def tag_color(tag: str) -> str:
    colors = {
        "appointment": "\033[94m", "billing": "\033[93m",
        "insurance":   "\033[96m", "refill":  "\033[95m",
        "case":        "\033[92m", "timeline":"\033[36m",
        "planner":     "\033[35m", "knowledge":"\033[34m",
        "auth":        "\033[91m", "risk":    "\033[31m",
        "edge":        "\033[90m", "stream":  "\033[33m",
    }
    return colors.get(tag, "\033[0m")

RESET = "\033[0m"
GREEN = "\033[32m"
RED   = "\033[31m"
GREY  = "\033[90m"
BOLD  = "\033[1m"


def print_result(r: TestResult, verbose: bool = False):
    icon    = f"{GREEN}✓{RESET}" if r.passed else f"{RED}✗{RESET}"
    ep_tag  = f"[{r.endpoint:6s}]"
    dur     = f"{r.duration_ms:6.0f}ms"
    color   = tag_color(r.test.tag)
    tag_str = f"{color}[{r.test.tag}]{RESET}" if r.test.tag else ""

    print(f"  {icon} {ep_tag} {dur}  {tag_str:20s} {r.test.name}")

    if not r.passed:
        for f in r.failures:
            print(f"      {RED}→ {f}{RESET}")
        if r.error:
            print(f"      {RED}→ Error: {r.error}{RESET}")
        if verbose and r.reply:
            print(f"      {GREY}Reply: {r.reply[:200]}{RESET}")


async def run_all(only: str | None, fail_fast: bool, verbose: bool, base_url: str = BASE_URL):
    results: list[TestResult] = []

    # Build list of (test, endpoint) pairs
    jobs: list[tuple[ChatTest, str]] = []

    if only in (None, "chat"):
        for t in TESTS:
            if t.endpoint in ("chat", "both"):
                jobs.append((t, "chat"))

    if only in (None, "stream"):
        for t in TESTS:
            if t.endpoint in ("stream", "both"):
                jobs.append((t, "stream"))
        for t in STREAM_TESTS:
            jobs.append((t, "stream"))

    total = len(jobs)
    print(f"\n{BOLD}PatientCare API — Chat Regression Suite{RESET}")
    print(f"Target  : {base_url}")
    print(f"Tests   : {total}")
    print(f"Mode    : {'fail-fast' if fail_fast else 'run-all'}\n")
    print("─" * 70)

    async with httpx.AsyncClient() as client:
        for idx, (test, endpoint) in enumerate(jobs, 1):
            print(f"  [{idx:3d}/{total}] Running {test.name} …", end="\r", flush=True)

            if endpoint == "chat":
                r = await run_chat(client, test, base_url)
            else:
                r = await run_stream(client, test, base_url)

            results.append(r)
            # Overwrite the running line
            print(" " * 70, end="\r")
            print_result(r, verbose=verbose)

            if fail_fast and not r.passed:
                print(f"\n{RED}Stopped at first failure (--fail-fast){RESET}\n")
                break

            await asyncio.sleep(DELAY_MS)

    # ── Summary ──────────────────────────────────────────────────────────────
    passed  = sum(1 for r in results if r.passed)
    failed  = sum(1 for r in results if not r.passed)
    avg_dur = sum(r.duration_ms for r in results) / len(results) if results else 0

    print("\n" + "─" * 70)
    print(f"{BOLD}Results{RESET}")
    print(f"  {GREEN}Passed : {passed}{RESET}")
    print(f"  {RED}Failed : {failed}{RESET}")
    print(f"  Total  : {len(results)}")
    print(f"  Avg    : {avg_dur:.0f} ms/request")

    if failed:
        print(f"\n{BOLD}{RED}Failed tests:{RESET}")
        for r in results:
            if not r.passed:
                print(f"  • [{r.endpoint}] {r.test.name}")
                for f in r.failures:
                    print(f"      → {f}")

    print()
    return failed


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PatientCare chat regression tests")
    parser.add_argument("--only",      choices=["chat", "stream"],
                        help="Run only /chat or /chat/stream tests")
    parser.add_argument("--fail-fast", action="store_true",
                        help="Stop on first failure")
    parser.add_argument("--verbose",   action="store_true",
                        help="Print reply text for failed tests")
    parser.add_argument("--url",       default=BASE_URL,
                        help=f"Base URL (default: {BASE_URL})")
    args = parser.parse_args()

    url = args.url.rstrip("/")
    failed = asyncio.run(run_all(args.only, args.fail_fast, args.verbose, base_url=url))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
