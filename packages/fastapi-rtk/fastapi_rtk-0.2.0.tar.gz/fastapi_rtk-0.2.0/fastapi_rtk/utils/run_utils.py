import inspect
import typing

from fastapi.concurrency import run_in_threadpool

from .prettify_dict import prettify_dict

P = typing.ParamSpec("P")
T = typing.TypeVar("T")

__all__ = ["smart_run", "safe_call", "call_with_valid_kwargs"]


async def smart_run(
    func: typing.Callable[P, typing.Union[T, typing.Awaitable[T]]],
    *args: P.args,
    **kwargs: P.kwargs,
) -> T:
    """
    A utility function that can run a function either as a coroutine or in a threadpool.

    Args:
        func: The function to be executed.
        *args: Positional arguments to be passed to the function.
        **kwargs: Keyword arguments to be passed to the function.

    Returns:
        The result of the function execution.

    Raises:
        Any exceptions raised by the function.

    """
    if inspect.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    return await run_in_threadpool(func, *args, **kwargs)


async def safe_call(coro: typing.Coroutine[typing.Any, typing.Any, T] | T) -> T:
    """
    A utility function that can await a coroutine or return a non-coroutine object.

    Args:
        coro (Any): The function call or coroutine to be awaited.

    Returns:
        The result of the function call or coroutine.
    """
    if isinstance(coro, typing.Coroutine):
        return await coro
    return coro


def call_with_valid_kwargs(
    func: typing.Callable[..., T], params: typing.Dict[str, typing.Any]
):
    """
    Call a function with valid keyword arguments. If a required parameter is missing, raise an error.

    Args:
        func (Callable[..., T]): The function to be called.
        params (Dict[str, Any]): The parameters to be passed to the function as keyword arguments.

    Raises:
        ValueError: If a required parameter is missing. The error message will contain the missing parameter and the given parameters.

    Returns:
        T: The result of the function call.
    """
    valid_kwargs: typing.Dict[str, typing.Any] = {}
    for [parameter_name, parameter_info] in inspect.signature(func).parameters.items():
        if parameter_name in params:
            valid_kwargs[parameter_name] = params[parameter_name]
        else:
            # Throw error if required parameter is missing
            if parameter_info.default == inspect.Parameter.empty:
                raise ValueError(
                    f"Parameter `{parameter_name}` does not exist in given parameters! Given parameters are:\n{prettify_dict(params, 2)}"
                )
    return func(**valid_kwargs)
