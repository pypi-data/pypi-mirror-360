from ewokscore import Task
from ewokscore.missing_data import MissingData
from pathlib import Path
import logging
from pyicat_plus.client.main import IcatClient
from pyicat_plus.client import defaults

logger = logging.getLogger(__name__)


class DataPortalUpload(
    Task, input_names=["processed_data_dir"], optional_input_names=["metadata"]
):
    """
    Task that uploads processed data to the Data Portal using pyicat_plus.
    This task is designed to be used in the context of a data processing pipeline.
    """

    def run(self):
        """
        Infers ICAT parameters from the processed data directory and stores processed data information
        using pyicat_plus.

        The processed_data_dir (icat_processed_path) is taken from the directory of the output path.
        For a processed_data_dir like:

        /data/visitor/proposal/beamline/sessions/PROCESSED_DATA/sample/sample_dataset
        """
        icat_processed_path = Path(self.inputs.processed_data_dir)
        path_parts = icat_processed_path.parts

        try:
            data_index = path_parts.index("PROCESSED_DATA")
            # Expected structure: ['', 'data', 'visitor', 'proposal', 'beamline', 'sessions', 'PROCESSED_DATA', 'sample', 'sample_dataset', 'sample_dataset.nx']
            proposal = path_parts[data_index - 3]
            beamline = path_parts[data_index - 2]
            dataset = path_parts[data_index + 2]
            sample_name = path_parts[data_index + 1]
        except (IndexError, ValueError):
            logger.warning(
                "Could not infer ICAT parameters from processed_data_dir: %s",
                icat_processed_path,
            )
            return

        # Replace 'PROCESSED_DATA' with 'RAW_DATA' in the path
        try:
            icat_raw = [
                "RAW_DATA" if part == "PROCESSED_DATA" else part
                for part in icat_processed_path.parts
            ]
            icat_raw = Path(*icat_raw)
        except Exception as e:
            logger.warning("Error constructing RAW_DATA path: %s", e)
            return

        if isinstance(self.inputs.metadata, MissingData):
            icat_metadata = {"Sample_name": sample_name}
        else:
            icat_metadata = self.inputs.metadata
            if not isinstance(icat_metadata, dict):
                raise ValueError("Metadata must be a dictionary.")

        try:
            client = IcatClient(metadata_urls=defaults.METADATA_BROKERS)
            client.store_processed_data(
                beamline=beamline,
                proposal=proposal,
                dataset=dataset,
                path=str(icat_processed_path),
                raw=[str(icat_raw)],
                metadata=icat_metadata,
            )
            client.disconnect()
        except Exception as e:
            logger.warning("Error storing processed data to ICAT: %s", e)
