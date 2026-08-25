# Verification evidence

Date: 2026-08-25. Environment: Windows, Python 3.12, `genvm-linter 0.11.0`.

Observed local results:

- `genvm-lint check`: lint passed (3 checks); SDK semantic validation passed; 10 public methods detected.
- `genvm-lint typecheck`: no type errors.
- `pytest tests/test_contract_invariants.py`: 6 passed.
- `python scripts/run_e2e.py`: 4/4 verdict cases and 2/2 settlement cases passed.

Observed deployment result:

- User-confirmed contract: `0x667126d44229a85cc635D35df74C990fF403D15d`.
- `gen_getContractCode` returned code on GenLayer Studio; the same address was not found on Asimov or Bradbury.
- Base64-decoded deployed code and the local contract are both 18,786 bytes.
- Both SHA-256 values are `801f3e9c674060651e8e26535949abe803368f64f1d5cbfb64bec2fe8a0ec597`; exact byte comparison returned `true`.

Not observed and therefore not claimed:

- No deployment transaction hash was supplied or discovered.
- Direct-mode lifecycle tests do not currently execute on this machine because the installed `gltest` Windows loader throws WinError 32 before loading the contract.

A real benign lifecycle was later completed. Transaction hashes, commitments, consensus output, and final view state are recorded in `studionet-lifecycle-2026-08-25.md`.

Important qualification: both deferred outbound GEN messages show `GENVM RESULT: ERROR` in the Studionet Explorer. Consensus and state transitions are proven; successful token settlement is not.
