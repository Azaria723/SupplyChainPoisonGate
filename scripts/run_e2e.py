"""Deterministic verdict and settlement matrix; no deployment or network calls."""


def derive(model_verdict, behavior_mask, intent, confidence):
    if model_verdict == "POISONED" and behavior_mask > 0 and intent == "MALICIOUS" and confidence == "HIGH":
        return "POISONED"
    return "NOT_PROVEN"


def settle(verdict, bond, deposit):
    if verdict == "POISONED":
        return {"hunter": bond + deposit, "maintainer": 0, "vault": 0, "slashed": bond}
    return {"hunter": 0, "maintainer": deposit, "vault": bond, "slashed": 0}


def main():
    cases = [
        ("proven secret exfiltration", ("POISONED", 3, "MALICIOUS", "HIGH"), "POISONED"),
        ("suspicion without behavior", ("POISONED", 0, "MALICIOUS", "HIGH"), "NOT_PROVEN"),
        ("low-confidence obfuscation", ("POISONED", 16, "MALICIOUS", "LOW"), "NOT_PROVEN"),
        ("benign telemetry", ("NOT_PROVEN", 2, "BENIGN", "HIGH"), "NOT_PROVEN"),
    ]
    passed = 0
    for name, values, expected in cases:
        actual = derive(*values)
        ok = actual == expected
        passed += int(ok)
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {actual}")
    assert settle("POISONED", 10_000, 1_000) == {"hunter": 11_000, "maintainer": 0, "vault": 0, "slashed": 10_000}
    assert settle("NOT_PROVEN", 10_000, 1_000) == {"hunter": 0, "maintainer": 1_000, "vault": 10_000, "slashed": 0}
    print(f"Result: {passed}/{len(cases)} verdict cases passed; 2/2 settlement cases passed")
    raise SystemExit(0 if passed == len(cases) else 1)


if __name__ == "__main__":
    main()
