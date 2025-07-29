from __future__ import annotations

import functools
import inspect
import traceback
from collections.abc import AsyncGenerator, Awaitable, Callable, Generator
from typing import Any, Generic, Literal, NoReturn, TypeVar, Union, cast

try:
  from typing import ParamSpec
except ImportError:
  try:
    from typing_extensions import ParamSpec  # type: ignore
  except ImportError:
    pass

try:
  from typing import TypeIs
except ImportError:
  try:
    from typing_extensions import TypeIs  # type: ignore
  except ImportError:
    pass

T = TypeVar('T', covariant=True)
E = TypeVar('E', covariant=True)
U = TypeVar('U')
F = TypeVar('F')
P = ParamSpec('P')
R = TypeVar('R')
TBE = TypeVar('TBE', bound=BaseException)


class UnwrapError(Exception):
  """
  Exception raised when an unwrap or expect operation fails on a Result.

  ```
  try:
      Err("fail").unwrap()
  except UnwrapError as e:
      print(e)
  # Called `Result.unwrap()` on an `Err` value: 'fail'
  ```
  """

  _result: Result[object, object]

  def __init__(self, result: Result[object, object], message: str) -> None:
    self._result = result
    super().__init__(message)

  @property
  def result(self) -> Result[..., Any]:
    """
    Returns the original result that caused the unwrap failure.

    Useful for debugging and error recovery scenarios where you need to inspect
    the original Result that failed to unwrap. Common in error handling pipelines
    where you want to log the original error context.

    ```
    try:
        Err("fail").unwrap()
    except UnwrapError as e:
        assert isinstance(e.result, Err)
    ```
    """
    return self._result


class Ok(Generic[T]):
  """
  Represents a successful result containing a value.

  Use when operations succeed and you want to chain further operations.
  Avoid when you need to represent failure states - use Err instead.

  ```
  Ok(42).unwrap()  # 42
  ```
  """

  __match_args__ = ('ok_value',)
  __slots__ = ('_value',)

  def __init__(self, value: T) -> None:
    self._value = value

  def __repr__(self) -> str:
    return f'Ok({self._value!r})'

  def __eq__(self, other: Any) -> bool:
    return isinstance(other, Ok) and self._value == other._value

  def __ne__(self, other: Any) -> bool:
    return not (self == other)

  def __hash__(self) -> int:
    return hash((True, self._value))

  def is_ok(self) -> Literal[True]:
    """
    Always returns True for Ok instances.

    Use for type narrowing and conditional logic. Prefer this over isinstance checks
    for better type inference. Avoid when you already know the Result type.

    ```
    Ok(1).is_ok()  # True
    ```
    """
    return True

  def is_err(self) -> Literal[False]:
    """
    Always returns False for Ok instances.

    Use for type narrowing and conditional logic. Prefer this over isinstance checks
    for better type inference. Avoid when you already know the Result type.

    ```
    Ok(1).is_err()  # False
    ```
    """
    return False

  def ok(self) -> T:
    """
    Returns the contained value for Ok instances.

    Use when you want to extract the value without unwrapping. Prefer unwrap()
    when you're certain the Result is Ok. Avoid when you need error handling.

    ```
    Ok(1).ok()  # 1
    ```
    """
    return self._value

  def err(self) -> None:
    """
    Always returns None for Ok instances since there's no error.

    Use for symmetry with Err.err() in generic code. Avoid when you know
    the Result is Ok - the return will always be None.

    ```
    Ok(1).err()  # None
    ```
    """
    return None

  @property
  def ok_value(self) -> T:
    """
    Returns the inner value for pattern matching and direct access.

    Use with match statements and when you need direct property access.
    Prefer unwrap() for general value extraction. Avoid when error handling is needed.

    ```
    Ok(2).ok_value  # 2
    ```
    """
    return self._value

  def swap(self) -> Err[T]:
    """
    Converts Ok to Err with the same value, swapping success/failure semantics.

    Use when you need to invert the meaning of success/failure in your logic.
    Common in testing scenarios or when adapting between different Result conventions.
    Avoid in normal business logic where semantics should remain consistent.

    ```
    Ok("x").swap()  # Err('x')
    ```
    """
    return Err(self._value)

  def value_or(self, default: Any) -> T:
    """
    Returns the contained value, ignoring the default (alias for unwrap_or).

    Use when you want consistent API with Err.value_or(). Prefer unwrap()
    when you know the Result is Ok. Avoid when the default value is expensive to compute.

    ```
    Ok(42).value_or(0)  # 42
    ```
    """
    return self._value

  def alt(self, op: Callable[[E], F]) -> Ok[T]:
    """
    No-op for Ok instances - error transformation doesn't apply to successful results.

    Use in generic code that handles both Ok and Err. The operation is ignored
    for Ok instances, maintaining the original value. Avoid when you know the Result is Ok.

    ```
    Ok(1).alt(lambda e: 0)  # Ok(1)
    ```
    """
    return self

  def expect(self, _message: str) -> T:
    """
    Returns the contained value, ignoring the message since Ok cannot fail.

    Use when you want consistent API with Err.expect() in generic code.
    Prefer unwrap() when you know the Result is Ok. Avoid when error context isn't needed.

    ```
    Ok(1).expect("should not fail")  # 1
    ```
    """
    return self._value

  def expect_err(self, message: str) -> NoReturn:
    """
    Always raises UnwrapError since Ok instances don't contain errors.

    Use when you expect an error but got success - indicates a logic error.
    Common in testing scenarios. Avoid in normal business logic.

    ```
    try:
        Ok(1).expect_err("should be error")
    except UnwrapError:
        pass
    ```
    """
    raise UnwrapError(self, message)

  def unwrap(self) -> T:
    """
    Returns the contained value safely since Ok instances always contain values.

    Use when you're certain the Result is Ok or when you want to fail fast on errors.
    Prefer this over ok() for value extraction. Avoid when error handling is required.

    ```
    Ok(1).unwrap()  # 1
    ```
    """
    return self._value

  def unwrap_err(self) -> NoReturn:
    """
    Always raises UnwrapError since Ok instances don't contain errors.

    Use when you expect an error but got success - indicates a logic error.
    Common in testing scenarios. Avoid in normal business logic.

    ```
    try:
        Ok(1).unwrap_err()
    except UnwrapError:
        pass
    ```
    """
    raise UnwrapError(self, 'Called `Result.unwrap_err()` on an `Ok` value')

  def unwrap_or(self, _default: U) -> T:
    """
    Returns the contained value, ignoring the default since Ok always has a value.

    Use when you want consistent API with Err.unwrap_or() in generic code.
    Prefer unwrap() when you know the Result is Ok. Avoid when the default is expensive.

    ```
    Ok(1).unwrap_or(0)  # 1
    ```
    """
    return self._value

  def unwrap_or_else(self, op: Callable[[E], T]) -> T:
    """
    Returns the contained value, ignoring the operation since Ok always has a value.

    Use when you want consistent API with Err.unwrap_or_else() in generic code.
    The operation is never called for Ok instances. Avoid when you know the Result is Ok.

    ```
    Ok(1).unwrap_or_else(lambda e: 0)  # 1
    ```
    """
    return self._value

  def unwrap_or_raise(self, e: object) -> T:
    """
    Returns the contained value, ignoring the exception since Ok cannot fail.

    Use when you want consistent API with Err.unwrap_or_raise() in generic code.
    The exception is never raised for Ok instances. Avoid when you know the Result is Ok.

    ```
    Ok(1).unwrap_or_raise(Exception)  # 1
    ```
    """
    return self._value

  def map(self, op: Callable[[T], U]) -> Ok[U]:
    """
    Transforms the contained value using the provided function, wrapping result in Ok.

    Use for transforming successful values while preserving the Ok context.
    Essential for functional programming patterns. Avoid when transformation can fail
    without proper error handling.

    ```
    Ok(2).map(lambda x: x * 10)  # Ok(20)
    ```
    """
    return Ok(op(self._value))

  async def map_async(self, op: Callable[[T], Awaitable[U]]) -> Ok[U]:
    """
    Asynchronously transforms the contained value, wrapping result in Ok.

    Use for async transformations of successful values. Essential for async
    functional programming patterns. Avoid when the async operation can fail
    without proper error handling.

    ```
    await Ok(2).map_async(async_lambda)
    ```
    """
    return Ok(await op(self._value))

  def map_or(self, default: U, op: Callable[[T], U]) -> U:
    """
    Transforms the contained value using the operation, ignoring the default.

    Use when you want consistent API with Err.map_or() in generic code.
    The default is never used for Ok instances. Prefer map() when you know the Result is Ok.

    ```
    Ok(2).map_or(0, lambda x: x * 2)  # 4
    ```
    """
    return op(self._value)

  def map_or_else(self, default_op: Callable[[], U], op: Callable[[T], U]) -> U:
    """
    Transforms the contained value using the operation, ignoring the default operation.

    Use when you want consistent API with Err.map_or_else() in generic code.
    The default operation is never called for Ok instances. Prefer map() when you know the Result is Ok.

    ```
    Ok(2).map_or_else(lambda: 0, lambda x: x * 2)  # 4
    ```
    """
    return op(self._value)

  def map_err(self, op: Callable[[E], F]) -> Ok[T]:
    """
    No-op for Ok instances - error transformation doesn't apply to successful results.

    Use in generic code that handles both Ok and Err. The operation is ignored
    for Ok instances, maintaining the original value. Avoid when you know the Result is Ok.

    ```
    Ok(2).map_err(lambda e: 0)  # Ok(2)
    ```
    """
    return self

  def and_then(self, op: Callable[[T], Result[U, E]]) -> Result[U, E]:
    """
    Chains another Result-returning operation on the contained value (monadic bind).

    Use for chaining operations that can fail, creating pipelines of fallible computations.
    Essential for functional error handling. Avoid when the operation cannot fail.

    ```
    Ok(2).and_then(lambda x: Ok(x * 2))  # Ok(4)
    ```
    """
    return op(self._value)

  async def and_then_async(self, op: Callable[[T], Awaitable[Result[U, E]]]) -> Result[U, E]:
    """
    Asynchronously chains another Result-returning operation on the contained value.

    Use for chaining async operations that can fail. Essential for async functional
    error handling patterns. Avoid when the async operation cannot fail.

    ```
    await Ok(2).and_then_async(async_lambda)
    ```
    """
    return await op(self._value)

  def or_else(self, op: Callable[[E], Result[T, F]]) -> Ok[T]:
    """
    No-op for Ok instances - error recovery doesn't apply to successful results.

    Use in generic code that handles both Ok and Err. The operation is ignored
    for Ok instances, maintaining the original value. Avoid when you know the Result is Ok.

    ```
    Ok(2).or_else(lambda e: Ok(0))  # Ok(2)
    ```
    """
    return self

  def inspect(self, op: Callable[[T], Any]) -> Result[T, E]:
    """
    Calls the provided function with the contained value for side effects, returns self.

    Use for debugging, logging, or other side effects without changing the Result.
    Common for tracing successful values in pipelines. Avoid when side effects are expensive.

    ```
    Ok(2).inspect(print)  # prints 2, returns Ok(2)
    ```
    """
    op(self._value)
    return self

  def inspect_err(self, op: Callable[[E], Any]) -> Result[T, E]:
    """
    No-op for Ok instances - error inspection doesn't apply to successful results.

    Use in generic code that handles both Ok and Err. The operation is ignored
    for Ok instances. Avoid when you know the Result is Ok.

    ```
    Ok(2).inspect_err(print)  # Ok(2), nothing printed
    ```
    """
    return self

  def match(self, *, ok: Callable[[T], U] | None = None, err: Callable[[E], U] | None = None) -> U:
    """
    Pattern matches on Ok, requiring an 'ok' handler and ignoring 'err' handler.

    Use for exhaustive pattern matching with clear intent. Provides type safety
    and forces explicit handling. Avoid when simple unwrap() or map() suffices.

    ```
    Ok(1).match(ok=lambda x: f"Got {x}", err=lambda e: f"Error: {e}")  # 'Got 1'
    ```
    """
    if ok is None:
      raise ValueError("Ok.match requires an 'ok' handler")
    return ok(self._value)


class Err(Generic[E]):
  """
  Represents a failed result containing an error value.

  Use when operations fail and you want to propagate error information.
  Avoid when success is the only meaningful outcome.

  ```
  Err("fail").unwrap_or(0)  # 0
  ```
  """

  __match_args__ = ('err_value',)
  __slots__ = ('_trace', '_value')

  def __init__(self, value: E) -> None:
    self._value = value
    # Use a sentinel for lazy traceback computation to avoid side effects in constructor
    self._trace: list[str] | None | type(...) = ...

  def _capture_traceback(self, exc: E) -> list[str] | None:
    # Only capture traceback if value is a BaseException and has __traceback__
    if isinstance(exc, BaseException) and exc.__traceback__ is not None:
      stack_summary = traceback.extract_tb(exc.__traceback__)
      return traceback.format_list(stack_summary)
    return None

  @property
  def trace(self) -> list[str] | None:
    """
    Returns the captured stack trace as a list of formatted strings for BaseException errors.

    Use for debugging and error reporting when the error value is an exception.
    Computed lazily to avoid performance overhead. Returns None for non-exception errors.
    Avoid when error value is not an exception.

    ```
    try:
        raise ValueError("fail")
    except ValueError as e:
        err = Err(e)
        print(err.trace)
    ```
    """
    # Lazy computation of traceback to avoid constructor side effects
    if self._trace is ...:
      self._trace = self._capture_traceback(self._value) if isinstance(self._value, BaseException) else None
    return self._trace

  def __repr__(self) -> str:
    return f'Err({self._value!r})'

  def __eq__(self, other: Any) -> bool:
    return isinstance(other, Err) and self._value == other._value

  def __ne__(self, other: Any) -> bool:
    return not (self == other)

  def __hash__(self) -> int:
    return hash((False, self._value))

  def is_ok(self) -> Literal[False]:
    """
    Always returns False for Err instances.

    Use for type narrowing and conditional logic. Prefer this over isinstance checks
    for better type inference. Avoid when you already know the Result type.

    ```
    Err("fail").is_ok()  # False
    ```
    """
    return False

  def is_err(self) -> Literal[True]:
    """
    Always returns True for Err instances.

    Use for type narrowing and conditional logic. Prefer this over isinstance checks
    for better type inference. Avoid when you already know the Result type.

    ```
    Err("fail").is_err()  # True
    ```
    """
    return True

  def ok(self) -> None:
    """
    Always returns None for Err instances since there's no success value.

    Use for symmetry with Ok.ok() in generic code. Avoid when you know
    the Result is Err - the return will always be None.

    ```
    Err("fail").ok()  # None
    ```
    """
    return None

  def err(self) -> E:
    """
    Returns the contained error value for Err instances.

    Use when you want to extract the error without unwrapping. Prefer unwrap_err()
    when you're certain the Result is Err. Avoid when you need success handling.

    ```
    Err("fail").err()  # "fail"
    ```
    """
    return self._value

  @property
  def err_value(self) -> E:
    """
    Returns the inner error value for pattern matching and direct access.

    Use with match statements and when you need direct property access.
    Prefer unwrap_err() for general error extraction. Avoid when success handling is needed.

    ```
    Err("fail").err_value  # "fail"
    ```
    """
    return self._value

  def swap(self) -> Ok[E]:
    """
    Converts Err to Ok with the error value, swapping failure/success semantics.

    Use when you need to invert the meaning of success/failure in your logic.
    Common in testing scenarios or when adapting between different Result conventions.
    Avoid in normal business logic where semantics should remain consistent.

    ```
    Err("fail").swap()  # Ok('fail')
    ```
    """
    return Ok(self._value)

  def value_or(self, default: U) -> U:
    """
    Returns the default value since Err instances don't contain success values.

    Use when you want to provide a fallback value for failed operations.
    Essential for graceful degradation patterns. Avoid when the default is expensive to compute.

    ```
    Err("fail").value_or(0)  # 0
    ```
    """
    return default

  def alt(self, op: Callable[[E], F]) -> Err[F]:
    """
    Transforms the contained error value using the provided function, wrapping result in Err.

    Use for transforming error values while preserving the Err context.
    Common for error normalization and enrichment. Avoid when error transformation can fail
    without proper handling.

    ```
    Err(1).alt(lambda e: e + 1)  # Err(2)
    ```
    """
    return Err(op(self._value))

  def expect(self, message: str) -> NoReturn:
    """
    Always raises UnwrapError with the provided message since Err instances represent failure.

    Use when you expect success but got failure - provides clear error context.
    Common for assertions and fail-fast scenarios. Avoid in normal error handling.

    ```
    try:
        Err("fail").expect("should not fail")
    except UnwrapError:
        pass
    ```
    """
    exc = UnwrapError(self, f'{message}: {self._value!r}')
    if isinstance(self._value, BaseException):
      raise exc from self._value
    raise exc

  def expect_err(self, _message: str) -> E:
    """
    Returns the contained error value, ignoring the message since Err always contains errors.

    Use when you want consistent API with Ok.expect_err() in generic code.
    Prefer unwrap_err() when you know the Result is Err. Avoid when success context isn't needed.

    ```
    Err("fail").expect_err("should be error")  # "fail"
    ```
    """
    return self._value

  def unwrap(self) -> NoReturn:
    """
    Always raises UnwrapError since Err instances don't contain success values.

    Use when you expect success but got failure - indicates a logic error.
    Common for fail-fast scenarios and debugging. Avoid in normal error handling.

    ```
    try:
        Err("fail").unwrap()
    except UnwrapError:
        pass
    ```
    """
    exc = UnwrapError(self, f'Called `Result.unwrap()` on an `Err` value: {self._value!r}')
    if isinstance(self._value, BaseException):
      raise exc from self._value
    raise exc

  def unwrap_err(self) -> E:
    """
    Returns the contained error value safely since Err instances always contain errors.

    Use when you're certain the Result is Err or when you want to fail fast on success.
    Prefer this over err() for error extraction. Avoid when success handling is required.

    ```
    Err("fail").unwrap_err()  # "fail"
    ```
    """
    return self._value

  def unwrap_or(self, default: U) -> U:
    """
    Returns the default value since Err instances don't contain success values.

    Use when you want to provide a fallback value for failed operations.
    Essential for graceful degradation patterns. Avoid when the default is expensive to compute.

    ```
    Err("fail").unwrap_or(0)  # 0
    ```
    """
    return default

  def unwrap_or_else(self, op: Callable[[E], T]) -> T:
    """
    Applies the operation to the error value and returns the result.

    Use when you want to compute a fallback value based on the error.
    Essential for error recovery patterns. Avoid when the operation is expensive or can fail.

    ```
    Err(2).unwrap_or_else(lambda e: e + 1)  # 3
    ```
    """
    return op(self._value)

  def unwrap_or_raise(self, e: type[TBE]) -> NoReturn:
    """
    Raises the provided exception type with the error value as the message.

    Use when you want to convert Result errors to traditional exceptions.
    Common at API boundaries. Avoid when you want to maintain Result-based error handling.

    ```
    try:
        Err("fail").unwrap_or_raise(ValueError)
    except ValueError:
        pass
    ```
    """
    raise e(self._value)

  def map(self, op: Callable[[T], U]) -> Err[E]:
    """
    No-op for Err instances - value transformation doesn't apply to failed results.

    Use in generic code that handles both Ok and Err. The operation is ignored
    for Err instances, maintaining the original error. Avoid when you know the Result is Err.

    ```
    Err("fail").map(lambda x: x * 2)  # Err('fail')
    ```
    """
    return self

  async def map_async(self, op: Callable[[T], Awaitable[U]]) -> Err[E]:
    """
    No-op for Err instances - async value transformation doesn't apply to failed results.

    Use in generic code that handles both Ok and Err. The operation is ignored
    for Err instances, maintaining the original error. Avoid when you know the Result is Err.

    ```
    await Err("fail").map_async(lambda x: x * 2)  # Err('fail')
    ```
    """
    return self

  def map_or(self, default: U, op: Callable[[T], U]) -> U:
    """
    Returns the default value since Err instances don't contain success values to transform.

    Use when you want to provide a fallback value instead of transforming.
    The operation is ignored for Err instances. Avoid when the default is expensive.

    ```
    Err("fail").map_or(0, lambda x: x * 2)  # 0
    ```
    """
    return default

  def map_or_else(self, default_op: Callable[[], U], op: Callable[[E], U]) -> U:
    """
    Calls the default operation since Err instances don't contain success values to transform.

    Use when you want to compute a fallback value for failed results.
    The main operation is ignored for Err instances. Avoid when the default operation is expensive.

    ```
    Err("fail").map_or_else(lambda: 42, lambda x: x * 2)  # 42
    ```
    """
    return default_op()

  def map_err(self, op: Callable[[E], F]) -> Err[F]:
    """
    Transforms the contained error value using the provided function, wrapping result in Err.

    Use for transforming error values while preserving the Err context.
    Common for error normalization and enrichment. Avoid when error transformation can fail.

    ```
    Err(2).map_err(lambda e: e + 1)  # Err(3)
    ```
    """
    return Err(op(self._value))

  def and_then(self, op: Callable[[T], Result[U, E]]) -> Err[E]:
    """
    No-op for Err instances - chaining operations doesn't apply to failed results.

    Use in generic code that handles both Ok and Err. The operation is ignored
    for Err instances, maintaining the original error. Avoid when you know the Result is Err.

    ```
    Err("fail").and_then(lambda x: Ok(x * 2))  # Err('fail')
    ```
    """
    return self

  async def and_then_async(self, op: Callable[[T], Awaitable[Result[U, E]]]) -> Err[E]:
    """
    No-op for Err instances - async chaining operations doesn't apply to failed results.

    Use in generic code that handles both Ok and Err. The operation is ignored
    for Err instances, maintaining the original error. Avoid when you know the Result is Err.

    ```
    await Err("fail").and_then_async(lambda x: Ok(x * 2))  # Err('fail')
    ```
    """
    return self

  def or_else(self, op: Callable[[E], Result[T, F]]) -> Result[T, F]:
    """
    Applies error recovery operation to the contained error value (monadic bind for errors).

    Use for chaining error recovery operations, creating pipelines of error handling.
    Essential for functional error recovery patterns. Avoid when the operation cannot fail.

    ```
    Err(2).or_else(lambda e: Ok(e + 1))  # Ok(3)
    ```
    """
    return op(self._value)

  def inspect(self, op: Callable[[T], Any]) -> Result[T, E]:
    """
    No-op for Err instances - value inspection doesn't apply to failed results.

    Use in generic code that handles both Ok and Err. The operation is ignored
    for Err instances. Avoid when you know the Result is Err.

    ```
    Err("fail").inspect(print)  # Err('fail'), nothing printed
    ```
    """
    return self

  def inspect_err(self, op: Callable[[E], Any]) -> Result[T, E]:
    """
    Calls the provided function with the contained error value for side effects, returns self.

    Use for debugging, logging, or other side effects without changing the Result.
    Common for tracing error values in pipelines. Avoid when side effects are expensive.

    ```
    Err("fail").inspect_err(print)  # prints 'fail', returns Err('fail')
    ```
    """
    op(self._value)
    return self

  def match(self, *, ok: Callable[[T], U] | None = None, err: Callable[[E], U] | None = None) -> U:
    """
    Pattern matches on Err, requiring an 'err' handler and ignoring 'ok' handler.

    Use for exhaustive pattern matching with clear intent. Provides type safety
    and forces explicit handling. Avoid when simple unwrap_err() or map_err() suffices.

    ```
    Err("fail").match(ok=lambda x: f"Got {x}", err=lambda e: f"Error: {e}")  # 'Error: fail'
    ```
    """
    if err is None:
      raise ValueError("Err.match requires an 'err' handler")
    return err(self._value)


Result = Union[Ok[T], Err[E]]
OkErr = (Ok, Err)


def as_result(
  *exceptions: type[TBE],
) -> Callable[[Callable[..., R]], Callable[..., Result[R, TBE]]]:
  """
  Decorator that converts a function to return Result, catching specified exceptions as Err.

  Use when you want to convert exception-based APIs to Result-based APIs.
  Essential for integrating with existing codebases. Avoid when functions already return Results.

  ```
  @as_result(ValueError)
  def parse_int(x: str) -> int:
      return int(x)

  parse_int("42")  # Ok(42)
  parse_int("fail")  # Err(ValueError(...))
  ```
  """
  if not exceptions or not all(
    inspect.isclass(exception) and issubclass(exception, BaseException) for exception in exceptions
  ):
    raise TypeError('as_result() requires one or more exception types')

  def decorator(f: Callable[..., R]) -> Callable[..., Result[R, TBE]]:
    @functools.wraps(f)
    def wrapper(*args: ..., **kwargs: Any) -> Result[R, TBE]:
      try:
        return Ok(f(*args, **kwargs))
      except exceptions as exc:
        return Err(exc)

    return wrapper

  return decorator


def as_async_result(
  *exceptions: type[TBE],
) -> Callable[[Callable[..., Awaitable[R]]], Callable[..., Awaitable[Result[R, TBE]]]]:
  """
  Decorator that converts an async function to return Result, catching specified exceptions as Err.

  Use when you want to convert async exception-based APIs to Result-based APIs.
  Essential for integrating async codebases. Avoid when async functions already return Results.

  ```
  @as_async_result(ValueError)
  async def parse_int_async(x: str) -> int:
      return int(x)
  ```
  """
  if not exceptions or not all(
    inspect.isclass(exception) and issubclass(exception, BaseException) for exception in exceptions
  ):
    raise TypeError('as_result() requires one or more exception types')

  def decorator(
    f: Callable[..., Awaitable[R]],
  ) -> Callable[..., Awaitable[Result[R, TBE]]]:
    @functools.wraps(f)
    async def async_wrapper(*args: ..., **kwargs: Any) -> Result[R, TBE]:
      try:
        return Ok(await f(*args, **kwargs))
      except exceptions as exc:
        return Err(exc)

    return async_wrapper

  return decorator


def is_ok(result: Result[T, E]) -> TypeIs[Ok[T]]:
  """
  Type guard that returns True if the result is Ok, providing type narrowing.

  Use for type-safe conditional logic and when you need type narrowing.
  Essential for type checkers. Prefer result.is_ok() for simple boolean checks.

  ```
  is_ok(Ok(1))  # True
  is_ok(Err("fail"))  # False
  ```
  """
  return result.is_ok()


def is_err(result: Result[T, E]) -> TypeIs[Err[E]]:
  """
  Type guard that returns True if the result is Err, providing type narrowing.

  Use for type-safe conditional logic and when you need type narrowing.
  Essential for type checkers. Prefer result.is_err() for simple boolean checks.

  ```
  is_err(Ok(1))  # False
  is_err(Err("fail"))  # True
  ```
  """
  return result.is_err()


def match(result: Result[T, E], ok_handler: Callable[[T], R], err_handler: Callable[[E], R] | None = None) -> R | None:
  """
  Pattern match on a Result and apply the appropriate handler function.

  This function provides a functional, explicit alternative to Python's pattern matching syntax,
  allowing you to handle both success (`Ok`) and error (`Err`) cases with dedicated handler functions.
  It's especially useful when you want to transform or branch on the contents of a Result
  without unwrapping it or writing conditional logic.

  **When to use:**
  - When you want to handle both success and error cases in a single, readable expression.
  - When you want to transform a Result into another value or type, e.g., for logging, formatting, or fallback logic.
  - When you want to avoid `try/except` and keep error handling explicit and composable.

  **When not to use:**
  - When you only care about the success value and want to fail fast (use `unwrap` or `unwrap_or`).
  - When you only want to transform the success or error value (use `map` or `map_err`).
  - When you need to propagate the Result further without handling it yet.


  ```
  result = get_user_age()  # Returns Result[int, str]
  formatted = match(
      result,
      ok_handler=lambda age: f"User is {age} years old",
      err_handler=lambda err: f"Error getting age: {err}"
  )
  # Ok case: "User is 25 years old"
  # Err case: "Error getting age: Invalid user data"
  ```
  """
  if result.is_ok():
    return ok_handler(result.unwrap())
  elif err_handler is not None:
    return err_handler(result.unwrap_err())
  return None


def do(
  fn_or_gen: Callable[..., Generator[Result[T, E], T, R]] | Generator[Result[T, E], T, R],
) -> Callable[[], Result[R, E]] | Result[R, E]:
  """
  Dual-purpose function for emulating do-notation with Result types.

  Use as a decorator for functions that yield Results, or as a helper for generators.
  Essential for imperative-style Result handling. Avoid when simple chaining suffices.
  Can be used as a decorator or called directly with a generator instance.

  ```
  @do
  def my_func() -> Generator[...]:
      x = yield Ok(2)
      y = yield Ok(3)
      return x + y

  my_func()  # Ok(5)
  ```
  """
  if isinstance(fn_or_gen, Generator):
    # Helper usage: do(my_generator)
    return _run_do(fn_or_gen)

  if callable(fn_or_gen):
    # Decorator usage: @do
    fn = fn_or_gen

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Result[R, E]:
      gen = fn(*args, **kwargs)
      return _run_do(gen)

    return wrapper

  raise TypeError('do() must be used as a decorator or called with a generator instance.')


def do_async(
  fn_or_gen: Callable[..., AsyncGenerator[Result[T, E], None]] | AsyncGenerator[Result[T, E], None],
) -> Callable[..., Awaitable[Result[T, E]]] | Awaitable[Result[T, E]]:
  """
  Dual-purpose function for emulating async do-notation with Result types.

  Use as a decorator for async functions that yield Results, or as a helper for async generators.
  Essential for imperative-style async Result handling. Avoid when simple async chaining suffices.
  Can be used as a decorator or called directly with an async generator instance.

  ```
  @do_async
  async def my_func() -> AsyncGenerator[...]:
      x = yield Ok(2)
      y = yield Ok(3)
      return x + y
  ```
  """
  if inspect.isasyncgen(fn_or_gen):
    return _run_do_async(fn_or_gen)

  if callable(fn_or_gen):
    fn = fn_or_gen

    @functools.wraps(fn)
    async def wrapper(*args: ..., **kwargs: Any) -> Result[T, E]:
      async_gen = fn(*args, **kwargs)
      return await _run_do_async(async_gen)

    return wrapper

  raise TypeError('do_async() must be used as a decorator or called with an async generator.')


def catch(
  *errors: type[E],
) -> Callable[[Callable[..., T]], Callable[..., Result[T, E]]]:
  """
  Decorator that catches specified exceptions and returns them as Err Results.

  Use when you want to convert specific exceptions to Results without catching all exceptions.
  More precise than as_result for targeted exception handling. Avoid when you need to catch all exceptions.

  ```
  @catch(ValueError)
  def parse(x: str) -> int:
      return int(x)
  ```
  """

  def decorator(func: Callable[..., T]) -> Callable[..., Result[T, E]]:
    @functools.wraps(func)
    def wrapper(*args: ..., **kwargs: Any) -> Result[T, E]:
      try:
        result = func(*args, **kwargs)
      except errors as e:
        return Err(e)
      return Ok(result)

    return wrapper

  return decorator


def catch_async(
  *errors: type[E],
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[Result[T, E]]]]:
  """
  Decorator that catches specified exceptions in async functions and returns them as Err Results.

  Use when you want to convert specific async exceptions to Results without catching all exceptions.
  More precise than as_async_result for targeted exception handling. Avoid when you need to catch all exceptions.

  ```
  @catch_async(ValueError)
  async def parse_async(x: str) -> int:
      return int(x)
  ```
  """

  def decorator(
    func: Callable[..., Awaitable[T]],
  ) -> Callable[..., Awaitable[Result[T, E]]]:
    @functools.wraps(func)
    async def wrapper(*args: ..., **kwargs: Any) -> Result[T, E]:
      try:
        result = await func(*args, **kwargs)
      except errors as e:
        return Err(e)
      return Ok(result)

    return wrapper

  return decorator


def _run_do(gen: Generator[Result[T, E], None, R]) -> Result[T | R, E]:
  """
  Internal helper for executing do-notation generators and handling Result flow control.

  Manages the generator execution, unwrapping Ok values and short-circuiting on Err values.
  Essential for do-notation implementation. Not intended for direct use.
  """
  try:
    value = None
    while True:
      res = gen.send(value)
      if isinstance(res, Err):
        return res
      value = res.unwrap()
  except StopIteration as e:
    return Ok(e.value)


async def _run_do_async(gen: AsyncGenerator[Result[T, E], None]) -> Result[T, E]:
  """
  Internal helper for executing async do-notation generators and handling Result flow control.

  Manages the async generator execution, unwrapping Ok values and short-circuiting on Err values.
  Essential for async do-notation implementation. Not intended for direct use.
  """
  try:
    value = None
    while True:
      res = await gen.asend(value)
      if isinstance(res, Err):
        return res
      value = res.unwrap()
  except StopAsyncIteration:
    return Ok(cast(T, value))
