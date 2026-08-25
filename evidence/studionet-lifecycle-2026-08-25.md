# Studionet lifecycle — 2026-08-25

Contract: `0x667126d44229a85cc635D35df74C990fF403D15d`

This was a real multi-validator lifecycle using immutable, benign GenLayer GitHub resources. It intentionally exercised the `NOT_PROVEN` path; no malicious accusation was fabricated.

## Accepted transactions

- `enroll_package`: `0xc612b5a531730d69da79c37e64827de75dfd6b76e36aa3631614fde760569ed9`
- `open_report`: `0xbd968da0a9506a5141b881b5ac247a0477fb6bc4a3b7e30b74c541bdf81cfae6`
- `attach_evidence` CHANGELOG: `0x1f8696f7041b357322dfc0522c07bda037dd6378c8359a431bf67a9b8f4bbae9`
- `attach_evidence` TREE: `0xfd32100d2550703e3da0bb139976c296d46c4eb69749f2716b9eb6697f6b8f4f`
- `seal_report`: `0x2516e0404784bd2966f6583906e28021689092b6f7714d8a8ab76c786d52e600`
- `adjudicate`: `0xd171cc0199d7063b3719d0ee47809c800d265b8458bf549f783111b876549eca`

The DIFF attachment also reached accepted state (the report sealed with all three committed items), but its hash was truncated from the retained terminal output and is not claimed here. The inbound `withdraw_bond` call was accepted, but the runner stopped while formatting its returned string hash; its full hash was not retained. Both state effects were independently confirmed through contract views.

## Outbound transfer limitation

The Explorer shows two finalized `OUT` messages from the contract to the maintainer with `GENVM RESULT: ERROR`: one emitted by rejected-report adjudication and one emitted by bond withdrawal. Therefore this run proves validator consensus and contract-state transitions, but **does not prove successful GEN receipt by the maintainer**. A network with working deferred transfers is required to prove custody settlement end to end.

## Evidence commitments

- DIFF SHA-256: `51b6b9ec267e8f09d5378c5ca066c6a9e1e586744299746e1d6705e9aeead3eb`
- CHANGELOG SHA-256: `60efad9e92948d9a82fda3e05e328c6cc9ac2a27bfe9941f88a23bc2dd0ef144`
- TREE SHA-256: `0695982b068f8043a21b6d3ccfc10b5cb7aa5e945186a1e10fbe6f7113dd48cf`
- Manifest: `a5deec2cbf55cd10868edfad065259569b532d0ff60389510883d5628c7d4147`

## Consensus result

- Transaction result: `MAJORITY_AGREE`
- Verdict: `NOT_PROVEN`
- Intent: `BENIGN` (validator output)
- Confidence: `HIGH`
- Behavior mask: `0`
- Summary: `No malicious code or behavior detected in the diff or package contents; dependencies appear legitimate and no install hooks or payloads are present.`

## Final contract state

- Package 0: `WITHDRAWN`, bond `0`, no open report.
- Report 0: `REJECTED`, deposit `0`, three evidence items, verdict `NOT_PROVEN`.
- Vault totals: `{"bonded":0,"report_deposits":0,"slashed":0}`.

These zeroed accounting values do not override the failed outbound messages and are not presented as proof that the recipient received GEN.
