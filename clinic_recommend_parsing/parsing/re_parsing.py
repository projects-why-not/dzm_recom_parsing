import re


def parse_rec_text(txt):
    shorts = re.findall(r"\(([А-Я]+)\)", txt)

    match = re.search(r"для [А-Яа-я ]+", txt)
    aim = " ".join(match.group().split()[1:])

    match = re.search(r"Рекомендуется [А-Яа-я0-9, ]+ проведение", txt)
    if match is not None:
        target = " ".join(match.group().split()[1:])
    else:
        match = re.search(r"Рекомендуется [А-Яа-я0-9, ]+ ", txt)
        target = " ".join(match.group().split()[1:])

    res = [[proc, target, aim] for proc in shorts]

    return res


def parse_rec_confidence(txt):
    conf_level = txt.split("Уровень убедительности рекомендаций ")[1].split()[0]
    return conf_level
