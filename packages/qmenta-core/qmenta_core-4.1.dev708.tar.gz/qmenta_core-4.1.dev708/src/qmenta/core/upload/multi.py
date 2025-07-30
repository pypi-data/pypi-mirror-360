import threading
from blinker import signal, Signal
from typing import List

from qmenta.core.upload.single import SingleUpload, UploadStatus, FileInfo
from qmenta.core.auth import Auth

"""
Handles the uploading of multiple data sets in parallel to QMENTA platform.
"""


class MultipleThreadedUploads():
    """
    Multiple uploads that are running in their own threads.
    signal('upload-progress') is triggered when a SingleUpload progress is
    changed. signal('upload-status') is triggered when a SingleUpload status is
    changed. Both signals are triggered with upload_index as a parameter.

    Parameters
    ----------
    auth : platform.Auth
        The Auth object to communicate with QMENTA platform

    Attributes
    ----------
    upload_list : list[SingleUpload]
        The SingleUpload objects that were added
    uploads_in_progress : int
        The number of uploads that are currently in progress
    """
    def __init__(self, auth: Auth) -> None:
        self.auth = auth
        self.upload_list: List[SingleUpload] = []
        self._last_upload_started_index: int = -1
        self.uploads_in_progress: int = 0
        self._max_parallel_uploads: int = 3

        on_status: Signal = signal('upload-status')
        on_status.connect(self._status_changed)

        self._upload_appended_signal: Signal = signal('upload-appended')
        self._all_threads: List[threading.Thread] = []

    def __del__(self) -> None:
        # Wait for all the upload threads to finish
        for thread in self._all_threads:
            thread.join()

    @property
    def max_parallel_uploads(self) -> int:
        """
        int : The maximum number of uploads to be in progress at the same time.
        When files are added and less uploads are in progress than the maximum
        allowed parallel uploads, the new file upload is automatically started.
        If an upload finishes, the next queued file upload will automatically
        be started.
        Decreasing the value of max_parallel_uploads will not terminate
        uploads that are already in progress. Default value: 3.
        """
        return self._max_parallel_uploads

    @max_parallel_uploads.setter
    def max_parallel_uploads(self, value: int) -> None:
        if self._max_parallel_uploads != value:
            self._max_parallel_uploads = value
            can_start_upload = (
                self._last_upload_started_index < len(self.upload_list) - 1
            )
            if self.uploads_in_progress < value and can_start_upload:
                self._start_next_upload()

    def add_upload(
        self, filename: str, file_info: FileInfo,
        anonymise: bool = True, keep_created_files: bool = True
    ) -> None:
        """
        Add a new upload to the upload list.

        Parameters
        ----------
        filename : str
            The full path to the file to be uploaded.
        file_info : FileInfo
            The metadata of the file to be uploaded.
        anonymise : bool
            Anonymise the data before uploading. Default value: True
        keep_created_files : bool
            Keep the files created by zipping and anonymising data. If set to
            False, the files that were created will be deleted after the
            upload. Default value: True.
        """
        upload_index: int = len(self.upload_list)
        new_upload: SingleUpload = SingleUpload(
            auth=self.auth,
            path=filename,
            file_info=file_info,
            anonymise=anonymise,
            upload_index=upload_index,
            keep_created_files=keep_created_files
        )
        self.upload_list.append(new_upload)
        self._upload_appended_signal.send(self, upload_index=upload_index)

        if self.uploads_in_progress < self.max_parallel_uploads:
            self._start_next_upload()

    def _status_changed(self, single_upload: SingleUpload,
                        upload_index: int) -> None:
        if single_upload.status in [
            UploadStatus.DONE, UploadStatus.FAILED
        ]:
            # When manually setting status of uploads when testing,
            #   we skip setting status to UPLOADING so the counter is wrong.
            #   So check that the value is > 0 first.
            if self.uploads_in_progress > 0:
                self.uploads_in_progress -= 1
            if (
                self._last_upload_started_index < len(self.upload_list) - 1
                and self.uploads_in_progress < self.max_parallel_uploads
            ):
                self._start_next_upload()

    def _start_next_upload(self) -> None:
        self.uploads_in_progress += 1
        self._last_upload_started_index += 1
        single_upload: SingleUpload = self.upload_list[
            self._last_upload_started_index]

        thread: threading.Thread = threading.Thread(target=single_upload.start)
        self._all_threads.append(thread)
        thread.start()
