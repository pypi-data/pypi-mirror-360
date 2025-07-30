# Pre-commit Setup

This repository uses [pre-commit](https://pre-commit.com/) to automatically run code formatters and linters before every commit.

## What gets checked:

✅ **Black** - Code formatting (120 char line length)
✅ **Flake8** - Linting and style checks
✅ **isort** - Import sorting
✅ **Trailing whitespace** - Removes trailing spaces
✅ **End-of-file-fixer** - Ensures files end with newline
✅ **YAML validation** - Checks YAML syntax
✅ **Large files** - Prevents accidentally committing large files
✅ **Merge conflicts** - Detects merge conflict markers

## Installation

Pre-commit hooks are automatically installed when you run:

```bash
python3 -m pip install pre-commit
python3 -m pre_commit install
```

## Manual execution

Run all hooks on all files:
```bash
python3 -m pre_commit run --all-files
```

Run specific hook:
```bash
python3 -m pre_commit run black
python3 -m pre_commit run flake8
```

## What happens during commit

When you run `git commit`, the hooks will automatically:

1. **Format your code** with Black
2. **Sort imports** with isort
3. **Check linting** with flake8
4. **Fix whitespace** issues
5. **Validate files** for common issues

If any hook fails or makes changes:
- The commit is **blocked**
- Files are **automatically fixed** where possible
- You need to **review changes** and commit again

## Configuration

- **Black**: 120 character line length (matches flake8)
- **Flake8**: Configured in `.flake8` file
- **isort**: Black-compatible profile
- **Hooks**: Configured in `.pre-commit-config.yaml`

## Benefits

🚀 **Consistent code style** across all contributors
🐛 **Catch linting issues** before they reach CI/CD
⚡ **Automatic formatting** saves time
🔒 **Enforced standards** in every commit
✨ **Clean git history** with properly formatted code

## GitHub Actions Integration

The same tools run in GitHub Actions, so pre-commit ensures:
- ✅ Local commits pass CI formatting checks
- ✅ No "fix formatting" commits needed
- ✅ Faster CI pipeline (no formatting failures)
- ✅ Consistent experience locally and in CI
