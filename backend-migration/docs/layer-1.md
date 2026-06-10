# Layer 1: Domain Models, Schemas, And Provenance

Layer 1 defines what metadata *means* in this backend: the internal `SoftwareMetadata` model, maSMP/CodeMeta export rules, and provenance (which extraction sources may set which fields and with what default confidence).

It does not call GitHub/GitLab, read files, or serve HTTP. Those belong to outer layers.

## What is a domain?

The main domain is **research software metadata**: repository URL, authors, license, programming languages, citations, releases, documentation, archival links, and related concepts.

The package layout leaves room for additional domains later (for example training materials) without overloading the software model:

```text
app/layer_1/
|-- entities/
|-- schemas/
`-- provenance/
```

## What is an entity?

An **entity** is a core domain model, not a database row or an API DTO.

The central entity is **`SoftwareMetadata`**: an internal worksheet that extraction steps fill from every source.

```text
GitHub / GitLab API
CITATION.cff
README
LICENSE
OpenAlex, Zenodo, Wayback, Software Heritage
      |
      v
SoftwareMetadata
      |
      v
maSMP or CodeMeta JSON-LD (at export time)
```

`SoftwareMetadata` is not a copy of maSMP or CodeMeta. Shared fields (`name`, `author`, `license`, …) are extracted once. Schema-specific fields use explicit prefixes (`masmp_*`, `codemeta_*`) when the meaning is tied to one export schema.

**Shared primitives** (`Person`, `License`, `ReferencePublication`, `VersionControlSystem`, …) live under `entities/shared_primitives/`.

**FAIR assessment** result types live under `entities/fair_assessment/`. The scoring logic runs in Layer 3 (`evaluators/`); Layer 1 only defines the result shape.

## What is a schema?

A **schema** is an output vocabulary (maSMP or CODEMETA). Layer 1 holds export field lists and JSON-LD context definitions under `app/layer_1/schemas/`.

```text
SoftwareMetadata  -->  JSONLDBuilder  -->  maSMP or CodeMeta document
```

`schemas/definitions.py` maps schema names to context, node types, and allowed export keys.

## What is provenance?

**Provenance** records where a value came from and how trustworthy that source is.

The software provenance package (`app/layer_1/provenance/software/`) defines:

- **Source ids** — `github_api`, `citation_cff`, `openalex`, … (`defaults.py`)
- **Confidence defaults** per source (`defaults.py`)
- **Property → allowed sources** (`sources.py`)
- **`MULTI_SOURCE_PROPERTIES`** — fields that can accumulate several sources (`author`, `keywords`, `identifier`, …)

```text
Pipeline (Layer 3) decides which extractors run.
Provenance (Layer 1) defines valid sources and default confidence.
Merge steps (Layer 3) record which sources actually contributed.
```

Provenance rules live in Python (version-controlled, testable), not in runtime user configuration.

## Adding a new schema (same domain)

1. Compare new schema fields to existing `SoftwareMetadata` fields.  
2. Reuse fields when the meaning matches.  
3. Add new fields only when needed; use schema prefixes for schema-specific concepts.  
4. Add `app/layer_1/schemas/<schema>/` with `export_fields.py`.  
5. Register in `schemas/definitions.py`.  
6. Extend `JSONLDBuilder` and composer profiles as needed.

## Adding a new domain

Use a separate domain when the subject is **not** research software (for example training materials).

1. New entity package under `entities/`.  
2. Domain-specific schemas and `provenance/<domain>/` if rules differ.  
3. Reuse shared primitives where meanings align.  
4. Compose Layer 3 steps for the new domain without changing the software pipeline unintentionally.

## Adding a new extraction source

1. Add source id and confidence in `provenance/software/defaults.py`.  
2. Add the source to relevant properties in `provenance/software/sources.py`.  
3. Implement extract/merge steps in Layer 3 that call `record_field` or `record_field_provenance` with that source.  
4. Add tests for provenance and extraction metadata.

## Design principles

Layer 1 answers:

- Is this a core domain concept?  
- Is this an export/schema rule?  
- Is this a provenance policy?

If not, the change belongs in an outer layer.

## Where to read next

- [Layer 2](layer-2.md) — orchestration  
- [Layer 3](layer-3.md) — pipelines and steps  
