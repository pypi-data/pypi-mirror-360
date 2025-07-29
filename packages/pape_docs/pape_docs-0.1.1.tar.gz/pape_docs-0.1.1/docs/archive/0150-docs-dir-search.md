# Search for the docs directory

A **decision and feature request**, created on **July 5, 2025**

## Status

Accepted and completed

## The questions

How should the script locate the directory into which to place new docs?

Should it look for a `pyproject.toml` and look in there for a docs location? Should it look for any kind of `ini` file?

Where do scripts like this typically look for this kind of information? What does Astral do with `uv` and `ruff`?

I don't want to save and load docs directory locations in a `~/.pape-docs` configuration directory or anything. I want minimal overhead.

## Research outcomes

Modern Python tools like `uv` and `ruff` primarily use `pyproject.toml` for project-specific configuration, often under a `[tool.<tool-name>]` section.

They also support dedicated `.toml` files (e.g., `ruff.toml`, `uv.toml`) and hierarchical discovery, where the closest configuration file in the directory tree is used.

User-level configurations are typically stored in standard OS-specific configuration directories (e.g., `~/.config/uv/uv.toml`).

Given the requirement for minimal overhead and project-specific configuration, using `pyproject.toml` is the most suitable approach.

## The plan

The script should locate the docs directory (`docs-dir`) into which to place the note in the following manner:

- Check the `PAPE_DOCS_DIR` environment variable.
    - If found, use it as `docs-dir`.
- Check for `pyproject.toml` in the current working directory and iteratively in parent directories.
    - If we find one, attempt to get the the `tool.pape-docs.docs-dir` value.
        - If we find it, use it as `docs-dir`.
        - If we don't find it, use the directory containing `pyproject.toml` as `docs-dir`.
- Look for a `docs/` directory in the CWD and iteratively in parent directories.
- Tell the users: "The script detected no `PAPE_DOCS_DIR` environment variable, no `pyproject.toml` in the current directory or any of its parents, and no `docs/` directory in the current directory or any of its parents. Please provide a docs directory to use. \[Default: ./docs/\]"

Once we have a `docs-dir` value, check if the directory exists yet. If not, ask the user whether we should create it.

We should only make the docs directory, nothing else --- not even parent directories. If we attempt to create the docs directory, but the parent directory does not exist, throw an error and advise the user: "`{docs-dir}` could not be created because the parent directory does not exist. Fix with `mkdir -p "{docs-dir}"`.
