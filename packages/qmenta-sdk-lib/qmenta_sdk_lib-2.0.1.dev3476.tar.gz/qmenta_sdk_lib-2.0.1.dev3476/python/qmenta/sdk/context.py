import hashlib
import json
import logging
import os
import re
import time
import uuid
import zipfile
from base64 import b64encode
from enum import Enum

from requests import HTTPError

from qmenta.sdk.directory_utils import TemporaryDirectory


class NoFilesError(Exception):
    """Error raised when no files are found in a `data` analysis type."""

    pass


class AnalysisContext:
    class QCEntity(Enum):
        """Enum with the following options: ANALYSIS, SESSION."""

        ANALYSIS = "analysis"
        SESSION = "patients"

    class QCStatus(Enum):
        """Enum with the following options: FAIL, PASS."""

        PASS = "pass"
        FAIL = "fail"

    class ReplaceFlag(Enum):
        """Enum with the following options: ALL, ONLY_FILE."""

        NO_REPLACEMENT = "0"
        ONLY_FILE = "1"
        ALL = "2"

    def __init__(self, analysis_id, comm):
        """Context object that interfaces with the QMENTA platform.
        Should not be created directly.
        """
        self.analysis_id = analysis_id
        self.__comm = comm
        self.__containers_data = {}
        self.analysis_data = None
        self.parent_analysis_data = None
        self.__initial_retry_wait_time = 0.01  # seconds
        self.__max_upload_retries = 5
        self.logger = logging.getLogger(__name__)
        self.__initial_chunk_retry_wait_time = (
            0.25  # seconds, TODO: remove when URL upload is fixed
        )
        self.__max_chunk_retries = 8

    def fetch_analysis_data(self):
        """Fetch information about current analysis.

        Returns
        -------
        dict
            Dictionary that contains important information about the current
            analysis, such as:
                * state (str) : State of the analysis
                * name (str) : Name of the analysis
                * script_name (str) : Name of the script
                * analysis_id (str) : A unique identifier for the analysis
                * user_id (str) : Username of the user that started analysis
                * patient_secret_name (str) : Name of the subject
                * ssid (str) : Timepoint identifier
                * settings (dict) : Settings dictionary.
                * tags (list) : List of tags
                * version (str) : Tool version
        """
        res = self.__comm.send_request(
            "analysis_manager/get_analysis_list", {"id": self.analysis_id}
        )
        if res:
            self.analysis_data = res[0]
            self.analysis_data["analysis_id"] = str(self.analysis_id)
            return self.analysis_data
        else:
            error_msg = "Analysis with ID={} not found".format(
                self.analysis_id
            )
            raise ValueError(error_msg)

    def fetch_parent_analysis_data(self):
        """Fetch information about the parent analysis of current analysis.

        Returns
        -------
        dict
            Dictionary that contains important information about the current
            analysis, such as:
                * state (str) : State of the analysis
                * name (str) : Name of the analysis
                * script_name (str) : Name of the script
                * user_id (str) : Username of the user that started analysis
                * patient_secret_name (str) : Name of the subject
                * ssid (str) : Timepoint identifier
                * settings (dict) : Settings dictionary.
                * tags (list) : List of tags
                * version (str) : Tool version
        """
        if self.parent_analysis_data is not None:
            return self.parent_analysis_data

        if not self.has_parent_analysis():
            raise Exception(
                "The current analysis does not have parent analysis !"
            )

        parent_analysis_id = self.analysis_data["super_analysis"][
            "parent_analysis_id"
        ]

        res = self.__comm.send_request(
            "analysis_manager/get_analysis_list", {"id": parent_analysis_id}
        )
        if res:
            self.parent_analysis_data = res[0]

            # fetching the full state of a flow
            res_state = self.__comm.send_request(
                "analysis_manager/get_super_analysis_state",
                {"analysis_id": parent_analysis_id},
            )

            self.parent_analysis_data["nodes"] = (
                res_state.get("data", dict()) if res_state else dict()
            )

            return self.parent_analysis_data
        else:
            error_msg = "Analysis flow with ID={} not found".format(
                parent_analysis_id
            )
            raise ValueError(error_msg)

    def get_communication_object(self):
        """Return the communication object used for communication with
        platform.

        Returns
        -------
        CommunicationObject
            The communication object used to communicate the platform
        """
        return self.__comm

    def set_qc_status(
        self,
        status=QCStatus.PASS,
        comments="",
        entity=QCEntity.ANALYSIS,
        input_id=None,
    ):
        """Changes the analysis or session QC status.

        Parameters
        ----------
        status : QCStatus
            QCStatus.PASS or QCStatus.FAIL
        comments : str, optional
            Additional comments explaining why the QC status has been set to
            pass or fail.
        entity : QCEntity, optional
            QCEntity.ANALYSIS or QCEntity.SESSION
        input_id : str, optional
            The id of the session in the settings definition when entity is
            QCEntity.SESSION
        """
        if entity == self.QCEntity.ANALYSIS:
            item_id = self.analysis_id
        elif entity == self.QCEntity.SESSION:
            container_id = self.analysis_data["settings"][input_id][
                "container_id"
            ]
            res = self.__comm.send_request(
                "file_manager/get_container_files",
                {"container_id": container_id},
            )
            item_id = str(int(res["patient_id"]))
        else:
            raise RuntimeError("Unknown entity {}".format(entity))

        data_to_send = {
            "item_ids": item_id,
            "status": status.value,
            "comments": comments,
            "entity": entity.value,
        }

        self.logger.info(
            "Setting ({}={}) QC status to {}: {}".format(
                entity.name, item_id, status, comments
            )
        )

        res = self.__comm.send_request(
            "projectset_manager/set_qa_status", data_to_send
        )
        if not res["success"]:
            raise RuntimeError(res["error"])

    def get_qc_status(self, analysis=False):
        """Gets the session QC status.

        Parameters
        ----------
        analysis: bool
            to get analysis QC
        """
        qa_status, qa_comments = None, None
        if not analysis:
            data_sessions = self.__comm.send_request(
                "patient_manager/get_patient_list",
                req_headers={"X-Range": "items=0-9999"},
                req_data={
                    "pars_patient_secret_name": "string"
                    ";{}".format(self.analysis_data['patient_secret_name'])
                },
            )
            self.logger.info(data_sessions[0])
            self.logger.info(
                "Getting QC for {patient_secret_name} / {ssid}".format(
                    **self.analysis_data
                )
            )
            for session in data_sessions:
                ssid = session["ssid"]
                self.logger.info(
                    "Matches QC for {} / {}?".format(
                        self.analysis_data["patient_secret_name"], ssid
                    )
                )

                if str(self.analysis_data["ssid"]) == str(ssid):
                    self.logger.info(session)
                    qa_status = session["qa_status"]
                    qa_comments = session["qa_comments"]
                    break

        if analysis:
            data_analyses = self.__comm.send_request(
                "analysis_manager/get_analysis_list",
                req_headers={"X-Range": "items=0-9999"},
                req_data={
                    "secret_name": self.analysis_data["patient_secret_name"]
                },
            )
            try:
                for analysis in data_analyses:
                    if analysis["_id"] == self.analysis_id:
                        self.logger.info(
                            f"Found analysis / {analysis}, getting QC."
                        )
                        qa_data = analysis["qa_data"]["new_value"]
                        qa_status = qa_data.split("<b>")[1].split("</b>")[
                            0
                        ]  # `fail` or `pass`
                        qa_comments = qa_data.split("<br/>")[1]
                        break
            except Exception as e:
                # Handle other potential exceptions
                self.logger.info(f"An error occurred: {e}")
        return qa_status, qa_comments

    def download_session_qa_requirements(self, path):
        """Downloads the list of project-level requirements for a session.

        Parameters
        ----------
        path : str
            The location where to store the requirements.r
        """
        if os.path.exists(path):
            raise RuntimeError(
                "Cannot download session qa because {} already exists!".format(
                    path
                )
            )

        data_to_send = {"project_id": self.analysis_data["projectset_id"]}

        url = "projectset_manager/get_session_qa_requirements"
        res = self.__comm.send_request(url, data_to_send)
        if not res["success"]:
            raise RuntimeError("Cannot download the session QA requirements")
        else:
            self.logger.info(
                "Storing project-level session QA requirements at {}".format(
                    path
                )
            )
            with open(path, "w") as fs:
                # Process as JSON to validate
                json.dump(res["data"], fs)

    def upload_session_qa_report(self, input_id, path):
        """Sets the QA status for all the files of session as per requirements.

        Parameters
        ----------
        input_id : str
            Identifier "id" of the input container in advanced settings.
        path : str
            The json file with the QA status for all files and rules
        """
        with open(path, "r") as fp:
            # Load as JSON to verify structure
            data = json.loads(fp.read())

        container_id = self.analysis_data["settings"][input_id]["container_id"]
        data_to_send = {"container_id": container_id, "data": json.dumps(data)}
        self.logger.info(
            "Sending session QA report with id {}:\n{}".format(
                data_to_send["container_id"], data_to_send["data"]
            )
        )

        res = self.__comm.send_request(
            "file_manager/set_session_qa", data_to_send
        )
        if not res["success"]:
            raise RuntimeError(res["error"])

    def set_progress(self, message=None, value=None):
        """Sets analysis progress.

        Parameters
        ----------
        value : int, optional
            Number between 0 and 100 indicating the current status of execution
        message : str, optional
            Progress message.
        """
        if not value and not message:
            self.logger.warning(
                "No information is available to report the progress"
            )
            return

        data_to_send = {"analysis_id": self.analysis_id}

        if value:
            value = int(value)  # Cast to int to avoid float/string problems
            if value > 100:
                self.logger.warning(
                    "The progress value should be between 0 and 100 "
                    "(using 100 instead)"
                )
                value = 100
            elif value < 0:
                self.logger.warning(
                    "The progress value should be between 0 and 100 "
                    "(using 0 instead)"
                )
                value = 0
            data_to_send["value"] = value

        if message:
            data_to_send["message"] = message

        self.logger.info("Progress: {} -> {}".format(value, message))
        self.__comm.send_request(
            "analysis_manager/set_analysis_progress", data_to_send
        )

    def get_settings(self):
        """Analysis settings.

        Returns
        -------
        dict
            Settings for the current analysis. This includes all the parameters
            defined in the tool specification (checkboxes, input fields, etc.)
            and can be accessed using their identifier.
        """
        return self.analysis_data["settings"]

    def get_files(
        self,
        input_id,
        modality=None,
        tags=None,
        reg_expression=None,
        file_filter_condition_name=None,
        subject_container_id=None,
    ):
        """Returns files in input container specified by `input_id` that match.

        Returns files that match the modality, tags and regular expression, if
        any. (X)OR that are selected by the file filter condition defined in
        the tool settings.

        Parameters
        ----------
        input_id : str
            Identifier "id" of the input container in advanced settings.
        modality : str, optional
            Optional modality, will allow any modalities if None given.
            Default is None.
        tags : set, optional
            Optional set of tags, will allow any tags if None given, and will
            match any set of tags (including the empty set) otherwise.
            Default is None.
        reg_expression : str, optional
            Regular expression to match with the file names in the specified
            container, will allow any file names if None given.
            Default is None.
        file_filter_condition_name : str, optional
            File filter specified in the settings of the tool.
            Default is None.
        subject_container_id : str, optional

        Examples
        --------
        Get all files that passed c_TEST (including any selection the user may
        have done using the GUI)

        >>> context.get_files('input', file_filter_condition_name='c_TEST')

        Get all files that passed c_TEST and have no tags

        >>> context.get_files('input', file_fitler_condition_name='c_TEST',
        ...                   tags=set())

        Get all files that passed c_TEST and have the DTI tag in their list of
        tags

        >>> context.get_files('input', file_fitler_condition_name='c_TEST',
        ...                   tags={'DTI'})

        Get all files that passed c_TEST whose name match the given regexp

        >>> context.get_files('input', file_filter_condition_name='c_TEST',
        ...                  reg_expression='^some_expression[0-9]')

        Alternatively, you can use no file_filter_condition_name to browse
        through the whole input container

        >>> context.get_files('input')

        Returns
        -------
        list of qmenta.sdk.context.File
            List of selected file handlers from the container.
        """
        self.logger.info(
            "Get files: {} [modality={} / tags={} / regex={}]".format(
                input_id, modality, tags, reg_expression
            )
        )

        file_filter_condition_name = file_filter_condition_name or ""

        input_settings = self.analysis_data["settings"][input_id]
        is_subject_setting = "containers" in input_settings
        container_id = (
            subject_container_id
            if is_subject_setting
            else input_settings["container_id"]
        )

        if is_subject_setting and subject_container_id is None:
            msg = (
                "must define subject_container_id for subjects "
                "with multiple sessions"
            )
            self.logger.error(msg)
            raise Exception(msg)

        if is_subject_setting:
            # get input settings for correct container
            try:
                all_input_setting = [
                    r
                    for r in input_settings["containers"]
                    if r["container_id"] == container_id
                ]
                input_settings = all_input_setting[0]
            except KeyError:
                msg = "container {} not found for input {!r}".format(
                    container_id, input_id
                )
                self.logger.exception(msg)
                raise Exception(msg)

            # ensure data structure is compatible with expected data
            if input_id not in self.__containers_data:
                self.__containers_data[input_id] = {}

            have_container_data = (
                container_id in self.__containers_data[input_id]
            )

        else:
            have_container_data = input_id in self.__containers_data

        if not have_container_data:
            # If files from the file container are not available, fetch them
            res = self.__comm.send_request(
                "file_manager/get_container_files",
                {"container_id": container_id},
            )

            if is_subject_setting:
                self.__containers_data[input_id][container_id] = res["data"]
            else:
                self.__containers_data[input_id] = res["data"]

        container_data_to_work_with = self.__containers_data[input_id]
        if is_subject_setting:
            container_data_to_work_with = self.__containers_data[input_id][
                container_id
            ]

        if file_filter_condition_name:
            # Get the files that passed the file_filter and take those that
            # have the required conditions
            selected_files = []

            if input_settings["passed"]:
                try:
                    file_filter_spec = input_settings["filters"][
                        file_filter_condition_name
                    ]
                except KeyError:
                    msg = "File filter condition {} not specified in the \
                    container {} settings !".format(
                        file_filter_condition_name, input_id
                    )
                    self.logger.error(msg)
                    raise Exception(msg)

                for file_desc in file_filter_spec["files"]:
                    metadata = container_data_to_work_with["meta"]
                    find_file_data = [
                        f for f in metadata if f["name"] == file_desc["name"]
                    ]
                    if find_file_data:
                        file_data = find_file_data[0]

                        fname, fmetadata, ftags = (
                            file_data["name"],
                            file_data["metadata"],
                            set(file_data["tags"]),
                        )

                        if _should_include_file(
                            fname,
                            fmetadata.get("modality", None),
                            ftags,
                            modality,
                            tags,
                            reg_expression,
                        ):
                            selected_files.append(
                                File(
                                    container_id,
                                    fname,
                                    fmetadata,
                                    ftags,
                                    self.__comm,
                                )
                            )

            return selected_files
        else:
            # in case the file filter condition name is not specified then we
            # need to take the other concrete search conditions i.e.
            # modality, tags, reg_expression

            # filter the files according to the filter defined
            return self.__files_from_container_data(
                container_data_to_work_with,
                container_id,
                modality,
                tags,
                reg_expression,
            )

    def _get_files_from_container(
        self, container_id, modality=None, tags=None, reg_expression=None
    ):
        self.logger.info("Get files from container {}".format(container_id))
        res = self.__comm.send_request(
            "file_manager/get_container_files", {"container_id": container_id}
        )
        if res["success"]:
            return self.__files_from_container_data(
                res["data"], container_id, modality, tags, reg_expression
            )
        else:
            raise RuntimeError(res["error"])

    def __files_from_container_data(
        self, container_data, container_id, modality, tags, reg_expression
    ):
        selected_files = []
        for file_data in container_data["meta"]:

            # TODO: Here we are assuming that file metadata has a name and a
            # metadata attribute. Need of jsonschema

            fname, fmetadata, ftags = (
                file_data["name"],
                file_data["metadata"],
                set(file_data["tags"]),
            )
            assume_file_selected = _should_include_file(
                fname,
                fmetadata.get("modality", None),
                ftags,
                modality,
                tags,
                reg_expression,
            )

            if assume_file_selected:
                selected_files.append(
                    File(container_id, fname, fmetadata, ftags, self.__comm)
                )
        return selected_files

    @staticmethod
    def __detect_file_format(file_path):
        if file_path.endswith(".nii"):
            return "nifti"
        elif file_path.endswith(".nii.gz"):
            return "nifti"
        elif file_path.endswith(".bvec"):
            return "bvec"
        elif file_path.endswith(".bval"):
            return "bval"
        else:
            return None

    def new_scan_session(
        self,
        ssid=None,
        date_at_scan=None,
        age_at_scan=None,
        backup_age=None,
        patient_metadata_id=None,
    ):
        """Add a new scan session.

        Only functional for analysis tools of type `data`.

        Parameters
        ----------
        ssid : int, optional
        date_at_scan : str, optional
            Possible formats: '%d.%m.%Y' / '%Y-%m-%d'.
            Examples: '01.01.2000' / '2000-01-01'
        age_at_scan : int, optional
        backup_age : int, optional
        patient_metadata_id : int, optional

        Returns
        -------
        int
            ID of the new scan session
        """
        try:
            patient_secret_name = self.analysis_data["patient_secret_name"]
        except KeyError:
            raise RuntimeError(
                "Patient secret name not available in analysis information. "
                "Check platform failures."
            )
        try:
            md5_original_file = self.get_settings()["md5_original_file"]
        except KeyError:
            raise RuntimeError(
                "MD5 hash not available via analysis settings. "
                "Check platform failures."
            )

        data = {
            "patient_secret_name": patient_secret_name,
            "md5_original_file": md5_original_file,
            "date_at_scan": date_at_scan,
            "age_at_scan": age_at_scan,
            "backup_age": backup_age,
            "analysis_id": self.analysis_id,
        }

        if ssid is not None:
            data["ssid"] = ssid

        if patient_metadata_id:
            data["patient_metadata_id"] = patient_metadata_id

        reply = self.__comm.send_request(
            "patient_manager/add_scan_session", data
        )

        if reply["success"]:
            return reply["data"]
        else:
            raise Exception(reply["error"])

    @staticmethod
    def __valid_upload_response(response, accumulated_bytes, total_bytes):
        """Files are sent chunk by chunk.

        Backend returns first a string per chunk and a JSON when the upload
        is completed (last chunk)
        Example:
          Response chunk 0:     0-524287/10485760 (str)
          Response chunk 1:     0-1048575/10485760 (str)
          ...
          Response chunk N-1:   0-9961471/10485760 (str)
          Response chunk N:     {"success": 1} (json)
        TODO: remove when upload via URL is working again
        """
        logger = logging.getLogger(__name__)

        try:
            if accumulated_bytes == total_bytes:  # Final chunk
                if response.json()["success"]:
                    return True
                else:
                    raise RuntimeError("Final chunk upload failed")
            else:  # Intermediate chunk
                expected_response = "0-{}/{}".format(
                    accumulated_bytes - 1, total_bytes
                )
                if response.text == expected_response:
                    return True
                else:
                    raise RuntimeError(
                        "Intermediate chunk upload \
                          failed: {!r} != {!r}".format(
                            response.text, expected_response
                        )
                    )
        except Exception as e:
            logger.error(
                "Error when loading upload response: {!r} -> {!r}".format(
                    response.text, e
                )
            )
            return False

    @staticmethod
    def __file_md5(path):
        BLOCKSIZE = 65536
        hasher = hashlib.md5()
        with open(path, "rb") as fp:
            buf = fp.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = fp.read(BLOCKSIZE)
        return b64encode(hasher.digest())

    def __validate_upload_response(self, response, total_bytes, md5_hash):
        if response.status_code != 200:
            self.logger.error(
                "Upload returned status code {}".format(response.status_code)
            )
            return False

        upload_manifest = response.json()
        if int(upload_manifest["size"]) != int(total_bytes):
            self.logger.error(
                "Upload size mismatch: {} != {}".format(
                    upload_manifest["size"], total_bytes
                )
            )
            return False

        if upload_manifest["md5Hash"] != md5_hash:
            self.logger.error(
                "MD5 hash mismatch: {} != {}".format(
                    upload_manifest["md5Hash"], md5_hash
                )
            )
            return False

        return True

    def upload_file(
        self,
        source_file_path,
        destination_path,
        modality=None,
        tags=None,
        file_info=None,
        file_format=None,
        protocol=None,
        container_id=None,
        replace=None,
        direct=True,
    ):
        """Upload a file to the platform, to be part of the result files.

        Parameters
        ----------
        source_file_path : str
            Path to the file to be uploaded.
        destination_path : str
            Path in the output container. Will be shown in the platform.
        modality: str, optional
            Optional modality of the uploaded file.
            None by default.
        tags : set, optional
            Set of tags for the uploaded file.
            None by default.
        file_info : dict, optional
            File information metadata.
        file_format : str, optional
            Use "dicom" when .zip file with .dcm slices (uploading a "nifti"
            file is automatically recognized as such).
        protocol : str, optional
        container_id : str, optional
        replace : str, optional
        direct : bool
        """
        tags = tags or set()
        # File information
        source_file_path = str(source_file_path)
        destination_path = str(destination_path)
        file_name = destination_path.split("/")[-1]
        total_bytes = os.path.getsize(source_file_path)

        self.logger.info(
            "Requesting upload URL to upload {!r} to {!r}".format(
                source_file_path, destination_path
            )
        )
        if not total_bytes > 0:
            self.logger.warning(
                "Skipping empty file {} upload".format(source_file_path)
            )
            return

        if modality:
            tags.add("m:" + modality)

        if replace:
            assert isinstance(replace, AnalysisContext.ReplaceFlag)
        else:
            replace = (
                AnalysisContext.ReplaceFlag.NO_REPLACEMENT
            )  # Try to find a proper file format when not available

        if not direct:
            session_id = str(uuid.uuid4())
            # make direct upload to bucket until URL is fixed
            chunk_num = 0
            with open(source_file_path, "rb") as file_object:
                chunk_retry_count = 0
                wait_time = self.__initial_chunk_retry_wait_time
                data = file_object.read(self.__comm.chunk_size)
                # If chunk num is 0, we still want to send an empty file
                while (
                    data or chunk_num == 0
                ) and chunk_retry_count <= self.__max_chunk_retries:
                    start_position = chunk_num * self.__comm.chunk_size
                    self.logger.debug(
                        "Chunk size is {}".format(self.__comm.chunk_size)
                    )
                    end_position = start_position + self.__comm.chunk_size - 1
                    bytes_to_send = self.__comm.chunk_size

                    if end_position >= total_bytes:
                        end_position = total_bytes - 1
                        bytes_to_send = (
                            total_bytes - chunk_num * self.__comm.chunk_size
                        )

                    bytes_range = "bytes {}-{}/{}".format(
                        start_position, end_position, total_bytes
                    )

                    # Request headers
                    req_headers = {
                        "Content-Type": "application/octet-stream",
                        "Content-Range": bytes_range,
                        "Session-ID": str(session_id),
                        "Content-Length": str(bytes_to_send),
                        "Content-Disposition": "attachment; "
                        "filename={}".format(file_name),
                    }

                    # If it is the last chunk, define more header fields
                    accumulated_bytes = (
                        chunk_num * self.__comm.chunk_size + bytes_to_send
                    )
                    if accumulated_bytes == total_bytes:
                        self.logger.debug("Sending last data chunk")
                        req_headers.update(
                            {
                                "X-Mint-Analysis-Output": str(
                                    self.analysis_id
                                ),
                                "X-Mint-File-Destination-Pat\
                                    h": destination_path,
                                "X-Mint-File-Tags": ",".join(tags),
                            }
                        )

                        # Conditional headers
                        if file_info:
                            req_headers["X-Mint-File-Info"] = json.dumps(
                                file_info
                            )
                        if file_format:
                            req_headers["X-Mint-File-Format"] = str(
                                file_format
                            )
                        if protocol:
                            req_headers["X-Mint-Protocol"] = str(protocol)
                        if container_id:
                            req_headers["X-Mint-Container"] = str(container_id)
                        if replace:
                            assert isinstance(
                                replace, AnalysisContext.ReplaceFlag
                            )
                            req_headers["X-Mint-Replace-Flag"] = replace.value
                        req_headers["X-Requested-With"] = "XMLHttpRequest"

                    # Send data chunk
                    response = self.__comm.send_request(
                        "upload", data, req_headers, return_json=False
                    )

                    # Verify upload
                    if self.__valid_upload_response(
                        response, accumulated_bytes, total_bytes
                    ):
                        # Read next chunk
                        data = file_object.read(self.__comm.chunk_size)
                        chunk_num += 1
                        chunk_retry_count = 0
                        wait_time = self.__initial_chunk_retry_wait_time
                    else:
                        chunk_retry_count += 1
                        wait_time = 2 * wait_time
                        time.sleep(wait_time)

                if (
                    data or chunk_retry_count != 0
                ):  # Restarted when successful upload
                    msg = (
                        "File {} could not be uploaded to the platform.\n"
                        "data - {}\n"
                        "chunk_retry_count - {}".format(
                            source_file_path, data, chunk_retry_count
                        )
                    )
                    self.logger.error(msg)
                    raise RuntimeError(msg)
                else:
                    self.logger.info("Upload completed")

        else:
            request_data = {
                "type": "analysis_output",
                "size": total_bytes,
                "path": destination_path,
                "analysis_id": self.analysis_id,
                "replace_flag": replace.value,
                "tags": ",".join(tags),
                "metadata": {"info": json.dumps(file_info)},
                "file_format": str(
                    file_format or self.__detect_file_format(source_file_path)
                ),
                "protocol": str(
                    protocol or file_name.split(".")[0]
                    if "." in file_name
                    else file_name
                ),
                "container_id": container_id,
            }
            url_request_response = self.__comm.send_request(
                "file_manager/get_upload_url", req_data=request_data
            )

            if (
                not url_request_response["success"]
                or "url" not in url_request_response
            ):
                self.logger.error("Error when requesting upload URL")
                self.logger.error("Request data: {}".format(request_data))
                self.logger.error(
                    "Returned error: {}".format(
                        url_request_response.get("error", None)
                    )
                )
                raise RuntimeError("Failed Upload")

            signed_url = url_request_response["url"]
            container_id = url_request_response["container_id"]

            md5_hash = self.__file_md5(source_file_path).decode()

            # Stream file to signed-url without loading it to memory
            completed_upload = False
            retry_count = 0
            wait_time = self.__initial_retry_wait_time
            while (
                not completed_upload
                and retry_count < self.__max_upload_retries
            ):
                with open(source_file_path, "rb") as fp:
                    upload_response = self.__comm.send_request(
                        method="POST",
                        url=signed_url,
                        req_data=fp,
                        return_json=False,
                    )

                # Verify upload
                if self.__validate_upload_response(
                    upload_response, total_bytes, md5_hash
                ):
                    completed_upload = True
                else:
                    retry_count += 1
                    if retry_count < self.__max_upload_retries:
                        wait_time = 2 * wait_time
                        time.sleep(wait_time)
                        self.logger.warning(
                            "Retrying upload (#{}) in {}".format(
                                retry_count, wait_time
                            )
                        )

            if not completed_upload:
                msg = "File {} could not be uploaded to the platform".format(
                    source_file_path
                )
                self.logger.error(msg)
                raise RuntimeError(msg)

            verification_response = self.__comm.send_request(
                "file_manager/verify_upload_via_url",
                req_data={
                    "container_id": container_id,
                    "path": destination_path,
                    "md5": md5_hash,
                },
            )
            if not verification_response.get("success", False):
                msg = "The upload could not be verified: {}".format(
                    verification_response.get("error")
                )
                self.logger.error(msg)
                raise RuntimeError(msg)
            else:
                self.logger.info("Upload verified")

    def download_resource(self, resource_path, destination_path):
        """Downloads a resource file from the bucket.

        Downloads user/group based resources, or legacy.

        Parameters
        ----------
        resource_path : str
            Path to the file in the resources bucket.
        destination_path : str
            Path where the file will be downloaded.
        """
        self.logger.info(
            "Downloading resource {!r} to {!r}".format(
                resource_path, destination_path
            )
        )

        data_to_send = {
            "analysis_id": self.analysis_id,
            "type": type,
            "path": resource_path,
        }
        try:
            res = self.__comm.send_request(
                "analysis_manager/get_resource",
                data_to_send,
                total_retry=1,
                return_json=False,
                stream=True,
            )
        except HTTPError as ex:
            self.logger.exception(ex)
            if ex.response.status_code == 404:
                msg = "Resource file {!r} not found".format(resource_path)
                self.logger.error(msg)
                raise Exception(msg)

            raise

        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        self.logger.debug("Saving {!r}".format(destination_path))
        with open(destination_path, "wb") as fp:
            for chunk in res.iter_content(chunk_size=self.__comm.chunk_size):
                if chunk:  # filter out keep-alive new chunks
                    fp.write(chunk)
                    fp.flush()
        self.logger.debug(
            "Finished downloading resource {!r}".format(destination_path)
        )

    def _get_manual_analysis_data(self):
        """Returns manual analysis data generated during manual step.

        Returns
        -------
        dict
            The values generated during the manual step (user interaction).
        """
        self.logger.info("Getting manual analysis data")

        data_to_send = {"analysis_id": self.analysis_id}
        try:
            res = self.__comm.send_request(
                "analysis_manager/get_manual_analysis_data",
                data_to_send,
                total_retry=1,
            )
        except HTTPError as ex:
            self.logger.exception(ex)
            if ex.response.status_code == 404:
                msg = "Manual analysis data not found (request exception)"
                self.logger.error(msg)
                raise Exception(msg)
            raise
        else:
            self.logger.info(res)
            return res["value"]

    def set_metadata_value(
        self,
        key,
        value,
        title=None,
        readonly=False,
        patient_secret_name=None,
        ssid=None,
    ):
        """Sets the value of a metadata parameter.

        Parameters
        ----------
        key : str
            The ID of the metadata parameter.
        value : int, str, float or list
            The new content of the parameter.
        title : str, optional
            How the metadata field should be presented
        readonly : bool, optional
            Whether the user should be able to edit the value on the platform
            or not (only by analyses)
        patient_secret_name : str, optional
            Manually select the patient_secret_name
        ssid : str, optional
            Manually select the ssid. This is useful to choose a specific
            session in a longitudinal analysis.
        """
        if not isinstance(key, str):
            raise Exception("Parameter 'key' must be of type 'str'.")
        result = re.findall(r"[^a-zA-Z0-9_\s]", key)
        if result:
            raise Exception(
                f"Special characters not accepted: {', '.join(result)}"
            )
        if not isinstance(value, (int, list, str, float)):
            raise Exception(
                "Parameter 'value' must be of type 'int', 'list', 'str', "
                "or 'float'."
            )

        if not self.get_metadata_value(key):
            # Create the metadata field if it does not exist
            if title:
                assert isinstance(title, str)

            allowed_types = {
                int: "integer",
                list: "list",
                str: "string",
                float: "decimal",
            }

            if type(value) not in allowed_types:
                raise ValueError(
                    "Invalid type for the metadata value: {!r}".format(
                        type(value)
                    )
                )
            parameter_type = allowed_types[type(value)]
            self._assure_metadata_parameters(
                [
                    {
                        "key": key,
                        "title": title if title else key,
                        "type": parameter_type,
                        "readonly": int(readonly),
                    }
                ]
            )

        self.logger.info(
            "Setting metadata parameter: {} = {!r}".format(key, value)
        )

        data_to_send = {
            "analysis_id": self.analysis_id,
            "key": key,
            "value": value,
            "patient_secret_name": patient_secret_name
            or self.analysis_data["patient_secret_name"],
            "ssid": ssid or self.analysis_data["ssid"],
        }

        try:
            res = self.__comm.send_request(
                "analysis_manager/set_metadata_value",
                data_to_send,
                total_retry=1,
            )
            if not res["success"]:
                msg = "Metadata error: {!r}".format(res["error"])
                self.logger.error(msg)
                raise Exception(msg)
        except HTTPError as ex:
            self.logger.exception(ex)
            raise

    def get_metadata_value(
        self, key=None, patient_secret_name=None, ssid=None
    ):
        """Gets the value of a metadata parameter for the current session.

        Parameters
        ----------
        key : str, optional
            The ID of the metadata parameter. If not set, it will return all
            the metadata for the session.
        patient_secret_name: str, optional
            Manually select the patient_secret_name
        ssid : str, optional
            Manually select the ssid. This is useful to choose a specific
            session in a longitudinal analysis.

        Returns
        -------
        The value of the parameter if it exists, raises otherwise
        """
        self.logger.info(
            "Getting value from field with id {} from subject {}/{}".format(
                key, patient_secret_name, ssid
            )
        )

        data_to_send = {
            "analysis_id": self.analysis_id,
            "ssid": ssid or self.analysis_data["ssid"],
            "patient_secret_name": patient_secret_name
            or self.analysis_data["patient_secret_name"],
        }

        if key is not None:
            data_to_send["key"] = key

        try:
            res = self.__comm.send_request(
                "analysis_manager/get_metadata_value",
                data_to_send,
                total_retry=1,
            )
            if not res["success"]:
                if "error" in res and "no metadata field" in res["error"]:
                    raise ValueError("Metadata field is empty or not found.")
                else:
                    msg = "Metadata error: {!r}".format(res["error"])
                    self.logger.error(msg)
                    raise RuntimeError(msg)
        except HTTPError as ex:
            self.logger.exception(ex)
            raise
        else:
            if res.get("value", None) is not None:
                return res["value"]
            else:
                raise ValueError("Metadata field is empty or not found.")

    def _assure_metadata_parameters(self, params):
        """Ensure that a parameter exists.

        Parameters
        ----------
        params : list
            The definition of the parameter. It may contain "title", "type",
            "visible", "readonly" or "order".
        """
        if not isinstance(params, list):
            params = list(params)

        for data_to_send in params:
            if not isinstance(data_to_send, dict):
                msg = (
                    "Format error. Metadata param configuration should be "
                    "stored in a dictionary"
                )
                self.logger.error(msg)
                raise TypeError(msg)

            data_to_send["analysis_id"] = self.analysis_id
            self.logger.info(
                "Checking metadata param config: {}".format(data_to_send)
            )
            try:
                res = self.__comm.send_request(
                    "analysis_manager/set_metadata_param",
                    data_to_send,
                    total_retry=1,
                )
                if not res["success"]:
                    msg = "Metadata error: {!r}".format(res["error"])
                    self.logger.error(msg)
                    raise Exception(msg)
            except HTTPError as ex:
                self.logger.exception(ex)
                raise

    # For multi-timepoint (longitudinal) analyses
    def get_sessions(self, input_id):
        input_data = self.analysis_data["settings"][input_id]
        try:
            containers = input_data["containers"]
        except KeyError:
            msg = "settings for {!r} must be from a subject"
            self.logger.error(msg)
            raise Exception(msg)
        else:
            return [
                Container(self, input_id, container_data)
                for container_data in containers
            ]

    def has_parent_analysis(self):
        return "super_analysis" in self.analysis_data

    def get_parent_files_from_input_id(self, input_id):
        if not self.has_parent_analysis():
            raise Exception(
                "The current analysis does not have parent analysis !"
            )

        filters_settings = (
            self.fetch_parent_analysis_data()
            .get("settings", dict())
            .get(input_id, dict())
            .get("filters", dict())
            .items()
        )
        selected_files = set()
        for filter_name, filter_content in filters_settings:
            if not filter_content["passed"]:
                continue
            for ff in filter_content.get("files", []):
                selected_files.add(ff["name"])

        return list(selected_files)

    def set_analysis_output_variables(
        self, variables_dict, clear_previous=False
    ):
        """Sets the output variables of analysis.

        Parameters
        ----------
        variables_dict : str
            Dictionary with the output variables
        clear_previous : bool, optional
            Whether the previous output variables should be cleared or not
        """
        if not isinstance(variables_dict, dict):
            self.logger.error(
                "The output variables are not of type dictionary ! "
                "(actual type {})".format(str(type(variables_dict)))
            )
            raise RuntimeError(
                "The output variables are not of type dictionary !"
            )

        variables_to_send = json.dumps(variables_dict)

        try:
            data_to_send = {
                "output": variables_to_send,
                "clear": int(clear_previous),
                "analysis_id": self.analysis_id,
            }

            res = self.__comm.send_request(
                "analysis_manager/set_output_variables",
                data_to_send,
                total_retry=2,
            )
            if not res["success"]:
                msg = "Setting output variables: {!r}".format(res["error"])
                self.logger.error(msg)
                raise Exception(msg)
        except HTTPError as ex:
            self.logger.exception(ex)
            raise

    def get_session_owner(self, input_id):
        """Get session owner.

        Parameters
        ----------
        input_id: str
            ID of the container used as input in the analysis

        Returns
        -------
        Owner information
        """
        self.logger.info(f"Getting value for owner of container {input_id}.")
        return self.__comm.send_request(
            "file_manager/get_container_files",
            self.analysis_data["settings"][input_id],
        )["owner"]


class Container:
    # is a kind of session, no other kinds of session currently implemented

    def __init__(self, context, input_id, container_data):
        self.__container_id = container_data.get("container_id", None)
        self.__input_id = input_id
        self.__context = context

        self.container_data = container_data

    def get_metadata(self):
        return self.__context._get_metadata_value(None)

    def get_files(
        self,
        modality=None,
        tags=None,
        reg_expression=None,
        file_filter_condition_name=None,
    ):
        return self.__context.get_files(
            self.__input_id,
            modality,
            tags,
            reg_expression,
            file_filter_condition_name,
            self.__container_id,
        )

    def _set_metadata_value(self, key, value):
        return self.__context._set_metadata_value(
            key,
            value,
            self.container_data["subject_name"],
            self.container_data["ssid"],
        )


class File:
    def __init__(self, container_id, name, metadata, tags, comm):
        """Object that represents a file and all its metadata in the platform.

        Should not be created directly.
        """
        self.__comm = comm
        self.__container_id = container_id
        self.name = name
        self.__metadata = metadata
        self.__tags = tags
        self.__download_path = None
        self.logger = logging.getLogger(__name__)

    def get_file_modality(self):
        """Get the modality of the file.

        Returns
        -------
        str or None
            Modality of the file or None if not known.
        """
        return self.__metadata.get("modality", None)

    def get_file_format(self):
        """Get the format of the file (e.g. 'nifti', 'txt', etc.).

        Returns
        -------
        str
            File format or None if not known.
        """
        return self.__metadata.get("format", None)

    def get_file_info(self):
        """Get the file information.

        The type of information depends on the type of file (e.g. nifti files
        include information such as 'Data strides', 'Data type', 'Dimensions'
        or 'Voxel size').

        Returns
        -------
        dict
            Dictionary of key-value pairs that depend on the format of file.
        """
        return self.__metadata.get("info", {})

    def get_file_tags(self):
        """Get the file tags.

        Returns
        -------
        set
            Set of tags associated to this file
        """
        return self.__tags if self.__tags is not None else set()

    def get_file_path(self):
        """Get the file download path.

        Returns
        -------
        str
            The path of the file where it has been downloaded

        Raises
        ------
        RuntimeError
            If `get_file_path` is called before the file has been downloaded
        """
        if self.__download_path is None:
            err_msg = (
                "File {!r} has no path because it has not been "
                "downloaded".format(self.name)
            )
            self.logger.error(err_msg)
            raise RuntimeError(err_msg)
        else:
            return self.__download_path

    def __download_file(self, destination_file_path):
        """Downloads the file into the specified `destination_file_path`.

        Parameters
        ----------
        destination_file_path : str
            Path where the file should be downloaded.
        """
        source_file = self.name

        self.logger.info(
            "Downloading {!r} to {!r}".format(
                source_file, destination_file_path
            )
        )

        data_to_send = {
            "container_id": self.__container_id,
            "files": source_file,
        }
        self.logger.debug(
            "Accessing {files!r} from container {container_id!r}".format(
                **data_to_send
            )
        )
        url_response = self.__comm.send_request(
            access_point="file_manager/download_file_via_url",
            req_data=data_to_send,
            return_json=True,
            stream=False,
        )

        if "data" not in url_response or len(url_response["data"]) != 1:
            raise RuntimeError(
                "Cannot download file via URL: {error_message}".format(
                    error_message=url_response.get("error", "No error message")
                )
            )
        presigned_entry = url_response["data"][0]  # Only one file
        if not isinstance(presigned_entry, dict):
            self.logger.info("Presigned URL {!r}".format(presigned_entry))
            presigned_entry = json.loads(presigned_entry)

        url = presigned_entry["url"]
        download_response = self.__comm.send_request(
            url=url, return_json=False, stream=True, method="GET"
        )

        os.makedirs(os.path.dirname(destination_file_path), exist_ok=True)
        with open(destination_file_path, "wb") as fp:
            # For Google Cloud Bucket, performance is at its best at 1 MB or
            # larger chunks.
            for chunk in download_response.iter_content(
                chunk_size=self.__comm.chunk_size
            ):  # Use 10 MB chunk
                if chunk:  # filter out keep-alive new chunks
                    fp.write(chunk)
                    fp.flush()  # Avoid using too much RAM by flushing to disk

        self.__download_path = destination_file_path
        self.logger.debug(
            "Finished downloading {!r}".format(destination_file_path)
        )

    def download(self, dest_path, unpack=True):
        """Downloads a file or the contents of a packed file.

        Parameters
        ----------
        dest_path:
            Path where the file should be downloaded to.
        unpack:
            Tells the function whether the file should be unpacked to the
            given folder.

        Returns
        -------
        str:
            The full path of the file or the folder with the unpacked files.
        """
        source_file = self.name

        # Normalize path
        dest_path = os.path.abspath(dest_path)

        self.logger.debug("Using path {!r}".format(dest_path))

        if source_file.endswith(".zip") and unpack:
            # Download the zip to a temporary directory and unpack its contents
            # to the user dir path
            with TemporaryDirectory() as temp_dir:
                temp_path = os.path.join(temp_dir, source_file)
                self.__download_file(temp_path)
                with zipfile.ZipFile(temp_path, "r") as zip_ref:
                    os.makedirs(dest_path, exist_ok=True)
                    zip_ref.extractall(path=dest_path)

            self.__download_path = (
                dest_path  # Replace download path with directory
            )
            return dest_path

        # Download the file to the directory and return the full path
        else:
            destination_file_path = os.path.join(dest_path, source_file)
            self.__download_file(destination_file_path)
            return destination_file_path


""" HELPERS """


def _should_include_file(
    fname,
    fmodality,
    ftags,
    search_modality,
    search_tags,
    search_reg_expression,
):
    """Checks if file should be selected or not according to specified
    selectors."""
    assert fname

    if search_modality is not None and fmodality != search_modality:
        return False

    # Search with tags has three outcomes:
    # 1. None - No filter (take all)
    # 2. Empty set - Take only those with no tags
    # 3. Set with elements - Take those with AT LEAST those tags
    if search_tags is not None:
        assert isinstance(ftags, set)
        assert isinstance(search_tags, set)
        if search_tags == set() and ftags != set():
            return False
        elif not search_tags.issubset(ftags):
            return False

    # If regexp, filter with it
    if search_reg_expression is not None:
        if not re.match(search_reg_expression, fname):
            return False

    return True
