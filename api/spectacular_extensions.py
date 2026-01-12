from drf_spectacular.extensions import OpenApiAuthenticationExtension


class JWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """Map our custom JWTAuthentication to the standard HTTP bearer scheme

    drf-spectacular will use this to represent the authenticator in the OpenAPI
    schema (so the Swagger UI shows the Authorize button for Bearer tokens).
    """
    # Name must be provided so drf-spectacular can reference the security scheme
    name = 'BearerAuth'
    target_class = 'api.authentication.JWTAuthentication'
    match_subclasses = True

    def get_security_definition(self, auto_schema):
        # return an OpenAPI security scheme object
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }
