# Kellu

[English](README.md) · [Español](README.es.md)

**A secure, modular AI assistant for the Kate editor that thinks before it spends tokens.**

> **Status: pre-0.1.0. Being rebuilt from scratch with a security-first design.** An earlier prototype exists and is being ported module by module. APIs, commands and configuration will change. Nothing is installable from PyPI yet. Security model: see [SECURITY.md](SECURITY.md).

---

## What is Kellu?

Kellu brings AI assistance into [Kate](https://kate-editor.org/) without a heavy GUI stack. It is not just a chat with an LLM. A small headless core decides **whether** a model is needed at all, redacts what leaves your machine, routes each task to the right provider with fallback, runs any process-spawning tool inside a sandbox, and talks to the editor through thin frontends.

## Principles

- **Security first, fail closed.** If a protection is unavailable (for example, no sandbox backend), the dangerous capability is disabled instead of silently running unprotected.
- **Least privilege.** Keys live in the OS keyring and are split into tiers. The model never sees secrets. Tools run with the minimum access they need.
- **Untrusted by default.** Files, web pages and stored snippets are data, never instructions.
- **Decision cascade.** Rules, then memory, then the LLM as a last resort. You can always force a model.
- **Modular and frugal.** Standard library first, optional extras, replaceable providers, stores and frontends.
- **Terminal-first.** Validate the core before adding any GUI.
- **Adaptable.** Runs on a modest laptop with cloud providers, or on a workstation with local models.

## Release plan

| Version | Focus | Contents |
|---|---|---|
| **0.1.0** | Secure foundation | Modular core, unified providers (OpenAI-compatible, Google), keyring vault with tiers, redaction and deny globs, risk-based permissions, **sandbox** (bubblewrap), tools (files, sandboxed shell, git), terminal REPL, Kate LSP (hover and completion), `kellu doctor` |
| **0.2.0** | Agent | Agent loop with tool calling and confirmations, rules stage of the cascade, context injection |
| **0.3.0** | Interoperability | OpenAI-compatible local gateway, ACP agent mode |
| **0.4.0** | Memory | Store of accepted solutions (SQLite by default, PostgreSQL + pgvector optional), memory stage |
| **0.5.0** | Adaptation | Local runtime detection (Ollama, LM Studio, llama.cpp), hardware profiles, MCP server and client |
| **Later** | | GUI through existing Kate plugins; Landlock, macOS and Windows sandbox backends |

0.1.0 intentionally has **no autonomous agent loop**: tools, permissions and the sandbox are validated on their own before a model can trigger them.

## Architecture

```
 Terminal   Kate (LSP)   Gateway*   ACP*   MCP*          <- frontends
      \          |          |        |      /
 ============ Kellu core (trusted: keys, network) ============
  scope -> rules* -> memory* -> sanitizer -> router -> provider
                                        \-> tools (risk levels, permissions)
 =============================================================
         |                                   |
  sandbox (bubblewrap):               host side, with confirmation:
  shell, tests, formatters            git and gh writes

  * after 0.1.0
```

The core has no UI and no side effects on import. Frontends, providers and stores are replaceable adapters. Dependency direction: `frontends → core/tools → providers/sandbox/security`.

## Security at a glance

- **Sandbox.** Process-spawning tools run in bubblewrap: no network by default, read-only system, the project as the only writable directory, scrubbed environment, no access to `~/.ssh`, `~/.gnupg` or the keyring bus.
- **Key tiers.** `provider` keys are available to the normal flow. `infra` and `db` secrets (cloud, DNS, databases) are not reachable by the assistant unless explicitly enabled with confirmation.
- **Risk levels.** Every tool is `read`, `write`, `destructive` or `network`. Destructive actions need typed confirmation. Git and GitHub writes run on the host, never inside the sandbox.
- **Data egress.** Deny globs (`.env`, keys, certificates) and secret redaction apply before anything is sent to a provider. A per-project local-only mode is planned.
- **A Python virtual environment isolates dependencies, not security.** The sandbox is what restricts tools.

Details, threat model and limits: [SECURITY.md](SECURITY.md).

## Decision cascade (design, 0.2.0 to 0.4.0)

1. **Rules.** Deterministic handling that needs no model (stack detection, git status, known commands).
2. **Memory.** Search previously accepted solutions. Reuse only if you accepted it or tests passed, above a similarity threshold, and not expired. Reused answers are labeled "from memory".
3. **LLM.** Route by task type to the best provider, with fallback. Force a model with `--model` or an equivalent option.

## Projects and scopes

Projects are discovered under a configurable root and grouped as macro-project, repository and subproject. Each scope can define rules, preferred providers, resource limits and a privacy mode (for example, local-only).

## Quick start

> Commands describe the **target interface** and may change before 0.1.0.

Requirements (Linux first): Python 3.11+, `libsecret-tools` (`secret-tool`) and `bubblewrap`. On Debian or Ubuntu: `sudo apt install libsecret-tools bubblewrap`. Some distributions restrict unprivileged user namespaces (for example Ubuntu 24.04); `kellu doctor` tells you whether the sandbox can run.

```bash
# Once released
pipx install kellu

# Development
git clone https://github.com/<your-user>/kellu.git
cd kellu
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"      # optional extras: [tui], [local], [dev]

kellu doctor                 # checks keyring, bubblewrap and user namespaces
kellu keys set openrouter    # stored in your keyring, never echoed
kellu                        # terminal assistant
```

If you have secrets in an older keyring schema, `kellu keys migrate --dry-run` lists names (never values) and the copy never deletes the originals.

### Use it inside Kate (LSP)

In Kate: *Settings → Configure Kate → LSP Client → User Server Settings*. Example:

```json
{
  "servers": {
    "python": {
      "command": ["kellu", "lsp"],
      "highlightingModeRegex": "^Python$"
    }
  }
}
```

Kellu's LSP server provides **hover** and **completion** only. Check the Kate LSP Client documentation for the exact format in your Kate version.

## Configuration

| Path | Purpose |
|---|---|
| `~/.config/kellu/` | Providers, routing, scopes, sandbox policy |
| `~/.local/state/kellu/` | Session logs, history (redacted, mode 0700) |
| `~/.cache/kellu/` | Caches |

```yaml
routing:
  code:
    primary: deepseek
    backup: [openrouter]
  general:
    primary: google
    backup: [deepseek, openrouter]
```

## Hardware profiles (design goal)

| Profile | Target | What runs |
|---|---|---|
| `minimal` | any machine | core + terminal, cloud providers, SQLite |
| `standard` | everyday laptop | plus LSP and MCP, small local model for completions |
| `full` | generous RAM or GPU | plus Kate plugin integration, larger local models, PostgreSQL + pgvector |

## Milestones to 0.1.0

- [ ] **M0** Repository, `src/` layout, `pyproject.toml`, XDG paths, CI, tests, license, `SECURITY.md`
- [ ] **M1** Config with packaged defaults, errors, logging, sessions; no side effects on import
- [ ] **M2** Providers: OpenAI-compatible client (streaming, tools), Google, router with timeouts and fallback
- [ ] **M3** `kellu keys` with tiers and migration, scrubbed environment, deny globs, redaction v1, permissions by risk
- [ ] **M4** Sandbox: interface, bubblewrap backend, policies, `kellu doctor`, escape tests
- [ ] **M5** Tools with generated schemas and risk levels: files, sandboxed shell, read-only git; host-side git and gh writes with confirmation
- [ ] **M6** Terminal REPL on the core; Kate LSP (hover, completion)
- [ ] **M7** Documentation and the 0.1.0 tag

## Related projects

Kellu is independent but designed to interoperate with other Kate AI efforts rather than replace them:

- [KateAI](https://github.com/ObiWindu/KateAI): a Kate plugin with a full GUI agent experience.
- [kate-agents](https://github.com/Mte90/kate-agents): a Kate plugin that brings Zed-style agents to the editor.

Interoperability is a goal, not an existing integration. No endorsement by their authors is implied.

## About the name

*Kellu* means "helper" in Mapudungun, the language of the Mapuche people. The name reflects the project's purpose: an assistant that helps, quietly, inside the tools you already use.

## Contributing

The project is young and the architecture is moving, so please open an issue before sending large changes. Especially welcome: security review, sanitization, provider abstractions, LSP integration, and data schemas for development memory. **Report vulnerabilities privately**, as described in [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
<!-- TODO: add the LICENSE file. -->

## Disclaimer

Kate is a text editor developed by the KDE community. Kellu is an independent project and is not affiliated with, sponsored by or endorsed by KDE. AI-generated output can be wrong: review suggestions before applying them.
