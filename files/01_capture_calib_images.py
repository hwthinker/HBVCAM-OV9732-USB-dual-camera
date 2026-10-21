#!/usr/bin/env python3
"""
STAGE 1 - Capture gambar checkerboard untuk kalibrasi stereo
HBVCAM-W2280U3-2 V22 (OV9732 Binocular USB3.0)

Cara pakai:
    python 01_capture_calib_images.py --index 0 --width 2560 --height 720

Siapkan papan checkerboard (cetak, tempel di permukaan kaku/rata).
Default di sini asumsi papan 9x6 INTERNAL CORNERS (artinya papan fisiknya
10x7 kotak). Kalau papanmu beda, ganti --cols / --rows.

Kontrol:
    c = capture pasangan gambar (kalau checkerboard terdeteksi di KEDUA mata)
    q / ESC = keluar

Tips pengambilan data (penting buat hasil kalibrasi bagus):
- Ambil minimal 15-20 pasang gambar valid (lebih banyak lebih baik)
- Gerakkan checkerboard ke berbagai posisi: kiri, kanan, atas, bawah,
  dekat, jauh, miring (tilt) ke beberapa sudut
- Pastikan checkerboard kelihatan PENUH dan TIDAK BLUR di kedua mata
- Jangan cuma capture pas checkerboard di tengah-tengah terus
"""

import argparse
import os
import time

import cv2
import numpy as np


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


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--index", type=int, default=0)
    p.add_argument("--width", type=int, default=2560)
    p.add_argument("--height", type=int, default=720)
    p.add_argument("--fourcc", type=str, default="MJPG")
    p.add_argument("--cols", type=int, default=9, help="jumlah internal corner horizontal")
    p.add_argument("--rows", type=int, default=6, help="jumlah internal corner vertikal")
    p.add_argument("--outdir", type=str, default="./calib_images")
    args = p.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    board_size = (args.cols, args.rows)

    cap = open_camera(args.index, args.width, args.height, args.fourcc)
    aw = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    ah = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Resolusi gabungan aktual: {aw}x{ah}")
    print(f"Mencari checkerboard {args.cols}x{args.rows} internal corners")
    print("Tekan 'c' untuk capture, 'q'/ESC untuk keluar\n")

    saved = 0
    flags = cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_FAST_CHECK

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Gagal baca frame.")
            break

        h, w = frame.shape[:2]
        mid = w // 2
        left = frame[:, :mid]
        right = frame[:, mid:]

        gray_l = cv2.cvtColor(left, cv2.COLOR_BGR2GRAY)
        gray_r = cv2.cvtColor(right, cv2.COLOR_BGR2GRAY)

        found_l, corners_l = cv2.findChessboardCorners(gray_l, board_size, flags=flags)
        found_r, corners_r = cv2.findChessboardCorners(gray_r, board_size, flags=flags)

        disp_l = left.copy()
        disp_r = right.copy()
        if found_l:
            cv2.drawChessboardCorners(disp_l, board_size, corners_l, found_l)
        if found_r:
            cv2.drawChessboardCorners(disp_r, board_size, corners_r, found_r)

        status = f"Saved: {saved}  |  L:{'OK' if found_l else '--'}  R:{'OK' if found_r else '--'}"
        color = (0, 255, 0) if (found_l and found_r) else (0, 0, 255)
        cv2.putText(disp_l, status, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

        cv2.imshow("Left", disp_l)
        cv2.imshow("Right", disp_r)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            break
        elif key == ord("c"):
            if found_l and found_r:
                ts = time.strftime("%Y%m%d_%H%M%S")
                lp = os.path.join(args.outdir, f"left_{saved:03d}_{ts}.png")
                rp = os.path.join(args.outdir, f"right_{saved:03d}_{ts}.png")
                cv2.imwrite(lp, left)
                cv2.imwrite(rp, right)
                saved += 1
                print(f"[{saved}] Tersimpan: {lp} | {rp}")
            else:
                print("Checkerboard belum terdeteksi penuh di kedua mata, coba reposisi.")

    cap.release()
    cv2.destroyAllWindows()
    print(f"\nTotal pasangan tersimpan: {saved}")
    print("Lanjut ke: python 02_stereo_calibrate.py")


if __name__ == "__main__":
    main()
