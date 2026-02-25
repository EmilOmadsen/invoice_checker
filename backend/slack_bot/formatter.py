from models.schemas import ValidationResult, CheckStatus

# Status emoji mapping
STATUS_EMOJI = {
    "approved": ":white_check_mark:",
    "missing_information": ":warning:",
    "invalid": ":x:",
}

STATUS_TEXT_DA = {
    "approved": "Godkendt",
    "missing_information": "Mangler information",
    "invalid": "Ugyldig",
}


def format_validation_result(
    result: ValidationResult, source_label: str
) -> list[dict]:
    """
    Convert a ValidationResult into Slack Block Kit blocks.

    Args:
        result: The ValidationResult from the AI validator
        source_label: Label for the source (e.g. "PayPal faktura")

    Returns:
        List of Block Kit block dicts
    """
    status_val = result.overall_status.value
    emoji = STATUS_EMOJI.get(status_val, ":question:")
    status_da = STATUS_TEXT_DA.get(status_val, status_val)

    present = [c for c in result.checks if c.status == CheckStatus.PRESENT]
    missing = [c for c in result.checks if c.status == CheckStatus.MISSING]
    unclear = [c for c in result.checks if c.status == CheckStatus.UNCLEAR]
    total = len(present) + len(missing) + len(unclear)

    blocks: list[dict] = []

    # Header
    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": source_label,
            "emoji": True,
        },
    })

    # Status summary
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                f"{emoji} *Status: {status_da}*\n"
                f":clipboard: {len(present)}/{total} tjek bestået"
            ),
        },
    })

    blocks.append({"type": "divider"})

    # Present checks
    if present:
        lines = []
        for c in present:
            line = f":white_check_mark: {c.requirement}"
            if c.found_value:
                line += f" — _{c.found_value}_"
            lines.append(line)
        # Slack has 3000 char limit per section text — truncate if needed
        text = "*Fundet og OK:*\n" + "\n".join(lines)
        if len(text) > 2900:
            text = text[:2900] + "\n..."
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": text},
        })

    # Missing checks
    if missing:
        blocks.append({"type": "divider"})
        lines = []
        for c in missing:
            line = f":x: *{c.requirement}*"
            if c.fix_recommendation:
                line += f"\n     _{c.fix_recommendation}_"
            lines.append(line)
        text = "*Mangler:*\n" + "\n".join(lines)
        if len(text) > 2900:
            text = text[:2900] + "\n..."
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": text},
        })

    # Unclear checks
    if unclear:
        blocks.append({"type": "divider"})
        lines = []
        for c in unclear:
            line = f":warning: *{c.requirement}*"
            if c.found_value:
                line += f" (fundet: _{c.found_value}_)"
            if c.fix_recommendation:
                line += f"\n     _{c.fix_recommendation}_"
            lines.append(line)
        text = "*Uklart:*\n" + "\n".join(lines)
        if len(text) > 2900:
            text = text[:2900] + "\n..."
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": text},
        })

    # Summary footer
    blocks.append({"type": "divider"})
    blocks.append({
        "type": "context",
        "elements": [
            {"type": "mrkdwn", "text": f":memo: {result.summary}"},
        ],
    })

    return blocks
