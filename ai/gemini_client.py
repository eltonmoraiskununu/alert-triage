import json
import re
import time
import logging
from datetime import date
from google import genai
from google.genai.errors import ClientError
from config.settings import GEMINI_API_KEY
from ai.prompts import (
    EXTRACT_SERVICE_PROMPT,
    TRIAGE_SYNTHESIS_PROMPT_APM,
    TRIAGE_SYNTHESIS_PROMPT_SYNTHETIC,
    TRIAGE_SYNTHESIS_PROMPT_SERVICE_LEVEL,
    INVESTIGATION_SYNTHESIS_PROMPT,
)

logger = logging.getLogger(__name__)

_client = genai.Client(api_key=GEMINI_API_KEY)
_MODEL = "gemini-3.1-flash-lite-preview"

_MAX_RETRIES = 3
_DEFAULT_RETRY_DELAY = 30


def _parse_retry_delay(error: ClientError) -> float:
    match = re.search(r"retryDelay.*?(\d+)s", str(error))
    if match:
        return float(match.group(1))
    return _DEFAULT_RETRY_DELAY


def _generate(prompt: str) -> str:
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            response = _client.models.generate_content(model=_MODEL, contents=prompt)
            return response.text.strip()
        except ClientError as e:
            if e.status_code == 429 and attempt < _MAX_RETRIES:
                delay = _parse_retry_delay(e)
                logger.warning(
                    "Gemini rate limited (attempt %d/%d). Retrying in %.0fs…",
                    attempt, _MAX_RETRIES, delay,
                )
                time.sleep(delay)
            else:
                raise


def extract_service_context(alert_text: str) -> dict:
    """Parse raw alert text into structured service context (triage or investigation)."""
    raw = _generate(
        EXTRACT_SERVICE_PROMPT.format(alert_text=alert_text, today=date.today().isoformat())
    )
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def synthesize_triage(service_name: str, severity: str, alert_summary: str, nr_data: dict) -> str:
    """Return a human-readable triage brief based on entity type."""
    entity_type = nr_data.get("entity_type")

    if entity_type == "APM":
        prompt = TRIAGE_SYNTHESIS_PROMPT_APM.format(
            service_name=service_name,
            severity=severity,
            alert_summary=alert_summary,
            burn_rate=f"{nr_data['burn_rate']:.2f}" if nr_data.get("burn_rate") is not None else "N/A",
            error_count=nr_data.get("error_count") if nr_data.get("error_count") is not None else "N/A",
            avg_duration_ms=f"{nr_data['avg_duration_ms']:.0f}" if nr_data.get("avg_duration_ms") is not None else "N/A",
        )
    elif entity_type == "SYNTHETIC":
        locations = ", ".join(nr_data["failing_locations"]) if nr_data.get("failing_locations") else "N/A"
        prompt = TRIAGE_SYNTHESIS_PROMPT_SYNTHETIC.format(
            service_name=service_name,
            severity=severity,
            alert_summary=alert_summary,
            total_checks=nr_data.get("total_checks") if nr_data.get("total_checks") is not None else "N/A",
            failed_checks=nr_data.get("failed_checks") if nr_data.get("failed_checks") is not None else "N/A",
            failure_rate=f"{nr_data['failure_rate']:.1f}" if nr_data.get("failure_rate") is not None else "N/A",
            failing_locations=locations,
        )
    elif entity_type == "SERVICE_LEVEL":
        compliance = nr_data.get("current_compliance")
        prompt = TRIAGE_SYNTHESIS_PROMPT_SERVICE_LEVEL.format(
            service_name=service_name,
            severity=severity,
            alert_summary=alert_summary,
            current_compliance=f"{compliance:.2f}" if compliance is not None else "N/A",
            compliance_category=nr_data.get("compliance_category", "Unknown"),
            slo_target=nr_data.get("slo_target", "N/A"),
            associated_entity=nr_data.get("associated_entity", "N/A"),
        )
    else:
        raise ValueError(f"Unknown entity_type: {entity_type}")

    return _generate(prompt)


def synthesize_investigation(
    service_name: str,
    user_summary: str,
    time_start: str,
    time_end: str,
    investigation_data: dict,
) -> str:
    """Return a root cause analysis based on investigation evidence."""
    prompt = INVESTIGATION_SYNTHESIS_PROMPT.format(
        service_name=service_name,
        entity_type=investigation_data.get("entity_type", "unknown"),
        sli_kind=investigation_data.get("sli_kind", "unknown"),
        time_start=time_start,
        time_end=time_end,
        user_summary=user_summary,
        sli_definition=investigation_data.get("sli_definition", "Not available."),
        sli_replay=investigation_data.get("sli_replay", "Not available."),
        alert_incidents=investigation_data.get("alert_incidents", "No data."),
        cwv_section_title=investigation_data.get("cwv_section_title", "Metric Data"),
        cwv_data=investigation_data.get("cwv_data", "No data."),
        log_correlation=investigation_data.get("log_correlation", "No data."),
        js_errors=investigation_data.get("js_errors", "No data."),
        deployments=investigation_data.get("deployments", "No data."),
    )
    return _generate(prompt)
