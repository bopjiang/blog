---
title: "Raspberry Pi Tips"
date: 2020-06-13T11:36:41+08:00
draft: true
categories:
  - tech
---


## Other
### Measure CPU temperature

```bash
$ sudo vcgencmd measure_temp
temp=44.4'C
```

## Desktop
### set 2560*1440 (2K) resolution display

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
