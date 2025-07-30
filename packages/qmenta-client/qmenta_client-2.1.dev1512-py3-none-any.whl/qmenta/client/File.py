import glob
import json
import os
from collections import defaultdict
from tempfile import TemporaryDirectory, mkstemp

import pandas as pd
from pydicom import dcmread

import qmenta.client
from qmenta.client.utils import unzip_dicoms


class File:
    """
    It represents files stored in the QMENTA Platform.
    Once it is instantiated it will act as an identifier used by the rest of
    objects.

    :param project: A QMENTA Project instance
    :type project: qmenta.client.Project

    :param subject_name: The name of the subject you want to work with
    :type subject_name: str

    :param ssid: The ssid of the subject you want to work with
    :type ssid: str

    :param file_name: The file_name of the file you want to work with
    :type file_name: str

    `ff_container = File(project, "MRB", "1", "gre_field_mapping_3.zip")`
    """

    def __init__(
        self,
        project: qmenta.client.Project,
        subject_name: str,
        ssid: str,
        file_name: str,
    ):
        self.file_name = file_name
        self.project = project
        self._container_id = None
        for cont in self.project.list_input_containers():
            if (
                cont["patient_secret_name"] == subject_name
                and cont["ssid"] == ssid
            ):
                self._container_id = cont["container_id"]
                break
        if self.file_name.endswith(".zip"):
            self._file_type = "DICOM"
        elif self.file_name.endswith(".nii"):
            self._file_type = "NIfTI"
        elif self.file_name.endswith(".nii.gz"):
            self._file_type = "NIfTI-GZ"

    def __str__(self):
        return self.file_name

    def pull_scan_sequence_info(
        self, specify_dicom_tags=None, output_format: str = "csv"
    ):
        """
        Pulling scan sequence information (e.g. series number, series type,
        series description, number of files, file formats available)
        via the API in CSV/TSV or JSON format.

        Additionally, pulling specified DICOM headers themselves via tha API.

        It downloads the file defined in the File object and extracts the
        DICOM information. Nifti is not supported at the moment

        :param specify_dicom_tags:  tags to extract from DICOM header
        :type output_format:  list

        :param output_format:  A file output type. Supported formats: "csv",
        "tsv", "json", dict
        :type output_format:  str

        :return:
        :rtype dict:
        """
        if specify_dicom_tags is None:
            specify_dicom_tags = list()
        valid_output_formats = ["csv", "tsv", "json", "dict"]
        assert (
            output_format in valid_output_formats
        ), f"Output format not valid. Choose one of {valid_output_formats}"

        with TemporaryDirectory() as temp_dir:
            local_file_name = mkstemp(dir=temp_dir) + ".zip"
            self.project.download_file(
                self._container_id,
                self.file_name,
                local_file_name,
                overwrite=False,
            )
            if self._file_type == "DICOM":
                unzip_dicoms(local_file_name, temp_dir, exclude_members=None)
                dicoms = glob.glob(os.path.join(temp_dir, "*"))
                output_data = defaultdict(list)
                number_files = 0
                for dcm_file in dicoms:
                    try:
                        open_file = dcmread(dcm_file)
                        number_files += 1
                        if number_files == 1:
                            # only needed for one file, all have the same data.
                            for attribute in specify_dicom_tags:
                                # error handling of attributes send by the user
                                assert (
                                    len(attribute) == 2
                                ), "Invalid length of DICOM Attribute"
                                assert isinstance(
                                    attribute[0], int
                                ), "Invalid type of DICOM Attribute"
                                output_data["dicom tag"].append(
                                    open_file[attribute].tag
                                )
                                output_data["attribute"].append(
                                    open_file[attribute].name
                                )
                                output_data["value"].append(
                                    open_file[attribute].value
                                )
                    except Exception as e:
                        print(str(e))
                        pass

        output_data["dicom tag"].append("N/A")
        output_data["attribute"].append("Number of files")
        output_data["value"].append(number_files)

        if output_format == "csv":
            pd.DataFrame(output_data).to_csv(
                f"scan_sequence_info.{output_format}", index=False
            )

        elif output_format == "tsv":
            pd.DataFrame(output_data).to_csv(
                f"scan_sequence_info.{output_format}", sep="\t", index=False
            )

        elif output_format == "json":
            with open(f"scan_sequence_info.{output_format}", "w") as fp:
                json.dump(output_data, fp)

        elif output_format == "dict":
            return output_data
