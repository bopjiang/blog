---
title: "Raspberry Pi Tips"
date: 2020-06-13T11:36:41+08:00
draft: false
categories:
  - tech
---

## Basic Config
```
sudo raspi-config
```

### static IP per SSID in wireless network
```ini
# in /etc/wpa_supplicant/wpa_supplicant.conf
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=CN

network={
        ssid="WIFI-NAME"
        psk="password"
}
```

```ini
# in /etc/dhcpcd.conf
# set wifi static ip per ssid
ssid WIFI-Name
static ip_address=10.2.32.50/24
static routers=10.2.32.1
static domain_name_servers=8.8.8.8
```
https://www.raspberrypi.org/forums/viewtopic.php?f=29&t=199081

## Monitor
### Measure CPU temperature
```bash
$ sudo vcgencmd measure_temp
temp=44.4'C

# use `sensors` in Ubuntu given package `lm-sensors` installed.
```

### monitor others
```bash
$ sudo vcgencmd commands
commands="vcos, ap_output_control, ap_output_post_processing, vchi_test_init, vchi_test_exit, vctest_memmap, vctest_start, vctest_stop, vctest_set, vctest_get, pm_set_policy, pm_get_status, pm_show_stats, pm_start_logging, pm_stop_logging, version, commands, set_vll_dir, set_backlight, set_logging, get_lcd_info, arbiter, cache_flush, otp_dump, test_result, codec_enabled, get_camera, get_mem, measure_clock, measure_volts, enable_clock, scaling_kernel, scaling_sharpness, get_hvs_asserts, get_throttled, measure_temp, get_config, hdmi_ntsc_freqs, hdmi_adjust_clock, hdmi_status_show, hvs_update_fields, pwm_speedup, force_audio, hdmi_stream_channels, hdmi_channel_map, display_power, read_ring_osc, memtest, dispmanx_list, get_rsts, schmoo, render_bar, disk_notify, inuse_notify, sus_suspend, sus_status, sus_is_enabled, sus_stop_test_thread, egl_platform_switch, mem_validate, mem_oom, mem_reloc_stats, hdmi_cvt, hdmi_timings, readmr, pmicrd, pmicwr, bootloader_version, bootloader_config, file"
```

### contrl LED

config in `/boot/config.txt`
```ini
# Disable the PWR LED
dtparam=pwr_led_trigger=none
dtparam=pwr_led_activelow=off
# Disable the Activity LED
dtparam=act_led_trigger=none
dtparam=act_led_activelow=off
# Disable ethernet port LEDs
dtparam=eth_led0=4
dtparam=eth_led1=4
```

or set in bash
```bash
# echo 0 > /sys/class/leds/led1/brightness
```


## Desktop
### set 2560*1440 (2K) resolution display
2K resolution is not supported by default, we should modify the `/boot/config.txt`

```diff
 # uncomment if hdmi display is not detected and composite is being output
-#hdmi_force_hotplug=1
+hdmi_force_hotplug=1

 # uncomment to force a specific HDMI mode (this will force VGA)
-#hdmi_group=1
-#hdmi_mode=1
+hdmi_group=2
+hdmi_mode=87
+hdmi_cvt=2560 1440 60 3

 # uncomment to force a HDMI mode rather than DVI. This can make audio work in
 # DMT (computer monitor) modes
-#hdmi_drive=2
+hdmi_drive=2

 # uncomment to increase signal to HDMI, if you have interference, blanking, or
 # no display
```

### terminal
```bash
sudo apt install guake
    ```
