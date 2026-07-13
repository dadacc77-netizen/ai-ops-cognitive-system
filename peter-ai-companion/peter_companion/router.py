from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Tuple

FORMAL_VIDEO_TRIGGER = "【正式生成影片】"


class InteractionMode(str, Enum):
    VOICE_COMPANION = "voice_companion"
    QUIET_SLOW = "quiet_slow"


class ExecutionMode(str, Enum):
    PLANNING = "planning"
    FORMAL_GENERATION = "formal_generation"


@dataclass(frozen=True)
class GateStatus:
    script_final: bool = False
    storyboard_final: bool = False
    generation_confirmed: bool = False

    @property
    def all_passed(self) -> bool:
        return self.script_final and self.storyboard_final and self.generation_confirmed

    @property
    def missing(self) -> Tuple[str, ...]:
        missing = []
        if not self.script_final:
            missing.append("腳本定稿門")
        if not self.storyboard_final:
            missing.append("分鏡定稿門")
        if not self.generation_confirmed:
            missing.append("生成確認門")
        return tuple(missing)


@dataclass(frozen=True)
class RouteDecision:
    interaction_mode: InteractionMode
    execution_mode: ExecutionMode
    safety_stop: bool
    supervisor_access: bool
    codex_candidate: bool
    cloud_intent: bool
    formal_trigger_present: bool
    missing_gates: Tuple[str, ...] = field(default_factory=tuple)
    notices: Tuple[str, ...] = field(default_factory=tuple)


QUIET_PATTERNS = (
    r"安靜\s*慢慢來",
    r"慢慢來",
    r"一次\s*(?:只做|一個|一件)",
    r"不要\s*(?:一次)?太多",
    r"先做一件",
)

NEGATIVE_SHARE_PATTERNS = (
    r"不要.*(?:分享|開放|給).*(?:主管|supervisor)",
    r"不准.*(?:主管|supervisor)",
    r"禁止.*(?:主管|supervisor)",
    r"不願意.*(?:主管|supervisor)",
)

POSITIVE_SHARE_PATTERNS = (
    r"(?:我)?同意.*(?:分享|開放|給).*(?:主管|supervisor)",
    r"(?:我)?授權.*(?:主管|supervisor)",
    r"可以.*(?:分享|開放|給).*(?:主管|supervisor)",
    r"讓.*(?:主管|supervisor).*(?:使用|查看|存取)",
    r"(?:主管|supervisor).*(?:可以|允許).*(?:使用|查看|存取)",
)

CODEX_TERMS = (
    "codex", "程式", "程式碼", "apps script", "github", "api",
    "自動化", "除錯", "debug", "測試", "版本管理", "批次處理",
    "部署", "後台系統",
)

CLOUD_TERMS = (
    "雲端", "資料夾", "上傳", "歸檔", "報表", "excel", "ppt",
    "powerpoint", "word", "pdf", "圖片", "影片", "檔案", "文件",
)

SECRET_PATTERNS = (
    r"(?i)\b(?:password|passwd|pwd)\s*[:=]\s*\S{4,}",
    r"密碼\s*(?:是|為|[:：=])\s*\S{4,}",
    r"驗證碼\s*(?:是|為|[:：=])\s*\d{4,8}",
    r"(?i)\b(?:api[_ -]?key|token|secret)\s*[:=]\s*[A-Za-z0-9_\-]{8,}",
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    r"\bsk-[A-Za-z0-9_\-]{12,}\b",
)


def _matches_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(term.lower() in lower for term in terms)


def _supervisor_consent(text: str) -> bool:
    if _matches_any(text, NEGATIVE_SHARE_PATTERNS):
        return False
    return _matches_any(text, POSITIVE_SHARE_PATTERNS)


def route_request(text: str, gates: GateStatus | None = None) -> RouteDecision:
    """Route a Peter request through the approved deterministic policy layer."""
    if not isinstance(text, str):
        raise TypeError("text 必須是字串")

    gates = gates or GateStatus()
    normalized = text.strip()

    quiet = _matches_any(normalized, QUIET_PATTERNS)
    safety_stop = _matches_any(normalized, SECRET_PATTERNS)
    formal_trigger_present = FORMAL_VIDEO_TRIGGER in normalized
    supervisor_access = _supervisor_consent(normalized)
    codex_candidate = _contains_any(normalized, CODEX_TERMS)
    cloud_intent = _contains_any(normalized, CLOUD_TERMS)

    interaction_mode = InteractionMode.QUIET_SLOW if quiet else InteractionMode.VOICE_COMPANION
    execution_mode = ExecutionMode.PLANNING
    missing_gates: Tuple[str, ...] = ()
    notices = []

    if formal_trigger_present:
        if gates.all_passed and not safety_stop:
            execution_mode = ExecutionMode.FORMAL_GENERATION
        else:
            missing_gates = gates.missing
            if missing_gates:
                notices.append("正式生成已鎖定：三道門尚未全部通過。")
            if safety_stop:
                notices.append("Safety Stop：偵測到疑似敏感資訊。")

    if safety_stop and "Safety Stop：偵測到疑似敏感資訊。" not in notices:
        notices.append("Safety Stop：偵測到疑似敏感資訊。")

    if cloud_intent and not supervisor_access:
        notices.append("雲端權限維持私人；未取得主管分享授權。")

    if interaction_mode is InteractionMode.QUIET_SLOW:
        notices.append("安靜慢慢來：只提供一個主要下一步。")

    return RouteDecision(
        interaction_mode=interaction_mode,
        execution_mode=execution_mode,
        safety_stop=safety_stop,
        supervisor_access=supervisor_access,
        codex_candidate=codex_candidate,
        cloud_intent=cloud_intent,
        formal_trigger_present=formal_trigger_present,
        missing_gates=missing_gates,
        notices=tuple(notices),
    )
