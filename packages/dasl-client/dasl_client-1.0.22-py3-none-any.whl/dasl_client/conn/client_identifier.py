from importlib.metadata import version


def get_user_agent() -> str:
    """
    A helper function defining the user agent for requests originating from
    the ASL python conn library. We include the version of the API that the
    connection was built off.

    :return: A user-agent string.
    """
    return get_client_identifier()


def get_client_identifier() -> str:
    """
    A helper function defining the client identifier for identifying the python
    client. We include the version of the version of the API that the client
    uses.

    :return: The python client identifier.
    """
    return f"asl-python-client/{version('dasl_api')}"
