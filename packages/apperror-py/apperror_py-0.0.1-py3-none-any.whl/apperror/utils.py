
def check_arg(expected: bool, err_msg: str) -> None:
    if not expected:
        # raise ValueError(f"Illegal argument: {err_msg}")
        raise ValueError(f"{err_msg}")