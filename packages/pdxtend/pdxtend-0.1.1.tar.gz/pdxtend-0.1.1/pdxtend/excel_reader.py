import pandas as pd
import os
import json
from typing import Optional, Union, Sequence


class ExcelReader:
    """
    A utility class for loading, updating, and saving Excel files using pandas.
    """

    def __init__(self, config_file: str = 'config.json') -> None:
        """
        Initialize the ExcelReader and load config if available.

        Parameters
        ----------
        config_file : str, default 'config.json'
            Path to the config JSON file containing the Excel path and sheet.
        """
        self._data: Optional[pd.DataFrame] = None
        self._path: Optional[str] = None
        self._sheet: Optional[str] = None
        self.config_file = config_file
        self._load_config()

        if not self._is_config_valid():
            self._force_valid_input()

    @property
    def data(self) -> pd.DataFrame:
        """
        Returns the loaded DataFrame, loading it if necessary.

        Returns
        -------
        pd.DataFrame
        """
        if self._data is None:
            self.load_file()
        return self._data

    def _load_config(self) -> None:
        """
        Load path and sheet name from the config file, or create an empty config.
        """
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self._path = config.get('path')
                self._sheet = config.get('sheet')
        else:
            self.save_config()

    def save_config(self) -> None:
        """
        Save current path and sheet name to the config file.
        """
        config = {'path': self._path, 'sheet': self._sheet}
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    def _is_valid_path(self, path: str) -> Optional[str]:
        """
        Validate the file path and return the appropriate engine.

        Parameters
        ----------
        path : str
            Excel file path to validate.

        Returns
        -------
        str or None
            Excel engine name if valid, otherwise None.
        """
        try:
            if path.endswith('.xlsb'):
                pd.read_excel(path, engine='pyxlsb')
                return 'pyxlsb'
            elif path.endswith(('.xlsx', '.xlsm')):
                pd.read_excel(path, engine='openpyxl')
                return 'openpyxl'
            return None
        except Exception:
            return None

    def _is_valid_sheet(self, path: str, sheet: str, engine: str) -> bool:
        """
        Check whether the sheet exists in the file.

        Parameters
        ----------
        path : str
            Excel file path.
        sheet : str
            Sheet name.
        engine : str
            Excel engine.

        Returns
        -------
        bool
        """
        try:
            return sheet in pd.ExcelFile(path, engine=engine).sheet_names
        except Exception:
            return False

    def _force_valid_input(self) -> None:
        """
        Loop to request valid file path and sheet name until provided.
        """
        while True:
            if not self._path or not os.path.exists(self._path):
                self._path = input("Enter a valid Excel file path (.xlsb, .xlsx, .xlsm): ").strip()
                if not os.path.exists(self._path):
                    print("Path not found. Try again.")
                    self._path = None
                    continue

            engine = self._is_valid_path(self._path)
            if not engine:
                print("Invalid file or unsupported format. Try again.")
                self._path = None
                continue

            if not self._sheet or not self._is_valid_sheet(self._path, self._sheet, engine):
                try:
                    available = pd.ExcelFile(self._path, engine=engine).sheet_names
                    print(f"\nAvailable sheets: {', '.join(available)}")
                    self._sheet = input("Enter a valid sheet name: ").strip()
                    continue
                except Exception as e:
                    print(f"Error reading file: {e}")
                    self._path, self._sheet = None, None
                    continue

            self.save_config()
            print("Path and sheet set successfully.")
            break

    def load_file(self, path: Optional[str] = None, sheet: Optional[str] = None) -> pd.DataFrame:
        """
        Load Excel file and return as a DataFrame.

        Parameters
        ----------
        path : str, optional
            Path to the Excel file. Uses saved path if not provided.
        sheet : str, optional
            Sheet name to load. Uses saved sheet if not provided.

        Returns
        -------
        pd.DataFrame
        """
        if path:
            self._path = path
        if sheet:
            self._sheet = sheet

        if not self._path:
            raise ValueError("No file path provided.")

        engine = self._is_valid_path(self._path)
        if not engine:
            raise ValueError("Invalid file or unsupported format.")

        self._data = pd.read_excel(self._path, sheet_name=self._sheet, engine=engine)
        return self._data

    def new_path(self, ask_user: bool = True) -> None:
        """
        Allow user to change the file path.

        Parameters
        ----------
        ask_user : bool, default True
            Whether to prompt the user.
        """
        if self._path and ask_user:
            while True:
                response = input(f"Current file: {self._path}. Load another? (y/n): ").strip().lower()
                if response == 'y':
                    while True:
                        new_path = input("Enter new path: ").strip()
                        engine = self._is_valid_path(new_path)
                        if engine:
                            self._path = new_path
                            self._data = None
                            self.save_config()
                            print("Path updated.")
                            break
                        else:
                            print("Invalid path or format.")
                    break
                elif response == 'n':
                    print("Keeping current path.")
                    break
                else:
                    print("Please enter 'y' or 'n'.")

    def new_sheet(self) -> None:
        """
        Allow user to change the sheet name.
        """
        engine = self._is_valid_path(self._path)
        if not engine:
            print("Invalid current path. Use new_path().")
            return

        try:
            sheets = pd.ExcelFile(self._path, engine=engine).sheet_names
            print(f"\nAvailable sheets: {', '.join(sheets)}")
            while True:
                new_sheet = input("Enter new sheet name: ").strip()
                if new_sheet in sheets:
                    self._sheet = new_sheet
                    self._data = None
                    self.save_config()
                    print("Sheet updated.")
                    break
                else:
                    print("Sheet not found.")
        except Exception as e:
            print(f"Error reading file: {e}")

    def _is_config_valid(self) -> bool:
        """
        Validate if saved path and sheet are usable.

        Returns
        -------
        bool
        """
        if not self._path or not os.path.exists(self._path):
            return False
        engine = self._is_valid_path(self._path)
        if not engine:
            return False
        return bool(self._sheet and self._is_valid_sheet(self._path, self._sheet, engine))

    def save_data(
        self,
        dataframe: Optional[pd.DataFrame] = None,
        path: Optional[Union[str, os.PathLike]] = None,
        sheet_name: Optional[str] = None,
        index: bool = False,
        na_rep: str = "",
        float_format: Optional[str] = None,
        columns: Optional[Sequence[str]] = None,
        header: Union[bool, Sequence[str]] = True,
    ) -> None:
        """
        Save DataFrame to Excel file, replacing the sheet if it exists.

        Parameters
        ----------
        dataframe : pd.DataFrame, optional
            DataFrame to save. If not provided, uses self._data.
        path : str or os.PathLike, optional
            Destination file path. Uses current path if not provided.
        sheet_name : str, optional
            Sheet name to write to. Uses current sheet if not provided.
        index : bool, default False
            Whether to write row indices.
        na_rep : str, default ''
            String representation of missing values.
        float_format : str, optional
            Format for float numbers.
        columns : sequence, optional
            Columns to include in output.
        header : bool or sequence, default True
            Write column headers or use custom labels.
        """
        save_path = path or self._path
        sheet = sheet_name or self._sheet

        if not save_path or not sheet:
            raise ValueError("Path and sheet name must be provided.")

        if dataframe is None:
            if self._data is None:
                raise ValueError("No data available to save.")
            dataframe = self._data

        try:
            with pd.ExcelWriter(save_path, engine="openpyxl", mode='a', if_sheet_exists='replace') as writer:
                dataframe.to_excel(
                    writer,
                    sheet_name=sheet,
                    index=index,
                    na_rep=na_rep,
                    float_format=float_format,
                    columns=columns,
                    header=header
                )
            print(f"Data successfully saved to '{save_path}' (sheet: '{sheet}').")
        except Exception as e:
            print(f"Error saving file: {e}")
