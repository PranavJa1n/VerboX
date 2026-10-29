import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from backend.utility.human_feedback import HumanFeedbackLoop
except ImportError:
    from backend.utility.human_feedback import HumanFeedbackLoop


async def test_feedback_loop():
    loop = HumanFeedbackLoop()

    loop.register_verdict({
        "verdict_id": "v_001",
        "trace_id": "t_001",
        "span_id": "s_001",
        "prompt_version": "v1",
        "flags": [{"type": "risky", "severity": 0.8, "reason": "High risk action"}],
    })

    label = await loop.submit_label(
        verdict_id="v_001",
        reviewer="pranav",
        reviewer_verdict="agree",
        correction_note="Pre-approved exception",
    )

    assert label.verdict_id == "v_001"
    assert label.reviewer_verdict.value == "agree"

    labels = await loop.get_all_labels()
    assert len(labels) == 1

    metrics = loop.calculate_agreement_metrics(labels, loop._verdicts)
    assert metrics["agreement_rate_pct"] == 100.0
    print("All assertions passed successfully!")


if __name__ == "__main__":
    asyncio.run(test_feedback_loop())
