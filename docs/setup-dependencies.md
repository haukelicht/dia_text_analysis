# Python dependency compatibility notes

Checked on **6 October 2026** using this project's [pyproject.toml](../pyproject.toml), [.python-version](../.python-version), and [uv.lock](../uv.lock). Students should start with the [README setup instructions](../README.md#computer-setup).

## What was checked

The project uses **CPython 3.13**. Its lockfile was successfully exported with `uv export --locked`, so uv accepted it as consistent with the project metadata. The exported requirements' environment markers were evaluated for Windows and macOS on Python 3.13. Wheel filenames recorded in the lockfile were checked against compatible CPython and platform tags using Python's `packaging` library, including `abi3` and universal wheels.

This checks availability of compatible package files, not whether every exercise runs on each platform. No fresh Windows or Intel Mac installation was performed.

Both configurations were installed in separate temporary Python 3.13.5 environments on Apple silicon with third-party source builds disabled. Basic validation passed imports, scikit-learn and statsmodels model fitting, Argon2 password hashing, YAML parsing, and plotting. Neural validation passed imports of the main neural libraries and inference with a small randomly initialized CPU transformer. These checks did not download pretrained models, test GPU execution, or run every exercise. The existing project environment was left in place; follow the README's upgrade instructions to recreate it with Python 3.13.

## Basic and neural configurations

`[project.dependencies]` defines the basic setup for Block 1, installed with `uv sync --locked --no-install-project`. `[project.optional-dependencies].neural` adds sentence embeddings, neural topic modelling, and transformer training, installed with `uv sync --locked --no-install-project --extra neural`. Although packaged as an extra, the neural setup is required from Block 2 onwards. Students should try installing and checking it before Block 2 and email **hauke.licht@uibk.ac.at** if they encounter installation issues.

The extra contains `accelerate`, `bertopic`, `bitsandbytes`, `datasets`, `hdbscan`, `protobuf`, `sentence-transformers`, `sentencepiece`, `tokenizers`, `torch`, `transformers`, and `umap-learn`. The basic setup retains data analysis, traditional machine learning, notebooks, and API clients including `openai` and `huggingface-hub`. The basic export contains no PyTorch, Transformers, BERTopic, Numba, or LLVM dependencies, including transitively. The lockfile now contains 203 package entries for Python 3.13. `tiktoken` was removed entirely because it has no published Windows ARM64 wheels and is not used in the current course code or notebooks. Selecting Python 3.13 also removes older Python-specific branches from the lockfile.

| Target (CPython 3.13) | Basic setup | With `--extra neural` |
| --- | --- | --- |
| Windows x64 | All 141 active third-party dependencies have compatible wheels. | All 179 have compatible wheels. |
| Native Windows ARM64 | All 141 active third-party dependencies have compatible wheels. | No compatible wheels for `torch`, `hdbscan`, or `pyarrow`. `torch` has no source archive in the lockfile. |
| macOS 14+, Apple silicon | All 142 active third-party dependencies have compatible wheels. | All 180 have compatible wheels. |
| macOS 13, Apple silicon | All 142 active third-party dependencies have compatible wheels. | `torch==2.12.1` and `bitsandbytes==0.50.2` require macOS 14+ wheels; neither has a source archive in this lockfile. |
| macOS 13+, Intel | All 142 active third-party dependencies have compatible wheels. | No compatible wheels for `torch`, `bitsandbytes`, `numba`, or `llvmlite`. `torch` and `bitsandbytes` have no source archives in the lockfile. |

The basic setup now has complete wheel coverage on all four OS/processor combinations. Python 3.13 supplies native Windows ARM64 wheels for the locked PyYAML and statsmodels releases. Intel macOS has an explicit platform-dependent `argon2-cffi-bindings==25.1.0` requirement because 26.1.0 lacks Intel Mac wheels. uv currently selects 25.1.0 across the resolution, although the explicit pin applies only to Intel macOS. Sources: [PyYAML files](https://pypi.org/project/PyYAML/6.0.3/#files), [statsmodels files](https://pypi.org/project/statsmodels/0.15.0/#files), and [Argon2 bindings 25.1.0 files](https://pypi.org/project/argon2-cffi-bindings/25.1.0/#files).

These limits are **inferred from actual locked artifacts**, rather than general library support claims. Installing compilers will not resolve a missing PyTorch distribution. Windows x64 emulation on ARM was not assessed. Full neural support on Intel Macs or native Windows ARM64 still needs different dependency versions or an alternative environment; students should not independently downgrade packages to bypass errors.

## Platform metadata in pyproject.toml

`[tool.uv].required-environments` declares Windows x64 and Apple silicon macOS with Python 3.13 as required wheel targets. During locking, uv checks packages without source distributions, such as PyTorch, against these targets. The setting includes optional dependencies in resolution; it **does not** exclude other platforms, guarantee wheels for packages with source archives, or encode the macOS 14 minimum. That minimum is documented in comments and checked through the actual wheel tags. See [uv's required-environments documentation](https://docs.astral.sh/uv/concepts/projects/config/#required-environments).

The Intel Mac Argon2 requirement uses a dependency marker to express a platform-specific version. An extra selects course functionality; it does not automatically pick older compatible versions for unsupported computers. See [uv's dependency documentation](https://docs.astral.sh/uv/concepts/projects/dependencies/).

Keep `--extra neural` on subsequent full-environment syncs: `uv sync --locked --no-install-project` alone removes neural-only packages. Both configurations use the same `.venv` and `uv.lock`.

## Native code and additional software

A **wheel** contains an already-built package. A package can contain Rust, C, or C++ code without requiring students to install a compiler. For configurations with complete wheel coverage above, the relevant `uv sync --locked --no-install-project` command should use those wheels. The repository currently declares the Python build backend `uv_build`, but the expected local course module is absent. The documented sync commands therefore use `--no-install-project` to install only third-party dependencies. Subsequent commands use `uv run --no-sync` so they do not trigger a build of the missing module. No placeholder source module is needed. See [uv’s project-installation options](https://docs.astral.sh/uv/concepts/projects/sync/#not-installing-the-current-project).

| Dependency or group | Additional software considerations |
| --- | --- |
| `tokenizers`, `pydantic-core`, `safetensors`, `hf-xet` | Contain Rust components. Compatible locked wheels avoid Rust compilation. For example, [Tokenizers' source installation](https://huggingface.co/docs/tokenizers/main/en/installation) requires Rust. |
| `sentencepiece` | Contains C++ code; source builds need CMake and a C++ compiler. The [official Python instructions](https://github.com/google/sentencepiece/blob/master/python/README.md) distinguish wheel installation from source builds. Compatible wheels are present for the supported course targets. |
| `numpy`, `scipy`, `pandas`, `scikit-learn`, `statsmodels`, `hdbscan`, `matplotlib`, `pyarrow`, and other compiled dependencies | Use native code. Source builds can require C/C++ or Fortran compilers and additional build libraries. Supported course targets have compatible locked wheels; no source-build toolchain is expected for setup. |
| `numba` and `llvmlite` (used by UMAP/BERTopic) | Wheels include required LLVM components. Students do not need a separate LLVM installation for wheel installation; see [Numba's installation guide](https://numba.readthedocs.io/en/stable/user/installing.html). Source builds have additional requirements. |
| `torch` | Uses native libraries. On Windows, missing runtime DLLs may require the [latest X64 Microsoft Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist); see [PyTorch's Windows FAQ](https://docs.pytorch.org/docs/main/notes/windows.html#import-error). This runtime is distinct from C++ Build Tools. |
| `bitsandbytes` | The locked release has Windows x64 and macOS 14+ ARM64 wheels. Its [version-specific installation guide](https://huggingface.co/docs/bitsandbytes/v0.50.2/en/installation) describes hardware/backend limits and C++/CMake requirements for source builds. Compiler versions in its wheel-build table describe how the wheels were built, not software every user must install. |

A GPU is not needed to install the environment or run basic Python and notebook checks. GPU-dependent exercises need suitable hardware, drivers, and a supported backend; wheel availability alone does not establish that. Do not install a CUDA Toolkit as part of the general student setup.

**Quarto is separate software**, installed with its official Windows/macOS installer. The VS Code extension and Python lockfile do not install the Quarto application. A TeX distribution is an output-format requirement for some PDF workflows, not a requirement for Python packages or HTML rendering.

Some notebooks download NLTK resources and Hugging Face models when executed. These are data/model downloads, rather than compiler dependencies, and need additional internet access and storage.
