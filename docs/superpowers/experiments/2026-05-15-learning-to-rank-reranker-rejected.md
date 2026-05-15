# Experiment 2026-05-15-learning-to-rank-reranker-rejected

## Summary

- total_net_income_all_drivers: 182563.54
- total_preference_penalty: 81170.0
- failed_driver_count: 0
- total_token_usage.total_tokens: 0
- simulate_time_seconds: 271.42
- simulation_duration_days: 30
- completed_steps: 1793

## Drivers

| driver_id | gross | cost | penalty | net | calculation_aborted | rules | actions |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| D001 | 18540.87 | 4220.05 | 3000.0 | 11320.81 | False | 3 | accepted_false=2, take_order=64, wait=42 |
| D002 | 39662.3 | 11109.82 | 5200.0 | 23352.48 | False | 3 | accepted_false=2, take_order=67, wait=13 |
| D003 | 3527.8 | 1082.52 | 400.0 | 2045.28 | False | 3 | accepted_false=2, take_order=11, wait=885 |
| D004 | 44738.45 | 12783.52 | 3000.0 | 28954.92 | False | 3 | accepted_false=2, take_order=78, wait=21 |
| D005 | 41639.94 | 10475.6 | 5600.0 | 25564.34 | False | 3 | accepted_false=3, take_order=88, wait=21 |
| D006 | 35633.38 | 10281.9 | 5600.0 | 19751.48 | False | 4 | accepted_false=1, take_order=64, wait=26 |
| D007 | 46830.21 | 13219.01 | 14000.0 | 19611.21 | False | 4 | accepted_false=8, take_order=89, wait=19 |
| D008 | 48636.07 | 14778.43 | 9600.0 | 24257.63 | False | 4 | accepted_false=4, take_order=77, wait=4 |
| D009 | 47918.6 | 13790.85 | 26100.0 | 8027.75 | False | 3 | accepted_false=2, reposition=4, take_order=78, wait=55 |
| D010 | 40527.17 | 12179.53 | 8670.0 | 19677.64 | False | 4 | accepted_false=3, reposition=7, take_order=69, wait=11 |

## Delta

- total_net_income_all_drivers: -133.1
- total_preference_penalty: -400.0
- failed_driver_count: +0.0
- total_token_usage.total_tokens: +0.0
- completed_steps: +1.0
- simulate_time_seconds: +35.8

| driver_id | gross | cost | penalty | net | actions Δ |
| --- | ---: | ---: | ---: | ---: | --- |
| D007 | -1693.6 | +242.5 | +0.0 | -1936.1 | accepted_false=+6.0, take_order=+7.0, wait=+5.0 |
| D002 | -1073.1 | -198.2 | +0.0 | -874.9 | accepted_false=+1.0, take_order=+1.0, wait=+2.0 |
| D004 | +57.6 | +508.4 | +0.0 | -450.7 | accepted_false=+0.0, take_order=-2.0, wait=-7.0 |
| D001 | +6.8 | +107.8 | +0.0 | -101.1 | accepted_false=-1.0, take_order=+0.0, wait=+1.0 |
| D003 | +0.0 | +0.0 | +0.0 | +0.0 | accepted_false=+0.0, take_order=+0.0, wait=+0.0 |
| D005 | +0.0 | +0.0 | +0.0 | +0.0 | accepted_false=+0.0, take_order=+0.0, wait=+0.0 |
| D006 | +0.0 | +0.0 | +0.0 | +0.0 | accepted_false=+0.0, take_order=+0.0, wait=+0.0 |
| D010 | -737.8 | -880.7 | +0.0 | +142.9 | accepted_false=+1.0, reposition=+0.0, take_order=+4.0, wait=-7.0 |
| D009 | +2604.3 | +369.8 | +0.0 | +2234.6 | accepted_false=+1.0, reposition=-5.0, take_order=+0.0, wait=-1.0 |
| D008 | +1073.1 | +620.9 | -400.0 | +852.2 | accepted_false=+2.0, take_order=+3.0, wait=+0.0 |

## Timeline D005

- Source action file: actions_202603_D005_20260515_184148.jsonl

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

- Source action file: actions_202603_D007_20260515_184148.jsonl

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
| 21 | 10023 | 2026-03-07 23:03 | take_order | 15 | (22.58,114.03) | (22.55,114.0) | cargo=39091, accepted=False, deadhead=4.54, haul=0 |
| 22 | 10320 | 2026-03-08 04:00 | wait | 297 | (22.55,114.0) | (22.55,114.0) | duration=297 |
| 23 | 10897 | 2026-03-08 13:37 | take_order | 577 | (22.55,114.0) | (22.08,113.13) | cargo=271709, accepted=True, deadhead=21.89, haul=124.89 |
| 24 | 11463 | 2026-03-08 23:03 | take_order | 566 | (22.08,113.13) | (23.15,113.51) | cargo=42209, accepted=True, deadhead=6.06, haul=128.27 |
| 25 | 11760 | 2026-03-09 04:00 | wait | 297 | (23.15,113.51) | (23.15,113.51) | duration=297 |
| 26 | 12406 | 2026-03-09 14:46 | take_order | 646 | (23.15,113.51) | (22.59,114.27) | cargo=348998, accepted=True, deadhead=18.05, haul=92.4 |
| 27 | 12417 | 2026-03-09 14:57 | take_order | 11 | (22.59,114.27) | (22.59,114.27) | cargo=353181, accepted=False |
| 28 | 12836 | 2026-03-09 21:56 | take_order | 419 | (22.59,114.27) | (22.65,113.38) | cargo=353887, accepted=True, deadhead=17.36, haul=79.2 |
| 29 | 13183 | 2026-03-10 03:43 | take_order | 347 | (22.65,113.38) | (22.69,113.7) | cargo=357282, accepted=True, deadhead=19.11, haul=51.75 |
| 30 | 13200 | 2026-03-10 04:00 | wait | 17 | (22.69,113.7) | (22.69,113.7) | duration=17 |
| 31 | 13894 | 2026-03-10 15:34 | take_order | 694 | (22.69,113.7) | (22.26,113.21) | cargo=280709, accepted=True, deadhead=23.55, haul=85.41 |
| 32 | 14315 | 2026-03-10 22:35 | take_order | 421 | (22.26,113.21) | (23.0,113.61) | cargo=53614, accepted=True, deadhead=19.24, haul=73.05 |
| 33 | 14944 | 2026-03-11 09:04 | take_order | 629 | (23.0,113.61) | (23.09,115.41) | cargo=282411, accepted=True, deadhead=17.71, haul=173.92 |
| 34 | 15404 | 2026-03-11 16:44 | take_order | 460 | (23.09,115.41) | (23.53,116.3) | cargo=282972, accepted=True, deadhead=51.48, haul=89.04 |
| 35 | 15428 | 2026-03-11 17:08 | take_order | 24 | (23.53,116.3) | (23.54,116.17) | cargo=369875, accepted=False, deadhead=13.3, haul=0 |
| 36 | 16084 | 2026-03-12 04:04 | take_order | 656 | (23.54,116.17) | (22.85,115.04) | cargo=368012, accepted=True, deadhead=23.45, haul=158.77 |
| 37 | 16624 | 2026-03-12 13:04 | take_order | 540 | (22.85,115.04) | (22.86,113.68) | cargo=370756, accepted=True, deadhead=28.26, haul=124.24 |
| 38 | 17124 | 2026-03-12 21:24 | take_order | 500 | (22.86,113.68) | (22.99,113.11) | cargo=67614, accepted=True, deadhead=2.22, haul=59.64 |
| 39 | 17473 | 2026-03-13 03:13 | take_order | 349 | (22.99,113.11) | (22.71,114.08) | cargo=67574, accepted=True, deadhead=8.9, haul=101.88 |
| 40 | 17520 | 2026-03-13 04:00 | wait | 47 | (22.71,114.08) | (22.71,114.08) | duration=47 |
| 41 | 17980 | 2026-03-13 11:40 | take_order | 460 | (22.71,114.08) | (23.71,112.74) | cargo=376909, accepted=True, deadhead=12.23, haul=164.24 |
| 42 | 18418 | 2026-03-13 18:58 | take_order | 438 | (23.71,112.74) | (22.92,113.17) | cargo=379446, accepted=True, deadhead=36.81, haul=84.81 |
| 43 | 19004 | 2026-03-14 04:44 | take_order | 586 | (22.92,113.17) | (22.09,113.51) | cargo=74165, accepted=True, deadhead=15.17, haul=95.86 |
| 44 | 19334 | 2026-03-14 10:14 | take_order | 330 | (22.09,113.51) | (22.81,113.75) | cargo=384261, accepted=True, deadhead=53.83, haul=67.32 |
| 45 | 19795 | 2026-03-14 17:55 | take_order | 461 | (22.81,113.75) | (22.23,113.31) | cargo=82681, accepted=True, deadhead=4.66, haul=82.96 |
| 46 | 20406 | 2026-03-15 04:06 | take_order | 611 | (22.23,113.31) | (23.12,113.72) | cargo=389222, accepted=True, deadhead=44.82, haul=77.0 |
| 47 | 20786 | 2026-03-15 10:26 | take_order | 380 | (23.12,113.72) | (22.83,114.21) | cargo=390570, accepted=True, deadhead=5.11, haul=64.0 |
| 48 | 21268 | 2026-03-15 18:28 | take_order | 482 | (22.83,114.21) | (22.99,113.05) | cargo=391084, accepted=True, deadhead=18.98, haul=102.82 |
| 49 | 21755 | 2026-03-16 02:35 | take_order | 487 | (22.99,113.05) | (22.83,114.19) | cargo=93392, accepted=True, deadhead=13.72, haul=131.77 |
| 50 | 21840 | 2026-03-16 04:00 | wait | 85 | (22.83,114.19) | (22.83,114.19) | duration=85 |
| 51 | 22225 | 2026-03-16 10:25 | take_order | 385 | (22.83,114.19) | (23.15,113.38) | cargo=95036, accepted=True, deadhead=20.5, haul=71.87 |
| 52 | 22820 | 2026-03-16 20:20 | take_order | 595 | (23.15,113.38) | (22.45,114.13) | cargo=397189, accepted=True, deadhead=13.26, haul=121.78 |
| 53 | 23233 | 2026-03-17 03:13 | take_order | 413 | (22.45,114.13) | (23.07,113.32) | cargo=400503, accepted=True, deadhead=30.53, haul=81.97 |
| 54 | 23280 | 2026-03-17 04:00 | wait | 47 | (23.07,113.32) | (23.07,113.32) | duration=47 |
| 55 | 23893 | 2026-03-17 14:13 | take_order | 613 | (23.07,113.32) | (22.54,113.87) | cargo=398669, accepted=True, deadhead=16.41, haul=92.95 |
| 56 | 24365 | 2026-03-17 22:05 | take_order | 472 | (22.54,113.87) | (23.17,113.66) | cargo=406246, accepted=True, deadhead=14.46, haul=86.8 |
| 57 | 24656 | 2026-03-18 02:56 | take_order | 291 | (23.17,113.66) | (22.98,113.75) | cargo=406308, accepted=True, deadhead=18.32, haul=21.53 |
| 58 | 24720 | 2026-03-18 04:00 | wait | 64 | (22.98,113.75) | (22.98,113.75) | duration=64 |
| 59 | 25295 | 2026-03-18 13:35 | take_order | 575 | (22.98,113.75) | (22.99,113.06) | cargo=409375, accepted=True, deadhead=18.27, haul=53.66 |
| 60 | 25322 | 2026-03-18 14:02 | take_order | 27 | (22.99,113.06) | (23.07,113.19) | cargo=112678, accepted=False, deadhead=16.0, haul=0 |
| 61 | 25744 | 2026-03-18 21:04 | take_order | 422 | (23.07,113.19) | (22.78,114.05) | cargo=412977, accepted=True, deadhead=3.02, haul=96.48 |
| 62 | 26405 | 2026-03-19 08:05 | take_order | 661 | (22.78,114.05) | (23.17,113.21) | cargo=415398, accepted=True, deadhead=15.82, haul=80.5 |
| 63 | 26913 | 2026-03-19 16:33 | take_order | 508 | (23.17,113.21) | (22.45,113.18) | cargo=113836, accepted=True, deadhead=10.26, haul=71.19 |
| 64 | 27523 | 2026-03-20 02:43 | take_order | 610 | (22.45,113.18) | (23.66,113.22) | cargo=119825, accepted=True, deadhead=24.39, haul=116.19 |
| 65 | 27600 | 2026-03-20 04:00 | wait | 77 | (23.66,113.22) | (23.66,113.22) | duration=77 |
| 66 | 28250 | 2026-03-20 14:50 | take_order | 650 | (23.66,113.22) | (22.48,112.71) | cargo=118789, accepted=True, deadhead=35.65, haul=132.23 |
| 67 | 28613 | 2026-03-20 20:53 | take_order | 363 | (22.48,112.71) | (23.14,113.12) | cargo=424414, accepted=True, deadhead=14.39, haul=87.85 |
| 68 | 28897 | 2026-03-21 01:37 | take_order | 284 | (23.14,113.12) | (23.06,113.17) | cargo=428106, accepted=True, deadhead=7.9, haul=5.92 |
| 69 | 29040 | 2026-03-21 04:00 | wait | 143 | (23.06,113.17) | (23.06,113.17) | duration=143 |
| 70 | 29619 | 2026-03-21 13:39 | take_order | 579 | (23.06,113.17) | (22.9,113.84) | cargo=428536, accepted=True, deadhead=11.42, haul=62.08 |
| 71 | 29645 | 2026-03-21 14:05 | take_order | 26 | (22.9,113.84) | (23.0,113.95) | cargo=132930, accepted=False, deadhead=15.83, haul=0 |
| 72 | 30035 | 2026-03-21 20:35 | take_order | 390 | (23.0,113.95) | (23.06,113.27) | cargo=135769, accepted=True, deadhead=11.48, haul=80.96 |
| 73 | 30046 | 2026-03-21 20:46 | take_order | 11 | (23.06,113.27) | (23.06,113.27) | cargo=435049, accepted=False |
| 74 | 30479 | 2026-03-22 03:59 | take_order | 433 | (23.06,113.27) | (23.11,113.04) | cargo=138913, accepted=True, deadhead=20.02, haul=27.6 |
| 75 | 30480 | 2026-03-22 04:00 | wait | 1 | (23.11,113.04) | (23.11,113.04) | duration=1 |
| 76 | 31144 | 2026-03-22 15:04 | take_order | 664 | (23.11,113.04) | (22.99,113.21) | cargo=434649, accepted=True, deadhead=13.6, haul=26.82 |
| 77 | 31534 | 2026-03-22 21:34 | take_order | 390 | (22.99,113.21) | (23.16,114.09) | cargo=144639, accepted=True, deadhead=13.98, haul=105.47 |
| 78 | 31845 | 2026-03-23 02:45 | take_order | 311 | (23.16,114.09) | (22.77,114.46) | cargo=439148, accepted=True, deadhead=19.21, haul=56.48 |
| 79 | 31920 | 2026-03-23 04:00 | wait | 75 | (22.77,114.46) | (22.77,114.46) | duration=75 |
| 80 | 32569 | 2026-03-23 14:49 | take_order | 649 | (22.77,114.46) | (22.78,113.72) | cargo=289837, accepted=True, deadhead=33.68, haul=108.38 |
| 81 | 32586 | 2026-03-23 15:06 | take_order | 17 | (22.78,113.72) | (22.76,113.78) | cargo=441167, accepted=False, deadhead=6.54, haul=0 |
| 82 | 32949 | 2026-03-23 21:09 | take_order | 363 | (22.76,113.78) | (22.82,113.94) | cargo=148391, accepted=True, deadhead=17.15, haul=26.77 |
| 83 | 33311 | 2026-03-24 03:11 | take_order | 362 | (22.82,113.94) | (22.55,113.87) | cargo=155060, accepted=True, deadhead=3.34, haul=27.64 |
| 84 | 33360 | 2026-03-24 04:00 | wait | 49 | (22.55,113.87) | (22.55,113.87) | duration=49 |
| 85 | 33905 | 2026-03-24 13:05 | take_order | 545 | (22.55,113.87) | (22.54,114.17) | cargo=152736, accepted=True, deadhead=16.47, haul=14.38 |
| 86 | 34474 | 2026-03-24 22:34 | take_order | 569 | (22.54,114.17) | (22.76,113.23) | cargo=158701, accepted=True, deadhead=30.02, haul=96.53 |
| 87 | 35147 | 2026-03-25 09:47 | take_order | 673 | (22.76,113.23) | (22.75,114.16) | cargo=453500, accepted=True, deadhead=16.66, haul=82.76 |
| 88 | 35759 | 2026-03-25 19:59 | take_order | 612 | (22.75,114.16) | (23.11,113.3) | cargo=291402, accepted=True, deadhead=17.91, haul=92.77 |
| 89 | 36250 | 2026-03-26 04:10 | take_order | 491 | (23.11,113.3) | (22.5,113.9) | cargo=167466, accepted=True, deadhead=15.15, haul=106.44 |
| 90 | 36827 | 2026-03-26 13:47 | take_order | 577 | (22.5,113.9) | (22.94,113.62) | cargo=294734, accepted=True, deadhead=11.25, haul=51.57 |
| 91 | 37165 | 2026-03-26 19:25 | take_order | 338 | (22.94,113.62) | (22.77,113.78) | cargo=296141, accepted=True, deadhead=14.69, haul=23.23 |
| 92 | 37318 | 2026-03-26 21:58 | take_order | 153 | (22.77,113.78) | (23.01,114.01) | cargo=175921, accepted=True, deadhead=14.32, haul=21.34 |
| 93 | 38006 | 2026-03-27 09:26 | take_order | 688 | (23.01,114.01) | (22.4,112.64) | cargo=171560, accepted=True, deadhead=2.45, haul=156.03 |
| 94 | 38552 | 2026-03-27 18:32 | take_order | 546 | (22.4,112.64) | (22.79,113.81) | cargo=465524, accepted=True, deadhead=12.27, haul=131.47 |
| 95 | 38775 | 2026-03-27 22:15 | take_order | 223 | (22.79,113.81) | (23.13,113.73) | cargo=184311, accepted=True, deadhead=11.33, haul=39.04 |
| 96 | 39239 | 2026-03-28 05:59 | take_order | 464 | (23.13,113.73) | (22.21,113.27) | cargo=184718, accepted=True, deadhead=11.64, haul=112.52 |
| 97 | 39828 | 2026-03-28 15:48 | take_order | 589 | (22.21,113.27) | (23.5,112.88) | cargo=183475, accepted=True, deadhead=34.13, haul=179.82 |
| 98 | 39839 | 2026-03-28 15:59 | take_order | 11 | (23.5,112.88) | (23.5,112.88) | cargo=304762, accepted=False |
| 99 | 40313 | 2026-03-28 23:53 | take_order | 474 | (23.5,112.88) | (22.77,113.1) | cargo=305025, accepted=True, deadhead=23.34, haul=75.3 |
| 100 | 40560 | 2026-03-29 04:00 | wait | 247 | (22.77,113.1) | (22.77,113.1) | duration=247 |
| 101 | 41267 | 2026-03-29 15:47 | take_order | 707 | (22.77,113.1) | (22.68,114.34) | cargo=478195, accepted=True, deadhead=20.54, haul=117.25 |
| 102 | 41525 | 2026-03-29 20:05 | take_order | 258 | (22.68,114.34) | (23.04,114.14) | cargo=200387, accepted=True, deadhead=6.26, haul=47.16 |
| 103 | 41973 | 2026-03-30 03:33 | take_order | 448 | (23.04,114.14) | (22.93,114.57) | cargo=202406, accepted=True, deadhead=6.75, haul=43.36 |
| 104 | 42000 | 2026-03-30 04:00 | wait | 27 | (22.93,114.57) | (22.93,114.57) | duration=27 |
| 105 | 42640 | 2026-03-30 14:40 | take_order | 640 | (22.93,114.57) | (23.38,113.2) | cargo=203930, accepted=True, deadhead=24.6, haul=172.37 |
| 106 | 43112 | 2026-03-30 22:32 | take_order | 472 | (23.38,113.2) | (22.66,114.34) | cargo=207729, accepted=True, deadhead=5.1, haul=145.74 |
| 107 | 43152 | 2026-03-30 23:12 | wait | 40 | (22.66,114.34) | (22.66,114.34) | duration=30 |
| 108 | 43440 | 2026-03-31 04:00 | wait | 288 | (22.66,114.34) | (22.66,114.34) | duration=288 |

## Timeline D010

- Source action file: actions_202603_D010_20260515_184148.jsonl

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
| 43 | 22804 | 2026-03-16 20:04 | take_order | 349 | (23.27,116.69) | (23.5,116.66) | cargo=398712, accepted=True, deadhead=40.62, haul=27.55 |
| 44 | 23405 | 2026-03-17 06:05 | take_order | 601 | (23.5,116.66) | (24.26,115.95) | cargo=402146, accepted=True, deadhead=48.19, haul=77.66 |
| 45 | 23998 | 2026-03-17 15:58 | take_order | 593 | (24.26,115.95) | (23.57,116.23) | cargo=102139, accepted=True, deadhead=48.49, haul=126.18 |
| 46 | 24249 | 2026-03-17 20:09 | take_order | 251 | (23.57,116.23) | (23.7,116.48) | cargo=407053, accepted=True, deadhead=20.02, haul=42.87 |
| 47 | 24969 | 2026-03-18 08:09 | take_order | 720 | (23.7,116.48) | (24.09,115.27) | cargo=109799, accepted=True, deadhead=21.25, haul=144.82 |
| 48 | 25649 | 2026-03-18 19:29 | take_order | 680 | (24.09,115.27) | (22.93,113.84) | cargo=406706, accepted=True, deadhead=17.4, haul=180.49 |
| 49 | 26292 | 2026-03-19 06:12 | take_order | 643 | (22.93,113.84) | (23.05,112.64) | cargo=112804, accepted=True, deadhead=10.48, haul=133.99 |
| 50 | 26796 | 2026-03-19 14:36 | take_order | 504 | (23.05,112.64) | (23.72,113.09) | cargo=111848, accepted=True, deadhead=27.99, haul=81.06 |
| 51 | 27496 | 2026-03-20 02:16 | take_order | 700 | (23.72,113.09) | (22.74,114.29) | cargo=116988, accepted=True, deadhead=9.23, haul=170.32 |
| 52 | 28178 | 2026-03-20 13:38 | take_order | 682 | (22.74,114.29) | (23.15,113.26) | cargo=422756, accepted=True, deadhead=5.25, haul=109.76 |
| 53 | 28804 | 2026-03-21 00:04 | take_order | 626 | (23.15,113.26) | (22.86,114.11) | cargo=127255, accepted=True, deadhead=9.41, haul=99.0 |
| 54 | 29523 | 2026-03-21 12:03 | take_order | 719 | (22.86,114.11) | (23.04,113.39) | cargo=429881, accepted=True, deadhead=9.79, haul=75.41 |
| 55 | 29848 | 2026-03-21 17:28 | take_order | 325 | (23.04,113.39) | (23.35,113.2) | cargo=134309, accepted=True, deadhead=9.47, haul=43.11 |
| 56 | 30223 | 2026-03-21 23:43 | take_order | 375 | (23.35,113.2) | (22.69,114.17) | cargo=432475, accepted=True, deadhead=10.74, haul=112.76 |
| 57 | 30403 | 2026-03-22 02:43 | wait | 180 | (22.69,114.17) | (22.69,114.17) | duration=180 |
| 58 | 30887 | 2026-03-22 10:47 | take_order | 484 | (22.69,114.17) | (22.58,113.91) | cargo=138106, accepted=True, deadhead=19.15, haul=39.06 |
| 59 | 31114 | 2026-03-22 14:34 | take_order | 227 | (22.58,113.91) | (22.94,113.72) | cargo=140485, accepted=True, deadhead=10.33, haul=50.76 |
| 60 | 31573 | 2026-03-22 22:13 | take_order | 459 | (22.94,113.72) | (22.72,114.13) | cargo=142531, accepted=True, deadhead=14.89, haul=63.49 |
| 61 | 31753 | 2026-03-23 01:13 | wait | 180 | (22.72,114.13) | (22.72,114.13) | duration=180 |
| 62 | 32311 | 2026-03-23 10:31 | take_order | 558 | (22.72,114.13) | (22.55,114.42) | cargo=145964, accepted=True, deadhead=13.09, haul=48.12 |
| 63 | 33007 | 2026-03-23 22:07 | take_order | 696 | (22.55,114.42) | (22.84,113.7) | cargo=290186, accepted=True, deadhead=28.94, haul=106.57 |
| 64 | 33187 | 2026-03-24 01:07 | wait | 180 | (22.84,113.7) | (22.84,113.7) | duration=180 |
| 65 | 33872 | 2026-03-24 12:32 | take_order | 685 | (22.84,113.7) | (22.88,113.46) | cargo=446937, accepted=True, deadhead=18.82, haul=22.76 |
| 66 | 34188 | 2026-03-24 17:48 | take_order | 316 | (22.88,113.46) | (23.34,113.14) | cargo=150936, accepted=True, deadhead=12.09, haul=58.8 |
| 67 | 34209 | 2026-03-24 18:09 | take_order | 21 | (23.34,113.14) | (23.26,113.2) | cargo=158756, accepted=False, deadhead=10.8, haul=0 |
| 68 | 34872 | 2026-03-25 05:12 | take_order | 663 | (23.26,113.2) | (22.58,114.93) | cargo=447380, accepted=True, deadhead=6.75, haul=189.2 |
| 69 | 35418 | 2026-03-25 14:18 | take_order | 546 | (22.58,114.93) | (22.53,113.36) | cargo=162377, accepted=True, deadhead=38.78, haul=129.59 |
| 70 | 35969 | 2026-03-25 23:29 | take_order | 551 | (22.53,113.36) | (22.92,114.01) | cargo=163475, accepted=True, deadhead=25.24, haul=96.59 |
| 71 | 36149 | 2026-03-26 02:29 | wait | 180 | (22.92,114.01) | (22.92,114.01) | duration=180 |
| 72 | 36690 | 2026-03-26 11:30 | take_order | 541 | (22.92,114.01) | (22.88,113.64) | cargo=294738, accepted=True, deadhead=7.56, haul=44.16 |
| 73 | 37204 | 2026-03-26 20:04 | take_order | 514 | (22.88,113.64) | (23.04,113.43) | cargo=461183, accepted=True, deadhead=10.58, haul=30.36 |
| 74 | 37848 | 2026-03-27 06:48 | take_order | 644 | (23.04,113.43) | (24.33,113.95) | cargo=297348, accepted=True, deadhead=14.72, haul=162.0 |
| 75 | 38403 | 2026-03-27 16:03 | take_order | 555 | (24.33,113.95) | (23.22,113.28) | cargo=467216, accepted=True, deadhead=85.61, haul=142.78 |
| 76 | 38922 | 2026-03-28 00:42 | take_order | 519 | (23.22,113.28) | (22.54,114.06) | cargo=299628, accepted=True, deadhead=9.31, haul=119.08 |
| 77 | 39627 | 2026-03-28 12:27 | take_order | 705 | (22.54,114.06) | (23.02,113.86) | cargo=474501, accepted=True, deadhead=10.26, haul=57.25 |
| 78 | 40040 | 2026-03-28 19:20 | take_order | 413 | (23.02,113.86) | (22.78,113.4) | cargo=187906, accepted=True, deadhead=11.47, haul=46.05 |
| 79 | 40588 | 2026-03-29 04:28 | take_order | 548 | (22.78,113.4) | (23.06,114.01) | cargo=189372, accepted=True, deadhead=14.56, haul=78.31 |
| 80 | 41066 | 2026-03-29 12:26 | take_order | 478 | (23.06,114.01) | (22.57,113.85) | cargo=479967, accepted=True, deadhead=6.75, haul=50.89 |
| 81 | 41107 | 2026-03-29 13:07 | take_order | 41 | (22.57,113.85) | (22.72,113.6) | cargo=481778, accepted=False, deadhead=30.6, haul=0 |
| 82 | 41586 | 2026-03-29 21:06 | take_order | 479 | (22.72,113.6) | (22.59,114.2) | cargo=482450, accepted=True, deadhead=7.35, haul=65.13 |
| 83 | 41766 | 2026-03-30 00:06 | wait | 180 | (22.59,114.2) | (22.59,114.2) | duration=180 |
| 84 | 42447 | 2026-03-30 11:27 | take_order | 681 | (22.59,114.2) | (23.02,113.36) | cargo=203833, accepted=True, deadhead=8.86, haul=89.7 |
| 85 | 42924 | 2026-03-30 19:24 | take_order | 477 | (23.02,113.36) | (22.85,113.68) | cargo=205434, accepted=True, deadhead=16.56, haul=36.34 |
| 86 | 43161 | 2026-03-30 23:21 | take_order | 237 | (22.85,113.68) | (23.06,113.99) | cargo=211873, accepted=True, deadhead=2.45, haul=37.28 |
| 87 | 43341 | 2026-03-31 02:21 | wait | 180 | (23.06,113.99) | (23.06,113.99) | duration=180 |

## Notes

- Source results directory: ..\results
- Generated at: 2026-05-15T18:42:21
