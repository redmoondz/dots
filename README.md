# dots

Arch Linux rice: **Hyprland + Noctalia Shell + fish + alacritty/kitty**, NVIDIA (open-dkms), pipewire, btrfs + timeshift.

Репо зеркалит `~/.config` (плюс `Wallpapers/` → `~/Pictures/Wallpapers`) и содержит установщик, который разворачивает всю систему с нуля.

## Установка на голый Arch

```sh
curl -fsSL https://raw.githubusercontent.com/redmoondz/dots/master/install.sh | bash
```

Требования: свежий Arch (пользователь с sudo, сеть). Бутстрап сам доставит `git` и `python`, склонирует репо в `~/Documents/dots` и запустит `install.py`.

Флаги пробрасываются через `bash -s --`:

```sh
curl -fsSL https://raw.githubusercontent.com/redmoondz/dots/master/install.sh | bash -s -- --dry-run
```

## Что делает install.py

Все данные — в `packages.json` (пакеты, сервисы, группы, деплой). Шаги идемпотентны, скрипт безопасно перезапускать; `--dry-run` печатает действия без выполнения.

1. Проверки (Arch, не root, sudo, сеть) + sudo keepalive на весь прогон
2. `[multilib]` в pacman.conf → `pacman -Syu`
3. git user.name / user.email (промпт с дефолтами)
4. Бутстрап `yay` из AUR → официальные пакеты → AUR-пакеты → npm globals → claude-code / codex CLI
5. Деплой конфигов **симлинками** (`~/.config/hypr → ~/Documents/dots/hypr`, …); `--mode=copy` для копий; бэкапы существующих папок в `*.bak-<дата>`
6. `system/zram-generator.conf` → `/etc/systemd/`
7. fish: `/etc/shells` + `chsh`; PATH `~/.local/bin`; группа `input` (voxtype)
8. Сервисы: NetworkManager, bluetooth, cronie, timesyncd (docker не включается; `voxtype.service` принудительно выключен — voxtype запускает Hyprland через exec-once)
9. Display manager: **SDDM** по умолчанию (`--dm gdm|greetd|tty|skip`; смена уже включённого DM — только с `--force-dm`)
10. NVIDIA/dkms sanity-check и скачивание whisper-модели voxtype (~3 ГБ, `--skip-model` чтобы отложить)
11. Финальный чеклист ручных действий

Полный список флагов: `python3 install.py install --help`, список шагов: `--list-steps`, отдельные шаги: `--only deploy,services`.

## Обслуживание

```sh
python3 install.py sync     # пакетные списки -> packages.json (конфиги и так симлинки)
python3 install.py check    # все имена пакетов ещё резолвятся в repo/AUR
```

`sync` регенерирует `packages.json` из `pacman -Qqen/-Qqem` по правилам `sync_policy` (GNOME исключается, пины сохраняются). Конфиг-директории при симлинк-деплое синхронизировать не нужно — правки сразу видны в `git diff`.

## Что не автоматизируется (чеклист после установки)

- Перезайти/перезагрузиться (группа `input`, login shell, драйвер NVIDIA)
- Залогиниться в `claude` и `codex`
- `nvidia-smi` — проверить драйвер после перезагрузки
- Настроить снапшоты timeshift
- Проверить voxtype: хоткей SCROLLLOCK (push-to-talk)

## Что не тестировалось на живой голой машине

Бутстрап yay с нуля, первое включение SDDM, первая сборка dkms-модулей, `chsh`, скачивание модели — эти шаги написаны по документации/истории и прогонялись только в идемпотентном режиме на уже настроенной системе. При первом реальном восстановлении читай вывод шагов.
