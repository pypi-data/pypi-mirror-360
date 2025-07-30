def validate_rounds(rounds: int, min: int, max: int) -> None:  # noqa: A002
    if rounds < min or rounds > max:
        msg = f"rounds must be between {min} - {max}"
        raise ValueError(msg)
