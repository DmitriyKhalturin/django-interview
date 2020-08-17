def truncate(data: str, limit: int) -> str:
    return data[:limit] + '..' if len(data) > limit else ''


def trunc_to8char(data: str) -> str:
    limit: int = 8
    return truncate(data, limit)
