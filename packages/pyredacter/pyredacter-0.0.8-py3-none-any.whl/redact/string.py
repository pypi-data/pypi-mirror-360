def redact_string(item: str, expose_start: int = 2, expose_end: int = 2) -> str:
    too_short = "*****"
    if len(item) <= 4:
        return too_short
    start = f"{item[:expose_start]}"
    end = f"{item[(expose_end * -1) :]}"
    stars = "*" * (len(item) - (expose_start + expose_end))
    return f"{start}{stars}{end}"


if __name__ == "__main__":
    password = "testpassword"
    redacted = redact_string(password, 4, 4)

    if len(password) != len(redacted):
        print("lenghts did not match, probably off-by-one")

    print(f"{password} has been redacted to {redacted}")
