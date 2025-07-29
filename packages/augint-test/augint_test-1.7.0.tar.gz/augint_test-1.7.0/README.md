# Augmenting Integrations

![ci status](https://github.com/svange/augint-test/actions/workflows/pipeline.yaml/badge.svg?branch=main)
![PyPI - Version](https://img.shields.io/pypi/v/augint-test)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=flat-square&logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Made with GH Actions](https://img.shields.io/badge/CI-GitHub_Actions-blue?logo=github-actions&logoColor=white)](https://github.com/features/actions "Go to GitHub Actions homepage")
[![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/semantic-release/semantic-release)
___


#### [Documentation](https://svange.github.io/augint-test "Auto generated documentation")
#### [Test Report](https://svange.github.io/augint-test/test-report.html "Test results from last CI/CD run")
#### [Changelog](https://svange.github.io/augint-test/CHANGELOG.md "CHANGELOG from last successful release")


- [Documentation](https://svange.github.io/augint-test "Auto generated documentation")
- [Test Report](https://svange.github.io/augint-test/test-report.html "Test results from last CI/CD run")
- [Changelog](https://svange.github.io/augint-test/CHANGELOG.md "CHANGELOG from last successful release")

---
## 🚀 Initial Setup (one-time per new repository)
1️⃣ Enable GitHub Pages
This will host your test reports at https://<user>.github.io/<repo>/.

- Go to Settings > Pages
    - Set Source:
      - Source: `gh-pages`
      - Branch: `gh-pages`
      - Folder: `/ (root)`
- Save

---
### 2️⃣ Configure Trusted Publisher on PyPI and TestPyPI

To enable automated publishing through GitHub Actions:

- Go to [PyPI Trusted Publishers](https://pypi.org/manage/account/#trusted-publishers)
- Click **Add a trusted publisher**, link this repo, and authorize publishing from `main`
- Repeat on [TestPyPI Trusted Publishers](https://test.pypi.org/manage/account/#trusted-publishers) for `dev`

---

### 3️⃣ Provide a `.env` file for augint-github

Create a file called `.env` in your project root:

```env
GH_REPO=<GITHUB_REPOSITORY>
GH_ACCOUNT=<GITHUB_ACCOUNT>
GH_TOKEN=<GITHUB_TOKEN>
```

### Helpful Commands
```pwsh
get-content .env | foreach {
    $name, $value = $_.split('=')
    if ([string]::IsNullOrWhiteSpace($name) -or $name.Contains('#')) {
        # skip empty or comment line in ENV file
        return
    }
    set-content env:\$name $value
}
```
