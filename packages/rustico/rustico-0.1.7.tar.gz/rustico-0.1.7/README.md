# rustico

> **A Schrödinger's Cat for Python error handling: your result is both alive and dead—until you unwrap it.**

## What is `rustico`?

`rustico` brings the power and elegance of Rust's `Result` type to Python. Every operation is either a success (`Ok`) or a failure (`Err`), and you must explicitly handle both. No more try/except hell—just beautiful, predictable, and composable error handling.

## Schrödinger's Cat: The Metaphor

Imagine every function call as a box containing Schrödinger's cat. Until you open (unwrap) the box, the cat is both alive (`Ok`) and dead (`Err`). With `rustico`, you don't have to guess or hope—when you unwrap the result, you'll know exactly what you got, and you'll handle both cases explicitly.

## Key Features

- 🔒 **Can't Forget Error Handling**: The type system forces you to handle both cases
- 📍 **Precise Error Information**: Know exactly what and where things failed
- 🧩 **Composable**: Chain operations without nested try/except blocks
- 🎯 **Early Exit**: Stop processing on first error automatically
- 🔍 **Type Safe**: Your IDE knows about both success and error cases
- ⚡ **Async Support**: First-class support for async/await
- 🧪 **Test Friendly**: Easily mock and test error conditions
- 🔄 **Pattern Matching**: Native support for Python 3.10+ pattern matching

For detailed documentation, see the [full documentation](docs/index.md).
