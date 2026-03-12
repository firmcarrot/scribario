## Summary

<!-- What does this PR do? 1-3 bullet points. -->

-
-

## Type of change

- [ ] Bug fix
- [ ] New feature
- [ ] Refactor (no behavior change)
- [ ] Documentation
- [ ] Tests only
- [ ] Infrastructure / deployment

## Linked issue

Closes #<!-- issue number, if applicable -->

## How to test

<!-- Step-by-step instructions for verifying this works. Be specific. -->

1.
2.
3.

## Test results

<!-- Paste the output of `pytest` + `ruff check .` + `mypy . --strict` -->

```
pytest: X passed, 0 failed
ruff: no issues
mypy: Success: no issues found
```

## Checklist

- [ ] Tests written first (TDD — failing test before any production code)
- [ ] All tests pass (`pytest`)
- [ ] No ruff errors (`ruff check .`)
- [ ] No mypy errors (`mypy . --strict`)
- [ ] Documentation updated (if behavior changed)
- [ ] `.env.example` updated (if new env vars added)
- [ ] Migration created (if new DB columns/tables added)
- [ ] No secrets committed

## Notes for reviewer

<!-- Anything the reviewer should pay special attention to, known limitations, or follow-up work -->
