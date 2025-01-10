def bytes_formatter(size) -> str:
    size = size if type(size) == int else 0
    power = 1024
    n = 0
    labels = ['B', 'KB', 'MB', 'GB', 'TB']

    while size > power:
        size /= power
        n += 1

    if n > 0:
        size = f'{size:.2f}'
    else:
        size = f'{size:.0f}'

    return f'{size}{labels[n]}'