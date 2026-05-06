#!/usr/bin/env python3
import json
import os
import plistlib
import sys

CONNECTIONS_PATH = os.path.expanduser(
    "~/Library/Application Support/TablePro/connections.json"
)
PREFS_PATH = os.path.expanduser("~/Library/Preferences/com.TablePro.plist")


def load_connections():
    with open(CONNECTIONS_PATH) as f:
        return json.load(f)


def load_prefs():
    """Return (groups_by_id, tags_by_id). Groups have name + parentId for nesting."""
    try:
        with open(PREFS_PATH, "rb") as f:
            prefs = plistlib.load(f)
    except FileNotFoundError:
        return {}, {}

    def parse_json_field(key):
        raw = prefs.get(key)
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="replace")
        if not isinstance(raw, str):
            return []
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return []

    groups = {g["id"]: g for g in parse_json_field("com.TablePro.groups") if "id" in g}
    tags = {t["id"]: t for t in parse_json_field("com.TablePro.tags") if "id" in t}
    return groups, tags


def group_path(group_id, groups):
    """Walk parentId chain to build 'Parent/Child' path. Empty string if not found."""
    parts = []
    seen = set()
    while group_id and group_id in groups and group_id not in seen:
        seen.add(group_id)
        g = groups[group_id]
        parts.append(g.get("name", ""))
        group_id = g.get("parentId")
    return "/".join(reversed(parts))


def group_color(group_id, groups):
    """Walk parentId chain returning the first non-'None' color. Empty if none."""
    seen = set()
    while group_id and group_id in groups and group_id not in seen:
        seen.add(group_id)
        c = groups[group_id].get("color", "None")
        if c and c != "None":
            return c
        group_id = groups[group_id].get("parentId")
    return ""


def pick_icon(conn, groups):
    """Group color (walking parents) > connection color > app icon."""
    for color in (group_color(conn.get("groupId"), groups), conn.get("color", "None")):
        if color and color != "None":
            path = f"icons/{color}.png"
            if os.path.exists(path):
                return path
    return "icon.png"


def to_item(conn, groups, tags):
    name = conn.get("name", "Unnamed")
    typ = conn.get("type", "Unknown")
    host = conn.get("host", "").strip()
    db = conn.get("database", "")
    port = conn.get("port", "")

    folder = group_path(conn.get("groupId"), groups)
    tag = tags.get(conn.get("tagId", ""), {}).get("name", "")

    location = host
    if host and port:
        location = f"{host}:{port}"

    subtitle_parts = []
    if folder:
        subtitle_parts.append(folder)
    if tag:
        subtitle_parts.append(tag)
    subtitle_parts.append(typ)
    if location:
        subtitle_parts.append(location)
    if db:
        subtitle_parts.append(db)
    if conn.get("sshEnabled"):
        ssh_host = conn.get("sshHost", "")
        if ssh_host:
            subtitle_parts.append(f"via {ssh_host}")

    icon_path = pick_icon(conn, groups)

    match = " ".join(
        p for p in (name, folder.replace("/", " "), tag, db, host, typ) if p
    )

    return {
        "uid": conn["id"],
        "title": name,
        "subtitle": " · ".join(subtitle_parts),
        "arg": f"tablepro://connect/{conn['id']}",
        "match": match,
        "icon": {"path": icon_path},
        "mods": {
            "cmd": {
                "subtitle": "Copy deep link to clipboard",
                "arg": f"tablepro://connect/{conn['id']}",
                "variables": {"action": "copy"},
            }
        },
        "variables": {"action": "open"},
    }


def main():
    try:
        conns = load_connections()
    except FileNotFoundError:
        print(
            json.dumps(
                {
                    "items": [
                        {
                            "title": "TablePro is not installed",
                            "subtitle": "Get it at https://tablepro.app",
                            "arg": "https://tablepro.app",
                            "valid": True,
                            "variables": {"action": "open"},
                        }
                    ]
                }
            )
        )
        return

    groups, tags = load_prefs()

    conns.sort(
        key=lambda c: (
            group_path(c.get("groupId"), groups),
            c.get("sortOrder", 0),
            c.get("name", ""),
        )
    )

    items = [to_item(c, groups, tags) for c in conns]
    if not items:
        items = [
            {
                "title": "No saved connections",
                "subtitle": "Add a connection in TablePro first",
                "valid": False,
            }
        ]

    print(json.dumps({"items": items}))


if __name__ == "__main__":
    main()
