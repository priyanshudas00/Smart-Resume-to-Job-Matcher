"""Allow running the package as a module: python -m resume_matcher."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
