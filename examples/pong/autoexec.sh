#!/bin/sh
PATH=/bin:/sbin:/usr/bin:/usr/sbin
export PATH
usb=$1
case "$usb" in /media/usb1/sd*|/media/usb2/sd*) ;; *) exit 1 ;; esac
awk -v target="$usb" '$2 == target && $3 == "vfat" {ok=1} END {exit !ok}' /proc/mounts || exit 1
dest="$usb/XZ_PONG2"
mkdir "$dest" || exit 1
set -C
exec > "$dest/report.txt" 2>&1 || exit 1
echo XZ_PONG_PRESENTATION_GATE_TEST
selected=
for p in /proc/[0-9]*; do
 [ -r "$p/comm" ] || continue
 [ "$(cat "$p/comm")" = rbp ] || continue
 [ -z "$selected" ] || exit 1
 selected=$p
done
[ -n "$selected" ] || exit 1
proc=$selected
digest=$(md5sum "$proc/exe" | awk '{print $1}')
[ "$digest" = 03722341b24045b36d3869b0c4c9968c ] || { echo 'App mismatch'; exit 1; }
start=$(awk '{print $22}' "$proc/stat")
[ -n "$start" ] || exit 1
readword() {
 dd if="$proc/mem" bs=4 skip="$1" count=1 | od -x | awk 'NR==1 && NF==3 && length($2)==4 && length($3)==4 && $2 !~ /[^0-9a-fA-F]/ && $3 !~ /[^0-9a-fA-F]/ {print "0x" $3 $2}'
}
emit32() {
 printf '%b' "\\$(printf '%03o' $(($1 & 255)))\\$(printf '%03o' $((($1 >> 8) & 255)))\\$(printf '%03o' $((($1 >> 16) & 255)))\\$(printf '%03o' $((($1 >> 24) & 255)))"
}
# s_layers[0], 1.25 verified symbol; bit 0 gates presentation, not validity.
slot=7072618
old=$(readword "$slot")
dimensions=$(readword $((slot + 2)))
echo "LAYER0_FLAGS=$old DIMENSIONS=$dimensions"
[ "$dimensions" = 0x01e00320 ] || { echo 'Unexpected main layer; no write'; exit 1; }
case "$old" in 0x40000001|0xc0000001) ;; *) echo 'Unexpected flags; no write'; exit 1 ;; esac
masked=$(($(($old)) & ~1))
emit32 "$masked" > "$dest/gated.bin"
emit32 "$old" > "$dest/original.bin"
[ "$(wc -c < "$dest/gated.bin")" -eq 4 ] || exit 1
same_process() { [ "$(awk '{print $22}' "$proc/stat")" = "$start" ]; }
restore() {
 same_process || { echo RESTORE_REFUSED_PROCESS_CHANGED; return 1; }
 current=$(readword "$slot")
 [ -n "$current" ] || return 1
 [ "$current" = "$old" ] && return 0
 [ "$((current))" -eq "$masked" ] || { echo RESTORE_REFUSED_FLAGS_CHANGED; return 1; }
 dd if="$dest/original.bin" of="$proc/mem" bs=4 seek="$slot" count=1 conv=notrunc || return 1
 [ "$(readword "$slot")" = "$old" ] && echo PRESENTATION_FLAG_RESTORED
}
# Arm restoration before attempting even the first write.
trap 'restore' 0
trap 'exit 1' 1 2 15
(sleep 25; echo WATCHDOG_RESTORE_CHECK; restore) &
watchdog=$!
same_process && [ "$(readword "$slot")" = "$old" ] || exit 1
dd if="$dest/gated.bin" of="$proc/mem" bs=4 seek="$slot" count=1 conv=notrunc || exit 1
check=$(readword "$slot")
[ -n "$check" ] && [ "$((check))" -eq "$masked" ] || exit 1
echo PRESENTATION_FLAG_GATED
sleep 1
/mnt/iso/pong
result=$?
echo "PONG_PROCESS_EXIT=$result"
restore
wait "$watchdog"
echo XZ_PONG_GATE_TEST_COMPLETE
exit "$result"
