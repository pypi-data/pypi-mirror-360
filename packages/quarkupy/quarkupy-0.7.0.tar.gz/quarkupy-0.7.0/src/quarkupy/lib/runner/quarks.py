from typing import ClassVar

import quarkupy

from . import QuarkHistoryItem, QuarkRemoteDriver, inputs

TIMEOUT = 14440  # 4 hours


class ClassifierPromptQuark(QuarkRemoteDriver):
    """
    Performs classification using a transformer-based model with a prompt-oriented approach.

    This class is a specialization of QuarkRemoteDriver that specifically handles
    transformer-based classification tasks using the context classifier prompt model.
    It manages the input, handles the communication with the remote API, and offers
    functionality for processing and saving the classification results. It acts as
    an intermediary that sends requests to the remote classification model service
    and retrieves its responses.

    Attributes:
        IDENTIFIER (str): A unique identifier for the specific quark model or task.
        quark_input (inputs.ContextClassifierPromptInput): The input data required
            for the context classifier prompt model.

    Methods:
        execute(): Sends the classifier prompt input to the remote transformer model,
            waits for the result, processes the retrieved history, and saves it
            to the appropriate storage.
    """
    IDENTIFIER: ClassVar[str] = "quark:transformer:classifier_prompt"

    quark_input: inputs.ContextClassifierPromptInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)
        res = await api_client.worker.registry.quark.transformer.context_classifier_prompt.run(**self.quark_input,
                                                                                        timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class ClassifierParserQuark(QuarkRemoteDriver):
    """
    Represents a specialized remote driver for invoking the Classifier Parser Quark
    transformer.

    This class extends the functionality of the QuarkRemoteDriver to call specific
    remote services for parsing classifier-related LLM inputs. It interfaces with
    the Quark ecosystem to send parsing requests, handle responses, and manage the
    history of the invoked operations.

    Attributes:
        IDENTIFIER (str): A constant class-level identifier for the Classifier
            Parser Quark transformer.
        quark_input (inputs.ParseClassifierLlmInput): Input data model containing
            parameters to be passed to the Quark API for parsing operations.
    """
    IDENTIFIER: ClassVar[str] = "quark:transformer:Classifier_parser"

    quark_input: inputs.ParseClassifierLlmInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)
        res = await api_client.worker.registry.quark.transformer.parse_classifier_llm.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history

class ContextInsertClassifiedSegmentsQuark(QuarkRemoteDriver):
    """
    Represents the context for inserting classified segments within a Quark system.

    This class extends the QuarkRemoteDriver and facilitates interaction with the backend
    to perform the operation of inserting classified segments into the system. It handles
    asynchronous execution of the operation, tracks the history of the operation, and
    interfaces with the required input and history management components.

    Attributes:
        IDENTIFIER (str): A constant string that uniquely identifies this type of Quark
            operation. It acts as a key identifier within the Quark system.
        quark_input (inputs.ContextInsertClassifiedSegmentsInput): Input parameters required
            for executing the operation. The structure and required fields are specified
            by the `ContextInsertClassifiedSegmentsInput` class.

    Methods:
        execute() -> QuarkHistoryItem:
            Executes the operation asynchronously and returns the result of the operation,
            which contains details about the processed classified segments and associated
            history item.
    """
    IDENTIFIER: ClassVar[str] = "quark:other:context_insert_classified_segments"

    quark_input: inputs.ContextInsertClassifiedSegmentsInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)
        res = await api_client.worker.registry.quark.other.context_insert_classified_segments.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history

class ContextInsertExtractedSegmentsQuark(QuarkRemoteDriver):
    """
    ContextInsertExtractedSegmentsQuark is a specialized QuarkRemoteDriver class.

    This class is responsible for handling the execution of inserting extracted segments
    into the context, specifically using the Quark Remote Driver APIs. It performs
    the operation asynchronously, manages API interaction, maintains operation history,
    and saves history data for further use.

    Attributes:
        IDENTIFIER (str): A unique identifier for the specific Quark operation.
        quark_input (inputs.ContextInsertExtractedSegmentsInput): Input parameters required
            for the execution of the operation.

    Methods:
        execute: Executes the operation of inserting extracted segments asynchronously,
            manages the API interaction, and stores the history of the operation for
            subsequent use.
    """
    IDENTIFIER: ClassVar[str] = "quark:other:context_insert_extracted_segments"

    quark_input: inputs.ContextInsertExtractedSegmentsInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)
        res = await api_client.worker.registry.quark.other.context_insert_extracted_segments.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history

class ContextInsertObjectsQuark(QuarkRemoteDriver):
    """
    Represents a driver for the "context_insert_objects" operation in the Quark system.

    Provides functionality to insert objects into a specific context within the Quark
    framework. This class extends the base QuarkRemoteDriver and provides an asynchronous
    method to securely execute the context insertion operation using the provided input
    parameters. It also handles history saving for the operation performed.

    Attributes:
        IDENTIFIER (ClassVar[str]): Identifier for this specific Quark operation.
        quark_input (inputs.ContextInsertObjectsInput): Input parameters required for
            the "context_insert_objects" operation.

    Methods:
        execute: Performs the context insertion operation asynchronously using the
            provided input and saves the resulting history.

    """
    IDENTIFIER: ClassVar[str] = "quark:other:context_insert_objects"

    quark_input: inputs.ContextInsertObjectsInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)
        res = await api_client.worker.registry.quark.other.context_insert_objects.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history

class ContextInsertSegmentsQuark(QuarkRemoteDriver):
    """
    Represents the quark remote driver responsible for inserting context segments.

    This class is a specialized implementation of the QuarkRemoteDriver that
    handles inserting context segments via the Quark API. It manages the input
    data needed for the operation, communicates with the Quark API asynchronously,
    and stores the resulting history. The class is primarily intended to execute
    the insertion of context segments and save the operation's history within the
    system.

    Attributes:
        IDENTIFIER (ClassVar[str]): A constant identifier for the quark operation
            "context_insert_segments".
        quark_input (inputs.ContextInsertSegmentsInput): Represents the input
            parameters required to execute the context insertion operation via
            the Quark API.
    """
    IDENTIFIER: ClassVar[str] = "quark:other:context_insert_segments"

    quark_input: inputs.ContextInsertSegmentsInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)
        res = await api_client.worker.registry.quark.other.context_insert_segments.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history

class DocExtractQuark(QuarkRemoteDriver):
    """
    Represents a driver for handling document extraction processes in the Quark system.

    This class is a specialized remote driver used for invoking and managing document
    extraction processes. It utilizes an asynchronous HTTP client to communicate with
    specific Quark extractors to perform operations defined in `quark_input`. The
    class is responsible for executing the extraction process, storing the results in
    the Quark history, and maintaining the identification of the quark operation for
    future reference.

    Attributes:
        IDENTIFIER (str): The unique identifier for the Quark document extraction functionality.
        quark_input (inputs.DocExtractQuarkInput): Defines input parameters for the
            document extraction process.

    Methods:
        execute(): Executes the document extraction process asynchronously and records
            the results in the Quark history.

    """
    IDENTIFIER: ClassVar[str] = "quark:extractor:docling_extractor"

    quark_input: inputs.DocExtractQuarkInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)
        res = await api_client.worker.registry.quark.extractor.docling_extractor.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class DocChunkerQuark(QuarkRemoteDriver):
    """
    Represents the DocChunkerQuark class.

    This class is a specialized remote driver for performing transformations using a
    document chunking model. It is designed to handle an input of type DocChunkerQuarkInput
    and process it using an asynchronous client to communicate with a remote API endpoint.
    The class also manages the history of transformations performed and maintains the
    associated quark history ID.

    Attributes:
        IDENTIFIER (str): A constant string identifier for the DocChunkerQuark class.
        quark_input (DocChunkerQuarkInput): The input object required for the quark transformation.

    Methods:
        execute:
            Executes the transformation asynchronously using the provided input and updates the
            object's history and quark identifier.

    """
    IDENTIFIER: ClassVar[str] = "quark:transformer:docling_chunker"

    quark_input: inputs.DocChunkerQuarkInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)
        res = await api_client.worker.registry.quark.transformer.docling_chunker.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class ExtractorPromptQuark(QuarkRemoteDriver):
    """
    Represents a remote driver for processing quark extractor prompts.

    This class extends the functionality of a QuarkRemoteDriver and is used for
    handling extractor prompts in quark transformer systems. It takes input
    data, sends it to a remote quark API, processes the results, and manages the
    resulting history and state.

    Attributes:
        IDENTIFIER (str): A constant string identifier for this class used within
            the quark transformer system.
        quark_input (inputs.ContextExtractPromptInput): Input data required to
            perform the quark extraction process.

    Methods:
        execute: Sends input data to the quark transformer API, processes the
            results, and updates the history state.

    Raises:
        None explicitly.
    """
    IDENTIFIER: ClassVar[str] = "quark:transformer:extractor_prompt"

    quark_input: inputs.ContextExtractPromptInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)
        res = await api_client.worker.registry.quark.transformer.context_extract_prompt.run(**self.quark_input,
                                                                                     timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class ExtractorParserQuark(QuarkRemoteDriver):
    """
    Handles the process of executing a Quark transformer to parse an extractor.

    This class extends QuarkRemoteDriver to provide functionality for executing
    a Quark transformer operation specifically designed to parse extractor inputs.
    It interacts with a remote API to process and manage the related tasks,
    while maintaining a local history of the operations performed.

    Attributes:
        IDENTIFIER (ClassVar[str]): A class-level unique identifier for this transformer.
        quark_input (inputs.ParseExtractorLlmInput): The input data required
            to perform the extractor parsing operation.

    Methods:
        execute: Executes the Quark transformer for parsing extractor inputs
            asynchronously, interacts with the remote API,
            saves the execution history and fetches the result.

    Raises:
        None

    Returns:
        None
    """
    IDENTIFIER: ClassVar[str] = "quark:transformer:extractor_parser"

    quark_input: inputs.ParseExtractorLlmInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)
        res = await api_client.worker.registry.quark.transformer.parse_extractor_llm.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class OpenAICompletionBaseQuark(QuarkRemoteDriver):
    """
    Represents the OpenAI Completion Base Quark driver.

    This class implements the functionality for interacting with the specific
    OpenAI Completion Base Quark. It inherits from the QuarkRemoteDriver and
    handles the process of executing the quark remotely using provided input
    and fetching the resulting quark history item.

    Attributes:
        IDENTIFIER: Class-level constant, identifying this specific driver type
            as "quark:ai:openai_completion_base".
        quark_input: The input object required for running the OpenAI Completion
            Base Quark.

    Methods:
        execute:
            Executes the quark remotely with the given input and manages the
            generated history data.

    Parameters:
        quark_input (inputs.OpenAICompletionsInput): Input data necessary for
        execution of the OpenAI Completion Base Quark.

    Returns:
        QuarkHistoryItem: The resulting history item after successful execution
        of the quark.

    Raises:
        Any exceptions generated during API interaction or input/output handling
        will propagate naturally to the caller.
    """
    IDENTIFIER: ClassVar[str] = "quark:ai:openai_completion_base"

    quark_input: inputs.OpenAICompletionsInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)
        res = await api_client.worker.registry.quark.ai.openai_completion_base.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class OpenAIEmbeddingsQuark(QuarkRemoteDriver):
    """
    Represents a Quark remote driver for OpenAI embeddings.

    This class provides an interface to interact with OpenAI's embeddings
    API through the Quark framework, allowing data processing and retrieval
    via asynchronous operations. The primary functionality is to execute
    requests to OpenAI embeddings, retrieve results, and manage related
    quark history.

    Attributes:
        IDENTIFIER (ClassVar[str]): A unique identifier string for this Quark
            type within the Quark framework.
        quark_input (inputs.OpenAIEmbeddingsInput): The input payload
            containing the parameters required for the OpenAI embeddings API call.
    """
    IDENTIFIER: ClassVar[str] = "quark:ai:openai_embeddings"

    quark_input: inputs.OpenAIEmbeddingsInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)
        res = await api_client.worker.registry.quark.ai.openai_embeddings.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class OpendalReadQuark(QuarkRemoteDriver):
    """
    Represents a driver for interacting with Opendal lists.

    This class enables interaction with a remote Opendal filesystem via the Quark framework. It manages the execution
    of remote operations asynchronously, processes the results, and stores the operation history. It is designed to
    integrate seamlessly with other components of the Quark framework and provides functionality specific to Opendal.

    Attributes:
        IDENTIFIER (str): Identifier for the Opendal list binary process in the Quark framework.
        quark_input (inputs.OpendalInput): Input details required for executing the Opendal-related operation.
    """
    IDENTIFIER: ClassVar[str] = "quark:files:opendal_list_binary"

    quark_input: inputs.OpendalInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)
        res = await api_client.worker.registry.quark.files.opendal.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class S3ReadCSVQuark(QuarkRemoteDriver):
    """
    Represents an S3 Read CSV operation in the Quark framework.

    This class handles the execution of a task to read CSV files
    stored in an S3 bucket via the Quark API. It extends `QuarkRemoteDriver`,
    leveraging its functionalities and features. The class interacts with
    the Quark API asynchronously to execute the operation and manages the
    result by saving it in the history for future reference.

    Attributes:
        IDENTIFIER (ClassVar[str]): A unique string identifier for the
                                    S3 Read CSV Quark.
        quark_input (inputs.S3ReadCSVQuarkInput): The input object containing
                                                  parameters required to
                                                  perform the operation.
    """
    IDENTIFIER: ClassVar[str] = "quark:files:s3_read_csv"

    quark_input: inputs.S3ReadCSVQuarkInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)
        res = await api_client.worker.registry.quark.files.s3_read_csv.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class S3ReadWholeFileQuark(QuarkRemoteDriver):
    """
    Represents a QuarkRemoteDriver that allows reading entire files from S3 in binary format.

    This class is a specialized implementation of the QuarkRemoteDriver designed to facilitate
    reading files stored in AWS S3 buckets as binary data. It uses provided input parameters
    to execute an asynchronous operation, utilizing the Quark API framework to retrieve the
    desired files. The results of the operation are stored as part of the quark history.

    Attributes:
        IDENTIFIER (str): A unique identifier for this Quark driver.
        quark_input (inputs.S3ReadWholeFileQuarkInput): Input parameters required for executing
            a read operation for files stored in S3.

    Methods:
        execute:
            Executes the S3 file read operation in binary mode and saves the result into the
            quark history.
    """
    IDENTIFIER: ClassVar[str] = "quark:files:s3_read_files_binary"

    quark_input: inputs.S3ReadWholeFileQuarkInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)
        res = await api_client.worker.registry.quark.files.s3_read_files_binary.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class SaTSegmentQuark(QuarkRemoteDriver):
    """
    Represents a Quark remote driver implementation for SaT segmentation.

    This class provides an asynchronous implementation of remote execution for
    SaT segmentation using the Quark ONNX transformer API.

    Attributes:
        IDENTIFIER (str): A unique string identifier for the Quark ONNX SaT
            segmentation transformer.
        quark_input (SaTSegmentationInput): Input payload required for the SaT
            segmentation process.

    Methods:
        execute():
            Executes the SaT segmentation process remotely using the Quark ONNX
            transformer and returns the associated history item.
    """
    IDENTIFIER: ClassVar[str] = "quark:transformer:onnx_sat_segmentation"

    quark_input: inputs.SaTSegmentationInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)
        res = await api_client.worker.registry.quark.transformer.onnx_sat_segmentation.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class TextTemplateBaseQuark(QuarkRemoteDriver):
    """
    Handles execution of the base handlebars transformer using QuarkRemoteDriver.

    This class is designed to interface with the Quark platform to run a specific
    transformer operation, defined as 'handlebars_base'. It manages the execution
    of this transformer, interacts with the remote API, and stores the results in
    Quark history. The execution process includes sending input data to the API,
    processing the response, and saving execution metadata. This class inherits
    from QuarkRemoteDriver, utilizing its base configurations and functionalities.

    Attributes:
        IDENTIFIER (ClassVar[str]): A unique identifier for this specific transformer operation.
        quark_input (inputs.TextTemplateInput): Input parameters required for the handlebars base transformer.
    Methods:
        execute: Executes the transformer operation asynchronously, retrieves the result,
            and saves the history of the operation.
    """
    IDENTIFIER: ClassVar[str] = "quark:transformer:handlebars_base"

    quark_input: inputs.TextTemplateInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)
        res = await api_client.worker.registry.quark.transformer.handlebars_base.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class VectorDBIngestQuark(QuarkRemoteDriver):
    """
    Handles the ingestion process for vector databases using LanceDB.

    This class is a remote driver specifically designed to manage the ingestion
    process into vector databases. It extends the QuarkRemoteDriver framework
    and ensures that the appropriate inputs are processed and the required
    results are retrieved and saved in the Quark history.

    Attributes:
        IDENTIFIER (str): A unique identifier for the quark vector LanceDB ingestion process.
        quark_input (inputs.VectorDBIngestInput): Inputs required for the ingestion operation.

    Methods:
        execute(): Executes the ingestion process into the vector database using the provided
            inputs and updates the Quark history.

    """
    IDENTIFIER: ClassVar[str] = "quark:vector:lancedb_ingest"

    quark_input: inputs.VectorDBIngestInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)
        res = await api_client.worker.registry.quark.vector.lancedb_ingest.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


class VectorDBSearchQuark(QuarkRemoteDriver):
    """Represents a driver class for performing vector database searches using LanceDB through Quark.

    This class extends QuarkRemoteDriver and implements functionality to interact
    with a vector database search API provided by Quark. The class is designed to
    execute search requests with the given inputs and manage the history of
    executed searches.

    Attributes:
        IDENTIFIER (str, ClassVar): A unique identifier for the vector database
            search functionality using LanceDB.
        quark_input (inputs.VectorDBSearchInput): Input data required to perform the
            vector database search operation.
    """
    IDENTIFIER: ClassVar[str] = "quark:vector:lancedb_search"

    quark_input: inputs.VectorDBSearchInput

    async def execute(self) -> QuarkHistoryItem:
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)
        res = await api_client.worker.registry.quark.vector.lancedb_search.run(**self.quark_input, timeout=TIMEOUT)
        await api_client.close()

        self._history = res
        self._quark_id = res.quark_history_id
        await self.save_history()

        return self._history


quark_runner_mapping = [
    {
        "identifier": "quark:ai:openai_completion_base",
        "input": inputs.OpenAICompletionsInput,
        "constructor": OpenAICompletionBaseQuark,
    },
    {
        "identifier": "quark:ai:openai_embeddings",
        "input": inputs.OpenAIEmbeddingsInput,
        "constructor": OpenAIEmbeddingsQuark,
    },
    {
        "identifier": "quark:extractor:docling_extractor",
        "input": inputs.DocExtractQuarkInput,
        "constructor": DocExtractQuark,
    },
    {
        "identifier": "quark:files:s3_read_csv",
        "input": inputs.S3ReadCSVQuarkInput,
        "constructor": S3ReadCSVQuark
    },
    {
        "identifier": "quark:files:s3_read_files_binary",
        "input": inputs.S3ReadWholeFileQuarkInput,
        "constructor": S3ReadWholeFileQuark,
    },
    {
        "identifier": "quark:files:opendal_list_binary",
        "input": inputs.OpendalInput,
        "constructor": OpendalReadQuark,
     },
    {
        "identifier": "quark:other:context_insert_objects",
        "input": inputs.ContextInsertObjectsInput,
        "constructor": ContextInsertObjectsQuark,
    },
    {
        "identifier": "quark:other:context_insert_segments",
        "input": inputs.ContextInsertSegmentsInput,
        "constructor": ContextInsertSegmentsQuark,
    },
    {
        "identifier": "quark:other:context_insert_classified_segments",
        "input": inputs.ContextInsertClassifiedSegmentsInput,
        "constructor": ContextInsertClassifiedSegmentsQuark,
    },
    {
        "identifier": "quark:other:context_insert_extracted_segments",
        "input": inputs.ContextInsertExtractedSegmentsInput,
        "constructor": ContextInsertExtractedSegmentsQuark,
    },
    {
        "identifier": "quark:transformer:classifier_prompt",
        "input": inputs.ContextClassifierPromptInput,
        "constructor": ClassifierPromptQuark,
    },
    {
        "identifier": "quark:transformer:extractor_prompt",
        "input": inputs.ContextExtractPromptInput,
        "constructor": ExtractorPromptQuark,
    },
    {
        "identifier": "quark:transformer:extractor_parser",
        "input": inputs.ParseExtractorLlmInput,
        "constructor": ExtractorParserQuark,
    },
    {
        "identifier": "quark:transformer:classifier_parser",
        "input": inputs.ParseClassifierLlmInput,
        "constructor": ClassifierParserQuark,
    },
    {
        "identifier": "quark:transformer:onnx_sat_segmentation",
        "input": inputs.SaTSegmentationInput,
        "constructor": SaTSegmentQuark,
    },
    {
        "identifier": "quark:transformer:docling_chunker",
        "input": inputs.DocChunkerQuarkInput,
        "constructor": DocChunkerQuark,
    },
    {
        "identifier": "quark:transformer:handlebars_base",
        "input": inputs.TextTemplateInput,
        "constructor": TextTemplateBaseQuark,
    },
    {
        "identifier": "quark:vector:lancedb_ingest",
        "input": inputs.VectorDBIngestInput,
        "constructor": VectorDBIngestQuark,
    },
    {
        "identifier": "quark:vector:lancedb_search",
        "input": inputs.VectorDBSearchInput,
        "constructor": VectorDBSearchQuark,
    },
]
