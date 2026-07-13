from __future__ import annotations

from pathlib import Path
import json
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
RELEASE = ROOT / "release"


def run_tests() -> tuple[bool, int, int]:
    suite = unittest.TestLoader().discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return result.wasSuccessful(), result.testsRun, len(result.failures) + len(result.errors)


def validate_contract() -> list[str]:
    errors: list[str] = []
    approved_name = "Peter AI Companion｜雙模式語音陪跑"
    for relative in ("README.md", "docs/01_PRODUCT_SPEC.md", "docs/02_SYSTEM_PROMPT.md"):
        content = (ROOT / relative).read_text(encoding="utf-8")
        if approved_name not in content:
            errors.append(f"{relative}: 缺少正式名稱")

    prompt = (ROOT / "docs/02_SYSTEM_PROMPT.md").read_text(encoding="utf-8")
    for required in (
        "【正式生成影片】",
        "腳本定稿門",
        "分鏡定稿門",
        "生成確認門",
        "權限預設私人",
        "Safety Stop",
    ):
        if required not in prompt:
            errors.append(f"System Prompt 缺少：{required}")
    return errors


def main() -> int:
    started = time.time()
    contract_errors = validate_contract()
    ok, tests_run, failures = run_tests()
    status = "PASS" if ok and not contract_errors else "FAIL"
    report = {
        "product": "Peter AI Companion｜雙模式語音陪跑",
        "version": "1.0-rc1",
        "status": status,
        "tests_run": tests_run,
        "test_failures_or_errors": failures,
        "contract_errors": contract_errors,
        "duration_seconds": round(time.time() - started, 3),
        "python": sys.version.split()[0],
    }
    RELEASE.mkdir(exist_ok=True)
    (RELEASE / "test-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
