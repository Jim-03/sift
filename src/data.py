import json


def get_data(detail: str):
    """Retrieve content defined in data.json

    Args:
        detail (str): The name of the key to extract

    Returns:
        dict[str, object]: The value of the specified key
    """
    with open("data.json", "r") as f:
        data = json.load(f)

        return data[detail]
