#!/usr/bin/env bash

EXTRA_LOG_FILE=/tmp/extra_commands.log

# MONITOR
options_monitor_turn_on_ddcutil=
options_monitor_turn_off_ddcutil=


options_script_shortcuts="[CHARM]: Show keybind cheatsheet (Shortcuts)"

# PIN WINDOWS
options_hyprland_toogle_pin=" : Pin floating window (Show on all workspaces)"
# TAGS

# Volume / Light Control
# Keyboard backlight controll
# Music controll

options="\
$option_group_togglelock\n\
$options_monitor_turn_on_ddcutil\n\
$options_monitor_turn_off_ddcutil\n\
$options_utility_colorpicker\n\
$options_utility_calculator\n\
$options_ss_region\n\
$options_ss_window\n\
$options_ss_monitor\n\
$options_ss_region_clipboard\n\
$options_ss_window_clipboard\n\
$options_ss_monitor_clipboard\n\
$options_hyprland_toogle_pin\n\
$options_script_shortcuts\
"
selected=$(echo -e $options | wofi --dmenu --prompt="Quick Menu" --lines --width=75% )

selected="${selected%"${selected##*[![:space:]]}"}"  # Trim trailing whitespace
selected="${selected#"${selected%%[![:space:]]*}"}"  # Trim leading whitespace



case $selected in
  "")
    # preventing the unkown command prompt if cancel
    ;;
  *)
    echo "sowwy, unkown command: |$selected|"| wofi --dmenu
    ;;
esac