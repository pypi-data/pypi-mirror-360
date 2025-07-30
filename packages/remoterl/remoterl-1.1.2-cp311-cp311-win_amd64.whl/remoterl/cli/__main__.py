#!/usr/bin/env python3
"""remoterl.cli
================
Cleaned-up CLI with the following fixes applied:

1️⃣ **Config consistency** - The CLI now documents the use of *JSON* (not YAML)
   for the persistent config file `config.json` living under
   `~/.config/remoterl/` (unless overridden by `REMOTERL_CONFIG_PATH`).
2️⃣ **Register retry loop** - Counts attempts correctly and aborts after three
   invalid entries.
3️⃣ **Invalid rl framework aborts** - `train` exits immediately with code 1 when the
   rl framework name is unrecognised.
5️⃣ **Extra args passthrough** - Typer’s native `ctx.args` is forwarded to the
   rl framework instead of the custom `parse_extra` helper.
6️⃣ **Uniform UX helpers** - `success()`, `warn()`, `fail()` colour helpers plus
   consistent non-zero exit codes on error paths.

The rest of the logic is unchanged.
"""
from __future__ import annotations

import os
import sys
from typing import List
import webbrowser
import typer

# ----------------------------------------------------------------------------
# Config helpers import (shared with existing module)
# ----------------------------------------------------------------------------
from ..config import load_config, save_config, resolve_api_key, validate_api_key, DEFAULT_CONFIG_PATH   
DASHBOARD_URL = "https://remoterl.com/user/dashboard"

# ----------------------------------------------------------------------------
# Typer application
# ----------------------------------------------------------------------------
app = typer.Typer(
    add_completion=False,
    help="RemoteRL - spin up remote trainers & simulators from one CLI.",
)

# ----------------------------------------------------------------------------
# Root – show help & --version flag
# ----------------------------------------------------------------------------
from importlib.metadata import version as _pkg_version, PackageNotFoundError

def _resolve_version() -> str:
    try:
        return _pkg_version("remoterl")
    except PackageNotFoundError:
        return "unknown"

@app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        is_flag=True,
        help="Show CLI version and exit.",
    ),
) -> None:
    """Root command - prints help when no sub-command is given."""
    if version:
        typer.echo(_resolve_version())
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()

# ----------------------------------------------------------------------------
# Style helpers – keep colouring uniform across commands
# ----------------------------------------------------------------------------

def _style(msg: str, fg: typer.colors.Color) -> str:  # internal
    return typer.style(msg, fg=fg)

def success(msg: str) -> None:
    typer.echo(_style(msg, typer.colors.GREEN))

def warn(msg: str) -> None:
    typer.echo(_style(msg, typer.colors.YELLOW))

def fail(msg: str) -> None:
    typer.echo(_style(msg, typer.colors.RED), err=True)


# ----------------------------------------------------------------------------
# Misc helpers
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# register – save API key
# ----------------------------------------------------------------------------
@app.command(help="Save (or update) your RemoteRL API key in the config file.")
def register(
    open_browser: bool = typer.Option(
        True,
        "--open-browser/--no-open-browser",
        "-o",
        help="Open your dashboard in a browser so you can copy the key quickly.",
    ),
) -> None:
    cfg = load_config()

    # Existing key?
    if (cur := cfg.get("api_key")):
        warn(f"Current API key: {cur[:8]}... (resolved)")

    # Browser helper
    if open_browser and hasattr(sys, "stdout"):
        warn(f"Opening {DASHBOARD_URL} ...")
        try:
            webbrowser.open(DASHBOARD_URL)
        except Exception:
            pass  # silent – browser may not be available

    # Prompt user (with retries)
    attempts = 0
    api_key = typer.prompt("Please enter your RemoteRL API key")
    while not validate_api_key(api_key):
        attempts += 1
        if attempts >= 3:
            fail("Too many invalid attempts – aborting.")
            raise typer.Exit(code=1)
        api_key = typer.prompt("Please enter a *valid* RemoteRL API key")

    # Persist
    cfg["api_key"] = api_key
    save_config(cfg)
    success(
        f"API key saved to {DEFAULT_CONFIG_PATH}."
    )

# ----------------------------------------------------------------------------
# simulate – unchanged except for cohesive error handling
# ----------------------------------------------------------------------------
@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def simulate(ctx: typer.Context) -> None:
    """
    Launch a Remote Simulator and wait for an Online Trainer to connect.\n
    \n
    To begin training with this simulator, run ``remoterl train``\n
    -either in another terminal on the same machine, or from any other PC or cloud instance.\n
    """
    from ..pipelines.simulate import simulate as _remote_simulate  # type: ignore

    api_key = resolve_api_key()
    if not api_key:
        fail("No RemoteRL API key found. Run `remoterl register` first or set REMOTERL_API_KEY.")
        raise typer.Exit(code=1)

    os.environ["REMOTERL_API_KEY"] = api_key
    _remote_simulate(list(ctx.args))

# ----------------------------------------------------------------------------
# train – rl framework selection + passthrough args
# ----------------------------------------------------------------------------
RL_FRAMEWORKS = {
    "gym",
    "gymnasium",  # alias – normalised to "gym"
    "ray",
    "rllib",
    "sb3",
    "stable_baselines3",
}
_RL_FRAMEWORKS_DESCRIPTION = {
    "gymnasium(gym)",
    "rllib(ray)",
    "stable-baselines3(sb3)",
}

@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def train(
    ctx: typer.Context,
    rl_framework: str = typer.Argument(
        "gym",
        metavar="FRAMEWORK",
        case_sensitive=False,
        help=f"RL Framework: {', '.join(sorted(_RL_FRAMEWORKS_DESCRIPTION))}",
    ),
) -> None:
    """
    Run an online training job using remote simulators, with support for popular RL frameworks.
    --------------------------------------------------------\n
    [Popular RL-framework params]\n
    You can pass RL framework-specific arguments after the ``--`` separator.\n
    \n
    <Examples>\n
    --------\n
    :: Basic Gym run ::\n
        remoterl train\n
    \n
    :: Stable-Baselines 3 / PPO ::\n
        remoterl train sb3 --algo ppo\n
    \n
    :: RLlib with larger batches ::\n
        remoterl train rllib --batch-size 64\n
    --------------------------------------------------------\n
    [RemoteRL trainer params]\n
    \n
    - ``--num-workers``        Number of trainer-side gateway workers\n
    - ``--num-env-runners``    Number of remote environment runners\n
    (passed through to the back-end unchanged)\n
    \n
    <Examples>\n
    --------\n
        remoterl train sb3   --num-workers 2 --num-env-runners 4\n
        remoterl train rllib --batch-size 64 --num-workers 3 --num-env-runners 6\n
    \n
    Note on duplicate flags\n
    -----------------------\n
    RemoteRL uses ``--num-workers`` / ``--num-env-runners`` itself **and**\n
    leaves them in the arg list, so any back-end that recognises the same\n
    names will see the exact values-you only need to set them once.\n
    """
    from ..pipelines.train import train as _online_train  # type: ignore

    api_key = resolve_api_key()
    if not api_key:
        fail("No RemoteRL API key found. Run `remoterl register` first or set REMOTERL_API_KEY.")
        raise typer.Exit(code=1)

    os.environ["REMOTERL_API_KEY"] = api_key

    selected = rl_framework.lower().replace("-", "_")
    if selected not in RL_FRAMEWORKS:
        fail(f"Invalid rl framework '{selected}'. Valid choices: {', '.join(sorted(RL_FRAMEWORKS))}.")
        raise typer.Exit(code=1)

    # Hand raw tail straight through (Typer already ignored unknown options)
    extra_args: List[str] = list(ctx.args)

    # Forward to the real trainer – signature: train(rl_framework: str, args: List[str])
    _online_train(selected, extra_args)  # type: ignore[arg-type]

# ----------------------------------------------------------------------------
# Entrypoint for console-script
# ----------------------------------------------------------------------------

def main() -> None:  # pragma: no cover – thin wrapper for console-scripts
    DEFAULT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    app()

if __name__ == "__main__":
    main()
