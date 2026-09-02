# Santa Build Loop

Every loop iteration must follow this order:

1. Read `CLAUDE.md` and `docs/santa-agent-workboard.md`.
2. Inspect `git status --short --branch`, recent commits, and any current claims.
3. If another worker owns a file, do not touch it. Choose the highest-priority unclaimed item.
4. Implement one coherent slice of work. Do not stop at a plan or a progress note.
5. Run focused tests, then the full relevant test suite.
6. Review the diff, public surfaces, privacy, pricing, and English/Spanish parity.
7. Update the workboard with the exact files, tests, result, and status.
8. Mark work `READY_FOR_REVIEW` before a coordinator reviews it. Only the coordinator may mark it `VERIFIED` or `COMMITTED`.

The build is complete only when every acceptance item in the workboard is `VERIFIED` and the final test command passes. If an external provider or credential is needed, implement a local dry-run adapter, document the one manual setup step, and continue with all locally achievable work.

Never send customer messages, record calls, publish social content, change DNS, charge money, or claim live integration without explicit operator approval and a real tested connection.
