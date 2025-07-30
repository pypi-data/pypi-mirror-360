# Home

## Mission

Provide a flexible and intuitive way to define Polars data transformations using a JSON-based configuration.

## Vision

Empower users to declaratively build complex data pipelines with Polars, enabling easier versioning, sharing, and understanding of data processing logic.

## Purpose

`polars-as-config` allows you to define a series of data manipulation steps, including Polars operations, custom functions, and variable substitutions, all through a simple JSON structure. This makes it ideal for scenarios where data transformation logic needs to be dynamic, stored externally, or easily understandable by non-programmers.

## Features

*   **Declarative Syntax:** Define Polars operations in a human-readable JSON format.
*   **Extensible:** Easily add and use custom Python functions within your configurations.
*   **Variable Support:** Parameterize your configurations using variables, with support for escaping.
*   **Nested Expressions:** Build complex expressions by nesting operations.
*   **Step-by-Step Execution:** Define a series of transformation steps that are applied sequentially. 