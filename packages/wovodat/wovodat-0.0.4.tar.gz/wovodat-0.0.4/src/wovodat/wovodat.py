import os
import pandas as pd
import requests
import zipfile
from requests import RequestException
from .const import CATEGORIES
from .validator import validate_data_type_code
from .utils import to_datetime, slugify
from functools import cached_property, cache
from typing_extensions import Self, Dict


class WOVOdat:
    download_url = (
        "https://wovodat.org/webServiceDataDownload/booleanDirDataDownload.php"
    )
    availability_url = (
        "https://wovodat.org/populate/convertie/Volcano_zone/sql_files/all_data.csv"
    )

    def __init__(
        self,
        verbose: bool = False,
        debug: bool = False,
    ):
        self.data_type_code = None
        self.verbose: bool = verbose
        self.debug: bool = debug

        self.output_dir = os.path.join(os.getcwd(), "output")
        self.wovodat_dir = os.path.join(self.output_dir, "wovodat")
        self.download_dir = os.path.join(self.wovodat_dir, "download")
        self.zip_dir = os.path.join(self.download_dir, "zip")
        self.extracted_dir = os.path.join(self.download_dir, "extracted")

        self.extracted_files = {}

    @cached_property
    def availability(self):
        df = pd.read_csv(self.availability_url)
        if len(df) == 0:
            print(f"⚠️ No data available in: {self.availability_url}")
            return pd.DataFrame()

        # Ensuring download directory exists
        os.makedirs(self.download_dir, exist_ok=True)
        filepath = os.path.join(self.download_dir, "availability.csv")

        df.to_csv(filepath, index=False)

        return df

    @cached_property
    def data_types(self) -> pd.DataFrame:
        categories = []
        for category in CATEGORIES:
            types = category["types"]
            for _type in types:
                _type["category"] = category["name"]
                _type["new_code"] = f"{category['code']}.{_type['code']}"
                categories.append(_type)

        df = pd.DataFrame(categories)
        df.drop(columns=["code"], inplace=True)
        df.rename(columns={"new_code": "code"}, inplace=True)
        df = df.iloc[:, [1, 0, 2]]

        return df

    def extract(self, zip_file: str, extract_dir: str = None) -> Dict[str, str]:
        """Extract zip files.

        Args:
            zip_file (str): zip file path.
            extract_dir (str): extract directory path. Defaults to None.

        Returns:
            Dict[str, str]: Metadata dan data file location.
        """
        if extract_dir is None:
            extract_dir = os.path.join(self.extracted_dir)
        os.makedirs(extract_dir, exist_ok=True)

        if self.debug:
            print(f"🔨 Extract directory: {extract_dir}. ")

        files_extracted = {}
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            for file in zip_ref.namelist():
                try:
                    zip_ref.extract(file, extract_dir)
                except OSError as e:
                    raise OSError(f"❌ Failed to extract {zip_file}: {e}")

                if "metadata" in file:
                    files_extracted["metadata"] = file
                else:
                    files_extracted["data"] = file

        if self.verbose:
            print(f"✅ Extracted {len(files_extracted)} files.")

        return files_extracted

    @cache
    def download(
        self,
        smithsonian_id: str,
        data_type_code: str,
        start_date: str,
        end_date: str,
        username: str,
        email: str,
        affiliation: str,
        url: str = None,
        output_dir: str = None,
        extract_zip: bool = True,
    ) -> Self:
        """Download data from WOVOdat website.

        Args:
            smithsonian_id (str): Smithsonian ID.
            data_type_code (str): Data type. Example: 6.2 for RSAM.
            start_date (str): Start date for download. YYYY-MM-DD format.
            end_date (str): End date for download. YYYY-MM-DD format.
            username (str): Username.
            email (str): Email.
            affiliation (str): Affiliation.
            url (str): Download URL. Optional
            output_dir (str): Output directory. Optional. Defaults to current directory.
            extract_zip (bool): Extract Zip files. Defaults to True.

        Returns:
            Self: WOVOdat object.
        """
        if url is None:
            url = self.download_url

        # Validate data type
        self.data_type_code = validate_data_type_code(data_type_code)

        # Validate date
        start_date_obj = to_datetime(start_date)
        end_date_obj = to_datetime(end_date)

        assert start_date_obj <= end_date_obj, ValueError(
            f"❌ Start date must ({start_date}) be before end date ({end_date})"
        )

        # TODO
        # Validate smithsonian_id

        # Ensuring output folder exists
        if output_dir is None:
            output_dir = self.output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Building params
        params = {
            "vdNum": smithsonian_id,
            "sTime": start_date,
            "eTime": end_date,
            "data": self.data_type_code,
            "downloadDataUsername": username,
            "downloadDataUseremail": email,
            "downloadDataUserobs": affiliation,
        }

        # Download zip file
        try:
            # Ensuring download directory exists
            os.makedirs(self.download_dir, exist_ok=True)

            # Downloading zip file
            response = requests.get(url, params=params)

            if self.debug:
                print(f"🔨 Downloaded from: {response.url}")
        except RequestException as e:
            raise RequestException(f"❌ Failed to download. {e}")

        if response.ok:
            # Ensuring zip directory exists
            os.makedirs(self.zip_dir, exist_ok=True)

            prefix = f"{smithsonian_id}_{start_date}_{end_date}_{slugify(self.data_type_code)}"
            filename = response.headers["content-disposition"].split("filename=")[1]
            file_path = os.path.join(self.zip_dir, f"{prefix}_{filename}")

            with open(file_path, mode="wb") as file:
                file.write(response.content)

            if self.verbose:
                print(f"✅ Downloaded file : {file_path}")

            # Extract files
            if extract_zip:
                self.extracted_files = self.extract(zip_file=file_path)

            return self

        raise ValueError(f"❌ Cannot find data: {response}")
