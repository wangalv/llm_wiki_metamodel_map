# Profile: default

The general-purpose profile. It applies when `Schema/wiki-config.json` doesn't name another.

- **Note kinds:** `topic`, `concept`, `entity`, `project` and `log`, as defined in `Schema/wiki-config.json`.
- **Plugins:** none. There are no extra lint rules, no generators and no converters.

This folder only documents the profile. To start a new domain, copy it to `scripts/profiles/<name>/`, rename this file to `<name>-profile.md`, add the plugin files you need (see `../plugin-interface.md`), and set `"profile": "<name>"` in `Schema/wiki-config.json`.
