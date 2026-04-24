# Production CLI Research Notes

This repo is a public distribution surface: CLI, plugin manifests, skill, and thin HTTP client. The backend remains hosted and private.

## Decisions Applied

`mnerve login` should default to hosted browser login at `https://nerve.maestro.onl/access/cli`, not `localhost:3000`. Localhost is a development override only through `--app-url http://localhost:3000` or `NERVE_APP_URL`.

The browser login flow should use an external browser, PKCE, and a loopback callback on `127.0.0.1:<ephemeral-port>`. This matches OAuth native-app guidance: browser-based authorization is preferred, public clients need PKCE, and loopback redirect URIs should allow arbitrary ephemeral ports.

The README should not assume `pip3`. For Python CLI applications, the public install hierarchy should be:

1. `uv tool install maestro-nerve` for persistent installs.
2. `uvx maestro-nerve ...` for one-off execution.
3. `pipx install maestro-nerve` for users who prefer PyPA tooling.
4. `python -m pip install --user maestro-nerve` as a compatibility fallback.

Agent/plugin setup should stay separate from CLI installation. npm, pnpm, and Bun users can keep using their host package runner for agent/plugin tooling; `mnerve` is still a PyPI-distributed CLI, so `uv` or `pipx` is the cleanest install path.

## Sources

- RFC 8252, OAuth 2.0 for Native Apps: external browser authorization, PKCE for public native app clients, and loopback redirects with OS-assigned ports.
- uv tools documentation: `uvx` is an alias for `uv tool run`; `uv tool install` installs command-line tools into isolated environments and exposes executables on PATH.
- pipx documentation: pipx installs Python applications in isolated environments and exposes their commands on PATH, avoiding dependency conflicts.
- GitHub CLI auth UX: production CLIs commonly support browser login and device/headless alternatives rather than requiring a raw token paste as the only path.
