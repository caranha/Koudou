def cast(value, type):
    if type is str:
        return f"{value}"
    elif type is bool:
        temp = value
        if isinstance(temp, str):
            temp = temp.lower()== "true"
        return bool(temp)
    elif type is int:
        return int(value)
    elif type is float:
        return float(value)
    else:
        tempstring = f"\n[Casting] Unknown typing: {type}\n"
        raise(ValueError(tempstring))