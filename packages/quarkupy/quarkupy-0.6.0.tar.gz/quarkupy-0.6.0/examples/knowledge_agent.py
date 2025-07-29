"""Manual chaining (i.e. outside of lattices) of Quarks for RAG ingest"""

import os
import pprint

import dotenv
from halo import Halo

import quarkupy.lib as q
import quarkupy.lib.agent as qa

# Configs
dotenv.load_dotenv()

API_KEY = os.environ.get("QUARK_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
API_END_POINT = "https://demo.quarklabs.ai/api/quark"

if API_KEY is None or API_KEY == "":
    raise ValueError("QUARK_API_KEY environment variable not set")
if OPENAI_API_KEY is None or OPENAI_API_KEY == "":
    raise ValueError("OPENAI_API_KEY environment variable not set")

SPINNER = "dots"



async def main():
    print(q.__banner__)
    with Halo(text="💠 Getting file list...\n", spinner=SPINNER):
        agent = qa.KnowledgeAgent(
            base_url=API_END_POINT,
            openai_api_key=OPENAI_API_KEY,
        )

        try:
            answer = await agent.ask("How do I get support?")
            pprint.pprint(answer)

        except KeyboardInterrupt:
            print("Interrupted")
        except Exception as e:
            print(f"An error occurred while fetching files: {e}")
            raise e


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())