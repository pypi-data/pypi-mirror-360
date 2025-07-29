class TriggeredLimitError(Exception):
    """Raised when a triggered usage limit blocks an LLM call."""

    def __init__(self, violation: dict):
        self.violation = violation
        details = (
            f"{violation.get('threshold_type')} threshold of ${violation.get('amount')} "
            f"{violation.get('period', '')} triggered at {violation.get('triggered_at')}"
        )
        super().__init__(f"Usage blocked due to triggered limit: {details}")
