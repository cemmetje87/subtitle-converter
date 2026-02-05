---
name: powershell-dev
description: PowerShell development - function templates, module scaffolding, best practices
triggers:
  - powershell function
  - ps module
  - cmdlet
  - advanced function
---

# PowerShell Development Skill

Generates PowerShell functions, modules, and development scaffolding following best practices.

## Commands

### /ps-function

Generate an advanced function following best practices.

**Usage**: `/ps-function <Verb-Noun> [--pipeline] [--shouldprocess]`

**Output**:

```powershell
function {Verb-Noun} {
    <#
    .SYNOPSIS
        Brief description of the function.
    .DESCRIPTION
        Detailed description of what the function does.
    .PARAMETER ParameterName
        Description of the parameter.
    .EXAMPLE
        {Verb-Noun} -ParameterName "Value"
        Description of what this example does.
    .INPUTS
        System.String
        Description of pipeline input.
    .OUTPUTS
        System.Object
        Description of output object.
    .NOTES
        Author: Your Name
        Version: 1.0.0
    #>
    [CmdletBinding(SupportsShouldProcess)]
    [OutputType([PSCustomObject])]
    param (
        [Parameter(Mandatory, ValueFromPipeline, ValueFromPipelineByPropertyName)]
        [ValidateNotNullOrEmpty()]
        [string]$ParameterName,

        [Parameter()]
        [ValidateSet('Option1', 'Option2', 'Option3')]
        [string]$OptionalParam = 'Option1',

        [Parameter()]
        [ValidateRange(1, 100)]
        [int]$Count = 10
    )

    begin {
        Write-Verbose "Starting {Verb-Noun}"
        # Initialization code
    }

    process {
        if ($PSCmdlet.ShouldProcess($ParameterName, "Action description")) {
            try {
                # Main logic here
                $result = [PSCustomObject]@{
                    Name   = $ParameterName
                    Status = 'Success'
                }

                Write-Output $result
            }
            catch {
                Write-Error "Operation failed: $($_.Exception.Message)"
                throw
            }
        }
    }

    end {
        Write-Verbose "Completed {Verb-Noun}"
        # Cleanup code
    }
}
```

---

### /ps-module

Scaffold a complete PowerShell module structure.

**Usage**: `/ps-module <ModuleName>`

**Creates**:

```
{ModuleName}/
├── {ModuleName}.psd1          # Module manifest
├── {ModuleName}.psm1          # Root module
├── Public/                    # Exported functions
│   └── .gitkeep
├── Private/                   # Internal functions
│   └── .gitkeep
├── Classes/                   # PowerShell classes
│   └── .gitkeep
├── Tests/                     # Pester tests
│   └── {ModuleName}.Tests.ps1
├── README.md
└── PSScriptAnalyzerSettings.psd1
```

**Module Manifest ({ModuleName}.psd1)**:

```powershell
@{
    RootModule        = '{ModuleName}.psm1'
    ModuleVersion     = '0.1.0'
    GUID              = '{new-guid}'
    Author            = 'Your Name'
    CompanyName       = 'Your Company'
    Copyright         = '(c) {year}. All rights reserved.'
    Description       = 'Module description'
    PowerShellVersion = '5.1'

    # Functions to export
    FunctionsToExport = @()
    CmdletsToExport   = @()
    VariablesToExport = @()
    AliasesToExport   = @()

    PrivateData = @{
        PSData = @{
            Tags         = @('Tag1', 'Tag2')
            LicenseUri   = ''
            ProjectUri   = ''
            ReleaseNotes = ''
        }
    }
}
```

**Root Module ({ModuleName}.psm1)**:

```powershell
# Get public and private function files
$Public = @(Get-ChildItem -Path "$PSScriptRoot/Public/*.ps1" -ErrorAction SilentlyContinue)
$Private = @(Get-ChildItem -Path "$PSScriptRoot/Private/*.ps1" -ErrorAction SilentlyContinue)

# Dot source the files
foreach ($file in @($Public + $Private)) {
    try {
        . $file.FullName
    }
    catch {
        Write-Error "Failed to import $($file.FullName): $_"
    }
}

# Export public functions
Export-ModuleMember -Function $Public.BaseName
```

---

### /ps-class

Generate a PowerShell class.

**Usage**: `/ps-class <ClassName>`

**Output**:

```powershell
class {ClassName} {
    # Properties
    [string]$Name
    [int]$Id
    [datetime]$CreatedAt

    # Hidden properties (not shown in default output)
    hidden [string]$InternalState

    # Static properties
    static [int]$InstanceCount = 0

    # Default constructor
    {ClassName}() {
        $this.CreatedAt = Get-Date
        [{ClassName}]::InstanceCount++
    }

    # Parameterized constructor
    {ClassName}([string]$name, [int]$id) {
        $this.Name = $name
        $this.Id = $id
        $this.CreatedAt = Get-Date
        [{ClassName}]::InstanceCount++
    }

    # Methods
    [string] ToString() {
        return "{0} (ID: {1})" -f $this.Name, $this.Id
    }

    [void] DoSomething([string]$input) {
        Write-Verbose "Processing: $input"
        $this.InternalState = $input
    }

    # Static method
    static [int] GetInstanceCount() {
        return [{ClassName}]::InstanceCount
    }
}
```

---

### /ps-enum

Generate a PowerShell enum.

**Usage**: `/ps-enum <EnumName> <values...>`

**Output**:

```powershell
enum {EnumName} {
    Unknown = 0
    Value1 = 1
    Value2 = 2
    Value3 = 3
}

# Usage example:
# $status = [{EnumName}]::Value1
# [Enum]::GetValues([{EnumName}])
```

---

### /ps-param-validation

Generate parameter validation attributes.

**Usage**: `/ps-param-validation <type>`

**Types**:

| Type     | Generated Validation                                    |
| -------- | ------------------------------------------------------- |
| `string` | ValidateNotNullOrEmpty, ValidateLength, ValidatePattern |
| `number` | ValidateRange, ValidateCount                            |
| `set`    | ValidateSet with values                                 |
| `path`   | ValidateScript for path existence                       |
| `email`  | ValidatePattern for email format                        |

**Example (path)**:

```powershell
[Parameter(Mandatory)]
[ValidateScript({
    if (Test-Path -Path $_ -PathType Container) {
        $true
    } else {
        throw "Path '$_' does not exist or is not a directory"
    }
})]
[string]$Path
```

**Example (email)**:

```powershell
[Parameter(Mandatory)]
[ValidatePattern('^[\w-\.]+@([\w-]+\.)+[\w-]{2,}$')]
[string]$Email
```

---

### /ps-error-handling

Generate error handling patterns.

**Usage**: `/ps-error-handling [--terminating] [--non-terminating]`

**Terminating Error Pattern**:

```powershell
try {
    # Risky operation
    $result = Invoke-RiskyOperation -ErrorAction Stop
}
catch [System.Net.WebException] {
    # Handle specific exception
    Write-Error "Network error: $($_.Exception.Message)"
    throw
}
catch [System.UnauthorizedAccessException] {
    # Handle access denied
    Write-Error "Access denied: $($_.Exception.Message)"
    throw
}
catch {
    # Handle all other exceptions
    $errorRecord = [System.Management.Automation.ErrorRecord]::new(
        $_.Exception,
        'OperationFailed',
        [System.Management.Automation.ErrorCategory]::OperationStopped,
        $null
    )
    $PSCmdlet.ThrowTerminatingError($errorRecord)
}
finally {
    # Cleanup code - always runs
    if ($resource) {
        $resource.Dispose()
    }
}
```

---

## Best Practices Applied

| Practice             | Implementation                            |
| -------------------- | ----------------------------------------- |
| Approved Verbs       | Use `Get-Verb` to validate                |
| Parameter Validation | ValidateNotNullOrEmpty, ValidateSet, etc. |
| Pipeline Support     | ValueFromPipeline, Begin/Process/End      |
| ShouldProcess        | For state-changing operations             |
| Comment-Based Help   | Full .SYNOPSIS, .DESCRIPTION, .EXAMPLE    |
| Error Handling       | Try/Catch with specific types             |
| Output               | Return objects, not formatted text        |

## References

| Topic              | Source                                                                                                                 |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| Approved Verbs     | https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/approved-verbs-for-windows-powershell-commands |
| Advanced Functions | https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_functions_advanced           |
| Classes            | https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_classes                      |
