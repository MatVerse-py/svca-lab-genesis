# Seed Anchoring Methodology

**MatVerse Node**

**Authors**: Mateus Arêas [1], Manus AI  
**Date**: February 17, 2026  
**Version**: 1.0.0  
**Status**: Certified / Executable Artifact

## Purpose

This document describes the deterministic methodology used to anchor the physical seed of the MatVerse node to its digital repository, generating the **Ohash (Ontological Hash)**.

## Architecture

The anchoring process follows a strict, deterministic pipeline to ensure that the resulting Ohash is a unique and verifiable representation of the node's identity and state.

**Pipeline:**

1. **Seed Acquisition**: A high-entropy physical seed is acquired from a Physical Unclonable Function (PUF) or a hardware bridge (e.g., RP2040).
2. **Canonical Serialization**: The repository's source files are identified and sorted in a canonical order to ensure a deterministic representation of the code.
3. **Repository Digest**: A SHA3-256 hash is computed over the canonically serialized source files, creating a unique digest of the repository's state.
4. **Domain-Separated Hash**: The physical seed and the repository digest are combined with a domain-specific string (e.g., "MATVERSE_NODE_V1") to prevent semantic collisions.
5. **Ohash Generation**: A final SHA3-256 hash is computed over the domain-separated components, resulting in the Ohash.

## Principles

- **Binding**: The Ohash binds the physical identity of the hardware to the digital state of the software.
- **Determinism**: The process is entirely deterministic; given the same seed and repository state, the same Ohash will always be generated.
- **Verifiability**: Any independent party can verify the Ohash by following the same methodology and using the same inputs.
- **Domain Separation**: The use of domain-specific strings ensures that the Ohash is unique to the MatVerse node and cannot be confused with other cryptographic commitments.

## Implementation

The methodology is implemented in the `genesis/seed_anchor.py` script, which provides a reference implementation for the anchoring process.

## References

1. Mateus Arêas. ORCID: [0009-0008-2973-4047](https://orcid.org/0009-0008-2973-4047).
2. CORE B DAY Protocol Documentation (2026).
3. SVCA Lab: Executable Science with Cryptographic Verification and Adaptive Physical Identity. Zenodo. [DOI: 10.5281/zenodo.18667128](https://doi.org/10.5281/zenodo.18667128)
