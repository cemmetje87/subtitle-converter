---
name: powershell-automation
description: PowerShell CI/CD automation - Pester tests, GitHub Actions, Azure DevOps pipelines
triggers:
  - pester test
  - powershell ci
  - github actions powershell
  - azure devops pipeline
  - psscriptanalyzer
---

# PowerShell Automation Skill

Generates CI/CD pipelines, Pester tests, and automation configurations for PowerShell projects.

## Commands

### /pester-test

Generate Pester test file for a function.

**Usage**: `/pester-test <function-name> [--path <path>]`

**Output**:

```powershell
#Requires -Module Pester

BeforeAll {
    . $PSScriptRoot/../Public/{FunctionName}.ps1
}

Describe "{FunctionName}" {
    Context "When given valid input" {
        BeforeEach {
            $testInput = "ValidValue"
        }

        It "Should return expected output" {
            $result = {FunctionName} -Name $testInput
            $result | Should -Not -BeNullOrEmpty
            $result.Name | Should -Be $testInput
        }

        It "Should accept pipeline input" {
            $result = $testInput | {FunctionName}
            $result | Should -Not -BeNullOrEmpty
        }
    }

    Context "When given invalid input" {
        It "Should throw on null input" {
            { {FunctionName} -Name $null } | Should -Throw
        }

        It "Should throw on empty string" {
            { {FunctionName} -Name "" } | Should -Throw
        }
    }

    Context "When external service is unavailable" {
        BeforeAll {
            Mock Invoke-RestMethod {
                throw "Service unavailable"
            }
        }

        It "Should handle service errors gracefully" {
            { {FunctionName} -Name "Test" } | Should -Throw "*unavailable*"
        }
    }
}
```

---

### /pester-mock

Generate mock templates for common dependencies.

**Usage**: `/pester-mock <dependency-type>`

**Dependency Types**:

| Type    | Generated Mock                       |
| ------- | ------------------------------------ |
| `api`   | Invoke-RestMethod, Invoke-WebRequest |
| `ad`    | Get-ADUser, Get-ADGroup              |
| `file`  | Get-Content, Set-Content             |
| `azure` | Connect-AzAccount, Get-AzResource    |

**Example Output (api)**:

```powershell
BeforeAll {
    Mock Invoke-RestMethod {
        return @{
            status = "success"
            data = @{ id = "12345"; name = "Test" }
        }
    } -ParameterFilter { $Uri -like "*api.example.com*" }

    Mock Invoke-WebRequest {
        return @{
            StatusCode = 200
            Content = '{"result": "ok"}'
        }
    }
}
```

---

### /gh-workflow

Generate GitHub Actions workflow for PowerShell.

**Usage**: `/gh-workflow [--name <name>] [--multi-platform]`

**Output**:

```yaml
name: PowerShell CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    steps:
      - uses: actions/checkout@v4

      - name: Install Pester
        shell: pwsh
        run: |
          Install-Module -Name Pester -MinimumVersion 5.0 -Force -SkipPublisherCheck

      - name: Run PSScriptAnalyzer
        shell: pwsh
        run: |
          Install-Module -Name PSScriptAnalyzer -Force
          $results = Invoke-ScriptAnalyzer -Path ./src -Recurse -Settings ./PSScriptAnalyzerSettings.psd1
          $results | Format-Table -AutoSize
          if ($results.Count -gt 0) { exit 1 }

      - name: Run Pester Tests
        shell: pwsh
        run: |
          $config = New-PesterConfiguration
          $config.Run.Path = './Tests'
          $config.CodeCoverage.Enabled = $true
          $config.CodeCoverage.Path = './src'
          $config.TestResult.Enabled = $true
          $config.TestResult.OutputFormat = 'NUnitXml'
          $config.TestResult.OutputPath = 'testResults.xml'
          Invoke-Pester -Configuration $config

      - name: Upload Test Results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results-${{ matrix.os }}
          path: testResults.xml

      - name: Upload Coverage
        uses: codecov/codecov-action@v4
        if: matrix.os == 'ubuntu-latest'
        with:
          files: coverage.xml
```

---

### /ado-pipeline

Generate Azure DevOps pipeline for PowerShell.

**Usage**: `/ado-pipeline [--name <name>]`

**Output**:

```yaml
trigger:
  - main

pool:
  vmImage: "windows-latest"

stages:
  - stage: Test
    displayName: "Test & Analyze"
    jobs:
      - job: TestPowerShell
        displayName: "Run Tests"
        steps:
          - task: PowerShell@2
            displayName: "Install Dependencies"
            inputs:
              targetType: "inline"
              script: |
                Install-Module -Name Pester -MinimumVersion 5.0 -Force -SkipPublisherCheck
                Install-Module -Name PSScriptAnalyzer -Force
              pwsh: true

          - task: PowerShell@2
            displayName: "Run PSScriptAnalyzer"
            inputs:
              targetType: "inline"
              script: |
                $results = Invoke-ScriptAnalyzer -Path ./src -Recurse
                $results | Format-Table -AutoSize
                if ($results.Where({$_.Severity -eq 'Error'}).Count -gt 0) {
                    throw "PSScriptAnalyzer found errors"
                }
              pwsh: true

          - task: PowerShell@2
            displayName: "Run Pester Tests"
            inputs:
              targetType: "inline"
              script: |
                $config = New-PesterConfiguration
                $config.Run.Path = './Tests'
                $config.TestResult.Enabled = $true
                $config.TestResult.OutputFormat = 'NUnitXml'
                $config.TestResult.OutputPath = '$(Build.ArtifactStagingDirectory)/testResults.xml'
                $config.CodeCoverage.Enabled = $true
                $config.CodeCoverage.OutputPath = '$(Build.ArtifactStagingDirectory)/coverage.xml'
                Invoke-Pester -Configuration $config
              pwsh: true

          - task: PublishTestResults@2
            displayName: "Publish Test Results"
            inputs:
              testResultsFormat: "NUnit"
              testResultsFiles: "$(Build.ArtifactStagingDirectory)/testResults.xml"
            condition: always()

          - task: PublishCodeCoverageResults@2
            displayName: "Publish Coverage"
            inputs:
              summaryFileLocation: "$(Build.ArtifactStagingDirectory)/coverage.xml"

  - stage: Publish
    displayName: "Publish Module"
    dependsOn: Test
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - job: PublishModule
        steps:
          - task: PowerShell@2
            displayName: "Publish to Gallery"
            inputs:
              targetType: "inline"
              script: |
                Publish-Module -Path ./src -NuGetApiKey $(PSGalleryApiKey)
              pwsh: true
            env:
              PSGalleryApiKey: $(PSGalleryApiKey)
```

---

### /ps-analyzer-config

Generate PSScriptAnalyzer settings file.

**Usage**: `/ps-analyzer-config`

**Output**:

```powershell
# PSScriptAnalyzerSettings.psd1
@{
    Severity     = @('Error', 'Warning')
    ExcludeRules = @(
        # Add rules to exclude if needed
    )
    Rules        = @{
        PSUseCompatibleSyntax = @{
            Enable         = $true
            TargetVersions = @('5.1', '7.0')
        }
        PSUseConsistentIndentation = @{
            Enable          = $true
            IndentationSize = 4
            Kind            = 'space'
        }
        PSUseConsistentWhitespace = @{
            Enable                          = $true
            CheckOpenBrace                  = $true
            CheckOpenParen                  = $true
            CheckOperator                   = $true
            CheckSeparator                  = $true
            CheckInnerBrace                 = $true
            CheckPipeForRedundantWhitespace = $true
        }
        PSPlaceOpenBrace = @{
            Enable             = $true
            OnSameLine         = $true
            NewLineAfter       = $true
            IgnoreOneLineBlock = $true
        }
        PSPlaceCloseBrace = @{
            Enable             = $true
            NewLineAfter       = $true
            IgnoreOneLineBlock = $true
            NoEmptyLineBefore  = $false
        }
        PSAlignAssignmentStatement = @{
            Enable         = $true
            CheckHashtable = $true
        }
    }
}
```

---

## Best Practices

1. **Fail fast in CI** - Use exit codes with PSScriptAnalyzer and Pester
2. **Multi-platform testing** - Test on Windows, Linux, macOS
3. **Mock external dependencies** - Never call real APIs in unit tests
4. **Use Pester 5+** - Modern discovery and configuration
5. **Code coverage thresholds** - Fail builds below minimum coverage
6. **Cache modules** - Speed up pipeline execution

## References

| Topic            | Source                                                                                 |
| ---------------- | -------------------------------------------------------------------------------------- |
| Pester           | https://pester.dev/docs/quick-start                                                    |
| PSScriptAnalyzer | https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/overview |
| GitHub Actions   | https://docs.github.com/en/actions                                                     |
| Azure Pipelines  | https://learn.microsoft.com/en-us/azure/devops/pipelines/                              |
