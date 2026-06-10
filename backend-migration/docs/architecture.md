# Architecture

CoMET-RS uses a layered architecture so each part has a clear job:

- **Layer 1** — internal data model, export schemas, provenance rules  
- **Layer 2** — orchestration (which pipeline to run for a request)  
- **Layer 3** — extraction steps (fetch, parse, enrich, merge into `SoftwareMetadata`)  
- **Layer 4** — HTTP API (FastAPI routes and response shaping)

Dependencies point inward: outer layers use inner layers; `SoftwareMetadata` does not import FastAPI or GitHub clients.

## The big picture

A repository URL enters the system; information is collected from platform APIs, repository files, and external services; everything is stored in one internal `SoftwareMetadata` object; the result is exported as maSMP or CodeMeta JSON-LD.

```text
API or CLI request
      |
      v
Use case orchestration (Layer 2)
      |
      v
Composer-built extraction pipeline (Layer 3)
      |
      v
Extract steps + merge steps
      |
      v
SoftwareMetadata (Layer 1)
      |
      v
JSON-LD export (Layer 3 builder) + API response (Layer 4)
```

The backend extracts shared fields once into `SoftwareMetadata`, then projects them into the requested schema (maSMP or CODEMETA).

### One HTTP request

```text
Layer 4  FastAPI route (e.g. GET /api/metadata/enriched)
    →
Layer 2  ExtractMetadataUseCase (compose pipeline, run it, build JSON-LD)
    →
Layer 3  Extraction steps (candidates in state.data, merges into metadata)
    →
Layer 4  build_enriched_metadata() and Pydantic response models
```

See [Layer 2](layer-2.md) and [Layer 3](layer-3.md) for detail.

## The four layers

**Layer 1** defines `SoftwareMetadata`, shared value objects (`Person`, `License`, …), schema export rules, and the software provenance registry (which sources may set which fields).

**Layer 2** runs `ExtractMetadataUseCase`: detect platform, compose the pipeline, run it, call `JSONLDBuilder`, return JSON-LD and optional extraction metadata.

**Layer 3** implements the pipeline: GitHub/GitLab steps, CFF/README/license parsers, OpenAlex/Zenodo/Wayback/Software Heritage steps, property-level merge steps, and `extraction_metadata` for per-field source/confidence.

**Layer 4** exposes `/api/*` endpoints, wires services to the use case, and builds `enriched_metadata` for the UI.

## Dependency direction

```text
Layer 4: API
    |
    v
Layer 2: Use cases
    |
    +--> Layer 3: steps, composers, builders, evaluators
    |
    v
Layer 1: Domain
```

## Extending the system

| Change | Main touchpoints |
|--------|------------------|
| New repository platform | Layer 3 platform steps + composer profile + URL matcher |
| New output schema | Layer 1 schema package + JSON-LD builder export fields |
| New metadata property | Layer 1 entity + provenance + Layer 3 extract/merge steps |
| New API behavior | Layer 4 routes/services |

## Where to read next

- [Getting started](getting-started.md) — run the API and MkDocs locally  
- [Layer 1](layer-1.md) — entities, schemas, provenance  
- [Layer 2](layer-2.md) — use cases  
- [Layer 3](layer-3.md) — pipelines and steps  
- [Layer 4](layer-4.md) — HTTP API  
