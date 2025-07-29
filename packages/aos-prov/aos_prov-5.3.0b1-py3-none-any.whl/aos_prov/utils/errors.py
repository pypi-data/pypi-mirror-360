#
#  Copyright (c) 2018-2024 Renesas Inc.
#  Copyright (c) 2018-2024 EPAM Systems Inc.
#


class OnUnitError(Exception):
    """On Unit Error."""


class UserCredentialsError(OnUnitError):
    """User Credentials Error."""


class DeviceRegisterError(OnUnitError):
    """Device Register Error."""


class DeviceDeregisterError(OnUnitError):
    """Device Deregister Error."""


class UnitError(OnUnitError):
    """Unit Error."""


class GrpcUnimplemented(OnUnitError):  # noqa: N818
    """Grpc Unimplemented."""


class CloudAccessError(OnUnitError):
    """Cloud Access Error."""


class AosProvError(OnUnitError):
    """Aos Prov Error."""
