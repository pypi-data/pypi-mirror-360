from .const import CATEGORIES


def validate_data_type_code(data_type: str) -> str:
    codes = data_type.split(".")
    assert len(codes) == 2, ValueError(
        f"❌ {data_type} is not a valid type. "
        f"Should be write with dot separated, eg: 1.1 or 2.1"
    )

    category_code = codes[0]
    type_code = codes[1]
    type_name = None

    for category in CATEGORIES:
        if category["code"] == category_code:
            for _type in category["types"]:
                if _type["code"] == type_code:
                    type_name = _type["name"]

    assert type_name is not None, ValueError(f"❌ {data_type} is not a valid type.")

    return type_name
