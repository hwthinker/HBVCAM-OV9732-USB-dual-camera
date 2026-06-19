#!/usr/bin/env python3
"""
Test program untuk HBVCAM-W2280U3-2 V22
1MP OV9732 USB3.0 Binocular Camera Module

Device ini muncul sebagai 1 UVC node, frame kiri+kanan digabung
side-by-side dalam satu gambar (mis. 2560x720 = 2 x 1280x720).
Script ini capture, split jadi 2 gambar (left/right), tampilkan,
dan print resolusi+FPS yang benar-benar ke-negotiate oleh OS/driver
(untuk verifikasi apakah device jalan di mode USB3.0 high-fps atau
jatuh ke fallback USB2.0 seperti yang diwanti-wanti vendor).

Pakai:
    python test_hbvcam_stereo.py --index 0 --width 2560 --height 720

Kontrol saat preview jalan:
    s = simpan snapshot (left/right terpisah)
    q / ESC = keluar

Catatan:
- Kalau gambar gagal terbuka / resolusi tidak ke-set, coba ganti
  kabel USB3.0 (jangan pakai kabel data HP / kabel charging biasa -
  vendor sudah wanti-wanti soal ini, sinyal USB3.0 SuperSpeed gampang
  drop ke USB2.0 kalau kabelnya tidak proper shielded).
- Index kamera (--index) bisa beda-beda. Kalau ada banyak webcam
  di laptop, coba 0, 1, 2, dst. Di Linux cek dulu dengan:
    v4l2-ctl --list-devices
"""

import argparse
import os
import time

import cv2


def open_camera(index: int, width: int, height: int, fourcc_str: str):
    backend = cv2.CAP_DSHOW if os.name == "nt" else cv2.CAP_V4L2
    cap = cv2.VideoCapture(index, backend)
    if not cap.isOpened():
        # fallback ke backend default kalau yang spesifik gagal
        cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        raise RuntimeError(f"Tidak bisa membuka kamera index {index}")

    fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
    cap.set(cv2.CAP_PROP_FOURCC, fourcc)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cap


def main():
    parser = argparse.ArgumentParser(description="Test HBVCAM OV9732 USB3.0 Binocular")
    parser.add_argument("--index", type=int, default=0, help="Index kamera (default 0)")
    parser.add_argument("--width", type=int, default=2560, help="Lebar gabungan L+R (default 2560)")
    parser.add_argument("--height", type=int, default=720, help="Tinggi frame (default 720)")
    parser.add_argument("--fourcc", type=str, default="MJPG", help="MJPG atau YUY2 (default MJPG)")
    parser.add_argument("--outdir", type=str, default="./snapshots", help="Folder simpan snapshot")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    cap = open_camera(args.index, args.width, args.height, args.fourcc)

    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)

    print("=" * 50)
    print(f"Diminta   : {args.width}x{args.height} @ {args.fourcc}")
    print(f"Aktual    : {actual_w}x{actual_h} @ {actual_fps:.1f} fps (klaim driver)")
    print("=" * 50)
    print("Tekan 's' untuk snapshot, 'q' atau ESC untuk keluar")

    frame_count = 0
    t_start = time.time()
    measured_fps = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Gagal membaca frame dari kamera.")
            break

        h, w = frame.shape[:2]
        mid = w // 2
        left = frame[:, :mid]
        right = frame[:, mid:]

        frame_count += 1
        elapsed = time.time() - t_start
        if elapsed >= 1.0:
            measured_fps = frame_count / elapsed
            frame_count = 0
            t_start = time.time()

        combo = frame.copy()
        cv2.putText(combo, f"{w}x{h}  measured ~{measured_fps:.1f} fps",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.line(combo, (mid, 0), (mid, h), (0, 0, 255), 1)

        cv2.imshow("Stereo gabungan (L | R)", combo)
        cv2.imshow("Left", left)
        cv2.imshow("Right", right)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):  # q atau ESC
            break
        elif key == ord("s"):
            ts = time.strftime("%Y%m%d_%H%M%S")
            left_path = os.path.join(args.outdir, f"left_{ts}.png")
            right_path = os.path.join(args.outdir, f"right_{ts}.png")
            cv2.imwrite(left_path, left)
            cv2.imwrite(right_path, right)
            print(f"Snapshot disimpan: {left_path} , {right_path}")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
