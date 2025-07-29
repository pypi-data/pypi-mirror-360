# Augmenting Integrations Library Template Repository


[![CI Status](https://github.com/svange/augint-test/actions/workflows/pipeline.yaml/badge.svg?branch=main)](https://github.com/svange/augint-test/actions/workflows/pipeline.yaml)
[![PyPI](https://img.shields.io/pypi/v/augint-test?style=flat-square)](https://pypi.org/project/augint-test/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=flat-square&logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-automated-blue?style=flat-square&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org)
[![semantic-release](https://img.shields.io/badge/%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg?style=flat-square)](https://github.com/semantic-release/semantic-release)
[![License](https://img.shields.io/github/license/svange/augint-test?style=flat-square)](https://github.com/svange/augint-test/blob/main/LICENSE)
[![Sponsor](https://img.shields.io/badge/donate-github%20sponsors-blueviolet?style=flat-square&logo=github-sponsors)](https://github.com/sponsors/svange)


---

## 📚 Project Resources

| [📖 Current Documentation](https://svange.github.io/augint-test) | [🧪 Test report for last release ](https://svange.github.io/augint-test/test-report.html) | [📝 Changelog for last release](https://svange.github.io/augint-test/CHANGELOG.md) |
|:----------------------------------------------------------------:|:-----------------------------------------------------------------------------------------:|:----------------------------------------------------------------------------------:|

---
## ⚡ Getting Started

### 1️⃣ Change `augint-test` to your project name:
- in `pyproject.toml`
- in `.github/workflows/pipeline.yaml`
- in `README.md`
- Rename directory: `src/augint_test` → `src/<your_project_name>`
- Delete `CHANGELOG.md` — it will regenerate on release.

---

### 2️⃣ Create a `.env` file for your repository
```env
# Needed for augint-github to find the repo
GH_REPO=<GITHUB_REPOSITORY>
GH_ACCOUNT=<GITHUB_ACCOUNT>

# Needed to publish to GitHub
GH_TOKEN=<GITHUB_TOKEN>
# Needed for pipeline generate docs stage (module name can't contain dashes)
MODULE_NAME=<MODULE_NAME>
# Needed for pipeline test runners
PYTHON_VERSION=<PYTHON_VERSION>
```
Push the `.env` file vars and secrets to your repository
```bash
ai-gh-push
```
---

- ### 3️⃣ Configure Trusted Publisher on PyPI and TestPyPI
  - Go to [PyPI Trusted Publishers](https://pypi.org/manage/account/#trusted-publishers)
  - Click **Add a trusted publisher**, link this repo, and authorize publishing from `main`
  - Repeat on [TestPyPI Trusted Publishers](https://test.pypi.org/manage/account/#trusted-publishers) for `dev`

---
### Helpful Commands
```pwsh
# "source" an .env file in PowerShell
get-content .env | foreach {
    $name, $value = $_.split('=')
    if ([string]::IsNullOrWhiteSpace($name) -or $name.Contains('#')) {
        # skip empty or comment line in ENV file
        return
    }
    set-content env:\$name $value
}
```
