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

### Set up your AWS OIDC provider (once per account)
Run this once per AWS account (safe to re-run; will no-op if it exists):
```powershell
aws iam create-open-id-connect-provider `
  --url https://token.actions.githubusercontent.com `
  --client-id-list sts.amazonaws.com
```

### Setup your AWS pipeline resources:

1. Create pipeline resources for stages DEV and PROD. Consider stage names like DevApiPortal and ProdApiPortal.
 ```powershell
 (augint-test-py3.12) PS C:\Users\samue\projects\augint-test> sam pipeline bootstrap --stage augint-test-testing

 sam pipeline bootstrap generates the required AWS infrastructure resources to connect
 to your CI/CD system. This step must be run for each deployment stage in your pipeline,
 prior to running the sam pipeline init command.

 We will ask for [1] stage definition, [2] account details, and
 [3] references to existing resources in order to bootstrap these pipeline resources.

 [1] Stage definition
 Stage configuration name: augint-test-testing

 [2] Account details
 The following AWS credential sources are available to use.
 To know more about configuration AWS credentials, visit the link below:
 https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html
         1 - Environment variables (not available)
         2 - default (named profile)
         3 - ...
         q - Quit and configure AWS credentials
 Select a credential source to associate with this stage: 2
 Associated account XYZ with configuration augint-test-testing.

 Enter the region in which you want these resources to be created [us-east-1]:
 Select a user permissions provider:
         1 - IAM (default)
         2 - OpenID Connect (OIDC)
 Choice (1, 2): 2
 Select an OIDC provider:
         1 - GitHub Actions
         2 - GitLab
         3 - Bitbucket
 Choice (1, 2, 3): 1
 Enter the URL of the OIDC provider [https://token.actions.githubusercontent.com]:
 Enter the OIDC client ID (sometimes called audience) [sts.amazonaws.com]:
 Enter the GitHub organization that the code repository belongs to. If there is no organization enter your username instead: svange
 Enter GitHub repository name: augint-test
 Enter the name of the branch that deployments will occur from [main]:

 [3] Reference application build resources
 Enter the pipeline execution role ARN if you have previously created one, or we will create one for you []:
 Enter the CloudFormation execution role ARN if you have previously created one, or we will create one for you []:
 Please enter the artifact bucket ARN for your Lambda function. If you do not have a bucket, we will create one for you []:
 Does your application contain any IMAGE type Lambda functions? [y/N]:

 [4] Summary
 Below is the summary of the answers:
         1 - Account: 330659553592
         2 - Stage configuration name: augint-test-testing
         3 - Region: us-east-1
         4 - OIDC identity provider URL: https://token.actions.githubusercontent.com
         5 - OIDC client ID: sts.amazonaws.com
         6 - GitHub organization: svange
         7 - GitHub repository: augint-test
         8 - Deployment branch:  main
         9 - Pipeline execution role: [to be created]
         10 - CloudFormation execution role: [to be created]
         11 - Artifacts bucket: [to be created]
         12 - ECR image repository: [skipped]
 Press enter to confirm the values above, or select an item to edit the value:

 ```

### Fix the trust policy on the generated PipelineExecutionRole
SAM CLI generates an invalid trust policy (uses ForAllValues:StringLike which fails).
Run this after bootstrap:

```powershell
# Load environment variables from .env file
get-content .env | foreach {
    $name, $value = $_.split('=')
    if ([string]::IsNullOrWhiteSpace($name) -or $name.Contains('#')) {
        # skip empty or comment line in ENV file
        return
    }
    set-content env:\$name $value
}

# Get AWS account ID
$accountId = (aws sts get-caller-identity --query 'Account' --output text)
# Set your GitHub org/user and repo
$githubUserOrOrg = $env:GH_ACCOUNT  
$githubRepo = $env:GH_REPO
$projectPrefix = ($githubRepo.Substring(0, [Math]::Min(9, $githubRepo.Length)))  # first 9 chars


# Find the generated pipeline execution role
$roleName = aws iam list-roles `
  --query "Roles[?starts_with(RoleName, 'aws-sam-cli-managed-${projectPrefix}') && contains(RoleName, 'PipelineExecutionRole')].RoleName" `
  --output text

if (-not $roleName) {
    Write-Error "Could not find a PipelineExecutionRole for project prefix $projectPrefix"
    exit 1
}

# Define the trust policy
$trustPolicy = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::$accountId:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringLike": {
          "token.actions.githubusercontent.com:sub": [
            "repo:$githubUserOrOrg/$githubRepo:ref:refs/heads/main",
            "repo:$githubUserOrOrg/$githubRepo:ref:refs/heads/dev"
          ]
        },
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        }
      }
    }
  ]
}
"@

# Update the role trust policy
aws iam update-assume-role-policy `
  --role-name $roleName `
  --policy-document $trustPolicy
```

### Change `augint-test` to your project name:
- in `pyproject.toml`
- in `.github/workflows/pipeline.yaml`
- in `README.md`
- Rename directory: `src/augint_test` → `src/<your_project_name>`
- Delete `CHANGELOG.md` — it will regenerate on release.

---

### Create a `.env` file for your repository
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

#######################
# AWS Pipeline Resources
#######################
TESTING_REGION=us-east-1
TESTING_PIPELINE_EXECUTION_ROLE=
TESTING_CLOUDFORMATION_EXECUTION_ROLE=
TESTING_ARTIFACTS_BUCKET=


```
Push the `.env` file vars and secrets to your repository
```bash
ai-gh-push
```
---

### Configure Trusted Publisher on PyPI and TestPyPI
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


aws iam list-open-id-connect-providers

aws iam get-open-id-connect-provider --open-id-connect-provider-arn arn:aws:iam::330659553592:oidc-provider/token.actions.githubusercontent.com

aws iam get-role --role-name aws-sam-cli-managed-augint-te-PipelineExecutionRole-npVjgGkjI8x6 --query 'Role.AssumeRolePolicyDocument' --output json
