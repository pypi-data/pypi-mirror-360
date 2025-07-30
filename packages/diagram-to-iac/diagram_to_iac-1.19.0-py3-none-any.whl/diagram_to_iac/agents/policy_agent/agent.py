"""
Policy Agent - Security Policy Enforcement for Terraform

This PolicyAgent enforces security policies using tfsec scanning and provides
policy gate functionality to block terraform apply operations on critical violations.
It integrates with the existing multi-agent architecture following established patterns.

Key Features:
- tfsec security scanning with JSON output
- Policy evaluation and apply blocking on critical violations
- JSON findings artifacts for audit trails
- Integration with LangGraph multi-agent workflow
- Follows established security patterns with ShellExecutor

Architecture:
1. LLM-based planner analyzes input and routes to appropriate nodes
2. Policy scan node executes tfsec scans using secure shell execution
3. Policy evaluation node determines if violations should block operations
4. Artifact creation node posts JSON findings for audit trails
5. Block node prevents terraform apply on critical violations
"""

import os
import time
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import TypedDict, Annotated, Optional, List, Dict, Any

import yaml
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field

# Import core infrastructure
from diagram_to_iac.core.agent_base import AgentBase
from diagram_to_iac.core.memory import create_memory, LangGraphMemoryAdapter
from diagram_to_iac.core.config_loader import get_config, get_config_value
from .tools.tfsec_tool import TfSecTool, TfSecScanInput, TfSecScanOutput


# --- Pydantic Schemas for Agent I/O ---
class PolicyAgentInput(BaseModel):
    """Input schema for PolicyAgent operations."""
    query: str = Field(..., description="Policy enforcement query or command")
    repo_path: str = Field(..., description="Path to Terraform repository")
    thread_id: Optional[str] = Field(default=None, description="Thread ID for conversation tracking")
    operation_type: str = Field(default="scan", description="Type of policy operation (scan, evaluate, block)")


class PolicyAgentOutput(BaseModel):
    """Output schema for PolicyAgent operations."""
    result: str = Field(..., description="Policy enforcement result")
    thread_id: str = Field(..., description="Thread ID for conversation tracking")
    policy_status: str = Field(..., description="Policy status (PASS, BLOCK, ERROR)")
    findings_count: int = Field(default=0, description="Number of policy findings")
    critical_findings: int = Field(default=0, description="Number of critical findings")
    should_block_apply: bool = Field(default=False, description="Whether to block terraform apply")
    artifact_path: Optional[str] = Field(default=None, description="Path to findings artifact")
    error_message: Optional[str] = Field(default=None, description="Error message if operation failed")


# --- LangGraph State Schema ---
class PolicyAgentState(TypedDict):
    """State schema for PolicyAgent workflow."""
    messages: Annotated[List[BaseMessage], "conversation history"]
    query: str
    repo_path: str
    thread_id: str
    operation_type: str
    scan_results: Optional[TfSecScanOutput]
    policy_status: str
    should_block_apply: bool
    artifact_path: Optional[str]
    error_message: Optional[str]
    final_result: str


class PolicyAgent(AgentBase):
    """
    Policy Agent for security policy enforcement in Terraform workflows.
    
    This agent provides security policy scanning and enforcement using tfsec,
    with the ability to block terraform apply operations on critical violations.
    """
    
    def __init__(self, config_path: str = None, memory_type: str = "persistent"):
        """Initialize PolicyAgent with configuration and tools."""
        self.config_path = config_path
        
        # Initialize logging first
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize memory
        self.memory = create_memory(memory_type=memory_type)
        self.memory_adapter = LangGraphMemoryAdapter(self.memory)
        
        # Initialize tools
        self.tfsec_tool = TfSecTool(config_path=config_path)
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load agent configuration using centralized system with fallback to direct file loading."""
        try:
            config = get_config()
            policy_config = config.get('agents', {}).get('policy_agent', {})
            
            if policy_config:
                self.logger.info("Configuration loaded from centralized system")
                return policy_config
            else:
                self.logger.warning("No policy agent configuration found in centralized system. Using defaults.")
                return self._get_fallback_config()
        except Exception as e:
            self.logger.warning(f"Failed to load from centralized config: {e}. Falling back to direct file loading.")
            # Fallback to direct file loading for backward compatibility
            if self.config_path and os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f)
            
            # Default configuration
            config_file = os.path.join(os.path.dirname(__file__), "config.yaml")
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return yaml.safe_load(f)
                    
            # Fallback minimal configuration
            return self._get_fallback_config()
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Get fallback configuration using centralized values."""
        return {
            "llm": {
                "model_name": get_config_value("ai.default_model", "gpt-4o-mini"),
                "temperature": get_config_value("ai.default_temperature", 0.1)
            },
            "policy": {
                "tfsec": {
                    "enabled": get_config_value("tools.policy.tfsec_enabled", True),
                    "timeout_seconds": get_config_value("network.shell_timeout", 120),
                    "block_on_severity": get_config_value("tools.policy.block_on_severity", ["CRITICAL", "HIGH"]),
                    "artifact_on_severity": get_config_value("tools.policy.artifact_on_severity", ["CRITICAL", "HIGH", "MEDIUM"])
                }
            }
        }
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for policy enforcement."""
        workflow = StateGraph(PolicyAgentState)
        
        # Add nodes
        workflow.add_node("planner", self._planner_llm_node)
        workflow.add_node("policy_scan", self._policy_scan_node)
        workflow.add_node("policy_evaluate", self._policy_evaluate_node)
        workflow.add_node("policy_block", self._policy_block_node)
        workflow.add_node("policy_report", self._policy_report_node)
        
        # Add edges
        workflow.set_entry_point("planner")
        workflow.add_conditional_edges(
            "planner",
            self._route_after_planner,
            {
                "policy_scan": "policy_scan",
                "policy_evaluate": "policy_evaluate", 
                "policy_block": "policy_block",
                "policy_report": "policy_report",
                "end": END
            }
        )
        
        # Policy scan flows to evaluation
        workflow.add_edge("policy_scan", "policy_evaluate")
        
        # Policy evaluation routes to block or report
        workflow.add_conditional_edges(
            "policy_evaluate",
            self._route_after_evaluation,
            {
                "policy_block": "policy_block",
                "policy_report": "policy_report"
            }
        )
        
        # Block and report both end
        workflow.add_edge("policy_block", END)
        workflow.add_edge("policy_report", END)
        
        return workflow.compile(checkpointer=MemorySaver())
    
    def _planner_llm_node(self, state: PolicyAgentState):
        """LLM-based planner node for routing policy operations."""
        try:
            query_content = state.get("query", "")
            
            # Use simple rule-based routing for now (can be enhanced with LLM later)
            route_decision = self._determine_route(query_content, state)
            
            self.memory.add_to_conversation(
                "assistant",
                f"Policy planner routing to: {route_decision}",
                {"agent": "policy_agent", "node": "planner", "route": route_decision}
            )
            
            return {"final_result": route_decision}
            
        except Exception as e:
            self.logger.error(f"Policy planner error: {str(e)}", exc_info=True)
            return {"final_result": "end", "error_message": str(e)}
    
    def _determine_route(self, query: str, state: PolicyAgentState) -> str:
        """Determine routing based on query content and state."""
        query_lower = query.lower()
        operation_type = state.get("operation_type", "scan")
        
        if operation_type == "scan" or "scan" in query_lower:
            return "policy_scan"
        elif operation_type == "evaluate" or "evaluate" in query_lower:
            return "policy_evaluate"
        elif operation_type == "block" or "block" in query_lower:
            return "policy_block"  
        elif "report" in query_lower or "artifact" in query_lower:
            return "policy_report"
        else:
            return "policy_scan"  # Default to scan
    
    def _policy_scan_node(self, state: PolicyAgentState):
        """Execute tfsec security scan on the repository."""
        try:
            repo_path = state.get("repo_path", "")
            
            self.logger.info(f"Starting policy scan for repository: {repo_path}")
            
            # Configure scan input
            scan_input = TfSecScanInput(
                repo_path=repo_path,
                output_format="json",
                timeout=self.config.get("policy", {}).get("tfsec", {}).get("timeout_seconds", 120)
            )
            
            # Execute scan
            scan_results = self.tfsec_tool.scan(scan_input)
            
            if scan_results.scan_successful:
                self.logger.info(f"Policy scan completed: {scan_results.total_findings} findings")
                status_msg = f"Policy scan completed successfully with {scan_results.total_findings} findings"
            else:
                self.logger.error(f"Policy scan failed: {scan_results.error_message}")
                status_msg = f"Policy scan failed: {scan_results.error_message}"
            
            self.memory.add_to_conversation(
                "assistant",
                status_msg,
                {
                    "agent": "policy_agent",
                    "node": "policy_scan",
                    "findings_count": scan_results.total_findings,
                    "scan_successful": scan_results.scan_successful
                }
            )
            
            return {
                "scan_results": scan_results,
                "policy_status": "SCANNED" if scan_results.scan_successful else "ERROR"
            }
            
        except Exception as e:
            error_msg = f"Policy scan node error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return {
                "policy_status": "ERROR",
                "error_message": error_msg
            }
    
    def _policy_evaluate_node(self, state: PolicyAgentState):
        """Evaluate scan results and determine if apply should be blocked."""
        try:
            scan_results = state.get("scan_results")
            if not scan_results:
                return {"policy_status": "ERROR", "error_message": "No scan results to evaluate"}
            
            # Get blocking configuration
            block_on_severity = self.config.get("policy", {}).get("tfsec", {}).get("block_on_severity", ["CRITICAL", "HIGH"])
            
            # Determine if apply should be blocked
            should_block = self.tfsec_tool.should_block_apply(scan_results, block_on_severity)
            
            if should_block:
                self.logger.warning(f"Policy evaluation: BLOCK - {scan_results.critical_count} critical, {scan_results.high_count} high severity findings")
                policy_status = "BLOCK"
            else:
                self.logger.info(f"Policy evaluation: PASS - No blocking violations found")
                policy_status = "PASS"
            
            self.memory.add_to_conversation(
                "assistant",
                f"Policy evaluation: {policy_status} - Should block apply: {should_block}",
                {
                    "agent": "policy_agent",
                    "node": "policy_evaluate",
                    "policy_status": policy_status,
                    "should_block_apply": should_block,
                    "critical_findings": scan_results.critical_count,
                    "high_findings": scan_results.high_count
                }
            )
            
            return {
                "policy_status": policy_status,
                "should_block_apply": should_block
            }
            
        except Exception as e:
            error_msg = f"Policy evaluation error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return {
                "policy_status": "ERROR",
                "error_message": error_msg
            }
    
    def _policy_block_node(self, state: PolicyAgentState):
        """Handle policy blocking - prevent terraform apply and create artifacts."""
        try:
            scan_results = state.get("scan_results")
            repo_path = state.get("repo_path", "")
            
            # Create artifact for audit trail
            artifact_path = self._create_artifact(scan_results, repo_path)
            
            block_msg = f"POLICY VIOLATION: Terraform apply blocked due to {scan_results.critical_count} critical and {scan_results.high_count} high severity policy violations"
            
            self.logger.warning(block_msg)
            self.memory.add_to_conversation(
                "assistant",
                block_msg,
                {
                    "agent": "policy_agent",
                    "node": "policy_block",
                    "action": "blocked_apply",
                    "artifact_path": artifact_path
                }
            )
            
            return {
                "final_result": block_msg,
                "artifact_path": artifact_path
            }
            
        except Exception as e:
            error_msg = f"Policy block node error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return {
                "final_result": error_msg,
                "error_message": error_msg
            }
    
    def _policy_report_node(self, state: PolicyAgentState):
        """Generate policy report and artifacts."""
        try:
            scan_results = state.get("scan_results")
            repo_path = state.get("repo_path", "")
            
            # Create artifact for audit trail
            artifact_path = self._create_artifact(scan_results, repo_path)
            
            report_msg = f"Policy scan completed: {scan_results.total_findings} findings ({scan_results.critical_count} critical, {scan_results.high_count} high, {scan_results.medium_count} medium, {scan_results.low_count} low)"
            
            self.logger.info(report_msg)
            self.memory.add_to_conversation(
                "assistant",
                report_msg,
                {
                    "agent": "policy_agent",
                    "node": "policy_report",
                    "action": "generated_report",
                    "artifact_path": artifact_path
                }
            )
            
            return {
                "final_result": report_msg,
                "artifact_path": artifact_path
            }
            
        except Exception as e:
            error_msg = f"Policy report node error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return {
                "final_result": error_msg,
                "error_message": error_msg
            }
    
    def _create_artifact(self, scan_results: TfSecScanOutput, repo_path: str) -> Optional[str]:
        """Create JSON artifact with policy findings."""
        try:
            # Get artifact configuration
            artifacts_config = self.config.get("policy", {}).get("artifacts", {})
            output_dir = artifacts_config.get("output_dir", "/workspace/.policy_findings")
            
            # Create artifact path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = artifacts_config.get("json_filename", "policy_findings_{timestamp}.json").format(timestamp=timestamp)
            artifact_path = os.path.join(output_dir, filename)
            
            # Create artifact
            if self.tfsec_tool.create_findings_artifact(scan_results, artifact_path):
                return artifact_path
            else:
                self.logger.warning("Failed to create policy findings artifact")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating policy artifact: {str(e)}")
            return None
    
    def _route_after_planner(self, state: PolicyAgentState) -> str:
        """Route after planner decision."""
        final_result = state.get("final_result", "")
        
        if final_result == "policy_scan":
            return "policy_scan"
        elif final_result == "policy_evaluate":
            return "policy_evaluate"
        elif final_result == "policy_block":
            return "policy_block"
        elif final_result == "policy_report":
            return "policy_report"
        else:
            return "end"
    
    def _route_after_evaluation(self, state: PolicyAgentState) -> str:
        """Route after policy evaluation."""
        should_block = state.get("should_block_apply", False)
        
        if should_block:
            return "policy_block"
        else:
            return "policy_report"
    
    # --- AgentBase Implementation ---
    
    def plan(self, agent_input: PolicyAgentInput) -> Dict[str, Any]:
        """Generate plan for policy enforcement."""
        return {
            "operation": "policy_enforcement",
            "repo_path": agent_input.repo_path,
            "query": agent_input.query,
            "steps": ["scan", "evaluate", "report_or_block"]
        }
    
    def run(self, agent_input: PolicyAgentInput) -> PolicyAgentOutput:
        """Execute policy enforcement workflow."""
        try:
            thread_id = agent_input.thread_id or str(uuid.uuid4())
            
            # Prepare initial state
            initial_state = PolicyAgentState(
                messages=[HumanMessage(content=agent_input.query)],
                query=agent_input.query,
                repo_path=agent_input.repo_path,
                thread_id=thread_id,
                operation_type=agent_input.operation_type,
                scan_results=None,
                policy_status="PENDING",
                should_block_apply=False,
                artifact_path=None,
                error_message=None,
                final_result=""
            )
            
            # Execute workflow
            config = {"configurable": {"thread_id": thread_id}}
            final_state = None
            
            for state in self.workflow.stream(initial_state, config):
                final_state = state
            
            if not final_state:
                raise RuntimeError("Workflow execution failed - no final state")
            
            # Extract results from final state
            state_values = list(final_state.values())[0] if final_state else {}
            scan_results = state_values.get("scan_results")
            
            return PolicyAgentOutput(
                result=state_values.get("final_result", "Policy enforcement completed"),
                thread_id=thread_id,
                policy_status=state_values.get("policy_status", "COMPLETED"),
                findings_count=scan_results.total_findings if scan_results else 0,
                critical_findings=scan_results.critical_count if scan_results else 0,
                should_block_apply=state_values.get("should_block_apply", False),
                artifact_path=state_values.get("artifact_path"),
                error_message=state_values.get("error_message")
            )
            
        except Exception as e:
            self.logger.error(f"Policy agent execution failed: {str(e)}", exc_info=True)
            return PolicyAgentOutput(
                result=f"Policy enforcement failed: {str(e)}",
                thread_id=agent_input.thread_id or "unknown",
                policy_status="ERROR",
                error_message=str(e)
            )
    
    def report(self, agent_output: PolicyAgentOutput) -> str:
        """Generate human-readable report of policy enforcement results."""
        report_lines = [
            "=== Policy Enforcement Report ===",
            f"Status: {agent_output.policy_status}",
            f"Total Findings: {agent_output.findings_count}",
            f"Critical Findings: {agent_output.critical_findings}",
            f"Should Block Apply: {agent_output.should_block_apply}",
        ]
        
        if agent_output.artifact_path:
            report_lines.append(f"Artifact: {agent_output.artifact_path}")
        
        if agent_output.error_message:
            report_lines.append(f"Error: {agent_output.error_message}")
        
        report_lines.append(f"Result: {agent_output.result}")
        
        return "\n".join(report_lines)