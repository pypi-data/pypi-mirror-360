import datetime
import json
import sys
from enum import Enum
from typing import Literal
from typing import Optional
from typing import TypedDict


class AuthenticationType(str, Enum):
    Logon = "Logon"
    Logoff = "Logoff"


class AuthenticationResult(str, Enum):
    Success = "Success"
    Partial = "Partial"
    Failure = "Failure"
    NA = "NA"


class AuthenticationLoginMethod(str, Enum):
    UsernamePassword = "Username & Password"
    StaffSSO = "Staff-SSO"
    UKGOVSSO = "UK.GOV-SSO"
    ExternalIDP = "External IdP"


class Severity(str, Enum):
    Informational = "Informational"
    Low = "Low"
    Medium = "Medium"
    High = "High"


class AuthenticationServer(TypedDict):
    """Dictionary to represent properties of the HTTP Server."""

    """
    A unique identifier for the server which serviced the Authentication event.

    Defaults to the WSGI SERVER_NAME field if not provided.
    """
    hostname: Optional[str]
    """Internet Protocol Address of the server serving this request."""
    ipAddr: Optional[str]


class AuthenticationClient(TypedDict):
    """Dictionary to represent properties of the HTTP Client."""

    """Internet Protocol Address of the client making the Authentication
    event."""
    ipAddr: Optional[str]


class AuthenticationUser(TypedDict):
    """Dictionary to represent properties of the users session."""

    """What type of role best describes this Authentication event."""
    role: Optional[
        Literal[
            "Regular",
            "Machine",
            "Admin",
            "System",
            "Application",
            "Service Principal",
            "Service",
            "Anonymous",
            "Other",
        ]
    ]
    """
    A unique identifier for the user.

    Defaults to the logged in Django User.username if not provided.
    """
    username: Optional[str]
    """
    A unique identifier for this authentication session if one exists.

    Defaults to the Django Sessions session key if not provided.
    """
    sessionId: Optional[str]


def log_authentication(
    request,
    type: AuthenticationType,
    result: AuthenticationResult,
    login_method: AuthenticationLoginMethod,
    user: Optional[AuthenticationUser] = None,
    server: Optional[AuthenticationServer] = None,
    client: Optional[AuthenticationClient] = None,
    severity: Optional[Severity] = None,
    time_generated: Optional[datetime.datetime] = None,
    result_details: Optional[str] = None,
    message: Optional[str] = None,
):
    """
    Log an ASIM Authentication Event to standard output.

    :param request: django.http.HttpRequest object which initiated this Authentication request
                    from which the following data will be logged if available
                        - Django Authentication systems current username
                        - Django Session middlewares Session Key
                        - Client IP address
                        - Server hostname
    :param type: What authentication action was attempted, either "Logon" or "Logoff"
    :param result: What outcome did the action have, either "Success", "Failure", "Partial", "NA"
    :param login_method: What authentication mechanism was being used, one of:
                        - "Username & Password"
                        - "Staff-SSO"
                        - "UK.GOV-SSO"
                        - "External IdP"
    :param user: Dictionary containing information on the subject of this Authentication event
                 see AuthenticationUser class for more details.
    :param server: Dictionary containing information on the server servicing this Authentication event
                   see AuthenticationServer class for more details.
    :param client: Dictionary containing information on the client performing this Authentication event
                   see AuthenticationClient class for more details.
    :param severity: Optional severity of the event, defaults to "Informational", otherwise one of:
                        - "Informational"
                        - "Low"
                        - "Medium"
                        - "High"
    :param time_generated: Optional datetime for when the event happened, otherwise datetime.now
    :param result_details: Optional string describing any details associated with the events outcome.
                           This field is typically populated when the result is a failure.
    :param message: Optional string describing the reason why the log was generated.

    See also: https://learn.microsoft.com/en-us/azure/sentinel/normalization-schema-authentication
    """
    if user == None:
        user = {}
    if server == None:
        server = {}
    if client == None:
        client = {}

    event_created = time_generated or datetime.datetime.now(tz=datetime.timezone.utc)

    event = {
        "EventCreated": event_created.isoformat(),  # TODO: Should this really be EventCreated, or TimeGenerated
        "DvcHostname": server.get("hostname", request.environ.get("SERVER_NAME")),
        "EventSeverity": severity or _default_severity(result),
        "EventOriginalType": _event_code(type, result),
        "SrcIpAddr": client.get("ipAddr", request.environ.get("REMOTE_ADDR")),
        "EventType": type,
        "EventResult": result,
        "LogonMethod": login_method,
        "EventSchema": "Authentication",
        "EventSchemaVersion": "0.1.4",
    }

    if "role" in user:
        event["ActorUserType"] = user["role"]

    if "sessionId" in user:
        event["ActorSessionId"] = user["sessionId"]
    elif request.session.session_key:
        event["ActorSessionId"] = request.session.session_key

    if "username" in user:
        event["ActorUserName"] = user["username"]
    elif request.user.username:
        event["ActorUserName"] = request.user.username

    if result_details:
        event["EventResultDetails"] = result_details

    if message:
        event["EventMessage"] = message

    if "ipAddr" in server:
        event["DvcIpAddr"] = server["ipAddr"]

    sys.stdout.write(json.dumps(event) + "\n")
    sys.stdout.flush()


log_authentication.Type = AuthenticationType
log_authentication.Result = AuthenticationResult
log_authentication.LoginMethod = AuthenticationLoginMethod
log_authentication.Severity = Severity


def _default_severity(result):
    return Severity.Informational if result == AuthenticationResult.Success else Severity.Medium


def _event_code(type, result):
    if type == AuthenticationType.Logon:
        if result == log_authentication.Result.Success:
            return "001a"
        elif result == AuthenticationResult.Failure:
            return "001b"
    elif type == AuthenticationType.Logoff:
        if result == AuthenticationResult.Success:
            return "001c"
        elif result == AuthenticationResult.Failure:
            return "001d"
    return "001"
