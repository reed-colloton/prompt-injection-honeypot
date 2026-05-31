class PromptInjectionHoneypot < Formula
  include Language::Python::Virtualenv

  desc "Dual-agent honeypot that detects and blocks indirect prompt injections"
  homepage "https://github.com/reed-colloton/prompt-injection-honeypot"
  url "https://github.com/reed-colloton/prompt-injection-honeypot/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "5c10b56b03f97d175680e2f45f907e76b178f423f0d9673b3c433490d412f44b"
  license "MIT"

  depends_on "python@3.13"

  # The LangChain / LangGraph dependency tree is large and fast-moving, so rather
  # than pinning ~100 individual `resource` blocks (as a small formula would) we
  # resolve the whole tree from PyPI at install time. That needs network access
  # during the build; the guard keeps the formula loadable on older Homebrews
  # that predate the DSL (where the build sandbox already allows network).
  allow_network_access! :build if respond_to?(:allow_network_access!)

  def install
    venv = virtualenv_create(libexec, "python3.13")
    # Install the package and its full dependency tree (binary wheels) from PyPI.
    system venv.root/"bin/pip", "install", "--disable-pip-version-check", buildpath
    bin.install_symlink venv.root/"bin/honeypot"
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
