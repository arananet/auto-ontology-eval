# Blueprint: auto-ontology-eval

Catalog blueprint: Python service (python-service)

## Idea
Executed evaluation of NVIDIA Auto Ontology as an enterprise semantic layer

## Stack
- Python 3.11+
- standard library first
- unittest or pytest

## Structure
- src package with one module per responsibility
- tests/ mirroring the package
- .openspec/specs/ with one spec per capability
- brain/ seeded from the idea brief

## First specs
- core-service

## Notes
Default for small APIs, CLIs and automation. Add a framework only when a spec needs it.

Pipeline: greenfield. Next station after intake is blueprint review of this file, then spec-writer.
