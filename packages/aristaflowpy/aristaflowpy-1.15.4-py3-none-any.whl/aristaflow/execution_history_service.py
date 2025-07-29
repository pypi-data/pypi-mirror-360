# Default Python Libraries
from typing import Generator

# AristaFlow REST Libraries
from af_process_manager.api.exec_hist_entry_remote_iterator_rest_api import (
    ExecHistEntryRemoteIteratorRestApi,
)
from af_process_manager.api.execution_history_api import ExecutionHistoryApi
from af_process_manager.models.exec_hist_entry_initial_remote_iterator_data import (
    ExecHistEntryInitialRemoteIteratorData,
)
from af_process_manager.models.execution_history_entry import ExecutionHistoryEntry
from aristaflow.abstract_service import AbstractService


class ExecutionHistoryService(AbstractService):
    """
    Accessing the execution history
    """

    def read_instance_history(self, inst_log_id) -> Generator[ExecutionHistoryEntry, None, None]:
        """
        Returns a generator allowing to read an arbitrary number of execution history entries.
        Close the generator for dropping the remote iterator.
        """
        pm: ExecutionHistoryApi = self._service_provider.get_service(ExecutionHistoryApi)
        eh_iter_api: ExecHistEntryRemoteIteratorRestApi = self._service_provider.get_service(
            ExecHistEntryRemoteIteratorRestApi
        )
        next_iter: ExecHistEntryInitialRemoteIteratorData = pm.read_instance_history(
            inst_log_id
        )
        # seems unlikely but still occurred
        if next_iter is None:
            return
        iterator_id = next_iter.iterator_id
        try:
            while next_iter and next_iter.exec_hist:
                for entry in next_iter.exec_hist:
                    yield entry
                if next_iter.closed:
                    break
                next_iter = eh_iter_api.exec_hist_entry_get_next(iterator_id)
        except GeneratorExit:
            # generator closed
            if iterator_id:
                eh_iter_api.exec_hist_entry_close(iterator_id)
