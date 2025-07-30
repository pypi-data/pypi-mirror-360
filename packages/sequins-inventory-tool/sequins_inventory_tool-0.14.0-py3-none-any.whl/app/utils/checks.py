"""Various utility functions for checking conditions."""

import typer
from functools import wraps


def require_api_endpoint_and_key():
    """
    Decorator to ensure that API endpoint and key are set.

    This decorator checks if the `ctx.obj` contains `api_endpoint` and
    `api_key`.

    If either is missing, it exits the program with an error message.

    Decorated functions must accept a `ctx` keyword argument of type
    `typer.Context`.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, ctx: typer.Context, **kwargs):
            if (
                ctx.obj is None
                or 'api_endpoint' not in ctx.obj
                or 'api_key' not in ctx.obj
            ):
                typer.echo(
                    'Error: API_ENDPOINT and API_KEY must be set via CLI or env'
                )
                raise typer.Exit(code=2)
            return f(*args, ctx=ctx, **kwargs)

        return wrapper

    return decorator
