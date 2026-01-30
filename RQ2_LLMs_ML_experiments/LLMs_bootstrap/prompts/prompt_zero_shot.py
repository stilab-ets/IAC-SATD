PROMPT_COT_improved = """
You are an expert Infrastructure-as-Code (IaC) developer. You must categorize IaC self-admitted technical debt (SATD) instances in Terraform code files. Each SATD instance includes:
- A single-line comment (keyword indicating technical debt),
- Context (adjacent explanatory comments),
- The associated code block.

STRICTLY follow the definitions and rules for each category provided below. Classify the instance into **all applicable categories**; this is a multi-label task. **Do not apply personal interpretation or prioritize categories** — only adhere to the definitions.

INSTANCE:
Technical_debt_single_line_comment: {comment}
Technical_debt_comment_context: {context}
Code_block_associated_if_exists: {code_block}

OUTPUT:  
List all matching categories using these labels (no explanation, just the codes):  
CAT1, CAT2, CAT3, CAT4, CAT5, CAT6, CAT7, CAT8

CATEGORY DEFINITIONS:

CAT1 - Computing Components Management Debt  
Covers misconfigurations or limitations in core compute-related infrastructure: virtual machines, containers, serverless functions, databases, and storage.  
**Apply if:**
- Comment/context refers to **setup/configuration** of these computing components.
- **Exclude** generic networking, security, or monitoring unless explicitly tied to compute (e.g., Kubernetes, ECS).
- Check code block if unclear:
  - Include: resource types like `aws_instance`, `azurerm_function_app`, modules named `"vm"`, `"storage_size"`, etc.
  - Exclude: networking/security/monitoring-specific types like `aws_security_group`, `log_analytics_workspace`.


CAT2 - IaC Code Debt
Covers Terraform code maintainability, readability, outdated practices, missing features, bugs, non-compliance with best practices.


CAT3 - Dependency Management Debt
Covers issues tied to Terraform core/version limits or provider-level limitations (not resource-level), often with references/links to Terraform or provider issues.


CAT4 - Security Debt
Covers weak security configurations related to firewall, security groups, IAM, encryption, key/credential management.


CAT5 - Networking Debt
Includes issues tied to routing/traffic (load balancing, ingress, egress), network addressing (VPC, subnets, zones), port management, domain configuration (e.g., Route 53).
YOU MUST STRICTLY EXCLUDE **security/monitoring** ITEMS UNLESS **EXPLICITLY** TIED TO NETWORKING.


CAT6 - Environment-Based Configuration Debt
Is more related to short term solutions applied for managing infrastructure environments, it includes:
- Environment staging (dev, prod, integration; must be **explicitly** mentioned),
- Automation/pipeline configs,
- Lifecycle rule automation (only lifecycle rules, not general rules).
Be strict and severe — include findings only if they clearly and explicitly relate to environment-based configuration debt.


CAT7 - Monitoring and Logging Debt
Covers issues related to missing or weak monitoring and logging configurations in infrastructure code.
Include only if there is clear and explicit evidence, such as:
- Use of monitoring/logging-specific resources (e.g., azurerm_monitor_diagnostic_setting),
- Modules named or labeled with terms like monitoring, logging, or similar.
Be strict and severe — include findings only if they clearly and explicitly relate to monitoring or logging configurations.


CAT8 - Test Debt
Covers the lack of testing practices in Terraform-based infrastructure provisioning.
Include only if there is clear evidence of testing intent or absence, such as:
- Use of keywords like: test, check, ensure, verify, investigate, inspect,
- Mentions of testing/security and static code checker tools like: tfsec, checkov, terrascan, etc.
If absent in comments/context, only include if code block/module name directly relates to testing.


REMEMBER:  
- Assign **all** applicable categories.  
- Do **not** apply your own judgment beyond the definitions.
- Answer only with the category codes (e.g., ANSWER: CAT1, CAT2, CAT3, CAT5); no extra text.

ANSWER:
"""

# CAT1 - Infrastructure Management Debt
# Covers issues related infrastructure components configuration to virtual machine config, container orchestration, storage/db management, serverless management, server management.
# **Apply if:**
# - The comment or context mentions **configuration** related to these areas.
# - **Exclude** Networking, Security, or Monitoring/Logging **unless they EXPLICITLY mention** infrastructure subcategories.
#   - To include “Load balancing in Kubernetes” → Infrastructure because of Kubernetes
#   - To exclude: “Configure load balancing” → Networking
# - If unclear from the comment/context, check the code block:
#   - `resource` types like `azurerm_virtual_machine`, `aws_lambda_function`, etc. → Include
#   - `module`/`variable` names like `"virtual-machine"`, `"storage_size"` → Include
#   - Resources clearly about networking, security, or monitoring (e.g., `security_policy`) → Exclude
#
#
# CAT2 - IaC Code Debt
# Covers Terraform code maintainability, readability, outdated practices, missing features, bugs, non-compliance with best practices.
#
#
# CAT3 - Dependency Management Debt
# Covers issues tied to Terraform core/version limits or provider-level limitations (not resource-level), often with references/links to Terraform or provider issues.
#
#
# CAT4 - Security Debt
# Covers weak security configurations related to firewall, security groups, IAM, encryption, key/credential management.
#
#
# CAT5 - Networking Debt
# Includes issues tied to routing/traffic (load balancing, ingress, egress), network addressing (VPC, subnets, zones), port management, domain configuration (e.g., Route 53).
# YOU MUST STRICTLY EXCLUDE **security/monitoring** ITEMS UNLESS **EXPLICITLY** TIED TO NETWORKING.
#
#
# CAT6 - Environment-Based Configuration Debt
# Is more related to short term solution applied for managing infrastructure environments, it includes:
# - Environment staging (dev, prod, integration; must be **explicitly** mentioned),
# - Automation/pipeline configs,
# - Lifecycle rule automation (only lifecycle rules, not general rules).
# Be strict and severe — include findings only if they clearly and explicitly relate to environment-based configuration debt.
#
#
# CAT7 - Monitoring and Logging Debt
# Covers issues related to missing or weak monitoring and logging configurations in infrastructure code.
# Include only if there is clear and explicit evidence, such as:
# - Use of monitoring/logging-specific resources (e.g., azurerm_monitor_diagnostic_setting),
# - Modules named or labeled with terms like monitoring, logging, or similar.
# Be strict and severe — include findings only if they clearly and explicitly relate to monitoring or logging configurations.
#
#
# CAT8 - Test Debt
# Covers the lack of testing practices in Terraform-based infrastructure provisioning.
# Include only if there is clear evidence of testing intent or absence, such as:
# - Use of keywords like: test, check, ensure, verify, investigate, inspect,
# - Mentions of testing/security and static code checker tools like: tfsec, checkov, terrascan, etc.
# If absent in comments/context, only include if code block/module name directly relates to testing.

# ----------------------ANCIENT PROMPT ---------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

# CAT1 - Infrastructure Management Debt
# Includes: virtual machine config, container orchestration, storage/db management, serverless management, server management.
#
# **Apply if:**
# - The comment or context mentions **configuration** related to these areas.
# - **Exclude** Networking, Security, or Monitoring/Logging **unless they EXPLICITLY mention** infrastructure subcategories.
#   - To include “Load balancing in Kubernetes” → Infrastructure because of Kubernetes
#   - To exclude: “Configure load balancing” → Networking
# - If unclear from the comment/context, check the code block:
#   - `resource` types like `azurerm_virtual_machine`, `aws_lambda_function`, etc. → Include
#   - `module`/`variable` names like `"virtual-machine"`, `"storage_size"` → Include
#   - Resources clearly about networking, security, or monitoring (e.g., `security_policy`) → Exclude
#
#
# CAT2 - IaC Code Debt
# Covers code maintainability, readability, outdated practices, missing features, bugs, non-compliance with best practices.
#
# CAT3 - Dependency Management
# Issues tied to Terraform core/version limits or provider-level limitations (not resource-level), often with references/links to Terraform or provider issues.
#
# CAT4 - Security Debt
# Covers weak security configurations: firewall, security groups, IAM, encryption, key/credential management.
#
# CAT5 - Networking Debt
# Includes: routing/traffic (load balancing, ingress, egress), network addressing (VPC, subnets, zones), port management, domain configuration (e.g., Route 53).
# Strictly exclude security/monitoring items unless **explicitly** tied to networking.
#
# CAT6 - Environment-Based Configuration Debt
# Includes:
# - Environment staging (dev, prod, integration; must be **explicitly** mentioned),
# - Automation/pipeline configs,
# - Lifecycle rule automation (only lifecycle rules, not general rules).
# Be strict — only include if clearly fitting.
#
# CAT7 - Monitoring and Logging Debt
# Covers monitoring/logging configurations (e.g., azurerm_monitor_diagnostic_setting, module “monitoring”). Be strict and severe — only include if **clearly and explicitly** fitting.
#
# CAT8 - Test Debt
# Keywords: test, check, ensure, investigate, inspect, or mention of tools like tfsec, checkov.
# If absent in comments/context, only include if code block/module name directly relates to testing.

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------- COT instructions
# ### Step-by-Step Reasoning Process (Chain of Thought):
#
# 1. **Review the Single-Line Comment and Context:**
#     - Read the `technical_debt_single_line_comment` and `technical_debt_comment_context`.
#     - For each category below, ask:  *Does the comment or context meet the definition for this category?*
#     - If YES, add that category tentatively.
#
# 2. **Review the Code Block:**
#     - If the comment and context are not sufficient, examine `code_block_associated_if_exists`.
#     - Check the `resource` type, `module`, `variable`, or `output` names.
#     - Ask: *Does the code block match the indicators for the category (type, name, etc.)?*
#     - If YES, include the category.
#
# 3. **Apply All Matching Categories:**
#     - This is a **multi-label** task: more than one category may apply.
#     - Use the category labels exactly as given: CAT1, CAT2, ..., CAT9.
#     - Do not skip categories that match just because another is present.
# ----------------------------------------------------------------------------------------------------------------------

# CAT9 - Documentation
# Comment context is explanatory (not a debt/issue):
# - Notes resolved debts (e.g., “this is fixed”),
# - Explains current setups, behavior, limitations,
# - Outlines setup steps or implementation details,
# - Provides rationale or unimplemented feature documentation.
# Must generally be longer (3+ lines).
