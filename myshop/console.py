import argparse
from .gui import main as gui
from .serveur import wsgi as server

def main():
    parser = argparse.ArgumentParser(description="Programme facilitant la gestion du stock d'une boutique")
    parser.add_argument(
        "instance",
        help="L'insatance que vous voulez lancer. Soit le serveur ou le clien",
        choices=['client','serveur'],
    )
    parser.add_argument(
        "--host",
        default='localhost',
        help="Specifier l'addresse du serveur (uniquement si vous lancez le serveur )",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Specifier le port sur laquel le serveur sera lancer (uniquement si vous lancez le serveur )",
    )
    parser.add_argument(
        "--url",
        help="Specifier l'url vers le serveur (uniquement si vous lancez le client )",
    )

    args = parser.parse_args()
    if args.instance == 'client':
        gui.run(args)
    elif args.instance == 'serveur':
        server.run(args)
    else:
        parser.error("Le paramete que vous avez donner n'est pas pris en charge")

if __name__ == '__main__':
    main()
