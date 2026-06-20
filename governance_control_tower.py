"""
╔══════════════════════════════════════════════════════════════════════╗
║   ENTERPRISE AI GOVERNANCE CONTROL TOWER                            ║
║   Christopher Crilly Pienaah | Kaggle Capstone 2026                 ║
║                                                                      ║
║   Track: Agents for Business                                         ║
║   Framework: Google Agent Development Kit (ADK)                      ║
║                                                                      ║
║   Architecture:                                                      ║
║     Governance Supervisor                                            ║
║       ├── Regulatory Intelligence Agent  (OSFI Navigator)           ║
║       ├── Compliance Assessment Agent    (OSFI Audit Copilot)       ║
║       ├── Model Risk Agent               (Model Risk Dashboard)     ║
║       ├── Reliability Evaluation Agent   (GenAI Reliability)        ║
║       └── Benchmarking Agent             (CanFraudBench)            ║
║     Deterministic Guardrail Engine                                   ║
║     Executive Report Generator                                       ║
║                                                                      ║
║   Live Systems:                                                      ║
║     osfi-navigator-frontend.vercel.app                              ║
║     osfi-audit-copilot-frontend.vercel.app                          ║
║     model-risk-dashboard.vercel.app                                  ║
║     genai-reliability-framework.vercel.app                           ║
║     github.com/CrillyPienaah/canfraudbench                          ║
╚══════════════════════════════════════════════════════════════════════╝

BLUE OCEAN POSITIONING:
Most developers build agents that write text.
This system builds multi-agent governance infrastructure that evaluates
AI models for enterprise readiness, regulatory compliance, and model risk
— before they reach production in regulated industries.

Target: Canadian federally regulated financial institutions
Regulatory Driver: OSFI Guideline E-23 (enforcement May 2027)
"""

import json
import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════
# SECTION 1: DETERMINISTIC VALIDATION RULES
# This is the foundation. The ADK graph and MCP schemas serve the rules,
# not the other way around. These rules are deterministic — no LLM
# can override them. This is what makes the system enterprise-grade.
# ══════════════════════════════════════════════════════════════════════

# Enterprise governance thresholds used for this demo, mapped to OSFI E-23 model risk expectations.
GOVERNANCE_THRESHOLDS = {
    # Fairness — Adverse Impact Ratio must be ≥ 0.80 (4/5ths rule)
    "air_min": 0.80,
    # Model Drift — Population Stability Index
    "psi_max": 0.20,          # > 0.20 = significant drift, investigate
    "psi_warning": 0.10,      # 0.10-0.20 = moderate drift, monitor
    # Reliability — Hallucination / grounding risk
    "hallucination_max": 0.10,
    # Performance — Minimum AUC for production models
    "auc_min": 0.70,
    # Calibration — Expected Calibration Error
    "ece_max": 0.05,
    # Equal Opportunity — TPR gap between demographic groups
    "tpr_gap_max": 0.10,
}


@dataclass
class GovernanceMetrics:
    """
    Standardized metrics schema for governance evaluation.
    All five agents contribute to this shared schema.
    """
    model_id: str
    model_name: str
    regulatory_framework: str = "OSFI E-23"

    # Performance metrics
    auc: float = 0.0
    ks_statistic: float = 0.0
    ece: float = 0.0

    # Fairness metrics (from CanFraudBench methodology)
    air: float = 0.0          # Adverse Impact Ratio
    demographic_parity: float = 0.0
    equal_opportunity: float = 0.0
    tpr_gap: float = 0.0

    # Drift metrics (from Model Risk Dashboard)
    psi: float = 0.0          # Population Stability Index
    csi: float = 0.0          # Characteristic Stability Index

    # Reliability metrics (from GenAI Reliability Framework)
    hallucination_risk: float = 0.0
    grounding_score: float = 0.0
    citation_coverage: float = 0.0

    # Regulatory readiness (from OSFI Navigator + Audit Copilot)
    regulatory_citations_present: bool = False
    audit_trail_generated: bool = False
    osfi_e23_sections_covered: List[str] = None

    def __post_init__(self):
        if self.osfi_e23_sections_covered is None:
            self.osfi_e23_sections_covered = []


def evaluate_guardrails(metrics: GovernanceMetrics) -> Dict[str, Any]:
    """
    Deterministic guardrail evaluation engine.

    This is the core of the Control Tower. Rules are hard-coded —
    no LLM can override them. This is what enterprises need:
    predictable, auditable, tamper-proof governance gates.

    Returns a structured assessment with APPROVED/BLOCKED status
    and a complete audit trail of every rule evaluated.
    """
    failures = []
    warnings = []
    passed = []

    # ── Fairness Guardrails ──────────────────────────────────────────
    if metrics.air < GOVERNANCE_THRESHOLDS["air_min"]:
        failures.append({
            "rule": "FAIRNESS_AIR",
            "severity": "CRITICAL",
            "message": f"Adverse Impact Ratio {metrics.air:.3f} below minimum {GOVERNANCE_THRESHOLDS['air_min']}",
            "osfi_reference": "OSFI E-23 Section 6.2: Fairness and Bias",
            "remediation": "Retrain with fairness constraints or apply post-processing calibration"
        })
    else:
        passed.append(f"Fairness AIR: {metrics.air:.3f} ≥ {GOVERNANCE_THRESHOLDS['air_min']} ✓")

    if metrics.tpr_gap > GOVERNANCE_THRESHOLDS["tpr_gap_max"]:
        failures.append({
            "rule": "FAIRNESS_EQUAL_OPPORTUNITY",
            "severity": "HIGH",
            "message": f"TPR gap {metrics.tpr_gap:.3f} exceeds maximum {GOVERNANCE_THRESHOLDS['tpr_gap_max']}",
            "osfi_reference": "OSFI E-23 Section 6.2: Equal Opportunity",
            "remediation": "Apply equalized odds post-processing"
        })
    else:
        passed.append(f"Equal Opportunity TPR gap: {metrics.tpr_gap:.3f} ≤ {GOVERNANCE_THRESHOLDS['tpr_gap_max']} ✓")

    # ── Model Drift Guardrails ───────────────────────────────────────
    if metrics.psi > GOVERNANCE_THRESHOLDS["psi_max"]:
        failures.append({
            "rule": "DRIFT_PSI_CRITICAL",
            "severity": "CRITICAL",
            "message": f"PSI {metrics.psi:.3f} indicates significant distribution shift",
            "osfi_reference": "OSFI E-23 Section 5.1: Model Monitoring",
            "remediation": "Immediate model retraining required"
        })
    elif metrics.psi > GOVERNANCE_THRESHOLDS["psi_warning"]:
        warnings.append({
            "rule": "DRIFT_PSI_WARNING",
            "severity": "WARNING",
            "message": f"PSI {metrics.psi:.3f} indicates moderate drift — monitor closely",
            "osfi_reference": "OSFI E-23 Section 5.1: Model Monitoring",
        })
    else:
        passed.append(f"Model Drift PSI: {metrics.psi:.3f} within threshold ✓")

    # ── Performance Guardrails ───────────────────────────────────────
    if metrics.auc < GOVERNANCE_THRESHOLDS["auc_min"]:
        failures.append({
            "rule": "PERFORMANCE_AUC",
            "severity": "HIGH",
            "message": f"AUC {metrics.auc:.3f} below minimum acceptable {GOVERNANCE_THRESHOLDS['auc_min']}",
            "osfi_reference": "OSFI E-23 Section 4.2: Model Performance Standards",
            "remediation": "Improve model or replace with better performing alternative"
        })
    else:
        passed.append(f"Performance AUC: {metrics.auc:.3f} ≥ {GOVERNANCE_THRESHOLDS['auc_min']} ✓")

    if metrics.ece > GOVERNANCE_THRESHOLDS["ece_max"]:
        warnings.append({
            "rule": "CALIBRATION_ECE",
            "severity": "WARNING",
            "message": f"ECE {metrics.ece:.3f} indicates poor probability calibration",
            "osfi_reference": "OSFI E-23 Section 4.3: Calibration",
        })
    else:
        passed.append(f"Calibration ECE: {metrics.ece:.3f} within threshold ✓")

    # ── Reliability Guardrails ───────────────────────────────────────
    if metrics.hallucination_risk > GOVERNANCE_THRESHOLDS["hallucination_max"]:
        failures.append({
            "rule": "RELIABILITY_HALLUCINATION",
            "severity": "CRITICAL",
            "message": f"Hallucination risk {metrics.hallucination_risk:.3f} exceeds maximum {GOVERNANCE_THRESHOLDS['hallucination_max']}",
            "osfi_reference": "OSFI E-23 Section 7.1: Model Reliability",
            "remediation": "Implement RAG with citation validation before deployment"
        })
    else:
        passed.append(f"Reliability Hallucination Risk: {metrics.hallucination_risk:.3f} ✓")

    # ── Regulatory Readiness Guardrails ─────────────────────────────
    if not metrics.regulatory_citations_present:
        failures.append({
            "rule": "REGULATORY_CITATIONS",
            "severity": "HIGH",
            "message": "No regulatory citations present in model documentation",
            "osfi_reference": "OSFI E-23 Section 3.1: Documentation Requirements",
            "remediation": "Add OSFI E-23 citations to model card and documentation"
        })
    else:
        passed.append("Regulatory citations present ✓")

    if not metrics.audit_trail_generated:
        failures.append({
            "rule": "AUDIT_TRAIL",
            "severity": "HIGH",
            "message": "No audit trail generated for this model evaluation",
            "osfi_reference": "OSFI E-23 Section 8.1: Governance and Accountability",
            "remediation": "Generate complete audit trail before submission for approval"
        })
    else:
        passed.append("Audit trail generated ✓")

    # ── Final Determination ──────────────────────────────────────────
    critical_failures = [f for f in failures if f["severity"] == "CRITICAL"]
    status = "BLOCKED" if failures else ("CONDITIONAL" if warnings else "APPROVED")

    return {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "model_id": metrics.model_id,
        "regulatory_framework": metrics.regulatory_framework,
        "summary": {
            "total_rules_evaluated": len(failures) + len(warnings) + len(passed),
            "passed": len(passed),
            "warnings": len(warnings),
            "failures": len(failures),
            "critical_failures": len(critical_failures),
        },
        "failures": failures,
        "warnings": warnings,
        "passed_rules": passed,
        "audit_required": status == "BLOCKED",
        "recommendation": _get_recommendation(status, failures),
    }


def _get_recommendation(status: str, failures: List[Dict]) -> str:
    if status == "APPROVED":
        return "Model meets all OSFI E-23 governance requirements. Approved for production deployment."
    elif status == "CONDITIONAL":
        return "Model passes critical checks but has warnings. Conditional approval pending remediation of warnings."
    else:
        critical = [f for f in failures if f["severity"] == "CRITICAL"]
        if critical:
            rules = ", ".join(f["rule"] for f in critical)
            return f"Model BLOCKED from production. Critical failures: {rules}. Immediate remediation required."
        return "Model blocked pending resolution of governance failures. See remediation guidance above."


# ══════════════════════════════════════════════════════════════════════
# SECTION 2: MCP-STYLE TOOL SCHEMAS
# Each live system is exposed as a tool the Supervisor Agent can call.
# In production these would be real MCP server connections to each
# live Railway/Vercel endpoint.
# ══════════════════════════════════════════════════════════════════════

class OSFINavigatorTool:
    """
    MCP-style tool connecting to OSFI Navigator.
    Live: osfi-navigator-production.up.railway.app

    Retrieves regulatory expectations from OSFI E-23 for a given
    model type and use case. Provides inline citation chips.
    """
    name = "osfi_navigator"
    description = "Retrieve OSFI E-23 regulatory requirements for an AI model"

    @staticmethod
    async def call(model_type: str, use_case: str) -> Dict[str, Any]:
        logger.info(f"[OSFI Navigator] Querying regulatory requirements for {model_type} / {use_case}")

        # In production: POST to osfi-navigator-production.up.railway.app/query
        # For demo: return structured mock based on real E-23 content
        return {
            "tool": "osfi_navigator",
            "regulatory_framework": "OSFI E-23",
            "model_type": model_type,
            "applicable_sections": [
                "Section 3: Governance Framework",
                "Section 4: Model Development and Validation",
                "Section 5: Model Monitoring",
                "Section 6: Fairness and Bias",
                "Section 7: Reliability and Robustness",
                "Section 8: Accountability and Audit",
            ],
            "key_requirements": [
                "Model risk governance framework must be documented",
                "Independent validation required before production",
                "Ongoing monitoring with PSI/CSI metrics",
                "Fairness testing using AIR ≥ 0.80",
                "Hallucination controls for generative AI components",
                "Complete audit trail for all model decisions",
            ],
            "citations_present": True,
            "enforcement_date": "May 2027",
        }


class AuditCopilotTool:
    """
    MCP-style tool connecting to OSFI Audit Copilot.
    Live: osfi-audit-copilot-production-f87b.up.railway.app

    Assesses compliance gaps between model documentation
    and OSFI E-23 requirements.
    """
    name = "audit_copilot"
    description = "Assess OSFI E-23 compliance gaps for a model"

    @staticmethod
    async def call(model_id: str, documentation_summary: str) -> Dict[str, Any]:
        logger.info(f"[Audit Copilot] Assessing compliance for {model_id}")

        # In production: POST to audit copilot API
        gaps = []
        if "fairness" not in documentation_summary.lower():
            gaps.append("Missing: Fairness testing documentation (OSFI E-23 §6.2)")
        if "monitoring" not in documentation_summary.lower():
            gaps.append("Missing: Ongoing monitoring plan (OSFI E-23 §5.1)")
        if "validation" not in documentation_summary.lower():
            gaps.append("Missing: Independent validation evidence (OSFI E-23 §4.3)")

        return {
            "tool": "audit_copilot",
            "model_id": model_id,
            "compliance_score": max(0, 100 - len(gaps) * 15),
            "compliance_gaps": gaps,
            "sections_assessed": 8,
            "sections_compliant": 8 - len(gaps),
            "audit_trail_generated": True,
            "regulatory_citations_present": len(gaps) == 0,
        }


class ModelRiskDashboardTool:
    """
    MCP-style tool connecting to Model Risk Dashboard.
    Live: model-risk-dashboard.vercel.app / model-risk-dashboard-production.up.railway.app

    Retrieves PSI drift metrics, AUC tracking, demographic parity,
    and OSFI E-23 compliance scoring. Pure Python FastAPI, no API keys.
    """
    name = "model_risk_dashboard"
    description = "Retrieve model risk metrics including PSI drift and fairness scores"

    @staticmethod
    async def call(model_id: str, metrics_payload: Dict) -> Dict[str, Any]:
        logger.info(f"[Model Risk Dashboard] Fetching risk metrics for {model_id}")

        # In production: GET from model-risk-dashboard-production.up.railway.app/metrics/{model_id}
        auc = metrics_payload.get("auc", 0.0)
        psi = metrics_payload.get("psi", 0.0)
        air = metrics_payload.get("air", 0.0)
        tpr_gap = metrics_payload.get("tpr_gap", 0.0)

        # OSFI E-23 compliance score calculation
        compliance_score = 100
        if air < 0.80: compliance_score -= 25
        if psi > 0.20: compliance_score -= 25
        if auc < 0.70: compliance_score -= 25
        if tpr_gap > 0.10: compliance_score -= 25

        return {
            "tool": "model_risk_dashboard",
            "model_id": model_id,
            "performance": {"auc": auc, "ks_statistic": metrics_payload.get("ks", 0.0)},
            "drift": {"psi": psi, "csi": metrics_payload.get("csi", 0.0)},
            "fairness": {
                "air": air,
                "demographic_parity": metrics_payload.get("demographic_parity", 0.0),
                "equal_opportunity": metrics_payload.get("equal_opportunity", 0.0),
                "tpr_gap": tpr_gap,
            },
            "osfi_e23_compliance_score": compliance_score,
            "risk_tier": "HIGH" if compliance_score < 50 else "MEDIUM" if compliance_score < 75 else "LOW",
        }


class GenAIReliabilityTool:
    """
    MCP-style tool connecting to GenAI Reliability Framework.
    Live: genai-reliability-framework.vercel.app

    Evaluates hallucination risk, grounding quality, and
    citation coverage for generative AI components.
    """
    name = "genai_reliability"
    description = "Evaluate GenAI component reliability and hallucination risk"

    @staticmethod
    async def call(model_id: str, sample_outputs: List[str] = None) -> Dict[str, Any]:
        logger.info(f"[GenAI Reliability] Evaluating reliability for {model_id}")

        # In production: POST to genai-reliability-framework API
        # Simulating evaluation based on model characteristics
        hallucination_risk = 0.05  # Well below 0.10 threshold for this demo
        grounding_score = 0.92
        citation_coverage = 0.88

        return {
            "tool": "genai_reliability",
            "model_id": model_id,
            "hallucination_risk": hallucination_risk,
            "grounding_score": grounding_score,
            "citation_coverage": citation_coverage,
            "reliability_grade": "A" if hallucination_risk < 0.05 else "B" if hallucination_risk < 0.10 else "F",
            "osfi_e23_section": "Section 7.1: Model Reliability",
            "recommendation": "Meets reliability standards for production deployment",
        }


class CanFraudBenchTool:
    """
    MCP-style tool connecting to CanFraudBench.
    Live: github.com/CrillyPienaah/canfraudbench
         huggingface.co/datasets/CrillyPienaah/CanFraudBench

    The key insight from CanFraudBench:
    A fraud model achieving AUC 0.969 can FAIL governance review
    due to fairness violations (AIR 0.59).

    This is the core demonstration that accuracy alone is insufficient
    for OSFI E-23 compliance in Canadian regulated institutions.
    """
    name = "canfraudbench"
    description = "Benchmark model against CanFraudBench Canadian fraud detection standards"

    @staticmethod
    async def call(model_id: str, air: float, auc: float) -> Dict[str, Any]:
        logger.info(f"[CanFraudBench] Benchmarking {model_id} — AUC: {auc}, AIR: {air}")

        # The canonical CanFraudBench finding
        canfraudbench_baseline_auc = 0.969
        canfraudbench_baseline_air = 0.59  # FAILS governance despite excellent AUC

        governance_pass = air >= 0.80
        performance_competitive = auc >= canfraudbench_baseline_auc * 0.95

        return {
            "tool": "canfraudbench",
            "model_id": model_id,
            "benchmark_comparison": {
                "submitted_auc": auc,
                "submitted_air": air,
                "canfraudbench_baseline_auc": canfraudbench_baseline_auc,
                "canfraudbench_baseline_air": canfraudbench_baseline_air,
            },
            "key_insight": (
                "CanFraudBench demonstrates that AUC 0.969 models can FAIL "
                "governance review due to fairness violations (AIR 0.59 < 0.80). "
                "Accuracy alone is insufficient for OSFI E-23 compliance."
            ),
            "governance_eligible": governance_pass,
            "performance_competitive": performance_competitive,
            "recommendation": (
                "ELIGIBLE for production" if governance_pass
                else "INELIGIBLE — fairness remediation required before production"
            ),
            "dataset": "huggingface.co/datasets/CrillyPienaah/CanFraudBench",
        }


# ══════════════════════════════════════════════════════════════════════
# SECTION 3: ADK SUPERVISOR AGENT
# The orchestration layer. Coordinates all five tools, collects results,
# applies deterministic guardrails, generates executive report.
# ══════════════════════════════════════════════════════════════════════

class GovernanceSupervisor:
    """
    ADK-style Supervisor Agent for Enterprise AI Governance.

    This is the Control Tower. It coordinates five specialized agents,
    applies deterministic guardrails, and produces an executive report
    that a Chief Risk Officer or OSFI examiner can act on.

    Architecture mirrors ADK SequentialAgent pattern:
    Tool calls → Metrics aggregation → Guardrail evaluation → Report
    """

    def __init__(self):
        self.osfi_navigator = OSFINavigatorTool()
        self.audit_copilot = AuditCopilotTool()
        self.model_risk = ModelRiskDashboardTool()
        self.genai_reliability = GenAIReliabilityTool()
        self.canfraudbench = CanFraudBenchTool()

    async def evaluate(
        self,
        model_id: str,
        model_name: str,
        model_type: str,
        use_case: str,
        documentation_summary: str,
        raw_metrics: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Full governance evaluation pipeline.

        Step 1: Retrieve regulatory requirements (OSFI Navigator)
        Step 2: Assess compliance gaps (Audit Copilot)
        Step 3: Fetch risk metrics (Model Risk Dashboard)
        Step 4: Evaluate reliability (GenAI Reliability Framework)
        Step 5: Benchmark performance (CanFraudBench)
        Step 6: Apply deterministic guardrails
        Step 7: Generate executive report
        """
        logger.info(f"[Governance Supervisor] Starting evaluation: {model_id}")
        evaluation_start = datetime.utcnow()

        # ── Step 1: Regulatory Intelligence ─────────────────────────
        regulatory = await self.osfi_navigator.call(model_type, use_case)
        logger.info(f"[Step 1/5] Regulatory requirements retrieved")

        # ── Step 2: Compliance Assessment ───────────────────────────
        compliance = await self.audit_copilot.call(model_id, documentation_summary)
        logger.info(f"[Step 2/5] Compliance gaps assessed: score {compliance['compliance_score']}")

        # ── Step 3: Model Risk Metrics ───────────────────────────────
        risk = await self.model_risk.call(model_id, raw_metrics)
        logger.info(f"[Step 3/5] Risk metrics fetched: tier {risk['risk_tier']}")

        # ── Step 4: Reliability Evaluation ──────────────────────────
        reliability = await self.genai_reliability.call(model_id)
        logger.info(f"[Step 4/5] Reliability evaluated: grade {reliability['reliability_grade']}")

        # ── Step 5: Benchmark Comparison ────────────────────────────
        benchmark = await self.canfraudbench.call(
            model_id,
            air=raw_metrics.get("air", 0.0),
            auc=raw_metrics.get("auc", 0.0),
        )
        logger.info(f"[Step 5/5] Benchmark complete: governance eligible = {benchmark['governance_eligible']}")

        # ── Step 6: Build Metrics Object and Apply Guardrails ────────
        metrics = GovernanceMetrics(
            model_id=model_id,
            model_name=model_name,
            auc=raw_metrics.get("auc", 0.0),
            ks_statistic=raw_metrics.get("ks", 0.0),
            ece=raw_metrics.get("ece", 0.0),
            air=raw_metrics.get("air", 0.0),
            demographic_parity=raw_metrics.get("demographic_parity", 0.0),
            equal_opportunity=raw_metrics.get("equal_opportunity", 0.0),
            tpr_gap=raw_metrics.get("tpr_gap", 0.0),
            psi=raw_metrics.get("psi", 0.0),
            csi=raw_metrics.get("csi", 0.0),
            hallucination_risk=reliability["hallucination_risk"],
            grounding_score=reliability["grounding_score"],
            citation_coverage=reliability["citation_coverage"],
            regulatory_citations_present=compliance["regulatory_citations_present"],
            audit_trail_generated=compliance["audit_trail_generated"],
            osfi_e23_sections_covered=regulatory["applicable_sections"],
        )

        guardrail_result = evaluate_guardrails(metrics)
        logger.info(f"[Guardrails] Status: {guardrail_result['status']}")

        # ── Step 7: Executive Report ─────────────────────────────────
        evaluation_end = datetime.utcnow()
        duration_ms = (evaluation_end - evaluation_start).total_seconds() * 1000

        report = self._generate_executive_report(
            model_id=model_id,
            model_name=model_name,
            regulatory=regulatory,
            compliance=compliance,
            risk=risk,
            reliability=reliability,
            benchmark=benchmark,
            guardrails=guardrail_result,
            duration_ms=duration_ms,
        )

        return report

    def _generate_executive_report(
        self,
        model_id: str,
        model_name: str,
        regulatory: Dict,
        compliance: Dict,
        risk: Dict,
        reliability: Dict,
        benchmark: Dict,
        guardrails: Dict,
        duration_ms: float,
    ) -> Dict[str, Any]:
        """
        Generates a structured executive governance report.
        Designed for Chief Risk Officers and OSFI examiners.
        """
        status_emoji = {
            "APPROVED": "✅",
            "CONDITIONAL": "⚠️",
            "BLOCKED": "🚫",
        }.get(guardrails["status"], "❓")

        return {
            "report_type": "Enterprise AI Governance Assessment",
            "generated_by": "AI Governance Control Tower v1.0",
            "generated_at": guardrails["timestamp"],
            "evaluation_duration_ms": round(duration_ms, 2),

            # Executive Summary
            "executive_summary": {
                "model_id": model_id,
                "model_name": model_name,
                "regulatory_framework": "OSFI Guideline E-23",
                "governance_status": f"{status_emoji} {guardrails['status']}",
                "recommendation": guardrails["recommendation"],
                "compliance_score": compliance["compliance_score"],
                "risk_tier": risk["risk_tier"],
                "reliability_grade": reliability["reliability_grade"],
            },

            # Detailed Findings by Agent
            "agent_findings": {
                "regulatory_intelligence": {
                    "agent": "OSFI Navigator",
                    "live_system": "osfi-navigator-production.up.railway.app",
                    "sections_applicable": len(regulatory["applicable_sections"]),
                    "key_requirements": regulatory["key_requirements"][:3],
                },
                "compliance_assessment": {
                    "agent": "OSFI Audit Copilot",
                    "live_system": "osfi-audit-copilot-production-f87b.up.railway.app",
                    "compliance_score": compliance["compliance_score"],
                    "gaps_found": len(compliance["compliance_gaps"]),
                    "gaps": compliance["compliance_gaps"],
                },
                "model_risk": {
                    "agent": "Model Risk Dashboard",
                    "live_system": "model-risk-dashboard.vercel.app",
                    "risk_tier": risk["risk_tier"],
                    "osfi_compliance_score": risk["osfi_e23_compliance_score"],
                    "key_metrics": {
                        "auc": risk["performance"]["auc"],
                        "psi": risk["drift"]["psi"],
                        "air": risk["fairness"]["air"],
                    },
                },
                "reliability_evaluation": {
                    "agent": "GenAI Reliability Framework",
                    "live_system": "genai-reliability-framework.vercel.app",
                    "hallucination_risk": reliability["hallucination_risk"],
                    "grounding_score": reliability["grounding_score"],
                    "reliability_grade": reliability["reliability_grade"],
                },
                "benchmark_comparison": {
                    "agent": "CanFraudBench",
                    "live_system": "github.com/CrillyPienaah/canfraudbench",
                    "governance_eligible": benchmark["governance_eligible"],
                    "key_insight": benchmark["key_insight"],
                    "recommendation": benchmark["recommendation"],
                },
            },

            # Guardrail Results
            "guardrail_evaluation": {
                "rules_evaluated": guardrails["summary"]["total_rules_evaluated"],
                "passed": guardrails["summary"]["passed"],
                "warnings": guardrails["summary"]["warnings"],
                "failures": guardrails["summary"]["failures"],
                "critical_failures": guardrails["summary"]["critical_failures"],
                "failures_detail": guardrails["failures"],
                "warnings_detail": guardrails["warnings"],
                "passed_rules": guardrails["passed_rules"],
            },

            # Audit Trail
            "audit_trail": {
                "agents_called": [
                    "OSFINavigatorTool",
                    "AuditCopilotTool",
                    "ModelRiskDashboardTool",
                    "GenAIReliabilityTool",
                    "CanFraudBenchTool",
                ],
                "guardrails_applied": True,
                "deterministic_rules": True,
                "llm_override_possible": False,
                "osfi_e23_sections_covered": regulatory["applicable_sections"],
                "audit_required": guardrails["audit_required"],
            },
        }


# ══════════════════════════════════════════════════════════════════════
# SECTION 4: DEMO SCENARIOS
# Two scenarios that tell the governance story clearly:
# Scenario A — Model that PASSES (well-governed model)
# Scenario B — Model that FAILS (AUC 0.969 but AIR 0.59 = BLOCKED)
#              This is the CanFraudBench finding.
# ══════════════════════════════════════════════════════════════════════

DEMO_SCENARIOS = {
    "scenario_a_pass": {
        "model_id": "credit_model_v3",
        "model_name": "TD Credit Risk Scoring Model v3",
        "model_type": "credit_risk",
        "use_case": "retail_credit_adjudication",
        "documentation_summary": (
            "This model uses XGBoost for credit risk scoring with fairness testing, "
            "independent validation, and ongoing monitoring. All OSFI E-23 sections "
            "have been addressed including fairness, validation, and monitoring requirements."
        ),
        "raw_metrics": {
            "auc": 0.847,
            "ks": 0.62,
            "ece": 0.018,
            "air": 0.91,          # ✅ Above 0.80 threshold
            "demographic_parity": 0.94,
            "equal_opportunity": 0.89,
            "tpr_gap": 0.06,      # ✅ Below 0.10 threshold
            "psi": 0.08,          # ✅ Below 0.10 warning threshold
            "csi": 0.05,
        },
    },

    "scenario_b_fail": {
        "model_id": "fraud_model_v1",
        "model_name": "CanFraudBench Reference Model — High AUC, Low Fairness",
        "model_type": "fraud_detection",
        "use_case": "transaction_fraud_detection",
        "documentation_summary": (
            "High-performance fraud detection model achieving AUC 0.969. "
            "Standard binary classifier trained on transaction data."
        ),
        "raw_metrics": {
            "auc": 0.969,         # ✅ Excellent performance
            "ks": 0.90,
            "ece": 0.001,
            "air": 0.59,          # 🚫 FAILS — below 0.80 threshold
            "demographic_parity": 0.71,
            "equal_opportunity": 0.68,
            "tpr_gap": 0.18,      # 🚫 FAILS — above 0.10 threshold
            "psi": 0.25,          # 🚫 FAILS — above 0.20 threshold
            "csi": 0.18,
        },
    },
}


async def run_demo():
    """
    Runs both demo scenarios to demonstrate the Control Tower.

    Scenario A: Well-governed model → APPROVED
    Scenario B: CanFraudBench model (AUC 0.969, AIR 0.59) → BLOCKED

    This is the core story:
    Accuracy alone is insufficient for OSFI E-23 compliance.
    """
    supervisor = GovernanceSupervisor()

    print("\n" + "═" * 70)
    print("  ENTERPRISE AI GOVERNANCE CONTROL TOWER")
    print("  Powered by Google ADK | OSFI E-23 Compliance")
    print("  Christopher Crilly Pienaah | Kaggle Capstone 2026")
    print("═" * 70)

    for scenario_key, scenario in DEMO_SCENARIOS.items():
        print(f"\n{'─' * 70}")
        print(f"  SCENARIO: {scenario['model_name']}")
        print(f"{'─' * 70}")

        report = await supervisor.evaluate(**scenario)

        # Print executive summary
        summary = report["executive_summary"]
        print(f"\n  GOVERNANCE STATUS: {summary['governance_status']}")
        print(f"  Compliance Score:  {summary['compliance_score']}/100")
        print(f"  Risk Tier:         {summary['risk_tier']}")
        print(f"  Reliability:       Grade {summary['reliability_grade']}")
        print(f"\n  RECOMMENDATION:")
        print(f"  {summary['recommendation']}")

        # Print guardrail results
        g = report["guardrail_evaluation"]
        print(f"\n  GUARDRAIL RESULTS ({g['rules_evaluated']} rules evaluated):")
        print(f"  ✓ Passed:   {g['passed']}")
        print(f"  ⚠ Warnings: {g['warnings']}")
        print(f"  ✗ Failures: {g['failures']} ({g['critical_failures']} critical)")

        if g["failures_detail"]:
            print(f"\n  FAILURES:")
            for f in g["failures_detail"]:
                print(f"  🚫 [{f['severity']}] {f['rule']}: {f['message']}")
                print(f"     OSFI Ref: {f['osfi_reference']}")
                print(f"     Fix: {f['remediation']}")

        # Print agent findings summary
        print(f"\n  AGENTS CALLED:")
        for agent_key, finding in report["agent_findings"].items():
            print(f"  → {finding['agent']} ({finding['live_system']})")

        print(f"\n  Evaluation completed in {report['evaluation_duration_ms']:.1f}ms")
        print(f"  Audit trail generated: {report['audit_trail']['guardrails_applied']}")
        print(f"  LLM override possible: {report['audit_trail']['llm_override_possible']}")

    print("\n" + "═" * 70)
    print("  CONTROL TOWER DEMO COMPLETE")
    print("  The CanFraudBench finding is clear:")
    print("  AUC 0.969 ≠ OSFI E-23 Compliant")
    print("  Accuracy alone is insufficient for regulated industries.")
    print("═" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(run_demo())
