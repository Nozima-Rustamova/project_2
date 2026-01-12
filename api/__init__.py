# Ensure drf-spectacular OpenApiAuthenticationExtension subclasses are imported
# so they register themselves when Django starts and the schema is generated.
from . import spectacular_extensions  # noqa: F401

