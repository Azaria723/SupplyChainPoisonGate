# SupplyChainPoisonGate

Contract-only GenLayer vault for adjudicating malicious software dependency updates. A maintainer deposits a real GEN security bond; a hunter deposits anti-spam collateral and commits three HTTPS evidence packets (`DIFF`, `CHANGELOG`, `TREE`). Validators fetch the committed bytes, verify SHA-256, compare code behavior against the changelog, and either slash the bond to the hunter or award the hunter deposit to the maintainer.

This repository intentionally contains **no frontend**. The Intelligent Contract is the product and all lifecycle calls can be made from GenLayer Studio.

## Deployment

- Network: GenLayer Studio (`https://studio.genlayer.com/api`)
- Contract: `0x667126d44229a85cc635D35df74C990fF403D15d`
- Verification date: 2026-08-25
- Deployed source SHA-256: `801f3e9c674060651e8e26535949abe803368f64f1d5cbfb64bec2fe8a0ec597`
- Local source SHA-256: `801f3e9c674060651e8e26535949abe803368f64f1d5cbfb64bec2fe8a0ec597`
- Result: the decoded on-chain source is byte-for-byte identical to `contracts/SupplyChainPoisonGate.py` (18,786 bytes).

## Why GenLayer

Hash checks can prove which bytes were submitted, but cannot decide whether a semantic code change is credential theft, covert exfiltration, a remote payload loader, or a benign feature. GenLayer validators make that consequential judgment from canonical evidence; the contract constrains the result with a closed verdict schema and objective cross-field checks before moving funds.

## Lifecycle

1. Owner allowlists trustworthy evidence hosts with `set_evidence_host`.
2. Maintainer calls payable `enroll_package` and supplies the security bond.
3. Hunter calls payable `open_report` with the exact configured report deposit.
4. Hunter attaches exactly one `DIFF`, `CHANGELOG`, and `TREE` HTTPS resource, each with its body SHA-256.
5. Hunter computes and submits the canonical evidence-manifest hash to `seal_report`.
6. Anyone calls `adjudicate`. Valid evidence is fetched and evaluated under validator consensus.
7. `POISONED`: bond + hunter deposit go to the hunter. `NOT_PROVEN`: deposit goes to the maintainer and the bond remains withdrawable.

Invalid payable calls roll back so attached GEN is not trapped. State is updated before deferred transfers. Only one report may be open per package.

## Local verification

```powershell
$env:PYTHONUTF8='1'
genvm-lint check contracts/SupplyChainPoisonGate.py
genvm-lint typecheck contracts/SupplyChainPoisonGate.py
python -m pytest -q tests/test_contract_invariants.py
python scripts/run_e2e.py
python scripts/build_evidence.py fixtures/poisoned
```

Verified locally on 2026-08-25: linter and semantic validation passed, typecheck reported zero errors, 6 invariant tests passed, and the deterministic matrix passed 4/4 verdict plus 2/2 settlement cases. The five `gltest` direct lifecycle tests are included, but the installed Windows runner currently fails before contract loading with `PermissionError [WinError 32]` while deleting its own open temporary stdin file; they are not claimed as passing.

The deployment is verified by reading `gen_getContractCode`. A benign lifecycle subsequently completed its contract-state transitions on Studionet: bond and report-deposit accounting, three pinned HTTPS commitments, manifest sealing, multi-validator adjudication (`NOT_PROVEN`), and withdrawal state transition. The two deferred outbound GEN messages failed in Studionet, so successful token settlement is **not** claimed. See [evidence/studionet-lifecycle-2026-08-25.md](evidence/studionet-lifecycle-2026-08-25.md).

See [contract.md](contract.md) for the design and threat model and [evidence/verification.md](evidence/verification.md) for exact evidence claims.
