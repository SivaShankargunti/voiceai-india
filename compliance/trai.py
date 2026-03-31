"""
TRAI Compliance Engine
Handles all Indian telecom regulatory requirements for AI calling.

Covers:
- Calling hours (10 AM - 7 PM IST)
- DND/NCPR registry checking
- AI disclosure requirements
- Number series routing (140 vs 1600)
- Opt-out handling
- Call audit logging
"""

from datetime import datetime, time
from enum import Enum
from dataclasses import dataclass, field
import json
import os

import pytz

IST = pytz.timezone("Asia/Kolkata")


class CallType(Enum):
    PROMOTIONAL = "promotional"      # Uses 140-series numbers
    TRANSACTIONAL = "transactional"  # Uses 1600-series numbers
    SERVICE = "service"              # Uses 1600-series numbers


class CallOutcome(Enum):
    ANSWERED = "answered"
    NO_ANSWER = "no_answer"
    BUSY = "busy"
    OPTED_OUT = "opted_out"
    DND_BLOCKED = "dnd_blocked"
    OUTSIDE_HOURS = "outside_hours"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ComplianceCheck:
    """Result of a pre-call compliance check"""
    can_call: bool
    reasons: list[str] = field(default_factory=list)
    within_hours: bool = False
    dnd_clear: bool = False
    consent_verified: bool = False
    number_series: str = ""
    disclosure_text_hi: str = ""
    disclosure_text_en: str = ""


@dataclass
class CallLog:
    """Audit trail record for every call"""
    call_id: str
    phone: str
    business_id: str
    business_name: str
    call_type: str
    timestamp: str
    duration_seconds: int
    outcome: str
    ai_disclosed: bool
    opt_out_offered: bool
    consent_type: str
    language: str
    transcript_summary: str = ""


class TRAIComplianceEngine:
    """
    Core TRAI compliance engine.
    Every outbound AI call MUST pass through this before dialing.
    """

    # TRAI mandated calling hours
    CALL_START_HOUR = 10  # 10:00 AM IST
    CALL_END_HOUR = 19    # 7:00 PM IST
    SAFE_START_HOUR = 10  # Buffer: 10:30 AM
    SAFE_START_MINUTE = 30
    SAFE_END_HOUR = 18    # Buffer: 6:30 PM
    SAFE_END_MINUTE = 30

    # DND registry (in production: sync from NCPR API daily)
    _dnd_numbers: set[str] = set()

    # Opted-out numbers (internal list — honor within 24-48 hours)
    _opted_out_numbers: set[str] = set()

    # Call logs for audit
    _call_logs: list[CallLog] = []

    def __init__(self, business_name: str, business_id: str = ""):
        self.business_name = business_name
        self.business_id = business_id
        self._load_dnd_list()
        self._load_opted_out_list()

    # ===== CALLING HOURS =====

    def is_within_calling_hours(self, use_safe_buffer: bool = True) -> bool:
        """Check if current IST time is within TRAI allowed hours."""
        now = datetime.now(IST)

        if use_safe_buffer:
            start = time(self.SAFE_START_HOUR, self.SAFE_START_MINUTE)
            end = time(self.SAFE_END_HOUR, self.SAFE_END_MINUTE)
        else:
            start = time(self.CALL_START_HOUR, 0)
            end = time(self.CALL_END_HOUR, 0)

        current_time = now.time()
        return start <= current_time <= end

    def time_until_next_window(self) -> str:
        """How long until the next calling window opens."""
        now = datetime.now(IST)
        current_time = now.time()

        if current_time < time(self.CALL_START_HOUR, 0):
            hours = self.CALL_START_HOUR - now.hour
            minutes = -now.minute if now.minute > 0 else 0
            return f"{hours}h {abs(minutes)}m until 10:00 AM IST"
        elif current_time >= time(self.CALL_END_HOUR, 0):
            hours = 24 - now.hour + self.CALL_START_HOUR
            return f"{hours}h until tomorrow 10:00 AM IST"
        else:
            return "Calling window is currently OPEN"

    # ===== DND REGISTRY =====

    def is_dnd_registered(self, phone: str) -> bool:
        """Check if number is on Do Not Disturb registry."""
        clean_phone = self._clean_phone(phone)
        return clean_phone in self._dnd_numbers

    def add_to_dnd(self, phone: str):
        """Add number to local DND list."""
        self._dnd_numbers.add(self._clean_phone(phone))
        self._save_dnd_list()

    # ===== OPT-OUT HANDLING =====

    def is_opted_out(self, phone: str) -> bool:
        """Check if number has opted out of calls."""
        return self._clean_phone(phone) in self._opted_out_numbers

    def process_opt_out(self, phone: str) -> dict:
        """
        Process an opt-out request. TRAI requires:
        - Honor within 24-48 hours
        - Sync with DND preferences
        - Confirm removal to the caller
        """
        clean_phone = self._clean_phone(phone)
        self._opted_out_numbers.add(clean_phone)
        self._save_opted_out_list()
        return {
            "phone": clean_phone,
            "opted_out": True,
            "message": "Number removed from calling list. Will be honored within 24 hours.",
            "timestamp": datetime.now(IST).isoformat(),
        }

    # ===== AI DISCLOSURE =====

    def get_disclosure_text(self, language: str = "hi", call_type: CallType = CallType.SERVICE) -> str:
        """
        Get mandatory AI disclosure text.
        TRAI requires: identify as AI + state business name + offer opt-out within 30 seconds.
        """
        if language == "hi":
            return (
                f"Namaste! Yeh ek AI assistant call hai {self.business_name} ki taraf se. "
                f"Agar aap yeh call nahi chahte, toh kripya 9 dabayein ya 'band karo' kahein."
            )
        elif language == "te":
            return (
                f"Namaskaram! Idi {self.business_name} nundi AI assistant call. "
                f"Meeru ee call vaddu anukuṇṭe, dayachesi 9 noppandi."
            )
        elif language == "ta":
            return (
                f"Vanakkam! Idhu {self.business_name} irundu AI assistant call. "
                f"Neengal idha virumbavillai endraal, thayavu seidhu 9 ai azhuthavum."
            )
        else:
            return (
                f"Hello! This is an AI assistant calling from {self.business_name}. "
                f"If you do not wish to receive this call, please press 9 or say 'stop'."
            )

    # ===== NUMBER SERIES =====

    def get_number_series(self, call_type: CallType) -> str:
        """
        Determine which number series to use per TRAI regulations.
        140-series: promotional calls
        1600-series: transactional/service calls
        """
        if call_type == CallType.PROMOTIONAL:
            return "140"
        return "1600"

    # ===== PRE-CALL VALIDATION =====

    def validate_call(
        self,
        phone: str,
        call_type: CallType = CallType.SERVICE,
        language: str = "hi",
        has_consent: bool = False,
    ) -> ComplianceCheck:
        """
        Complete pre-call compliance check.
        Returns whether the call can proceed and why/why not.
        """
        reasons = []
        within_hours = self.is_within_calling_hours()
        dnd_clear = not self.is_dnd_registered(phone)
        opted_out = self.is_opted_out(phone)

        if not within_hours:
            reasons.append(f"Outside TRAI calling hours (10 AM - 7 PM IST). {self.time_until_next_window()}")

        if not dnd_clear:
            reasons.append("Number is registered on DND/NCPR registry")

        if opted_out:
            reasons.append("Number has opted out of calls from this business")
            dnd_clear = False

        if call_type == CallType.PROMOTIONAL and not has_consent:
            reasons.append("Promotional calls require explicit prior consent")

        can_call = within_hours and dnd_clear and not opted_out
        if call_type == CallType.PROMOTIONAL:
            can_call = can_call and has_consent

        return ComplianceCheck(
            can_call=can_call,
            reasons=reasons,
            within_hours=within_hours,
            dnd_clear=dnd_clear,
            consent_verified=has_consent,
            number_series=self.get_number_series(call_type),
            disclosure_text_hi=self.get_disclosure_text("hi", call_type),
            disclosure_text_en=self.get_disclosure_text("en", call_type),
        )

    # ===== CALL LOGGING =====

    def log_call(
        self,
        call_id: str,
        phone: str,
        duration_seconds: int,
        outcome: CallOutcome,
        call_type: CallType = CallType.SERVICE,
        language: str = "hi",
        transcript_summary: str = "",
    ) -> CallLog:
        """
        Log every call for TRAI audit compliance.
        Must record: who, when, how long, outcome, disclosure status.
        """
        log = CallLog(
            call_id=call_id,
            phone=self._clean_phone(phone),
            business_id=self.business_id,
            business_name=self.business_name,
            call_type=call_type.value,
            timestamp=datetime.now(IST).isoformat(),
            duration_seconds=duration_seconds,
            outcome=outcome.value,
            ai_disclosed=True,
            opt_out_offered=True,
            consent_type="service" if call_type != CallType.PROMOTIONAL else "explicit",
            language=language,
            transcript_summary=transcript_summary,
        )
        self._call_logs.append(log)
        self._save_call_log(log)
        return log

    def get_call_logs(self, limit: int = 50) -> list[CallLog]:
        """Get recent call logs for audit."""
        return self._call_logs[-limit:]

    # ===== OPT-OUT DETECTION =====

    def check_opt_out_keywords(self, text: str) -> bool:
        """
        Check if user's speech contains opt-out keywords.
        Must handle Hindi, English, and Hinglish.
        """
        opt_out_keywords = [
            # English
            "stop", "unsubscribe", "remove me", "don't call", "do not call",
            "opt out", "no more calls", "stop calling",
            # Hindi
            "band karo", "mat karo", "nahi chahiye", "ruko",
            "phone mat karo", "call mat karo", "band", "bas",
            # Telugu
            "aapandi", "vaddu", "call cheyyakandi",
            # Tamil
            "niruthungal", "vendam", "call pannatheenga",
        ]
        text_lower = text.lower().strip()
        return any(keyword in text_lower for keyword in opt_out_keywords)

    # ===== PRIVATE HELPERS =====

    def _clean_phone(self, phone: str) -> str:
        """Normalize phone number to 10-digit format."""
        phone = phone.strip().replace(" ", "").replace("-", "")
        if phone.startswith("+91"):
            phone = phone[3:]
        elif phone.startswith("91") and len(phone) == 12:
            phone = phone[2:]
        elif phone.startswith("0"):
            phone = phone[1:]
        return phone

    def _load_dnd_list(self):
        """Load DND list from file."""
        dnd_file = os.path.join(os.path.dirname(__file__), "dnd_numbers.json")
        if os.path.exists(dnd_file):
            with open(dnd_file, "r") as f:
                self._dnd_numbers = set(json.load(f))

    def _save_dnd_list(self):
        """Save DND list to file."""
        dnd_file = os.path.join(os.path.dirname(__file__), "dnd_numbers.json")
        with open(dnd_file, "w") as f:
            json.dump(list(self._dnd_numbers), f)

    def _load_opted_out_list(self):
        """Load opted-out numbers from file."""
        opt_file = os.path.join(os.path.dirname(__file__), "opted_out.json")
        if os.path.exists(opt_file):
            with open(opt_file, "r") as f:
                self._opted_out_numbers = set(json.load(f))

    def _save_opted_out_list(self):
        """Save opted-out numbers to file."""
        opt_file = os.path.join(os.path.dirname(__file__), "opted_out.json")
        with open(opt_file, "w") as f:
            json.dump(list(self._opted_out_numbers), f)

    def _save_call_log(self, log: CallLog):
        """Append call log to file."""
        log_file = os.path.join(os.path.dirname(__file__), "call_logs.jsonl")
        with open(log_file, "a") as f:
            f.write(json.dumps(vars(log)) + "\n")