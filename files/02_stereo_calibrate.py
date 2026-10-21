#!/usr/bin/env python3
"""
STAGE 2 - Kalibrasi stereo
HBVCAM-W2280U3-2 V22 (OV9732 Binocular USB3.0)

Membaca pasangan gambar dari folder (hasil 01_capture_calib_images.py),
mendeteksi checkerboard, kalibrasi intrinsik tiap kamera, lalu
stereoCalibrate + stereoRectify. Hasil disimpan ke stereo_calib.npz
untuk dipakai di 03_depth_live.py.

Cara pakai:
    python 02_stereo_calibrate.py --calib-dir ./calib_images --square-size 25.0

--square-size : ukuran SATU KOTAK checkerboard dalam mm (PENTING, ukur
                 pakai penggaris/jangka sorong dari papan fisik kamu,
                 jangan asal tebak, karena ini yang nentukan skala depth
                 nantinya akurat atau ngawur)

Baseline (jarak antar lensa) HASIL HITUNGAN dibandingkan ke spek
datasheet 60.00mm sebagai sanity check.
"""

import argparse
import glob
import os

import cv2
import numpy as np


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--calib-dir", type=str, default="./calib_images")
    p.add_argument("--cols", type=int, default=9)
    p.add_argument("--rows", type=int, default=6)
    p.add_argument("--square-size", type=float, default=25.0, help="ukuran kotak checkerboard dalam mm")
    p.add_argument("--output", type=str, default="./stereo_calib.npz")
    p.add_argument("--expected-baseline", type=float, default=60.0, help="baseline dari datasheet (mm)")
    args = p.parse_args()

    board_size = (args.cols, args.rows)

    # Siapkan koordinat 3D object points (checkerboard di Z=0, satuan mm)
    objp = np.zeros((args.rows * args.cols, 3), np.float32)
    objp[:, :2] = np.mgrid[0:args.cols, 0:args.rows].T.reshape(-1, 2)
    objp *= args.square_size

    left_files = sorted(glob.glob(os.path.join(args.calib_dir, "left_*.png")))
    right_files = sorted(glob.glob(os.path.join(args.calib_dir, "right_*.png")))

    if len(left_files) == 0 or len(left_files) != len(right_files):
        raise RuntimeError(
            f"Jumlah gambar left ({len(left_files)}) dan right ({len(right_files)}) "
            "tidak sama atau kosong. Cek folder calib-dir."
        )

    print(f"Ditemukan {len(left_files)} pasangan gambar.")

    flags_find = cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
    criteria_sub = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    objpoints, imgpoints_l, imgpoints_r = [], [], []
    img_size = None

    for lf, rf in zip(left_files, right_files):
        img_l = cv2.imread(lf)
        img_r = cv2.imread(rf)
        gray_l = cv2.cvtColor(img_l, cv2.COLOR_BGR2GRAY)
        gray_r = cv2.cvtColor(img_r, cv2.COLOR_BGR2GRAY)
        if img_size is None:
            img_size = (gray_l.shape[1], gray_l.shape[0])

        ok_l, corners_l = cv2.findChessboardCorners(gray_l, board_size, flags=flags_find)
        ok_r, corners_r = cv2.findChessboardCorners(gray_r, board_size, flags=flags_find)

        if not (ok_l and ok_r):
            print(f"  Skip (corner tidak ketemu): {os.path.basename(lf)}")
            continue

        corners_l = cv2.cornerSubPix(gray_l, corners_l, (11, 11), (-1, -1), criteria_sub)
        corners_r = cv2.cornerSubPix(gray_r, corners_r, (11, 11), (-1, -1), criteria_sub)

        objpoints.append(objp)
        imgpoints_l.append(corners_l)
        imgpoints_r.append(corners_r)

    n_valid = len(objpoints)
    print(f"Pasangan valid untuk kalibrasi: {n_valid}")
    if n_valid < 8:
        print("PERINGATAN: jumlah pasangan valid terlalu sedikit (<8). "
              "Hasil kalibrasi kemungkinan kurang akurat. Sebaiknya capture lebih banyak.")

    # --- Kalibrasi tiap kamera secara individual dulu ---
    print("\nKalibrasi kamera kiri...")
    rms_l, mtx_l, dist_l, _, _ = cv2.calibrateCamera(objpoints, imgpoints_l, img_size, None, None)
    print(f"  RMS reprojection error: {rms_l:.4f} px")

    print("Kalibrasi kamera kanan...")
    rms_r, mtx_r, dist_r, _, _ = cv2.calibrateCamera(objpoints, imgpoints_r, img_size, None, None)
    print(f"  RMS reprojection error: {rms_r:.4f} px")

    # --- Stereo calibrate (cari R, T antar kedua kamera) ---
    print("\nStereo calibrate...")
    flags_stereo = cv2.CALIB_FIX_INTRINSIC
    criteria_stereo = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-5)

    rms_stereo, mtx_l, dist_l, mtx_r, dist_r, R, T, E, F = cv2.stereoCalibrate(
        objpoints, imgpoints_l, imgpoints_r,
        mtx_l, dist_l, mtx_r, dist_r,
        img_size, criteria=criteria_stereo, flags=flags_stereo,
    )
    print(f"  RMS stereo reprojection error: {rms_stereo:.4f} px")

    baseline_mm = float(np.linalg.norm(T))
    print(f"\nBaseline hasil kalibrasi : {baseline_mm:.2f} mm")
    print(f"Baseline spek datasheet  : {args.expected_baseline:.2f} mm")
    diff_pct = abs(baseline_mm - args.expected_baseline) / args.expected_baseline * 100
    print(f"Selisih                 : {diff_pct:.1f}%")
    if diff_pct > 15:
        print("  -> Selisih cukup besar. Kemungkinan --square-size salah ukur, "
              "atau jumlah/kualitas pasangan gambar kurang. Cek lagi.")
    else:
        print("  -> Cukup masuk akal, lanjut ke rectify.")

    # --- Stereo rectify ---
    R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(
        mtx_l, dist_l, mtx_r, dist_r, img_size, R, T,
        flags=cv2.CALIB_ZERO_DISPARITY, alpha=0,
    )

    map_l1, map_l2 = cv2.initUndistortRectifyMap(mtx_l, dist_l, R1, P1, img_size, cv2.CV_16SC2)
    map_r1, map_r2 = cv2.initUndistortRectifyMap(mtx_r, dist_r, R2, P2, img_size, cv2.CV_16SC2)

    np.savez(
        args.output,
        mtx_l=mtx_l, dist_l=dist_l, mtx_r=mtx_r, dist_r=dist_r,
        R=R, T=T, E=E, F=F, R1=R1, R2=R2, P1=P1, P2=P2, Q=Q,
        map_l1=map_l1, map_l2=map_l2, map_r1=map_r1, map_r2=map_r2,
        img_size=np.array(img_size), baseline_mm=baseline_mm,
        roi1=np.array(roi1), roi2=np.array(roi2),
    )
    print(f"\nKalibrasi disimpan ke: {args.output}")
    print("Lanjut ke: python 03_depth_live.py")


if __name__ == "__main__":
    main()
