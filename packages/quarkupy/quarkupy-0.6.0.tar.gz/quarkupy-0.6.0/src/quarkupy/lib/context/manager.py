from __future__ import annotations

import pydantic

from typing import Optional, Any, Union

from httpcore import URL
from pydantic import PrivateAttr

import quarkupy as q
import pyarrow as pa


class ContextManager(pydantic.BaseModel):
    """
    Manage context within the Quark platform
    """

    # Pydantic model configuration
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    # API configuration
    base_url: Union[str, URL, None]

    _client: q.AsyncClient = PrivateAttr()

    def init_client(self) -> None:
        """
        Initialize the Quark client with the provided API key and base URL.

        :return: An instance of `q.AsyncClient`.
        """
        if not self._client:
            self._client = q.AsyncClient(
                base_url=self.base_url
            )

        return

    def model_post_init(self, __context: Any) -> None:
        """
        Post-initialization method to set up the client after the model is created.

        :param __context: The context in which the model is being initialized.
        """
        #self.init_client()
        return

    async def get_files(self, source_id: Optional[pydantic.types.UUID] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> pa.Table:
        """
        Fetches files from a specified source asynchronously. This method interacts
        with an external service to retrieve file data. It allows optional filtering
        based on a source identifier and supports pagination through limit and offset
        parameters. Retrieved data is processed into a table format before being
        returned.

        Parameters:
            source_id (Optional[UUID]): A source identifier to filter the files by, or
                None to fetch files without filtering by source.
            limit (Optional[int]): The maximum number of files to retrieve, or None to
                fetch all available files.
            offset (Optional[int]): The starting offset for file retrieval, or None to
                start from the beginning.

        Returns:
            pa.Table: A pyarrow Table object containing the fetched file data.

        Raises:
            This method does not handle exceptions internally; any errors encountered
            during execution, such as networking or processing errors, will be raised
            directly.
        """
        source_id_param = source_id.__str__() if source_id else None
        limit_param = limit if limit is not None else None
        offset_param = offset if offset is not None else None

        client = q.AsyncClient(
                base_url=self.base_url
            )

        raw = await client.worker.context.retrieve_files(source_id=source_id_param, limit=limit_param, offset=offset_param)
        buf = await raw.read()
        await client.close()

        return pa.ipc.open_stream(buf).read_all()

    async def get_classifiers(self, source_id: Optional[pydantic.types.UUID] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> pa.Table:
        """
        Asynchronously retrieves a list of classifiers from the specified data source. The classifiers
        can be fetched with an optional limit on the number of results, an offset for pagination,
        and can also be filtered by a specific source ID. The data is returned as an Apache Arrow
        table.

        Parameters:
            source_id (Optional[UUID]):
                An optional UUID representing the data source for which classifiers should be
                fetched. If not provided, classifiers from all sources will be retrieved.

            limit (Optional[int]):
                An optional integer specifying the maximum number of classifiers to retrieve. If
                not provided, there will be no limit applied.

            offset (Optional[int]):
                An optional integer specifying the offset for pagination of the results. If not
                provided, it will default to fetching results from the beginning.

        Returns:
            pa.Table:
                An Apache Arrow table containing the retrieved classifiers data.

        Async:
            This method is an asynchronous coroutine and should be awaited to retrieve its full
            result.

        """
        source_id_param = source_id.__str__() if source_id else None
        limit_param = limit if limit is not None else None
        offset_param = offset if offset is not None else None

        client = q.AsyncClient(
                base_url=self.base_url
            )

        raw = await client.worker.context.classifiers.list(source_id=source_id_param, limit=limit_param, offset=offset_param)
        buf = await raw.read()
        await client.close()

        return pa.ipc.open_stream(buf).read_all()

    async def get_extractors(self, source_id: Optional[pydantic.types.UUID] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> pa.Table:
        """
        Retrieve extractor details from a specified source and return them as a PyArrow Table.

        This method asynchronously fetches data about extractors based on the given source
        ID, with options for pagination using the limit and offset parameters. The data is
        retrieved via an HTTP client, and the raw response is processed into a PyArrow Table.

        Parameters:
            source_id (Optional[pydantic.types.UUID]): The unique identifier of the source to retrieve extractors from.
                If None, extractors from all sources will be retrieved.
            limit (Optional[int]): The maximum number of extractor records to retrieve. If None, no limit is applied.
            offset (Optional[int]): The number of extractor records to skip before collecting results. If None, no offset is applied.

        Returns:
            pa.Table: A PyArrow Table containing the list of extractors retrieved from the source.

        Raises:
            TypeError: Raised if invalid types are provided for method arguments.
            aiohttp.ClientError: Raised when there are HTTP client related issues during the data retrieval process.
            ValueError: Raised if the response cannot be parsed into a valid format or if an error occurs while
                processing the data.
        """
        source_id_param = source_id.__str__() if source_id else None
        limit_param = limit if limit is not None else None
        offset_param = offset if offset is not None else None

        client = q.AsyncClient(
                base_url=self.base_url
            )

        raw = await client.worker.context.extractors.list(source_id=source_id_param, limit=limit_param, offset=offset_param)
        buf = await raw.read()
        await client.close()

        return pa.ipc.open_stream(buf).read_all()

    async def get_classifier_text(self, classifier_id: pydantic.types.UUID) -> pa.Table:
        """
        Retrieve and return classifier text data in the form of an Apache Arrow Table.

        This asynchronous method communicates with a remote asynchronous API to fetch textual data
        associated with a specific classifier by its identifier. The retrieved data is processed and
        returned as an Apache Arrow Table.

        Parameters:
            classifier_id (UUID): The unique identifier of the classifier whose text data is to
                be retrieved.

        Returns:
            pa.Table: The classifier text data encapsulated in an Apache Arrow table.
        """
        client = q.AsyncClient(
                base_url=self.base_url
            )

        raw = await client.worker.context.classifiers.retrieve_text(classifier_id=classifier_id.__str__())
        buf = await raw.read()
        await client.close()

        return pa.ipc.open_stream(buf).read_all()

    async def get_extractor_text(self, extractor_id: pydantic.types.UUID) -> pa.Table:
        """
        Asynchronously retrieves and processes text data from an extractor using its unique
        identifier and converts it into a PyArrow table.

        Parameters:
        extractor_id: pydantic.types.UUID
            The unique identifier of the text extractor.

        Returns:
        pa.Table
            A PyArrow Table containing the processed text data.

        Raises:
        Any exceptions raised during HTTP communication with the client, data retrieval,
        or PyArrow table processing.
        """
        client = q.AsyncClient(
                base_url=self.base_url
            )

        raw = await client.worker.context.extractors.retrieve_text(extractor_id=extractor_id.__str__())
        buf = await raw.read()
        await client.close()

        return pa.ipc.open_stream(buf).read_all()
