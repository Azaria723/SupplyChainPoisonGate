# Studionet E2E Verification

- Network: GenLayer Studionet (chain ID `61999`)
- Contract: [`0x667126d44229a85cc635D35df74C990fF403D15d`](https://explorer-studio.genlayer.com/address/0x667126d44229a85cc635D35df74C990fF403D15d)
- Deployment: visible on the contract Explorer page; the full deployment hash was not retained locally and is not asserted here.
- Source parity: decoded deployed source and `contracts/SupplyChainPoisonGate.py` are byte-identical (18,786 bytes); both SHA-256 values are `801f3e9c674060651e8e26535949abe803368f64f1d5cbfb64bec2fe8a0ec597`.
- Test intent: exercise a benign evidence path. Expected adjudication is `NOT_PROVEN`; no malicious allegation is fabricated.

## Scenario matrix

| ID | Scenario and exact input | Expected | Transaction evidence | Consensus/result | Authoritative readback | Gate |
|---|---|---|---|---|---|---|
| E2E-00 | Verify deployed code for the contract address through `gen_getContractCode` | Exact local/deployed source parity | Contract [Explorer page](https://explorer-studio.genlayer.com/address/0x667126d44229a85cc635D35df74C990fF403D15d) | Read-only RPC | Equal byte length, SHA-256, and byte comparison | **PASS** |
| E2E-01 | Owner allows `raw.githubusercontent.com` | Evidence host becomes usable | Owner transaction hash was not retained | Owner reported accepted; subsequent pinned raw GitHub evidence calls succeeded | Three allowed-host evidence records were accepted later | **PARTIAL** — indirect readback only |
| E2E-02 | Maintainer enrolls npm package with bond `1000000000000000` and report deposit `100000000000000` | Package 0 becomes `ACTIVE` | [`0xc612…9ed9`](https://explorer-studio.genlayer.com/tx/0xc612b5a531730d69da79c37e64827de75dfd6b76e36aa3631614fde760569ed9) | `ACCEPTED`, `MAJORITY_AGREE`, return `0` | Package 0: `ACTIVE`; bond and deposit policy match input | **PASS** |
| E2E-03 | Hunter opens `studionet-benign-20260825-01` with exact report deposit | Report 0 becomes `COLLECTING` | [`0xbd96…fae6`](https://explorer-studio.genlayer.com/tx/0xbd968da0a9506a5141b881b5ac247a0477fb6bc4a3b7e30b74c541bdf81cfae6) | `ACCEPTED`, `MAJORITY_AGREE`, return `0` | Report 0 recorded hunter and deposit | **PASS** |
| E2E-04 | Attach pinned `DIFF`, `CHANGELOG`, and `TREE` HTTPS bodies with SHA-256 commitments | Exactly three distinct evidence roles | CHANGELOG [`0x1f86…bae9`](https://explorer-studio.genlayer.com/tx/0x1f8696f7041b357322dfc0522c07bda037dd6378c8359a431bf67a9b8f4bbae9); TREE [`0xfd32…8f4f`](https://explorer-studio.genlayer.com/tx/0xfd32100d2550703e3da0bb139976c296d46c4eb69749f2716b9eb6697f6b8f4f); DIFF full hash not retained | Retained calls `ACCEPTED`, `MAJORITY_AGREE`; sealing later required all three | `evidence_count = 3` | **PARTIAL** — state complete, one tx hash missing |
| E2E-05 | Seal canonical manifest `a5deec2cbf55cd10868edfad065259569b532d0ff60389510883d5628c7d4147` | Report becomes `SEALED` only if manifest matches | [`0x2516…e600`](https://explorer-studio.genlayer.com/tx/0x2516e0404784bd2966f6583906e28021689092b6f7714d8a8ab76c786d52e600) | `ACCEPTED`, `MAJORITY_AGREE`, `REPORT_SEALED` | Report 0: `SEALED`, manifest stored, evidence count 3 | **PASS** |
| E2E-06 | Permissionless semantic adjudication over pinned benign resources | `NOT_PROVEN`, mask 0; no slashing | [`0xd171…9eca`](https://explorer-studio.genlayer.com/tx/0xd171cc0199d7063b3719d0ee47809c800d265b8458bf549f783111b876549eca) | `ACCEPTED`, `MAJORITY_AGREE`; 3 `AGREE`, 2 `IDLE` after quorum; consensus payload says `BENIGN`, `HIGH` | Report 0: `REJECTED`, verdict `NOT_PROVEN`, confidence `HIGH`, behavior mask 0 | **PASS** |
| E2E-07 | Maintainer calls `withdraw_bond(0)` after rejected report | Package accounting becomes withdrawn and deferred GEN messages deliver | Inbound withdrawal is visible on the contract Explorer page, but its full hash was not retained; two corresponding `OUT` rows show `GENVM RESULT: ERROR` | Inbound state transition accepted; outbound delivery failed | Package 0: `WITHDRAWN`, bond 0; vault accounting 0; recipient credit is **not proven** | **FAIL** for token delivery; **PASS** for state transition |

## Committed HTTPS evidence

| Role | Immutable URL | SHA-256 |
|---|---|---|
| DIFF | `https://raw.githubusercontent.com/genlayerlabs/genlayer-js/1b7f50a3a3f2963ea857941b0fb386081dd5c326/README.md` | `51b6b9ec267e8f09d5378c5ca066c6a9e1e586744299746e1d6705e9aeead3eb` |
| CHANGELOG | `https://raw.githubusercontent.com/genlayerlabs/genlayer-cli/3396474b775d998ab3778ac7cfd1e2e197f8b47f/CHANGELOG.md` | `60efad9e92948d9a82fda3e05e328c6cc9ac2a27bfe9941f88a23bc2dd0ef144` |
| TREE | `https://raw.githubusercontent.com/genlayerlabs/genlayer-js/1b7f50a3a3f2963ea857941b0fb386081dd5c326/package.json` | `0695982b068f8043a21b6d3ccfc10b5cb7aa5e945186a1e10fbe6f7113dd48cf` |

## Local negative-path coverage

The repository contains tests for owner authorization, exact payable deposit, maintainer self-report rejection, evidence-role uniqueness, host allowlisting, incomplete evidence rejection, manifest mismatch, and withdrawal blocking while a report is open. Six static/invariant tests pass locally. The five SDK direct-mode lifecycle tests are present but are not claimed as passing because the installed Windows `gltest` loader fails before contract loading with WinError 32.

These negative paths were **not rerun as Studionet transactions** in this evidence session and therefore remain `LOCAL ONLY`, not on-chain E2E proof.

## Completion gates

| Gate | Result | Basis |
|---|---|---|
| Deployed source parity | **PASS** | Exact bytes and SHA-256 match |
| Payable bond/deposit accounting | **PASS** | Accepted inputs and authoritative views |
| Three-role HTTPS commitment and manifest | **PASS** | Evidence count 3 and sealed manifest |
| AI validator consensus | **PASS** | `MAJORITY_AGREE`, closed verdict and readback |
| Benign `NOT_PROVEN` state machine | **PASS** | Report `REJECTED`, package remains withdrawable |
| Outbound GEN delivery | **FAIL** | Both deferred `OUT` messages show GenVM error |
| Negative-path Studionet matrix | **NOT RUN** | Covered locally only |
| Transaction-link completeness | **PARTIAL** | Owner setup, DIFF attach, deployment, and withdrawal full hashes not retained |

**E2E COMPLETION GATE: PARTIAL.** Core Intelligent Contract adjudication and protected state transitions are proven. End-to-end token delivery is not proven and failed in this Studionet run. No scenario marked `FAIL`, `PARTIAL`, or `NOT RUN` is presented as a pass.
