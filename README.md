# Crypto Gameplan marketplace

The Claude Code plugins and skills that Crypto Gameplan uses and maintains, in one catalog. Add it once and every plugin
listed here can be installed and updated from Claude Code.

## Install

In Claude Code, type:

```text
/plugin marketplace add crypto-gameplan/cgp-marketplace
```

Then install what you need, for example:

```text
/plugin install cgp-essentials@crypto-gameplan
```

Or in a terminal:

```bash
claude plugin marketplace add crypto-gameplan/cgp-marketplace
claude plugin install cgp-essentials@crypto-gameplan
```

Run `/reload-plugins` or restart Claude Code afterwards.

## Plugins

| Plugin | What it does | Source |
|---|---|---|
| `cgp-essentials` | The skills Crypto Gameplan uses every day | [plugins/cgp-essentials](plugins/cgp-essentials) |
| `cgp-effort` | Picks the reasoning effort for every prompt, with a prompt-cache countdown and one-click Compact and Handoff | [crypto-gameplan/cgp-effort](https://github.com/crypto-gameplan/cgp-effort) |

## Maintaining the catalog

The catalog is [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json). Every plugin has one entry there.

A plugin without code of its own (skills, commands, settings) lives in this repository as a folder under `plugins/`.
A plugin with its own code, tests and releases, such as cgp-effort, keeps its own repository and the catalog points
to it.

### Add a skill to cgp-essentials

1. Copy [templates/skill](templates/skill) to `plugins/cgp-essentials/skills/<skill-name>/`.
2. Fill in `SKILL.md`. The `name` in its header must match the folder name.
3. Raise `version` in [plugins/cgp-essentials/.claude-plugin/plugin.json](plugins/cgp-essentials/.claude-plugin/plugin.json).
4. Run `claude plugin validate --strict plugins/cgp-essentials` and commit.

### Add a plugin

- Without code: create `plugins/<name>/` with `.claude-plugin/plugin.json`, then add an entry with
  `"source": "./plugins/<name>"` to the catalog.
- With its own repository: add an entry whose `source` is the repository URL and its release branch, as for
  cgp-effort.

### Versions

Every `plugin.json` sets a `version`. People receive an update only when that number goes up, so raise it for each
change you want to ship and leave it alone for work in progress. Plugins from other authors are listed at a version or
commit we have checked, never at their latest state.

CI runs `claude plugin validate --strict` on the catalog and on every folder in `plugins/`.

## License

MIT, see [LICENSE](LICENSE).
