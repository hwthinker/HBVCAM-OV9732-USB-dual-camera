"""
Dual / Stereo Camera Viewer — Gearway OV9732 (15aa:1555)
Cross-platform: Linux (V4L2) dan Windows (DirectShow)

Kamera ini mengirim satu frame wide side-by-side (kiri|kanan).
Program ini membelah frame tersebut dan menampilkan kedua kamera.

Cara pakai:
    python check_dual_camera.py                # auto-detect
    python check_dual_camera.py --device 4     # paksa pakai device index 4
    python check_dual_camera.py --res 1280 720 # paksa resolusi per-mata

Kontrol keyboard:
    q         = keluar
    s         = screenshot
    f         = fullscreen toggle
    h         = flip horizontal toggle
    i         = tampilkan/sembunyikan info overlay
"""

import sys
import argparse
import time
import cv2
import numpy as np

# ── Platform detection ────────────────────────────────────────────────────────
IS_WINDOWS = sys.platform == 'win32'
IS_LINUX   = sys.platform.startswith('linux')

if IS_WINDOWS:
    CAMERA_BACKEND = cv2.CAP_DSHOW
    DEVICE_LABEL   = "Camera #{}"
else:
    CAMERA_BACKEND = cv2.CAP_V4L2
    DEVICE_LABEL   = "/dev/video{}"

# ── Resolusi stereo yang dicoba (total_width x height) ──────────────────────
STEREO_RESOLUTIONS = [
    (2560, 720),
    (1280, 480),
    (1600, 600),
]

DEVICE_NAMES_STEREO = ["USB Camera", "Gearway", "HBVCAM", "OV9732", "stereo"]


def find_stereo_device_linux():
    import glob
    candidates = []
    for path in sorted(glob.glob("/sys/class/video4linux/video*/name")):
        try:
            name = open(path).read().strip()
            if any(s.lower() in name.lower() for s in DEVICE_NAMES_STEREO):
                idx = int(path.split("video")[2].split("/")[0])
                candidates.append((idx, name))
        except Exception:
            pass
    for idx, name in candidates:
        if idx % 2 == 0:
            return idx
    return candidates[0][0] if candidates else None


_PS_DSHOW_ENUM = r"""
$src = @"
using System;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;
[ComImport,Guid("29840822-5B84-11D0-BD3B-00A0C911CE86"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface ICreateDevEnum{[PreserveSig]int CreateClassEnumerator([In]ref Guid p,out IEnumMoniker e,int f);}
[ComImport,Guid("62BE5D10-60EB-11d0-BD3B-00A0C911CE86")]class SDE{}
[ComImport,Guid("55272A00-42CB-11CE-8135-00AA004BB851"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IPropertyBag{[PreserveSig]int Read([MarshalAs(UnmanagedType.LPWStr)]string n,ref object v,object e);[PreserveSig]int Write([MarshalAs(UnmanagedType.LPWStr)]string n,ref object v);}
public class DSE{
static Guid VID=new Guid("860BB310-5D01-11d0-BD3B-00A0C911CE86");
public static string Run(){var r="";var de=(ICreateDevEnum)new SDE();IEnumMoniker em;de.CreateClassEnumerator(ref VID,out em,0);if(em==null)return "";IMoniker[]m=new IMoniker[1];int i=0;while(em.Next(1,m,IntPtr.Zero)==0){Guid bg=typeof(IPropertyBag).GUID;object bo;m[0].BindToStorage(null,null,ref bg,out bo);var pb=(IPropertyBag)bo;object v=null;pb.Read("FriendlyName",ref v,null);r+=string.Format("{0}|{1}\n",i,v);i++;}return r;}}
"@
Add-Type -TypeDefinition $src -Language CSharp
[DSE]::Run()
"""


def _dshow_enumerate():
    import subprocess
    try:
        result = subprocess.run(
            ['powershell', '-NoProfile', '-Command', _PS_DSHOW_ENUM],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            cameras = []
            for line in result.stdout.strip().splitlines():
                line = line.strip()
                if '|' not in line:
                    continue
                idx_str, name = line.split('|', 1)
                cameras.append((int(idx_str.strip()), name.strip()))
            return cameras
    except Exception:
        pass
    return []


def list_cameras_windows():
    cameras = _dshow_enumerate()
    if cameras:
        return cameras
    result = []
    for i in range(10):
        cap = cv2.VideoCapture(i, CAMERA_BACKEND)
        if cap.isOpened():
            result.append((i, f"Camera #{i}"))
            cap.release()
    return result


def list_cameras_linux():
    import glob
    cameras = []
    for path in sorted(glob.glob("/sys/class/video4linux/video*/name")):
        try:
            name = open(path).read().strip()
            idx  = int(path.split("video")[2].split("/")[0])
            cameras.append((idx, name))
        except Exception:
            pass
    return cameras


def list_cameras():
    if IS_WINDOWS:
        return list_cameras_windows()
    return list_cameras_linux()


def prompt_camera_selection(cameras, default_idx):
    print("\nKamera yang tersedia:")
    print("-" * 40)
    for idx, name in cameras:
        tag = "  <-- [DEFAULT]" if idx == default_idx else ""
        print(f"  [{idx}] {name}{tag}")
    print("-" * 40)

    valid  = [idx for idx, _ in cameras]
    prompt = (f"Pilih index kamera (Enter = {default_idx}): "
              if default_idx is not None else f"Pilih index kamera {valid}: ")

    while True:
        try:
            choice = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(0)

        if choice == "" and default_idx is not None:
            print(f"[INFO] Memakai default: index {default_idx}")
            return default_idx
        try:
            chosen = int(choice)
            if chosen in valid:
                return chosen
            print(f"  [!] Index {chosen} tidak ada. Pilih dari: {valid}")
        except ValueError:
            print("  [!] Masukkan angka atau tekan Enter untuk default.")


def find_stereo_device_windows():
    for idx, name in _dshow_enumerate():
        if any(s.lower() in name.lower() for s in DEVICE_NAMES_STEREO):
            print(f"[INFO] DirectShow [{idx}] '{name}' -> stereo camera")
            return idx
    for i in range(10):
        cap = cv2.VideoCapture(i, CAMERA_BACKEND)
        if not cap.isOpened():
            continue
        for total_w, h in STEREO_RESOLUTIONS:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,  total_w)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
            if (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) == total_w and
                    int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) == h):
                cap.release()
                print(f"[INFO] Fallback: index {i} support stereo {total_w}x{h}")
                return i
        cap.release()
    return None


def find_stereo_device():
    if IS_WINDOWS:
        return find_stereo_device_windows()
    return find_stereo_device_linux()


def open_stereo(device_idx, forced_res=None):
    cap = cv2.VideoCapture(device_idx, CAMERA_BACKEND)
    if not cap.isOpened():
        cap = cv2.VideoCapture(device_idx)
    if not cap.isOpened():
        return None, 0, 0

    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if forced_res:
        eye_w, eye_h = forced_res
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  eye_w * 2)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, eye_h)
        return cap, int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) // 2, int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    for total_w, h in STEREO_RESOLUTIONS:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  total_w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        if (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) == total_w and
                int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) == h):
            return cap, total_w // 2, h

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return cap, w // 2, h


def draw_overlay(img, text_lines, start_y=30):
    for i, line in enumerate(text_lines):
        y = start_y + i * 22
        cv2.putText(img, line, (9, y + 1),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(img, line, (8, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 1, cv2.LINE_AA)


def show_stereo(cap, eye_w, eye_h, device_idx):
    total_w   = eye_w * 2
    dev_label = DEVICE_LABEL.format(device_idx)

    print(f"\n[INFO] Device : {dev_label}")
    print(f"[INFO] Frame  : {total_w}x{eye_h} -> setiap mata {eye_w}x{eye_h}")
    print(f"[INFO] FPS cap: {cap.get(cv2.CAP_PROP_FPS):.1f}")
    print("\n[INFO] Keyboard: q=keluar | s=screenshot | f=fullscreen | h=flip | i=info")

    # Biarkan kamera pakai AUTO exposure & AUTO WB bawaan driver
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1 if IS_WINDOWS else 3)
    cap.set(cv2.CAP_PROP_AUTO_WB, 1)
    for _ in range(5):
        cap.read()

    screenshot_n = 0
    fullscreen   = False
    flip_h       = False
    show_info    = True
    frame_count  = 0
    t0           = time.time()
    fps_display  = 0.0

    win = "Gearway OV9732 - Dual Stereo Camera"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win, min(total_w + 4, 1800), eye_h + 60)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        _, fw = frame.shape[:2]
        if fw < eye_w * 2:
            print(f"[WARNING] Frame terlalu sempit ({fw}px)")
            break

        left  = frame[:, :eye_w].copy()
        right = frame[:, eye_w:eye_w * 2].copy()

        if flip_h:
            left  = cv2.flip(left,  1)
            right = cv2.flip(right, 1)

        frame_count += 1
        elapsed = time.time() - t0
        if elapsed >= 1.0:
            fps_display = frame_count / elapsed
            frame_count = 0
            t0 = time.time()

        if show_info:
            draw_overlay(left, [
                f"KIRI  [{eye_w}x{eye_h}]",
                f"FPS: {fps_display:.1f}",
            ])
            draw_overlay(right, [
                f"KANAN [{eye_w}x{eye_h}]",
            ])

        divider = np.zeros((eye_h, 4, 3), dtype=np.uint8)
        divider[:] = (0, 200, 0)
        cv2.imshow(win, np.hstack([left, divider, right]))

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('s'):
            screenshot_n += 1
            fname = f"stereo_{screenshot_n:03d}.jpg"
            cv2.imwrite(fname, np.hstack([left, divider, right]))
            print(f"[SAVED] {fname}")
        elif key == ord('f'):
            fullscreen = not fullscreen
            cv2.setWindowProperty(win, cv2.WND_PROP_FULLSCREEN,
                cv2.WINDOW_FULLSCREEN if fullscreen else cv2.WINDOW_NORMAL)
        elif key == ord('h'):
            flip_h = not flip_h
        elif key == ord('i'):
            show_info = not show_info

    cap.release()
    cv2.destroyAllWindows()
    print("\n[INFO] Selesai.")


def main():
    parser = argparse.ArgumentParser(
        description="Gearway OV9732 Dual Stereo Camera Viewer")
    parser.add_argument("--device", "-d", type=int, default=None,
                        help="Camera device index (default: auto-detect)")
    parser.add_argument("--res", nargs=2, type=int, metavar=("W", "H"), default=None,
                        help="Resolusi per mata, misal: --res 1280 720")
    args = parser.parse_args()

    platform_tag = "Windows/DirectShow" if IS_WINDOWS else "Linux/V4L2"
    print("=" * 60)
    print("  Gearway OV9732 — Dual Stereo Camera")
    print(f"  Platform: {platform_tag}")
    print("=" * 60)

    device_idx = args.device
    if device_idx is None:
        print("\n[INFO] Mencari kamera yang tersedia...")
        cameras     = list_cameras()
        default_idx = find_stereo_device()

        if not cameras:
            print("[ERROR] Tidak ada kamera ditemukan.")
            sys.exit(1)

        device_idx = prompt_camera_selection(cameras, default_idx)

    print(f"\n[INFO] Membuka {DEVICE_LABEL.format(device_idx)}...")

    forced_res = tuple(args.res) if args.res else None
    cap, eye_w, eye_h = open_stereo(device_idx, forced_res)

    if cap is None:
        print(f"[ERROR] Tidak bisa membuka {DEVICE_LABEL.format(device_idx)}")
        sys.exit(1)

    if eye_w == 0:
        print("[ERROR] Resolusi tidak valid dari kamera.")
        cap.release()
        sys.exit(1)

    show_stereo(cap, eye_w, eye_h, device_idx)


if __name__ == "__main__":
    main()
