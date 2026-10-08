# Lens: Security

Can someone outside get in, read what they should not, or make the system do
something it should not, through this change?

**Not yours:** logic bugs with no attacker in the story (Correctness), rollback
and state (State and rollback), conventions (Conformance).

## What to hunt

| Problem | Confidence when proven |
|---|---|
| Secret in the diff: token, password, private key, connection string, kubeconfig, certificate | 100 |
| Input from outside reaching a query, shell, path, template or deserializer without validation (injection) | 90 |
| Endpoint or action with no authorization check, or checking the user but not the ownership (IDOR) | 90 |
| Personal or sensitive data written to a log, an error message or a URL | 85 |
| Error message that tells the caller what exists ("user not found" vs "wrong password") | 80 |
| Weak or home-made crypto, fixed IV, disabled certificate check (`verify=False`, `-k`, `insecureSkipVerify`) | 90 |
| New dependency, or a version pinned to something with a known vulnerability | 80 |
| Permission widened: container as root, `privileged`, `hostNetwork`, wildcard RBAC, `0.0.0.0/0`, `chmod 777` | 90 |
| Secret passed as a plain env var or build arg, baked into an image layer or printed by CI | 90 |
| CI job that runs code from a fork or an untrusted branch with access to secrets | 90 |

## Rules

- **Scanner output is evidence, not a verdict.** Confirm each hit at its line,
  set aside false positives with the reason, and hunt what scanners miss:
  authorization, ownership, sensitive data in logs.
- **Reachability first.** A flaw counts once you showed the path from outside to
  it. Unreachable code is a Note, not a Critical.
- **Never repeat a secret's value.** Point to file and line, mask it (`***`), and
  say it must be rotated, not just removed: it is already in git history.
- When the risk is real but the fix depends on context you do not have, say what
  control is missing and leave the choice of library to the user.
