#!/usr/bin/env python3
#
# AIHub Downloader Module
# Handles dataset downloads and file operations for AIHub API
#
# - Downloads datasets using API key authentication
# - Processes and merges file parts
# - Handles file tree and dataset information retrieval
#
# @author Jung-In An <ji5489@gmail.com>
# @with Claude Sonnet 4 (Cutoff 2025/06/16)

import csv
import os
import re
import subprocess
import tarfile
import time
from enum import Enum
from typing import Dict, List, Optional, Tuple

import requests


class DownloadStatus(Enum):
    """Enumeration for download operation status."""
    SUCCESS = "success"
    NETWORK_ERROR = "network_error"
    PRIVILEGE_ERROR = "privilege_error"
    AUTHENTICATION_ERROR = "authentication_error"
    FILE_NOT_FOUND = "file_not_found"
    INSUFFICIENT_DISK_SPACE = "insufficient_disk_space"
    UNKNOWN_ERROR = "unknown_error"

    def get_message(self) -> str:
        """Get human-readable message for the status."""
        messages = {
            DownloadStatus.SUCCESS: "Download completed successfully.",
            DownloadStatus.NETWORK_ERROR: "Network connection failed. Please check your internet connection.",
            DownloadStatus.PRIVILEGE_ERROR: "Terms and conditions must be accepted before downloading.",
            DownloadStatus.AUTHENTICATION_ERROR: "Authentication failed. Please check your API key.",
            DownloadStatus.FILE_NOT_FOUND: "The requested dataset or file was not found.",
            DownloadStatus.INSUFFICIENT_DISK_SPACE: "Insufficient disk space for download.",
            DownloadStatus.UNKNOWN_ERROR: "Download failed due to an unknown error."
        }
        return messages.get(self, "Unknown status.")

    def is_success(self) -> bool:
        """Check if the status represents a successful operation."""
        return self == DownloadStatus.SUCCESS

    def is_error(self) -> bool:
        """Check if the status represents an error."""
        return self != DownloadStatus.SUCCESS


class AIHubDownloader:
    BASE_URL = "https://api.aihub.or.kr"
    BASE_DOWNLOAD_URL = f"{BASE_URL}/down/0.5"
    BASE_FILETREE_URL = f"{BASE_URL}/info"
    DATASET_URL = f"{BASE_URL}/info/dataset.do"

    def __init__(self, auth_headers: Optional[Dict[str, str]] = None):
        self.auth_headers = auth_headers or {}

    def _process_response(
        self, response: requests.Response
    ) -> Tuple[bool, Optional[str]]:
        """Process the response and determine if it's a success."""
        if response.status_code == 200 or response.status_code == 502:
            content = response.text

            # Remove the first three lines if they match the specified pattern
            lines = content.split("\n")
            if len(lines) >= 3:
                if (
                    "UTF-8" in lines[0]
                    and "output normally" in lines[1]
                    and "modify the character information" in lines[2]
                ):
                    lines = lines[3:]

            # Find and format the notice section
            notice_start = -1
            notice_end = -1
            for i, line in enumerate(lines):
                if re.search(r"={3,}\s*공지\s*사항\s*={3,}", line, re.IGNORECASE):
                    notice_start = i
                elif notice_start != -1 and re.match(r"={3,}", line):
                    notice_end = i
                    break

            if notice_start != -1 and notice_end != -1:
                notice = "\n".join(lines[notice_start + 1: notice_end])
                if notice.strip() == "":
                    lines = lines[:notice_start] + lines[notice_end + 2:]
                else:
                    formatted_notice = f"Notice:\n{notice}\n"
                    lines = (
                        lines[:notice_start]
                        + [formatted_notice]
                        + lines[notice_end + 2:]
                    )

            content = "\n".join(lines)
            return True, content.strip()
        else:
            return False, None

    def get_file_tree(self, dataset_key: str) -> Optional[str]:
        """Fetch file tree structure for a specific dataset."""
        url = f"{self.BASE_FILETREE_URL}/{dataset_key}.do"
        try:
            response = requests.get(url, timeout=30)  # Add 30 second timeout
            success, content = self._process_response(response)
            if success:
                return content
            else:
                # Remove print statement - let calling code handle errors
                # print(f"Failed to fetch file tree. Status code: {response.status_code}")
                return None
        except requests.Timeout:
            # Remove print statement - let calling code handle errors
            # print("Timeout while fetching file tree")
            return None
        except requests.RequestException as e:
            # Remove print statement - let calling code handle errors
            # print(f"Request failed while fetching file tree: {e}")
            return None

    def process_dataset_list(self, content: str) -> List[Tuple[str, str]]:
        """Process the dataset list content."""
        lines = content.split("\n")

        # Remove header and footer lines
        start = next((i for i, line in enumerate(lines) if "=" in line), 0)
        end = next(
            (i for i in range(len(lines) - 1, -1, -1) if "=" in lines[i]), len(lines)
        )

        dataset_lines = lines[start + 1: end]

        datasets = []
        for line in dataset_lines:
            parts = line.split(",", 1)
            if len(parts) == 2:
                datasets.append((parts[0].strip(), parts[1].strip()))

        return datasets

    def export_dataset_list_to_csv(
        self, datasets: List[Tuple[str, str]], filename: str
    ):
        """Export the dataset list to a CSV file."""
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ID", "Name"])  # Header
            writer.writerows(datasets)

    def get_dataset_info(self) -> Optional[List[Tuple[str, str]]]:
        """Fetch information about all datasets and return as a list."""
        try:
            response = requests.get(self.DATASET_URL, timeout=30)  # Add 30 second timeout
            success, content = self._process_response(response)
            if success and content:
                return self.process_dataset_list(content)
            else:
                # Remove print statement - let calling code handle errors
                # print(
                #     f"Failed to fetch dataset information. Status code: {response.status_code}"
                # )
                return None
        except requests.Timeout:
            # Remove print statement - let calling code handle errors
            # print("Timeout while fetching dataset information")
            return None
        except requests.RequestException as e:
            # Remove print statement - let calling code handle errors
            # print(f"Request failed while fetching dataset information: {e}")
            return None

    def download_and_process_dataset(
        self, dataset_key: str, file_keys: str = "all", output_dir: str = ".",
        progress_callback=None
    ) -> DownloadStatus:
        """Download a dataset, extract it, merge parts, and clean up."""
        download_status = self.download_dataset(dataset_key, file_keys, output_dir, progress_callback)

        if download_status == DownloadStatus.SUCCESS:
            if progress_callback:
                progress_callback("Extracting files...", -1, -1, -1)  # Indeterminate progress
            tar_file = os.path.join(output_dir, "download.tar")

            # Extract the tar file
            self._extract_tar(tar_file, output_dir)

            if progress_callback:
                progress_callback("Merging file parts...", -1, -1, -1)  # Indeterminate progress
            # Merge parts in all subdirectories
            self._merge_parts_in_subdirs(output_dir)
            # Clean up: remove the original tar file
            os.remove(tar_file)
            return DownloadStatus.SUCCESS
        else:
            return download_status

    def _extract_tar(self, tar_file: str, extract_dir: str):
        """Extract the downloaded tar file."""
        with tarfile.open(tar_file, "r") as tar:
            tar.extractall(path=extract_dir)

    def _merge_parts_in_subdirs(self, root_dir: str):
        """Traverse all subdirectories and merge parts in the last child folders."""
        for dirpath, dirnames, filenames in os.walk(root_dir):
            if any(
                re.search(r".*\.part[0-9]+", filename, re.IGNORECASE)
                for filename in filenames
            ):
                self._merge_parts(dirpath)

    def _merge_parts(self, target_dir: str):
        """Merge all part files in the given directory."""
        # Find all unique prefixes of part files
        part_files = [
            f
            for f in os.listdir(target_dir)
            if re.search(r".*\.part[0-9]+", f, re.IGNORECASE)
        ]
        prefixes = set(f.rsplit(".part", 1)[0] for f in part_files)

        for prefix in prefixes:
            # Log merging progress instead of printing
            # print(f"Merging {prefix} in {target_dir}")

            # Find all part files for this prefix and sort them
            parts = sorted(
                [f for f in part_files if f.startswith(prefix)],
                key=lambda x: int(x.rsplit(".part", 1)[1]),
            )

            # Merge the parts
            with open(os.path.join(target_dir, prefix), "wb") as outfile:
                for part in parts:
                    with open(os.path.join(target_dir, part), "rb") as infile:
                        outfile.write(infile.read())

            # Remove the part files
            for part in parts:
                os.remove(os.path.join(target_dir, part))

    def _check_disk_space(self, required_size: int, output_dir: str) -> bool:
        """Check if there's sufficient disk space for the download."""
        try:
            fstat = os.statvfs(output_dir)
            available_space = fstat.f_frsize * fstat.f_bavail
            return available_space >= required_size
        except OSError:
            # If we can't check disk space, assume it's available
            return True

    def download_dataset(
        self, dataset_key: str, file_keys: str = "all", output_dir: str = ".",
        progress_callback=None
    ) -> DownloadStatus:
        """Download a dataset using requests."""
        url = f"{self.BASE_DOWNLOAD_URL}/{dataset_key}.do?fileSn={file_keys}"
        return self._download_with_requests(url, dataset_key, output_dir, progress_callback)

    def download_dataset_with_size_check(
        self, dataset_key: str, file_keys: str = "all", output_dir: str = ".",
        estimated_size: int = 0, progress_callback=None
    ) -> DownloadStatus:
        """Download a dataset with disk space checking."""
        # Check disk space if estimated size is provided
        if estimated_size > 0:
            if not self._check_disk_space(estimated_size, output_dir):
                return DownloadStatus.INSUFFICIENT_DISK_SPACE

        return self.download_dataset(dataset_key, file_keys, output_dir, progress_callback)

    def _download_with_requests(
            self, url: str, dataset_key: str, output_dir: str, progress_callback=None) -> DownloadStatus:
        """Download using requests with progress tracking."""
        output_file = os.path.join(output_dir, "download.tar")

        # Check if download.tar already exists and backup it
        if os.path.exists(output_file):
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(output_dir, f"download_{timestamp}.tar")
            os.rename(output_file, backup_file)
            # Remove the Korean print statement - this information is not essential for users
            # print(f"msg : download.tar 파일이 존재하여 {backup_file}로 백업하였습니다.")

        try:
            with requests.get(url, headers=self.auth_headers, stream=True) as response:
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))

                # Initialize progress tracking
                downloaded_size = 0
                start_time = time.time()
                last_update_time = start_time
                last_downloaded_size = 0

                with open(output_file, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:  # Filter out keep-alive chunks
                            file.write(chunk)
                            downloaded_size += len(chunk)

                            # Calculate speed and progress
                            current_time = time.time()
                            elapsed_time = current_time - start_time

                            # Update progress every 100ms to avoid overwhelming the GUI
                            if current_time - last_update_time >= 0.1:
                                # Calculate speed (bytes per second)
                                time_diff = current_time - last_update_time
                                size_diff = downloaded_size - last_downloaded_size
                                speed = size_diff / time_diff if time_diff > 0 else 0

                                # Calculate progress percentage (if total size is known from server)
                                # Note: The GUI will calculate its own percentage based on expected size
                                progress_percent = (downloaded_size / total_size * 100) if total_size > 0 else -1

                                # Call progress callback if provided
                                if progress_callback:
                                    progress_callback(
                                        f"Downloading... {self._format_size(downloaded_size)}",
                                        progress_percent,
                                        downloaded_size,
                                        speed
                                    )

                                last_update_time = current_time
                                last_downloaded_size = downloaded_size

                # Final progress update
                if progress_callback:
                    total_time = time.time() - start_time
                    avg_speed = downloaded_size / total_time if total_time > 0 else 0
                    progress_callback(
                        f"Download completed: {self._format_size(downloaded_size)}",
                        100,
                        downloaded_size,
                        avg_speed
                    )

                # Log download completion instead of printing
                # print("Download completed.")
                return DownloadStatus.SUCCESS

        except requests.RequestException as e:
            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 502:
                # Must submit the acceptance form before downloading
                form_url = f"https://aihub.or.kr/aihubdata/data/dwld.do?dataSetSn={dataset_key}"
                # Convert the privilege error message to a more concise format
                # print(f"+==============================================================================+")
                # print(f"| PrivilegeError: You must accept the terms and conditions before downloading. |")
                # print(f"| Please visit the following AIHub URL and accept the terms:                   |")
                # print(f"| {'':76s} |")
                # print(f"| {form_url:76s} |")
                # print(f"+==============================================================================+")

                # Open default browser for this URL
                import webbrowser
                webbrowser.open(form_url)
                return DownloadStatus.PRIVILEGE_ERROR
            elif hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 401:
                    return DownloadStatus.AUTHENTICATION_ERROR
                elif e.response.status_code == 404:
                    return DownloadStatus.FILE_NOT_FOUND
                else:
                    return DownloadStatus.NETWORK_ERROR
            else:
                return DownloadStatus.NETWORK_ERROR

    def _format_size(self, size_bytes: float) -> str:
        """Format bytes into human readable format (cross-platform)."""
        if size_bytes == 0:
            return "0B"

        size_names = ["B", "KiB", "MiB", "GiB", "TiB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f}{size_names[i]}"

    def get_raw_url(self, dataset_key: str, file_keys: str = "all") -> str:
        """Get the raw download URL for a dataset."""
        return f"{self.BASE_DOWNLOAD_URL}/{dataset_key}.do?fileSn={file_keys}"
