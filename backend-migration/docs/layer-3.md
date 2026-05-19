# Layer 3: Pipelines, Adapters, And Extraction Steps

Layer 3 is the **extraction engine**: repository and file adapters, external API clients, ordered **pipelines** of **steps**, merge logic, JSON-LD export, and FAIR evaluation.

- **Extract steps** — write candidates to `state.data` (or single-source fields directly to `metadata`).  
- **Merge steps** — combine candidates into `SoftwareMetadata` and record provenance per contributing source.  
- **Composer** — picks the step list for domain × schema × platform.

Layer 2 runs the pipeline; Layer 4 serves HTTP. Layer 1 defines field meanings and provenance rules.

## What is a pipeline?

An **`ExtractionPipeline`** is an ordered tuple of steps. **`ExtractionPipelineRunner`** runs each `run(context, state)` in sequence.

```text
Step 1 -> Step 2 -> ... -> Step N
   same StepContext (immutable)
   same StepState (mutable metadata + data scratchpad)
```

Order matters: a step that reads `state.data["extracted_citation_authors"]` must run after the step that fills it.

## Contracts

| Piece | Location | Purpose |
|-------|----------|---------|
| `StepContext` | `steps/contracts/step.py` | Repo URL, schema, platform, token |
| `StepState` | `steps/contracts/step.py` | `metadata` + `data` dict |
| `ExtractionStep` | `steps/contracts/step.py` | `name` + `run()` |
| `ExtractionPipeline` | `steps/contracts/pipeline.py` | Ordered steps |
| `ExtractionMetadataCollector` | `extraction_metadata/protocol.py` | Record source/confidence |
| `InMemoryExtractionMetadataCollector` | `extraction_metadata/in_memory.py` | Default collector; dedupes sources in `get_all()` |
| `record_field_provenance` | `extraction_metadata/record.py` | Helper for merge steps |

### Provenance recording

- **Platform steps** that write directly to `metadata` call `record_field(state, field)` (defaults to GitHub/GitLab source).  
- **Merge steps** call `record_field_provenance(state, field, source, confidence)` for each non-empty candidate bucket (citation, OpenAlex, README, Zenodo, …).  
- **Keywords** — platform topics/tags go to `state.data["extracted_platform_keywords"]`; `MergeSoftwareKeywordsStep` merges platform + CFF + OpenAlex and records each source once.  
- The use case provides `state.data["record_field"]` via `_build_record_field()` in Layer 2.

## What is a step?

### Extract steps

Write **candidates** under stable keys, for example:

- `extracted_citation_authors`  
- `extracted_openalex_keywords`  
- `extracted_platform_keywords`  
- `extracted_zenodo_archive_urls`

### Merge steps

Read candidates, deduplicate, set `state.metadata.<field>`, record provenance. Example — authors:

```text
CITATION.cff  --> extracted_citation_authors --\
README bibtex --> all_readme_authors          +--> MergeSoftwareAuthorsStep --> metadata.author
OpenAlex      --> extracted_openalex_authors -/
```

Merge modules live in `steps/merge_steps/software/` (for example `merge_software_authors_step.py`).

### Direct metadata writes

Single-source platform fields (name, description, dates, …) may write straight to `metadata` and call `record_field` when appropriate.

## Step bundles

Functions that return `tuple[ExtractionStep, ...]` for one property or concern:

```text
app/layer_3/steps/step_bundles/
|-- software/
|   |-- authors.py
|   |-- keywords.py
|   |-- identifiers.py
|   |-- alternate_names.py
|   |-- reference_publication.py
|   `-- archived_urls.py
|-- citation_steps.py
`-- readme_steps.py
```

Example:

```text
software_author_steps()
  = ExtractCitationAuthorsStep
  + (optional README / OpenAlex author steps)
  + MergeSoftwareAuthorsStep
```

Bundles accept parameters such as `sources=("citation", "openalex", "readme")` to tune profiles.

## Composer and profiles

`PipelineComposer` in `composers/pipeline_composer.py`:

```text
compose(domain, schema, platform) -> ExtractionPipeline
```

Profiles under `composers/profiles/`:

- `software_github_masmp.py`  
- `software_github_codemeta.py`  
- `software_gitlab_masmp.py`  
- `software_gitlab_codemeta.py`  

Each `build_*_pipeline()` concatenates platform step groups, property bundles, and shared steps (for example `common_platform_steps()`).

## Folder map

```text
app/layer_3/
|-- composers/
|-- extraction_metadata/
|-- builders/              # JSONLDBuilder
|-- evaluators/            # FAIRness from SoftwareMetadata
|-- utils/                 # e.g. URLPatternMatcher
`-- steps/
    |-- contracts/
    |-- step_bundles/
    |-- merge_steps/software/
    `-- extract_steps/
        |-- adapters/platform/   # github/, gitlab/, common/
        `-- services/
            |-- files/           # citation/, readme/, license/, workflows/
            |-- external/        # openalex/, zenodo/, wayback/, software_heritage/
            `-- llm/
```

**`services/files/workflows/`** — `CitationCffWorkflow`, `ReadmeExtractionWorkflow` for grouped file parsing.

**`services/files/citation/helpers/cff_parse.py`** — shared CFF YAML loading (`ensure_cff_yaml_loaded`).

## Adding a new step

1. Choose pattern: candidates in `state.data`, merge to `metadata`, or direct write.  
2. Place under `merge_steps/` or the right `extract_steps/` subtree; file name `*_step.py`, class `*Step`.  
3. Implement `name` and `run(context, state) -> state`.  
4. Wire into a bundle and/or profile; keep producers before consumers.  
5. Record provenance if the field appears in UI enrichment.  
6. Update Layer 1 entity + provenance for new fields.  
7. Add tests (`StepContext` + `StepState`).

## Adding a profile or platform

1. Copy the nearest profile module.  
2. Swap platform step imports.  
3. Register in `PipelineComposer.compose`.  
4. Extend `URLPatternMatcher` and API platform checks if needed.

## Design principles

| Question | Layer |
|----------|-------|
| Network, files, parsers? | 3 |
| Field meaning, allowed sources? | 1 |
| Request sequencing? | 2 |
| HTTP responses? | 4 |

Keep steps small; profiles should read like a table of contents.

## Where to read next

- [Layer 2](layer-2.md) — use case and progress  
- [Layer 4](layer-4.md) — enriched API responses  
- [Layer 1](layer-1.md) — provenance registry  
