class PromptInjectionHoneypot < Formula
  desc "Dual-agent honeypot that detects and blocks indirect prompt injections"
  homepage "https://github.com/reed-colloton/prompt-injection-honeypot"
  url "https://github.com/reed-colloton/prompt-injection-honeypot/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "5c10b56b03f97d175680e2f45f907e76b178f423f0d9673b3c433490d412f44b"
  license "MIT"

  depends_on "python@3.13"

  # The LangChain / LangGraph dependency tree is large and fast-moving, so rather
  # than pinning ~100 individual `resource` blocks (as a small formula would) we
  # create a venv and resolve the whole tree from PyPI at install time. That needs
  # network access during the build; the guard keeps the formula loadable on older
  # Homebrews that predate the DSL (where the build sandbox already allows network).
  allow_network_access! :build if respond_to?(:allow_network_access!)

  # Several deps ship prebuilt Rust extension wheels (pydantic-core, orjson, jiter,
  # tiktoken, ormsgpack, uuid-utils) whose `.so` files have an `@rpath/...` dylib
  # ID and no header padding, so Homebrew can't rewrite the ID to the long opt
  # path. They're loaded by CPython via dlopen by path, so keep the @rpath IDs
  # as-is instead of relocating them.
  preserve_rpath if respond_to?(:preserve_rpath)

  def install
    python = Formula["python@3.13"].opt_bin/"python3.13"
    # A plain venv ships its own pip (offline ensurepip). We then `pip install`
    # the package so its dependencies resolve from PyPI as binary wheels --
    # unlike Homebrew's virtualenv helpers, which force `--no-deps --no-binary`.
    system python, "-m", "venv", libexec
    system libexec/"bin/pip", "install", "--disable-pip-version-check", buildpath
    bin.install_symlink libexec/"bin/honeypot"
  end

  test do
    # With no key configured the CLI prints a welcome banner and then exits 1 on
    # empty input. Clear the keys first so the test is deterministic regardless
    # of the caller's environment.
    ENV.delete("OPENROUTER_API_KEY")
    ENV.delete("TAVILY_API_KEY")
    assert_match "Welcome to the Prompt-Injection Honeypot!",
                 pipe_output("#{bin}/honeypot", "\n", 1)
  end
end
