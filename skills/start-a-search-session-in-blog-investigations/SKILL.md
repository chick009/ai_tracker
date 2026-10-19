---
name: Start a search session in blog-investigations
description: >-
  Use this when starting a normal Search session (not Computer) inside the
  Perplexity project blog-investigations, with a query the user supplies.
---
# Start a search session in blog-investigations

Start one Search session in the existing Perplexity project **blog-investigations**. The query is an input. Do not use Computer mode.

Assumes Chrome is already signed in to Perplexity. Do not type credentials.

## Inputs

- `{query}`: the text to send as the new session. Never substitute a placeholder such as "type here". If no query was given, ask for it and stop.

## Steps

1. Open the project: https://www.perplexity.ai/projects/814f1ea0-2efe-4d68-b32a-5db564ed33ca
   The page title is blog-investigations. If a sidebar link named blog-investigations is already visible, that link is equivalent.
2. Focus the session composer at the bottom, placeholder "Start a session in blog-investigations".
3. Set the composer mode to Search. If Computer (or any other mode) is selected, switch it to Search before typing.
4. Replace any existing draft with `{query}` and submit the session.
5. Wait until the answer is on screen. Report the answer text and the session URL.

## Do not

- Do not open or continue a Computer task.
- Do not create a new project.
- Do not submit until `{query}` is the real request the user asked to send.
