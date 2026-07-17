#!/usr/bin/env python3
"""dots installer — restores this Arch + Hyprland setup on a fresh machine.

Usage:
  python3 install.py [install] [flags]   full restore (default command)
  python3 install.py sync    [flags]     live configs + package lists -> repo
  python3 install.py check               validate packages.json against repos

Bootstrap on a bare system:
  curl -fsSL https://raw.githubusercontent.com/redmoondz/dots/master/install.sh | bash

Python 3 stdlib only. Safe to re-run: every step checks state before acting.
"""

import argparse
import fnmatch
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
HOME = Path.home()
CONFIG = HOME / ".config"
PACMAN_LOCK = Path("/var/lib/pacman/db.lck")


# ---------------------------------------------------------------- logging ---

class Log:
    use_color = sys.stdout.isatty() and not os.environ.get("NO_COLOR")

    @classmethod
    def _c(cls, code, text):
        return f"\033[{code}m{text}\033[0m" if cls.use_color else text

    @classmethod
    def step(cls, name, title):
        print()
        print(cls._c("1;36", f"==> [{name}] {title}"))

    @classmethod
    def info(cls, msg):
        print(f"    {msg}")

    @classmethod
    def cmd(cls, msg):
        print(cls._c("2", f"    $ {msg}"))

    @classmethod
    def ok(cls, msg):
        print(cls._c("32", f"    ok: {msg}"))

    @classmethod
    def skip(cls, msg):
        print(cls._c("2", f"    skip: {msg}"))

    @classmethod
    def warn(cls, msg):
        print(cls._c("33", f"    warning: {msg}"))

    @classmethod
    def err(cls, msg):
        print(cls._c("1;31", f"    error: {msg}"), file=sys.stderr)


# ------------------------------------------------------------------ shell ---

class Ctx:
    def __init__(self, args, manifest):
        self.args = args
        self.manifest = manifest
        self.checklist = []
        self.dry_run = getattr(args, "dry_run", False)
        self.interactive = sys.stdin.isatty() and not getattr(args, "noconfirm", False)
        self._sudo_stop = None

    def note(self, msg):
        if msg not in self.checklist:
            self.checklist.append(msg)


def run(ctx, cmd, sudo=False, check=True, capture=False, ro=False, shell=False):
    """Run a command. Mutating commands (ro=False) are skipped in --dry-run."""
    if sudo and not shell:
        cmd = ["sudo"] + cmd
    display = cmd if shell else " ".join(cmd)
    if ctx.dry_run and not ro:
        Log.cmd(f"[DRY] {display}")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
    if not ro:
        Log.cmd(display)
    if any(w in (display if isinstance(display, str) else "") for w in ("pacman ", "yay ")) and not ro:
        wait_pacman_lock(ctx)
    return subprocess.run(
        cmd, shell=shell, check=check,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        text=True,
    )


def out(ctx, cmd, **kw):
    """Capture stdout of a read-only command (runs even in --dry-run)."""
    r = run(ctx, cmd, capture=True, ro=True, check=False, **kw)
    return (r.stdout or "").strip()


def wait_pacman_lock(ctx, timeout=300):
    import time
    waited = 0
    while PACMAN_LOCK.exists() and waited < timeout:
        if waited == 0:
            Log.warn(f"pacman database is locked ({PACMAN_LOCK}), waiting…")
        time.sleep(5)
        waited += 5
    if PACMAN_LOCK.exists():
        Log.err("pacman lock did not clear; remove it manually if no pacman is running")
        sys.exit(1)


def confirm(ctx, prompt, default=True):
    if not ctx.interactive:
        return default
    suffix = "[Y/n]" if default else "[y/N]"
    try:
        answer = input(f"    {prompt} {suffix} ").strip().lower()
    except EOFError:
        return default
    if not answer:
        return default
    return answer in ("y", "yes", "д", "да")


def start_sudo_keepalive(ctx):
    if ctx.dry_run:
        return
    subprocess.run(["sudo", "-v"], check=True)
    stop = threading.Event()

    def loop():
        while not stop.wait(60):
            subprocess.run(["sudo", "-nv"], check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    threading.Thread(target=loop, daemon=True).start()
    ctx._sudo_stop = stop


# --------------------------------------------------------------- manifest ---

def load_manifest():
    path = REPO_ROOT / "packages.json"
    if not path.is_file():
        Log.err(f"{path} not found — run install.py from a clone of the dots repo")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def pkg_names(entries):
    return [e if isinstance(e, str) else e["name"] for e in entries]


def installed_packages(ctx):
    return set(out(ctx, ["pacman", "-Qq"]).split())


# ------------------------------------------------------------ install steps ---

def step_preflight(ctx):
    if not Path("/etc/arch-release").exists() and "arch" not in out(ctx, ["cat", "/etc/os-release"]).lower():
        Log.err("this is not Arch Linux")
        sys.exit(1)
    if os.geteuid() == 0:
        Log.err("run as your normal user, not root (makepkg refuses root; sudo is used internally)")
        sys.exit(1)
    if not shutil.which("sudo"):
        Log.err("sudo is required")
        sys.exit(1)
    ping = run(ctx, ["curl", "-fsI", "-m", "10", "https://archlinux.org"],
               check=False, capture=True, ro=True)
    if ping.returncode != 0:
        Log.warn("archlinux.org is unreachable — network problems will break the install")
    Log.ok(f"Arch Linux, user={os.environ.get('USER', 'unknown')}, repo={REPO_ROOT}")


def step_multilib(ctx):
    conf = Path("/etc/pacman.conf").read_text()
    if "\n[multilib]" in conf:
        Log.skip("multilib already enabled")
        return
    new = conf.replace("#[multilib]\n#Include = /etc/pacman.d/mirrorlist",
                       "[multilib]\nInclude = /etc/pacman.d/mirrorlist")
    if new == conf:
        Log.warn("could not find the commented [multilib] block in /etc/pacman.conf — enable it manually")
        ctx.note("Enable [multilib] in /etc/pacman.conf manually (needed for steam/wine/lib32-*)")
        return
    if not ctx.dry_run:
        subprocess.run(["sudo", "tee", "/etc/pacman.conf"], input=new,
                       text=True, check=True, stdout=subprocess.DEVNULL)
    Log.ok("enabled [multilib] in /etc/pacman.conf")


def step_update(ctx):
    if ctx.args.skip_update:
        Log.warn("SKIPPING full system update — partial upgrades are dangerous on Arch")
        return
    run(ctx, ["pacman", "-Syu", "--noconfirm"], sudo=True)


def step_git_config(ctx):
    defaults = ctx.manifest.get("git_defaults", {})
    for key, default in defaults.items():
        current = out(ctx, ["git", "config", "--global", key])
        if current:
            Log.skip(f"git {key} already set: {current}")
            continue
        value = getattr(ctx.args, "git_" + key.split(".")[1], None) or default
        if ctx.interactive:
            try:
                typed = input(f"    git {key} [{default}]: ").strip()
                value = typed or default
            except EOFError:
                pass
        run(ctx, ["git", "config", "--global", key, value])
        Log.ok(f"git {key} = {value}")


def step_yay(ctx):
    if shutil.which("yay"):
        Log.skip("yay already installed")
        return
    run(ctx, ["pacman", "-S", "--needed", "--noconfirm", "git", "base-devel"], sudo=True)
    tmp = tempfile.mkdtemp(prefix="yay-build-")
    run(ctx, ["git", "clone", "https://aur.archlinux.org/yay.git", tmp])
    if not ctx.dry_run:
        subprocess.run(["makepkg", "-si", "--noconfirm"], cwd=tmp, check=True)
        shutil.rmtree(tmp, ignore_errors=True)
    Log.ok("yay built and installed from AUR")


def step_native(ctx):
    pkgs = pkg_names(ctx.manifest["pacman"])
    if ctx.args.with_optional:
        pkgs += pkg_names(ctx.manifest.get("optional", []))
    missing = [p for p in pkgs if p not in installed_packages(ctx)]
    if not missing:
        Log.skip(f"all {len(pkgs)} native packages already installed")
        return
    Log.info(f"{len(missing)} packages to install: {' '.join(missing)}")
    run(ctx, ["pacman", "-S", "--needed", "--noconfirm"] + pkgs, sudo=True)


def step_aur(ctx):
    pkgs = pkg_names(ctx.manifest["aur"])
    installed = installed_packages(ctx)
    banned = pkg_names(ctx.manifest.get("removed_do_not_install", []))
    present_banned = [p for p in banned if p in installed]
    if present_banned:
        Log.warn(f"packages from removed_do_not_install are installed: {' '.join(present_banned)} "
                 "(not touching them — remove manually if unwanted)")
    missing = [p for p in pkgs if p not in installed]
    if not missing:
        Log.skip(f"all {len(pkgs)} AUR packages already installed")
        return
    Log.info(f"{len(missing)} AUR packages to install: {' '.join(missing)}")
    run(ctx, ["yay", "-S", "--needed", "--noconfirm"] + pkgs)


def step_npm(ctx):
    for pkg in ctx.manifest.get("npm_global", []):
        r = run(ctx, ["npm", "ls", "-g", pkg], check=False, capture=True, ro=True)
        if r.returncode == 0:
            Log.skip(f"npm global {pkg} already installed")
            continue
        run(ctx, ["npm", "install", "-g", pkg], sudo=True)


def step_curl_tools(ctx):
    for tool in ctx.manifest.get("curl_installers", []):
        creates = Path(os.path.expanduser(tool["creates"]))
        if creates.exists():
            Log.skip(f"{tool['name']} already installed ({creates})")
            continue
        run(ctx, f"curl -fsSL {tool['url']} | {tool['shell']}", shell=True)
        if note := tool.get("note"):
            ctx.note(f"{tool['name']}: {note}")


# ----------------------------------------------------------------- deploy ---

def backup_path(path):
    return path.with_name(path.name + ".bak-" + datetime.now().strftime("%Y%m%d-%H%M%S"))


def deploy_symlink(ctx, src, dst):
    if dst.is_symlink():
        if dst.resolve() == src.resolve():
            Log.skip(f"{dst} -> {src} (already linked)")
            return
        Log.warn(f"{dst} is a symlink to {os.readlink(dst)} — relinking to {src}")
        if not ctx.dry_run:
            dst.unlink()
    elif dst.exists():
        bak = backup_path(dst)
        Log.info(f"backing up {dst} -> {bak}")
        if not ctx.dry_run:
            dst.rename(bak)
    if not ctx.dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.symlink_to(src)
    Log.ok(f"{dst} -> {src}")


def deploy_copy(ctx, src, dst):
    if dst.is_symlink():
        Log.warn(f"{dst} is a symlink (deployed in symlink mode earlier) — leaving it alone")
        return
    if not ctx.dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst, dirs_exist_ok=True)
    Log.ok(f"copied {src} -> {dst}")


def step_deploy(ctx):
    mode = ctx.args.mode or ctx.manifest["deploy"].get("default_mode", "symlink")
    deploy = deploy_symlink if mode == "symlink" else deploy_copy
    Log.info(f"deploy mode: {mode}")
    for d in ctx.manifest["deploy"]["config_dirs"]:
        src = REPO_ROOT / d
        if not src.is_dir():
            Log.warn(f"{src} missing in repo — skipped")
            continue
        deploy(ctx, src, CONFIG / d)

    wp = ctx.manifest["deploy"]["wallpapers"]
    wsrc = REPO_ROOT / wp["src"]
    wdst = Path(os.path.expanduser(wp["dst"]))
    if wsrc.is_dir():
        deploy(ctx, wsrc, wdst)
    compat = Path(os.path.expanduser(wp["compat_symlink"]))
    if compat.is_symlink():
        Log.skip(f"{compat} symlink already present")
    elif compat.exists():
        Log.warn(f"{compat} exists as a real directory — not replacing it")
    else:
        if not ctx.dry_run:
            compat.symlink_to(wdst.name)
        Log.ok(f"{compat} -> {wdst.name} (compat symlink)")

    if ctx.args.with_zsh:
        deploy_copy(ctx, REPO_ROOT / ".zshrc", HOME / ".zshrc")


def step_system_files(ctx):
    for entry in ctx.manifest["deploy"].get("system_files", []):
        src = REPO_ROOT / entry["src"]
        dst = Path(entry["dst"])
        if not src.is_file():
            Log.warn(f"{src} missing in repo — skipped")
            continue
        if dst.is_file() and dst.read_text() == src.read_text():
            Log.skip(f"{dst} already up to date")
            continue
        run(ctx, ["install", "-m", entry.get("mode", "0644").lstrip("0") or "644",
                  str(src), str(dst)], sudo=True)
        Log.ok(f"installed {dst}")


def step_shell(ctx):
    shell = ctx.manifest["shell"]
    path, user = shell["path"], os.environ.get("USER", "")
    shells = Path("/etc/shells").read_text().splitlines()
    if path in shells:
        Log.skip(f"{path} already registered in /etc/shells")
    else:
        if not ctx.dry_run:
            subprocess.run(["sudo", "tee", "-a", "/etc/shells"], input=path + "\n",
                           text=True, check=True, stdout=subprocess.DEVNULL)
        Log.ok(f"registered {path} in /etc/shells")
    current = out(ctx, ["getent", "passwd", user]).split(":")[-1]
    if current == path:
        Log.skip(f"login shell is already {path}")
    else:
        run(ctx, ["chsh", "-s", path, user], sudo=True)
        ctx.note("Re-login for the fish login shell to take effect")


def ensure_line(ctx, file, line, marker):
    if file.is_file() and marker in file.read_text():
        Log.skip(f"{file} already references {marker}")
        return
    Log.info(f"appending to {file}: {line}")
    if not ctx.dry_run:
        with open(file, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def step_path(ctx):
    ensure_line(ctx, HOME / ".bashrc",
                'export PATH="$HOME/.local/bin:$PATH"', ".local/bin")
    fish_conf = CONFIG / "fish" / "config.fish"
    if fish_conf.is_file() or fish_conf.is_symlink():
        ensure_line(ctx, fish_conf, "fish_add_path -g ~/.local/bin", ".local/bin")


def step_groups(ctx):
    user = os.environ.get("USER", "")
    current = set(out(ctx, ["id", "-nG", user]).split())
    for g in pkg_names(ctx.manifest.get("groups", [])):
        if g in current:
            Log.skip(f"{user} already in group {g}")
            continue
        run(ctx, ["usermod", "-aG", g, user], sudo=True)
        ctx.note(f"Re-login (or reboot) for the '{g}' group membership to take effect")


def step_services(ctx):
    services = ctx.manifest.get("services", {})
    for unit in services.get("system_enable", []):
        state = out(ctx, ["systemctl", "is-enabled", unit])
        if state == "enabled":
            Log.skip(f"{unit} already enabled")
        else:
            run(ctx, ["systemctl", "enable", unit], sudo=True)
    for unit in services.get("user_verify", []):
        state = out(ctx, ["systemctl", "--user", "is-enabled", unit])
        if state != "enabled":
            Log.warn(f"user unit {unit} is '{state or 'missing'}' — usually enabled by package presets; check after reboot")
    for entry in services.get("user_do_not_enable", []):
        unit = entry if isinstance(entry, str) else entry["name"]
        state = out(ctx, ["systemctl", "--user", "is-enabled", unit])
        if state == "enabled":
            reason = "" if isinstance(entry, str) else f" ({entry.get('reason', '')})"
            Log.warn(f"{unit} is enabled but must not be{reason} — disabling")
            run(ctx, ["systemctl", "--user", "disable", "--now", unit])
        else:
            Log.skip(f"{unit} correctly not enabled")


def current_display_manager(ctx):
    link = Path("/etc/systemd/system/display-manager.service")
    if link.is_symlink():
        return Path(os.readlink(link)).name.removesuffix(".service")
    return None


def step_display_manager(ctx):
    dm_conf = ctx.manifest["display_manager"]
    current = current_display_manager(ctx)
    choice = ctx.args.dm
    if choice is None:
        if current:
            Log.skip(f"display manager '{current}' already enabled (use --dm/--force-dm to change)")
            return
        default = dm_conf.get("default", "sddm")
        if ctx.interactive:
            options = "/".join(dm_conf["variants"])
            try:
                typed = input(f"    display manager ({options}) [{default}]: ").strip()
                choice = typed or default
            except EOFError:
                choice = default
        else:
            choice = default
    if choice == "skip":
        Log.skip("display manager step skipped")
        return
    if choice not in dm_conf["variants"]:
        Log.err(f"unknown display manager '{choice}'")
        return
    if current and current != choice:
        if not ctx.args.force_dm:
            Log.warn(f"'{current}' is currently enabled; re-run with --dm={choice} --force-dm to replace it")
            return
        run(ctx, ["systemctl", "disable", current], sudo=True)
    variant = dm_conf["variants"][choice]
    if variant.get("packages"):
        run(ctx, ["pacman", "-S", "--needed", "--noconfirm"] + variant["packages"], sudo=True)
    if choice == "greetd":
        greetd_conf = Path("/etc/greetd/config.toml")
        if not greetd_conf.exists() and not ctx.dry_run:
            content = ('[terminal]\nvt = 1\n\n[default_session]\n'
                       'command = "tuigreet --remember --cmd Hyprland"\nuser = "greeter"\n')
            subprocess.run(["sudo", "mkdir", "-p", "/etc/greetd"], check=True)
            subprocess.run(["sudo", "tee", str(greetd_conf)], input=content,
                           text=True, check=True, stdout=subprocess.DEVNULL)
    if choice == "tty":
        ctx.note("tty login chosen: add a getty autologin drop-in and start Hyprland from fish on tty1")
        return
    if variant.get("enable"):
        run(ctx, ["systemctl", "enable", variant["enable"]], sudo=True)
        Log.ok(f"{choice} installed and enabled")


def step_nvidia_check(ctx):
    installed = installed_packages(ctx)
    if "nvidia-open-dkms" not in installed:
        Log.skip("nvidia-open-dkms not installed — nothing to check")
        return
    status = out(ctx, ["dkms", "status"])
    if "nvidia" in status and "installed" in status:
        Log.ok("dkms reports nvidia modules built")
    else:
        Log.warn("nvidia dkms modules not built yet — they build automatically when "
                 "linux-headers are present; verify with `dkms status` and `nvidia-smi` after reboot")
    ctx.note("After reboot verify the GPU stack: nvidia-smi")


def step_voxtype(ctx):
    if "voxtype" not in installed_packages(ctx):
        Log.skip("voxtype not installed")
        return
    vox = ctx.manifest.get("voxtype", {})
    model = Path(os.path.expanduser(vox.get("model_path", "")))
    if model.is_file():
        Log.skip(f"whisper model already present: {model}")
    elif ctx.args.skip_model:
        ctx.note(f"Download the voxtype model later: voxtype setup --download --model {vox.get('model_name')}")
    else:
        size = vox.get("download_size", "large")
        if confirm(ctx, f"Download voxtype whisper model {vox.get('model_name')} ({size})?", default=True):
            run(ctx, ["voxtype", "setup", "--download", "--model", vox.get("model_name", "large-v3"),
                      "--no-post-install"])
        else:
            ctx.note(f"Download the voxtype model later: voxtype setup --download --model {vox.get('model_name')}")
    if ctx.args.voxtype_gpu:
        run(ctx, ["voxtype", "setup", "gpu", "--enable"], sudo=True)
    ctx.note("voxtype starts via Hyprland exec-once (never enable voxtype.service); "
             "test dictation with the SCROLLLOCK hotkey after re-login")


INSTALL_STEPS = [
    ("preflight", "sanity checks", step_preflight, None),
    ("multilib", "enable [multilib] repo", step_multilib, None),
    ("update", "full system update (pacman -Syu)", step_update, None),
    ("git-config", "git identity", step_git_config, None),
    ("yay", "bootstrap yay from AUR", step_yay, None),
    ("native", "official repo packages", step_native, "skip_native"),
    ("aur", "AUR packages", step_aur, "skip_aur"),
    ("npm", "npm global packages", step_npm, "skip_npm"),
    ("curl-tools", "claude-code / codex CLIs", step_curl_tools, "skip_curl"),
    ("deploy", "deploy dotfiles", step_deploy, "skip_deploy"),
    ("system-files", "system config files", step_system_files, "skip_deploy"),
    ("shell", "fish as login shell", step_shell, None),
    ("path", "~/.local/bin on PATH", step_path, None),
    ("groups", "user groups", step_groups, None),
    ("services", "systemd services", step_services, "skip_services"),
    ("display-manager", "display manager", step_display_manager, "skip_services"),
    ("nvidia-check", "NVIDIA/dkms sanity check", step_nvidia_check, None),
    ("voxtype", "voxtype model + GPU setup", step_voxtype, None),
]


def cmd_install(ctx):
    only = set(ctx.args.only.split(",")) if ctx.args.only else None
    if only:
        unknown = only - {name for name, *_ in INSTALL_STEPS}
        if unknown:
            Log.err(f"unknown step(s): {', '.join(sorted(unknown))} (see --list-steps)")
            sys.exit(1)
    needs_sudo = only is None or only - {"preflight", "git-config", "path", "deploy", "nvidia-check"}
    if only is None or "preflight" in only:
        Log.step("preflight", "sanity checks")
        step_preflight(ctx)
    if needs_sudo:
        start_sudo_keepalive(ctx)
    for name, title, func, skip_attr in INSTALL_STEPS:
        if name == "preflight":
            continue
        if only is not None and name not in only:
            continue
        if skip_attr and getattr(ctx.args, skip_attr, False):
            Log.step(name, title)
            Log.skip(f"--{skip_attr.replace('_', '-')}")
            continue
        Log.step(name, title)
        func(ctx)
    print()
    if ctx.checklist:
        print(Log._c("1;33", "=== Post-install checklist ==="))
        for item in ctx.checklist:
            print(f"  * {item}")
    print(Log._c("1;32", "\nDone." + (" (dry run — nothing was changed)" if ctx.dry_run else "")))


# ------------------------------------------------------------------- sync ---

def sync_configs(ctx):
    for d in ctx.manifest["deploy"]["config_dirs"]:
        live = CONFIG / d
        repo = REPO_ROOT / d
        if live.is_symlink():
            if live.resolve() == repo.resolve():
                Log.skip(f"{live} is a symlink into the repo — always in sync")
            else:
                Log.warn(f"{live} is a symlink to {os.readlink(live)} — not syncing")
            continue
        if not live.is_dir():
            Log.warn(f"{live} does not exist — skipped")
            continue
        Log.info(f"mirror {live} -> {repo}")
        if not ctx.dry_run:
            if repo.exists():
                shutil.rmtree(repo)
            shutil.copytree(live, repo)
    wp = ctx.manifest["deploy"]["wallpapers"]
    live = Path(os.path.expanduser(wp["dst"]))
    repo = REPO_ROOT / wp["src"]
    if live.is_symlink():
        Log.skip(f"{live} is a symlink — wallpapers live in the repo already")
    elif live.is_dir():
        Log.info(f"mirror {live} -> {repo}")
        if not ctx.dry_run:
            if repo.exists():
                shutil.rmtree(repo)
            shutil.copytree(live, repo)


def sync_packages(ctx):
    policy = ctx.manifest["sync_policy"]
    keep_always = set(policy.get("keep_always", []))
    optional_names = set(pkg_names(ctx.manifest.get("optional", [])))
    removed_names = set(pkg_names(ctx.manifest.get("removed_do_not_install", [])))

    def excluded(name):
        if name in policy.get("keep_exceptions", []):
            return False
        return any(fnmatch.fnmatch(name, g) for g in policy.get("exclude_globs", []))

    native_now = set(out(ctx, ["pacman", "-Qqen"]).split())
    foreign_now = set(out(ctx, ["pacman", "-Qqem"]).split())

    desired_native = {n for n in native_now
                      if not excluded(n) and n not in optional_names and n not in removed_names}
    desired_aur = {n for n in foreign_now
                   if not any(fnmatch.fnmatch(n, g) for g in policy.get("aur_exclude_globs", []))
                   and n not in removed_names}

    def merge(existing, desired):
        names = set(pkg_names(existing))
        kept = [e for e in existing
                if (n := (e if isinstance(e, str) else e["name"])) in desired or n in keep_always]
        added = sorted(desired - names)
        dropped = sorted(names - desired - keep_always)
        return kept + added, added, dropped

    new_pacman, pac_added, pac_dropped = merge(ctx.manifest["pacman"], desired_native)
    new_aur, aur_added, aur_dropped = merge(ctx.manifest["aur"], desired_aur)

    for label, added, dropped in (("pacman", pac_added, pac_dropped), ("aur", aur_added, aur_dropped)):
        if added:
            Log.ok(f"{label}: added {' '.join(added)}")
        if dropped:
            Log.warn(f"{label}: dropped (no longer explicitly installed): {' '.join(dropped)}")
        if not added and not dropped:
            Log.skip(f"{label}: no changes")

    if pac_added or pac_dropped or aur_added or aur_dropped:
        ctx.manifest["pacman"] = new_pacman
        ctx.manifest["aur"] = new_aur
        ctx.manifest["meta"]["generated_on"] = datetime.now().strftime("%Y-%m-%d")
        if not ctx.dry_run:
            with open(REPO_ROOT / "packages.json", "w", encoding="utf-8") as f:
                json.dump(ctx.manifest, f, indent=2, ensure_ascii=False)
                f.write("\n")
        Log.ok("packages.json regenerated")


def cmd_sync(ctx):
    if not ctx.args.packages_only:
        Log.step("sync", "live configs -> repo")
        sync_configs(ctx)
    if not ctx.args.configs_only:
        Log.step("sync", "package lists -> packages.json")
        sync_packages(ctx)
    Log.step("sync", "repo status")
    status = out(ctx, ["git", "-C", str(REPO_ROOT), "status", "--short"])
    print(status or "    clean")
    if status:
        Log.info("review and commit: git -C ~/Documents/dots add -A && git -C ~/Documents/dots commit")


# ------------------------------------------------------------------ check ---

def cmd_check(ctx):
    manifest = ctx.manifest
    ok = True

    Log.step("check", "official repo packages resolve (pacman -Si)")
    native = pkg_names(manifest["pacman"]) + pkg_names(manifest.get("optional", []))
    for variant in manifest["display_manager"]["variants"].values():
        native += variant.get("packages", [])
    r = run(ctx, ["pacman", "-Si"] + sorted(set(native)), check=False, capture=True, ro=True)
    bad = [line.split("'")[1] for line in (r.stderr or "").splitlines() if "was not found" in line]
    if bad:
        ok = False
        Log.err(f"not in official repos: {' '.join(bad)} (moved to/from AUR? update packages.json)")
    else:
        Log.ok(f"{len(set(native))} native package names resolve")

    Log.step("check", "AUR packages resolve (yay -Si)")
    if shutil.which("yay"):
        aur = sorted(set(pkg_names(manifest["aur"])))
        r = run(ctx, ["yay", "-Si"] + aur, check=False, capture=True, ro=True)
        bad = [line.split("'")[1] for line in (r.stderr or "").splitlines() if "was not found" in line]
        if bad:
            ok = False
            Log.err(f"not found in AUR/repos: {' '.join(bad)}")
        else:
            Log.ok(f"{len(aur)} AUR package names resolve")
    else:
        Log.warn("yay not installed — AUR names not validated")

    Log.step("check", "removed_do_not_install packages")
    installed = installed_packages(ctx)
    present = [p for p in pkg_names(manifest.get("removed_do_not_install", [])) if p in installed]
    if present:
        Log.warn(f"installed although on the do-not-install list: {' '.join(present)}")
    else:
        Log.ok("none installed")

    sys.exit(0 if ok else 1)


# ------------------------------------------------------------------- main ---

def parse_args():
    p = argparse.ArgumentParser(prog="install.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")

    pi = sub.add_parser("install", help="restore the system (default)")
    pi.add_argument("--dry-run", action="store_true", help="print actions without executing")
    pi.add_argument("--noconfirm", action="store_true", help="take defaults for all prompts")
    pi.add_argument("--mode", choices=["symlink", "copy"], help="dotfile deploy strategy (default: symlink)")
    pi.add_argument("--dm", choices=["sddm", "gdm", "greetd", "tty", "skip"], help="display manager")
    pi.add_argument("--force-dm", action="store_true", help="replace an already-enabled display manager")
    for flag in ("update", "native", "aur", "npm", "curl", "deploy", "services", "model"):
        pi.add_argument(f"--skip-{flag}", action="store_true", help=f"skip the {flag} phase")
    pi.add_argument("--with-optional", action="store_true", help="also install optional[] packages")
    pi.add_argument("--with-zsh", action="store_true", help="also deploy the legacy .zshrc")
    pi.add_argument("--voxtype-gpu", action="store_true", help="run `voxtype setup gpu --enable`")
    pi.add_argument("--git-name", help="git user.name (skips prompt)")
    pi.add_argument("--git-email", help="git user.email (skips prompt)")
    pi.add_argument("--only", help="comma-separated list of steps to run")
    pi.add_argument("--list-steps", action="store_true", help="list step names and exit")

    ps = sub.add_parser("sync", help="live configs + package lists -> repo")
    ps.add_argument("--dry-run", action="store_true")
    ps.add_argument("--packages-only", action="store_true", help="only regenerate packages.json")
    ps.add_argument("--configs-only", action="store_true", help="only mirror configs/wallpapers")

    sub.add_parser("check", help="validate packages.json against repos")

    argv = sys.argv[1:]
    if not argv or argv[0].startswith("-"):
        argv = ["install"] + argv
    return p.parse_args(argv)


def main():
    args = parse_args()
    if getattr(args, "list_steps", False):
        for name, title, *_ in INSTALL_STEPS:
            print(f"{name:16} {title}")
        return
    manifest = load_manifest()
    ctx = Ctx(args, manifest)
    if args.cmd == "sync":
        cmd_sync(ctx)
    elif args.cmd == "check":
        cmd_check(ctx)
    else:
        cmd_install(ctx)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\ninterrupted")
        sys.exit(130)
    except subprocess.CalledProcessError as e:
        Log.err(f"command failed with exit code {e.returncode}: {e.cmd}")
        sys.exit(e.returncode)
