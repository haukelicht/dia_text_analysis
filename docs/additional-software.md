# Do I need Rust, C++, CUDA, or other software?

For setups with complete prebuilt-package coverage in the [README compatibility table](../README.md#computer-setup), **Rust, C/C++ compilers, and a CUDA Toolkit are not expected to be needed for the locked Python installation**. Compiled dependencies have compatible **wheels** (ready-to-install packages) in the lockfile. On macOS, we install Apple's Command Line Tools to obtain Git if it is missing; the Python packages themselves do not require those tools for wheel installation.

- **Windows runtime libraries:** PyTorch may need the **Microsoft Visual C++ Redistributable**. If importing `torch` gives a missing-DLL or runtime error, install the latest **X64** redistributable from [Microsoft's official download page](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist), reopen VS Code, and repeat the check. This is a runtime library, distinct from the full Visual Studio C++ development tools. See also [PyTorch's Windows FAQ](https://docs.pytorch.org/docs/main/notes/windows.html#import-error).
- **GPU exercises:** installation does not guarantee that your laptop can run every GPU exercise. An NVIDIA GPU needs a compatible driver for CUDA use; specialised `bitsandbytes` operations have hardware requirements. Follow the instructor's guidance for those exercises. See the [installation guide for the locked bitsandbytes version](https://huggingface.co/docs/bitsandbytes/v0.50.2/en/installation).
- **Later downloads:** some notebooks download NLTK resources or model files when first run. Those need internet access and disk space beyond the Python installation.

The [dependency compatibility notes](setup-dependencies.md) distinguish basic and neural dependencies, explain native-code requirements, and list the remaining neural-package gaps for Intel Macs and Windows ARM64. The supported neural targets are also documented in [pyproject.toml](../pyproject.toml) with uv checks for wheel-only packages.


[Return to the setup instructions](../README.md#computer-setup).
