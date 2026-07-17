# dots

Arch Linux rice: **Hyprland + Noctalia Shell + fish + alacritty/kitty**, NVIDIA (open-dkms), pipewire, btrfs + timeshift.

![rice](media/no_widnows.png)
![alacritty](media/alacritty.png)

Репо зеркалит `~/.config` (плюс `Wallpapers/` → `~/Pictures/Wallpapers`) и содержит установщик, который разворачивает всю систему с нуля одной командой.

## Состав

| Директория | Что это |
|---|---|
| `hypr/` | Hyprland на **Lua** (`hyprland.lua` + `config/*.lua`), hypridle/hyprlock/hyprpaper, скрипты обоев и voxtype-toggle |
| `noctalia/` | Noctalia Shell (quickshell): settings, цвета, плагины |
| `fish/` | fish + Tide prompt (полностью вендорен, fisher не нужен) |
| `alacritty/`, `kitty/` | терминалы + коллекции тем |
| `fastfetch/`, `solaar/`, `voxtype/` | fetch-конфиг, Logitech-девайсы, голосовой ввод |
| `Wallpapers/` | обои (деплоятся в `~/Pictures/Wallpapers`) |
| `packages.json` | манифест: пакеты, сервисы, группы, деплой — всё, чем управляет установщик |
| `install.py` / `install.sh` | установщик и curl-бутстрап |
| `system/` | системные файлы (`zram-generator.conf` → `/etc/systemd/`) |

## Установка на голый Arch

Требования: свежий Arch, пользователь с sudo, сеть. Дальше одна команда:

```sh
curl -fsSL https://raw.githubusercontent.com/redmoondz/dots/master/install.sh | bash
```

Бутстрап сам доставит `git` и `python`, склонирует репо в `~/Documents/dots` и запустит `install.py`. Флаги пробрасываются через `bash -s --`:

```sh
# посмотреть, что будет сделано, ничего не меняя
curl -fsSL https://raw.githubusercontent.com/redmoondz/dots/master/install.sh | bash -s -- --dry-run

# полностью без вопросов (все промпты = дефолты)
curl -fsSL https://raw.githubusercontent.com/redmoondz/dots/master/install.sh | bash -s -- --noconfirm
```

Если репо уже склонировано — то же самое напрямую:

```sh
python3 ~/Documents/dots/install.py install [флаги]
```

### Что делает установщик (по шагам)

Все шаги **идемпотентны** — скрипт безопасно перезапускать, готовое печатается как `skip`, изменения как `ok`. Пароль sudo спрашивается один раз (дальше keepalive).

1. **preflight** — проверки: Arch, не root, sudo, сеть
2. **multilib** — включает `[multilib]` в pacman.conf (steam/wine/lib32)
3. **update** — `pacman -Syu` (частичные апгрейды на Arch опасны)
4. **git-config** — user.name/user.email (промпт с дефолтами)
5. **yay** — сборка yay из AUR через makepkg
6. **native / aur / npm / curl-tools** — все пакеты из `packages.json`: официальные, AUR (voxtype, noctalia-git, chrome, spotify…), `@openai/codex`, claude-code и codex CLI
7. **deploy** — конфиги **симлинками**: `~/.config/hypr → ~/Documents/dots/hypr` и т.д. Репо становится единственным источником правды — правки конфигов сразу видны в `git diff`. Существующие папки бэкапятся в `*.bak-<дата>`. Альтернатива: `--mode=copy`
8. **system-files** — `system/zram-generator.conf` → `/etc/systemd/`
9. **shell / path / groups** — fish в `/etc/shells` + `chsh`, `~/.local/bin` в PATH, группа `input` (нужна voxtype)
10. **services** — NetworkManager, bluetooth, cronie, timesyncd. Docker ставится, но сервис **не** включается. `voxtype.service` принудительно выключается — voxtype запускает Hyprland через `exec-once`, двойной запуск краш-лупит
11. **display-manager** — по умолчанию **SDDM** (`--dm gdm|greetd|tty|skip`). Уже включённый DM не трогается без `--force-dm`
12. **nvidia-check** — проверка, что dkms собрал модули nvidia (только предупреждает, не чинит)
13. **voxtype** — скачивание whisper-модели `large-v3` (~3 ГБ, спросит; `--skip-model` чтобы отложить), `--voxtype-gpu` для GPU-инференса
14. Финальный **чеклист** ручных действий

### Флаги

| Флаг | Значение |
|---|---|
| `--dry-run` | напечатать действия, ничего не выполняя |
| `--noconfirm` | не задавать вопросов, брать дефолты |
| `--mode symlink\|copy` | стратегия деплоя конфигов (дефолт: symlink) |
| `--dm sddm\|gdm\|greetd\|tty\|skip` | display manager (дефолт: sddm) |
| `--force-dm` | заменить уже включённый DM |
| `--skip-update / -native / -aur / -npm / -curl / -deploy / -services / -model` | пропустить фазу |
| `--with-optional` | доставить пакеты из `optional[]` (loupe, papers, hyprpolkitagent…) |
| `--with-zsh` | задеплоить legacy `.zshrc` |
| `--voxtype-gpu` | `voxtype setup gpu --enable` |
| `--git-name / --git-email` | git-идентичность без промпта |
| `--only шаг1,шаг2` | выполнить только указанные шаги (имена: `--list-steps`) |

Примеры:

```sh
python3 install.py install --only deploy          # только пересоздать симлинки
python3 install.py install --dm=greetd --force-dm # сменить DM на greetd
python3 install.py install --skip-aur --skip-model --noconfirm
```

## Обслуживание

```sh
python3 install.py sync     # пакетные списки -> packages.json
python3 install.py check    # все имена пакетов ещё резолвятся в repo/AUR
```

- **`sync`** регенерирует `packages.json` из `pacman -Qqen/-Qqem` по правилам `sync_policy`: GNOME-стек исключается, пины (pipewire, порталы, lib32-nvidia-utils, virtualbox-host-dkms…) сохраняются, пакеты из `removed_do_not_install` не возвращаются. Также зеркалит конфиги live → репо, если они ещё не симлинки. Сам ничего не коммитит — только показывает `git status`.
- **`check`** гоняет `pacman -Si` / `yay -Si` по всем именам — ловит миграции пакетов между AUR и официальными репами. Запускай перед восстановлением на новой машине.

Поставил новый пакет → `python3 install.py sync` → `git add -A && git commit && git push`. Поменял конфиг → он уже в репо (симлинки) → просто закоммить.

## Дизайн-решения

- **GNOME исключён.** На исходной машине GNOME стоит параллельно, но восстановление его не тянет: gdm/gnome-shell и весь стек в `sync_policy.exclude_globs`. Исключения: `gnome-keyring` (секреты под Hyprland) и GNOME-зависимости, ставшие явными пакетами (pipewire, bluez, libnotify, noto-fonts, polkit, xdg-desktop-portal-hyprland/-gtk).
- **Источник правды — pacman, не bash_history.** История хранит опечатки и откаты; манифест собран из `pacman -Qqen/-Qqem` и обновляется `sync`.
- **`removed_do_not_install`**: epiphany, noctalia-qs (заменён noctalia-git), datagrip, google-chrome-bin, voxtype-cuda — ставились и осознанно удалялись, установщик их никогда не вернёт.
- **Провайдер-пины**: `lib32-nvidia-utils` и `virtualbox-host-dkms` прописаны явно, иначе `--noconfirm` выберет lib32-mesa / virtualbox-host-modules-arch.

## Чеклист после установки (печатается и самим скриптом)

- Перезайти/перезагрузиться — группа `input`, login shell, драйвер NVIDIA
- Залогиниться в `claude` и `codex`
- `nvidia-smi` — проверить драйвер после перезагрузки
- Настроить снапшоты timeshift
- voxtype: хоткей **SCROLLLOCK** (push-to-talk); тумблер демона — `SUPER+ALT+R`

## Известные ограничения

- Бутстрап yay с нуля, первое включение SDDM, первая сборка dkms и `chsh` не прогонялись на живой голой машине — только в идемпотентном режиме на настроенной системе. При первом реальном восстановлении читай вывод шагов.
- Whisper-модель (~3 ГБ) не в репо и качается отдельно; без неё voxtype не работает.
- Логины claude/codex/chrome/spotify и прочие аккаунты не автоматизируются.
