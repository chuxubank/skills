---
name: agent-collaboration
description: >-
  Routes explicitly requested agent collaboration across direct work, focused
  headless Grok delegation, Pi subagents, and Herdr. Use when the user asks to
  delegate, coordinate agents, run parallel reviewers or researchers, use
  Herdr or Pi subagents, or choose a collaboration backend. Do not use for
  ordinary single-agent tasks.
---

# Agent Collaboration

Choose the smallest route that provides the fresh judgment, parallelism, or
durable observation the user requested. A skill defines the workflow; the
selected backend owns execution.

## Route the work

1. **Direct work** is the default when the task does not benefit from an
   independent judgment or concurrent lane.
2. **One focused delegate** uses the host's native one-off delegation when
   available. When the user requests Grok, invoke `grok-subagent`; do not
   duplicate its CLI and central-review procedure here. If the current agent is
   already Grok, work directly unless a fresh isolated judgment is material.
3. **Pi subagents** fit two or more independent read-only lanes or a
   scout-worker-fresh-reviewer loop. Use this route only when Pi's `subagent`
   tool is available. Otherwise recommend it without pretending to execute it.
4. **Herdr** is a top-level session control surface. Control it only when the
   user explicitly asks for Herdr, then invoke the `herdr` skill. A Herdr-hosted
   Pi session may own Pi children; Herdr observes that lifecycle rather than
   becoming a second child orchestrator.

If the preferred backend is unavailable, state that constraint and use the
smallest available route that preserves the requested independence. Ask before
switching to a materially different model, service, repository, or execution
scope.

## Preserve ownership

- Keep exactly one writer in a working tree. Put parallel writers in isolated
  worktrees created before delegation.
- Give scouts and reviewers fresh context and read-only authority. A single
  writer may inherit or fork the approved plan when that context is useful.
- Start a fresh mutation agent instead of reusing a bloated long-lived session.
- Give every delegate one bounded outcome, relevant paths, existing changes to
  preserve, exact verification, and a stopping condition.
- Keep nested delegation off unless the task defines a bounded fan-out and one
  parent remains responsible for synthesis.
- For analysis, review, or planning requests, keep every delegate read-only.

The top-level owner independently reads the final diff, runs the required
checks, resolves conflicting reports, and owns commit, push, publication, and
other external effects unless the user explicitly assigns them elsewhere.

## Complete the collaboration

Report which route ran, which agents received mutation authority, how isolation
was enforced, what evidence the owner verified directly, and any work that
still requires user or runtime validation. Completion requires the owner to
account for every changed file and every failed or missing lane.
