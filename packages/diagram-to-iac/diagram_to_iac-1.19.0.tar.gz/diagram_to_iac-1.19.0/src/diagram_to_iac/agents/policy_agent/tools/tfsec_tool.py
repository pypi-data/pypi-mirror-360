"""
TfSec Tool - Policy scanning tool for Terraform configurations

This tool provides secure execution of tfsec policy scanning following
the established security patterns in the diagram-to-iac system.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from diagram_to_iac.tools.shell.shell import ShellExecutor, ShellExecInput


class TfSecScanInput(BaseModel):
    """Input for tfsec security scan."""
    repo_path: str = Field(..., description="Path to Terraform repository to scan")
    output_format: str = Field(default="json", description="Output format (json, text)")
    severity_filter: Optional[List[str]] = Field(default=None, description="Filter by severity levels")
    timeout: int = Field(default=120, description="Timeout in seconds for scan")


class TfSecFinding(BaseModel):
    """Represents a single tfsec finding."""
    rule_id: str = Field(..., description="tfsec rule ID")
    rule_description: str = Field(..., description="Description of the rule")
    severity: str = Field(..., description="Severity level (CRITICAL, HIGH, MEDIUM, LOW)")
    resource: str = Field(..., description="Terraform resource affected")
    location: Dict[str, Any] = Field(..., description="Location information")
    description: str = Field(..., description="Finding description")


class TfSecScanOutput(BaseModel):
    """Output from tfsec security scan."""
    scan_successful: bool = Field(..., description="Whether scan completed successfully")
    findings: List[TfSecFinding] = Field(default_factory=list, description="Security findings")
    total_findings: int = Field(default=0, description="Total number of findings")
    critical_count: int = Field(default=0, description="Number of critical findings")
    high_count: int = Field(default=0, description="Number of high severity findings")
    medium_count: int = Field(default=0, description="Number of medium severity findings")
    low_count: int = Field(default=0, description="Number of low severity findings")
    scan_duration: float = Field(default=0.0, description="Scan duration in seconds")
    raw_output: str = Field(default="", description="Raw tfsec output")
    error_message: Optional[str] = Field(default=None, description="Error message if scan failed")


class TfSecTool:
    """
    TfSec tool for Terraform security scanning.
    
    This tool provides secure execution of tfsec following the established
    security patterns in the diagram-to-iac system.
    """
    
    def __init__(self, config_path: str = None):
        """Initialize TfSec tool with security executor."""
        self.shell_executor = ShellExecutor(config_path=config_path)
        
    def scan(self, scan_input: TfSecScanInput) -> TfSecScanOutput:
        """
        Execute tfsec security scan on Terraform repository.
        
        Args:
            scan_input: TfSec scan configuration
            
        Returns:
            TfSecScanOutput: Scan results and findings
        """
        start_time = time.time()
        
        try:
            # Validate repository path exists
            repo_path = Path(scan_input.repo_path)
            if not repo_path.exists():
                return TfSecScanOutput(
                    scan_successful=False,
                    error_message=f"Repository path does not exist: {scan_input.repo_path}"
                )
            
            # Build tfsec command
            command = self._build_tfsec_command(scan_input)
            
            # Execute scan using secure shell executor
            shell_input = ShellExecInput(
                command=command,
                cwd=scan_input.repo_path,
                timeout=scan_input.timeout
            )
            
            shell_result = self.shell_executor.shell_exec(shell_input)
            scan_duration = time.time() - start_time
            
            # Parse tfsec output
            if shell_result.exit_code == 0 or shell_result.exit_code == 1:
                # Exit code 1 is normal for tfsec when findings are present
                return self._parse_tfsec_output(
                    shell_result.output, 
                    scan_duration,
                    True
                )
            else:
                return TfSecScanOutput(
                    scan_successful=False,
                    scan_duration=scan_duration,
                    raw_output=shell_result.output,
                    error_message=f"tfsec scan failed with exit code {shell_result.exit_code}"
                )
                
        except Exception as e:
            scan_duration = time.time() - start_time
            return TfSecScanOutput(
                scan_successful=False,
                scan_duration=scan_duration,
                error_message=f"tfsec scan error: {str(e)}"
            )
    
    def _build_tfsec_command(self, scan_input: TfSecScanInput) -> str:
        """Build tfsec command with appropriate options."""
        command_parts = ["tfsec"]
        
        # Add output format
        command_parts.extend(["--format", scan_input.output_format])
        
        # Add severity filter if specified
        if scan_input.severity_filter:
            for severity in scan_input.severity_filter:
                command_parts.extend(["--minimum-severity", severity.upper()])
        
        # Add current directory (will be set by shell executor)
        command_parts.append(".")
        
        return " ".join(command_parts)
    
    def _parse_tfsec_output(
        self, 
        raw_output: str, 
        scan_duration: float, 
        scan_successful: bool
    ) -> TfSecScanOutput:
        """Parse tfsec JSON output into structured format."""
        findings = []
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        try:
            if raw_output.strip():
                # Parse JSON output from tfsec
                tfsec_data = json.loads(raw_output)
                
                # Handle both single results and arrays
                results = tfsec_data.get("results", [])
                if not isinstance(results, list):
                    results = [results] if results else []
                
                for result in results:
                    severity = result.get("severity", "UNKNOWN").upper()
                    
                    finding = TfSecFinding(
                        rule_id=result.get("rule_id", ""),
                        rule_description=result.get("rule_description", ""),
                        severity=severity,
                        resource=result.get("resource", ""),
                        location=result.get("location", {}),
                        description=result.get("description", "")
                    )
                    findings.append(finding)
                    
                    # Count by severity
                    severity_key = severity.lower()
                    if severity_key in counts:
                        counts[severity_key] += 1
                        
        except json.JSONDecodeError:
            # If JSON parsing fails, treat as text output with no findings
            pass
        except Exception as e:
            # Log parsing error but continue
            pass
        
        return TfSecScanOutput(
            scan_successful=scan_successful,
            findings=findings,
            total_findings=len(findings),
            critical_count=counts["critical"],
            high_count=counts["high"],
            medium_count=counts["medium"],
            low_count=counts["low"],
            scan_duration=scan_duration,
            raw_output=raw_output
        )
    
    def should_block_apply(self, scan_output: TfSecScanOutput, block_on_severity: List[str]) -> bool:
        """
        Determine if terraform apply should be blocked based on findings.
        
        Args:
            scan_output: Results from tfsec scan
            block_on_severity: List of severity levels that should block apply
            
        Returns:
            bool: True if apply should be blocked
        """
        if not scan_output.scan_successful:
            # Block on scan failures
            return True
            
        block_levels = [level.upper() for level in block_on_severity]
        
        for finding in scan_output.findings:
            if finding.severity.upper() in block_levels:
                return True
                
        return False
    
    def create_findings_artifact(
        self, 
        scan_output: TfSecScanOutput, 
        artifact_path: str
    ) -> bool:
        """
        Create JSON artifact file with scan findings.
        
        Args:
            scan_output: Results from tfsec scan
            artifact_path: Path where to save the artifact
            
        Returns:
            bool: True if artifact was created successfully
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
            
            # Create artifact data
            artifact_data = {
                "scan_timestamp": time.time(),
                "scan_successful": scan_output.scan_successful,
                "total_findings": scan_output.total_findings,
                "severity_counts": {
                    "critical": scan_output.critical_count,
                    "high": scan_output.high_count,
                    "medium": scan_output.medium_count,
                    "low": scan_output.low_count
                },
                "scan_duration": scan_output.scan_duration,
                "findings": [finding.model_dump() for finding in scan_output.findings],
                "raw_output": scan_output.raw_output
            }
            
            # Write artifact file
            with open(artifact_path, 'w') as f:
                json.dump(artifact_data, f, indent=2)
                
            return True
            
        except Exception as e:
            return False