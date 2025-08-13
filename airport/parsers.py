from rest_framework.exceptions import ValidationError


def parse_int(value: str, field_name: str) -> int:
    try:
        return int(value)
    except ValueError:
        raise ValidationError({
            field_name: f"{field_name} must be an integer"
        })


def parse_int_list(value: str, field_name: str) -> list[int]:
    try:
        return [int(x.strip()) for x in value.split(",")]
    except ValueError:
        raise ValidationError({
            field_name:
                f"{field_name} must be integers separated by comma"
        })


def parse_date(value: str, field_name: str) -> tuple[int, int, int]:
    try:
        year, month, day = map(int, value.split("-"))
        return year, month, day
    except ValueError:
        raise ValidationError({
            field_name: "Invalid datetime format. Use YYYY-MM-DD"
        })
