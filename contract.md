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

## Known limitations

- Host allowlisting reduces arbitrary-web input but does not establish repository ownership.
- No time oracle is used, so there is no deadline-based cancellation. The maintainer cannot withdraw while a report is open; adjudication is permissionless.
- Validator analysis is bounded to three evidence bodies, each capped at 256 KB and truncated to 3,500 characters in the prompt.
- This is a testnet-oriented prototype, not an audited production insurance product.

