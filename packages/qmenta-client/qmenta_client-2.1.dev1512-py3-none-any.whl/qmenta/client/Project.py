from __future__ import print_function

import hashlib
import json
import logging
import os
import re
import sys
import time
from collections import defaultdict
from enum import Enum
from qmenta.core import errors
from qmenta.core import platform

from qmenta.client import Account

if sys.version_info[0] == 3:
    # Note: this branch & variable is only needed for python 2/3 compatibility
    unicode = str

logger_name = "qmenta.client"
OPERATOR_LIST = ["eq", "ne", "gt", "gte", "lt", "lte"]
ANALYSIS_NAME_EXCLUDED_CHARACTERS = [
    "\\",
    "[",
    "]",
    "(",
    ")",
    "{",
    "}",
    "+",
    "*",
]


def convert_qc_value_to_qcstatus(value):
    """
    Convert input string to QCStatus class.

    Parameters
    ----------
    value : str
        Value to convert.

    Returns
    -------
    QCStatus or Bool
        QCStatus.PASS, QCStatus.FAIL or QCStatus.UNDETERMINED.
        False if the Value cannot be convered.
    """
    logger = logging.getLogger(logger_name)
    if value == "pass":
        return QCStatus.PASS
    elif value == "fail":
        return QCStatus.FAIL
    elif value == "":
        return QCStatus.UNDERTERMINED
    else:
        logger.error(
            f"The input value '{value}' cannot be converted to class QCStatus."
        )
        return False


class QCStatus(Enum):
    """
    Enum with the following options:
    FAIL, PASS, UNDERTERMINED
    that are the possible options for the QA/QC status of both
    analysis and session.
    """

    PASS = "pass"
    FAIL = "fail"
    UNDERTERMINED = ""


class Project:
    """
    This class is used to work with QMENTA projects.
    The class is instantiated passing as argument a Connection
    object and the id

    :param account: A QMENTA Account instance
    :type account: qmenta.client.Account

    :param project_id: The ID (or name) of the project you want to work with
    :type project_id: Int or string

    """

    """ Project Related Methods """

    def __init__(self, account: Account, project_id, max_upload_retries=5):
        # if project_id is a string (the name of the project), get the
        # project id (int)
        if isinstance(project_id, str):
            project_name = project_id
            project_id = next(
                iter(
                    filter(
                        lambda proj: proj["name"] == project_id,
                        account.projects,
                    )
                )
            )["id"]
        else:
            if isinstance(project_id, float):
                project_id = int(project_id)
            project_name = next(
                iter(
                    filter(
                        lambda proj: proj["id"] == project_id, account.projects
                    )
                )
            )["name"]

        self._account = account
        self._project_id = project_id
        self._project_name = project_name

        # Max upload retries
        self.max_retries = max_upload_retries

        # Set the passed project ID as the Active one
        self._set_active(project_id)

        # Cache
        self._subjects_metadata = None

    def _set_active(self, project_id):
        """
        Set the active project.

        Parameters
        ----------
        project_id : str
            Project identifier.

        Returns
        -------
        bool
            True if the project was correctly set, False otherwise.
        """
        logger = logging.getLogger(logger_name)
        try:
            platform.parse_response(
                platform.post(
                    self._account.auth,
                    "projectset_manager/activate_project",
                    data={"project_id": int(project_id)},
                )
            )
        except errors.PlatformError:
            logger.error("Unable to activate the project.")
            return False

        logger.info("Successfully changed project")
        self._project_id = project_id
        return True

    def __repr__(self):
        rep = "<Project {}>".format(self._project_name)
        return rep

    """ Upload / Download Data Related Methods """

    def _upload_chunk(
        self,
        data,
        range_str,
        length,
        session_id,
        disposition,
        last_chunk,
        name="",
        date_of_scan="",
        description="",
        subject_name="",
        ssid="",
        filename="DATA.zip",
        input_data_type="mri_brain_data:1.0",
        result=False,
        add_to_container_id=0,
        split_data=False,
        mock_response=False,
    ):
        """
        Upload a chunk of a file to the platform.

        Parameters
        ----------
        data
            The file chunk to upload
        range_str
            The string to send that describes the content range
        length
            The content length of the chunk to send
        session_id
            The session ID from the file path
        filename
            The name of the file to be sent
        disposition
            The disposition of the content
        last_chunk
            Set this only for the last chunk to be uploaded.
            All following parameters are ignored when False.
        split_data
            Sets the header that informs the platform to split
            the uploaded file into multiple sessions.
        """

        request_headers = {
            "Content-Type": "application/zip",
            "Content-Range": range_str,
            "Session-ID": str(session_id),
            "Content-Length": str(length),
            "Content-Disposition": disposition,
        }
        if mock_response:
            request_headers["mock_case"] = mock_response

        if last_chunk:
            request_headers["X-Mint-Name"] = name
            request_headers["X-Mint-Date"] = date_of_scan
            request_headers["X-Mint-Description"] = description
            request_headers["X-Mint-Patient-Secret"] = subject_name
            request_headers["X-Mint-SSID"] = ssid
            request_headers["X-Mint-Filename"] = filename
            request_headers["X-Mint-Project-Id"] = str(self._project_id)
            request_headers["X-Mint-Split-Data"] = str(int(split_data))

            if input_data_type:
                request_headers["X-Mint-Type"] = input_data_type

                if result:
                    request_headers["X-Mint-In-Out"] = "out"
                else:
                    request_headers["X-Mint-In-Out"] = "in"

            if add_to_container_id > 0:
                request_headers["X-Mint-Add-To"] = str(add_to_container_id)

            request_headers["X-Requested-With"] = "XMLHttpRequest"

        response_time = 900.0 if last_chunk else 120.0
        response = platform.post(
            auth=self._account.auth,
            endpoint="upload",
            data=data,
            headers=request_headers,
            timeout=response_time,
        )
        return response

    def upload_file(
        self,
        file_path,
        subject_name,
        ssid="",
        date_of_scan="",
        description="",
        result=False,
        name="",
        input_data_type="qmenta_medical_image_data:3.10",
        add_to_container_id=0,
        chunk_size=2**9,
        max_retries=10,
        split_data=False,
        mock_response=False,
    ):
        """
        Upload a ZIP file to the platform.

        Parameters
        ----------
        file_path : str
            Path to the ZIP file to upload.
        subject_name : str
            Subject ID of the data to upload in the project in QMENTA Platform.
        ssid : str
            Session ID of the Subject ID (i.e., ID of the timepoint).
        date_of_scan : str
            Date of scan/creation of the file
        description : str
            Description of the file
        result : bool
            If result=True then the upload will be taken as an offline analysis
        name : str
            Name of the file in the platform
        input_data_type : str
            qmenta_medical_image_data:3.11
        add_to_container_id : int
            ID of the container to which this file should be added (if id > 0)
        chunk_size : int
            Size in kB of each chunk. Should be expressed as
            a power of 2: 2**x. Default value of x is 9 (chunk_size = 512 kB)
        split_data : bool
            If True, the platform will try to split the uploaded file into
            different sessions. It will be ignored when the ssid or a
            add_to_container_id are given.

        Returns
        -------
        bool
            True if correctly uploaded, False otherwise.
        """
        filename = os.path.split(file_path)[1]
        input_data_type = "offline_analysis:1.0" if result else input_data_type

        chunk_size *= 1024

        name = name or os.path.split(file_path)[1]

        total_bytes = os.path.getsize(file_path)

        split_data = self.__assert_split_data(
            split_data, ssid, add_to_container_id
        )

        # making chunks of the file and sending one by one
        logger = logging.getLogger(logger_name)
        with open(file_path, "rb") as file_object:

            file_size = os.path.getsize(file_path)
            if file_size == 0:
                logger.error("Cannot upload empty file {}".format(file_path))
                return False
            uploaded = 0
            session_id = self.__get_session_id(file_path)
            chunk_num = 0
            retries_count = 0
            uploaded_bytes = 0
            response = None
            last_chunk = False
            error_message = None

            while True:
                data = file_object.read(chunk_size)
                if not data:
                    break

                start_position = chunk_num * chunk_size
                end_position = start_position + chunk_size - 1
                bytes_to_send = chunk_size

                if end_position >= total_bytes:
                    last_chunk = True
                    end_position = total_bytes - 1
                    bytes_to_send = total_bytes - uploaded_bytes

                bytes_range = (
                    "bytes "
                    + str(start_position)
                    + "-"
                    + str(end_position)
                    + "/"
                    + str(total_bytes)
                )

                dispstr = f"attachment; filename={filename}"
                response = self._upload_chunk(
                    data,
                    bytes_range,
                    bytes_to_send,
                    session_id,
                    dispstr,
                    last_chunk,
                    name,
                    date_of_scan,
                    description,
                    subject_name,
                    ssid,
                    filename,
                    input_data_type,
                    result,
                    add_to_container_id,
                    split_data,
                    mock_response=mock_response,
                )
                if response is None:
                    retries_count += 1
                    time.sleep(retries_count * 5)
                    if retries_count > max_retries:
                        error_message = "HTTP Connection Problem"
                        break
                elif int(response.status_code) == 201:
                    chunk_num += 1
                    retries_count = 0
                    uploaded_bytes += chunk_size
                elif int(response.status_code) == 200:
                    self.__show_progress(file_size, file_size, finish=True)
                    break
                elif int(response.status_code) == 416:
                    retries_count += 1
                    time.sleep(retries_count * 5)
                    if retries_count > self.max_retries:
                        error_message = (
                            "Error Code: 416; Requested Range "
                            "Not Satisfiable (NGINX)"
                        )
                        break
                else:
                    retries_count += 1
                    time.sleep(retries_count * 5)
                    if retries_count > max_retries:
                        error_message = (
                            "Number of retries has been reached. "
                            "Upload process stops here !"
                        )
                        break

                uploaded += chunk_size
                self.__show_progress(uploaded, file_size)
        if error_message is not None:
            raise Exception(error_message)
        try:
            platform.parse_response(response)
        except errors.PlatformError as error:
            logger.error(error)
            return False

        message = (
            "Your data was successfully uploaded. "
            "The uploaded file will be soon processed !"
        )
        logger.info(message)
        return True

    def delete_file(self, container_id, filenames):
        """
        Delete a file or files from a container.
        Can be an input or an output container

        Parameters
        ----------
        container_id : int
        filenames : str or list of str

        """
        if not isinstance(filenames, str):
            if isinstance(filenames, list):
                if not all([isinstance(f, str) for f in filenames]):
                    raise TypeError("Elements of `filenames` must be str")
                filenames = ";".join(filenames)
            else:
                raise TypeError("`filenames` must be str or list of str")

        platform.post(
            self._account.auth,
            "file_manager/delete_files",
            data={"container_id": container_id, "files": filenames},
        )

    def upload_mri(self, file_path, subject_name):
        """
        Upload new MRI data to the subject.

        Parameters
        ----------
        file_path : str
            Path to the file to upload
        subject_name: str

        Returns
        -------
        bool
            True if upload was correctly done, False otherwise.
        """

        if self.__check_upload_file(file_path):
            return self.upload_file(file_path, subject_name)

    def upload_gametection(self, file_path, subject_name):
        """
        Upload new Gametection data to the subject.

        Parameters
        ----------
        file_path : str
            Path to the file to upload
        subject_name: str

        Returns
        -------
        bool
            True if upload was correctly done, False otherwise.
        """

        if self.__check_upload_file(file_path):
            return self.upload_file(
                file_path,
                subject_name,
                input_data_type="parkinson_gametection",
            )
        return False

    def upload_result(self, file_path, subject_name):
        """
        Upload new result data to the subject.

        Parameters
        ----------
        file_path : str
            Path to the file to upload
        subject_name: str

        Returns
        -------
        bool
            True if upload was correctly done, False otherwise.
        """

        if self.__check_upload_file(file_path):
            return self.upload_file(file_path, subject_name, result=True)
        return False

    def download_file(
        self, container_id, file_name, local_filename=False, overwrite=False
    ):
        """
        Download a single file from a  specific container.

        Parameters
        ----------
        container_id : str
            ID of the container inside which the file is.
        file_name : str
            Name of the file in the container.
        local_filename : str
            Name of the file to be created. By default, the same as file_name.
        overwrite : bool
            Whether to overwrite the file if existing.
        """
        logger = logging.getLogger(logger_name)
        if not isinstance(file_name, str):
            raise ValueError(
                "The name of the file to download (file_name) should be of "
                "type string."
            )
        if not isinstance(local_filename, str):
            raise ValueError(
                "The name of the output file (local_filename) should be of "
                "type string."
            )

        if file_name not in self.list_container_files(container_id):
            msg = (
                f'File "{file_name}" does not exist in container '
                f"{container_id}"
            )
            raise Exception(msg)

        local_filename = local_filename or file_name

        if os.path.exists(local_filename) and not overwrite:
            msg = f"File {local_filename} already exists"
            raise Exception(msg)

        params = {"container_id": container_id, "files": file_name}
        with platform.post(
            self._account.auth,
            "file_manager/download_file",
            data=params,
            stream=True,
        ) as response, open(local_filename, "wb") as f:

            for chunk in response.iter_content(chunk_size=2**9 * 1024):
                f.write(chunk)
            f.flush()

        logger.info(
            f"File {file_name} from container {container_id} saved "
            f"to {local_filename}"
        )
        return True

    def download_files(
        self, container_id, filenames, zip_name="files.zip", overwrite=False
    ):
        """
        Download a set of files from a given container.

        Parameters
        ----------
        container_id : int
            ID of the container inside which the file is.
        filenames : list[str]
            List of files to download.
        overwrite : bool
            Whether to overwrite the file if existing.
        zip_name : str
            Name of the zip where the downloaded files are stored.
        """
        logger = logging.getLogger(logger_name)

        if not all([isinstance(file_name, str) for file_name in filenames]):
            raise ValueError(
                "The name of the files to download (filenames) should be "
                "of type string."
            )
        if not isinstance(zip_name, str):
            raise ValueError(
                "The name of the output ZIP file (zip_name) should be "
                "of type string."
            )

        files_not_in_container = list(
            filter(
                lambda f: f not in self.list_container_files(container_id),
                filenames,
            )
        )

        if files_not_in_container:
            msg = (
                f"The following files are missing in container "
                f"{container_id}: {', '.join(files_not_in_container)}"
            )
            raise Exception(msg)

        if os.path.exists(zip_name) and not overwrite:
            msg = f'File "{zip_name}" already exists'
            raise Exception(msg)

        params = {"container_id": container_id, "files": ";".join(filenames)}
        with platform.post(
            self._account.auth,
            "file_manager/download_file",
            data=params,
            stream=True,
        ) as response, open(zip_name, "wb") as f:

            for chunk in response.iter_content(chunk_size=2**9 * 1024):
                f.write(chunk)
            f.flush()

        logger.info(
            "Files from container {} saved to {}".format(
                container_id, zip_name
            )
        )
        return True

    def copy_container_to_project(self, container_id, project_id):
        """
        Copy a container to another project.

        Parameters
        ----------
        container_id : int
            ID of the container to copy.
        project_id : int or str
            ID of the project to retrieve, either the numeric ID or the name

        Returns
        -------
        bool
            True on success, False on fail
        """

        if type(project_id) is int or type(project_id) is float:
            p_id = int(project_id)
        elif type(project_id) is str:
            projects = self._account.projects
            projects_match = [
                proj for proj in projects if proj["name"] == project_id
            ]
            if not projects_match:
                raise Exception(
                    f"Project {project_id}"
                    + " does not exist or is not available for this user."
                )
            p_id = int(projects_match[0]["id"])
        else:
            raise TypeError("project_id")
        data = {
            "container_id": container_id,
            "project_id": p_id,
        }

        try:
            platform.parse_response(
                platform.post(
                    self._account.auth,
                    "file_manager/copy_container_to_another_project",
                    data=data,
                )
            )
        except errors.PlatformError as e:
            logging.getLogger(logger_name).error(
                "Couldn not copy container: {}".format(e)
            )
            return False

        return True

    """ Subject/Session Related Methods """

    @property
    def subjects(self):
        """
        Return the list of subject names (Subject ID) from the selected
        project.

        :return: a list of subject names
        :rtype: List(Strings)
        """

        subjects = self.subjects_metadata
        names = [s["patient_secret_name"] for s in subjects]
        return list(set(names))

    @property
    def subjects_metadata(self):
        """
        List all subject data from the selected project.

        Returns
        -------
        dict
            A list of dictionary of {"metadata_name": "metadata_value"}
        """
        return self.get_subjects_metadata()

    @property
    def metadata_parameters(self):
        """
        List all the parameters in the subject-level metadata.

        Each project has a set of parameters that define the subjects-level
        metadata. This function returns all these parameters and its
        properties. New subject-level metadata parameters can be creted in the
        QMENTA Platform via the Metadata Manager. The API only allow
        modification of these subject-level metadata parameters via the
        'change_subject_metadata()' method.

        Returns
        -------
        dict[str] -> dict[str] -> x
            dictionary {"param_name":
                 { "order": Int,
                 "tags": [tag1, tag2, ..., ],
                 "title: "Title",
                 "type": "integer|string|date|list|decimal",
                 "visible": 0|1
                 }}
        """
        logger = logging.getLogger(logger_name)
        try:
            data = platform.parse_response(
                platform.post(
                    self._account.auth, "patient_manager/module_config"
                )
            )
        except errors.PlatformError:
            logger.error("Could not retrieve metadata parameters.")
            return None
        return data["fields"]

    def check_subject_name(self, subject_name):
        """
        Check if a given subject name (Subject ID) exists in the selected
        project.

        Parameters
        ----------
        subject_name : str
            Subject ID of the subject to check

        Returns
        -------
        bool
            True if subject name exists in project, False otherwise
        """

        return subject_name in self.subjects

    def get_subject_container_id(self, subject_name, ssid):
        """
        Given a Subject ID and Session ID, return its Container ID.

        Parameters
        ----------
        subject_name : str
            Subject ID of the subject in the project.
        ssid : str
            Session ID of the subject in the project.

        Returns
        -------
        int or bool
            The Container ID of the subject in the project, or False if
            the subject is not found.
        """

        search_criteria = {"s_n": subject_name, "ssid": str(ssid)}
        response = self.list_input_containers(search_criteria=search_criteria)

        for subject in response:
            if (
                subject["patient_secret_name"] == subject_name
                and subject["ssid"] == ssid
            ):
                return subject["container_id"]
        return False

    def get_subject_id(self, subject_name, ssid):
        """
        Given a Subject ID and Session ID, return its Patient ID in the
        project.

        Parameters
        ----------
        subject_name : str
            Subject ID of the subject in the project.
        ssid : str
            Session ID of the subject in the project.

        Returns
        -------
        int or bool
            The ID of the subject in the project, or False if
            the subject is not found.
        """

        for user in self.get_subjects_metadata():
            if user["patient_secret_name"] == str(subject_name) and user[
                "ssid"
            ] == str(ssid):
                return int(user["_id"])
        return False

    def get_subjects_metadata(self, search_criteria=None, items=(0, 9999)):
        """
        List all Subject ID/Session ID from the selected project that meet the
        defined search criteria at a session level.

        Parameters
        ----------
        search_criteria: dict
            Each element is a string and is built using the formatting
            "type;value", or "type;operation|value"
        items : List[int]
            list containing two elements [min, max] that correspond to the
            mininum and maximum range of analysis listed

        Complete search_criteria Dictionary Explanation:

        search_criteria = {
            "pars_patient_secret_name": "string;SUBJECTID",
            "pars_ssid": "integer;OPERATOR|SSID",
            "pars_modalities": "string;MODALITY",
            "pars_tags": "tags;TAGS",
            "pars_age_at_scan": "integer;OPERATOR|AGE_AT_SCAN",
            "pars_[dicom]_KEY": "KEYTYPE;KEYVALUE",
            "pars_PROJECTMETADATA": "METADATATYPE;METADATAVALUE",
            }

        where "pars_patient_secret_name": Applies the search to the
        'Subject ID'.
        SUBJECTID is a comma separated list of strings.
        "pars_ssid": Applies the search to the 'Session ID'.
        SSID is an integer.
        OPERATOR is the operator to apply. One of:
            - Equal: eq
            - Different Than: ne
            - Greater Than: gt
            - Greater/Equal To: gte
            - Lower Than: lt
            - Lower/Equal To: lte

        "pars_modalities": Applies the search to the file 'Modalities'
            available within each Subject ID.
        MODALITY is a comma separated list of string. A session is provided as
            long as one MODALITY is available.
        "pars_tags": Applies the search to the file 'Tags' available within
            each Subject ID and to the subject-level 'Tags'.
        TAGS is a comma separated list of strings. A session is provided as
            long as one tag is available.
        "pars_age_at_scan": Applies the search to the 'age_at_scan' metadata
            field.
        AGE_AT_SCAN is an integer.
        "pars_[dicom]_KEY": Applies the search to the metadata fields
            available within each file. KEY must be one of the
            metadata keys of the files. The full list of KEYS for a given
            file is shown in the QMENTA Platform within the File Information
            of such File.
        KEYTYPE is the type of the KEY. One of:
            - integer
            - decimal
            - string
            - list

            if 'integer' or 'decimal' you must also include an OPERATOR
                (i.e., "integer;OPERATOR|KEYVALUE").
            if 'list' the KEYVALUE should be a semicolon separated list of
                values. (i.e., "list;KEYVALUE1;KEYVALUE2;KEYVALUE3)
                KEYVALUEs must be strings.
        KEYVALUE is the expected value of the KEY.
        "pars_[dicom]_PROJECTMETADATA": Applies to the metadata defined
            within the 'Metadata Manager' of the project.
        PROJECTMETADATA is the ID of the metadata field.
        METADATATYPE is the type of the metadata field. One of:
            - string
            - integer
            - list
            - decimal
            - single_option
            - multiple_option

            if 'integer' or 'decimal' you must also include an OPERATOR
                (i.e., "integer;OPERATOR|METADATAVALUE").
        KEYVALUE is the expected value of the metadata.

        1) Example:
        search_criteria = {
            "pars_patient_secret_name": "string;abide",
            "pars_ssid": "integer;eq|2"
        }

        2) Example:
        search_criteria = {
            "pars_modalities": "string;T1",
            "pars_tags": "tags;flair",
            "pars_[dicom]_Manufacturer": "string;ge",
            "pars_[dicom]_FlipAngle": "integer;gt|5",
            "pars_[dicom]_ImageType": "list;PRIMARY;SECONDARY",
        }

        Note the search criteria applies to all the files included within a
            session. Hence, it does not imply that all the criteria conditions
            are applied to the same files. In example 2) above, it means that
            any Subject ID/Session ID that has a file classified with a 'T1'
            modality, a file with a 'flair' tag, a file whose Manufacturer
            contains 'ge', a file whose FlipAngle is greater than '5º', and a
            file with ImageType with any of the values: PRIMARY or SECONDARY
            will be selected.

        Returns
        -------
        dict
            A list of dictionary of {"metadata_name": "metadata_value"}

        """

        if search_criteria is None:
            search_criteria = {}
        if len(items) != 2:
            raise ValueError(
                f"The number of elements in items '{len(items)}' "
                f"should be equal to two."
            )

        if not all([isinstance(item, int) for item in items]):
            raise ValueError(
                f"All values in items " f"'{items}' must be integers"
            )

        if search_criteria != {} and not all(
            [item.startswith("pars_") for item in search_criteria.keys()]
        ):
            raise ValueError(
                f"All keys of the search_criteria dictionary "
                f"'{search_criteria.keys()}' must start with 'pars_'."
            )

        for key, value in search_criteria.items():
            if value.split(";")[0] in ["integer", "decimal"]:
                assert value.split(";")[1].split("|")[0] in OPERATOR_LIST, (
                    f"Search criteria of type '{value.split(';')[0]}' must "
                    f"include an operator ({', '.join(OPERATOR_LIST)})."
                )

        content = platform.parse_response(
            platform.post(
                self._account.auth,
                "patient_manager/get_patient_list",
                data=search_criteria,
                headers={"X-Range": f"items={items[0]}-{items[1]}"},
            )
        )
        return content

    def change_subject_metadata(
        self, patient_id, subject_name, ssid, tags, age_at_scan, metadata
    ):
        """
        Change the Subject ID, Session ID, Tags, Age at Scan and Metadata of
        the session with Patient ID

        Parameters
        ----------
        patient_id : Integer
            Patient ID representing the session to modify.
        subject_name : String
            Represents the new Subject ID.
        ssid : String
            Represents the new Session ID.
        tags : list of strings in lowercase
            Represents the new tags of the session.
        age_at_scan : Integer
            Represents the new Age at Scan of the Session.
        metadata : Dictionary
            Each pair key/value representing the new metadata values.

            The keys must either all start with "md\\_" or none start
            with "md\\_".

            The key represents the ID of the metadata field.

        Returns
        -------
        bool
            True if correctly modified, False otherwise
        """
        logger = logging.getLogger(logger_name)

        try:
            patient_id = str(int(patient_id))
        except ValueError:
            raise ValueError(
                f"'patient_id': '{patient_id}' not valid. Must be convertible "
                f"to int."
            )

        if not isinstance(tags, list) or not all(
            isinstance(item, str) for item in tags
        ):
            raise ValueError(f"tags: '{tags}' should be a list of strings.")
        tags = [tag.lower() for tag in tags]

        if not isinstance(subject_name, str) or (
            subject_name is None or subject_name == ""
        ):
            raise ValueError("subject_name must be a non empty string.")

        if not isinstance(ssid, str) or (ssid is None or ssid == ""):
            raise ValueError("ssid must be a non empty string.")

        try:
            age_at_scan = str(int(age_at_scan)) if age_at_scan else None
        except ValueError:
            raise ValueError(
                f"age_at_scan: '{age_at_scan}' not valid. Must be an integer."
            )

        if not isinstance(metadata, dict):
            raise ValueError(f"metadata: '{metadata}' should be a dictionary.")

        has_md_prefix = ["md_" == key[:3] for key in metadata.keys()]
        if not (all(has_md_prefix) or not any(has_md_prefix)):
            raise ValueError(
                f"metadata: '{metadata}' must be a dictionary whose keys are "
                f"either all starting with 'md_' or none."
            )

        metadata_keys = self.metadata_parameters.keys()
        if not all(
            (
                key[3:] in metadata_keys
                if "md_" == key[:3]
                else key in metadata_keys
            )
            for key in metadata.keys()
        ):
            raise ValueError(
                f"Some metadata keys provided ({', '.join(metadata.keys())}) "
                "are not available in the project. They can be added via the "
                "Metadata Manager via the QMENTA Platform graphical user "
                "interface (GUI)."
            )

        post_data = {
            "patient_id": patient_id,
            "secret_name": str(subject_name),
            "ssid": str(ssid),
            "tags": ",".join(tags),
            "age_at_scan": age_at_scan,
        }
        for key, value in metadata.items():
            id_ = key[3:] if "md_" == key[:3] else key
            post_data[f"last_vals.{id_}"] = value

        try:
            platform.parse_response(
                platform.post(
                    self._account.auth,
                    "patient_manager/upsert_patient",
                    data=post_data,
                )
            )
        except errors.PlatformError:
            logger.error(f"Patient ID '{patient_id}' could not be modified.")
            return False

        logger.info(f"Patient ID '{patient_id}' successfully modified.")
        return True

    def get_subjects_files_metadata(
        self, search_criteria=None, items=(0, 9999)
    ):
        """
        List all Subject ID/Session ID from the selected project that meet the
            defined search criteria at a file level.

        Note, albeit the search criteria is similar to the one defined in
            method 'get_subjects_metadata()' (see differences below), the
            output is different as this method provides the sessions which
            have a file that satisfy all the conditions of the search criteria.
            This method is slow.

        Parameters
        ----------
        search_criteria: dict
            Each element is a string and is built using the formatting
            "type;value", or "type;operation|value"
        items : List[int]
            list containing two elements [min, max] that correspond to the
            mininum and maximum range of analysis listed

        Complete search_criteria Dictionary Explanation:

        search_criteria = {
            "pars_patient_secret_name": "string;SUBJECTID",
            "pars_ssid": "integer;OPERATOR|SSID",
            "pars_modalities": "string;MODALITY",
            "pars_tags": "tags;TAGS",
            "pars_age_at_scan": "integer;OPERATOR|AGE_AT_SCAN",
            "pars_[dicom]_KEY": "KEYTYPE;KEYVALUE",
            "pars_PROJECTMETADATA": "METADATATYPE;METADATAVALUE",
            }

        Where:
        "pars_patient_secret_name": Applies the search to the 'Subject ID'.
        SUBJECTID is a comma separated list of strings.
        "pars_ssid": Applies the search to the 'Session ID'.
        SSID is an integer.
        OPERATOR is the operator to apply. One of:
            - Equal: eq
            - Different Than: ne
            - Greater Than: gt
            - Greater/Equal To: gte
            - Lower Than: lt
            - Lower/Equal To: lte

        "pars_modalities": Applies the search to the file 'Modalities'
            available within each Subject ID.
        MODALITY is a string.
        "pars_tags": Applies only the search to the file 'Tags' available
            within each Subject ID.
        TAGS is a comma separated list of strings. All tags must be present in
            the same file.
        "pars_age_at_scan": Applies the search to the 'age_at_scan' metadata
            field.
        AGE_AT_SCAN is an integer.
        "pars_[dicom]_KEY": Applies the search to the metadata fields
            available within each file. KEY must be one of the
        metadata keys of the files. The full list of KEYS for a given
            file is shown in the QMENTA Platform within the File Information
            of such File.
        KEYTYPE is the type of the KEY. One of:
            - integer
            - decimal
            - string
            - list

            if 'integer' or 'decimal' you must also include an OPERATOR
                (i.e., "integer;OPERATOR|KEYVALUE").
            if 'list' the KEYVALUE should be a semicolon separated list of
                values. (i.e., "list;KEYVALUE1;KEYVALUE2;KEYVALUE3)
                KEYVALUEs must be strings.
        KEYVALUE is the expected value of the KEY.
        "pars_[dicom]_PROJECTMETADATA": Applies to the metadata defined
            within the 'Metadata Manager' of the project.
        PROJECTMETADATA is the ID of the metadata field.
        METADATATYPE is the type of the metadata field. One of:
            - string
            - integer
            - list
            - decimal
            - single_option
            - multiple_option

            if 'integer' or 'decimal' you must also include an OPERATOR
                (i.e., "integer;OPERATOR|METADATAVALUE").
        KEYVALUE is the expected value of the metadata.

        1) Example:
        search_criteria = {
            "pars_patient_secret_name": "string;abide",
            "pars_ssid": "integer;eq|2"
        }

        2) Example:
        search_criteria = {
            "pars_patient_secret_name": "string;001"
            "pars_modalities": "string;T2",
            "pars_tags": "tags;flair",
            "pars_[dicom]_Manufacturer": "string;ge",
            "pars_[dicom]_FlipAngle": "integer;gt|5",
            "pars_[dicom]_ImageType": "list;PRIMARY;SECONDARY",
        }

        Note the search criteria might apply to both the files metadata
            information available within a session and the metadata of the
            session. And the method provides a session only if all the file
            related conditions are satisfied within the same file.
            In example 2) above, it means that the output will contain any
            session whose Subject ID contains '001', and there is a file with
            modality 'T2', tag 'flair', FlipAngle greater than 5º, and
            ImageType with both values PRIMARY and SECONDARY.
            Further, the acquisition had to be performed in a Manufacturer
            containing 'ge'.

        Returns
        -------
        dict
            A list of dictionary of {"metadata_name": "metadata_value"}

        """

        if search_criteria is None:
            search_criteria = {}
        content = self.get_subjects_metadata(search_criteria, items=items)

        # Wrap search criteria.
        modality, tags, dicom_metadata = self.__wrap_search_criteria(
            search_criteria
        )

        # Iterate over the files of each subject selected to include/exclude
        # them from the results.
        subjects = list()
        for subject in content:
            files = platform.parse_response(
                platform.post(
                    self._account.auth,
                    "file_manager/get_container_files",
                    data={"container_id": str(int(subject["container_id"]))},
                )
            )

            for file in files["meta"]:
                if modality and modality != (file.get("metadata") or {}).get(
                    "modality"
                ):
                    continue
                if tags and not all([tag in file.get("tags") for tag in tags]):
                    continue
                if dicom_metadata:
                    result_values = list()
                    for key, dict_value in dicom_metadata.items():
                        f_value = (
                            (file.get("metadata") or {}).get("info") or {}
                        ).get(key)
                        d_operator = dict_value["operation"]
                        d_value = dict_value["value"]
                        result_values.append(
                            self.__operation(d_value, d_operator, f_value)
                        )

                    if not all(result_values):
                        continue
                subjects.append(subject)
                break
        return subjects

    def get_file_metadata(self, container_id, filename):
        """
        Retrieve the metadata from a particular file in a particular container.

        Parameters
        ----------
        container_id : str
            Container identifier.
        filename : str
            Name of the file.

        Returns
        -------
        dict
            Dictionary with the metadata. False otherwise.
        """
        all_metadata = self.list_container_files_metadata(container_id)
        if all_metadata:
            for file_meta in all_metadata:
                if file_meta["name"] == filename:
                    return file_meta
        else:
            return False

    def change_file_metadata(self, container_id, filename, modality, tags):
        """
        Change modality and tags of `filename` in `container_id`

        Parameters
        ----------
        container_id : int
            Container identifier.
        filename : str
            Name of the file to be edited.
        modality : str or None
            Modality identifier, or None if the file shouldn't have
            any modality
        tags : list[str] or None
            List of tags, or None if the filename shouldn't have any tags
        """

        tags_str = "" if tags is None else ";".join(tags)
        platform.parse_response(
            platform.post(
                self._account.auth,
                "file_manager/edit_file",
                data={
                    "container_id": container_id,
                    "filename": filename,
                    "tags": tags_str,
                    "modality": modality,
                },
            )
        )

    def delete_session(self, subject_name, session_id):
        """
        Delete a session from a subject within a project providing the
        Subject ID and Session ID.

        Parameters
        ----------
        subject_name : str
            Subject ID of the subject
        session_id : str
            The Session ID of the session that will be deleted

        Returns
        -------
        bool
            True if correctly deleted, False otherwise.
        """
        logger = logging.getLogger(logger_name)
        all_sessions = self.get_subjects_metadata()

        session_to_del = [
            s
            for s in all_sessions
            if s["patient_secret_name"] == subject_name
            and s["ssid"] == session_id
        ]

        if not session_to_del:
            logger.error(
                f"Session {subject_name}/{session_id} could not be found in "
                f"this project."
            )
            return False
        elif len(session_to_del) > 1:
            raise RuntimeError(
                "Multiple sessions with same Subject ID and Session ID. "
                "Contact support."
            )
        else:
            logger.info(
                "{}/{} found (id {})".format(
                    subject_name, session_id, session_to_del[0]["_id"]
                )
            )

        session = session_to_del[0]

        try:
            platform.parse_response(
                platform.post(
                    self._account.auth,
                    "patient_manager/delete_patient",
                    data={
                        "patient_id": str(int(session["_id"])),
                        "delete_files": 1,
                    },
                )
            )
        except errors.PlatformError:
            logger.error(
                f"Session \"{subject_name}/{session['ssid']}\" could "
                f"not be deleted."
            )
            return False

        logger.info(
            f"Session \"{subject_name}/{session['ssid']}\" successfully "
            f"deleted."
        )
        return True

    def delete_session_by_patientid(self, patient_id):
        """
        Delete a session from a subject within a project providing the
        Patient ID.

        Parameters
        ----------
        patient_id : str
            Patient ID of the Session ID/Subject ID

        Returns
        -------
        bool
            True if correctly deleted, False otherwise.
        """
        logger = logging.getLogger(logger_name)

        try:
            platform.parse_response(
                platform.post(
                    self._account.auth,
                    "patient_manager/delete_patient",
                    data={
                        "patient_id": str(int(patient_id)),
                        "delete_files": 1,
                    },
                )
            )
        except errors.PlatformError:
            logger.error(f"Patient ID {patient_id} could not be deleted.")
            return False

        logger.info(f"Patient ID {patient_id} successfully deleted.")
        return True

    def delete_subject(self, subject_name):
        """
        Delete a subject from the project. It deletes all its available
        sessions only providing the Subject ID.

        Parameters
        ----------
        subject_name : str
            Subject ID of the subject to be deleted.

        Returns
        -------
        bool
            True if correctly deleted, False otherwise.
        """

        logger = logging.getLogger(logger_name)
        # Always fetch the session IDs from the platform before deleting them
        all_sessions = self.get_subjects_metadata()

        sessions_to_del = [
            s for s in all_sessions if s["patient_secret_name"] == subject_name
        ]

        if not sessions_to_del:
            logger.error(
                "Subject {} cannot be found in this project.".format(
                    subject_name
                )
            )
            return False

        for ssid in [s["ssid"] for s in sessions_to_del]:
            if not self.delete_session(subject_name, ssid):
                return False
        return True

    """ Container Related Methods """

    def list_input_containers(self, search_criteria=None, items=(0, 9999)):
        """
        Retrieve the list of input containers available to the user under a
        certain search criteria.

        Parameters
        ----------
        search_criteria : dict
            Each element is a string and is built using the formatting
        "type;value".

        List of possible keys:
        d_n: container_name # TODO: WHAT IS THIS???
        s_n: subject_id
            Subject ID of the subject in the platform.
        ssid: session_id
            Session ID of the subejct in the platform.
        from_d: from date
            Starting date in which perform the search. Format: DD.MM.YYYY
        to_d: to date
            End date in which perform the search. Format: DD.MM.YYYY
        sets: data sets (modalities)  # TODO: WHAT IS THIS???

        items: Tuple(int, int)
            Starting and ending element of the search.

        Returns
        -------
        dict
        List of containers, each a dictionary containing the following
        information:
            {"container_name", "container_id", "patient_secret_name", "ssid"}
        """

        if search_criteria is None:
            search_criteria = {}
        if len(items) != 2:
            raise ValueError(
                f"The number of elements in items '{len(items)}' "
                f"should be equal to two."
            )
        if not all(isinstance(item, int) for item in items):
            raise ValueError(
                f"All items elements '{items}' should be integers."
            )

        response = platform.parse_response(
            platform.post(
                self._account.auth,
                "file_manager/get_container_list",
                data=search_criteria,
                headers={"X-Range": f"items={items[0]}-{items[1]}"},
            )
        )
        containers = [
            {
                "patient_secret_name": container_item["patient_secret_name"],
                "container_name": container_item["name"],  # ???
                "container_id": container_item["_id"],
                "ssid": container_item["ssid"],
            }
            for container_item in response
        ]
        return containers

    def list_result_containers(self, search_condition=None, items=(0, 9999)):
        """
        List the result containers available to the user.
        Examples
        --------

        >>> search_condition = {
            "secret_name":"014_S_6920",
            "from_d": "06.02.2025",
            "with_child_analysis": 1,
            "state": "completed"
        }
            list_result_containers(search_condition=search_condition)

        Note the keys not needed for the search do not have to be included in
            the search condition.

        Parameters
        ----------
        search_condition : dict
            - p_n: str or None Analysis name
            - type: str or None Type (analysis_code:analysis_version).
            - analysis_code: str or None Type
            - from_d: str or None dd.mm.yyyy Date from
            - to_d: str or None dd.mm.yyyy Date to
            - qa_status: str or None pass/fail/nd QC status
            - secret_name: str or None Subject ID
            - tags: str or None
            - with_child_analysis: 1 or None if 1, child analysis of workflows
            will appear
            - id: str or None ID
            - state: running, completed, pending, exception or None
            - username: str or None

        items : List[int]
            list containing two elements [min, max] that correspond to the
            mininum and maximum range of analysis listed

        Returns
        -------
        dict
            List of containers, each a dictionary
            {"name": "container-name", "id": "container_id"}
            if "id": None, that analysis did not had an output container,
            probably it is a workflow
        """
        if search_condition is None:
            search_condition = {}
        analyses = self.list_analysis(search_condition, items)
        return [
            {
                "name": analysis["name"],
                "id": (analysis.get("out_container_id") or None),
            }
            for analysis in analyses
        ]

    def list_container_files(
        self,
        container_id,
    ):
        """
        List the name of the files available inside a given container.
        Parameters
        ----------
        container_id : str or int
            Container identifier.

        Returns
        -------
        list[str]
            List of file names (strings)
        """
        try:
            content = platform.parse_response(
                platform.post(
                    self._account.auth,
                    "file_manager/get_container_files",
                    data={"container_id": container_id},
                )
            )
        except errors.PlatformError as e:
            logging.getLogger(logger_name).error(e)
            return False
        if "files" not in content.keys():
            logging.getLogger(logger_name).error("Could not get files")
            return False
        return content["files"]

    def list_container_filter_files(
        self, container_id, modality="", metadata_info={}, tags=[]
    ):
        """
        List the name of the files available inside a given container.
        search condition example:
        "metadata": {"SliceThickness":1},
        }
        Parameters
        ----------
        container_id : str or int
            Container identifier.

        modality: str
            String containing the modality of the files being filtered

        metadata_info: dict
            Dictionary containing the file metadata of the files being filtered

        tags: list[str]
            List of strings containing the tags of the files being filtered

        Returns
        -------
        selected_files: list[str]
            List of file names (strings)
        """
        content_files = self.list_container_files(container_id)
        content_meta = self.list_container_files_metadata(container_id)
        selected_files = []
        for index, file in enumerate(content_files):
            metadata_file = content_meta[index]
            tags_file = metadata_file.get("tags")
            tags_bool = [tag in tags_file for tag in tags]
            info_bool = []
            if modality == "":
                modality_bool = True
            else:
                modality_bool = modality == metadata_file["metadata"].get(
                    "modality"
                )
            for key in metadata_info.keys():
                meta_key = (
                    (metadata_file.get("metadata") or {}).get("info") or {}
                ).get(key)
                if meta_key is None:
                    logging.getLogger(logger_name).warning(
                        f"{key} is not in file_info from file {file}"
                    )
                info_bool.append(metadata_info[key] == meta_key)
            if all(tags_bool) and all(info_bool) and modality_bool:
                selected_files.append(file)
        return selected_files

    def list_container_files_metadata(self, container_id):
        """
        List all the metadata of the files available inside a given container.

        Parameters
        ----------
        container_id : str
            Container identifier.

        Returns
        -------
        dict
            Dictionary of {"metadata_name": "metadata_value"}
        """

        try:
            data = platform.parse_response(
                platform.post(
                    self._account.auth,
                    "file_manager/get_container_files",
                    data={"container_id": container_id},
                )
            )
        except errors.PlatformError as e:
            logging.getLogger(logger_name).error(e)
            return False

        return data["meta"]

    """ Analysis Related Methods """

    def get_analysis(self, analysis_name_or_id):
        """
        Returns the analysis corresponding with the analysis id or analysis
        name

        Parameters
        ----------
        analysis_name_or_id : int, str
            analysis_id or analysis name to search for

        Returns
        -------
        analysis: dict
            A dictionary containing the analysis information
        """
        if isinstance(analysis_name_or_id, int):
            search_tag = "id"
        elif isinstance(analysis_name_or_id, str):
            if analysis_name_or_id.isdigit():
                search_tag = "id"
                analysis_name_or_id = int(analysis_name_or_id)
            else:
                search_tag = "p_n"
                excluded_bool = [
                    character in analysis_name_or_id
                    for character in ANALYSIS_NAME_EXCLUDED_CHARACTERS
                ]
                if any(excluded_bool):
                    raise Exception(
                        f"p_n does not allow "
                        f"characters {ANALYSIS_NAME_EXCLUDED_CHARACTERS}"
                    )
        else:
            raise Exception(
                "The analysis identifier must be its name or an integer"
            )

        search_condition = {
            search_tag: analysis_name_or_id,
        }
        response = platform.parse_response(
            platform.post(
                self._account.auth,
                "analysis_manager/get_analysis_list",
                data=search_condition,
            )
        )

        if len(response) > 1:
            raise Exception(
                f"multiple analyses with name {analysis_name_or_id} found"
            )
        elif len(response) == 1:
            return response[0]
        else:
            return None

    def list_analysis(self, search_condition=None, items=(0, 9999)):
        """
        List the analysis available to the user.

        Examples
        --------

        >>> search_condition = {
            "secret_name":"014_S_6920",
            "from_d": "06.02.2025",
            "with_child_analysis": 1,
            "state": "completed"
        }
            list_analysis(search_condition=search_condition)

        Note the keys not needed for the search do not have to be included in
            the search condition.

        Parameters
        ----------
        search_condition : dict
            - p_n: str or None Analysis name
            - type: str or None Type (analysis_code:analysis_version).
            - analysis_code: str or None Type
            - from_d: str or None dd.mm.yyyy Date from
            - to_d: str or None dd.mm.yyyy Date to
            - qa_status: str or None pass/fail/nd QC status
            - secret_name: str or None Subject ID
            - tags: str or None
            - with_child_analysis: 1 or None if 1, child analysis of workflows
            will appear
            - id: int or None ID
            - state: running, completed, pending, exception or None
            - username: str or None
            - only_data: int or None

        items : List[int]
            list containing two elements [min, max] that correspond to the
            mininum and maximum range of analysis listed

        Returns
        -------
        dict
            List of analysis, each a dictionary
        """
        if search_condition is None:
            search_condition = {}
        if len(items) != 2:
            raise ValueError(
                f"The number of elements in items '{len(items)}' "
                f"should be equal to two."
            )
        if not all(isinstance(item, int) for item in items):
            raise ValueError(
                f"All items elements '{items}' should be integers."
            )
        search_keys = {
            "p_n": str,
            "type": str,
            "analysis_code": str,
            "from_d": str,
            "to_d": str,
            "qa_status": str,
            "secret_name": str,
            "tags": str,
            "with_child_analysis": int,
            "id": int,
            "state": str,
            "only_data": int,
            "username": str,
        }
        for key in search_condition.keys():
            if key not in search_keys.keys():
                raise Exception(
                    (
                        f"This key '{key}' is not accepted by this search "
                        f"condition"
                    )
                )
            if (
                not isinstance(search_condition[key], search_keys[key])
                and search_condition[key] is not None
            ):
                raise Exception(
                    (
                        f"The key {key} in the search condition is not type "
                        f"{search_keys[key]}"
                    )
                )
            if "p_n" == key:
                excluded_bool = [
                    character in search_condition["p_n"]
                    for character in ANALYSIS_NAME_EXCLUDED_CHARACTERS
                ]
                if any(excluded_bool):
                    raise Exception(
                        "p_n does not allow "
                        f"characters {ANALYSIS_NAME_EXCLUDED_CHARACTERS}"
                    )
        req_headers = {"X-Range": f"items={items[0]}-{items[1] - 1}"}
        return platform.parse_response(
            platform.post(
                auth=self._account.auth,
                endpoint="analysis_manager/get_analysis_list",
                headers=req_headers,
                data=search_condition,
            )
        )

    def start_analysis(
        self,
        script_name,
        version,
        in_container_id=None,
        analysis_name=None,
        analysis_description=None,
        ignore_warnings=False,
        settings=None,
        tags=None,
        preferred_destination=None,
        ignore_file_selection=True,
    ):
        """
        Starts an analysis on a subject.

        Parameters
        ----------
        script_name : str
            ID of the script to be run.
        version: str
            Version of the script to be run, examples: 1.0, 5.3.4
        in_container_id : int or dict
            The ID of the container to get the data from, or a dictionary with
            one or more container names as keys, and IDs as values.
            Input container names are generally prefixed with "input\\_".
            If not, the prefix will be automatically added.
        analysis_name : str
            Name of the analysis (optional)
        analysis_description : str
            Description of the analysis (optional)
        ignore_warnings : bool
            If False, warnings by server cause failure.
        settings : dict
            The input settings used to run the analysis.
            Use either settings or in_container_id. Input specification
            in the settings dict can be done by using the key "input".
        tags : list[str]
            The tags of the analysis.
        preferred_destination : str
            The machine on which to run the analysis
        ignore_file_selection : Bool
            When the file filter of the analysis is satified by multiple files.
            False if you want to select manually the file to input to the
            analysis. True otherwise and the analysis will cancelled.

        Returns
        -------
        int
            The analysis ID if correctly started, None otherwise.
        """
        logger = logging.getLogger(logger_name)

        if in_container_id is None and settings is None:
            raise ValueError(
                "Pass a value for either in_container_id or settings."
            )

        post_data = {"script_name": script_name, "version": version}

        settings = settings or {}

        if in_container_id:
            if isinstance(in_container_id, dict):
                for key, value in in_container_id.items():
                    if "input" not in key:
                        key = "input_" + key
                    settings[key] = value
            else:
                settings["input"] = str(in_container_id)

        for key in settings:
            post_data["as_" + key] = settings[key]

        # name and description are optional
        if analysis_name:
            post_data["name"] = analysis_name
        if analysis_description:
            post_data["description"] = analysis_description
        if tags:
            if isinstance(tags, list) and len(tags) > 0:
                post_data["tags"] = ",".join(tags)
            elif isinstance(tags, (str, unicode)):
                post_data["tags"] = tags
        if preferred_destination:
            post_data["preferred_destination"] = preferred_destination

        logger.debug(f"post_data = {post_data}")
        return self.__handle_start_analysis(
            post_data,
            ignore_warnings=ignore_warnings,
            ignore_file_selection=ignore_file_selection,
        )

    def delete_analysis(self, analysis_id):
        """
        Delete an analysis

        Parameters
        ----------
        analysis_id : int
            ID of the analysis to be deleted
        """
        logger = logging.getLogger(logger_name)

        try:
            platform.parse_response(
                platform.post(
                    auth=self._account.auth,
                    endpoint="analysis_manager/delete_analysis",
                    data={"project_id": analysis_id},
                )
            )
        except errors.PlatformError as error:
            logger.error("Could not delete analysis: {}".format(error))
            return False

        return True

    def restart_analysis(self, analysis_id):
        """
        Restart an analysis. Only worklows can be restarted, the finished
        tools within the workflow will be kept and the missing ones
        (which probably previously failed) will start. This process maintains
        the flow of the workflow.

        Tools can not be restarted given that they are considered as single
        processing units. You can start execution of another analysis instead.

        For the workflow to restart, all its failed child must be removed
        first. You can only restart your own analysis.

        Parameters
        ----------
        analysis_id : int
            ID of the analysis to be restarted
        """
        logger = logging.getLogger(logger_name)

        analysis = self.list_analysis({"id": analysis_id})[0]

        if analysis.get("super_analysis_type") != 1:
            raise ValueError(
                "The analysis indicated is not a workflow and hence, it "
                "cannot be restarted."
            )

        try:
            platform.parse_response(
                platform.post(
                    auth=self._account.auth,
                    endpoint="analysis_manager/restart_analysis",
                    data={"analysis_id": analysis_id},
                    timeout=1000,
                )
            )
        except errors.PlatformError as error:
            logger.error("Could not delete analysis: {}".format(error))
            return False

        return True

    def get_analysis_log(self, analysis_id, file_name=None):
        """
        Get the log of an analysis and save it in the provided file.
        The logs of analysis can only be obtained for the tools you created.

        Note workflows do not have a log so the printed message will only be
        ERROR.
        You can only download the anlaysis log of the tools that you own.

        Note this method is very time consuming.

        Parameters
        ----------
        analysis_id : int
            ID of the script to be run.
        file_name: str
            Path to the file where to export the log.
            If None the file will be: f'logs_{analysis_id}.txt'

        Returns
        -------
        str or bool
            File name of the exported file if the export is possible.
            False otherwise.
        """
        logger = logging.getLogger(logger_name)
        try:
            analysis_id = str(int(analysis_id))
        except ValueError:
            raise ValueError(
                f"'analysis_id' has to be an integer not '{analysis_id}'."
            )

        file_name = file_name if file_name else f"logs_{analysis_id}.txt"
        try:
            res = platform.post(
                auth=self._account.auth,
                endpoint="analysis_manager/download_execution_file",
                data={
                    "project_id": analysis_id,
                    "file": f"logs_{analysis_id}",
                },
                timeout=1000,
            )
        except Exception:
            logger.error(
                f"Could not export the analysis log of '{analysis_id}'"
            )
            return False

        if not res.ok:
            logger.error(
                f"The log file could not be extracted for Analysis ID:"
                f" {analysis_id}."
            )
            return False

        with open(file_name, "w") as f:
            f.write(res.text)
        return file_name

    """ QC Status Related Methods """

    def set_qc_status_analysis(
        self, analysis_id, status=QCStatus.UNDERTERMINED, comments=""
    ):
        """
        Changes the analysis QC status.

        Parameters
        ----------
        analysis_id : int
            Analysis ID number
        status : QCStatus
            QCStatus.PASS, QCStatus.FAIL or QCStatus.UNDETERMINED
        comments : str, optional
            Additional comments explaining why the reasoning of setting the
            QC status to such state.

        Returns
        -------
        bool
            True if the QC status was correctly changed, False otherwise.
        """

        logger = logging.getLogger(__name__)
        logger.info(f"Setting QC status to {status}: {comments}")

        if not isinstance(status, QCStatus):
            raise ValueError("Status should be type 'QCStatus'.")

        try:
            analysis_id = str(int(analysis_id))
        except ValueError:
            raise ValueError(
                f"analysis_id: '{analysis_id}' not valid. Must be convertible "
                f"to int."
            )

        try:
            platform.parse_response(
                platform.post(
                    auth=self._account.auth,
                    endpoint="projectset_manager/set_qa_status",
                    data={
                        "item_ids": analysis_id,
                        "status": status.value,
                        "comments": str(comments),
                        "entity": "analysis",
                    },
                )
            )
        except Exception:
            logger.error(
                f"It was not possible to change the QC status of Analysis ID:"
                f" {analysis_id}"
            )
            return False
        return True

    def set_qc_status_subject(
        self, patient_id, status=QCStatus.UNDERTERMINED, comments=""
    ):
        """
        Changes the QC status of a Patient ID (equivalent to a
        Subject ID/Session ID).

        Parameters
        ----------
        patient_id : int
            Patient ID number of the session.
        status : QCStatus
            QCStatus.PASS, QCStatus.FAIL or QCStatus.UNDETERMINED
        comments : str, optional
            Additional comments explaining why the reasoning of setting the
            QC status to such state.

        Returns
        -------
        bool
            True if the QC status was correctly changed, False otherwise.
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Setting QC status to {status}: {comments}")

        if not isinstance(status, QCStatus):
            raise ValueError("Status should be type 'QCStatus'.")

        try:
            patient_id = str(int(patient_id))
        except ValueError:
            raise ValueError(
                f"'patient_id': '{patient_id}' not valid. Must be convertible"
                f" to int."
            )

        try:
            platform.parse_response(
                platform.post(
                    auth=self._account.auth,
                    endpoint="projectset_manager/set_qa_status",
                    data={
                        "item_ids": patient_id,
                        "status": status.value,
                        "comments": str(comments),
                        "entity": "patients",
                    },
                )
            )
        except Exception:
            logger.error(
                f"It was not possible to change the QC status of Patient ID:"
                f" {patient_id}"
            )
            return False
        return True

    def get_qc_status_analysis(self, analysis_id):
        """
        Gets the QC status of an anlaysis provided its Analysis ID.

        Parameters
        ----------
        analysis_id : int
            Analysis ID number

        Returns
        -------
        status : QCStatus or False
            QCStatus.PASS, QCStatus.FAIL or QCStatus.UNDETERMINED
            False if the status cannot be extracted.
        comments : str or False
            Comments defined in the QC Status.
            False if the comments cannot be extracted.
        """
        try:
            search_criteria = {"id": analysis_id}
            to_return = self.list_analysis(search_criteria)
            return (
                convert_qc_value_to_qcstatus(to_return[0]["qa_status"]),
                to_return[0]["qa_comments"],
            )
        except IndexError:
            # Handle the case where no matching analysis is found
            logging.error(
                f"No analysis was found with such Analysis ID: "
                f"'{analysis_id}'."
            )
            return False, False
        except Exception:
            # Handle other potential exceptions
            logging.error(
                f"It was not possible to extract the QC status from Analysis "
                f"ID: {analysis_id}"
            )
            return False, False

    def get_qc_status_subject(
        self, patient_id=None, subject_name=None, ssid=None
    ):
        """
        Gets the session QC status via the patient ID or the Subject ID
        and the Session ID.

        Parameters
        ----------
        patient_id : int
            Patient ID number of the session
        subject_name : string
            Subject ID of the session
        ssid : string
            Session ID

        Returns
        -------
        status : QCStatus or False
            QCStatus.PASS, QCStatus.FAIL or QCStatus.UNDETERMINED
            False if the status cannot be extracted.
        comments : str or False
            Comments defined in the QC Status.
            False if the comments cannot be extracted.
        """

        if patient_id:
            try:
                patient_id = int(patient_id)
            except ValueError:
                raise ValueError(
                    f"patient_id '{patient_id}' should be an integer."
                )
            sessions = self.get_subjects_metadata(search_criteria={})
            session = [
                session
                for session in sessions
                if int(session["_id"]) == patient_id
            ]
            if len(session) < 1:
                logging.error(
                    f"No session was found with Patient ID: '{patient_id}'."
                )
                return False, False
            return (
                convert_qc_value_to_qcstatus(session[0]["qa_status"]),
                session[0]["qa_comments"],
            )
        elif subject_name and ssid:
            session = self.get_subjects_metadata(
                search_criteria={
                    "pars_patient_secret_name": f"string;{subject_name}",
                    "pars_ssid": (
                        f"integer;eq|{ssid}"
                        if str(ssid).isdigit()
                        else f"string;{ssid}"
                    ),
                }
            )
            if len(session) < 1:
                logging.error(
                    f"No session was found with Subject ID: '{subject_name}'"
                    f" and Session ID: '{ssid}'."
                )
                return False, False
            return (
                convert_qc_value_to_qcstatus(session[0]["qa_status"]),
                session[0]["qa_comments"],
            )
        else:
            raise ValueError(
                "Either 'patient_id' or 'subject_name' and 'ssid' must "
                "not be empty."
            )

    """ Protocol Adherence Related Methods """

    def set_project_pa_rules(self, rules_file_path, guidance_text=""):
        """
        Updates the active project's protocol adherence rules using the
        provided rules file.

        Parameters
        ----------
            rules_file_path : str
                The file path to the JSON file containing the protocol
                 adherence rules.
            guidance_text : str
                Description of the protocol adherence rules.

        Returns
        -------
            bool: True if the protocol adherence rules were set successfully,
            False otherwise.
        """
        logger = logging.getLogger(logger_name)
        # Read the rules from the JSON file
        try:
            with open(rules_file_path, "r") as fr:
                rules = json.load(fr)
        except FileNotFoundError:
            logger.error(
                f"Protocol adherence rule file '{rules_file_path}' not found."
            )
            return False

        # Update the project's QA rules
        res = platform.parse_response(
            platform.post(
                auth=self._account.auth,
                endpoint="projectset_manager/set_session_qa_requirements",
                data={
                    "project_id": self._project_id,
                    "rules": json.dumps(rules),
                    "guidance_text": guidance_text,
                },
            )
        )

        if not res.get("success") == 1:
            logger.error(
                "There was an error setting up the protocol adherence rules."
            )
            logger.error(platform.parse_response(res))
            return False

        return True

    def get_project_pa_rules(
        self, rules_file_path, project_has_no_rules=False
    ):
        """
        Retrive the active project's protocol adherence rules

        Parameters
        ----------
            rules_file_path : str
                The file path to the JSON file to store the protocol adherence
                rules.
            project_has_no_rules: bool
                for testing purposes

        Returns
        -------
            guidance_text : str
                Description of the protocol adherence rules,
                False if extraction of the protocol adhernece rules is not
                possible.
        """
        logger = logging.getLogger(logger_name)

        # Update the project's QA rules
        res = platform.parse_response(
            platform.post(
                auth=self._account.auth,
                endpoint="projectset_manager/get_session_qa_requirements",
                data={"project_id": self._project_id},
            )
        )

        if "rules" not in res or project_has_no_rules:
            logger.error(
                f"There was an error extracting the protocol adherence rules"
                f" from {self._project_name}."
            )
            logger.error(platform.parse_response(res))
            return False

        try:
            for rule in res["rules"]:
                for key in ["_id", "order", "time_modified"]:
                    if rule.get(key, False):
                        del rule[key]
            with open(rules_file_path, "w") as fr:
                json.dump(res["rules"], fr, indent=4)
        except FileNotFoundError:
            logger.error(
                f"Protocol adherence rules could not be exported to file: "
                f"'{rules_file_path}'."
            )
            return False

        return res["guidance_text"]

    def parse_qc_text(self, patient_id=None, subject_name=None, ssid=None):
        """
        Parse QC (Quality Control) text output into a structured dictionary
        format.

        This function takes raw QC text output (from the Protocol Adherence
        analysis) and parses it into a structured format that
        separates passed and failed rules, along with their associated files
        and conditions.

        Args:
            patient_id (str, optional):
                Patient identifier. Defaults to None.
            subject_name (str, optional):
                Subject/patient name. Defaults to None. Mandatory if no
                patient_id is provided.
            ssid (str, optional):
                Session ID. Defaults to None. Mandatory if subject_name is
                provided.

        Returns:
            dict: A structured dictionary containing a list of dictionaries
            with passed rules and their details and failed rules and their
            details. Details of passed rules are:
            per each rule: Files that have passed the rule. Per each file name
            of the file and number of conditions of the rule. Details of
            failed rules are: per each rule failed conditions: Number of
            times it failed. Each condition status.

        Example:
            >>> parse_qc_text(subject_name="patient_123", ssid=1)
            {
                "passed": [
                    {
                        "rule": "T2",
                        "sub_rule": "rule_15T",
                        "files": [
                            {
                                "file": "path/to/file1",
                                "passed_conditions": 4
                            }
                        ]
                    }
                ],
                "failed": [
                    {
                        "rule": "T1",
                        "files": [
                            {
                                "file": "path/to/file2",
                                "conditions": [
                                    {
                                        "status": "failed",
                                        "condition": "SliceThickness between.."
                                    }
                                ]
                            }
                        ],
                        "failed_conditions": {
                            "SliceThickness between...": 1
                        }
                    }
                ]
            }
        """

        _, text = self.get_qc_status_subject(
            patient_id=patient_id, subject_name=subject_name, ssid=ssid
        )

        result = {"passed": [], "failed": []}

        # Split into failed and passed sections
        sections = re.split(r"={10,}\n\n", text)
        if len(sections) == 3:
            failed_section = sections[1].split("=" * 10)[0].strip()
            passed_section = sections[2].strip()
        else:
            section = sections[1].split("=" * 10)[0].strip()
            if "PASSED QC MESSAGES" in section:
                passed_section = section
                failed_section = ""
            else:
                failed_section = section
                passed_section = ""

        # Parse failed rules
        failed_rules = re.split(r"\n ❌ ", failed_section)
        result = self.__parse_fail_rules(failed_rules, result)

        # Parse passed rules
        passed_rules = re.split(r"\n ✅ ", passed_section)
        result = self.__parse_pass_rules(passed_rules, result)

        return result

    def calculate_qc_statistics(self):
        """
        Calculate comprehensive statistics from multiple QC results across
        subjects from a project in the QMENTA platform.

        This function aggregates and analyzes QC results from
        multiple subjects/containers, providing statistical insights about
        rule pass/fail rates, file statistics, and condition failure patterns.

        Returns:
            dict: A dictionary containing comprehensive QC statistics
            including:
                - passed_rules: Total count of passed rules across all subjects
                - failed_rules: Total count of failed rules across all subjects
                - subjects_passed: Count of subjects with no failed rules
                - subjects_with_failed: Count of subjects with at least one
                failed rule
                - num_passed_files_distribution: Distribution of how many
                rules have N passed files
                - file_stats: File-level statistics (total, passed, failed,
                pass percentage)
                - condition_failure_rates: Frequency and percentage of each
                failed condition
                - rule_success_rates: Success rates for each rule type

        The statistics help identify:
            - Overall QC pass rates
            - Most common failure conditions
            - Rule-specific success rates
            - Distribution of passed files per rule
            - Subject-level pass rates

        Example:
            >>> project.calculate_qc_statistics()
            {
                "passed_rules": 42,
                "failed_rules": 8,
                "subjects_passed": 15,
                "subjects_with_failed": 5,
                "num_passed_files_distribution": {
                    "1": 30,
                    "2": 12
                },
                "file_stats": {
                    "total": 50,
                    "passed": 45,
                    "failed": 5,
                    "pass_percentage": 90.0
                },
                "condition_failure_rates": {
                    "SliceThickness": {
                        "count": 5,
                        "percentage": 62.5
                    }
                },
                "rule_success_rates": {
                    "T1": {
                        "passed": 20,
                        "failed": 2,
                        "success_rate": 90.91
                    }
                }
            }
        """
        qc_results_list = list()
        containers = self.list_input_containers()

        for c in containers:
            qc_results_list.append(
                self.parse_qc_text(
                    subject_name=c["patient_secret_name"], ssid=c["ssid"]
                )
            )

        # Initialize statistics
        stats = {
            "passed_rules": 0,
            "failed_rules": 0,
            "subjects_passed": 0,
            "subjects_with_failed": 0,
            "num_passed_files_distribution": defaultdict(
                int
            ),  # How many rules have N passed files
            "file_stats": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "pass_percentage": 0.0,
            },
            "condition_failure_rates": defaultdict(
                lambda: {"count": 0, "percentage": 0.0}
            ),
            "rule_success_rates": defaultdict(
                lambda: {"passed": 0, "failed": 0, "success_rate": 0.0}
            ),
        }

        total_failures = 0

        # sum subjects with not failed qc message
        stats["subjects_passed"] = sum(
            [1 for rules in qc_results_list if not rules["failed"]]
        )
        # sum subjects with some failed qc message
        stats["subjects_with_failed"] = sum(
            [1 for rules in qc_results_list if rules["failed"]]
        )
        # sum rules that have passed
        stats["passed_rules"] = sum(
            [
                len(rules["passed"])
                for rules in qc_results_list
                if rules["failed"]
            ]
        )
        # sum rules that have failed
        stats["failed_rules"] = sum(
            [
                len(rules["failed"])
                for rules in qc_results_list
                if rules["failed"]
            ]
        )

        for qc_results in qc_results_list:

            # Count passed files distribution
            for rule in qc_results["passed"]:
                num_files = len(rule["files"])
                stats["num_passed_files_distribution"][num_files] += 1
                stats["file_stats"]["passed"] += len(rule["files"])
                stats["file_stats"]["total"] += len(rule["files"])
                rule_name = rule["rule"]
                stats["rule_success_rates"][rule_name]["passed"] += 1

            for rule in qc_results["failed"]:
                stats["file_stats"]["total"] += len(rule["files"])
                stats["file_stats"]["failed"] += len(rule["files"])
                for condition, count in rule["failed_conditions"].items():
                    # Extract just the condition text without actual value
                    clean_condition = re.sub(
                        r"\.\s*Actual value:.*$", "", condition
                    )
                    stats["condition_failure_rates"][clean_condition][
                        "count"
                    ] += count
                    total_failures += count
                rule_name = rule["rule"]
                stats["rule_success_rates"][rule_name]["failed"] += 1

        if stats["file_stats"]["total"] > 0:
            stats["file_stats"]["pass_percentage"] = round(
                (stats["file_stats"]["passed"] / stats["file_stats"]["total"])
                * 100,
                2,
            )

        # Calculate condition failure percentages
        for condition in stats["condition_failure_rates"]:
            if total_failures > 0:
                stats["condition_failure_rates"][condition]["percentage"] = (
                    round(
                        (
                            stats["condition_failure_rates"][condition][
                                "count"
                            ]
                            / total_failures
                        )
                        * 100,
                        2,
                    )
                )

        # Calculate rule success rates
        for rule in stats["rule_success_rates"]:
            total = (
                stats["rule_success_rates"][rule]["passed"]
                + stats["rule_success_rates"][rule]["failed"]
            )
            if total > 0:
                stats["rule_success_rates"][rule]["success_rate"] = round(
                    (stats["rule_success_rates"][rule]["passed"] / total)
                    * 100,
                    2,
                )

        # Convert defaultdict to regular dict for cleaner JSON output
        stats["num_passed_files_distribution"] = dict(
            stats["num_passed_files_distribution"]
        )
        stats["condition_failure_rates"] = dict(
            stats["condition_failure_rates"]
        )
        stats["rule_success_rates"] = dict(stats["rule_success_rates"])

        return stats

    """ Helper Methods """

    def __handle_start_analysis(
        self,
        post_data,
        ignore_warnings=False,
        ignore_file_selection=True,
        n_calls=0,
    ):
        """
        Handle the possible responses from the server after start_analysis.
        Sometimes we have to send a request again, and then check again the
        response. That"s why this function is separated from start_analysis.

        Since this function sometimes calls itself, n_calls avoids entering an
        infinite loop due to some misbehaviour in the server.
        """

        call_limit = 10
        n_calls += 1

        logger = logging.getLogger(logger_name)
        if n_calls > call_limit:
            logger.error(
                f"__handle_start_analysis_response called itself more\
                          than {n_calls} times: aborting."
            )
            return None
        response = None
        try:
            response = platform.parse_response(
                platform.post(
                    self._account.auth,
                    "analysis_manager/analysis_registration",
                    data=post_data,
                )
            )
            logger.info(response["message"])
            return (
                int(response["analysis_id"])
                if "analysis_id" in response
                else None
            )

        except platform.ChooseDataError as choose_data:
            if ignore_file_selection:
                logger.error(
                    "Existence of multiple files satisfying the input data "
                    "requirements and parameter ignore_file_selection==True."
                )
                logger.error(
                    f"Unable to start the analysis: "
                    f"{post_data['script_name']}:"
                    f"{post_data['version']} with input "
                    f"{post_data['as_input']}."
                )
                return None
            has_warning = False

            # logging any warning that we have
            if choose_data.warning:
                has_warning = True
                logger.warning(choose_data.warning)

            new_post = {
                "analysis_id": choose_data.analysis_id,
                "script_name": post_data["script_name"],
                "version": post_data["version"],
            }
            if "tags" in post_data.keys():
                new_post["tags"] = post_data["tags"]

            if choose_data.data_to_choose:
                self.__handle_manual_choose_data(new_post, choose_data)
            else:
                if has_warning and not ignore_warnings:
                    logger.error(
                        "Cancelling analysis due to warnings, set "
                        "'ignore_warnings' to True to override."
                    )
                    new_post["cancel"] = "1"
                else:
                    logger.info("suppressing warnings")
                    new_post["user_preference"] = "{}"
                    new_post["_mint_only_warning"] = "1"

            return self.__handle_start_analysis(
                new_post, ignore_warnings, ignore_file_selection, n_calls
            )
        except platform.ActionFailedError as e:
            logger.error(f"Unable to start the analysis: {e}.")
            return None

    @staticmethod
    def __handle_manual_choose_data(post_data, choose_data):
        """
        Handle the responses of the user when there is need to select a file
        to start the analysis.

        At the moment only supports a manual selection via the command-line
        interface.

        Parameters
        ----------
            post_data : dict
                Current post_data dictionary. To be mofidied in-place.
            choose_data : platform.ChooseDataError
                Error raised when trying to start an analysis, but data has to
                be chosen.
        """

        logger = logging.getLogger(logger_name)
        logger.warning(
            "Multiple inputs available. You have to select the desired file/s "
            "to continue."
        )
        # in case we have data to choose
        chosen_files = {}
        for settings_key in choose_data.data_to_choose:
            logger.warning(
                f"Type next the file/s for the input with ID: "
                f"'{settings_key}'."
            )
            chosen_files[settings_key] = {}
            filters = choose_data.data_to_choose[settings_key]["filters"]
            for filter_key in filters:
                filter_data = filters[filter_key]

                # skip the filters that did not pass
                if not filter_data["passed"]:
                    continue
                elif post_data.get("cancel"):
                    continue

                if filter_data["range"][0] != 0:
                    number_of_files_to_select = filter_data["range"][0]
                elif filter_data["range"][1] != 0:
                    number_of_files_to_select = min(
                        filter_data["range"][1], len(filter_data["files"])
                    )
                else:
                    number_of_files_to_select = len(filter_data["files"])

                # If the files need to be selected automatically based
                # on their file information.
                # Need to apply some filtering criteria at this stage.
                # Based on the information provided by next methods.
                # files_info = list_container_files_metadata() or
                # list_container_filter_files()

                if number_of_files_to_select != len(filter_data["files"]):
                    substring = ""
                    if number_of_files_to_select > 1:
                        substring = "s (i.e., file1.zip, file2.zip, file3.zip)"
                    logger.warning(
                        f"  · File filter name: '{filter_key}'. Type "
                        f"{number_of_files_to_select} file{substring}."
                    )
                    save_file_ids, select_file_filter = {}, ""
                    for file_ in filter_data["files"]:
                        select_file_filter += (
                            f"       · File name: {file_['name']}\n"
                        )
                        save_file_ids[file_["name"]] = file_["_id"]
                    names = [
                        el.strip()
                        for el in input(select_file_filter).strip().split(",")
                    ]

                    if len(names) != number_of_files_to_select:
                        logger.error(
                            "The number of files selected does not correspond "
                            "to the number of needed files."
                        )
                        logger.error(
                            f"Selected: {len(names)} vs. "
                            f"Number of files to select: "
                            f"{number_of_files_to_select}."
                        )
                        logger.error("Cancelling analysis.")
                        post_data["cancel"] = "1"

                    elif any([name not in save_file_ids for name in names]):
                        logger.error(
                            f"Some selected file/s '{', '.join(names)}' "
                            f"do not exist. Cancelling analysis..."
                        )
                        post_data["cancel"] = "1"
                    else:
                        chosen_files[settings_key][filter_key] = [
                            save_file_ids[name] for name in names
                        ]

                else:
                    logger.warning(
                        "Setting all available files to be input to the "
                        "analysis."
                    )
                    files_selection = [
                        ff["_id"]
                        for ff in filter_data["files"][
                            :number_of_files_to_select
                        ]
                    ]
                    chosen_files[settings_key][filter_key] = files_selection

        post_data["user_preference"] = json.dumps(chosen_files)

    @staticmethod
    def __get_modalities(files):
        modalities = []
        for file_ in files:
            modality = file_["metadata"]["modality"]
            if modality not in modalities:
                modalities.append(modality)
        return modalities

    def __show_progress(self, done, total, finish=False):
        bytes_in_mb = 1024 * 1024
        progress_message = "\r[{:.2f} %] Uploaded {:.2f} of {:.2f} Mb".format(
            done / float(total) * 100, done / bytes_in_mb, total / bytes_in_mb
        )
        sys.stdout.write(progress_message)
        sys.stdout.flush()
        if not finish:
            pass
            # sys.stdout.write("")
            # sys.stdout.flush()
        else:
            sys.stdout.write("\n")

    def __get_session_id(self, file_path):
        m = hashlib.md5()
        m.update(file_path.encode("utf-8"))
        return str(time.time()).replace(".", "") + "_" + m.hexdigest()

    def __check_upload_file(self, file_path):
        """
        Check whether a file has the correct extension to upload.

        Parameters
        ----------
        file_path : str
            Path to the file

        Returns
        -------
        bool
            True if correct extension, False otherwise.
        """

        # TODO: Add a file zipper here so zips files in a folder

        file_parts = file_path.split(".")
        extension = file_parts[-1]

        if extension != "zip":
            logging.getLogger(logger_name).error("You must upload a zip.")
            return False
        else:
            return True

    @staticmethod
    def __operation(reference_value, operator, input_value):
        """
        The method performs an operation by comparing the two input values.
        The Operation is applied to the Input Value in comparison to the
        Reference Value.

        Parameters
        ----------
        reference_value : str, list, or int
            Reference value.
        operator : str
            Operation.
        input_value : str, list, or int
            Input value.

        Returns
        -------
        bool
            True if the operation is satisfied, False otherwise.
        """
        if not input_value:  # Handles None, "", and other falsy values
            return False

        operator_actions = {
            "in": lambda: reference_value in input_value,
            "in-list": lambda: all(
                el in input_value for el in reference_value
            ),
            "eq": lambda: input_value == reference_value,
            "gt": lambda: input_value > reference_value,
            "gte": lambda: input_value >= reference_value,
            "lt": lambda: input_value < reference_value,
            "lte": lambda: input_value <= reference_value,
        }

        action = operator_actions.get(operator, lambda: False)
        return action()

    @staticmethod
    def __wrap_search_criteria(search_criteria=None):
        """
        Wraps the conditions specified within the Search Criteria in order for
        other methods to handle it easily. The conditions are grouped only into
        three groups: Modality, Tags and the File Metadata (if DICOM it
        corresponds to the DICOM information), and each of them is output
        in a different variable.

        Parameters
        ----------
        search_criteria : dict
            Each element is a string and is built using the formatting
                "KEYTYPE;VALUE", or "KEYTYPE;OPERATOR|VALUE".

                Full list of keys avaiable for the dictionary:

                search_criteria = {
                    "pars_patient_secret_name": "string;SUBJECTID",
                    "pars_ssid": "integer;OPERATOR|SSID",
                    "pars_modalities": "string;MODALITY",
                    "pars_tags": "tags;TAGS",
                    "pars_age_at_scan": "integer;OPERATOR|AGE_AT_SCAN",
                    "pars_[dicom]_KEY": "KEYTYPE;KEYVALUE",
                    "pars_PROJECTMETADATA": "METADATATYPE;METADATAVALUE",
                    }

                See documentation for a complete definition.

        Returns
        -------
        tuple
            A tuple containing:
            - str: modality is a string containing the modality of the search
            criteria extracted from 'pars_modalities';
            - list: tags is a list of strings containing the tags of the search
            criteria extracted 'from pars_tags',
            - dict: containing the file metadata of the search criteria
            extracted from 'pars_[dicom]_KEY'
        """

        # The keys not included bellow apply to the whole session.
        if search_criteria is None:
            search_criteria = {}
        modality, tags, file_metadata = "", list(), dict()
        for key, value in search_criteria.items():
            if key == "pars_modalities":
                modalities = value.split(";")[1].split(",")
                if len(modalities) != 1:
                    raise ValueError(
                        f"A file can only have one modality. "
                        f"Provided Modalities: {', '.join(modalities)}."
                    )
                modality = modalities[0]
            elif key == "pars_tags":
                tags = value.split(";")[1].split(",")
            elif "pars_[dicom]_" in key:
                d_tag = key.split("pars_[dicom]_")[1]
                d_type = value.split(";")[0]
                if d_type == "string":
                    file_metadata[d_tag] = {
                        "operation": "in",
                        "value": value.replace(d_type + ";", ""),
                    }
                elif d_type == "integer":
                    d_operator = value.split(";")[1].split("|")[0]
                    d_value = value.split(";")[1].split("|")[1]
                    file_metadata[d_tag] = {
                        "operation": d_operator,
                        "value": int(d_value),
                    }
                elif d_type == "decimal":
                    d_operator = value.split(";")[1].split("|")[0]
                    d_value = value.split(";")[1].split("|")[1]
                    file_metadata[d_tag] = {
                        "operation": d_operator,
                        "value": float(d_value),
                    }
                elif d_type == "list":
                    value.replace(d_type + ";", "")
                    file_metadata[d_tag] = {
                        "operation": "in-list",
                        "value": value.replace(d_type + ";", "").split(";"),
                    }
        return modality, tags, file_metadata

    @staticmethod
    def __assert_split_data(split_data, ssid, add_to_container_id):
        """
        Assert if the split_data parameter is possible to use in regards
        to the ssid and add_to_container_id parameters during upload.
        Changes its status to False if needed.

        Parameters
        ----------
        split_data : Bool
            split_data parameter from method 'upload_file'.
        ssid : str
            Session ID.
        add_to_container_id : int or bool
            Container ID or False

        Returns
        -------
        split_data : Bool

        """

        logger = logging.getLogger(logger_name)
        if ssid and split_data:
            logger.warning(
                "split-data argument will be ignored because ssid has been "
                "specified"
            )
            split_data = False

        if add_to_container_id and split_data:
            logger.warning(
                "split-data argument will be ignored because "
                "add_to_container_id has been specified"
            )
            split_data = False

        return split_data

    @staticmethod
    def __parse_pass_rules(passed_rules, result):
        """
        Parse pass rules.
        """

        for rule_text in passed_rules[1:]:  # Skip first empty part
            rule_name = rule_text.split(" ✅")[0].strip()
            rule_data = {"rule": rule_name, "sub_rule": None, "files": []}

            # Get sub-rule
            sub_rule_match = re.search(r"Sub-rule: (.*?)\n", rule_text)
            if sub_rule_match:
                rule_data["sub_rule"] = sub_rule_match.group(1).strip()

            # Get files passed
            files_passed = re.search(
                r"List of files passed:(.*?)(?=\n\n|\Z)", rule_text, re.DOTALL
            )
            if files_passed:
                for line in files_passed.group(1).split("\n"):
                    line = line.strip()
                    if line.startswith("·"):
                        file_match = re.match(r"· (.*?) \((\d+)/(\d+)\)", line)
                        if file_match:
                            rule_data["files"].append(
                                {
                                    "file": file_match.group(1).strip(),
                                    "passed_conditions": int(
                                        file_match.group(2)
                                    ),
                                }
                            )

            result["passed"].append(rule_data)
        return result

    @staticmethod
    def __parse_fail_rules(failed_rules, result):
        """
        Parse fail rules.
        """

        for rule_text in failed_rules[1:]:  # Skip first empty part
            rule_name = rule_text.split(" ❌")[0].strip()
            rule_data = {
                "rule": rule_name,
                "files": [],
                "failed_conditions": {},
            }

            # Extract all file comparisons for this rule
            file_comparisons = re.split(r"- Comparison with file:", rule_text)
            for comp in file_comparisons[1:]:  # Skip first part
                file_name = comp.split("\n")[0].strip()
                conditions_match = re.search(
                    r"Conditions:(.*?)(?=\n\t- Comparison|\n\n|$)",
                    comp,
                    re.DOTALL,
                )
                if not conditions_match:
                    continue

                conditions_text = conditions_match.group(1).strip()
                # Parse conditions
                conditions = []
                for line in conditions_text.split("\n"):
                    line = line.strip()
                    if line.startswith("·"):
                        status = "✔" if "✔" in line else "🚫"
                        condition = re.sub(r"^· [✔🚫]\s*", "", line)
                        conditions.append(
                            {
                                "status": (
                                    "passed" if status == "✔" else "failed"
                                ),
                                "condition": condition,
                            }
                        )

                # Add to failed conditions summary
                for cond in conditions:
                    if cond["status"] == "failed":
                        cond_text = cond["condition"]
                        if cond_text not in rule_data["failed_conditions"]:
                            rule_data["failed_conditions"][cond_text] = 0
                        rule_data["failed_conditions"][cond_text] += 1

                rule_data["files"].append(
                    {"file": file_name, "conditions": conditions}
                )

            result["failed"].append(rule_data)
        return result
