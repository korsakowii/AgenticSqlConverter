# Open-Source Boundary

This document defines what may enter the AgenticSqlConverter repository
and what must stay out. It is the rule that every commit, prompt,
example, test fixture, and design note is checked against.

## Operating Principle

AgenticSqlConverter is an independent open-source toolkit. Its only
inputs are public SQL standards, public dialect documentation, public
SQLGlot APIs, and original work. No code, prompt, schema, query, naming
convention, account model, infrastructure assumption, or workflow
specific to any non-public organization belongs in this repository,
regardless of who authored it.

## What May Enter the Repository

- Source code authored from scratch against public references.
- SQL fixtures hand-written for testing, or drawn from SQLGlot's public
  test corpus, public tutorials, standards material, or public dialect
  documentation.
- Prompt templates written from scratch and committed under version
  control. Prompts must be generic — they describe SQL dialect
  translation, not any specific company's data.
- Documentation that explains the toolkit's behavior in generic terms.
- Configuration examples that use placeholder values
  (`LLM_API_KEY=...`, `your_target_dialect_here`) and never real
  credentials or real endpoints.
- Examples and demos that use synthetic table names like `users`,
  `orders`, `events`, `sessions`.

## What May Not Enter the Repository

- SQL drawn from any private codebase, private query log, or private
  data warehouse — even after renaming columns. Structural
  fingerprints (join shapes, CTE compositions, naming patterns) carry
  information.
- Schema definitions, table inventories, or column taxonomies sourced
  from any private system.
- Prompt text copied or adapted from any private prompt library.
- Internal documents, design docs, runbooks, or wiki content from any
  organization, including paraphrased versions.
- Code adapted from any non-public source repository, including
  snippets, helper functions, or test scaffolding.
- Account models, account hierarchies, permission schemes, routing
  assumptions, or deployment flows from any private environment.
- Identifiers — project names, product names, internal codenames — that
  are private to any organization.
- Customer data, employee data, or any personally identifiable
  information.
- Credentials, tokens, internal hostnames, internal URLs, or VPN-only
  endpoints.

## Boundary Tests

When in doubt about a contribution, ask:

1. **Origin test.** Can the author point to a public source, such as
   SQLGlot documentation, SQL standard references, public dialect
   documentation, a public blog, or their own prior public work, that
   justifies this code or text? If the only source is a private system,
   it does not enter the repository.
2. **Generality test.** Does this feature, prompt, or example describe
   "translate SQL of this shape" or does it describe "translate SQL
   that looks like the queries at company X"? Only the first form is
   in scope.
3. **Substitution test.** If every identifier in this contribution were
   replaced with a fresh random word, would it still make sense as a
   piece of a generic SQL toolkit? If the example only makes sense
   because of the specific names used, it is not generic.
4. **Public-doc test.** For any rewrite rule that targets a specific
   dialect, is the rule grounded in public documentation or in widely
   known SQL standards? Rules that encode private workarounds are out
   of scope.

A contribution must pass all four tests.

## Synthetic Example Set

The repository's example fixtures use this generic universe:

```text
Tables:    users, orders, events, sessions, products, payments
Keys:      user_id, order_id, event_id, session_id, product_id
Time:      created_at, updated_at, event_ts, order_ts
Status:    status ∈ {active, inactive, pending, completed}
Amounts:   total_amount, unit_price, quantity
```

This universe is intentionally bland. It is the same shape used in SQL
tutorials and public dialect documentation. It is rich enough to
exercise joins, window functions, CTEs, set operations, and date
arithmetic without resembling any specific organization's data.

## Non-Goals

This repository is deliberately limited to generic SQL dialect migration.
It is:

- **Not a data assistant.** It does not answer business questions,
  summarize data, or interpret query results.
- **Not a business-view assistant.** It does not depend on semantic
  layers, metric catalogs, dashboards, or BI tooling.
- **Not an internal workflow automation tool.** It does not orchestrate
  approvals, ticketing, deployments, or review processes.
- **Not tied to any proprietary schema or private account model.** It treats
  identifiers as opaque SQL names and does not encode private data
  models.
- **Not dependent on company infrastructure.** It does not require
  private networks, private endpoints, private identity providers, or a
  hosted control plane.

## Process for Borderline Cases

If a contributor needs to add an example that came to mind from
private work, they should:

1. Strip the example to its SQL skeleton.
2. Re-author it from scratch against the synthetic universe above.
3. Verify the new version does not preserve the original column
   ordering, naming pattern, or join structure. Same logical SQL
   feature, different surface.
4. If they cannot do step 3 without losing the test value, the example
   does not belong here. They should use SQLGlot's corpus instead.

## Prompt Hygiene

Prompts in `agentic_sql_converter/prompts/` describe the task in
dialect-agnostic terms:

- "Translate the following source-dialect CTE to the target dialect."
- "Identify functions that have no direct equivalent in the target
  dialect."

Prompts must not contain:

- Names of private tables, columns, schemas, or projects.
- Examples of "good" or "bad" SQL drawn from any private system.
- Style rules that encode an organization's internal conventions
  rather than published vendor guidance.

## Audit Trail

The repository's git history, the
[`docs/project_origin_and_scope.md`](./project_origin_and_scope.md)
document, and this boundary document together constitute the audit
trail. If a question arises about whether a piece of work originated
here or elsewhere, the git timeline of this repository is the
reference.

## Enforcement

This boundary is enforced by:

- The author, before each commit, against the four boundary tests.
- Code review on every pull request from outside contributors.
- A periodic sweep of `prompts/`, `examples/`, and `tests/` fixtures
  to confirm they remain inside the synthetic universe.
