import pathlib
import typing

class Acquisition:
    def __init__(
        self,
        path: typing.Union[str, pathlib.Path],
    ) -> None:
        """Open an acquisition folder at the given path.

        Args:
            path (typing.Union[str, pathlib.Path]): the path to the acquisition folder
        """
    @property
    def path(self) -> str:
        """Get the acquisition path"""
    @property
    def name(self) -> str:
        """Get the acquisition name"""
    @property
    def params(self) -> dict:
        """Get the acquisition parameters dict."""
    @property
    def metadata(self) -> dict:
        """Get the acquisition metadata dict."""
    @property
    def readout_metadata(self) -> typing.Optional[dict]:
        """Get the acquisition readout metadata dict."""
    @property
    def pedestals_calibration(self) -> typing.Optional[dict]:
        """Get the acquisition pedestals calibration dict if available"""
    @property
    def adc_to_mv_calibration(self) -> typing.Optional[dict]:
        """Get the acquisition ADC to mV calibration dict if available"""
    @property
    def timing_calibration(self) -> typing.Optional[dict]:
        """Get the acquisition timing calibration dict if available"""
    @property
    def is_valid(self) -> bool:
        """Check if the acquisition folder is a valid acquisition."""
    @property
    def chunk_count(self) -> int:
        """Get the number of chunks (.bin/.idx file pairs) in the acquisition."""
    def raw_event(self, index: int) -> dict:
        """Get the raw event at the given index.

        Args:
            index (int): the event index

        Returns:
            dict: the event

        Raises:
            IndexError: if the event index is out of bounds
        """
    def parsed_event(self, index: int) -> dict:
        """Get a parsed event at the given index. Requires naludaq to be installed.

        Args:
            index (int): the event index

        Returns:
            dict: the event. If the event could not be parsed, the "data" key
                will not be present.

        Raises:
            ImportError: if naludaq is not installed
            IndexError: if the event index is out of bounds
        """
    @typing.overload
    def __getitem__(self, index: int) -> dict:
        """Get a parsed event from the acquisition.

        Args:
            index (int): the index of the event.

        Returns:
            dict: the event

        Raises:
            IndexError: if the event index is out of bounds
        """
    @typing.overload
    def __getitem__(self, indices: slice) -> list[dict]:
        """Get a list of parsed events from the acquisition.

        Args:
            indices (slice): the indices of the events.

        Returns:
            list[dict]: the list of events
        """
    def __len__(self) -> int: ...
    def __iter__(self) -> typing.Iterator[dict]: ...

def is_acquisition(path: typing.Union[str, pathlib.Path]) -> bool:
    """Check if the given path is an acquisition folder.

    Args:
        path (typing.Union[str, pathlib.Path]): the path to check

    Returns:
        bool: True if the path is an acquisition folder, False otherwise
    """

def list_acquisitions(
    path: typing.Union[str, pathlib.Path]
) -> typing.List[Acquisition]:
    """List the acquisitions in the given folder.

    Args:
        path (typing.Union[str, pathlib.Path]): the folder path

    Returns:
        list[Aquisition]: the list of acquisition names
    """

def export_csv(
    acq: Acquisition,
    indices: typing.Iterable[int],
    out_dir: typing.Union[str, pathlib.Path],
    pedestals_correction: bool,
):
    """Export the given events to one or more CSV files.

    Args:
        acq (Acquisition): the acquisition containing the events to export.
        indices (typing.Iterable[int]): the indices of the events to export.
        out_dir (typing.Union[str, pathlib.Path]): the output directory for the
            CSV files.
        pedestals_correction (bool): whether to apply the pedestals correction.
            If the acquisition does not contain pedestals calibration this flag
            is ignored.
    """
