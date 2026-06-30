set shell := ["bash", "-cu"]

port := env_var_or_default("PORT", "8910")
branch := env_var_or_default("GITHUB_PAGES_BRANCH", "master")
dev_output := env_var_or_default("PELICAN_DEV_OUTPUT", ".dev-output")

alias s := server
server:
    #!/usr/bin/env bash
    set -euo pipefail

    port="{{port}}"
    dev_output="{{dev_output}}"

    cleanup() {
      trap - INT TERM EXIT
      kill "${pelican_pid:-}" "${server_pid:-}" 2>/dev/null || true
      wait 2>/dev/null || true
    }

    trap 'cleanup; exit 0' INT
    trap 'cleanup; exit 0' TERM
    trap cleanup EXIT

    case "$dev_output" in
      ""|"/"|".")
        echo "Refusing unsafe PELICAN_DEV_OUTPUT=$dev_output" >&2
        exit 1
        ;;
    esac

    rm -rf "$dev_output"

    uv run pelican content -o "$dev_output" -s devconf.py -r &
    pelican_pid=$!

    for _ in {1..600}; do
      if [[ -f "$dev_output/index.html" && -f "$dev_output/theme/stylesheet/style.min.css" ]]; then
        break
      fi

      if ! kill -0 "$pelican_pid" 2>/dev/null; then
        wait "$pelican_pid"
        exit $?
      fi

      sleep 0.2
    done

    if [[ ! -f "$dev_output/index.html" || ! -f "$dev_output/theme/stylesheet/style.min.css" ]]; then
      echo "Timed out waiting for Pelican to generate $dev_output" >&2
      exit 1
    fi

    uv run python -m http.server "$port" --bind 127.0.0.1 --directory "$dev_output" &
    server_pid=$!

    echo "Serving site at: http://127.0.0.1:$port - Tap CTRL-C to stop"

    set +e
    wait -n "$pelican_pid" "$server_pid"
    status=$?
    set -e

    echo "dev server stopped; cleaning up..." >&2
    exit "$status"

open:
    open http://localhost:{{port}}

publish:
    uv run pelican content -o output -s publishconf.py

refresh:
    rm -rf output
    git add .
    git commit -m "Updated content" --allow-empty
    git push origin dev

github:
    @echo "GitHub deployment is handled by the GitHub Action now."
    @echo "Commit your changes on 'dev' and push that branch instead:"
    @echo "  git push origin dev"
