# AGENTS.md

Project instructions for coding agents working in this repository.

## Non-negotiable: test before handing work back

If you change commands, build config, scripts, paths, imports, packaging, local dev workflow, or anything user-facing, you must run an appropriate verification step before replying.

Do not claim something works based only on inspection.
Do not hand back untested changes when a relevant local test or command can be run.

Minimum expectation:
- If you change a command in `Justfile`, run that command or a directly equivalent command.
- If you change Pelican config, run Pelican with the updated config.
- If you change local serving behavior, verify the generated HTML or server startup output.
- If something cannot be tested, explicitly say why and what remains unverified.

## For this repo specifically

After changing local blog workflow files (`Justfile`, `pelicanconf.py`, `devconf.py`, `publishconf.py`, theme paths, plugin paths):
- run the relevant `uv run pelican ...` command
- confirm the server starts or the site generates successfully
- check that generated links/CSS paths look correct for local development when applicable

Prefer proving behavior over assuming behavior.
