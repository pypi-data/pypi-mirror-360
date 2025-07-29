import os
import logging
import zipfile
import gdown
import shutil

logger = logging.getLogger(__name__)

class Downloader:
    """
    Downloads pretrained models and other relevant data from Google Drive using gdown.

    The downloader accepts a shareable Google Drive URL or file ID.
    It downloads the file using gdown’s fuzzy matching to handle different URL formats.
    If the downloaded file is a zip archive, it is automatically extracted.
    """

    def __init__(
        self,
        drive_url: str,
        output_dir: str = os.path.join(os.path.expanduser("~"), "rara_subject_indexer_resources")
    ):
        """
        Parameters
        ----------
        drive_url : str
            Google Drive shareable URL or file ID.
        output_dir : str, optional
            Directory to save downloaded data, by default "rara_subject_indexer_resources"
        """
        self.drive_url = drive_url
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def download(self) -> None:
        """
        Download the file from Google Drive using gdown.
        The function downloads the file (using fuzzy matching to extract the file ID if needed)
        directly into the designated output directory. If the file is a zip archive,
        it is automatically extracted.
        """
        logger.info(f"Downloading from {self.drive_url} to {self.output_dir}")
        # Pass output as a directory to let gdown infer the filename and place the file in output_dir.
        # Ensure that the output path ends with a separator to indicate it's a directory.
        output_path = os.path.join(self.output_dir, "")
        downloaded_path = gdown.download(self.drive_url, output_path, quiet=False, fuzzy=True)
        if not downloaded_path:
            raise RuntimeError("Download failed; no file was downloaded.")

        logger.info(f"Downloaded file saved into {downloaded_path}")

        if downloaded_path.endswith('.zip') or self._is_zip_file(downloaded_path):
            logger.info("Zip archive detected, extracting...")
            try:
                with zipfile.ZipFile(downloaded_path, 'r') as zip_ref:
                    zip_ref.extractall(self.output_dir)
                logger.info(f"Extracted zip archive to {self.output_dir}")
            except Exception as e:
                logger.error(f"Failed to extract zip archive: {e}")
                raise e
            os.remove(downloaded_path)
            
    def download_folder(self) -> None:
        """
        Download a Google Drive folder using gdown.
        The function downloads the folder directly into the designated output directory. 
        Zip archive in the folder are automatically extracted.
        """
        # Create a temporary zip folder, which will be deleted after
        # all the files are downloaded & extracted
        zip_dir = os.path.join(self.output_dir, "zip")
        logger.info(f"Downloading from {self.drive_url} to temporary directory '{zip_dir}'.")
        
        os.makedirs(zip_dir, exist_ok=True)
        
        # Download Google Drive folder
        downloaded_path = gdown.download_folder(self.drive_url, output=zip_dir)
        if not downloaded_path:
            raise RuntimeError("Download failed; no files were downloaded.")

        logger.info(f"Downloaded files saved into '{downloaded_path}'.")
        logger.info(f"Extracting .zip files...")
        
        downloaded_files = [os.path.join(zip_dir, fn) for fn in os.listdir(zip_dir)]
        
        for downloaded_path in downloaded_files:
            if downloaded_path.endswith(".zip") or self._is_zip_file(downloaded_path):
                logger.info("Zip archive detected, extracting...")
                try:
                    with zipfile.ZipFile(downloaded_path, "r") as zip_ref:
                        zip_ref.extractall(self.output_dir)
                    logger.info(f"Extracted zip archive to {self.output_dir}")
                except Exception as e:
                    logger.error(f"Failed to extract zip archive: {e}")
                    raise e
                os.remove(downloaded_path)
             
        logger.info(f"Removing zip files dir '{zip_dir}'.")
        shutil.rmtree(zip_dir)

    def _is_zip_file(self, file_path: str) -> bool:
        """
        Check whether the given file is a zip archive.

        Parameters
        ----------
        file_path : str
            Path to the file.

        Returns
        -------
        bool
            True if the file is a zip archive, False otherwise.
        """
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                _ = zip_ref.namelist()
            return True
        except zipfile.BadZipFile:
            return False
