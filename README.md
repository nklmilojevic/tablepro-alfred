# TablePro for Alfred

Search and open [TablePro](https://tablepro.app) connections from Alfred.

![keyword tp + query](https://img.shields.io/badge/Alfred-5%2B-5C5CFF) ![macOS](https://img.shields.io/badge/macOS-14%2B-blue)

## Install

1. Download the latest `TablePro.alfredworkflow` from [Releases](../../releases/latest).
2. Double-click to install in Alfred.

Requires Alfred 5+ and TablePro 0.37 or later (UUID-keyed deep links).

## Usage

Type `tp` in Alfred, optionally followed by a query:

| Action | Result |
|---|---|
| `↵` Enter | Open the connection in TablePro |
| `⌘ ↵` Cmd-Enter | Copy the `tablepro://` deep link to the clipboard |

Alfred fuzzy-matches against connection name, folder path, tag, database, host, and type — so `tp dev send` jumps straight to MailerSend/Dev, `tp prod` lists every production-tagged connection.

Each row shows:

- **Icon** — colored circle matching the connection's folder color (falls back to the connection's own color, then the TablePro app icon).
- **Title** — connection name.
- **Subtitle** — `Folder/Subfolder · tag · type · host:port · database · via sshHost`.

## How it works

- Reads connection metadata from `~/Library/Application Support/TablePro/connections.json`.
- Reads folder and tag definitions from `~/Library/Preferences/com.TablePro.plist`.
- Selecting an item runs `open tablepro://connect/<uuid>`, which is TablePro's [documented URL scheme](https://docs.tablepro.app/external-api/url-scheme).

No network, no daemon. Just a Python 3 script filter (stdlib only).

## Privacy

`connections.json` does **not** contain passwords — TablePro keeps those in the macOS Keychain. This workflow never sees credentials.

## Build from source

```sh
./build.sh
```

Produces `TablePro.alfredworkflow` in the repo root. The script regenerates the colored circle icons via `generate-icons.py` (pure stdlib PNG writer, no dependencies).

## Releasing

Tag and push:

```sh
git tag v0.4.0
git push origin v0.4.0
```

GitHub Actions patches `info.plist`'s version from the tag, builds the workflow, and creates a release with the bundle attached. See `.github/workflows/release.yml`.

## Credits

Inspired by the official TablePro [Raycast extension](https://docs.tablepro.app/external-api/raycast).
