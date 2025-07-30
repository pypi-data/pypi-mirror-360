import contextlib
import httpx

from starlette.applications import Starlette
from starlette.routing import BaseRoute, Route
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import JSONResponse

from .database import AsyncDBMiddleware, create_pool
from .auth_utils import JWTAuthBackend


def get_user(request) -> JSONResponse:
    """Get user route"""
    return JSONResponse(request.user.to_json() if request.user.is_authenticated else None)


# App factory
def create_app(
    routes: list[BaseRoute],
    secret: str,
    root_domain: str,
    database_uri: str | None,
    debug=False,
) -> Starlette:
    @contextlib.asynccontextmanager
    async def lifespan(app_):
        print("Building Asyncpg Pool")
        app_.state.db_pool = await create_pool(database_uri)
        print("Creating HTTPX Client instance")
        app_.state.httpx_client = httpx.AsyncClient()
        yield
        print("Closing HTTPX Client")
        await app_.state.httpx_client.aclose()
        print("Closing Asyncpg Pool")
        await app_.state.db_pool.close()

    authbackend = JWTAuthBackend(secret, root_domain)

    # Allow origins from both HTTP or HTTPS, root or subdomains, any port
    root_domain_re = r"https?://(.*\.)?{}(:\d*)?".format(root_domain.replace(".", r"\."))
    print("Allowed Origins Regex:", root_domain_re)

    # noinspection PyTypeChecker
    app = Starlette(
        routes=routes + [Route("/getuser", get_user, methods=["GET"])],
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origin_regex=root_domain_re,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["Authorization"],
            ),
            Middleware(AsyncDBMiddleware),
            Middleware(
                AuthenticationMiddleware,
                backend=authbackend,
                on_error=authbackend.auth_error_handler,
            ),
        ],
        lifespan=lifespan,
        debug=debug,
    )
    # noinspection PyUnresolvedReferences
    app.router.redirect_slashes = False
    return app
