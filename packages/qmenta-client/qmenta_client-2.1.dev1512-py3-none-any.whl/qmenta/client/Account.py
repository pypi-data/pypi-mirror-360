from __future__ import print_function

import logging
from qmenta.core import errors
from qmenta.core import platform
from urllib3.exceptions import HTTPError

from .Project import Project
from .utils import load_json

logger_name = "qmenta.client"


class Account:
    """
    It represents your QMENTA account and implements the HTTP connection
    with the server. Once it is instantiated it will act as an identifier
    used by the rest of objects.

    Parameters
    ----------
    username : str
        Username on the platform. To get one go to https://platform.qmenta.com
    password : str
        The password assigned to the username.
    base_url : str
        The base url of the platform.
    verify_certificates : bool
        verify SSL certificates?

    Attributes
    ----------
    auth : qmenta.core.platform.Auth
        The Auth object used for communication with the platform
    """

    def __init__(
        self,
        username,
        password,
        base_url="https://platform.qmenta.com",
        verify_certificates=True,
    ):

        self._cookie = None
        self.username = username
        self.password = password
        self.baseurl = base_url
        self.verify_certificates = verify_certificates
        self.auth = None
        self.login()

    def __repr__(self):
        rep = "<Account session for {}>".format(self.username)
        return rep

    def login(self):
        """
        Login to the platform.

        Raises
        ------
        qmenta.core.platform.ConnectionError
            When the connection to the platform fails.
        qmenta.core.platform.InvalidLoginError
            When invalid credentials are provided.
        """
        logger = logging.getLogger(logger_name)
        try:
            auth = platform.Auth.login(
                self.username,
                self.password,
                base_url=self.baseurl,
                ask_for_2fa_input=True,
            )
        except errors.PlatformError as e:
            logger.error("Failed to log in: {}".format(e))
            self.auth = None
            raise

        self.auth = auth
        logger.info("Logged in as {}".format(self.username))

    def logout(self):
        """
        Logout from the platform.

        Raises
        ------
        qmenta.core.errors.PlatformError
            When the logout was not successful
        """

        logger = logging.getLogger(logger_name)
        try:
            platform.parse_response(platform.post(self.auth, "logout"))
        except errors.PlatformError as e:
            logger.error("Logout was unsuccessful: {}".format(e))
            raise

        logger.info("Logged out successfully")

    def get_project(self, project_id):
        """
        Retrieve a project instance, given its id, which can be obtained
        checking account.projects.

        Parameters
        ----------
        project_id : int or str
            ID of the project to retrieve, either the numeric ID or the name

        Returns
        -------
        Project
            A project object representing the desired project
        """
        if type(project_id) is int or type(project_id) is float:
            return Project(self, int(project_id))
        elif type(project_id) is str:
            projects = self.projects
            projects_match = [
                proj for proj in projects if proj["name"] == project_id
            ]
            if not projects_match:
                raise Exception(
                    f"Project {project_id} does not exist or is not available "
                    f"for this user."
                )
            return Project(self, int(projects_match[0]["id"]))
        return None

    @property
    def projects(self):
        """
        List all the projects available to the current user.

        Returns
        -------
        list[dict]
            List of project information (name, and id)
        """
        logger = logging.getLogger(logger_name)

        try:
            data = platform.parse_response(
                platform.post(
                    self.auth, "projectset_manager/get_projectset_list"
                )
            )
        except errors.PlatformError as e:
            logger.error("Failed to get project list: {}".format(e))
            raise

        titles = []
        for project in data:
            titles.append({"name": project["name"], "id": project["_id"]})
        return titles

    def add_project(
        self,
        project_abbreviation,
        project_name,
        description="",
        users=None,
        from_date="",
        to_date="",
    ):
        """
        Add a new project to the user account.

        Parameters
        ----------
        project_abbreviation : str
            Abbreviation of the project name.
        project_name : str
            Project name.
        description : str
            Description of the project.
        users : list[str]
            List of users to which this project is available.
        from_date : str
            Date of beginning of the project.
        to_date : str
            Date of ending of the project.

        Returns
        -------
        bool
            True if project was correctly added, False otherwise
        """
        if users is None:
            users = []
        logger = logging.getLogger(logger_name)
        for project in self.projects:
            if project["name"] == project_name:
                logger.error("Project name or abbreviation already exists.")
                return False

        try:
            platform.parse_response(
                platform.post(
                    self.auth,
                    "projectset_manager/upsert_project",
                    data={
                        "name": project_name,
                        "description": description,
                        "from_date": from_date,
                        "to_date": to_date,
                        "abbr": project_abbreviation,
                        "users": "|".join(users),
                    },
                )
            )
        except errors.PlatformError as e:
            logger.error(e)
            return False

        for project in self.projects:
            if project["name"] == project_name:
                logger.info("Project was successfully created.")
                return Project(self, int(project["id"]))
        logger.error("Project could note be created.")
        return False

    def _send_request(
        self,
        path,
        req_parameters=None,
        req_headers=None,
        stream=False,
        return_raw_response=False,
        response_timeout=900.0,
    ):
        """
        TODO: not used and contains warnings, maybe we should delete it.

        Send a request to the QMENTA Platform.

        Interaction with the server is performed as POST requests.

        Parameters
        ----------
        req_parameters : dict
            Data to send in the POST request.
        req_headers : dict
            Extra headers to include in the request:
        stream : bool
            Defer downloading the response body until accessing the
            response.content attribute.
        return_raw_response : bool
            When True, return the response from the
            server as-is. When False (by default),
            parse the answer as json to return a
            dictionary.
        response_timeout : float
            The timeout time in seconds to wait for the response.
        """

        req_headers = req_headers or {}
        req_url = "/".join((self.baseurl, path))
        if self._cookie is not None:
            req_headers["Cookie"] = self._cookie
        req_headers["Mint-Api-Call"] = "1"

        logger = logging.getLogger(logger_name)
        try:
            if path == "upload":
                response = self.pool.request(
                    "POST",
                    req_url,
                    body=req_parameters,
                    headers=req_headers,
                    timeout=response_timeout,
                    preload_content=not stream,
                )
            else:
                response = self.pool.request(
                    "POST",
                    req_url,
                    req_parameters or {},
                    headers=req_headers,
                    timeout=response_timeout,
                    preload_content=not stream,
                )
            if response.status >= 400:
                raise HTTPError(
                    "STATUS {}: {}".format(response.status, response.reason)
                )
        except Exception as e:
            error = "Could not send request. ERROR: {0}".format(e)
            logger.error(error)
            raise

        # Set the login cookie in our object
        if "set-cookie" in response.headers:
            self._cookie = response.headers["set-cookie"]

        if return_raw_response:
            return response

        # raise exception if there is no response from server
        if not response:
            error = "No response from server."
            logger.error(error)
            raise Exception(error)

        try:
            parsed_content = load_json(response.data)
        except Exception:
            error = "Could not parse the response as JSON data: {}".format(
                response.data
            )
            logger.error(error)
            raise

        # throw exceptions if anything strange happened
        if "error" in parsed_content:
            error = parsed_content["error"] or "Unknown error"
            logger.error(error)
            raise Exception(error)
        elif "success" in parsed_content and parsed_content["success"] == 3:
            error = parsed_content["message"]
            logger.error(error)
            raise Exception(error)
        return parsed_content
