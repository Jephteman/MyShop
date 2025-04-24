import datetime

version = '0.0.1-alpha'


def get_timestamp() -> str:
    """
    Retourne l'horodatage actuel au format 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        str: Horodatage actuel.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")