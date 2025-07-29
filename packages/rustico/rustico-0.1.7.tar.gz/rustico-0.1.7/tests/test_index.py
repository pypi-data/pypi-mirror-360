import re
from typing import AsyncGenerator, Generator

import pytest

from rustico import (
  Err,
  Ok,
  Result,
  UnwrapError,
  as_async_result,
  as_result,
  catch,
  catch_async,
  do,
  do_async,
  is_err,
  is_ok,
)


class MyCustomError(Exception):
  pass


def sync_div(a: int, b: int) -> Result[float, str]:
  if b == 0:
    return Err('Cannot divide by zero')
  return Ok(a / b)


async def async_div(a: int, b: int) -> Result[float, str]:
  if b == 0:
    return Err('Cannot divide by zero')
  return Ok(a / b)


class TestOk:
  def test_ok_creation_and_value(self):
    """✅ Test: Business Logic - Ok should hold and return its value."""
    ok_val = Ok(42)
    assert ok_val.is_ok()
    assert not ok_val.is_err()
    assert ok_val.ok() == 42
    assert ok_val.ok_value == 42
    assert ok_val.unwrap() == 42
    assert ok_val.expect('Should not fail') == 42
    assert ok_val.err() is None

  def test_ok_equality(self):
    """✅ Test: Business Logic - Ok instances with same value should be equal."""
    assert Ok(10) == Ok(10)
    assert Ok(10) != Ok(20)
    assert Ok(10) != Err(10)
    assert Ok(10) != 10

  def test_ok_map(self):
    """✅ Test: Business Logic - map transforms the inner value."""
    assert Ok(5).map(lambda x: x * 2) == Ok(10)

  @pytest.mark.asyncio
  async def test_ok_map_async(self):
    """✅ Test: System Interactions - map_async transforms value with an async func."""

    async def double(x):
      return x * 2

    assert await Ok(5).map_async(double) == Ok(10)

  def test_ok_and_then(self):
    """✅ Test: Business Logic - and_then chains with another Result-producing function."""
    assert Ok(10).and_then(lambda x: sync_div(x, 2)) == Ok(5.0)
    assert Ok(10).and_then(lambda x: sync_div(x, 0)) == Err('Cannot divide by zero')

  @pytest.mark.asyncio
  async def test_ok_and_then_async(self):
    """✅ Test: System Interactions - and_then_async chains with an async Result func."""
    assert await Ok(10).and_then_async(lambda x: async_div(x, 2)) == Ok(5.0)
    assert await Ok(10).and_then_async(lambda x: async_div(x, 0)) == Err('Cannot divide by zero')

  def test_ok_or_else_is_noop(self):
    """✅ Test: Business Logic - or_else has no effect on Ok."""
    assert Ok(100).or_else(lambda e: Err(f'Error: {e}')) == Ok(100)

  def test_ok_unwrap_err_raises(self):
    """✅ Test: Error Handling - unwrap_err on Ok must raise UnwrapError."""
    with pytest.raises(UnwrapError):
      Ok(10).unwrap_err()

  def test_ok_swap(self):
    """✅ Test: Business Logic - swap turns an Ok into an Err."""
    assert Ok('value').swap() == Err('value')

  def test_ok_value_or(self):
    """✅ Test: Business Logic - value_or returns the value, not the default."""
    assert Ok(42).value_or(0) == 42

  def test_ok_inspect(self):
    """✅ Test: Business Logic - inspect runs a side-effect on Ok value."""
    inspected_val = None

    def side_effect(v):
      nonlocal inspected_val
      inspected_val = v

    result = Ok(123).inspect(side_effect)
    assert result == Ok(123)
    assert inspected_val == 123


class TestErr:
  def test_err_creation_and_value(self):
    """✅ Test: Business Logic - Err should hold and return its error."""
    err_val = Err('epic fail')
    assert err_val.is_err()
    assert not err_val.is_ok()
    assert err_val.err() == 'epic fail'
    assert err_val.err_value == 'epic fail'
    assert err_val.ok() is None

  def test_err_equality(self):
    """✅ Test: Business Logic - Err instances with same value should be equal."""
    assert Err('fail') == Err('fail')
    assert Err('fail') != Err('other fail')
    assert Err('fail') != Ok('fail')

  def test_err_map_is_noop(self):
    """✅ Test: Business Logic - map has no effect on Err."""
    assert Err('fail').map(lambda x: x * 2) == Err('fail')

  @pytest.mark.asyncio
  async def test_err_map_async_is_noop(self):
    """✅ Test: System Interactions - map_async has no effect on Err."""

    async def double(x):
      return x * 2

    assert await Err('fail').map_async(double) == Err('fail')

  def test_err_and_then_is_noop(self):
    """✅ Test: Business Logic - and_then has no effect on Err."""
    assert Err('fail').and_then(lambda x: sync_div(x, 2)) == Err('fail')

  def test_err_or_else(self):
    """✅ Test: Business Logic - or_else transforms an error."""
    assert Err(0).or_else(lambda e: sync_div(10, e + 2)) == Ok(5.0)
    assert Err('fail').or_else(lambda e: Err(f'New error: {e}')) == Err('New error: fail')

  def test_err_unwrap_raises(self):
    """✅ Test: Error Handling - unwrap on Err must raise UnwrapError."""
    expected_message = re.escape("Called `Result.unwrap()` on an `Err` value: 'fail'")
    with pytest.raises(UnwrapError, match=expected_message):
      Err('fail').unwrap()

  def test_err_expect_raises(self):
    """✅ Test: Error Handling - expect on Err raises UnwrapError with a custom message."""
    with pytest.raises(UnwrapError, match="Custom message: 'fail'"):
      Err('fail').expect('Custom message')

  def test_err_swap(self):
    """✅ Test: Business Logic - swap turns an Err into an Ok."""
    assert Err('error').swap() == Ok('error')

  def test_err_value_or(self):
    """✅ Test: Business Logic - value_or returns the default value."""
    assert Err('error').value_or(0) == 0

  def test_err_alt(self):
    """✅ Test: Business Logic - alt transforms the error value."""
    assert Err('oops').alt(str.upper) == Err('OOPS')

  def test_err_map_err(self):
    """✅ Test: Business Logic - map_err is an alias for alt."""
    assert Err('oops').map_err(str.upper) == Err('OOPS')

  def test_err_inspect_err(self):
    """✅ Test: Business Logic - inspect_err runs a side-effect on Err value."""
    inspected_val = None

    def side_effect(e):
      nonlocal inspected_val
      inspected_val = e

    result = Err('error_val').inspect_err(side_effect)
    assert result == Err('error_val')
    assert inspected_val == 'error_val'

  def test_err_trace_capture(self):
    """✅ Test: Error Handling - Err should capture a traceback for exceptions."""

    @as_result(ValueError)
    def func_that_fails():
      raise ValueError('fail')

    result = func_that_fails()
    assert result.is_err()
    assert isinstance(result.err_value, ValueError)
    assert result.trace is not None
    assert isinstance(result.trace, list)
    assert any('ValueError' in line and 'fail' in line for line in result.trace)

  def test_err_trace_is_none_for_non_exceptions(self):
    """✅ Test: Error Handling - Err should not have a trace for non-exception values."""
    result = Err('just a string error')
    assert result.trace is None


# --- Integration Tests for Decorators ---
class TestDecorators:
  def test_as_result_success(self):
    """✅ Test: Critical Paths - @as_result should return Ok on success."""

    @as_result(ValueError)
    def safe_func():
      return 'success'

    assert safe_func() == Ok('success')

  def test_as_result_catches_specified_error(self):
    """✅ Test: Error Handling - @as_result should catch specified exceptions."""

    @as_result(ValueError)
    def safe_func():
      raise ValueError('fail')

    result = safe_func()
    assert result.is_err()
    assert isinstance(result.err_value, ValueError)

  def test_as_result_does_not_catch_unspecified_error(self):
    """✅ Test: Error Handling - @as_result should not catch other exceptions."""

    @as_result(TypeError)
    def safe_func():
      raise ValueError('fail')

    with pytest.raises(ValueError):
      safe_func()

  def test_as_result_requires_exception_types(self):
    """✅ Test: Error Handling - @as_result raises TypeError for invalid args."""
    expected_message = re.escape('as_result() requires one or more exception types')
    with pytest.raises(TypeError, match=expected_message):

      @as_result('not a type')
      def my_func():
        pass

  @pytest.mark.asyncio
  async def test_as_async_result_success(self):
    """✅ Test: Critical Paths - @as_async_result should return Ok on success."""

    @as_async_result(ValueError)
    async def safe_async_func():
      return 'success'

    assert await safe_async_func() == Ok('success')

  @pytest.mark.asyncio
  async def test_as_async_result_catches_error(self):
    """✅ Test: Error Handling - @as_async_result should catch exceptions."""

    @as_async_result(ValueError)
    async def safe_async_func():
      raise ValueError('fail')

    result = await safe_async_func()
    assert result.is_err()
    assert isinstance(result.err_value, ValueError)


# --- Integration Tests for catch Decorators ---
class TestCatchDecorators:
  def test_catch_success(self):
    """✅ Test: Critical Paths - @catch should return Ok on success."""

    @catch(MyCustomError)
    def func():
      return 42

    assert func() == Ok(42)

  def test_catch_handles_error(self):
    """✅ Test: Error Handling - @catch should return Err on specified exception."""

    @catch(MyCustomError)
    def func():
      raise MyCustomError('it failed')

    result = func()
    assert result.is_err()
    assert isinstance(result.err_value, MyCustomError)

  @pytest.mark.asyncio
  async def test_catch_async_success(self):
    """✅ Test: Critical Paths - @catch_async should return Ok on success."""

    @catch_async(MyCustomError)
    async def func():
      return 42

    assert await func() == Ok(42)

  @pytest.mark.asyncio
  async def test_catch_async_handles_error(self):
    """✅ Test: Error Handling - @catch_async should return Err on specified exception."""

    @catch_async(MyCustomError)
    async def func():
      raise MyCustomError('it failed async')

    result = await func()
    assert result.is_err()
    assert isinstance(result.err_value, MyCustomError)


# --- Unit Tests for Do Notation ---
class TestDoNotation:
  # --- Sync `do` decorator tests ---
  def test_do_decorator_success(self):
    """✅ Test: @do decorator succeeds with all Ok values."""

    @do
    def do_logic() -> Generator[Result[int, str], None, int]:
      x = yield Ok(10)
      y = yield Ok(20)
      return x + y

    assert do_logic() == Ok(30)

  def test_do_decorator_failure(self):
    """✅ Test: @do decorator fails on the first Err value."""

    @do
    def do_logic() -> Generator[Result[int, str], None, int]:
      x = yield Ok(10)
      _ = yield Err('something went wrong')
      return x + 1

    assert do_logic() == Err('something went wrong')

  # --- Sync `do` helper function tests ---
  def test_do_helper_success(self):
    """✅ Test: do() helper succeeds with all Ok values."""

    def do_logic() -> Generator[Result[int, str], None, int]:
      x = yield Ok(10)
      y = yield Ok(20)
      return x + y

    assert do(do_logic()) == Ok(30)

  def test_do_helper_failure(self):
    """✅ Test: do() helper fails on the first Err value."""

    def do_logic() -> Generator[Result[int, str], None, int]:
      x = yield Ok(10)
      _ = yield Err('something went wrong')
      return x + 1

    assert do(do_logic()) == Err('something went wrong')

  # --- Async `do_async` decorator tests ---
  @pytest.mark.asyncio
  async def test_do_async_decorator_success(self):
    """✅ Test: @do_async decorator succeeds with all Ok values."""

    @do_async
    async def do_logic() -> AsyncGenerator[Result[int, str], None]:
      x = yield Ok(10)
      y = yield Ok(20)
      yield Ok(x + y)

    assert await do_logic() == Ok(30)

  @pytest.mark.asyncio
  async def test_do_async_decorator_failure(self):
    """✅ Test: @do_async decorator fails on the first Err value."""

    @do_async
    async def do_logic() -> AsyncGenerator[Result[int, str], None]:
      x = yield Ok(10)
      _ = yield Err('async error')
      yield Ok(x + 1)

    assert await do_logic() == Err('async error')

  # --- Async `do_async` helper function tests ---
  @pytest.mark.asyncio
  async def test_do_async_helper_success(self):
    """✅ Test: do_async() helper succeeds with all Ok values."""

    async def do_logic() -> AsyncGenerator[Result[int, str], None]:
      x = yield Ok(10)
      y = yield Ok(20)
      yield Ok(x + y)

    assert await do_async(do_logic()) == Ok(30)

  @pytest.mark.asyncio
  async def test_do_async_helper_failure(self):
    """✅ Test: do_async() helper fails on the first Err value."""

    async def do_logic() -> AsyncGenerator[Result[int, str], None]:
      x = yield Ok(10)
      _ = yield Err('async error')
      yield Ok(x + 1)

    assert await do_async(do_logic()) == Err('async error')

  # --- Edge Case Test ---
  def test_do_raises_on_async_generator(self):
    """✅ Test: Error Handling - sync `do` raises TypeError for async generators."""

    async def async_gen():
      yield Ok(1)

    # Assuming your dual-purpose `do` raises a TypeError for wrong generator type
    with pytest.raises(TypeError):
      do(async_gen())


# --- Unit Tests for Type Guards ---
class TestTypeGuards:
  def test_is_ok(self):
    """✅ Test: Business Logic - is_ok correctly identifies Ok types."""
    assert is_ok(Ok(1)) is True
    assert is_ok(Err(1)) is False

  def test_is_err(self):
    """✅ Test: Business Logic - is_err correctly identifies Err types."""
    assert is_err(Err(1)) is True
    assert is_err(Ok(1)) is False
