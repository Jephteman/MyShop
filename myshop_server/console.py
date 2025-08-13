
import argparse
from . import wsgi as server

def main():
    parser = argparse.ArgumentParser(description="Programme facilitant la gestion du stock d'une boutique")
 
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
    server.run(args)

if __name__ == '__main__':
    main()
