#!/usr/bin/env python3
"""
STAGE 3 - Live disparity & depth map
HBVCAM-W2280U3-2 V22 (OV9732 Binocular USB3.0)

Pakai hasil kalibrasi dari 02_stereo_calibrate.py (stereo_calib.npz).
Frame kiri-kanan di-rectify dulu (koreksi distorsi + sejajarkan baris),
lalu dihitung disparity (StereoSGBM), lalu dikonversi ke depth (mm)
pakai matrix Q dari stereoRectify.

Cara pakai:
    python 03_depth_live.py --calib ./stereo_calib.npz --index 0 \\
        --width 2560 --height 720

Kontrol:
    klik kiri mouse di window "Depth" = print jarak (mm) titik itu ke console
    s = simpan snapshot (left rectified, disparity, depth)
    q / ESC = keluar

Trackbar di window "Tuning" buat atur parameter SGBM secara live kalau
hasil disparity-nya kurang bagus (noisy / banyak lubang hitam).
"""

import argparse
import os
import time

import cv2
import numpy as np

depth_map_global = None


def open_camera(index, width, height, fourcc_str):
    backend = cv2.CAP_DSHOW if os.name == "nt" else cv2.CAP_V4L2
    cap = cv2.VideoCapture(index, backend)
    if not cap.isOpened():
        cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        raise RuntimeError(f"Tidak bisa membuka kamera index {index}")
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc_str))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cap


def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and depth_map_global is not None:
        z = depth_map_global[y, x]
        if np.isfinite(z) and z > 0:
            print(f"Titik ({x},{y}) -> jarak ~{z:.1f} mm ({z/10:.1f} cm)")
        else:
            print(f"Titik ({x},{y}) -> depth tidak valid (di luar disparity range)")


def nothing(_):
    pass


def main():
    global depth_map_global

    p = argparse.ArgumentParser()
    p.add_argument("--calib", type=str, default="./stereo_calib.npz")
    p.add_argument("--index", type=int, default=0)
    p.add_argument("--width", type=int, default=2560)
    p.add_argument("--height", type=int, default=720)
    p.add_argument("--fourcc", type=str, default="MJPG")
    p.add_argument("--outdir", type=str, default="./depth_snapshots")
    args = p.parse_args()

    if not os.path.exists(args.calib):
        raise FileNotFoundError(
            f"File kalibrasi '{args.calib}' tidak ditemukan. "
            "Jalankan 01_capture_calib_images.py lalu 02_stereo_calibrate.py dulu."
        )

    os.makedirs(args.outdir, exist_ok=True)
    data = np.load(args.calib)
    map_l1, map_l2 = data["map_l1"], data["map_l2"]
    map_r1, map_r2 = data["map_r1"], data["map_r2"]
    Q = data["Q"]
    baseline_mm = float(data["baseline_mm"])
    print(f"Kalibrasi dimuat. Baseline: {baseline_mm:.2f} mm")

    cap = open_camera(args.index, args.width, args.height, args.fourcc)

    cv2.namedWindow("Tuning")
    cv2.createTrackbar("numDisparities(/16)", "Tuning", 8, 32, nothing)   # x16
    cv2.createTrackbar("blockSize", "Tuning", 5, 21, nothing)             # akan dibuat ganjil >=5
    cv2.createTrackbar("uniqRatio", "Tuning", 10, 30, nothing)
    cv2.createTrackbar("speckleWinSize", "Tuning", 100, 200, nothing)
    cv2.createTrackbar("speckleRange", "Tuning", 2, 10, nothing)

    cv2.namedWindow("Depth")
    cv2.setMouseCallback("Depth", mouse_callback)

    print("Tekan 's' untuk snapshot, 'q'/ESC untuk keluar")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Gagal baca frame.")
            break

        h, w = frame.shape[:2]
        mid = w // 2
        left = frame[:, :mid]
        right = frame[:, mid:]

        rect_l = cv2.remap(left, map_l1, map_l2, cv2.INTER_LINEAR)
        rect_r = cv2.remap(right, map_r1, map_r2, cv2.INTER_LINEAR)

        gray_l = cv2.cvtColor(rect_l, cv2.COLOR_BGR2GRAY)
        gray_r = cv2.cvtColor(rect_r, cv2.COLOR_BGR2GRAY)

        num_disp = max(16, cv2.getTrackbarPos("numDisparities(/16)", "Tuning") * 16)
        block_size = cv2.getTrackbarPos("blockSize", "Tuning")
        block_size = block_size + 1 if block_size % 2 == 0 else block_size
        block_size = max(5, block_size)
        uniq_ratio = cv2.getTrackbarPos("uniqRatio", "Tuning")
        speckle_win = cv2.getTrackbarPos("speckleWinSize", "Tuning")
        speckle_range = cv2.getTrackbarPos("speckleRange", "Tuning")

        stereo = cv2.StereoSGBM_create(
            minDisparity=0,
            numDisparities=num_disp,
            blockSize=block_size,
            P1=8 * 3 * block_size ** 2,
            P2=32 * 3 * block_size ** 2,
            disp12MaxDiff=1,
            uniquenessRatio=uniq_ratio,
            speckleWindowSize=speckle_win,
            speckleRange=speckle_range,
            mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY,
        )

        disparity = stereo.compute(gray_l, gray_r).astype(np.float32) / 16.0

        points_3d = cv2.reprojectImageTo3D(disparity, Q)
        depth_map_global = points_3d[:, :, 2]
        depth_map_global[disparity <= 0] = np.nan

        disp_vis = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX)
        disp_vis = disp_vis.astype(np.uint8)
        disp_color = cv2.applyColorMap(disp_vis, cv2.COLORMAP_JET)

        valid_depth = depth_map_global[
            np.isfinite(depth_map_global) & (depth_map_global > 0) & (depth_map_global < 5000)
        ]
        if valid_depth.size > 0:
            med = np.median(valid_depth)
            cv2.putText(disp_color, f"median depth (valid): {med:.0f} mm",
                        (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow("Left Rectified", rect_l)
        cv2.imshow("Depth", disp_color)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            break
        elif key == ord("s"):
            ts = time.strftime("%Y%m%d_%H%M%S")
            cv2.imwrite(os.path.join(args.outdir, f"left_rect_{ts}.png"), rect_l)
            cv2.imwrite(os.path.join(args.outdir, f"disparity_{ts}.png"), disp_color)
            np.save(os.path.join(args.outdir, f"depth_{ts}.npy"), depth_map_global)
            print(f"Snapshot disimpan ({ts})")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
