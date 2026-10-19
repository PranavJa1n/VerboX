import uuid
import os
from datetime import datetime
from backend.judge.llm_client import judge
from backend.judge.prompt import build_judge_prompt, PROMPT_VERSION
from backend.judge.schema import Flag, Verdict
from dotenv import load_dotenv

load_dotenv()

def evaluate(step: dict) -> Verdict:

    prompt = build_judge_prompt(step)
    raw_output = judge(prompt)
    flags = [Flag(type=f.type, severity=f.severity, reason=f.reason) for f in raw_output.flags]
    print(f"✅ [Module 1] LLM Audit Complete. Found {len(flags)} flags.")
    return Verdict(
        verdict_id = str(uuid.uuid4()),
        trace_id = step.get("trace_id"),
        span_id = step.get("span_id"),
        flags = flags,
        judge_model = 'gpt-4o',
        prompt_version = PROMPT_VERSION,
        evaluated_at = datetime.now()
    )