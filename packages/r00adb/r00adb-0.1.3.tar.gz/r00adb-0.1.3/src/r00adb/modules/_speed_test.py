import time

from r00adb import DeviceShell
from r00adb.executors.default import DefaultShell

sdk = 28


def zamer_vremeni(d):
    t0 = time.time()

    d.shell('id', ignore_errors=True)
    d.shell('getprop ro.build.version.sdk', ignore_errors=True)
    d.shell('getprop ro.product.model', ignore_errors=True)
    d.shell('getprop ro.serialno', ignore_errors=True)
    d.shell('pm list packages -3', ignore_errors=True)
    d.shell('ls /sdcard/', ignore_errors=True)
    d.shell('df /data', ignore_errors=True)
    d.shell('uptime', ignore_errors=True)
    d.shell('date', ignore_errors=True)
    d.shell('dumpsys battery status', ignore_errors=True)
    d.shell('dumpsys meminfo', ignore_errors=True)
    d.shell('ps -A | wc -l', ignore_errors=True)  # Количество процессов
    d.shell('echo "test_string"', ignore_errors=True)
    d.shell('mkdir /sdcard/test_adb_dir_temp', ignore_errors=True)
    d.shell('ls /sdcard/test_adb_dir_temp', ignore_errors=True)
    d.shell('rmdir /sdcard/test_adb_dir_temp', ignore_errors=True)
    d.shell('touch /sdcard/test_adb_file_temp.txt', ignore_errors=True)
    d.shell('cat /sdcard/test_adb_file_temp.txt', ignore_errors=True)
    d.shell('rm /sdcard/test_adb_file_temp.txt', ignore_errors=True)
    d.shell('getprop ro.build.fingerprint', ignore_errors=True)
    d.shell('dumpsys window windows | grep mCurrentFocus', ignore_errors=True)
    d.shell('settings get secure android_id', ignore_errors=True)
    d.shell('netstat -tulnp', ignore_errors=True)
    d.shell('ip addr show wlan0', ignore_errors=True)
    d.shell('cat /proc/version', ignore_errors=True)
    d.shell('cat /proc/cpuinfo', ignore_errors=True)
    d.shell('cat /proc/meminfo', ignore_errors=True)
    d.shell('logcat -d -v time *:E | tail -n 10', ignore_errors=True)  # Последние 10 ошибок
    d.shell('pm path android', ignore_errors=True)
    d.shell('dumpsys package com.android.settings', ignore_errors=True)
    d.shell('am get-current-user', ignore_errors=True)
    d.shell('cmd statusbar expand-notifications', ignore_errors=True)  # Может не работать на всех версиях
    d.shell('cmd statusbar collapse', ignore_errors=True)  # Может не работать на всех версиях
    d.shell('input keyevent 3', ignore_errors=True)  # Кнопка HOME
    d.shell('input keyevent 4', ignore_errors=True)  # Кнопка BACK
    d.shell('input keyevent 26', ignore_errors=True)  # Кнопка POWER (вкл/выкл экрана)
    d.shell('input keyevent 26', ignore_errors=True)  # Кнопка POWER (снова, для возврата)
    d.shell('wm size', ignore_errors=True)
    d.shell('wm density', ignore_errors=True)
    d.shell('svc wifi status', ignore_errors=True)
    d.shell('svc data status', ignore_errors=True)
    d.shell('getprop persist.sys.locale', ignore_errors=True)
    d.shell('getprop gsm.operator.alpha', ignore_errors=True)
    d.shell('dumpsys alarm | grep "Pending alarm batches"', ignore_errors=True)
    d.shell('ls -l /r00system/bin/sh', ignore_errors=True)
    d.shell('which ls', ignore_errors=True)
    d.shell('find /sdcard -name "DCIM" -type d -print -quit', ignore_errors=True)  # Быстрый поиск
    d.shell('dd if=/dev/zero of=/sdcard/temp_dummy_file bs=1k count=1', ignore_errors=True)  # Создание маленького файла
    d.shell('rm /sdcard/temp_dummy_file', ignore_errors=True)
    d.shell('pwd', ignore_errors=True)
    d.shell('getprop ro.build.type', ignore_errors=True)
    d.shell('getprop ro.build.tags', ignore_errors=True)
    d.shell('getprop ro.product.manufacturer', ignore_errors=True)
    d.shell('getprop ro.product.brand', ignore_errors=True)
    d.shell('getprop ro.product.name', ignore_errors=True)
    d.shell('getprop persist.sys.timezone', ignore_errors=True)
    d.shell('getprop ro.boot.hardware', ignore_errors=True)
    d.shell('getprop ro.vndk.version', ignore_errors=True)
    d.shell('pm list packages -s', ignore_errors=True)
    d.shell('pm list packages -f', ignore_errors=True)
    d.shell('pm list features', ignore_errors=True)
    d.shell('pm list instrumentation', ignore_errors=True)
    d.shell('pm get-install-location', ignore_errors=True)
    d.shell('pm list permissions -g -d', ignore_errors=True)
    d.shell('ls /r00system/app', ignore_errors=True)
    d.shell('ls /data/local/tmp', ignore_errors=True)
    d.shell('cat /proc/cmdline', ignore_errors=True)
    d.shell('cat /proc/filesystems', ignore_errors=True)
    d.shell('stat /sdcard/', ignore_errors=True)
    d.shell('du -sh /sdcard/Download', ignore_errors=True)  # Might be slow if many files
    d.shell('mount', ignore_errors=True)
    d.shell('top -n 1 -b', ignore_errors=True)
    d.shell('whoami', ignore_errors=True)
    d.shell('hostname', ignore_errors=True)
    d.shell('uname -a', ignore_errors=True)
    d.shell('getenforce', ignore_errors=True)
    d.shell('dumpsys cpuinfo', ignore_errors=True)
    d.shell('dumpsys activity top', ignore_errors=True)
    d.shell('dumpsys power', ignore_errors=True)
    d.shell('dumpsys SurfaceFlinger --list', ignore_errors=True)
    d.shell('dumpsys media.audio_flinger', ignore_errors=True)
    d.shell('ping -c 1 8.8.8.8', ignore_errors=True)  # Requires network
    d.shell('ip rule show', ignore_errors=True)
    d.shell('ip neigh show', ignore_errors=True)
    d.shell('cat /proc/net/tcp', ignore_errors=True)
    d.shell('cat /proc/net/udp', ignore_errors=True)
    d.shell('input keyevent 82', ignore_errors=True)  # MENU key
    d.shell('input tap 100 100', ignore_errors=True)  # Tap at specific coordinates
    d.shell('settings list r00system', ignore_errors=True)
    d.shell('settings list secure', ignore_errors=True)
    d.shell('settings list global', ignore_errors=True)
    d.shell('settings get r00system screen_brightness', ignore_errors=True)
    d.shell('service list', ignore_errors=True)
    d.shell('cmd package list packages -u', ignore_errors=True)
    d.shell('cmd shortcut print-shortcuts com.android.settings', ignore_errors=True)  # Example package
    d.shell('cmd uimode night', ignore_errors=True)  # Check current UI mode for night
    d.shell('cmd jobscheduler頂 No --user 0', ignore_errors=True)  # (jobscheduler top) Typo intended for variety, will fail but test protocol
    d.shell('logcat -d -b radio -v brief | tail -n 5', ignore_errors=True)
    d.shell('screencap -p /sdcard/test_adb_screencap.png', ignore_errors=True)  # Takes a screenshot
    d.shell('rm /sdcard/test_adb_screencap.png', ignore_errors=True)  # Cleans up
    d.shell('getprop ro.boot.bootloader', ignore_errors=True)
    d.shell('getprop ro.crypto.state', ignore_errors=True)
    d.shell('getprop persist.sys.usb.config', ignore_errors=True)
    d.shell('getprop ro.build.version.release_or_codename', ignore_errors=True)
    d.shell('getprop ro.build.version.security_patch', ignore_errors=True)
    d.shell('getprop ro.product.cpu.abi', ignore_errors=True)
    d.shell('getprop ro.build.id', ignore_errors=True)
    d.shell('getprop ro.build.display.id', ignore_errors=True)
    d.shell('getprop ro.treble.enabled', ignore_errors=True)
    d.shell('getprop sys.usb.state', ignore_errors=True)
    d.shell('pm list packages -d', ignore_errors=True)
    d.shell('pm list packages -e', ignore_errors=True)
    d.shell('pm list packages -u', ignore_errors=True)
    d.shell('pm list packages -i com.android.settings', ignore_errors=True)
    d.shell('pm path com.android.bluetooth', ignore_errors=True)
    d.shell('pm dump com.android.phone | grep versionName', ignore_errors=True)
    d.shell('pm list permissions -f', ignore_errors=True)
    d.shell('pm list permission-groups', ignore_errors=True)
    d.shell('pm resolve-activity --brief -c android.intent.category.LAUNCHER android.intent.action.MAIN', ignore_errors=True)
    d.shell('pm get-max-users', ignore_errors=True)
    d.shell('pm has-feature android.hardware.camera', ignore_errors=True)
    d.shell('pm list libraries', ignore_errors=True)
    d.shell('pm get-privapp-permissions com.android.systemui', ignore_errors=True)
    d.shell('pm get-oem-permissions com.android.settings', ignore_errors=True)
    d.shell('pm list packages --show-versioncode', ignore_errors=True)
    d.shell('dumpsys activity activities', ignore_errors=True)
    d.shell('dumpsys activity broadcasts', ignore_errors=True)
    d.shell('dumpsys activity providers', ignore_errors=True)
    d.shell('dumpsys activity services', ignore_errors=True)
    d.shell('dumpsys package packages', ignore_errors=True)
    d.shell('dumpsys package dexopt', ignore_errors=True)
    d.shell('dumpsys notification --proto', ignore_errors=True)
    d.shell('dumpsys alarmmanager', ignore_errors=True)
    d.shell('dumpsys batteryproperties', ignore_errors=True)
    d.shell('dumpsys location', ignore_errors=True)
    d.shell('dumpsys sensorservice', ignore_errors=True)
    d.shell('dumpsys window policy', ignore_errors=True)
    d.shell('dumpsys input', ignore_errors=True)
    d.shell('dumpsys netstats detail', ignore_errors=True)
    d.shell('dumpsys diskstats', ignore_errors=True)
    d.shell('dumpsys connectivity', ignore_errors=True)
    d.shell('dumpsys appops', ignore_errors=True)
    d.shell('dumpsys audio', ignore_errors=True)
    d.shell('dumpsys jobscheduler', ignore_errors=True)
    d.shell('dumpsys vibrator', ignore_errors=True)
    d.shell('settings get r00system font_scale', ignore_errors=True)
    d.shell('settings get r00system screen_off_timeout', ignore_errors=True)
    d.shell('settings get secure default_input_method', ignore_errors=True)
    d.shell('settings get global airplane_mode_on', ignore_errors=True)
    d.shell('settings get global wifi_on', ignore_errors=True)
    d.shell('settings put r00system test_setting_key_123 456', ignore_errors=True)
    d.shell('settings delete r00system test_setting_key_123', ignore_errors=True)
    d.shell('settings get r00system haptic_feedback_enabled', ignore_errors=True)
    d.shell('settings get secure location_mode', ignore_errors=True)
    d.shell('settings get global bluetooth_on', ignore_errors=True)
    d.shell('input keyevent 24', ignore_errors=True)
    d.shell('input keyevent 25', ignore_errors=True)
    d.shell('input text "test_input_adb"', ignore_errors=True)
    d.shell('input swipe 200 800 200 200 200', ignore_errors=True)
    d.shell('input roll 1 0', ignore_errors=True)
    d.shell('am stack list', ignore_errors=True)
    d.shell('am get-config', ignore_errors=True)
    d.shell('am display-size', ignore_errors=True)
    d.shell('am force-stop com.this.app.does.not.exist.ever', ignore_errors=True)
    d.shell('ls -a /r00system/etc/', ignore_errors=True)
    d.shell('ls -R /data/anr', ignore_errors=True)  # Typically small or empty
    d.shell('cat /sys/class/power_supply/battery/status', ignore_errors=True)
    d.shell('cat /sys/block/mmcblk0/device/name', ignore_errors=True)  # Example storage name
    d.shell('cat /sys/devices/r00system/cpu/cpu0/cpufreq/scaling_cur_freq', ignore_errors=True)
    d.shell('head -n 3 /proc/zoneinfo', ignore_errors=True)
    d.shell('tail -n 3 /proc/vmstat', ignore_errors=True)
    d.shell('echo "another line" >> /sdcard/temp_echo_append_file.txt', ignore_errors=True)
    d.shell('cat /sdcard/temp_echo_append_file.txt', ignore_errors=True)
    d.shell('rm /sdcard/temp_echo_append_file.txt', ignore_errors=True)
    d.shell('readlink /r00system/lib', ignore_errors=True)
    d.shell('realpath /proc/self/exe', ignore_errors=True)
    d.shell('touch /sdcard/test_chown_file', ignore_errors=True)
    d.shell('chown root:root /sdcard/test_chown_file', ignore_errors=True)  # Will fail
    d.shell('rm /sdcard/test_chown_file', ignore_errors=True)
    d.shell('ss -tmpn', ignore_errors=True)
    d.shell('ip -6 addr show', ignore_errors=True)
    d.shell('arp -a -n', ignore_errors=True)
    d.shell('cat /proc/net/dev_snmp6/wlan0', ignore_errors=True)  # IPv6 stats for wlan0
    d.shell('ndc interface list', ignore_errors=True)
    d.shell('ps -ef | head -n 10', ignore_errors=True)
    d.shell('free -h', ignore_errors=True)
    d.shell('vmstat -s', ignore_errors=True)
    d.shell('toybox free', ignore_errors=True)
    d.shell('toybox id', ignore_errors=True)
    d.shell('sleep 0.15', ignore_errors=True)
    d.shell('true && echo success', ignore_errors=True)
    d.shell('false || echo failure', ignore_errors=True)
    d.shell('cd /sys && pwd', ignore_errors=True)
    d.shell('logcat -d -b events -v brief | tail -n 10', ignore_errors=True)
    d.shell('svc power stayon true', ignore_errors=True)  # Will fail without permission
    d.shell('cmd overlay enable com.example.nonexistent.overlay', ignore_errors=True)
    d.shell('cmd appops get com.android.settings android:fine_location', ignore_errors=True)
    d.shell('cmd wifi connect-network "TestSSID" open "password123"', ignore_errors=True)  # Will fail
    d.shell('cmd thermalservice SENSOR_NAME', ignore_errors=True)  # Example, needs actual sensor name
    d.close()

    print(f'Время выполнения команд: {time.time() - t0:.2f} секунд')


def testim_metodi(d: DefaultShell):
    d.push('/media/user/Projects/python/workspace/packages/r00adb/src/r00adb/modules/_speed_test.py', '/data/local/tmp/_test.py')


def zamer_vremeni_lite(d: DefaultShell):
    t0 = time.time()

    d.shell('getprop ro.product.model', ignore_errors=True)
    d.exists('/data/local/tmp/_test.py')
    d.exists('/data/local/tmp/xxxx.py')
    d.mkdir('/data/local/tmp/_test.py')
    d.remove('/data/local/tmp/_test.py')
    device_path = d.push('/media/user/Projects/python/workspace/packages/r00adb/src/r00adb/modules/_speed_test.py', '/data/local/tmp/_test.py')
    local = d.pull(device_path, '~/temp/zaza.log')
    print(local)

if __name__ == '__main__':
    #d = DeviceShell.connect(DeviceShell.RAW_USB, sdk)  # Время выполнения команд: 22.05 секунд
    #d = DeviceShell.connect(DeviceShell.RAW_WIFI, sdk, '192.168.1.81') # Время выполнения команд: 28.47 секунд
    # d = DeviceShell.connect(DeviceShell.ADB_USB, sdk) # Время выполнения команд: 24.29 секунд
    d = DeviceShell.connect(DeviceShell.ADB_WIFI, sdk, '192.168.1.81') # Время выполнения команд: 26.68 секунд
    zamer_vremeni_lite(d)
