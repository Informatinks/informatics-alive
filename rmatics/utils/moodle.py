def get_contest_str_id(id):
    res = str(id)
    while len(res) < 6:
        res = "0" + res
    return res
