# Contract design

## Scope

The smallest credible version supports one active bond and one open report per package. It does not attempt to clone npm, PyPI, GitHub, or an entire package registry. Instead, it adjudicates a canonical, content-addressed evidence packet and settles a real vault.

## State machines

- Package: `ACTIVE -> SLASHED` or `ACTIVE -> WITHDRAWN`.
- Report: `COLLECTING -> SEALED -> SLASHED|REJECTED`.

The report deposit discourages spam. A rejected claim transfers the deposit to the accused maintainer; a proven claim returns it together with the slashed bond to the hunter.

## Evidence protocol

Each report binds the baseline commit, target commit, target tree digest, report key, and an ordered list of three evidence objects. Every object contains `kind`, `url`, and `sha256`. `seal_report` independently reconstructs canonical compact JSON (sorted keys) and rejects a mismatched manifest hash. During adjudication, fetched bytes must match their SHA-256 or they are marked invalid.

The prompt treats fetched material as untrusted data, requires valid DIFF and TREE commitments for conviction, and maps proven behavior to fixed bits: credential theft (1), exfiltration (2), remote payload execution (4), malicious install hook (8), obfuscated dynamic execution (16), and wallet/key substitution (32). A `POISONED` output is downgraded unless the behavior mask is nonzero, intent is `MALICIOUS`, and confidence is `HIGH`.

## Lessons applied

- Make the GenLayer judgment economically consequential, not decorative.
- Verify the real evidence bytes and semantic answer, not only JSON shape.
- Keep the verdict vocabulary closed and add deterministic post-consensus guards.
- Separate evidence collection, sealing, adjudication, and settlement into explicit states.
- Preserve honest, reproducible evidence: distinguish local checks, simulated matrices, and actual on-chain transactions.
- Keep the repository contract-focused; no mock frontend or copied application shell.

## Lessons from strong Studionet evidence reports

A strong verification file is more than a list of transaction hashes. It should make every claim independently checkable and distinguish execution layers that can succeed or fail separately.

- Pin the network, contract address, deployment evidence, and deployed/local source parity at the top.
- Use a scenario matrix with exact inputs, expected result, transaction evidence, consensus result, and authoritative state readback.
- Link every retained transaction hash directly to Explorer instead of requiring reviewers to search manually.
- Include negative paths such as authorization failure, duplicate submission, invalid state transition, and commitment mismatch; a contract is not fully evidenced by one happy path.
- Treat consensus acceptance, contract-state mutation, and deferred external-message delivery as three different claims. One does not prove the others.
- End with explicit completion gates (`PASS`, `FAIL`, `PARTIAL`, or `NOT RUN`) and never upgrade missing or failed evidence to `PASS`.
- Preserve limitations in the primary evidence document. In this deployment, both outbound GEN messages failed even though adjudication and withdrawal state transitions were accepted, so token settlement remains unproven.

## Known limitations

- Host allowlisting reduces arbitrary-web input but does not establish repository ownership.
- No time oracle is used, so there is no deadline-based cancellation. The maintainer cannot withdraw while a report is open; adjudication is permissionless.
- Validator analysis is bounded to three evidence bodies, each capped at 256 KB and truncated to 3,500 characters in the prompt.
- This is a testnet-oriented prototype, not an audited production insurance product.
