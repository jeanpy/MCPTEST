
import subprocess
import socket
import urllib.request
import urllib.error
import time

from mcp.server import MCPServer

# Configuration du lab
NGINX_HOST = "192.168.100.30"
NGINX_PORT = 80

# Initialisation du serveur MCP
mcp = MCPServer("Diagnostic-IT")


@mcp.tool()
def ping_serveur() -> dict:
    """Teste la connectivite ICMP du serveur Nginx."""
    try:
        resultat = subprocess.run(
            ["ping", "-c", "2", "-W", "2", NGINX_HOST],
            capture_output=True,
            text=True,
            timeout=7
        )

        return {
            "outil": "ping_serveur",
            "cible": NGINX_HOST,
            "joignable": resultat.returncode == 0,
            "details": resultat.stdout[-1500:]
        }
    except Exception as e:
        return {"erreur": str(e)}


@mcp.tool()
def test_port(port: int = 80) -> dict:
    """Teste la connexion TCP au port 80 de Nginx."""
    if port != NGINX_PORT:
        return {"erreur": "Seul le port 80 est autorise"}

    debut = time.monotonic()

    try:
        with socket.create_connection(
            (NGINX_HOST, port), timeout=3
        ):
            latence = round(
                (time.monotonic() - debut) * 1000, 2
            )
            return {
                "outil": "test_port",
                "cible": NGINX_HOST,
                "port": port,
                "accessible": True,
                "latence_ms": latence
            }
    except OSError as e:
        return {
            "outil": "test_port",
            "cible": NGINX_HOST,
            "port": port,
            "accessible": False,
            "erreur": str(e)
        }


@mcp.tool()
def test_http() -> dict:
    """Teste le service HTTP du serveur Nginx."""
    url = f"http://{NGINX_HOST}/"

    try:
        with urllib.request.urlopen(
            url, timeout=5
        ) as reponse:
            contenu = reponse.read(1000)

            return {
                "outil": "test_http",
                "url": url,
                "code_http": reponse.status,
                "fonctionnel": 200 <= reponse.status < 400,
                "contenu": contenu.decode(
                    "utf-8", errors="replace"
                )
            }

    except urllib.error.HTTPError as e:
        return {
            "outil": "test_http",
            "url": url,
            "code_http": e.code,
            "fonctionnel": False
        }

    except Exception as e:
        return {
            "outil": "test_http",
            "url": url,
            "fonctionnel": False,
            "erreur": str(e)
        }


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000
    )
