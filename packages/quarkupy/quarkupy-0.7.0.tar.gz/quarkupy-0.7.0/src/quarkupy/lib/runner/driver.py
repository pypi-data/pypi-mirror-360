from __future__ import annotations, absolute_import

import os
import abc
import time
import logging
from time import sleep
from typing import Type, Union, Literal, ClassVar

import pyarrow as pa
import pydantic

import quarkupy

LatticeStatus = Literal["New", "Scheduled", "Running", "Completed", "Failed"]
QuarkStatus = Literal["New", "Scheduled", "Running", "OutputStaged", "Completed", "Failed"]

from . import QuarkHistoryItem, QuarkRegistryItem, inputs

class QuarkRemoteDriver(pydantic.BaseModel, metaclass=abc.ABCMeta):
    """
    Abstract base class for implementing remote drivers (runners) to interact with the Quark system. The base class
    implements nearly all methods except the specific `execute` method, which subclasses must implement to call
    the appropriate API with the appropriate input data.

    :ivar IDENTIFIER: Constant identifier for the Quark driver. Empty string for an abstract class.
    :type IDENTIFIER: ClassVar[str]
    :ivar lattice_id: Universally unique identifier (UUID) representing the lattice.
    :type lattice_id: pydantic.UUID4
    :ivar quark_input: Input parameters or data required for the quark process.
    :type quark_input: QuarkInput
    :ivar _registry_item: Metadata for the registry item fetched from the server, if available.
    :type _registry_item: quarkupy.QuarkRegistryItem | None
    :ivar _history: History or status metadata fetched or created on the server.
    :type _history: quarkupy.QuarkHistoryItem | None
    """

    # Pydantic model configuration
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    # Const identifier for the Quark - empty string for abstract class
    IDENTIFIER: ClassVar[str]

    # Quark Inputs
    lattice_id: str
    quark_input: inputs.QuarkInput

    # API configuration
    QUARK_API_KEY: str = os.environ.get("QUARK_API_KEY")
    BASE_URL: str

    # Server-side registry metadata
    _registry_item: QuarkRegistryItem | None = None

    # Server-side history/status metadata
    _history: QuarkHistoryItem | None = None
    _quark_id: pydantic.UUID7 | None = None

    @property
    def quark_id(self):
        return self._quark_id

    @property
    def history(self):
        return self._history

    @history.setter
    def history(self, history):
        self._history = history

    @property
    def registry_item(self):
        return self._registry_item

    @classmethod
    def from_identifier(
        cls,
        identifier: str,
        lattice_id: str,
        quark_input: inputs.QuarkInput,
    ) -> QuarkRemoteDriver:
        """
        Constructs an instance of `QuarkNativeRunner` using the provided identifier
        to determine the appropriate constructor. The method searches the
        `quark_runner_mapping` for an entry matching the identifier.

        :param identifier: Identifier used to match an entry in `quark_runner_mapping`.
        :param lattice_id: A UUID4 to uniquely represent the lattice.
        :param quark_input: Input parameters or data required for the quark runner.
        :return: An instance of `QuarkNativeRunner` constructed with the mapped
            constructor.
        :raises ValueError: If `identifier` is not found in `quark_runner_mapping`.
        """
        from quarks import quark_runner_mapping

        for mapping in quark_runner_mapping:
            if mapping["identifier"] == identifier:
                return mapping["constructor"](lattice_id=lattice_id, quark_input=quark_input)

        raise ValueError(f"Quark identifier {identifier} not found in quark_runner_mapping")

    @staticmethod
    def input_type_by_identifier(identifier: str) -> inputs.QuarkInput:
        """
        Returns the input class for the given identifier.

        This method returns the input class for the given identifier. The identifier
        is used to search the `quark_runner_mapping` for the corresponding input class.

        :param identifier: Identifier used to match an entry in `quark_runner_mapping`.
        :return: The input class corresponding to the identifier.
        """
        from quarks import quark_runner_mapping

        for mapping in quark_runner_mapping:
            if mapping["identifier"] == identifier:
                if mapping["input"] is None:
                    raise ValueError(f"No input class found for identifier {identifier}")
                return Type[mapping["input"]]
            else:
                raise ValueError(f"No input class found for identifier {identifier}")
        return None

    async def poll_until_complete(self, timeout_min: int = 30, interval_sec: int = 2) -> QuarkHistoryItem | None:
        if interval_sec < 1:
            raise ValueError("Must have a minimum poll interval of 1s")
        start_time = time.monotonic()
        poll_timeout_time = start_time + (timeout_min * 60)

        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)

        while time.monotonic() < poll_timeout_time:
            history = await api_client.history.quark.retrieve(id=self.quark_id)

            if history.status == "Completed":
                await api_client.close()
                self.history = history

                return history

            elif history.status == "Failed":
                logging.log(logging.ERROR, "Quark Run Failed")
                await api_client.close()
                self.history = history

                return history

            sleep(interval_sec)

        raise TimeoutError("Timed out waiting on Quark to complete")

    async def get_registry_item(self) -> QuarkRegistryItem:
        """
        Fetches a single registry item based on its identifier from the Quark service.

        This method retrieves a specific item from the quark registry through a REST
        API call. The identifier of the item should be in the format `quark:category:name`.
        The function interacts with the `quarkupy` API client to extract the category
        and name from the identifier and fetches the corresponding registry information.

        :return: An instance of `quarkupy.QuarkRegistryItem` containing the
                 information of the requested registry item.
        """
        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)

        cat, name = self.IDENTIFIER.split(":")[1:]
        res = await api_client.worker.registry.quark.retrieve(name=name, cat=cat)

        # Close the API client to avoid closure errors in asyncio
        await api_client.close()

        return res

    async def save_history(self):
        """
        Saves the Quark history (status) - as stored in this model - on the Quark services via a REST call. This call is an "upsert" call, meaning
        if a history item with the same `quark_id` exists, it will be updated with the new status. If not, a new history
        item will be created.


        :raises Exception: If there is an error during the API operation.
        """
        if self._history is not None:
            api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)

            await api_client.history.quark.update(**self.history.model_dump())
            await api_client.close()
        else:
            raise Exception("No history item to save")

    async def start(self):
        """
        Starts the process by retrieving a registry item and initializing a new history item.

        This method must be executed before the `execute` method to ensure the Quark is properly initialized

        :return: None
        :rtype: None
        """
        self._registry_item = await self.get_registry_item()

    async def read_output_dataset(self) -> Union[pa.Table, None]:
        """
        Retrieves the output dataset associated with a completed Quark process.
        If the Quark process did not complete successfully, or if a dataset is unavailable, this
        method will return None. Otherwise, it fetches the dataset using the provided Quarkupy
        API and reads its content into an Apache Arrow Table.

        :parameter: None
        :raises Exception: If an issue occurs when attempting to retrieve or read the dataset
            data using the API.
        :return: An Apache Arrow Table containing the dataset data or None if the dataset is
            unavailable.
        :rtype: pa.Table | None
        """
        if self._history.status == "Failed":
            raise Exception(f"Quark {self._history.quark_id} failed to complete")

        elif self._history.status != "Completed":
            logging.log(logging.ERROR, f"Quark {self._history.quark_id} has not complete successfully")
            return None

        elif self._history.output["dataset_uuid"] is None:
            logging.log(logging.ERROR, f"Quark {self._history.quark_id} did not produce a dataset")
            return None

        api_client = quarkupy.AsyncClient(base_url=self.BASE_URL)

        record_batches_raw = await api_client.worker.dataset.retrieve_arrow(self._history.output["dataset_uuid"])
        buf = await record_batches_raw.read()

        await api_client.close()

        return pa.ipc.open_stream(buf).read_all()

    @abc.abstractmethod
    async def execute(self) -> QuarkHistoryItem:
        """
        Executes the Quark on the remote worker and returns the history item of its status.

        :return:
        """
        raise NotImplementedError
