# Experiment 2026-05-15-hard-window-risk-weight-2000-rejected

## Summary

- total_net_income_all_drivers: 182043.47
- total_preference_penalty: 81570.0
- failed_driver_count: 0
- total_token_usage.total_tokens: 0
- simulate_time_seconds: 236.55
- simulation_duration_days: 30
- completed_steps: 1801

## Drivers

| driver_id | gross | cost | penalty | net | calculation_aborted | rules | actions |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| D001 | 18534.1 | 4112.22 | 3000.0 | 11421.88 | False | 3 | accepted_false=3, take_order=64, wait=41 |
| D002 | 40735.43 | 11308.05 | 5200.0 | 24227.38 | False | 3 | accepted_false=1, take_order=66, wait=11 |
| D003 | 3527.8 | 1082.52 | 400.0 | 2045.28 | False | 3 | accepted_false=2, take_order=11, wait=885 |
| D004 | 44680.83 | 12275.17 | 3000.0 | 29405.65 | False | 3 | accepted_false=2, take_order=80, wait=28 |
| D005 | 41639.94 | 10475.6 | 5600.0 | 25564.34 | False | 3 | accepted_false=3, take_order=88, wait=21 |
| D006 | 35633.38 | 10281.9 | 5600.0 | 19751.48 | False | 4 | accepted_false=1, take_order=64, wait=26 |
| D007 | 47711.2 | 12817.05 | 14000.0 | 20894.15 | False | 4 | accepted_false=4, take_order=85, wait=20 |
| D008 | 47562.94 | 14157.52 | 10000.0 | 23405.41 | False | 4 | accepted_false=2, take_order=74, wait=4 |
| D009 | 45314.27 | 13421.09 | 26100.0 | 5793.18 | False | 3 | accepted_false=1, reposition=9, take_order=78, wait=56 |
| D010 | 41264.97 | 13060.24 | 8670.0 | 19534.72 | False | 4 | accepted_false=2, reposition=7, take_order=65, wait=18 |

## Delta

- total_net_income_all_drivers: -653.1
- total_preference_penalty: +0.0
- failed_driver_count: +0.0
- total_token_usage.total_tokens: +0.0
- completed_steps: +9.0
- simulate_time_seconds: +0.9

| driver_id | gross | cost | penalty | net | actions Δ |
| --- | ---: | ---: | ---: | ---: | --- |
| D007 | -812.6 | -159.5 | +0.0 | -653.1 | accepted_false=+2.0, take_order=+3.0, wait=+6.0 |
| D001 | +0.0 | +0.0 | +0.0 | +0.0 | accepted_false=+0.0, take_order=+0.0, wait=+0.0 |
| D002 | +0.0 | +0.0 | +0.0 | +0.0 | accepted_false=+0.0, take_order=+0.0, wait=+0.0 |
| D003 | +0.0 | +0.0 | +0.0 | +0.0 | accepted_false=+0.0, take_order=+0.0, wait=+0.0 |
| D004 | +0.0 | +0.0 | +0.0 | +0.0 | accepted_false=+0.0, take_order=+0.0, wait=+0.0 |
| D005 | +0.0 | +0.0 | +0.0 | +0.0 | accepted_false=+0.0, take_order=+0.0, wait=+0.0 |
| D006 | +0.0 | +0.0 | +0.0 | +0.0 | accepted_false=+0.0, take_order=+0.0, wait=+0.0 |
| D008 | +0.0 | +0.0 | +0.0 | +0.0 | accepted_false=+0.0, take_order=+0.0, wait=+0.0 |
| D009 | +0.0 | +0.0 | +0.0 | +0.0 | accepted_false=+0.0, reposition=+0.0, take_order=+0.0, wait=+0.0 |
| D010 | +0.0 | +0.0 | +0.0 | +0.0 | accepted_false=+0.0, reposition=+0.0, take_order=+0.0, wait=+0.0 |

## Timeline D005

- Source action file: actions_202603_D005_20260515_112016.jsonl

| step | minute | wall_time | action | elapsed | before | after | details |
| ---: | ---: | --- | --- | --- | --- | --- | --- |
| 1 | 360 | 2026-03-01 06:00 | wait | 360 | (22.58,113.08) | (22.58,113.08) | duration=360 |
| 2 | 893 | 2026-03-01 14:53 | take_order | 533 | (22.58,113.08) | (22.49,113.98) | cargo=32, accepted=True, deadhead=48.29, haul=98.05 |
| 3 | 1327 | 2026-03-01 22:07 | take_order | 434 | (22.49,113.98) | (23.21,113.65) | cargo=221304, accepted=True, deadhead=23.91, haul=86.88 |
| 4 | 1936 | 2026-03-02 08:16 | take_order | 609 | (23.21,113.65) | (22.61,112.97) | cargo=226276, accepted=True, deadhead=9.89, haul=94.86 |
| 5 | 2399 | 2026-03-02 15:59 | take_order | 463 | (22.61,112.97) | (22.96,113.85) | cargo=226813, accepted=True, deadhead=32.19, haul=79.23 |
| 6 | 2410 | 2026-03-02 16:10 | take_order | 11 | (22.96,113.85) | (22.96,113.85) | cargo=232633, accepted=False |
| 7 | 2768 | 2026-03-02 22:08 | take_order | 358 | (22.96,113.85) | (23.13,113.22) | cargo=3440, accepted=True, deadhead=11.16, haul=76.07 |
| 8 | 3255 | 2026-03-03 06:15 | take_order | 487 | (23.13,113.22) | (22.98,114.04) | cargo=315314, accepted=True, deadhead=3.02, haul=84.0 |
| 9 | 3716 | 2026-03-03 13:56 | take_order | 461 | (22.98,114.04) | (22.85,113.61) | cargo=313703, accepted=True, deadhead=11.12, haul=44.18 |
| 10 | 4114 | 2026-03-03 20:34 | take_order | 398 | (22.85,113.61) | (22.17,113.4) | cargo=317757, accepted=True, deadhead=12.71, haul=70.21 |
| 11 | 4628 | 2026-03-04 05:08 | take_order | 514 | (22.17,113.4) | (22.73,114.08) | cargo=320365, accepted=True, deadhead=39.14, haul=69.71 |
| 12 | 4680 | 2026-03-04 06:00 | wait | 52 | (22.73,114.08) | (22.73,114.08) | duration=52 |
| 13 | 5222 | 2026-03-04 15:02 | take_order | 542 | (22.73,114.08) | (22.65,113.31) | cargo=320679, accepted=True, deadhead=5.65, haul=79.28 |
| 14 | 5233 | 2026-03-04 15:13 | take_order | 11 | (22.65,113.31) | (22.65,113.31) | cargo=249564, accepted=False |
| 15 | 5513 | 2026-03-04 19:53 | take_order | 280 | (22.65,113.31) | (23.02,113.15) | cargo=13533, accepted=True, deadhead=6.05, haul=42.03 |
| 16 | 5890 | 2026-03-05 02:10 | take_order | 377 | (23.02,113.15) | (23.52,113.44) | cargo=325854, accepted=True, deadhead=10.56, haul=53.42 |
| 17 | 6120 | 2026-03-05 06:00 | wait | 230 | (23.52,113.44) | (23.52,113.44) | duration=230 |
| 18 | 6633 | 2026-03-05 14:33 | take_order | 513 | (23.52,113.44) | (22.67,112.98) | cargo=17721, accepted=True, deadhead=17.91, haul=88.96 |
| 19 | 6930 | 2026-03-05 19:30 | take_order | 297 | (22.67,112.98) | (23.13,112.65) | cargo=257345, accepted=True, deadhead=17.47, haul=58.81 |
| 20 | 7458 | 2026-03-06 04:18 | take_order | 528 | (23.13,112.65) | (22.8,113.28) | cargo=22675, accepted=True, deadhead=14.87, haul=67.08 |
| 21 | 7560 | 2026-03-06 06:00 | wait | 102 | (22.8,113.28) | (22.8,113.28) | duration=102 |
| 22 | 8127 | 2026-03-06 15:27 | take_order | 567 | (22.8,113.28) | (22.65,114.23) | cargo=332431, accepted=True, deadhead=7.18, haul=91.78 |
| 23 | 8487 | 2026-03-06 21:27 | take_order | 360 | (22.65,114.23) | (23.18,114.24) | cargo=337632, accepted=True, deadhead=16.42, haul=61.45 |
| 24 | 8901 | 2026-03-07 04:21 | take_order | 414 | (23.18,114.24) | (23.03,113.89) | cargo=263098, accepted=True, deadhead=7.16, haul=46.08 |
| 25 | 9000 | 2026-03-07 06:00 | wait | 99 | (23.03,113.89) | (23.03,113.89) | duration=99 |
| 26 | 9621 | 2026-03-07 16:21 | take_order | 621 | (23.03,113.89) | (23.14,114.17) | cargo=266886, accepted=True, deadhead=7.58, haul=35.63 |
| 27 | 9863 | 2026-03-07 20:23 | take_order | 242 | (23.14,114.17) | (23.17,114.32) | cargo=344104, accepted=True, deadhead=3.26, haul=18.54 |
| 28 | 10567 | 2026-03-08 08:07 | take_order | 704 | (23.17,114.32) | (22.55,114.14) | cargo=273036, accepted=True, deadhead=19.57, haul=59.63 |
| 29 | 11164 | 2026-03-08 18:04 | take_order | 597 | (22.55,114.14) | (22.83,114.69) | cargo=39485, accepted=True, deadhead=23.53, haul=73.0 |
| 30 | 11541 | 2026-03-09 00:21 | take_order | 377 | (22.83,114.69) | (22.7,114.28) | cargo=346887, accepted=True, deadhead=33.26, haul=43.51 |
| 31 | 11880 | 2026-03-09 06:00 | wait | 339 | (22.7,114.28) | (22.7,114.28) | duration=339 |
| 32 | 12327 | 2026-03-09 13:27 | take_order | 447 | (22.7,114.28) | (22.58,113.93) | cargo=45051, accepted=True, deadhead=12.25, haul=30.88 |
| 33 | 12889 | 2026-03-09 22:49 | take_order | 562 | (22.58,113.93) | (23.17,113.89) | cargo=278861, accepted=True, deadhead=24.87, haul=74.67 |
| 34 | 13399 | 2026-03-10 07:19 | take_order | 510 | (23.17,113.89) | (23.09,113.42) | cargo=280744, accepted=True, deadhead=9.79, haul=57.54 |
| 35 | 14043 | 2026-03-10 18:03 | take_order | 644 | (23.09,113.42) | (22.65,114.15) | cargo=280052, accepted=True, deadhead=17.14, haul=74.11 |
| 36 | 14295 | 2026-03-10 22:15 | take_order | 252 | (22.65,114.15) | (22.95,114.03) | cargo=361915, accepted=True, deadhead=8.42, haul=43.66 |
| 37 | 14751 | 2026-03-11 05:51 | take_order | 456 | (22.95,114.03) | (23.01,113.04) | cargo=282552, accepted=True, deadhead=6.53, haul=95.3 |
| 38 | 14760 | 2026-03-11 06:00 | wait | 9 | (23.01,113.04) | (23.01,113.04) | duration=9 |
| 39 | 15212 | 2026-03-11 13:32 | take_order | 452 | (23.01,113.04) | (23.11,113.69) | cargo=283212, accepted=True, deadhead=8.43, haul=73.95 |
| 40 | 15506 | 2026-03-11 18:26 | take_order | 294 | (23.11,113.69) | (22.74,114.41) | cargo=368048, accepted=True, deadhead=6.78, haul=77.82 |
| 41 | 15880 | 2026-03-12 00:40 | take_order | 374 | (22.74,114.41) | (22.62,113.99) | cargo=363925, accepted=True, deadhead=4.56, haul=47.56 |
| 42 | 16200 | 2026-03-12 06:00 | wait | 320 | (22.62,113.99) | (22.62,113.99) | duration=320 |
| 43 | 16905 | 2026-03-12 17:45 | take_order | 705 | (22.62,113.99) | (23.0,113.05) | cargo=370573, accepted=True, deadhead=27.15, haul=80.3 |
| 44 | 17192 | 2026-03-12 22:32 | take_order | 287 | (23.0,113.05) | (22.93,113.63) | cargo=71567, accepted=True, deadhead=11.48, haul=48.44 |
| 45 | 17664 | 2026-03-13 06:24 | take_order | 472 | (22.93,113.63) | (23.33,114.48) | cargo=65955, accepted=True, deadhead=14.78, haul=94.82 |
| 46 | 18196 | 2026-03-13 15:16 | take_order | 532 | (23.33,114.48) | (23.32,113.52) | cargo=377497, accepted=True, deadhead=46.92, haul=59.66 |
| 47 | 18472 | 2026-03-13 19:52 | take_order | 276 | (23.32,113.52) | (22.83,113.6) | cargo=381552, accepted=True, deadhead=10.21, haul=57.51 |
| 48 | 18841 | 2026-03-14 02:01 | take_order | 369 | (22.83,113.6) | (23.38,113.24) | cargo=79046, accepted=True, deadhead=12.71, haul=84.09 |
| 49 | 19080 | 2026-03-14 06:00 | wait | 239 | (23.38,113.24) | (23.38,113.24) | duration=239 |
| 50 | 19499 | 2026-03-14 12:59 | take_order | 419 | (23.38,113.24) | (22.9,112.87) | cargo=383821, accepted=True, deadhead=7.78, haul=71.91 |
| 51 | 19856 | 2026-03-14 18:56 | take_order | 357 | (22.9,112.87) | (23.48,113.04) | cargo=82150, accepted=True, deadhead=14.72, haul=68.88 |
| 52 | 20417 | 2026-03-15 04:17 | take_order | 561 | (23.48,113.04) | (23.05,113.45) | cargo=390250, accepted=True, deadhead=22.55, haul=49.55 |
| 53 | 20520 | 2026-03-15 06:00 | wait | 103 | (23.05,113.45) | (23.05,113.45) | duration=103 |
| 54 | 20918 | 2026-03-15 12:38 | take_order | 398 | (23.05,113.45) | (22.83,114.21) | cargo=390570, accepted=True, deadhead=23.81, haul=64.0 |
| 55 | 21276 | 2026-03-15 18:36 | take_order | 358 | (22.83,114.21) | (22.58,113.98) | cargo=392118, accepted=True, deadhead=19.01, haul=51.42 |
| 56 | 21662 | 2026-03-16 01:02 | take_order | 386 | (22.58,113.98) | (22.58,113.82) | cargo=393895, accepted=True, deadhead=29.36, haul=36.05 |
| 57 | 21960 | 2026-03-16 06:00 | wait | 298 | (22.58,113.82) | (22.58,113.82) | duration=298 |
| 58 | 22357 | 2026-03-16 12:37 | take_order | 397 | (22.58,113.82) | (23.15,113.38) | cargo=95036, accepted=True, deadhead=32.82, haul=71.87 |
| 59 | 22751 | 2026-03-16 19:11 | take_order | 394 | (23.15,113.38) | (23.19,113.41) | cargo=398263, accepted=True, deadhead=15.38, haul=18.7 |
| 60 | 22964 | 2026-03-16 22:44 | take_order | 213 | (23.19,113.41) | (23.11,113.46) | cargo=402107, accepted=True, deadhead=10.21, haul=20.21 |
| 61 | 23572 | 2026-03-17 08:52 | take_order | 608 | (23.11,113.46) | (22.29,113.24) | cargo=398979, accepted=True, deadhead=5.56, haul=99.34 |
| 62 | 24236 | 2026-03-17 19:56 | take_order | 664 | (22.29,113.24) | (22.65,114.1) | cargo=403279, accepted=True, deadhead=10.82, haul=98.02 |
| 63 | 24911 | 2026-03-18 07:11 | take_order | 675 | (22.65,114.1) | (22.71,113.64) | cargo=407751, accepted=True, deadhead=14.54, haul=61.71 |
| 64 | 25452 | 2026-03-18 16:12 | take_order | 541 | (22.71,113.64) | (22.87,114.15) | cargo=406735, accepted=True, deadhead=25.01, haul=78.02 |
| 65 | 25869 | 2026-03-18 23:09 | take_order | 417 | (22.87,114.15) | (23.1,113.13) | cargo=111162, accepted=True, deadhead=14.55, haul=93.81 |
| 66 | 26280 | 2026-03-19 06:00 | wait | 411 | (23.1,113.13) | (23.1,113.13) | duration=411 |
| 67 | 26781 | 2026-03-19 14:21 | take_order | 501 | (23.1,113.13) | (22.45,113.18) | cargo=113836, accepted=True, deadhead=3.26, haul=71.19 |
| 68 | 27300 | 2026-03-19 23:00 | take_order | 519 | (22.45,113.18) | (23.3,113.29) | cargo=419166, accepted=True, deadhead=17.51, haul=95.83 |
| 69 | 27720 | 2026-03-20 06:00 | wait | 420 | (23.3,113.29) | (23.3,113.29) | duration=420 |
| 70 | 28167 | 2026-03-20 13:27 | take_order | 447 | (23.3,113.29) | (22.91,113.19) | cargo=123659, accepted=True, deadhead=3.79, haul=43.24 |
| 71 | 28465 | 2026-03-20 18:25 | take_order | 298 | (22.91,113.19) | (22.82,113.79) | cargo=426058, accepted=True, deadhead=10.24, haul=52.56 |
| 72 | 29180 | 2026-03-21 06:20 | take_order | 715 | (22.82,113.79) | (22.84,114.04) | cargo=428977, accepted=True, deadhead=15.32, haul=36.24 |
| 73 | 29684 | 2026-03-21 14:44 | take_order | 504 | (22.84,114.04) | (22.58,113.47) | cargo=129926, accepted=True, deadhead=18.66, haul=79.11 |
| 74 | 30164 | 2026-03-21 22:44 | take_order | 480 | (22.58,113.47) | (23.16,113.22) | cargo=433273, accepted=True, deadhead=23.46, haul=66.65 |
| 75 | 30695 | 2026-03-22 07:35 | take_order | 531 | (23.16,113.22) | (23.07,113.92) | cargo=138294, accepted=True, deadhead=9.41, haul=76.99 |
| 76 | 31151 | 2026-03-22 15:11 | take_order | 456 | (23.07,113.92) | (22.31,113.45) | cargo=139813, accepted=True, deadhead=4.56, haul=94.0 |
| 77 | 31478 | 2026-03-22 20:38 | take_order | 327 | (22.31,113.45) | (22.97,113.1) | cargo=142647, accepted=True, deadhead=14.59, haul=81.42 |
| 78 | 32091 | 2026-03-23 06:51 | take_order | 613 | (22.97,113.1) | (23.04,113.66) | cargo=439061, accepted=True, deadhead=5.56, haul=57.35 |
| 79 | 32575 | 2026-03-23 14:55 | take_order | 484 | (23.04,113.66) | (22.47,113.12) | cargo=146998, accepted=True, deadhead=14.72, haul=89.11 |
| 80 | 33029 | 2026-03-23 22:29 | take_order | 454 | (22.47,113.12) | (22.96,114.02) | cargo=151449, accepted=True, deadhead=16.35, haul=90.86 |
| 81 | 33749 | 2026-03-24 10:29 | take_order | 720 | (22.96,114.02) | (22.85,113.18) | cargo=446813, accepted=True, deadhead=12.73, haul=99.54 |
| 82 | 34111 | 2026-03-24 16:31 | take_order | 362 | (22.85,113.18) | (22.63,114.08) | cargo=448685, accepted=True, deadhead=3.02, haul=94.1 |
| 83 | 34466 | 2026-03-24 22:26 | take_order | 355 | (22.63,114.08) | (22.86,113.37) | cargo=160450, accepted=True, deadhead=22.24, haul=72.83 |
| 84 | 35147 | 2026-03-25 09:47 | take_order | 681 | (22.86,113.37) | (22.75,114.16) | cargo=453500, accepted=True, deadhead=1.51, haul=82.76 |
| 85 | 35759 | 2026-03-25 19:59 | take_order | 612 | (22.75,114.16) | (23.11,113.3) | cargo=291402, accepted=True, deadhead=17.91, haul=92.77 |
| 86 | 36165 | 2026-03-26 02:45 | take_order | 406 | (23.11,113.3) | (22.57,113.49) | cargo=454520, accepted=True, deadhead=13.59, haul=75.7 |
| 87 | 36360 | 2026-03-26 06:00 | wait | 195 | (22.57,113.49) | (22.57,113.49) | duration=195 |
| 88 | 36895 | 2026-03-26 14:55 | take_order | 535 | (22.57,113.49) | (23.4,113.13) | cargo=167678, accepted=True, deadhead=14.46, haul=86.11 |
| 89 | 37373 | 2026-03-26 22:53 | take_order | 478 | (23.4,113.13) | (23.32,113.44) | cargo=296690, accepted=True, deadhead=13.22, haul=38.87 |
| 90 | 37708 | 2026-03-27 04:28 | take_order | 335 | (23.32,113.44) | (23.12,113.05) | cargo=175126, accepted=True, deadhead=6.04, haul=39.95 |
| 91 | 37800 | 2026-03-27 06:00 | wait | 92 | (23.12,113.05) | (23.12,113.05) | duration=92 |
| 92 | 38338 | 2026-03-27 14:58 | take_order | 538 | (23.12,113.05) | (22.67,113.69) | cargo=176510, accepted=True, deadhead=7.24, haul=87.66 |
| 93 | 38673 | 2026-03-27 20:33 | take_order | 335 | (22.67,113.69) | (22.59,114.22) | cargo=181351, accepted=True, deadhead=15.6, haul=60.56 |
| 94 | 38702 | 2026-03-27 21:02 | take_order | 29 | (22.59,114.22) | (22.68,114.37) | cargo=185571, accepted=False, deadhead=18.36, haul=0 |
| 95 | 39167 | 2026-03-28 04:47 | take_order | 465 | (22.68,114.37) | (22.88,113.73) | cargo=185565, accepted=True, deadhead=11.24, haul=71.77 |
| 96 | 39240 | 2026-03-28 06:00 | wait | 73 | (22.88,113.73) | (22.88,113.73) | duration=73 |
| 97 | 39617 | 2026-03-28 12:17 | take_order | 377 | (22.88,113.73) | (22.58,113.79) | cargo=470607, accepted=True, deadhead=9.41, haul=26.15 |
| 98 | 40207 | 2026-03-28 22:07 | take_order | 590 | (22.58,113.79) | (23.11,113.67) | cargo=303449, accepted=True, deadhead=27.03, haul=49.37 |
| 99 | 40753 | 2026-03-29 07:13 | take_order | 546 | (23.11,113.67) | (22.82,114.44) | cargo=191613, accepted=True, deadhead=11.24, haul=86.88 |
| 100 | 41270 | 2026-03-29 15:50 | take_order | 517 | (22.82,114.44) | (23.51,114.42) | cargo=479716, accepted=True, deadhead=27.22, haul=63.11 |
| 101 | 41620 | 2026-03-29 21:40 | take_order | 350 | (23.51,114.42) | (22.76,114.11) | cargo=482840, accepted=True, deadhead=39.25, haul=51.84 |
| 102 | 41971 | 2026-03-30 03:31 | take_order | 351 | (22.76,114.11) | (22.58,113.96) | cargo=203453, accepted=True, deadhead=15.96, haul=32.65 |
| 103 | 42120 | 2026-03-30 06:00 | wait | 149 | (22.58,113.96) | (22.58,113.96) | duration=149 |
| 104 | 42654 | 2026-03-30 14:54 | take_order | 534 | (22.58,113.96) | (22.26,113.47) | cargo=483897, accepted=True, deadhead=21.89, haul=83.3 |
| 105 | 43059 | 2026-03-30 21:39 | take_order | 405 | (22.26,113.47) | (22.58,113.18) | cargo=208699, accepted=True, deadhead=35.7, haul=13.1 |
| 106 | 43099 | 2026-03-30 22:19 | wait | 40 | (22.58,113.18) | (22.58,113.18) | duration=30 |
| 107 | 43139 | 2026-03-30 22:59 | wait | 40 | (22.58,113.18) | (22.58,113.18) | duration=30 |
| 108 | 43179 | 2026-03-30 23:39 | wait | 40 | (22.58,113.18) | (22.58,113.18) | duration=30 |
| 109 | 43560 | 2026-03-31 06:00 | wait | 381 | (22.58,113.18) | (22.58,113.18) | duration=381 |

## Timeline D007

- Source action file: actions_202603_D007_20260515_112016.jsonl

| step | minute | wall_time | action | elapsed | before | after | details |
| ---: | ---: | --- | --- | --- | --- | --- | --- |
| 1 | 240 | 2026-03-01 04:00 | wait | 240 | (23.05,112.46) | (23.05,112.46) | duration=240 |
| 2 | 1440 | 2026-03-02 00:00 | wait | 1200 | (23.05,112.46) | (23.05,112.46) | duration=1200 |
| 3 | 1680 | 2026-03-02 04:00 | wait | 240 | (23.05,112.46) | (23.05,112.46) | duration=240 |
| 4 | 2215 | 2026-03-02 12:55 | take_order | 535 | (23.05,112.46) | (22.97,113.22) | cargo=225915, accepted=True, deadhead=31.06, haul=99.39 |
| 5 | 2748 | 2026-03-02 21:48 | take_order | 533 | (22.97,113.22) | (22.7,114.33) | cargo=312749, accepted=True, deadhead=8.41, haul=124.39 |
| 6 | 3437 | 2026-03-03 09:17 | take_order | 689 | (22.7,114.33) | (23.09,113.8) | cargo=234787, accepted=True, deadhead=18.86, haul=50.64 |
| 7 | 3869 | 2026-03-03 16:29 | take_order | 432 | (23.09,113.8) | (23.19,112.9) | cargo=315882, accepted=True, deadhead=14.32, haul=78.5 |
| 8 | 4233 | 2026-03-03 22:33 | take_order | 364 | (23.19,112.9) | (23.39,112.83) | cargo=242561, accepted=True, deadhead=8.4, haul=19.81 |
| 9 | 4753 | 2026-03-04 07:13 | take_order | 520 | (23.39,112.83) | (23.07,113.84) | cargo=10478, accepted=True, deadhead=26.13, haul=94.74 |
| 10 | 5238 | 2026-03-04 15:18 | take_order | 485 | (23.07,113.84) | (22.15,113.14) | cargo=320288, accepted=True, deadhead=13.97, haul=124.17 |
| 11 | 5618 | 2026-03-04 21:38 | take_order | 380 | (22.15,113.14) | (22.88,113.8) | cargo=250310, accepted=True, deadhead=12.62, haul=113.65 |
| 12 | 6092 | 2026-03-05 05:32 | take_order | 474 | (22.88,113.8) | (23.49,113.21) | cargo=251237, accepted=True, deadhead=7.17, haul=86.17 |
| 13 | 6517 | 2026-03-05 12:37 | take_order | 425 | (23.49,113.21) | (22.37,113.28) | cargo=325405, accepted=True, deadhead=11.62, haul=120.25 |
| 14 | 7118 | 2026-03-05 22:38 | take_order | 601 | (22.37,113.28) | (23.09,114.68) | cargo=20369, accepted=True, deadhead=21.04, haul=147.54 |
| 15 | 7571 | 2026-03-06 06:11 | take_order | 453 | (23.09,114.68) | (24.2,115.08) | cargo=329885, accepted=True, deadhead=6.67, haul=123.66 |
| 16 | 8224 | 2026-03-06 17:04 | take_order | 653 | (24.2,115.08) | (23.04,113.17) | cargo=22897, accepted=True, deadhead=120.08, haul=165.97 |
| 17 | 8565 | 2026-03-06 22:45 | take_order | 341 | (23.04,113.17) | (23.21,112.81) | cargo=338772, accepted=True, deadhead=11.42, haul=40.65 |
| 18 | 9051 | 2026-03-07 06:51 | take_order | 486 | (23.21,112.81) | (22.6,113.78) | cargo=265605, accepted=True, deadhead=21.36, haul=99.3 |
| 19 | 9525 | 2026-03-07 14:45 | take_order | 474 | (22.6,113.78) | (22.23,112.83) | cargo=266319, accepted=True, deadhead=24.08, haul=124.21 |
| 20 | 10008 | 2026-03-07 22:48 | take_order | 483 | (22.23,112.83) | (22.58,114.03) | cargo=33909, accepted=True, deadhead=11.76, haul=120.67 |
| 21 | 10519 | 2026-03-08 07:19 | take_order | 511 | (22.58,114.03) | (23.06,114.68) | cargo=272937, accepted=True, deadhead=21.0, haul=65.57 |
| 22 | 11232 | 2026-03-08 19:12 | take_order | 713 | (23.06,114.68) | (22.77,113.7) | cargo=345373, accepted=True, deadhead=46.96, haul=112.6 |
| 23 | 11637 | 2026-03-09 01:57 | take_order | 405 | (22.77,113.7) | (22.83,113.37) | cargo=349046, accepted=True, deadhead=16.01, haul=50.45 |
| 24 | 11760 | 2026-03-09 04:00 | wait | 123 | (22.83,113.37) | (22.83,113.37) | duration=123 |
| 25 | 12441 | 2026-03-09 15:21 | take_order | 681 | (22.83,113.37) | (22.73,114.16) | cargo=276483, accepted=True, deadhead=5.93, haul=84.69 |
| 26 | 12848 | 2026-03-09 22:08 | take_order | 407 | (22.73,114.16) | (22.78,113.77) | cargo=354096, accepted=True, deadhead=11.39, haul=49.22 |
| 27 | 13145 | 2026-03-10 03:05 | take_order | 297 | (22.78,113.77) | (22.6,114.17) | cargo=277746, accepted=True, deadhead=17.49, haul=40.15 |
| 28 | 13200 | 2026-03-10 04:00 | wait | 55 | (22.6,114.17) | (22.6,114.17) | duration=55 |
| 29 | 13915 | 2026-03-10 15:55 | take_order | 715 | (22.6,114.17) | (23.11,113.15) | cargo=280823, accepted=True, deadhead=13.1, haul=105.99 |
| 30 | 14254 | 2026-03-10 21:34 | take_order | 339 | (23.11,113.15) | (22.75,113.6) | cargo=359928, accepted=True, deadhead=4.9, haul=62.58 |
| 31 | 14768 | 2026-03-11 06:08 | take_order | 514 | (22.75,113.6) | (22.63,114.18) | cargo=364290, accepted=True, deadhead=21.35, haul=78.75 |
| 32 | 15415 | 2026-03-11 16:55 | take_order | 647 | (22.63,114.18) | (22.49,112.76) | cargo=282946, accepted=True, deadhead=9.32, haul=142.57 |
| 33 | 15767 | 2026-03-11 22:47 | take_order | 352 | (22.49,112.76) | (23.17,112.89) | cargo=369846, accepted=True, deadhead=18.88, haul=63.39 |
| 34 | 16447 | 2026-03-12 10:07 | take_order | 680 | (23.17,112.89) | (24.24,113.43) | cargo=284634, accepted=True, deadhead=7.78, haul=138.18 |
| 35 | 17059 | 2026-03-12 20:19 | take_order | 612 | (24.24,113.43) | (22.56,114.01) | cargo=65695, accepted=True, deadhead=32.78, haul=174.88 |
| 36 | 17283 | 2026-03-13 00:03 | take_order | 224 | (22.56,114.01) | (22.58,114.22) | cargo=286270, accepted=True, deadhead=8.29, haul=29.8 |
| 37 | 17520 | 2026-03-13 04:00 | wait | 237 | (22.58,114.22) | (22.58,114.22) | duration=237 |
| 38 | 18150 | 2026-03-13 14:30 | take_order | 630 | (22.58,114.22) | (22.77,113.93) | cargo=72880, accepted=True, deadhead=24.49, haul=40.0 |
| 39 | 18487 | 2026-03-13 20:07 | take_order | 337 | (22.77,113.93) | (23.14,112.97) | cargo=77492, accepted=True, deadhead=6.91, haul=105.16 |
| 40 | 19018 | 2026-03-14 04:58 | take_order | 531 | (23.14,112.97) | (22.36,112.89) | cargo=286786, accepted=True, deadhead=14.88, haul=80.22 |
| 41 | 19717 | 2026-03-14 16:37 | take_order | 699 | (22.36,112.89) | (23.25,113.53) | cargo=384584, accepted=True, deadhead=17.82, haul=104.99 |
| 42 | 19728 | 2026-03-14 16:48 | take_order | 11 | (23.25,113.53) | (23.25,113.53) | cargo=389838, accepted=False |
| 43 | 19953 | 2026-03-14 20:33 | take_order | 225 | (23.25,113.53) | (23.35,113.41) | cargo=388146, accepted=True, deadhead=12.4, haul=27.38 |
| 44 | 20556 | 2026-03-15 06:36 | take_order | 603 | (23.35,113.41) | (22.69,114.1) | cargo=87930, accepted=True, deadhead=17.82, haul=115.93 |
| 45 | 20914 | 2026-03-15 12:34 | take_order | 358 | (22.69,114.1) | (22.49,113.63) | cargo=86284, accepted=True, deadhead=18.15, haul=70.23 |
| 46 | 21327 | 2026-03-15 19:27 | take_order | 413 | (22.49,113.63) | (22.54,113.83) | cargo=86869, accepted=True, deadhead=24.38, haul=38.33 |
| 47 | 21954 | 2026-03-16 05:54 | take_order | 627 | (22.54,113.83) | (23.15,113.38) | cargo=95036, accepted=True, deadhead=36.18, haul=71.87 |
| 48 | 22465 | 2026-03-16 14:25 | take_order | 511 | (23.15,113.38) | (22.47,113.48) | cargo=96322, accepted=True, deadhead=14.99, haul=80.17 |
| 49 | 22891 | 2026-03-16 21:31 | take_order | 426 | (22.47,113.48) | (22.56,113.96) | cargo=399463, accepted=True, deadhead=29.15, haul=68.04 |
| 50 | 23593 | 2026-03-17 09:13 | take_order | 702 | (22.56,113.96) | (22.52,114.12) | cargo=402258, accepted=True, deadhead=26.08, haul=32.07 |
| 51 | 24061 | 2026-03-17 17:01 | take_order | 468 | (22.52,114.12) | (22.95,113.17) | cargo=403447, accepted=True, deadhead=23.37, haul=93.74 |
| 52 | 24385 | 2026-03-17 22:25 | take_order | 324 | (22.95,113.17) | (23.09,113.34) | cargo=107953, accepted=True, deadhead=16.8, haul=15.38 |
| 53 | 24851 | 2026-03-18 06:11 | take_order | 466 | (23.09,113.34) | (23.04,113.91) | cargo=404768, accepted=True, deadhead=7.85, haul=58.81 |
| 54 | 25420 | 2026-03-18 15:40 | take_order | 569 | (23.04,113.91) | (22.31,113.38) | cargo=109961, accepted=True, deadhead=3.91, haul=99.39 |
| 55 | 25863 | 2026-03-18 23:03 | take_order | 443 | (22.31,113.38) | (23.02,113.25) | cargo=110233, accepted=True, deadhead=36.75, haul=43.73 |
| 56 | 26160 | 2026-03-19 04:00 | wait | 297 | (23.02,113.25) | (23.02,113.25) | duration=297 |
| 57 | 26767 | 2026-03-19 14:07 | take_order | 607 | (23.02,113.25) | (22.45,113.18) | cargo=113836, accepted=True, deadhead=12.06, haul=71.19 |
| 58 | 27309 | 2026-03-19 23:09 | take_order | 542 | (22.45,113.18) | (23.28,112.94) | cargo=118648, accepted=True, deadhead=17.45, haul=81.23 |
| 59 | 27600 | 2026-03-20 04:00 | wait | 291 | (23.28,112.94) | (23.28,112.94) | duration=291 |
| 60 | 28068 | 2026-03-20 11:48 | take_order | 468 | (23.28,112.94) | (22.41,114.02) | cargo=122995, accepted=True, deadhead=6.52, haul=140.92 |
| 61 | 28641 | 2026-03-20 21:21 | take_order | 573 | (22.41,114.02) | (22.57,113.33) | cargo=425139, accepted=True, deadhead=19.59, haul=75.99 |
| 62 | 29000 | 2026-03-21 03:20 | take_order | 359 | (22.57,113.33) | (23.08,113.75) | cargo=129063, accepted=True, deadhead=14.78, haul=62.53 |
| 63 | 29040 | 2026-03-21 04:00 | wait | 40 | (23.08,113.75) | (23.08,113.75) | duration=40 |
| 64 | 29523 | 2026-03-21 12:03 | take_order | 483 | (23.08,113.75) | (24.31,113.67) | cargo=429035, accepted=True, deadhead=10.75, haul=131.21 |
| 65 | 30126 | 2026-03-21 22:06 | take_order | 603 | (24.31,113.67) | (23.12,114.17) | cargo=431855, accepted=True, deadhead=23.51, haul=145.36 |
| 66 | 30686 | 2026-03-22 07:26 | take_order | 560 | (23.12,114.17) | (22.51,112.78) | cargo=432381, accepted=True, deadhead=19.58, haul=143.36 |
| 67 | 31244 | 2026-03-22 16:44 | take_order | 558 | (22.51,112.78) | (23.15,113.87) | cargo=138745, accepted=True, deadhead=16.71, haul=142.96 |
| 68 | 31270 | 2026-03-22 17:10 | take_order | 26 | (23.15,113.87) | (23.02,113.82) | cargo=434858, accepted=False, deadhead=15.33, haul=0 |
| 69 | 31594 | 2026-03-22 22:34 | take_order | 324 | (23.02,113.82) | (22.86,114.02) | cargo=145561, accepted=True, deadhead=13.71, haul=22.31 |
| 70 | 32113 | 2026-03-23 07:13 | take_order | 519 | (22.86,114.02) | (23.51,113.25) | cargo=142335, accepted=True, deadhead=6.35, haul=108.54 |
| 71 | 32394 | 2026-03-23 11:54 | take_order | 281 | (23.51,113.25) | (23.2,113.22) | cargo=146414, accepted=True, deadhead=7.88, haul=31.4 |
| 72 | 32833 | 2026-03-23 19:13 | take_order | 439 | (23.2,113.22) | (22.79,113.76) | cargo=148465, accepted=True, deadhead=5.28, haul=76.93 |
| 73 | 33153 | 2026-03-24 00:33 | take_order | 320 | (22.79,113.76) | (22.79,114.37) | cargo=443626, accepted=True, deadhead=18.98, haul=76.18 |
| 74 | 33360 | 2026-03-24 04:00 | wait | 207 | (22.79,114.37) | (22.79,114.37) | duration=207 |
| 75 | 33899 | 2026-03-24 12:59 | take_order | 539 | (22.79,114.37) | (22.73,113.86) | cargo=155585, accepted=True, deadhead=11.43, haul=61.46 |
| 76 | 34281 | 2026-03-24 19:21 | take_order | 382 | (22.73,113.86) | (22.68,113.16) | cargo=449206, accepted=True, deadhead=18.05, haul=78.4 |
| 77 | 34777 | 2026-03-25 03:37 | take_order | 496 | (22.68,113.16) | (22.04,112.1) | cargo=291466, accepted=True, deadhead=16.36, haul=121.0 |
| 78 | 34800 | 2026-03-25 04:00 | wait | 23 | (22.04,112.1) | (22.04,112.1) | duration=23 |
| 79 | 35430 | 2026-03-25 14:30 | take_order | 630 | (22.04,112.1) | (22.01,111.77) | cargo=453431, accepted=True, deadhead=68.59, haul=36.14 |
| 80 | 35766 | 2026-03-25 20:06 | take_order | 336 | (22.01,111.77) | (22.49,112.48) | cargo=293310, accepted=True, deadhead=97.35, haul=44.03 |
| 81 | 36455 | 2026-03-26 07:35 | take_order | 689 | (22.49,112.48) | (23.03,113.37) | cargo=459357, accepted=True, deadhead=22.71, haul=92.72 |
| 82 | 36910 | 2026-03-26 15:10 | take_order | 455 | (23.03,113.37) | (22.72,112.97) | cargo=460751, accepted=True, deadhead=20.5, haul=69.94 |
| 83 | 37384 | 2026-03-26 23:04 | take_order | 474 | (22.72,112.97) | (23.25,113.68) | cargo=458929, accepted=True, deadhead=15.55, haul=107.2 |
| 84 | 37680 | 2026-03-27 04:00 | wait | 296 | (23.25,113.68) | (23.25,113.68) | duration=296 |
| 85 | 38079 | 2026-03-27 10:39 | take_order | 399 | (23.25,113.68) | (22.79,114.11) | cargo=466747, accepted=True, deadhead=16.73, haul=61.51 |
| 86 | 38595 | 2026-03-27 19:15 | take_order | 516 | (22.79,114.11) | (23.97,113.56) | cargo=298787, accepted=True, deadhead=12.07, haul=153.58 |
| 87 | 39160 | 2026-03-28 04:40 | take_order | 565 | (23.97,113.56) | (22.73,113.97) | cargo=301323, accepted=True, deadhead=61.38, haul=142.92 |
| 88 | 39833 | 2026-03-28 15:53 | take_order | 673 | (22.73,113.97) | (22.73,113.07) | cargo=185076, accepted=True, deadhead=9.3, haul=83.08 |
| 89 | 39848 | 2026-03-28 16:08 | take_order | 15 | (22.73,113.07) | (22.73,113.03) | cargo=190302, accepted=False, deadhead=4.1, haul=0 |
| 90 | 40246 | 2026-03-28 22:46 | take_order | 398 | (22.73,113.03) | (23.27,112.81) | cargo=191962, accepted=True, deadhead=12.94, haul=58.7 |
| 91 | 40844 | 2026-03-29 08:44 | take_order | 598 | (23.27,112.81) | (22.56,114.1) | cargo=193655, accepted=True, deadhead=10.55, haul=150.6 |
| 92 | 41361 | 2026-03-29 17:21 | take_order | 517 | (22.56,114.1) | (22.75,113.65) | cargo=194974, accepted=True, deadhead=4.67, haul=48.12 |
| 93 | 41664 | 2026-03-29 22:24 | take_order | 303 | (22.75,113.65) | (22.77,113.94) | cargo=201338, accepted=True, deadhead=16.62, haul=24.76 |
| 94 | 41944 | 2026-03-30 03:04 | take_order | 280 | (22.77,113.94) | (23.01,114.46) | cargo=201764, accepted=True, deadhead=18.82, haul=47.93 |
| 95 | 42000 | 2026-03-30 04:00 | wait | 56 | (23.01,114.46) | (23.01,114.46) | duration=56 |
| 96 | 42515 | 2026-03-30 12:35 | take_order | 515 | (23.01,114.46) | (22.95,113.22) | cargo=483896, accepted=True, deadhead=18.51, haul=124.18 |
| 97 | 42905 | 2026-03-30 19:05 | take_order | 390 | (22.95,113.22) | (23.03,113.85) | cargo=206965, accepted=True, deadhead=3.34, haul=65.65 |
| 98 | 42916 | 2026-03-30 19:16 | take_order | 11 | (23.03,113.85) | (23.03,113.85) | cargo=211021, accepted=False |
| 99 | 42956 | 2026-03-30 19:56 | wait | 40 | (23.03,113.85) | (23.03,113.85) | duration=30 |
| 100 | 42996 | 2026-03-30 20:36 | wait | 40 | (23.03,113.85) | (23.03,113.85) | duration=30 |
| 101 | 43036 | 2026-03-30 21:16 | wait | 40 | (23.03,113.85) | (23.03,113.85) | duration=30 |
| 102 | 43076 | 2026-03-30 21:56 | wait | 40 | (23.03,113.85) | (23.03,113.85) | duration=30 |
| 103 | 43116 | 2026-03-30 22:36 | wait | 40 | (23.03,113.85) | (23.03,113.85) | duration=30 |
| 104 | 43156 | 2026-03-30 23:16 | wait | 40 | (23.03,113.85) | (23.03,113.85) | duration=30 |
| 105 | 43440 | 2026-03-31 04:00 | wait | 284 | (23.03,113.85) | (23.03,113.85) | duration=284 |

## Timeline D010

- Source action file: actions_202603_D010_20260515_112016.jsonl

| step | minute | wall_time | action | elapsed | before | after | details |
| ---: | ---: | --- | --- | --- | --- | --- | --- |
| 1 | 13 | 2026-03-01 00:13 | reposition | 13 | (23.19,113.36) | (23.13,113.26) | target=(23.13,113.26) |
| 2 | 481 | 2026-03-01 08:01 | take_order | 468 | (23.13,113.26) | (22.73,113.89) | cargo=220575, accepted=True, deadhead=127.45, haul=63.36 |
| 3 | 1067 | 2026-03-01 17:47 | take_order | 586 | (22.73,113.89) | (23.09,112.5) | cargo=306569, accepted=True, deadhead=32.47, haul=133.31 |
| 4 | 1424 | 2026-03-01 23:44 | take_order | 357 | (23.09,112.5) | (23.2,113.29) | cargo=225267, accepted=True, deadhead=36.23, haul=48.15 |
| 5 | 1604 | 2026-03-02 02:44 | wait | 180 | (23.2,113.29) | (23.2,113.29) | duration=180 |
| 6 | 1613 | 2026-03-02 02:53 | reposition | 9 | (23.2,113.29) | (23.13,113.26) | target=(23.13,113.26) |
| 7 | 2016 | 2026-03-02 09:36 | take_order | 403 | (23.13,113.26) | (23.22,113.85) | cargo=222799, accepted=True, deadhead=10.56, haul=54.75 |
| 8 | 2377 | 2026-03-02 15:37 | take_order | 361 | (23.22,113.85) | (22.76,114.41) | cargo=2520, accepted=True, deadhead=8.79, haul=75.2 |
| 9 | 2972 | 2026-03-03 01:32 | take_order | 595 | (22.76,114.41) | (23.08,113.49) | cargo=4857, accepted=True, deadhead=15.34, haul=102.23 |
| 10 | 2997 | 2026-03-03 01:57 | reposition | 25 | (23.08,113.49) | (23.13,113.26) | target=(23.13,113.26) |
| 11 | 3722 | 2026-03-03 14:02 | take_order | 725 | (23.13,113.26) | (21.72,111.83) | cargo=235391, accepted=True, deadhead=8.48, haul=211.03 |
| 12 | 4428 | 2026-03-04 01:48 | take_order | 706 | (21.72,111.83) | (23.0,113.01) | cargo=318208, accepted=True, deadhead=21.19, haul=166.01 |
| 13 | 4458 | 2026-03-04 02:18 | reposition | 30 | (23.0,113.01) | (23.13,113.26) | target=(23.13,113.26) |
| 14 | 4995 | 2026-03-04 11:15 | take_order | 537 | (23.13,113.26) | (23.02,112.51) | cargo=316262, accepted=True, deadhead=12.72, haul=89.45 |
| 15 | 5673 | 2026-03-04 22:33 | take_order | 678 | (23.02,112.51) | (22.66,114.16) | cargo=323005, accepted=True, deadhead=30.78, haul=167.44 |
| 16 | 5853 | 2026-03-05 01:33 | wait | 180 | (22.66,114.16) | (22.66,114.16) | duration=180 |
| 17 | 5959 | 2026-03-05 03:19 | reposition | 106 | (22.66,114.16) | (23.13,113.26) | target=(23.13,113.26) |
| 18 | 6635 | 2026-03-05 14:35 | take_order | 676 | (23.13,113.26) | (22.13,112.86) | cargo=252973, accepted=True, deadhead=11.85, haul=106.68 |
| 19 | 7274 | 2026-03-06 01:14 | take_order | 639 | (22.13,112.86) | (22.93,113.36) | cargo=325161, accepted=True, deadhead=16.25, haul=110.63 |
| 20 | 7779 | 2026-03-06 09:39 | take_order | 505 | (22.93,113.36) | (22.16,113.32) | cargo=258379, accepted=True, deadhead=13.69, haul=97.87 |
| 21 | 8465 | 2026-03-06 21:05 | take_order | 686 | (22.16,113.32) | (22.79,114.22) | cargo=332993, accepted=True, deadhead=15.72, haul=102.63 |
| 22 | 8645 | 2026-03-07 00:05 | wait | 180 | (22.79,114.22) | (22.79,114.22) | duration=180 |
| 23 | 9219 | 2026-03-07 09:39 | take_order | 574 | (22.79,114.22) | (22.91,113.89) | cargo=337596, accepted=True, deadhead=14.69, haul=48.07 |
| 24 | 9729 | 2026-03-07 18:09 | take_order | 510 | (22.91,113.89) | (22.1,113.41) | cargo=32128, accepted=True, deadhead=3.27, haul=105.16 |
| 25 | 10409 | 2026-03-08 05:29 | take_order | 680 | (22.1,113.41) | (21.8,111.69) | cargo=272548, accepted=True, deadhead=21.35, haul=159.24 |
| 26 | 11014 | 2026-03-08 15:34 | take_order | 605 | (21.8,111.69) | (22.34,112.64) | cargo=343483, accepted=True, deadhead=27.88, haul=92.28 |
| 27 | 11630 | 2026-03-09 01:50 | take_order | 616 | (22.34,112.64) | (23.14,113.26) | cargo=37598, accepted=True, deadhead=19.67, haul=123.35 |
| 28 | 12170 | 2026-03-09 10:50 | take_order | 540 | (23.14,113.26) | (22.83,114.6) | cargo=349879, accepted=True, deadhead=12.47, haul=153.88 |
| 29 | 12702 | 2026-03-09 19:42 | take_order | 532 | (22.83,114.6) | (22.48,113.09) | cargo=349245, accepted=True, deadhead=6.98, haul=156.29 |
| 30 | 13244 | 2026-03-10 04:44 | take_order | 542 | (22.48,113.09) | (23.56,113.0) | cargo=278304, accepted=True, deadhead=23.91, haul=131.75 |
| 31 | 13959 | 2026-03-10 16:39 | take_order | 715 | (23.56,113.0) | (22.37,112.61) | cargo=53326, accepted=True, deadhead=20.59, haul=134.09 |
| 32 | 14081 | 2026-03-10 18:41 | reposition | 122 | (22.37,112.61) | (23.21,113.37) | target=(23.21,113.37) |
| 33 | 14091 | 2026-03-10 18:51 | wait | 10 | (23.21,113.37) | (23.21,113.37) | duration=10 |
| 34 | 14094 | 2026-03-10 18:54 | reposition | 3 | (23.21,113.37) | (23.19,113.36) | target=(23.19,113.36) |
| 35 | 18600 | 2026-03-13 22:00 | wait | 4506 | (23.19,113.36) | (23.19,113.36) | duration=4506 |
| 36 | 19173 | 2026-03-14 07:33 | take_order | 573 | (23.19,113.36) | (22.52,113.6) | cargo=80093, accepted=True, deadhead=8.37, haul=86.81 |
| 37 | 19201 | 2026-03-14 08:01 | take_order | 28 | (22.52,113.6) | (22.65,113.5) | cargo=79957, accepted=False, deadhead=17.73, haul=0 |
| 38 | 19772 | 2026-03-14 17:32 | take_order | 571 | (22.65,113.5) | (22.56,114.07) | cargo=384586, accepted=True, deadhead=24.73, haul=84.04 |
| 39 | 20458 | 2026-03-15 04:58 | take_order | 686 | (22.56,114.07) | (23.19,116.23) | cargo=86692, accepted=True, deadhead=12.59, haul=219.66 |
| 40 | 21169 | 2026-03-15 16:49 | take_order | 711 | (23.19,116.23) | (23.57,116.93) | cargo=388406, accepted=True, deadhead=17.45, haul=81.98 |
| 41 | 21769 | 2026-03-16 02:49 | take_order | 600 | (23.57,116.93) | (23.73,115.6) | cargo=94382, accepted=True, deadhead=39.81, haul=97.82 |
| 42 | 22455 | 2026-03-16 14:15 | take_order | 686 | (23.73,115.6) | (23.27,116.69) | cargo=395487, accepted=True, deadhead=82.51, haul=42.86 |
| 43 | 23090 | 2026-03-17 00:50 | take_order | 635 | (23.27,116.69) | (22.58,114.38) | cargo=398734, accepted=True, deadhead=46.09, haul=204.15 |
| 44 | 23723 | 2026-03-17 11:23 | take_order | 633 | (22.58,114.38) | (23.15,114.46) | cargo=402585, accepted=True, deadhead=25.42, haul=45.96 |
| 45 | 24415 | 2026-03-17 22:55 | take_order | 692 | (23.15,114.46) | (23.27,116.44) | cargo=102190, accepted=True, deadhead=12.92, haul=210.48 |
| 46 | 24595 | 2026-03-18 01:55 | wait | 180 | (23.27,116.44) | (23.27,116.44) | duration=180 |
| 47 | 25166 | 2026-03-18 11:26 | take_order | 571 | (23.27,116.44) | (23.71,116.58) | cargo=409233, accepted=True, deadhead=28.59, haul=45.13 |
| 48 | 25559 | 2026-03-18 17:59 | take_order | 393 | (23.71,116.58) | (23.18,116.62) | cargo=110745, accepted=True, deadhead=20.43, haul=39.77 |
| 49 | 26285 | 2026-03-19 06:05 | take_order | 726 | (23.18,116.62) | (22.79,114.54) | cargo=414562, accepted=True, deadhead=41.58, haul=238.91 |
| 50 | 26842 | 2026-03-19 15:22 | take_order | 557 | (22.79,114.54) | (22.51,113.08) | cargo=413964, accepted=True, deadhead=30.05, haul=168.91 |
| 51 | 27456 | 2026-03-20 01:36 | take_order | 614 | (22.51,113.08) | (23.66,113.22) | cargo=119825, accepted=True, deadhead=28.44, haul=116.19 |
| 52 | 28106 | 2026-03-20 12:26 | take_order | 650 | (23.66,113.22) | (22.48,112.71) | cargo=118789, accepted=True, deadhead=35.65, haul=132.23 |
| 53 | 28823 | 2026-03-21 00:23 | take_order | 717 | (22.48,112.71) | (23.12,113.98) | cargo=423321, accepted=True, deadhead=22.32, haul=153.85 |
| 54 | 29476 | 2026-03-21 11:16 | take_order | 653 | (23.12,113.98) | (22.79,113.63) | cargo=132036, accepted=True, deadhead=18.44, haul=39.61 |
| 55 | 29803 | 2026-03-21 16:43 | take_order | 327 | (22.79,113.63) | (22.7,114.21) | cargo=135038, accepted=True, deadhead=18.86, haul=72.92 |
| 56 | 30234 | 2026-03-21 23:54 | take_order | 431 | (22.7,114.21) | (23.44,113.42) | cargo=137294, accepted=True, deadhead=5.25, haul=112.63 |
| 57 | 30414 | 2026-03-22 02:54 | wait | 180 | (23.44,113.42) | (23.44,113.42) | duration=180 |
| 58 | 31115 | 2026-03-22 14:35 | take_order | 701 | (23.44,113.42) | (23.51,114.52) | cargo=136836, accepted=True, deadhead=12.4, haul=112.0 |
| 59 | 31840 | 2026-03-23 02:40 | take_order | 725 | (23.51,114.52) | (23.08,113.41) | cargo=436460, accepted=True, deadhead=70.13, haul=187.13 |
| 60 | 32499 | 2026-03-23 13:39 | take_order | 659 | (23.08,113.41) | (22.47,113.12) | cargo=146998, accepted=True, deadhead=19.05, haul=89.11 |
| 61 | 33011 | 2026-03-23 22:11 | take_order | 512 | (22.47,113.12) | (22.77,114.13) | cargo=290210, accepted=True, deadhead=21.69, haul=87.81 |
| 62 | 33191 | 2026-03-24 01:11 | wait | 180 | (22.77,114.13) | (22.77,114.13) | duration=180 |
| 63 | 33557 | 2026-03-24 07:17 | take_order | 366 | (22.77,114.13) | (22.87,113.8) | cargo=446674, accepted=True, deadhead=8.37, haul=37.04 |
| 64 | 34016 | 2026-03-24 14:56 | take_order | 459 | (22.87,113.8) | (22.91,114.15) | cargo=290673, accepted=True, deadhead=14.18, haul=29.71 |
| 65 | 34628 | 2026-03-25 01:08 | take_order | 612 | (22.91,114.15) | (22.51,113.11) | cargo=449897, accepted=True, deadhead=14.72, haul=103.95 |
| 66 | 35198 | 2026-03-25 10:38 | take_order | 570 | (22.51,113.11) | (22.1,113.4) | cargo=161584, accepted=True, deadhead=25.06, haul=41.46 |
| 67 | 35745 | 2026-03-25 19:45 | take_order | 547 | (22.1,113.4) | (22.8,114.35) | cargo=292150, accepted=True, deadhead=54.0, haul=137.38 |
| 68 | 36206 | 2026-03-26 03:26 | take_order | 461 | (22.8,114.35) | (22.65,113.27) | cargo=167080, accepted=True, deadhead=2.45, haul=110.7 |
| 69 | 36895 | 2026-03-26 14:55 | take_order | 689 | (22.65,113.27) | (23.4,113.13) | cargo=167678, accepted=True, deadhead=23.25, haul=86.11 |
| 70 | 37549 | 2026-03-27 01:49 | take_order | 654 | (23.4,113.13) | (22.27,113.46) | cargo=463467, accepted=True, deadhead=8.79, haul=121.56 |
| 71 | 38261 | 2026-03-27 13:41 | take_order | 712 | (22.27,113.46) | (21.92,113.25) | cargo=298312, accepted=True, deadhead=24.44, haul=68.62 |
| 72 | 38945 | 2026-03-28 01:05 | take_order | 684 | (21.92,113.25) | (22.95,114.21) | cargo=298126, accepted=True, deadhead=31.81, haul=162.69 |
| 73 | 39591 | 2026-03-28 11:51 | take_order | 646 | (22.95,114.21) | (23.03,114.54) | cargo=474410, accepted=True, deadhead=12.73, haul=46.39 |
| 74 | 40015 | 2026-03-28 18:55 | take_order | 424 | (23.03,114.54) | (23.27,113.22) | cargo=186697, accepted=True, deadhead=20.04, haul=134.01 |
| 75 | 40457 | 2026-03-29 02:17 | take_order | 442 | (23.27,113.22) | (22.74,113.89) | cargo=191751, accepted=True, deadhead=6.52, haul=96.55 |
| 76 | 41031 | 2026-03-29 11:51 | take_order | 574 | (22.74,113.89) | (24.37,114.91) | cargo=194508, accepted=True, deadhead=23.71, haul=186.8 |
| 77 | 41631 | 2026-03-29 21:51 | take_order | 600 | (24.37,114.91) | (23.49,116.56) | cargo=196038, accepted=True, deadhead=57.04, haul=167.06 |
| 78 | 41811 | 2026-03-30 00:51 | wait | 180 | (23.49,116.56) | (23.49,116.56) | duration=180 |
| 79 | 42366 | 2026-03-30 10:06 | take_order | 555 | (23.49,116.56) | (23.34,116.45) | cargo=202085, accepted=True, deadhead=17.69, haul=31.15 |
| 80 | 42377 | 2026-03-30 10:17 | take_order | 11 | (23.34,116.45) | (23.34,116.45) | cargo=485978, accepted=False |
| 81 | 42854 | 2026-03-30 18:14 | take_order | 477 | (23.34,116.45) | (23.39,116.53) | cargo=485205, accepted=True, deadhead=19.17, haul=19.59 |
| 82 | 42894 | 2026-03-30 18:54 | wait | 40 | (23.39,116.53) | (23.39,116.53) | duration=30 |
| 83 | 42934 | 2026-03-30 19:34 | wait | 40 | (23.39,116.53) | (23.39,116.53) | duration=30 |
| 84 | 42974 | 2026-03-30 20:14 | wait | 40 | (23.39,116.53) | (23.39,116.53) | duration=30 |
| 85 | 43014 | 2026-03-30 20:54 | wait | 40 | (23.39,116.53) | (23.39,116.53) | duration=30 |
| 86 | 43054 | 2026-03-30 21:34 | wait | 40 | (23.39,116.53) | (23.39,116.53) | duration=30 |
| 87 | 43084 | 2026-03-30 22:04 | wait | 30 | (23.39,116.53) | (23.39,116.53) | duration=30 |
| 88 | 43124 | 2026-03-30 22:44 | wait | 40 | (23.39,116.53) | (23.39,116.53) | duration=30 |
| 89 | 43164 | 2026-03-30 23:24 | wait | 40 | (23.39,116.53) | (23.39,116.53) | duration=30 |
| 90 | 43204 | 2026-03-31 00:04 | wait | 40 | (23.39,116.53) | (23.39,116.53) | duration=30 |

## Notes

- Source results directory: ..\results
- Generated at: 2026-05-15T11:21:11
