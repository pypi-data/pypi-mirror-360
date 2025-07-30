import subprocess


def check_ffmpeg_installed():
    """
    Check if ffmpeg is installed on the system.

    Returns:
        True if ffmpeg is installed, False otherwise.
    """
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        return False
    return True


def convert_raw_video_to_output_file(
    raw_filepath: str,
    output_filepath: str,
    verbose=False,
):
    """
    Convert a raw video file to an output file using ffmpeg.

    Parameters:
        raw_filepath: The path to the raw video file.
        output_filepath: The path to the output file.
        verbose: Will output ffmpeg output to stdout
    """
    # Suppress ffmpeg output if not verbose
    stdout = subprocess.DEVNULL if not verbose else None

    subprocess.run(
        [
            "ffmpeg",
            "-i",
            raw_filepath,
            "-vf",
            "v360=dfisheye:e:ih_fov=193:iv_fov=193",
            "-y",
            output_filepath,
        ],
        stdout=stdout,
        stderr=subprocess.STDOUT,
    )
