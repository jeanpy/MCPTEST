
import asyncio
import json

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

# Adresse du serveur MCP
MCP_URL = "http://172.16.0.13:8000/mcp"


async def main():

    print("Connexion au serveur MCP...")

    async with streamable_http_client(MCP_URL) as (
        read_stream, write_stream, _
    ):

        async with ClientSession(
            read_stream, write_stream
        ) as session:

            # Initialisation du protocole
            await session.initialize()
            print("Connexion MCP etablie !")

            # Decouverte des outils
            outils = await session.list_tools()

            print("\n=== OUTILS DISPONIBLES ===")

            for outil in outils.tools:
                print(f"\nNom : {outil.name}")
                print(f"Description : {outil.description}")
                print(json.dumps(
                    outil.inputSchema,
                    indent=2,
                    ensure_ascii=False
                ))

            # Execution de l'outil ping
            print("\n=== TEST PING ===")

            resultat = await session.call_tool(
                "ping_serveur",
                arguments={}
            )

            for contenu in resultat.content:
                if contenu.type == "text":
                    print(contenu.text)

            # Execution de l'outil TCP
            print("\n=== TEST PORT 80 ===")

            resultat = await session.call_tool(
                "test_port",
                arguments={"port": 80}
            )

            for contenu in resultat.content:
                if contenu.type == "text":
                    print(contenu.text)

            # Execution de l'outil HTTP
            print("\n=== TEST HTTP ===")

            resultat = await session.call_tool(
                "test_http",
                arguments={}
            )

            for contenu in resultat.content:
                if contenu.type == "text":
                    print(contenu.text)


if __name__ == "__main__":
    asyncio.run(main())
