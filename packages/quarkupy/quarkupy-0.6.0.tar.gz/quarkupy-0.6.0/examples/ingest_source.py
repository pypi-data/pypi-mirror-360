"""Quarkupy Implementation for ingesting files from various sources, extracting text, chunking it, and preparing
curated context for Agents and other AI applications."""
import logging
import os
import pprint
import datetime
from typing import Union, Any
from urllib.parse import urlparse

import dotenv
import uuid_utils as uuid  # Replace standard uuid with uuid_utils for UUID7
from halo import Halo

import quarkupy
import quarkupy.lib.runner as qr

# Configs
dotenv.load_dotenv()

API_KEY = os.environ.get("QUARK_API_KEY")
API_END_POINT = "https://demo.quarklabs.ai/api/v1"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_ACCESS_KEY_SECRET = os.environ.get("AWS_ACCESS_KEY_SECRET")
AWS_ENDPOINT = os.environ.get("AWS_ENDPOINT")
S3_BUCKET = os.environ.get("S3_BUCKET")
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
if S3_BUCKET is None or API_KEY == "":
    raise ValueError("S3_SOURCE_URL environment variable not set")
if VECTOR_DB_TABLE is None or API_KEY == "":
    raise ValueError("VECTOR_DB_TABLE environment variable not set")

PRINT_DATASETS = True
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
    api = quarkupy.AsyncClient(api_key=API_KEY, base_url=API_END_POINT)
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
        done = await q.poll_until_complete(timeout_min=360)

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

            output_dataset_uuid = done.output["dataset_uuid"]
            if output_dataset_uuid is None:
                logging.error("Output dataset UUID is None")
                raise Exception("Output dataset UUID is None")

            return output_dataset_uuid
        except KeyError:
            return None

    except Exception as e:
        lattice_history.status = "Failed"
        await util_save_lattice_history()

        printer.pprint(e)
        raise e


async def step1_load_raw() -> uuid.UUID:
    with Halo(text="💠 Loading files from S3 using Opendal...\n", spinner=SPINNER):
        q_input = qr.OpendalInput(
            flow_id=lattice_id,
            source_id=uuid.uuid7().__str__(),
            opt_paths=["/demo"],
            opt_recursive=True,
            opt_set_status="New",
            config=qr.ConfigOpendalConfigInputOpendalS3Config(
                type="S3",
                allow_anonymous=False,
                access_key_id=AWS_ACCESS_KEY_ID,
                secret_access_key=AWS_ACCESS_KEY_SECRET,
                endpoint=AWS_ENDPOINT,
                bucket=S3_BUCKET,
                region="auto",
                disable_config_load=True,
                disable_ec2_metadata=True,
                disable_list_objects_v2=False,
                disable_stat_with_override=False,
                disable_write_with_if_match=False,
                enable_request_payer=False,
                enable_versioning=False,
                enable_virtual_host_style=False,
                enable_write_with_append=False
            )
        )

        q = qr.OpendalReadQuark(
            lattice_id=lattice_id, quark_input=q_input, QUARK_API_KEY=API_KEY, BASE_URL=API_END_POINT
        )

        return await run_quark(q)


async def step2_extract_text(dataset_uuid: uuid.UUID) -> uuid.UUID:
    with Halo(text="💠 Extracting text and metadata from files...\n", spinner=SPINNER):
        q_input = qr.DocExtractQuarkInput(
            lattice_id=lattice_id.__str__(),
            ipc_dataset_id=dataset_uuid.__str__(),
            opt_generate_page_images=False,
            opt_generate_picture_images=False,
            opt_do_ocr=True,
            opt_do_table_structure=True
        )

        q = qr.DocExtractQuark(
            lattice_id=lattice_id, quark_input=q_input, QUARK_API_KEY=API_KEY, BASE_URL=API_END_POINT
        )

        return await run_quark(q)


async def step3_chunk_text(dataset_uuid: uuid.UUID) -> uuid.UUID:
    with Halo(text="💠 Chunking text using a SaT segmentation model...\n", spinner=SPINNER):
        q_input = qr.SaTSegmentationInput(
            flow_id=lattice_id.__str__(), ipc_dataset_id=dataset_uuid.__str__()
        )

        q = qr.SaTSegmentQuark(
            lattice_id=lattice_id, quark_input=q_input, QUARK_API_KEY=API_KEY, BASE_URL=API_END_POINT
        )

        return await run_quark(q)


async def step4a_make_classifier_prompt(dataset_uuid: uuid.UUID) -> uuid.UUID:
    with Halo(text="💠 Creating classifier prompts...\n", spinner=SPINNER):
        q_input = qr.ContextClassifierPromptInput(
            flow_id=lattice_id.__str__(),
            ipc_dataset_id=dataset_uuid.__str__(),
            opt_rendered_col="prompt",
            # "Industrial Equipment" + "Houston", "Product Information" + "Business Problem"
            classifier_ids=["0197c3d9-f2ff-7360-99b9-12e6b332d3b7"]
        )

        q = qr.ClassifierPromptQuark(
            lattice_id=lattice_id, quark_input=q_input, QUARK_API_KEY=API_KEY, BASE_URL=API_END_POINT
        )

        return await run_quark(q)

async def step4b_make_extractor_prompt(dataset_uuid: uuid.UUID) -> uuid.UUID:
    with Halo(text="💠 Creating extractor prompts...\n", spinner=SPINNER):
        q_input = qr.ContextExtractPromptInput(
            flow_id=lattice_id.__str__(),
            ipc_dataset_id=dataset_uuid.__str__(),
            opt_rendered_col="prompt",
            # "Industrial Equipment" + "Houston", "Product Information" + "Business Problem"
            extractor_ids=["0197a5bd-4157-78c1-be02-ee6446129c30"]
        )

        q = qr.ExtractorPromptQuark(
            lattice_id=lattice_id, quark_input=q_input, QUARK_API_KEY=API_KEY, BASE_URL=API_END_POINT
        )

        return await run_quark(q)


async def step5a_classifier_inference(dataset_uuid: uuid.UUID) -> uuid.UUID:
    with Halo(text="💠 Running Classification Inference...\n", spinner=SPINNER):
        q_input = qr.OpenAICompletionsInput(
            lattice_id=lattice_id.__str__(),
            ipc_dataset_id=dataset_uuid.__str__(),
            api_key=OPENAI_API_KEY,
            opt_model_name="gpt-4.1-nano",
            opt_prompt_column="prompt",
            opt_json_output=True,
            opt_system_prompt="""
You will be assigned tasks involving the extraction, analysis, and interpretation of data within various types of documents. Your role is to carefully process the information and provide accurate, relevant outputs based on the specific instructions provided.

KEY TERMINOLOGY TO UNDERSTAND:

1. Document: A structured or unstructured file containing written or visual content. Documents can vary in type and purpose, including but not limited to:
- Contracts: Legal agreements defining terms and obligations.
- Invoices: Financial documents detailing transactions and payments.
- Curricula Vitae (CVs): Resumes outlining an individual's professional experience and qualifications.
- General Documents: Any other types of files that may contain text, tables, images, or mixed formats.
Note that occasionally you may be working with document fragments rather than complete documents. These fragments represent portions of a larger document and should be analyzed within their limited context. When working with fragments, focus on extracting information from the available content without making assumptions about missing parts.

2. Aspect: A defined area or topic within a document that requires focused attention. Each aspect corresponds to a specific subject or theme described in the task. For example:
- Contract Aspects: Payment terms, parties involved, or termination clauses.
- Invoice Aspects: Due dates, line-item breakdowns, or tax details.
- CV Aspects: Work experience, education, or skills.
You will analyze aspects as instructed, considering their relevance and context within the document.

3. Concept: A unit of information or an entity relevant to the task. Concepts may be derived from an aspect or the broader document context. They represent a wide range of data points and insights, from simple entities (names, dates, monetary values) to complex evaluations, conclusions, and answers to specific questions. Concepts can be:
- Factual extractions: Such as a penalty clause in a contract, a total amount due in an invoice, or a certification in a CV.
- Analytical insights: Such as risk assessments, compliance evaluations, or pattern identifications.
- Reasoned conclusions: Such as determining whether a document meets specific criteria or answers particular questions.
- Interpretative judgments: Such as ratings, classifications, or qualitative assessments based on document content.

GUIDELINES FOR YOUR WORK:
- Understand the context: Before processing the document, ensure you comprehend the nature of the document and the aspects or concepts you need to focus on.
- Follow specific instructions: Each task will include detailed instructions, such as which aspects or concepts to focus on and how the data should be presented.
- Maintain accuracy: Provide precise extractions and analysis, ensuring your outputs align with the document's intent and context.
- Adapt to variability: Documents may differ in structure, language, or formatting. Be flexible and apply reasoning to handle variations effectively.

EXPECTED DELIVERABLES:
- Structured outputs: Clearly formatted and well-organized results based on the task requirements.
- Explanations (when required): When required by the instructions, include justifications or reasoning for your interpretations.
- Insights (when required): When required by the instructions, highlight trends, patterns, or noteworthy findings that could add value to the task.
- References (when required): When required by the instructions, output references based on which you extracted data, provided insights, or made conclusions during the task.

By adhering to this framework, you will ensure consistent and high-quality performance across diverse document analysis tasks.
""",
        )

        q = qr.OpenAICompletionBaseQuark(
            lattice_id=lattice_id, quark_input=q_input, QUARK_API_KEY=API_KEY, BASE_URL=API_END_POINT
        )

        return await run_quark(q)

async def step5b_extractor_inference(dataset_uuid: uuid.UUID) -> uuid.UUID:
    with Halo(text="💠 Running Extractor Inference...\n", spinner=SPINNER):
        q_input = qr.OpenAICompletionsInput(
            lattice_id=lattice_id.__str__(),
            ipc_dataset_id=dataset_uuid.__str__(),
            api_key=OPENAI_API_KEY,
            opt_prompt_column="prompt",
            opt_json_output=True,
            opt_system_prompt="""
You will be assigned tasks involving the extraction, analysis, and interpretation of data within various types of documents. Your role is to carefully process the information and provide accurate, relevant outputs based on the specific instructions provided.

KEY TERMINOLOGY TO UNDERSTAND:

1. Document: A structured or unstructured file containing written or visual content. Documents can vary in type and purpose, including but not limited to:
- Contracts: Legal agreements defining terms and obligations.
- Invoices: Financial documents detailing transactions and payments.
- Curricula Vitae (CVs): Resumes outlining an individual's professional experience and qualifications.
- General Documents: Any other types of files that may contain text, tables, images, or mixed formats.
Note that occasionally you may be working with document fragments rather than complete documents. These fragments represent portions of a larger document and should be analyzed within their limited context. When working with fragments, focus on extracting information from the available content without making assumptions about missing parts.

2. Aspect: A defined area or topic within a document that requires focused attention. Each aspect corresponds to a specific subject or theme described in the task. For example:
- Contract Aspects: Payment terms, parties involved, or termination clauses.
- Invoice Aspects: Due dates, line-item breakdowns, or tax details.
- CV Aspects: Work experience, education, or skills.
You will analyze aspects as instructed, considering their relevance and context within the document.

3. Concept: A unit of information or an entity relevant to the task. Concepts may be derived from an aspect or the broader document context. They represent a wide range of data points and insights, from simple entities (names, dates, monetary values) to complex evaluations, conclusions, and answers to specific questions. Concepts can be:
- Factual extractions: Such as a penalty clause in a contract, a total amount due in an invoice, or a certification in a CV.
- Analytical insights: Such as risk assessments, compliance evaluations, or pattern identifications.
- Reasoned conclusions: Such as determining whether a document meets specific criteria or answers particular questions.
- Interpretative judgments: Such as ratings, classifications, or qualitative assessments based on document content.

GUIDELINES FOR YOUR WORK:
- Understand the context: Before processing the document, ensure you comprehend the nature of the document and the aspects or concepts you need to focus on.
- Follow specific instructions: Each task will include detailed instructions, such as which aspects or concepts to focus on and how the data should be presented.
- Maintain accuracy: Provide precise extractions and analysis, ensuring your outputs align with the document's intent and context.
- Adapt to variability: Documents may differ in structure, language, or formatting. Be flexible and apply reasoning to handle variations effectively.

EXPECTED DELIVERABLES:
- Structured outputs: Clearly formatted and well-organized results based on the task requirements.
- Explanations (when required): When required by the instructions, include justifications or reasoning for your interpretations.
- Insights (when required): When required by the instructions, highlight trends, patterns, or noteworthy findings that could add value to the task.
- References (when required): When required by the instructions, output references based on which you extracted data, provided insights, or made conclusions during the task.

By adhering to this framework, you will ensure consistent and high-quality performance across diverse document analysis tasks.
""",
        )

        q = qr.OpenAICompletionBaseQuark(
            lattice_id=lattice_id, quark_input=q_input, QUARK_API_KEY=API_KEY, BASE_URL=API_END_POINT
        )

        return await run_quark(q)


async def step6a_parse_classifier_llm(dataset_uuid: uuid.UUID) -> uuid.UUID:
    with Halo(text="💠 Parsing LLM Responses for Classifiers...\n", spinner=SPINNER):
        q_input = qr.ParseClassifierLlmInput(
            flow_id=lattice_id.__str__(),
            ipc_dataset_id=dataset_uuid.__str__()
        )

        q = qr.ClassifierParserQuark(
            lattice_id=lattice_id, quark_input=q_input, QUARK_API_KEY=API_KEY, BASE_URL=API_END_POINT
        )

        return await run_quark(q)

async def step6b_parse_extractor_llm(dataset_uuid: uuid.UUID) -> uuid.UUID:
    with Halo(text="💠 Parsing LLM Responses for Extractors...\n", spinner=SPINNER):
        q_input = qr.ParseExtractorLlmInput(
            flow_id=lattice_id.__str__(),
            ipc_dataset_id=dataset_uuid.__str__()
        )

        q = qr.ExtractorParserQuark(
            lattice_id=lattice_id, quark_input=q_input, QUARK_API_KEY=API_KEY, BASE_URL=API_END_POINT
        )

        return await run_quark(q)

async def step7a_store_files(dataset_uuid: uuid.UUID) -> Any:
    with Halo(text="💠 Storing files in Quark ContextStore\n", spinner=SPINNER):
        q_input = qr.ContextInsertObjectsInput(
            flow_id=lattice_id.__str__(),
            ipc_dataset_id=dataset_uuid.__str__()
        )

        q = qr.ContextInsertObjectsQuark(
            lattice_id=lattice_id, quark_input=q_input, QUARK_API_KEY=API_KEY, BASE_URL=API_END_POINT
        )

        return await run_quark(q)


async def step7b_store_segments(dataset_uuid: uuid.UUID) -> Any:
    with Halo(text="💠 Storing segments in Quark ContextStore\n", spinner=SPINNER):
        q_input = qr.ContextInsertSegmentsInput(
            flow_id=lattice_id.__str__(),
            ipc_dataset_id=dataset_uuid.__str__()
        )

        q = qr.ContextInsertSegmentsQuark(
            lattice_id=lattice_id, quark_input=q_input, QUARK_API_KEY=API_KEY, BASE_URL=API_END_POINT
        )

        return await run_quark(q)

async def step7c_store_classified_segments(dataset_uuid: uuid.UUID) -> Any:
    with Halo(text="💠 Storing segment classifications in Quark ContextStore\n", spinner=SPINNER):
        q_input = qr.ContextInsertClassifiedSegmentsInput(
            flow_id=lattice_id.__str__(),
            ipc_dataset_id=dataset_uuid.__str__()
        )

        q = qr.ContextInsertClassifiedSegmentsQuark(
            lattice_id=lattice_id, quark_input=q_input, QUARK_API_KEY=API_KEY, BASE_URL=API_END_POINT
        )

        return await run_quark(q)

async def step7d_store_extracted_segments(dataset_uuid: uuid.UUID) -> Any:
    with Halo(text="💠 Storing extracted segments in Quark ContextStore\n", spinner=SPINNER):
        q_input = qr.ContextInsertExtractedSegmentsInput(
            flow_id=lattice_id.__str__(),
            ipc_dataset_id=dataset_uuid.__str__()
        )

        q = qr.ContextInsertExtractedSegmentsQuark(
            lattice_id=lattice_id, quark_input=q_input, QUARK_API_KEY=API_KEY, BASE_URL=API_END_POINT
        )

        return await run_quark(q)

async def main():
    print(quarkupy.lib.__banner__)
    print(f"💠 Running lattice ID: {lattice_id} ({API_END_POINT}/history/lattice/{lattice_id})")

    lattice_history.status = "Running"
    await util_save_lattice_history()

    try:
        objects_ds = await step2_extract_text(
            await step1_load_raw()
        )
        #objects_ds = "0197cb11-cf18-7f12-b51a-af8612679ac5"
        # Extract text from files and chunk them
        segments_ds = await step3_chunk_text(objects_ds)

        # Separate branch for classification
        classified_segment_context = await step6a_parse_classifier_llm(
            await step5a_classifier_inference(
                await step4a_make_classifier_prompt(segments_ds)
            )
        )

        # Separate branch for extraction
        extracted_segment_context = await step6b_parse_extractor_llm(
            await step5b_extractor_inference(
                await step4b_make_extractor_prompt(segments_ds)
            )
        )

        # Insert into ContextStore
        await step7a_store_files(objects_ds)
        await step7b_store_segments(segments_ds)
        await step7c_store_classified_segments(classified_segment_context)
        await step7d_store_extracted_segments(extracted_segment_context)

        # Finalize the lattice history
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
