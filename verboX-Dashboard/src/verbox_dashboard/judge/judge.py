import uuid
import os
from datetime import datetime
from verbox_dashboard.judge.llm_client import judge
from verbox_dashboard.judge.prompt import build_judge_prompt, PROMPT_VERSION
from verbox_dashboard.judge.schema import Flag, Verdict
from dotenv import load_dotenv

load_dotenv()

def evaluate(step: dict) -> Verdict:

    prompt = build_judge_prompt(step)
    raw_output = judge(prompt)
    flags = [Flag(type=f.type, severity=f.severity, reason=f.reason) for f in raw_output.flags]

    return Verdict(
        verdict_id = str(uuid.uuid4),
        trace_id = step.get("trace_id"),
        span_id = step.get("span_id"),
        flags = flags,
        judge_model = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        prompt_version = PROMPT_VERSION,
        evaluated_at = datetime.now()
    )