import numpy as np
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class WearableReading:
    hrv_ms: float       # Heart Rate Variability in milliseconds
    sleep_hrs: float    # Sleep duration in hours
    rhr_bpm: int        # Resting Heart Rate in bpm
    steps: int          # Daily step count

class BurnoutBiomarker:
    BASELINES = {"hrv": 55, "sleep": 7.5, "rhr": 62, "steps": 8000}
    WEIGHTS   = {"hrv": 0.35, "sleep": 0.25, "rhr": 0.25, "steps": 0.15}

    def personalise(self, user_readings: List[WearableReading]):
        """Override population baselines with user's own 30-day avg."""
        if len(user_readings) >= 30:
            self.BASELINES["hrv"]   = np.mean([r.hrv_ms for r in user_readings])
            self.BASELINES["sleep"] = np.mean([r.sleep_hrs for r in user_readings])
            self.BASELINES["rhr"]   = np.mean([r.rhr_bpm for r in user_readings])
            self.BASELINES["steps"] = np.mean([r.steps for r in user_readings])

    def score_day(self, r: WearableReading) -> Dict:
        signals = {
            "hrv"  : (self.BASELINES["hrv"]   - r.hrv_ms)    / self.BASELINES["hrv"],
            "sleep": (self.BASELINES["sleep"] - r.sleep_hrs) / self.BASELINES["sleep"],
            "rhr"  : (r.rhr_bpm - self.BASELINES["rhr"])    / self.BASELINES["rhr"],
            "steps": (self.BASELINES["steps"] - r.steps)    / self.BASELINES["steps"],
        }
        raw  = sum(self.WEIGHTS[k] * max(0, v) for k,v in signals.items())
        risk = round(min(100, raw * 100), 1)
        return {"risk": risk, "signals": signals}

    def rolling_risk(self, days: List[WearableReading]) -> float:
        return round(np.mean([self.score_day(d)["risk"] for d in days[-7:]]), 1)
    def interpret(self, score: float) -> str:
        if score >= 70: return "High — escalate to clinician"
        if score >= 45: return "Moderate — recommend check-in"
        return "Low — continue monitoring"