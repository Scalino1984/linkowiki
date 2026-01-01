## Datei und Ordnerstruktur des Projekts:
---

linkowiki
├── AI_PROMPT_MIGRATION.md
├── AI_SYSTEM_PROMPT.md
├── AUTO_ASSIST_FEATURES.md
├── beispiele
│   ├── chat_app.py
│   └── chat_app.ts
├── beispiele.md
├── bin
│   ├── ai_endpoint.py
│   ├── app.py
│   ├── clean_cache.py
│   ├── release.py
│   └── srv.py
├── BUGFIX_SUMMARY.md
├── .claude
│   └── settings.local.json
├── CLI_DEMO.md
├── cli_doppelte_header.png
├── cli.png
├── CONTRIBUTING.md
├── .copilot_history
├── darstellung.png
├── design.md
├── doc
│   ├── CONFIG.md
│   ├── COPILOT_CLI.md
│   ├── FEATURES.md
│   ├── IMPROVEMENTS.md
│   ├── INTERACTIVE_OPTIONS.md
│   ├── PROVIDERS.md
│   ├── PYDANTICAI_V2_ARCHITECTURE.md
│   ├── QUICKSTART.md
│   ├── README-ja.md
│   ├── SESSION_AI.md
│   └── standalone.md
├── docker-compose.debug.yml
├── docker-compose.yml
├── Dockerfile
├── .dockerignore
├── .env.example
├── etc
│   ├── config.yaml
│   ├── linkowiki.conf
│   ├── providers.json
│   └── providers.schema.json
├── examples
│   └── pydanticai_v2_examples.py
├── FIXES_COMPLETE.md
├── .github
│   └── workflows
│       ├── pydanticai-conformance.yml
│       ├── tests-macos.yml
│       └── tests-ubuntu.yml
├── .gitignore
├── IMPLEMENTATION_DETAILS.md
├── lib
│   ├── adapter
│   │   ├── adapter.py
│   │   ├── cheat_cheat.py
│   │   ├── cheat_sheets.py
│   │   ├── cmd.py
│   │   ├── common.py
│   │   ├── git_adapter.py
│   │   ├── __init__.py
│   │   ├── internal.py
│   │   ├── latenz.py
│   │   ├── learnxiny.py
│   │   ├── question.py
│   │   ├── rosetta.py
│   │   ├── tldr.py
│   │   └── upstream.py
│   ├── buttons.py
│   ├── cache.py
│   ├── cheat_wrapper.py
│   ├── cheat_wrapper_test.py
│   ├── config.py
│   ├── fetch.py
│   ├── fmt
│   │   ├── comments.py
│   │   ├── __init__.py
│   │   ├── internal.py
│   │   └── markdown.py
│   ├── frontend
│   │   ├── ansi.py
│   │   ├── html.py
│   │   └── __init__.py
│   ├── globals.py
│   ├── languages_data.py
│   ├── limits.py
│   ├── options.py
│   ├── panela
│   │   ├── colors.json
│   │   ├── colors.py
│   │   └── panela_colors.py
│   ├── postprocessing.py
│   ├── post.py
│   ├── routing.py
│   ├── search.py
│   ├── standalone.py
│   └── stateful_queries.py
├── LICENSE
├── linko-wiki.log
├── .linkowiki-session.json
├── liveausgabe.png
├── Makefile
├── new.png
├── PROFESSIONAL_CLI.md
├── README.md
├── requirements.txt
├── .rich_session_history
├── .session_shell_history
├── share
│   ├── adapters
│   │   ├── chmod.grc
│   │   ├── chmod.sh
│   │   ├── oeis.sh
│   │   └── rfc.sh
│   ├── ansi2html.sh
│   ├── bash_completion.txt
│   ├── cht.sh.txt
│   ├── emacs-ivy.txt
│   ├── emacs.txt
│   ├── firstpage.txt -> firstpage-v2.txt
│   ├── firstpage-v1.txt
│   ├── firstpage-v2.pnl
│   ├── firstpage-v2.txt
│   ├── fish.txt
│   ├── help.txt
│   ├── intro.txt
│   ├── post.txt
│   ├── scripts
│   │   ├── cacheCleanup.go
│   │   └── remove-from-cache.sh
│   ├── static
│   │   ├── 1.html
│   │   ├── big-logo.png
│   │   ├── big-logo-v2-fixed.png
│   │   ├── cht.sh-url-structure.png
│   │   ├── demo-curl.gif
│   │   ├── demo-sublime.gif
│   │   ├── edit-cheat-sheet.png
│   │   ├── idea-demo.gif
│   │   ├── malformed-response.html
│   │   ├── opensearch.xml
│   │   ├── stat-2017-06-05.png
│   │   ├── stealth-mode.gif
│   │   ├── style.css
│   │   ├── supported-languages-c++.png
│   │   ├── vim-demo.gif
│   │   ├── vscode-snippet-demo.gif
│   │   └── when-you-lie-katze.png
│   ├── styles-demo.txt
│   ├── vim
│   │   └── .vimrc
│   ├── vim.txt
│   └── zsh.txt
├── skalierung_claude.png
├── skalierung_linkowiki.png
├── start-wiki
├── testfile
├── test.png
├── tests
│   ├── demo_fixed_cli.py
│   ├── README.md
│   ├── results
│   │   ├── 1
│   │   ├── 10
│   │   ├── 11
│   │   ├── 12
│   │   ├── 13
│   │   ├── 14
│   │   ├── 15
│   │   ├── 16
│   │   ├── 17
│   │   ├── 18
│   │   ├── 19
│   │   ├── 2
│   │   ├── 20
│   │   ├── 21
│   │   ├── 22
│   │   ├── 23
│   │   ├── 24
│   │   ├── 25
│   │   ├── 3
│   │   ├── 4
│   │   ├── 5
│   │   ├── 6
│   │   ├── 7
│   │   ├── 8
│   │   └── 9
│   ├── run-tests.sh
│   ├── test_auto_assist_features.py
│   ├── test_cli_fixes.py
│   ├── test_cli_integration.py
│   ├── test_pydantic_ai_conformance.py
│   └── tests.txt
├── tools
│   ├── ai
│   │   ├── agent_factory.py
│   │   ├── agents
│   │   │   ├── __init__.py
│   │   │   └── wiki_agent.py
│   │   ├── assistant.py
│   │   ├── __init__.py
│   │   ├── providers.py
│   │   ├── routing.py
│   │   └── tools
│   │       ├── file_tools.py
│   │       ├── git_tools.py
│   │       ├── __init__.py
│   │       └── wiki_tools.py
│   ├── config.py
│   ├── copilot_cli_full.py
│   ├── copilot_context.py
│   ├── copilot_shell.py
│   ├── linkowiki-admin.py
│   ├── linkowiki-cli.py
│   ├── memory
│   │   ├── context.py
│   │   └── __init__.py
│   ├── rich_session_shell.py
│   ├── session
│   │   ├── export.py
│   │   ├── __init__.py
│   │   └── manager.py
│   ├── simple_copilot_shell.py
│   ├── validate_providers.py
│   └── wiki_search.py
└── wiki
    ├── .changelog
    └── README

---