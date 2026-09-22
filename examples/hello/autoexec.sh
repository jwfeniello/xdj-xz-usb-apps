#!/bin/sh
PATH=/bin:/sbin:/usr/bin:/usr/sbin
export PATH
usb=$1
case "$usb" in /media/usb1/sd*|/media/usb2/sd*) ;; *) exit 1 ;; esac
awk -v target="$usb" '$2==target && $3=="vfat" {ok=1} END {exit !ok}' /proc/mounts || exit 1
n=1
while [ -e "$usb/XZ_HELLO$n" ] || [ -L "$usb/XZ_HELLO$n" ]; do n=$((n+1)); [ "$n" -le 99 ] || exit 1; done
out="$usb/XZ_HELLO$n"
mkdir "$out" || exit 1
set -C
exec > "$out/report.txt" 2>&1 || exit 1
echo XZ_HELLO_LAUNCHER
/mnt/iso/hello
result=$?
echo "XZ_HELLO_EXIT=$result"
exit "$result"
