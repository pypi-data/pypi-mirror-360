"""Manual chaining (i.e. outside of lattices) of Quarks for RAG ingest"""
import logging
import os
import pprint
import datetime
from typing import Union
from urllib.parse import urlparse

import dotenv
import uuid_utils as uuid  # Replace standard uuid with uuid_utils for UUID7
from halo import Halo

import quarkupy as q
import quarkupy.lib.runner as qr

# Configs
dotenv.load_dotenv()

API_KEY = os.environ.get("QUARK_API_KEY")
API_END_POINT = "http://local.quarkdev.co:8080/api/quark"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_ACCESS_KEY_SECRET = os.environ.get("AWS_ACCESS_KEY_SECRET")
AWS_ENDPOINT = os.environ.get("AWS_ENDPOINT")
S3_SOURCE_URL = os.environ.get("S3_SOURCE_URL")
VECTOR_DB_TABLE = os.environ.get("VECTOR_DB_TABLE")

if API_KEY is None or API_KEY == "":
    raise ValueError("QUARK_API_KEY environment variable not set")
if OPENAI_API_KEY is None or API_KEY == "":
    raise ValueError("OPENAI_API_KEY environment variable not set")
if AWS_ACCESS_KEY_ID is None or API_KEY == "":
    raise ValueError("AWS_ACCESS_KEY_ID environment variable not set")
if AWS_ACCESS_KEY_SECRET is None or API_KEY == "":
    raise ValueError("AWS_ACCESS_KEY_SECRET environment variable not set")
if AWS_ENDPOINT is None or API_KEY == "":
    raise ValueError("AWS_ENDPOINT environment variable not set")
if S3_SOURCE_URL is None or API_KEY == "":
    raise ValueError("S3_SOURCE_URL environment variable not set")
if VECTOR_DB_TABLE is None or API_KEY == "":
    raise ValueError("VECTOR_DB_TABLE environment variable not set")
if not S3_SOURCE_URL.startswith("s3://") or API_KEY == "":
    raise ValueError("S3_SOURCE_URL must start with s3://")

PRINT_DATASETS = False
PRINT_QUARK_METRICS = True
PRINT_QUARK_HISTORY = False
SPINNER = "dots"

host_url = urlparse(API_END_POINT)
url_root = f"{host_url.scheme}://{host_url.netloc}"


# Mock lattice id for grouping Quarks
lattice_id = uuid.uuid7().__str__()
lattice_identifier = "lattice:rag_demo_ingest"

lattice_history = qr.FlowHistoryItem(
    flow_history_id=lattice_id.__str__(),
    registry_qrn=lattice_identifier,
    created_at=datetime.datetime.now(datetime.timezone.utc),
    updated_at=datetime.datetime.now(datetime.timezone.utc),
    nodes=[],
    edges=[],
    input=None,
    output=None,
    metrics=None,
    status="New",
    identity_id="019738eb-eb84-77d1-b0be-1514c0a9ed6a",
)


async def util_save_lattice_history():
    """
    Saves the Quark history (status) on the Quark services via a REST call. This call is an "upsert" call, meaning
    if a history item with the same `quark_id` exists, it will be updated with the new status. If not, a new history
    item will be created.

    :raises Exception: If there is an error during the API operation.
    """
    api = q.AsyncClient(base_url=API_END_POINT)
    await api.history.flow.update(**lattice_history.model_dump())
    await api.close()


printer = pprint.PrettyPrinter(indent=2)


async def run_quark(q) -> Union[uuid.UUID, None]:
    """Common control flow for running quarks"""
    try:
        await q.start()
        await q.execute()
        print(f"💠 Quark ID: {q.quark_id} - more: {url_root}/q/history/quark/{q.quark_id}")

        # Runs are asynchronous, so we need to poll until the run is complete
        done = await q.poll_until_complete()

        lattice_history.nodes.append(q.history.quark_history_id)

        if PRINT_QUARK_HISTORY:
            printer.pprint(done.model_dump())

        if PRINT_QUARK_METRICS:
            printer.pprint(done.state)

        try:
            print(
                f"💠 Got dataset with ID: {done.output['dataset_uuid']} - preview: {url_root}/q/data-manager/quark-outputs/{done.output['dataset_uuid']}"
            )
            if PRINT_DATASETS:
                t = await q.read_output_dataset()
                if t is not None:
                    printer.pprint(t.to_pandas())
                else:
                    print("No dataset produced")

            return done.output["dataset_uuid"]
        except KeyError:
            return None

    except Exception as e:
        lattice_history.status = "Failed"
        await util_save_lattice_history()

        printer.pprint(e)
        raise e


async def extract_text(dataset_uuid: uuid.UUID) -> uuid.UUID:
    with Halo(text="💠 Extracting text from files...\n", spinner=SPINNER):
        q_input = qr.DocExtractQuarkInput(
            lattice_id=lattice_id.__str__(),
            ipc_dataset_id=dataset_uuid.__str__(),
            opt_generate_page_images=False,
            opt_generate_picture_images=True,
            opt_do_ocr=True,
            opt_do_table_structure=True
        )

        q = qr.DocExtractQuark(
            lattice_id=lattice_id, quark_input=q_input, QUARK_API_KEY=API_KEY, BASE_URL=API_END_POINT
        )

        return await run_quark(q)

async def main():
    print(q.lib.__banner__)
    print(f"💠 Running lattice ID: {lattice_id} ({API_END_POINT}/history/lattice/{lattice_id})")

    lattice_history.status = "Running"
    await util_save_lattice_history()

    try:

        await extract_text("01976c3d-3660-7253-9a97-0e9668fb8bae")

        lattice_history.status = "Completed"
        await util_save_lattice_history()

        print("Done! 🎉")
    except KeyboardInterrupt:
        lattice_history.status = "Failed"
        await util_save_lattice_history()
        print("Interrupted")
    except Exception as e:
        lattice_history.status = "Failed"
        await util_save_lattice_history()
        raise e


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
