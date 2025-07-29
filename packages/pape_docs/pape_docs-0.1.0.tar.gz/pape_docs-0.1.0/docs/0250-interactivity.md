# Robust interactivity

A **functionality note** created on **July 5, 2025**

## Status

Accepted. Implementation has not started.

## The note

The `new-doc` script should take an option about non-interactivity. The default should be to run interactively.

If the non-interactive option is provided, the script should:

- Throw an error if any required arguments that have no default value (this should just be the short title) are missing.
- Never interactively ask for any arguments. Never hang asking for input.

Otherwise, the script should function interactively:

- Ask for required arguments that have no defaults. Keep re-asking if the user provides an invalid response.
- For everything else, provide reasonable defaults that are used in case of empty responses. If the user provides a non-empty, invalid response, re-ask for a valid response.

## `click`

This functionality might compete with/be redundant with `click`'s functionality of specifying arguments as required or not. I'll need to figure out how to make this proposed functionality play well with `click`.

Maybe to resolve this, the function decoration options can all be `required=False`, and the name of each can have the suffix `_from_invocation` (or something) to indicate that the option came from the script invocation rather than from an interactive request.
