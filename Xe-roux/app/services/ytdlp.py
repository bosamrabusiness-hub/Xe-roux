"""Wrapper around yt-dlp CLI to extract video metadata and handle downloads."""

import asyncio
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


async def _run_cmd(cmd: List[str]) -> str:
    """Run external command asynchronously and return stdout."""
    # On Windows, use subprocess.run in a thread pool to avoid asyncio subprocess issues
    if sys.platform == "win32":
        import concurrent.futures
        def _run_in_thread():
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr)
            return result.stdout
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(pool, _run_in_thread)
    else:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(stderr.decode())
        return stdout.decode()


async def _run_cmd_with_progress(cmd: List[str], progress_callback=None) -> str:
    """Run external command with progress tracking using yt-dlp's progress output."""
    import re
    
    # Add progress reporting option to yt-dlp (newline ensures real-time output)
    progress_cmd = cmd + ["--newline", "--progress"]
    
    # On Windows, use subprocess.run in a thread pool to avoid asyncio subprocess issues
    if sys.platform == "win32":
        import concurrent.futures
        
        def _run_with_progress():
            import threading
            import queue
            
            process = subprocess.Popen(
                progress_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            stdout_lines = []
            stderr_lines = []
            progress_queue = queue.Queue()
            
            def read_stderr():
                """Read stderr and capture progress."""
                try:
                    print("DEBUG: Starting to read stderr")  # Debug log
                    for line in iter(process.stderr.readline, ''):
                        if not line:
                            break
                        stderr_lines.append(line)
                        print(f"DEBUG: Stderr line: {line.strip()}")  # Debug log
                        
                        # Parse progress information
                        if progress_callback and "[download]" in line:
                            print(f"DEBUG: Found download line: {line.strip()}")  # Debug log
                            # Extract percentage using regex
                            percent_match = re.search(r'(\d+(?:\.\d+)?)%', line)
                            if percent_match:
                                try:
                                    percent = float(percent_match.group(1))
                                    print(f"DEBUG: Extracted progress: {percent}%")  # Debug log
                                    progress_queue.put(percent)
                                    # Call progress callback immediately
                                    progress_callback(percent)
                                except Exception as e:
                                    print(f"DEBUG: Error parsing percentage: {e}")  # Debug log
                    print("DEBUG: Finished reading stderr")  # Debug log
                except Exception as e:
                    print(f"DEBUG: Exception in read_stderr: {e}")  # Debug log
            
            # Start stderr reading thread
            stderr_thread = threading.Thread(target=read_stderr)
            stderr_thread.daemon = True
            stderr_thread.start()
            
            # Read stdout
            try:
                for line in iter(process.stdout.readline, ''):
                    if not line:
                        break
                    stdout_lines.append(line)
                    # NEW: Also parse progress information from stdout (some systems emit progress here)
                    if progress_callback and "[download]" in line:
                        percent_match = re.search(r'(\d+(?:\.\d+)?)%', line)
                        if percent_match:
                            try:
                                percent = float(percent_match.group(1))
                                progress_queue.put(percent)
                                progress_callback(percent)
                            except Exception as e:
                                print(f"DEBUG: Error parsing percentage from stdout: {e}")  # Debug log
            except Exception:
                pass
            
            # Wait for stderr thread
            stderr_thread.join()
            
            # Wait for process to complete with timeout
            print("DEBUG: Waiting for process to complete...")  # Debug log
            try:
                returncode = process.wait(timeout=300)  # 5 minute timeout
                print(f"DEBUG: Process completed with return code: {returncode}")  # Debug log
            except subprocess.TimeoutExpired:
                print("DEBUG: Process timed out after 5 minutes")  # Debug log
                process.kill()
                raise Exception("yt-dlp process timed out after 5 minutes")
            
            stderr_thread.join(timeout=10)  # Give stderr thread time to finish
            
            # Get final progress if available
            final_progress = None
            while not progress_queue.empty():
                final_progress = progress_queue.get_nowait()
            
            if final_progress is not None:
                print(f"DEBUG: Final progress: {final_progress}%")  # Debug log
                progress_callback(final_progress)
            
            if returncode != 0:
                error_output = ''.join(stderr_lines)
                print(f"DEBUG: Error output: {error_output}")  # Debug log
                raise RuntimeError(error_output)
            
            # Store progress values for async processing
            progress_values = []
            while not progress_queue.empty():
                progress_values.append(progress_queue.get())
            
            return ''.join(stdout_lines), progress_values
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result, progress_values = await loop.run_in_executor(pool, _run_with_progress)
            
            # Process progress values
            if progress_callback and progress_values:
                print(f"DEBUG: Processing {len(progress_values)} progress values")  # Debug log
                for progress_value in progress_values:
                    print(f"DEBUG: Calling progress callback with {progress_value}%")  # Debug log
                    await progress_callback(progress_value)
            else:
                print(f"DEBUG: No progress callback or values: callback={progress_callback}, values={progress_values}")  # Debug log
            
            return result
    else:
        # For non-Windows systems, use asyncio subprocess with progress tracking
        process = await asyncio.create_subprocess_exec(
            *progress_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        stdout_lines = []
        
        async def read_stderr():
            while True:
                line = await process.stderr.readline()
                if not line:
                    break
                line = line.decode()
                
                # Parse progress information
                if progress_callback and "[download]" in line:
                    percent_match = re.search(r'(\d+(?:\.\d+)?)%', line)
                    if percent_match:
                        try:
                            percent = float(percent_match.group(1))
                            await progress_callback(percent)
                        except Exception:
                            pass  # Ignore parsing errors
        
        async def read_stdout():
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                stdout_lines.append(line.decode())
        
        # Read both streams concurrently
        await asyncio.gather(read_stderr(), read_stdout())
        
        await process.wait()
        
        if process.returncode != 0:
            stderr_output = await process.stderr.read()
            raise RuntimeError(stderr_output.decode())
        
        return ''.join(stdout_lines)


async def fetch_preview(url: str) -> Dict[str, Any]:
    """Return metadata for the provided URL using yt-dlp --dump-json."""
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--skip-download",
        url,
    ]
    output = await _run_cmd(cmd)
    data = json.loads(output)
    
    # Filter formats to only MP4 and audio formats
    all_formats = data.get("formats", [])
    filtered_formats = []
    
    for fmt in all_formats:
        ext = fmt.get("ext", "").lower()
        # Keep video formats (MP4) ONLY if they contain both video and audio
        if ext in {"mp4"}:
            if fmt.get("vcodec") != "none" and fmt.get("acodec") != "none":
                # Exclude resolutions higher than 2K (1440p)
                height = fmt.get("height")
                if height is None and fmt.get("resolution"):
                    # resolution might be like "1920x1080" or "1080p"
                    import re
                    m = re.search(r"(\d+)[pP]", fmt.get("resolution"))
                    if m:
                        height = int(m.group(1))
                if height is None or height <= 2160:
                    filtered_formats.append(fmt)
        # Keep common audio-only formats where vcodec is 'none'
        elif ext in {"m4a", "mp3", "wav", "flac", "aac", "ogg"}:
            if fmt.get("vcodec") == "none":
                filtered_formats.append(fmt)
    
    # Simplify and deduplicate based on ext + quality label
    mapped_formats = []
    seen_keys: set[str] = set()
    for fmt in filtered_formats:
        ext = fmt.get("ext", "").lower()
        # Determine quality/label field
        if fmt.get("vcodec") == "none":  # audio-only
            abr = fmt.get("abr") or fmt.get("tbr")
            if abr:
                abr_int = int(round(abr / 32) * 32)
                quality_label = f"{abr_int}K"
            else:
                quality_label = "audio only"
        else:
            quality_label = fmt.get("resolution") or fmt.get("height") or "video"

        key = f"{ext}_{quality_label}"
        if key in seen_keys:
            continue  # skip duplicate quality for same extension
        seen_keys.add(key)

        mapped_formats.append({
            "formatId": fmt.get("format_id", ""),
            "ext": ext,
            "resolution": quality_label,
            "filesize": fmt.get("filesize", None)
        })

    # Sort formats: Video (MP4 first) then audio, keeping ascending resolution/bitrate for user friendliness
    import re  # ensure available inside nested function
    def sort_key(item):
        is_video = item["resolution"].endswith("p") or item["resolution"].isdigit()
        if is_video:
            # extract number before 'p'
            m = re.search(r"(\d+)", str(item["resolution"]))
            height = int(m.group(1)) if m else 0
        else:
            # audio bitrate like 128K
            m = re.search(r"(\d+)", str(item["resolution"]))
            height = int(m.group(1)) if m else 0
        return (
            0 if is_video and item["ext"] == "mp4" else 1 if is_video else 2,  # MP4 video first, other video, then audio
            height
        )

    mapped_formats.sort(key=sort_key)

    
    return {
        "id": data.get("id"),
        "url": url,
        "title": data.get("title"),
        "thumbnail": data.get("thumbnail"),
        "duration": data.get("duration"),
        "formats": mapped_formats,
    }


async def download_with_progress(url: str, format_id: str, output_path: str, progress_callback=None) -> str:
    """Download video with progress tracking. Uses python yt_dlp for precise progress if available."""
    try:
        import yt_dlp  # type: ignore

        # Build format string mapping similar to previous logic
        if format_id.lower() == "mp4":
            mapped_format = f"bestvideo[ext={format_id}]+bestaudio[ext=m4a]/best[ext={format_id}]/best"
            final_format = mapped_format
        elif format_id.lower() == "mp3":
            final_format = "bestaudio"
        else:
            final_format = format_id

        def _hook(d: dict):
            if d.get("status") == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                downloaded = d.get("downloaded_bytes", 0)
                if total:
                    percent = downloaded / total * 100
                    if progress_callback:
                        try:
                            progress_callback(percent)
                        except Exception:
                            pass
        ydl_opts = {
            "format": final_format,
            "outtmpl": output_path,
            "progress_hooks": [_hook],
            # Suppress additional output – we manage our own logging/progress
            "noprogress": True,
            "quiet": True,
        }
        # Run in thread executor to avoid blocking event loop
        import asyncio, functools
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))
        return output_path
    except ImportError:
        # Fallback to CLI method
        if format_id.lower() in {"mp4"}:
            mapped_format = f"bestvideo[ext={format_id}]+bestaudio[ext=m4a]/best[ext={format_id}]/best"
            format_id_arg = mapped_format
        elif format_id.lower() == "mp3":
            format_id_arg = "bestaudio"
        else:
            format_id_arg = format_id

        cmd = [
            "yt-dlp",
            "-f",
            format_id_arg,
        ]

        if format_id.lower() == "mp3":
            cmd += ["-x", "--audio-format", "mp3"]

        cmd += [
            "-o",
            output_path,
            url,
        ]
        if progress_callback:
            return await _run_cmd_with_progress(cmd, progress_callback)
        else:
            return await _run_cmd(cmd)