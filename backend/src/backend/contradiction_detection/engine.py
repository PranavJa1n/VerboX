import itertools
from backend.contradiction_detection.stage1 import Stage1
from backend.contradiction_detection.stage2 import Stage2
from backend.contradiction_detection.schema import ContradictionReport

class AgnosticContradictionEngine:
    def __init__(self):
        self.stage1 = Stage1()
        self.stage2 = Stage2()

    def analyze_swarm_claims(self, claims: list[str]) -> list[dict]:
        """
        Accepts N claims from N unknown agents.
        Returns a list of all detected contradictions.
        """
        detected_contradictions = []

        # Generate every possible unique pair of claims from the swarm (N choose 2)
        all_pairs = list(itertools.combinations(claims, 2))

        for statement_a, statement_b in all_pairs:
            pair = [statement_a, statement_b]
            
            # STAGE 1: Fast NLP Noun Overlap
            if self.stage1.check(pair):
                
                # STAGE 2: Azure LLM Logic Check
                report: ContradictionReport = self.stage2.check(pair)
                
                if report.is_contradictory:
                    detected_contradictions.append({
                        "statement_a": statement_a,
                        "statement_b": statement_b,
                        "severity": report.confidence_score,
                        "reasoning": report.reasoning
                    })

        return detected_contradictions