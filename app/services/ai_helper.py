import os
import json

try:
    from openai import OpenAI

    _api_key = os.environ.get("AI_API_KEY", "")
    _client = (
        OpenAI(
            api_key=_api_key,
            base_url=os.environ.get("AI_BASE_URL", "https://api.groq.com/openai/v1"),
        )
        if _api_key
        else None
    )
except Exception:
    _client = None

MODEL = os.environ.get("AI_MODEL", "openai/gpt-oss-20b")

STATUS_PARSE_PROMPT = """You are a project status parser. Given a free-text project update,
extract structured information. Respond ONLY with valid JSON, no other text, no markdown fences.

Schema:
{{
  "progress_percent": <int 0-100 or null>,
  "blocker_detected": <bool>,
  "blocker_description": <string or null>,
  "suggested_delay_reason": <one of: requirements_not_finalized, resource_unavailable,
      waiting_business_feedback, data_unavailable, development_issue,
      integration_dependency, scope_change, testing_issue, approval_pending, other, null>,
  "risk_signal": <one of: none, low, medium, high>
}}

Update text: {update_text}"""

DASHBOARD_NARRATIVE_PROMPT = """You are a project portfolio assistant for management.
Given this summary data, write a 2-3 sentence narrative highlighting what needs attention
today and why. Be specific and direct, no fluff, no generic filler.

Data: {data}"""


def _fallback_parse_result(error: bool = True) -> dict:
    return {
        "progress_percent": None,
        "blocker_detected": False,
        "blocker_description": None,
        "suggested_delay_reason": None,
        "risk_signal": "none",
        "parse_error": error,
    }


def parse_status_update(update_text: str) -> dict:
    """
    Converts a free-text status update into structured fields using the LLM.
    This NEVER writes to the database directly - callers must persist the
    result as a suggestion for human review (see AIUpdateSuggestion model).
    Returns a safe fallback if the configured AI provider is unavailable, while
    the rule-based project governance features remain usable.
    """
    if _client is None:
        return _fallback_parse_result()

    try:
        response = _client.chat.completions.create(
            model=MODEL,
            max_tokens=500,
            messages=[
                {"role": "user", "content": STATUS_PARSE_PROMPT.format(update_text=update_text)}
            ],
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception:
        return _fallback_parse_result()


def generate_dashboard_narrative(summary_data: dict) -> str:
    if _client is None:
        return "AI summary unavailable (service not configured)."

    try:
        response = _client.chat.completions.create(
            model=MODEL,
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": DASHBOARD_NARRATIVE_PROMPT.format(data=json.dumps(summary_data)),
                }
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "AI summary temporarily unavailable."
