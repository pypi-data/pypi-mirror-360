import hashlib
import os
import threading
import time
from base64 import b64encode
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Generator

from blinker import Signal, signal
from requests import Response, post

from qmenta.core import errors, platform, auth
from qmenta.core.upload import prepare


"""
Handles the uploading of data to QMENTA platform.
"""


class UploadError(errors.Error):
    """
    When a problem occurs while uploading.
    """
    pass


class UploadAlreadyStartedError(UploadError):
    """
    When calling upload_file() a second time and the upload is already
    in progress.
    """
    pass


class UploadAlreadyDoneError(UploadError):
    """
    When calling upload_file() a second time and the upload already finished.
    """
    pass


@dataclass
class FileInfo:
    """
    Specifies the metadata of a file that will be uploaded to the platform.

    Parameters
    ----------
    project_id : int
        The ID of the project to which the new file will be added
    name : str
        The name of the file in the platform. It is recommended to use the
        filename (optional)
    date_of_scan : str
        The date when the scan was made (optional)
    description : str
        A description of the data that is uploaded (optional)
    subject_name : str
        The anonymised ID of the subject (optional)
    session_id : str
        The ID of the scanning session for the subject (optional).
        If left blank, the next numerical session ID for the subject will
        automatically be assigned to the session by the platform.
    input_data_type : str
        The analysis to be used to process the data (optional).
        When left blank, the input data type will be set automatically.
        It is recommended to leave it blank, except for testing specific tools
        for processing uploaded data.
    is_result : bool
        Default value: False. Set to True if the uploaded data is the output
        of an offline analysis.
    add_to_container_id : int
        ID of the container to which this file should be added (if id > 0).
        Default value: 0. When the value is 0, the data will be added to
        a new container.
    split_data : bool
        If True, the platform will try to split the uploaded file into
        different sessions. It will be ignored when the session_id is given.
        Default value: False.
    """
    project_id: int
    name: str = ""
    date_of_scan: str = ""
    description: str = ""
    subject_name: str = ""
    session_id: str = ""
    input_data_type: str = ""
    is_result: bool = False
    add_to_container_id: int = 0
    split_data: bool = False

    def __post_init__(self) -> None:
        if self.is_result and not self.input_data_type:
            self.input_data_type = "offline_analysis:1.0"

        if self.split_data and self.session_id:
            # Don't split data when session_id is set
            self.split_data = False


class UploadStatus(Enum):
    """
    The current stage of a SingleUpload in the uploading process.
    """

    TO_ZIP = 0
    TO_ZIP_AND_ANONYMISE = 1
    ZIPPING = 2
    TO_ANONYMISE = 3
    ANONYMISING = 4
    TO_UPLOAD = 5
    UPLOADING = 6
    TO_CLEAN = 7
    DELETING_TMP_FILES = 8
    DONE = 9
    FAILED = 10


class SingleUpload:
    """
    Class to upload a single ZIP file to the platform.
    When there is a failure in initializing the instance,
    status will be set to FAILED, and a status_message will
    be set.

    Parameters
    ----------
    auth : Auth
        The object used to authenticate to the QMENTA platform.
    path : str
        The input directory or file that will be zipped (optional),
        anonymised (optional) and uploaded.
    file_info : FileInfo
        All the metadata for the file to be stored in the platform.
    anonymise : bool
        If set, a new zip file will be created with the same name which
        contains the anonymised version of the data of the original
        zip file. The new zip file will be uploaded instead of the original
        one. Default value: True.
    upload_index : int
        This value will be passed to the 'upload-status' and 'upload-progress'
        signals. It is set by MultipleThreadedUploads and used to quickly
        identify the upload that was updated. Default value: -1.
    keep_created_files : bool
        Keep the files containing the zipped directory and anonymised data
        after the upload finished. When set to False, the ``qm-*.zip`` files
        that were created by this SingleUpload will be deleted when the upload
        if finished. Default value: True.

    Attributes
    ----------
    input_filename : str
        The file that will be anonymised (optional), and uploaded.
    upload_filename : str
        The file that will be uploaded. If anonymisation is disabled, this
        will be the same as filename. With anonymisation enabled, a new file
        will be created that contains the anonymised data.
    upload_id : str
        The upload session ID. This will be automatically generated and
        depends on the current time and the upload filename.
    file_size : int
        The size in bytes of the file to be uploaded. Automatically determined
        when the SingleUpload object is constructed.
    status_message : str
        In case the status becomes FAILED, status_message will contain a
        message indicating what went wrong.

    Raises
    ------
    errors.CannotReadFileError
        When the input cannot be read
    """

    # Only run a single anonymisation at once to prevent using too many
    #   computer resources, and to prevent reading/writing from/to the same
    #   file in multiple threads.
    _anon_lock: threading.Lock = threading.Lock()

    def __init__(
        self,
        auth: auth.Auth,
        path: str,
        file_info: FileInfo,
        anonymise: bool = True,
        upload_index: int = -1,
        keep_created_files: bool = True,
    ) -> None:
        self.auth = auth
        self.path = path
        self.file_info = file_info
        self.upload_index = upload_index
        self.keep_created_files = keep_created_files
        self._created_files_list: List[str] = []

        # file_size will be set in _check_type_and_size if the original file
        #   will be uploaded, or after anonymisation when anonymise == True.
        self.file_size: int = -1
        self._bytes_uploaded: int = 0

        self._status_signal: Signal = signal("upload-status")
        self._progress_signal: Signal = signal("upload-progress")

        self._status: UploadStatus
        self.upload_filename: str

        # Optimized for GCS Bucket Storage
        self._chunk_size = 2**24  # 16 MiB

        if os.path.isfile(self.path):
            self.input_filename = self.path
            if anonymise:
                self.upload_filename = ""  # to be set when anonymising
                self._status = UploadStatus.TO_ANONYMISE
            else:
                self.upload_filename = self.input_filename
                self._status = UploadStatus.TO_UPLOAD

        elif os.path.isdir(self.path):
            self.input_filename = ""  # to be set when zipping
            self.upload_filename = ""
            if anonymise:
                self._status = UploadStatus.TO_ZIP_AND_ANONYMISE
            else:
                self._status = UploadStatus.TO_ZIP
        else:
            raise errors.CannotReadFileError(
                "Cannot read input zip file or directory: {}".format(self.path)
            )

        self.status_message: str = ""
        self.upload_id: str = ""

        # This will store the response (from requests library) object from the
        # last upload request
        self._last_response: Optional[Response] = None

    @staticmethod
    def _get_upload_id(file_path: str) -> str:
        m = hashlib.md5()
        m.update(str(file_path).encode("utf-8"))
        return str(time.time()).replace(".", "") + "_" + m.hexdigest()

    @property
    def status(self) -> UploadStatus:
        """
        UploadStatus: The current status of the upload.
        Setting the status will trigger signal('upload-status').
        """
        return self._status

    @status.setter
    def status(self, value: UploadStatus) -> None:
        if self._status != value:
            self._status = value
            self._status_signal.send(self, upload_index=self.upload_index)

    @property
    def bytes_uploaded(self) -> int:
        """
        int: The amount of bytes that has been uploaded so far.
        When the value is updated, signal('upload-progress') is sent.
        """
        return self._bytes_uploaded

    @bytes_uploaded.setter
    def bytes_uploaded(self, value: int) -> None:
        if self._bytes_uploaded != value:
            self._bytes_uploaded = value
            self._progress_signal.send(self, upload_index=self.upload_index)

    def _add_upload_info_to_request_headers(
        self, upload_info: FileInfo, headers: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        headers["X-Mint-Name"] = upload_info.name
        headers["X-Mint-Date"] = upload_info.date_of_scan
        headers["X-Mint-Description"] = upload_info.description
        headers["X-Mint-Patient-Secret"] = upload_info.subject_name
        headers["X-Mint-SSID"] = upload_info.session_id
        headers["X-Mint-Project-Id"] = str(upload_info.project_id)
        headers["X-Mint-Split-Data"] = str(int(upload_info.split_data))

        if upload_info.input_data_type:
            headers["X-Mint-Type"] = upload_info.input_data_type

            if upload_info.is_result:
                headers["X-Mint-In-Out"] = "out"
            else:
                headers["X-Mint-In-Out"] = "in"

        if upload_info.add_to_container_id > 0:
            headers["X-Mint-Add-To"] = str(upload_info.add_to_container_id)
        return headers

    def start(self) -> None:
        """
        Check that the file was not uploaded yet, anonymise it if needed,
        and upload the (anonymised) file.
        When there is a failure in anonymising or uploading, status
        will be set to FAILED and a status_message is set.

        Raises
        ------
        UploadAlreadyDoneError
        UploadAlreadyStartedError
        prepare.FileError
        """
        if self.status in [UploadStatus.FAILED, UploadStatus.DONE]:
            raise UploadAlreadyDoneError(self.input_filename)
        elif self.status == UploadStatus.UPLOADING:
            raise UploadAlreadyStartedError(self.input_filename)

        assert self._last_response is None

        to_zip: bool = self.status in [
            UploadStatus.TO_ZIP,
            UploadStatus.TO_ZIP_AND_ANONYMISE,
        ]
        to_anonymise: bool = self.status in [
            UploadStatus.TO_ZIP_AND_ANONYMISE,
            UploadStatus.TO_ANONYMISE,
        ]

        try:
            if to_zip:
                self._zip_directory()

            if to_anonymise:
                self._anonymise_zip_file()
            else:
                self.upload_filename = self.input_filename

            self.upload_id = SingleUpload._get_upload_id(self.upload_filename)
            self._last_response = self._upload_file()

            if self._status == UploadStatus.TO_CLEAN:
                for filename in self._created_files_list:
                    self._delete_file(filename)

                self.status = UploadStatus.DONE

        except errors.Error as e:
            self.status_message = str(e)
            self.status = UploadStatus.FAILED

    def _zip_directory(self) -> None:
        """
        Zip the contents of the input directory, and updates status
        as needed.

        Raises
        ------
        prepare.FileError
        """
        assert self.status in [
            UploadStatus.TO_ZIP,
            UploadStatus.TO_ZIP_AND_ANONYMISE,
        ]
        to_anonymise: bool = self.status == UploadStatus.TO_ZIP_AND_ANONYMISE

        with SingleUpload._anon_lock:
            self.input_filename = prepare.get_input_filename(self.path)
            self.status = UploadStatus.ZIPPING
            prepare.zip_directory(self.path, self.input_filename)
            self._created_files_list.append(self.input_filename)
            if to_anonymise:
                self.status = UploadStatus.TO_ANONYMISE
            else:
                self.status = UploadStatus.TO_UPLOAD

    def _anonymise_zip_file(self) -> None:
        """
        Anonymise the file, and updates status as needed.

        Raises
        ------
        prepare.FileError
        """
        assert self.status == UploadStatus.TO_ANONYMISE

        # Check the zip file
        prepare.get_zipfile_size(self.input_filename)

        with SingleUpload._anon_lock:
            self.upload_filename = prepare.get_anon_filename(
                self.input_filename
            )
            self.status = UploadStatus.ANONYMISING
            assert self.input_filename != self.upload_filename
            prepare.anonymise_zip(self.input_filename, self.upload_filename)
            self._created_files_list.append(self.upload_filename)
            self.status = UploadStatus.TO_UPLOAD

    @staticmethod
    def _validate_upload_response(
        response: Response, total_bytes: int, md5_hash: str
    ) -> None:
        """
        Parse a Response object after an upload to verify if it was succesful.

        Parameters
        ----------
        response : requests.Response
            The response of the upload via URL.
        total_bytes : int
            The number of bytes that should have been uploaded.
        md5_hash : str
            The base64 md5 hash of the file that was uploaded.

        Raises
        ------
        UploadError
            The status code, the size or the md5 in the Response object are
            wrong.
        """
        if response.status_code != 200:
            raise UploadError(
                "Upload returned status code {}".format(response.status_code)
            )

        upload_manifest = response.json()
        if int(upload_manifest["size"]) != int(total_bytes):
            raise UploadError(
                "Upload size mismatch: {} != {}".format(
                    upload_manifest["size"], total_bytes
                )
            )

        if upload_manifest["md5Hash"] != md5_hash:
            raise UploadError(
                "MD5 hash mismatch: {} != {}".format(
                    upload_manifest["md5Hash"], md5_hash
                )
            )

    @staticmethod
    def _file_md5(path: str) -> str:
        """Compute the base64 md5 hash of a file.

        Parameters
        ----------
        path : str
            The path of the file.

        Returns
        -------
        str
            A base64 md5 hash.
        """
        BLOCKSIZE = 65536
        hasher = hashlib.md5()
        with open(path, "rb") as fp:
            buf = fp.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = fp.read(BLOCKSIZE)
        return b64encode(hasher.digest()).decode()

    def _upload_file(self) -> Response:
        """
        Upload the file to the QMENTA platform.
        Updates status and progress as needed.

        Returns
        -------
        The Response from the platform for the last uploaded chunk.

        Raises
        ------
        prepare.FileError
        UploadError
        platform.ConnectionError
        """
        assert self.status == UploadStatus.TO_UPLOAD
        self.status = UploadStatus.UPLOADING
        self.file_size = prepare.get_zipfile_size(self.upload_filename)
        fname: str = os.path.split(self.upload_filename)[1]
        self.bytes_uploaded = 0

        url_request_response = platform.post(
            auth=self.auth,
            endpoint="file_manager/get_upload_url",
            data={
                "size": self.file_size,
                "type": "session",
                "path": fname,
                "data_type": self.file_info.input_data_type,
                "container_id": str(self.file_info.add_to_container_id),
                "patient_secret_name": self.file_info.subject_name,
                "ssid": self.file_info.session_id,
                "description": self.file_info.description,
                "date": self.file_info.date_of_scan,
                "split_data": str(int(self.file_info.split_data)),
                "_pid": self.file_info.project_id,
            },
        )

        url_response_data = platform.parse_response(url_request_response)
        signed_url: str = url_response_data["url"]
        container_id: str = url_response_data["container_id"]

        md5_hash: str = self._file_md5(self.upload_filename)

        # Stream file to signed-url without loading it to memory
        max_retries: int = 5
        completed_upload: bool = False
        retries_count: int = 0
        while not completed_upload and retries_count < max_retries:

            def iterate_over_file() -> Generator[Any, Any, Any]:
                with open(self.upload_filename, "rb") as stream:
                    while True:
                        contents = stream.read(self._chunk_size)
                        if not contents:
                            break
                        else:
                            yield contents
                            self.bytes_uploaded += len(contents)

            upload_response = post(
                url=signed_url,
                data=iterate_over_file(),
                stream=True
            )

            # Verify upload
            try:
                self._validate_upload_response(
                    upload_response, self.file_size, md5_hash
                )
            except UploadError:
                retries_count += 1
                if retries_count < max_retries:
                    wait_time: int = 2 ** retries_count
                    time.sleep(wait_time)
                    print(
                        "Retrying upload (#{}) in {}".format(
                            retries_count, wait_time
                        )
                    )
            else:
                completed_upload = True

        if not completed_upload:
            raise UploadError(
                "File {} could not be uploaded to the platform".format(
                    self.upload_filename
                )
            )

        verification_response = platform.post(
            auth=self.auth,
            endpoint="file_manager/verify_upload_via_url",
            data={
                "container_id": container_id,
                "path": fname,
                "md5": md5_hash,
            },
        )
        platform.parse_response(verification_response)
        self.bytes_uploaded = self.file_size
        if self.keep_created_files:
            self.status = UploadStatus.DONE
        else:
            self.status = UploadStatus.TO_CLEAN

        return verification_response

    def _delete_file(self, filename: str) -> None:
        # Only delete files that were created here
        basename: str = os.path.basename(filename)
        assert basename.startswith("qm-")
        assert basename.endswith(".zip")

        os.remove(filename)
