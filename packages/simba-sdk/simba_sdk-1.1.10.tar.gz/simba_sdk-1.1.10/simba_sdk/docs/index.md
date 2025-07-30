---
tags:
  - developer tools
---

The SIMBA SDK for Python simplifies creating, managing, and using Ensure features from Python code. This is including but not limited to:

- Creating Decentralised Identity Documents (DIDs)
- Verifiable Credentials (VPs)
- Verifiable Presentations (VPs)
- Publishing Resources
- Access Control to resources using VPs

## Essential Overview
- The minimum supported Python version is 3.8 or later.
- You **must** have been onboarded to a SIMBA environment that has Ensure available to use the SDKs.
- The SIMBA SDK provides all method calls as `async`, providing flexibility for long-running code. ([ref](https://docs.python.org/3/library/asyncio.html))

The SDK is built on two layers:
### The Client layer
This layer utilises OpenAPI specification files to automatically generate Python code that makes requests to the Ensure family of APIs. Schemas, query objects and method calls are provided to help ensure proper validation of any input or output to the endpoints. This layer can be considered unstable in that the APIs change regularly, and without much thought to how they will affect the SDK. Regenerating your clients could regularly result in breaking changes.
### The Sessions layer
This layer wraps the Client layer and provides a degree of abstraction. While the Client code is automatically generated from OpenAPI and not in a sense manually maintained, this layer is. The `Session` classes use the Client layer behind the scenes to interact with the APIs, but bridge the gap between the often-changing schemas and methods, and a more stable set of dataclasses and methods relating to higher-level 'actions' a user might perform on the Ensure system.

It is recommended to use the Session layer for the majority of use cases.
