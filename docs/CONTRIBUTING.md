# Scribario — Contributing Guide

Thank you for your interest in contributing to Scribario. This guide covers everything you need to work on the codebase effectively.

---

## Development Setup

### Requirements

- Python 3.11+
- A Supabase project (free tier is fine)
- API keys for Telegram, Anthropic, and Kie.ai

### Install

```bash
git clone https://github.com/your-org/scribario.git
cd scribario

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Configure

```bash
cp .env.example .env
# Edit .env with your API keys
```

---

## Code Standards

### Formatting and Linting

We use **ruff** for both linting and formatting. The configuration is in `pyproject.toml`.

```bash
# Check for issues
ruff check .

# Fix automatically where possible
ruff check --fix .

# Format
ruff format .

# Check format without writing
ruff format --check .
```

Enabled rule sets: `E, F, I, N, W, UP, B, SIM, RUF`
Line length: 100 characters

### Type Checking

We use **mypy --strict**. All code must pass type checking.

```bash
mypy . --strict
```

This means:
- All function parameters and return types annotated
- No implicit `Any`
- No untyped definitions

Use `from __future__ import annotations` at the top of files for forward references.

### Imports

- Absolute imports preferred: `from bot.config import get_settings`
- isort is enforced by ruff (rule set `I`)
- Standard library → third-party → local, each group separated by a blank line

### Logging

Use **structlog** with structured key-value pairs, not f-strings in log messages:

```python
# Correct
logger.info("Content generated", extra={"draft_id": draft_id, "caption_count": 3})

# Wrong
logger.info(f"Content generated: {draft_id}")
```

### Async

The entire codebase is async-first. Use `async def` and `await` everywhere. Never use `asyncio.run()` inside a function — only at the entrypoint.

---

## TDD — The Iron Law

**No production code without a failing test first.**

The workflow:
1. Write a test that captures the intended behavior
2. Watch it fail (`pytest tests/your_test.py -v`)
3. Write the minimal code to make it pass
4. Watch it pass
5. Refactor if needed

Every new feature, bug fix, and handler must follow this process. PRs that add production code without corresponding tests will not be merged.

### Writing Tests

Test files live in `tests/`. File naming: `test_<module>.py`.

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.asyncio
async def test_caption_generation_includes_visual_prompt():
    """Each generated caption must include a non-empty visual_prompt."""
    result = await generate_captions(
        intent="Post about our new sauce",
        profile=mock_brand_profile(),
        examples=[],
        platform_targets=["facebook"],
        num_options=3,
    )

    assert len(result) == 3
    for caption in result:
        assert caption.visual_prompt  # must not be empty
```

Run the full test suite:

```bash
pytest
pytest --cov=. --cov-report=term-missing   # with coverage
```

---

## PR Process

1. **Branch from `main`**: `git checkout -b feat/your-feature-name`
2. **Write tests first** — see TDD section above
3. **Implement the feature**
4. **Run the full check suite:**
   ```bash
   ruff check .
   ruff format --check .
   mypy . --strict
   pytest
   ```
5. **All checks must pass** before opening a PR
6. **Open PR against `main`** using the [PR template](.github/pull_request_template.md)
7. A maintainer will review within 2 business days

**Commit message format:** `feat:`, `fix:`, `chore:`, `docs:`, `test:` prefix.

---

## Adding a New Job Handler

Job handlers live in `worker/jobs/`. Each handler is an async function that receives a job payload from pgmq.

### Steps

1. **Write a test** in `tests/worker/test_your_job.py`
2. **Create the handler** in `worker/jobs/your_job.py`:

```python
"""Handler for the your_job job type."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def handle(payload: dict[str, Any]) -> None:
    """Process a your_job job.

    Args:
        payload: Job payload from pgmq. Expected keys: ...
    """
    # 1. Extract and validate payload
    request_id = payload["request_id"]
    tenant_id = payload["tenant_id"]

    logger.info("Processing your_job", extra={"request_id": request_id})

    # 2. Do the work
    # ...

    # 3. Update DB state
    # ...

    logger.info("your_job complete", extra={"request_id": request_id})
```

3. **Register the handler** in `worker/main.py`:

```python
from worker.jobs import your_job

JOB_HANDLERS = {
    "generate_content": generate_content.handle,
    "post_content": post_content.handle,
    "your_job": your_job.handle,        # add this
}
```

4. **Create the queue** via a Supabase migration if it doesn't exist:

```sql
SELECT pgmq.create('your_queue_name');
```

---

## Adding a New Social Platform

Scribario uses Postiz as the publishing abstraction layer, so adding a new platform is mostly configuration — not code.

### Steps

1. **Add the platform to Postiz** — connect it via the Postiz admin UI
2. **Add the OAuth flow** (if needed) in `bot/services/postiz_oauth.py`
3. **Update `platform_targets` validation** in `bot/handlers/intake.py`
4. **Update the user-facing platform list** in `docs/USER_GUIDE.md`
5. **Write an integration test** in `tests/bot/test_posting.py`

For platforms not supported by Postiz, you'll need to add a native posting client in `pipeline/posting.py` and register it as a posting provider.

---

## Adding a New AI Image Provider

Image generation is abstracted behind `ImageGenerationService` in `pipeline/image_gen.py`. To add a new provider:

1. **Write a test** in `tests/pipeline/test_image_gen.py` using the new provider
2. **Implement the provider** as a class implementing the `ImageProvider` protocol:

```python
class YourProvider:
    async def generate(self, prompt: str) -> ImageResult:
        """Generate a single image from a text prompt."""
        ...

    async def generate_batch(self, prompts: list[str]) -> list[ImageResult]:
        """Generate multiple images in parallel."""
        ...
```

3. **Add provider selection** to `ImageGenerationService` — either via environment variable or per-tenant config
4. **Add the API key** to `bot/config.py` and the environment variables table in `docs/SETUP.md`

---

## Questions

Open an issue or start a discussion. Include as much context as possible — stack trace, OS, Python version, and what you expected vs. what happened.
