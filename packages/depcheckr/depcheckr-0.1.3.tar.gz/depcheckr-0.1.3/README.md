# 📦 depcheckr

[![PyPI version](https://img.shields.io/pypi/v/depcheckr.svg)](https://pypi.org/project/depcheckr/)
[![Python versions](https://img.shields.io/pypi/pyversions/depcheckr.svg)](https://pypi.org/project/depcheckr/)
[![License](https://img.shields.io/github/license/ashenlabs/depcheckr)](https://github.com/ashenlabs/depcheckr/blob/main/LICENSE)
[![Tests](https://github.com/ashenlabs/depcheckr/actions/workflows/test.yml/badge.svg)](https://github.com/ashenlabs/depcheckr/actions/workflows/test.yml)
[![Release](https://github.com/ashenlabs/depcheckr/actions/workflows/release.yml/badge.svg)](https://github.com/ashenlabs/depcheckr/actions/workflows/release.yml)

**The smart, modern way to manage your Python dependencies.**

> Inspect, compare, and upgrade dependencies in your `pyproject.toml` — with style and safety.

---

## 🚀 Features

* 📖 Inspect your dependencies and check if they’re up to date
* 📈 Get clear update types: `major`, `minor`, `patch`, or `up-to-date`
* 🔁 Upgrade individual packages or all at once
* 🧪 Dry-run support so nothing breaks accidentally
* 💄 Beautiful CLI powered by [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/)
* 🦄 Python 3.11+ native — built with modern tooling and async speed

---

## 📥 Installation

```bash
pip install depcheckr
```

> 💡 Make sure your project is initialized as a Git repository:
>
> ```bash
> git init
> ```

---

## 🛠 Usage

### 🔍 Inspect dependencies

```bash
depcheckr inspect show
```

Or inspect dev dependencies:

```bash
depcheckr inspect show --group dev
```

### ♻️ Upgrade dependencies

Upgrade one or more specific packages:

```bash
depcheckr upgrade apply --upgrade django httpx
```

Upgrade all outdated packages:

```bash
depcheckr upgrade apply --upgrade-all
```

Preview changes without writing to file:

```bash
depcheckr upgrade apply --upgrade-all --dry-run
```

---

## ✅ Git Commit Conventions

depcheckr follows the [Conventional Commits](https://www.conventionalcommits.org/) standard. This is required for changelog automation and GitHub release notes.

### Examples

* `feat: add support for --upgrade-all`
* `fix: correct version parsing issue`
* `chore: bump version to 0.2.0`

### Hooks and Automation

This repo uses [pre-commit](https://pre-commit.com/) and `commitlint` to enforce commit standards.

Install pre-commit hooks:

```bash
pre-commit install
```

Your commits will now be linted automatically.

### Optional: Use Commitizen (interactive prompt)

You can install [Commitizen](https://commitizen-tools.github.io/commitizen/):

```bash
npm install -g commitizen cz-conventional-changelog
```

Then run:

```bash
cz
```

Or, if you're using [Bun](https://bun.sh) and already initialized the repo with Git:

```bash
bun x cz
```

If using [Lazygit](https://github.com/jesseduffield/lazygit), add this to `~/.config/lazygit/config.yml`:

```yaml
customCommands:
  - key: "C"
    context: "files"
    command: "cz commit"
    description: "Commit using Commitizen"
    subprocess: true
```

---

## 🧪 Requirements

* Python 3.11 or newer
* Git (ensure repo is initialized with `git init`)

---

## 📦 Packaging and Development

To build locally with [uv](https://github.com/astral-sh/uv):

```bash
uv venv
uv pip install -e .
depcheckr inspect show
```

To publish:

```bash
uv build
uv pip install twine
python -m twine upload dist/*
```

---

## 🤝 Contributing

Contributions are welcome! To get started:

1. Fork the repo and clone it locally
2. Install dependencies with `uv pip install -e .`
3. Set up the pre-commit hooks: `pre-commit install`
4. Use conventional commits via `cz` or `cz commit`
5. Run tests and lint before opening a PR

Please follow the [Conventional Commits](https://www.conventionalcommits.org/) format and ensure all checks pass before submitting pull requests.

---

## 🪪 License

MIT License © 2025 Patrick Mazulo
