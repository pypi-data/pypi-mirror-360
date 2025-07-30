#!/usr/bin/env python3
import json
from typing import Any, Dict, List, Optional

from lokus.lgpd_validator import LGPDIssue
from lokus.security_validator import SecurityIssue


def report_findings(
    findings: List[Dict[str, Any]],
    swagger_file_path: str,
    config_file_path: str,
    output_json: bool = False,
    verbose: bool = False,
    security_issues: Optional[List[SecurityIssue]] = None,
    lgpd_issues: Optional[List[LGPDIssue]] = None,
) -> int:
    """
    Reports the findings from the validation process.

    Args:
        findings: List of forbidden key findings.
        swagger_file_path: Path to the Swagger/OpenAPI file.
        config_file_path: Path to the configuration file.
        output_json: Format of the output to JSON.
        verbose: Whether to include verbose output.
        security_issues: Optional list of security issues.
        lgpd_issues: Optional list of LGPD compliance issues.

    Returns:
        int: Exit code (0 for success, 1 for issues found, 2 for errors).
    """

    has_issues = bool(findings or security_issues or lgpd_issues)

    if output_json:
        # JSON output format
        output = {
            "swagger_file": swagger_file_path,
            "config_file": config_file_path,
            "findings": findings,
            "security_issues": [
                {
                    "rule_id": issue.rule_id,
                    "title": issue.title,
                    "description": issue.description,
                    "severity": issue.severity.value,
                    "path": issue.path,
                    "recommendation": issue.recommendation,
                    "reference": issue.reference,
                }
                for issue in (security_issues or [])
            ],
            "lgpd_issues": [
                {
                    "rule_id": issue.rule_id,
                    "title": issue.title,
                    "description": issue.description,
                    "severity": issue.severity.value,
                    "path": issue.path,
                    "recommendation": issue.recommendation,
                    "reference": issue.reference,
                }
                for issue in (lgpd_issues or [])
            ],
        }
        print(json.dumps(output))
    else:  # Default to text format
        print("Swagger/OpenAPI Specification Validator")
        print("--------------------------------------")
        print(f"Specification File: {swagger_file_path}")
        print(f"Configuration File: {config_file_path}")
        print("")

        if has_issues:
            print("STATUS: VALIDATION FAILED")

            if findings:
                print(f"\nForbidden Items Found: {len(findings)}")
                print("--------------------------------------")
                for i, finding in enumerate(findings, 1):
                    print(f"  {i}. Path: {finding.get('path')}")
                    print(f"     Key: {finding.get('key')}")
                    print(f"     Type: {finding.get('type')}")
                    print(f"     Reason: {finding.get('message')}")
                    if i < len(findings):
                        print("")

            if security_issues:
                print(f"\nSecurity Issues Found: {len(security_issues)}")
                print("--------------------------------------")
                for i, issue in enumerate(security_issues, 1):
                    print(f"  {i}. [{issue.severity.value}] {issue.title}")
                    print(f"     Rule ID: {issue.rule_id}")
                    print(f"     Path: {issue.path}")
                    print(f"     Description: {issue.description}")
                    print(f"     Recommendation: {issue.recommendation}")
                    print(f"     Reference: {issue.reference}")
                    if i < len(security_issues):
                        print("")

            if lgpd_issues:
                print(f"\nLGPD Compliance Issues Found: {len(lgpd_issues)}")
                print("--------------------------------------")
                for i, issue in enumerate(lgpd_issues, 1):
                    print(f"  {i}. [{issue.severity.value}] {issue.title}")
                    print(f"     Rule ID: {issue.rule_id}")
                    print(f"     Path: {issue.path}")
                    print(f"     Description: {issue.description}")
                    print(f"     Recommendation: {issue.recommendation}")
                    print(f"     Reference: {issue.reference}")
                    if i < len(lgpd_issues):
                        print("")

            print(
                "\nPlease review the findings and update the API specification or the validator configuration."
            )
        else:
            print("STATUS: VALIDATION PASSED - No issues found.")

    # Set exit status
    if has_issues:
        return 1  # Issues found
    else:
        return 0  # All clear


# Note: sys.exit() will be called in the main script based on the return value of this function
# and other potential errors (like file not found, parse errors) that occur before this stage.

if __name__ == "__main__":
    from src.security_validator import SecurityIssue, SecurityIssueSeverity

    sample_findings_issues = [
        {
            "path": "info.contact.email",
            "key": "email",
            "type": "forbidden_key_at_path",
            "message": "Publicly exposing contact emails in API specs can lead to spam or phishing.",
        },
        {
            "path": "components.securitySchemes.LegacyApiKey.x-api-key",
            "key": "x-api-key",
            "type": "forbidden_key",
            "message": "Key 'x-api-key' is globally forbidden.",
        },
    ]

    sample_security_issues = [
        SecurityIssue(
            rule_id="AUTH-001",
            title="Weak API Key Configuration",
            description="API Key 'apiKey' is not properly secured",
            severity=SecurityIssueSeverity.HIGH,
            path="components.securitySchemes.apiKey",
            recommendation="Configure API key to be sent in header or cookie",
        )
    ]

    sample_findings_no_issues = []

    print("--- Testing Reporter (Text Format - Issues Found) ---")
    exit_code_text_issues = report_findings(
        sample_findings_issues,
        "specs/api.yaml",
        ".forbidden_keys.yaml",
        "text",
        security_issues=sample_security_issues,
    )
    print(f"Exited with: {exit_code_text_issues} (Expected 1)")
    print("\n")

    print("--- Testing Reporter (Text Format - No Issues) ---")
    exit_code_text_no_issues = report_findings(
        sample_findings_no_issues,
        "specs/api_clean.yaml",
        ".forbidden_keys.yaml",
        "text",
    )
    print(f"Exited with: {exit_code_text_no_issues} (Expected 0)")
    print("\n")

    print("--- Testing Reporter (JSON Format - Issues Found) ---")
    exit_code_json_issues = report_findings(
        sample_findings_issues,
        "specs/api.yaml",
        ".forbidden_keys.yaml",
        "json",
        security_issues=sample_security_issues,
    )
    print(f"Exited with: {exit_code_json_issues} (Expected 1)")
    print("\n")

    print("--- Testing Reporter (JSON Format - No Issues) ---")
    exit_code_json_no_issues = report_findings(
        sample_findings_no_issues,
        "specs/api_clean.yaml",
        ".forbidden_keys.yaml",
        "json",
    )
    print(f"Exited with: {exit_code_json_no_issues} (Expected 0)")
    print("\n")

    print("--- Testing Reporter (Text Format - Verbose) ---")
    exit_code_text_verbose = report_findings(
        sample_findings_issues,
        "specs/api.yaml",
        ".forbidden_keys.yaml",
        "text",
        verbose=True,
        security_issues=sample_security_issues,
    )
    print(f"Exited with: {exit_code_text_verbose} (Expected 1)")
