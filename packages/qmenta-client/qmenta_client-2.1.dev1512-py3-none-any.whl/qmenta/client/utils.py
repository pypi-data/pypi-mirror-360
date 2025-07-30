import json
import os
import re
import zipfile


def load_json(data):
    """
    Loads a JSON string and returns the dictionary.

    Parameters
    ----------
    data : str or bytes
        If the input data is not as tring but bytes, it will automatically
        be converted to string before parsing the JSON.

    Returns
    -------
    dict
        The parsed JSON.
    """
    try:
        return json.loads(data)
    except TypeError:
        # Decode bytes into string
        return json.loads(data.decode())


def unzip_dicoms(zip_path, output_folder, exclude_members=None):
    """
    Recursive unzipping. It allows recursive unzipping, which means that all
    zips inside
    the zip file will be extracted as well.

    ZIP files can contain the same file twice. This can be accomplished using
    the "add to archive" function of your zip tool. By default, a later file
    overwrites any former file(s) when extracting as this is usually the
    desired behavior.

    WARNING: This function deletes all extracted zips, including the root
    'zip_path'.

    Parameters
    ----------
    zip_path : str
        Path to zip
    output_folder : str
        Path to output folder. The folder must exist before being created.
    exclude_members : list of str, optional
        List of complimentary regex expressions to exclude from being extracted
        from the zip. If None, all files will be extracted. Default is None.

    Returns
    -------
    list of str
        List of extracted files.
    """
    # Compatibility with pathlib.Path
    zip_path = str(zip_path)
    output_folder = str(output_folder)

    # Zip extraction
    extracted_files = list()
    with zipfile.ZipFile(zip_path) as zfile:
        members = zfile.namelist()  # list all available members
        members = list(set(members))  # exclude repeated files
        if exclude_members is not None:
            # Filter members according to the passed exclusion rules
            for exclude_members_rule in exclude_members:
                members = [
                    x for x in members if not re.match(exclude_members_rule, x)
                ]

        # Extract all files and add them to the list of extracted files
        zfile.extractall(path=output_folder, members=members)
        current_extracted_files = [
            os.path.join(output_folder, fpath) for fpath in members
        ]
        extracted_files.extend(current_extracted_files)
    os.unlink(zip_path)
