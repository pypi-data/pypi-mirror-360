#!/usr/bin/env bash

# inspired by: https://github.com/jason9075/rofi-hyprland-keybinds-cheatsheet/blob/main/rofi_keybinds.sh
#TODO: add commentto all bindings and support bindings not based on bind, executing commands fails


HYPR_CONF="$HOME/.config/hypr/hyprland.conf"

# extract the keybinding from hyprland.conf
mapfile -t BINDINGS < <(grep '^bind=' "$HYPR_CONF" | \
    sed -e 's/  */ /g' -e 's/bind=//g' -e 's/, /,/g' -e 's/ # /,/' | \
    awk -F, -v q="'" '{cmd=""; for(i=3;i<NF;i++) cmd=cmd $(i) " ";print "<b>"$1 " + " $2 "</b>  <i>" $NF ",</i><span color=" q "gray" q ">" cmd "</span>"}')

CHOICE=$(printf '%s\n' "${BINDINGS[@]}" | wofi --dmenu --height=65% --width=75% --prompt "Hyprland Keybinds:")

# extract cmd from span <span color='gray'>cmd</span>
CMD=$(echo "$CHOICE" | sed -n 's/.*<span color='\''gray'\''>\(.*\)<\/span>.*/\1/p')

# execute it if first word is exec else use hyprctl dispatch
if [[ $CMD == exec* ]]; then
    eval "$CMD"
else
    hyprctl dispatch "$CMD"
fi
