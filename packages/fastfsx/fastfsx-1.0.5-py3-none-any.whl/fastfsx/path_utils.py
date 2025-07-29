from pathlib import Path


def path_from_dir(relative: Path) -> str:
    parts = []
    for part in relative.parts:
        if part.startswith('(') and part.endswith(')'):
            continue
        elif part.startswith('[') and part.endswith(']'):
            parts.append('{' + part[1:-1] + '}')
        else:
            parts.append(part)
    if len(parts) == 0:
        return ''
    return '/' + '/'.join(parts)
