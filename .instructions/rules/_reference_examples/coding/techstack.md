# CorpIT Scheduled Tasks - Tech Stack

Comprehensive inventory of technologies, infrastructure, and tooling used in this repository.

---

## 📋 Primary Languages

| Language | Version | Purpose |
|----------|---------|---------|
| **PowerShell** | 7.0+ (7.2+ recommended) | Core automation scripting |
| **Python** | 3.10+ | CLI tooling (`corpit-scout`) |
| **JavaScript/Node.js** | - | CI/CD and release automation |

---

## 🏗️ Infrastructure

### Execution Environment

| Component | Details |
|-----------|---------|
| **Host Server** | `vm-pss-p-wus3-1.blackline.corp` |
| **Operating System** | Windows Server 2019 |
| **Execution Model** | Windows Task Scheduler |
| **Shell** | PowerShell 7 (pwsh) + OpenSSH |
| **Remote Access** | SSH (ED25519 key-based authentication) |

### Domain Infrastructure

| Component | Details |
|-----------|---------|
| **Domain Controller** | `vm-dcx-p-wus3-1.blackline.corp` |
| **Active Directory Domain** | `BLACKLINE.corp` |
| **File Server** | `\\vm-fil-p-wus3-1.blackline.corp\Shares` |
| **SFTP Server** | `itsftp.blackline.corp` (onboarding document uploads) |

---

## ☁️ Cloud Services

### Microsoft 365 / Azure

| Service | Purpose |
|---------|---------|
| **Entra ID (Azure AD)** | Identity provider, user management |
| **Microsoft Graph API** | User/group management, mailbox operations |
| **Exchange Online** | Mailbox permissions, auto-reply, email forwarding |
| **SharePoint Online** | Site collection administration |
| **Microsoft Teams** | Direct Routing phone numbers, notifications |
| **Azure Key Vault** | Secrets storage (`bl-corpit-automation`) |
| **Azure Monitor (Log Analytics)** | Centralized logging and monitoring |
| **Azure Logic Apps** | Teams notification webhooks |

### Authentication Details

| Property | Value |
|----------|-------|
| **Tenant** | `bloffice.onmicrosoft.com` |
| **Tenant ID** | `45d659f4-1555-498b-93b5-0b99a89a284b` |
| **Auth Method** | Certificate-based (thumbprint: `25f547a3ed8a16db096757f4d296c82b3eacf628`) |

---

## 🔗 External Integrations

| System | Purpose | Endpoint |
|--------|---------|----------|
| **Workday (HRIS)** | Employee data source | `https://services1.wd108.myworkday.com` |
| **Jira Cloud** | Ticket management (ELC, BLIT projects) | `https://blsi.atlassian.net` |
| **Salesforce** | Account provisioning requests | (via email integration) |
| **Druva inSync** | Backup group assignments | (via AD groups) |
| **PRTG Network Monitor** | Task execution monitoring | Port 9876 (HTTP JSON API) |

---

## 📦 PowerShell Modules

### Microsoft Modules

| Module | Version | Purpose |
|--------|---------|---------|
| `Microsoft.Graph.Authentication` | 2.19.0 (pinned) | Graph API auth |
| `Microsoft.Graph.Users` | 2.19.0 | User management |
| `Microsoft.Graph.Groups` | 2.19.0 | Group management |
| `Microsoft.Graph.Users.Actions` | 2.19.0 | User actions |
| `ExchangeOnlineManagement` | 3.7.0+ | Exchange administration |
| `MicrosoftTeams` | - | Teams phone management |
| `PnP.PowerShell` | - | SharePoint operations |
| `Az.Accounts` / `Az.KeyVault` | - | Azure authentication |
| `ActiveDirectory` | - | On-prem AD operations |

### Third-Party Modules

| Module | Purpose |
|--------|---------|
| `PSFramework` | Logging, configuration |
| `JiraPS` | Jira ticket operations |
| `MSAL.PS` | OAuth2 token acquisition |

### Custom Modules (14 total)

| Module | Purpose |
|--------|---------|
| `BLMSModule.psm1` | Microsoft Graph & M365 operations |
| `BLADModule.psm1` | Active Directory operations |
| `BLJiraModule.psm1` | JIRA ticket management |
| `BLWorkdayModule.psm1` | Workday API integration |
| `BLLoggingModule.psm1` | Consolidated logging + Azure Monitor |
| `BLValidationModule.psm1` | User data validation |
| `BLNotificationModule.psm1` | Teams & email notifications |
| `BLOnboardingModule.psm1` | Onboarding logic |
| `BLOffboardingModule.psm1` | Offboarding logic |
| `BLOffboardingState.psm1` | Offboarding state management |
| `BLPDFModule.psm1` | PDF password sheet generation |
| `BLTemplateModule.psm1` | HTML/text template processing |
| `BLUtilityModule.psm1` | Retry logic, WhatIf handling |
| `BLActionRunner.psm1` | Generic action runner |
| `BLTaskStatusModule.psm1` | Task status tracking |

---

## 🐍 Python Dependencies (corpit-scout)

| Package | Purpose |
|---------|---------|
| `click` | CLI framework |
| `rich` | Terminal formatting |
| `GitPython` | Git repository operations |
| `directory-tree` | Directory visualization |
| `markdown` | Markdown processing |
| `pytest` | Testing (dev) |

---

## 🔧 Development & CI/CD Tools

### Version Control & Releases

| Tool | Purpose |
|------|---------|
| **Git** | Version control |
| **semantic-release** | Automated versioning & changelog |
| **commitizen** | Conventional commit CLI |
| **commitlint** | Commit message linting |

### Task Runner

| Tool | Purpose |
|------|---------|
| **mise** | Task runner & tool version management |
| **uv** | Python package management |
| **glow** | Markdown rendering in terminal |

### Node.js DevDependencies

```json
{
  "@commitlint/cli": "^18.6.0",
  "@commitlint/config-conventional": "^18.6.0",
  "@semantic-release/changelog": "^6.0.3",
  "@semantic-release/git": "^10.0.1",
  "commitizen": "^4.3.0",
  "cz-conventional-changelog": "^3.3.0",
  "semantic-release": "^24.2.0"
}
```

---

## 📊 Monitoring & Observability

| Component | Details |
|-----------|---------|
| **Azure Monitor** | Log Analytics workspace for centralized logs |
| **PRTG** | HTTP Data Advanced sensor for task heartbeats |
| **Status Files** | JSON files tracking task execution (`monitoring/task-status/`) |
| **Daily Log Files** | Date-organized logs in `logs/tasks/` |

---

## 📄 Output Formats

| Format | Usage |
|--------|-------|
| **PDF** | Password instruction sheets |
| **HTML** | Email templates, daily reports |
| **JSON** | Task status, API responses |
| **CSV** | Workday exports, data files |
| **Text** | Log files, JIRA comments |

---

## 🔐 Security Components

| Component | Details |
|-----------|---------|
| **Secrets Storage** | Azure Key Vault (`bl-corpit-automation`) |
| **Authentication** | Certificate-based (no passwords) |
| **Service Accounts** | `app_RBACUpdate`, `app_flowuser`, `app_workday_uploads` |
| **SSH Keys** | ED25519 for server access |

---

## 📁 Key Directories

| Directory | Purpose |
|-----------|---------|
| `tasks/` | Scheduled task automation scripts |
| `modules/` | Reusable PowerShell modules |
| `tools/` | Utility scripts and CLI tools |
| `assets/` | Email templates, CSS, images |
| `logs/` | Task execution logs |
| `monitoring/` | Task status JSON files |
| `prtg/` | PRTG monitoring server |
| `docs/` | Documentation |

---

*Last updated: 2026-01-21*
