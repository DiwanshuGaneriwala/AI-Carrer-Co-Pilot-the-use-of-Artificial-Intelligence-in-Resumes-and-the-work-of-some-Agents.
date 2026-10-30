from typing import List, Dict, Set

class SkillGapAnalyzer:
    ALIASES: Dict[str, str] = {
        "resct.js": "react",
        "reactjs": "react",
        "node.js": "node",
        "nodejs": "node",
        "postgres": "postgresql",
        "mango": "mongodb",
        "k8s": "kubernetes",
        "py": "python",
        "ts": "typescript",
        "js": "javascript",
        "aws": "aws",
        "rest": "rest api",
        "restful api": "rest api",
        "docker container": "docker",
    }

    def __init__(self, alias_map: Dict[str, str] = None):
        self.aliases = {**self.ALIASES, **(alias_map or {})}

    def _normalize(self, skill: str) -> str:
        s = skill.strip().lower()
        return self.aliases.get(s, s)

    def analyze(
            self,
            candidate_skills: List[str],
            required_skills: List[str],
            preferred_skills: List[str] = None
    ) -> Dict:
        preferred_skills = preferred_skills or []

        cand_map = {self._normalize(s): s for s in candidate_skills}
        req_map = {self._normalize(s): s for s in required_skills}
        pref_map = {self._normalize(s): s for s in preferred_skills}

        cand_keys: Set[str] = set(cand_map.keys())
        req_keys: Set[str] = set(req_map.keys())
        pref_keys: Set[str] = set(pref_map.keys())

        matched_req_keys = req_keys.intersection(cand_keys)
        missing_req_keys = req_keys - cand_keys

        matched_pref_keys = pref_keys.intersection(cand_keys)
        missing_pref_keys = pref_keys - cand_keys

        req_match_pct = (
            round((len(matched_req_keys) / len(req_keys)) * 100, 2)
            if req_keys else 100.0
        )
        pref_match_pct = (
            round((len(matched_pref_keys) / len(pref_keys)) * 100, 2)
            if pref_keys else 100.0
        )

        if req_keys and pref_keys:
            readiness_score = round(req_match_pct * 0.75 + pref_match_pct * 0.25, 2)
        else:
            readiness_score = req_match_pct

        return {
            "readiness_score": readiness_score,
            "required": {
                "match_percentage": req_match_pct,
                "matched": sorted([req_map[k] for k in matched_req_keys]),
                "missing": sorted([req_map[k] for k in missing_req_keys]),
            },
            "preferred": {
                "match_percentage": pref_match_pct,
                "matched": sorted([pref_map[k] for k in matched_pref_keys]),
                "missing": sorted([pref_map[k] for k in missing_pref_keys]),
            },
            "additional_candidate_skills": sorted(
                [cand_map[k] for k in cand_keys - req_keys - pref_keys]
            ),
        }