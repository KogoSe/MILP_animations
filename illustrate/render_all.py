"""Render every scene in order and (optionally) concatenate them into one
file with ffmpeg.

This matches common_prompt.md Section 6: "renders every scene in order
with the same quality flag ... optional --concat joins the rendered MP4s
into video/final.mp4 using ffmpeg (skip with a message if ffmpeg is not
installed)."

Usage (run from the `illustrate/` folder):

    uv run python render_all.py --quality h
    uv run python render_all.py --quality l --concat
    uv run python render_all.py --concat --output my_video.mp4

Renders one scene at a time in-process order (scene01 -> scene12), so if
one scene fails you still keep the videos already rendered before it.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# (module file, class name) in the order they appear in the video.
SCENES = [
    ("scene01_problem.py", "Scene01Problem"),
    ("scene02_grouping.py", "Scene02Grouping"),
    ("scene03_pairing.py", "Scene03Pairing"),
    ("scene04_judge_solution.py", "Scene04JudgeSolution"),
    ("scene05_search_space.py", "Scene05SearchSpace"),
    ("scene06_variables.py", "Scene06Variables"),
    ("scene07_load_equation.py", "Scene07LoadEquation"),
    ("scene08_milp_model.py", "Scene08MilpModel"),
    ("scene09_relaxation.py", "Scene09Relaxation"),
    ("scene10_branch_and_bound.py", "Scene10BranchAndBound"),
    ("scene11_proof.py", "Scene11Proof"),
    ("scene12_back_to_reality.py", "Scene12BackToReality"),
]

# manim quality flag -> (cli flag, resolution folder name under media/videos/<scene>/)
QUALITY_MAP = {
    "l": ("-ql", "480p15"),
    "m": ("-qm", "720p30"),
    "h": ("-qh", "1080p60"),
    "p": ("-qp", "1440p60"),
    "k": ("-qk", "2160p60"),
}


def render_scene(module_file, class_name, quality_flag, dry_run=False):
    """Render one scene with manim. Returns the expected output mp4 path."""
    module_stem = Path(module_file).stem
    _, res_folder = QUALITY_MAP[quality_flag if quality_flag in QUALITY_MAP else "h"]
    cmd = ["uv", "run", "manim", QUALITY_MAP[quality_flag][0], module_file, class_name]

    print(f"\n=== Rendering {class_name} ({module_file}) ===")
    print(" ".join(cmd))
    if not dry_run:
        result = subprocess.run(cmd, cwd=HERE)
        if result.returncode != 0:
            raise RuntimeError(
                f"manim failed for {class_name} (exit code {result.returncode}). "
                f"Stopping -- fix the error above and re-run."
            )

    out_path = HERE / "media" / "videos" / module_stem / res_folder / f"{class_name}.mp4"
    return out_path


def concat_videos(paths, output_path):
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        print(
            "\nffmpeg is not installed or not on PATH -- skipping concatenation. "
            "Install ffmpeg and re-run with --concat to produce the joined file."
        )
        return

    missing = [p for p in paths if not p.exists()]
    if missing:
        print("\nCannot concatenate -- these rendered files are missing:")
        for p in missing:
            print(f"  {p}")
        return

    concat_list_path = HERE / "_concat_list.txt"
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for p in paths:
            # ffmpeg's concat demuxer wants forward slashes and escaped quotes
            f.write(f"file '{p.as_posix()}'\n")

    cmd = [
        ffmpeg, "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list_path), "-c", "copy", str(output_path),
    ]
    print(f"\n=== Concatenating {len(paths)} scenes into {output_path} ===")
    print(" ".join(cmd))
    result = subprocess.run(cmd, cwd=HERE)
    concat_list_path.unlink(missing_ok=True)

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg concat failed (exit code {result.returncode}).")
    print(f"\nDone. Final video: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Render all HAC explainer scenes in order.")
    parser.add_argument("--quality", choices=list(QUALITY_MAP.keys()), default="h",
                         help="manim quality flag: l=480p15, m=720p30, h=1080p60 (default), "
                              "p=1440p60, k=2160p60")
    parser.add_argument("--concat", action="store_true",
                         help="After rendering, join all scenes into one file with ffmpeg.")
    parser.add_argument("--output", default="final.mp4",
                         help="Output filename for --concat (default: final.mp4, written in this folder).")
    parser.add_argument("--only", nargs="+", metavar="SceneClassName",
                         help="Render only these scene classes (e.g. --only Scene03Pairing Scene04JudgeSolution). "
                              "Concat still uses all 12 scenes' expected paths if --concat is passed alongside "
                              "--only, so make sure everything has been rendered at least once.")
    parser.add_argument("--dry-run", action="store_true",
                         help="Print the commands without actually running manim/ffmpeg.")
    args = parser.parse_args()

    scenes_to_render = SCENES
    if args.only:
        wanted = set(args.only)
        scenes_to_render = [s for s in SCENES if s[1] in wanted]
        unknown = wanted - {s[1] for s in SCENES}
        if unknown:
            print(f"Warning: unknown scene class name(s) ignored: {', '.join(sorted(unknown))}")

    rendered_paths = []
    for module_file, class_name in scenes_to_render:
        path = render_scene(module_file, class_name, args.quality, dry_run=args.dry_run)
        rendered_paths.append(path)

    if args.concat:
        all_paths = [
            HERE / "media" / "videos" / Path(mf).stem / QUALITY_MAP[args.quality][1] / f"{cn}.mp4"
            for mf, cn in SCENES
        ]
        output_path = HERE / args.output
        if args.dry_run:
            print(f"\n(dry run) would concatenate {len(all_paths)} files into {output_path}")
        else:
            concat_videos(all_paths, output_path)

    print("\nAll requested renders finished.")


if __name__ == "__main__":
    sys.exit(main())
