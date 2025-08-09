#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

def run(cmd):
    print(">>", cmd)
    ret = subprocess.call(cmd, shell=True)
    if ret != 0:
        sys.exit(f"Command failed ({ret}): {cmd}")

def check_tool():
    try:
        out = subprocess.check_output("which vogmerge", shell=True).decode().strip()
    except subprocess.CalledProcessError:
        out = ""
    if not out:
        sys.exit("Error: 'vogmerge' not found in PATH.")
    print(f"Using vogmerge: {out}")

def main():
    ap = argparse.ArgumentParser(description="Stack a .vog brick N times along +Y by gluing BC_4 (top) to BC_3 (bottom).")
    ap.add_argument("grid", help="Input .vog file (e.g., mesh.vog)")
    ap.add_argument("count", type=int, help="Total number of bricks in the final stack (>=1)")
    ap.add_argument("--dy", type=float, required=True, help="Brick height in Y (translation per layer)")
    ap.add_argument("--tol", type=float, default=1e-6, help="Glue tolerance for vogmerge (default: 1e-6)")
    ap.add_argument("--out", default=None, help="Output .vog filename (default: <base>_stack<count>.vog)")
    ap.add_argument("--keep_tmp", action="store_true", help="Keep intermediate .vog files")
    args = ap.parse_args()

    check_tool()

    in_path = Path(args.grid).resolve()
    if not in_path.exists():
        sys.exit(f"Input grid not found: {in_path}")

    base = in_path.with_suffix("").name
    workdir = Path.cwd()

    # Filenames
    start_vog = workdir / f"{base}_start.vog"          # once-renamed base
    combined_vog = workdir / f"{base}_combined.vog"    # rolling combined
    tmp_vog = workdir / f"{base}_combined_tmp.vog"     # scratch during glue
    slice_vog = workdir / f"{base}_slice.vog"          # translated copy per step

    out_vog = Path(args.out) if args.out else (workdir / f"{base}_stack{args.count}.vog")
    if out_vog.exists():
        out_vog.unlink()

    # 0) Start: copy/rename BC_3->bottom, BC_4->top (leave others unchanged)
    # We write to _start.vog so we don't mutate the original.
    cmd0 = (
        f'vogmerge -g "{in_path}" '
        f'-o "{start_vog}" '
        f'-bc BC_3,bottom -bc BC_4,top '
        f'-bc BC_5,inlet_1 -bc BC_6,outlet_1'
    )
    run(cmd0)

    # Initialize combined with the first brick as-is.
    shutil.copyfile(start_vog, combined_vog)

    # 1) Loop over remaining bricks: translate and glue
    # We want: glue combined.top  to new.bottom
    for i in range(1, args.count):
        dy_i = args.dy * i

        # Make a translated copy of the original *start_vog*
        # Keep its boundary names (bottom/top).
        idx = i + 1
        cmd_trans = (
            f'vogmerge -g "{start_vog}" '
            f'-o "{slice_vog}" '
            f'-yshift {dy_i} '
            f'-bc inlet_1,inlet_{idx} -bc outlet_1,outlet_{idx}'
        )
        run(cmd_trans)

        # Glue the previous stack (top) to the new slice (bottom)
        cmd_glue = (
            f'vogmerge -g "{combined_vog}" -glue top '
            f'-g "{slice_vog}" -glue bottom '
            f'-o "{tmp_vog}" -tol {args.tol}'
        )
        run(cmd_glue)

        # Move tmp→combined for next iteration
        tmp_vog.replace(combined_vog)

    # 2) Finalize: copy combined to requested output name
    shutil.copyfile(combined_vog, out_vog)

    # 3) Optional cleanup
    if not args.keep_tmp:
        for p in [start_vog, combined_vog, tmp_vog, slice_vog]:
            try:
                if p.exists():
                    p.unlink()
            except Exception:
                pass

    print(f"\nDone. Wrote: {out_vog}")

if __name__ == "__main__":
    main()
