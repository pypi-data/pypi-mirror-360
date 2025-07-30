#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import argparse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

class GoogleSheetTranslator:
    def __init__(self, creds_file):
        load_dotenv()
        self.creds_file = creds_file
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.client = self._authorize()


    def _authorize(self):
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.creds_file, self.scope)
        return gspread.authorize(creds)

    def export_to_dict(self, sheet_name: str, tab_name: str) -> dict:
        """Fetches data from the specified sheet/tab and returns it as a language -> id -> translation dict."""
        sheet = self.client.open(sheet_name).worksheet(tab_name)
        data = sheet.get_all_values()

        if not data:
            raise ValueError("No data found in the sheet.")

        header = data[0]
        rows = data[1:]

        if "id" not in header:
            raise ValueError("Header must include an 'id' column.")

        id_index = header.index("id")
        translations = {}

        for lang_index, lang_code in enumerate(header):
            if lang_code == "id":
                continue
            lang_dict = {}
            for row in rows:
                if len(row) <= id_index:
                    continue
                row_id = row[id_index]
                if len(row) > lang_index and row[lang_index]:
                    lang_dict[row_id] = row[lang_index].replace("\n", "\\\n")
                else:
                    lang_dict[row_id] = ''
            translations[lang_code] = lang_dict

        return translations

    def export_from_env(self) -> dict:
        """Reads SHEET_NAME, TAB_NAME, and CREDS_FILE from environment variables and calls export_to_dict."""
        sheet_name = os.getenv("GST_SHEET")
        tab_name = os.getenv("GST_TAB")
        creds_file = os.getenv("GST_CREDS", "credentials.json")  # default fallback

        if not sheet_name or not tab_name:
            raise EnvironmentError("Environment variables GST_SHEET and GST_TAB must be set.")

        self.creds_file = creds_file
        self.client = self._authorize()
        return self.export_to_dict(sheet_name, tab_name)


    def export_to_java(self, resource_path, translation_prefix: str):
        trans = self.export_from_env()
        for key, value in trans.items():
            f = open(f"{resource_path}/{translation_prefix}_{key}.properties", "w")
            for key, value in value.items():
                f.write(f"{key}={value}\n")  

            f.close()


    def export_to_i18next(self, resource_path: str):
        trans = self.export_from_env()
        for lang, items in trans.items():
            path = f"{resource_path}/{lang}"
# Check whether the specified path exists or not
            isExist = os.path.exists(path)
            if not isExist:
                os.makedirs(path)

            with open(f"{path}/translation.json", "w") as translation:
                translation.write("{\n")
                index = len(items.items())
                for key, value in items.items():
                    val = value.replace('"', '\\\"')
                    translation.write(f"  \"{key}\": \"{val or key}\"")
                    index -= 1
                    if index > 0:
                        translation.write(",\n")

                translation.write("\n}\n")



def main():
    parser = argparse.ArgumentParser(description="Export translations from Google Sheets to JSON.")
    parser.add_argument('--sheet-name', required=False, help='Google Sheet name (or set GST_SHEET env)')
    parser.add_argument('--tab-name', required=False, help='Tab name in the sheet (or set GST_TAB env)')
    parser.add_argument('--credentials', default='credentials.json', help='Path to service account JSON')
    parser.add_argument('--output', default='translations.json', help='Path to output JSON file')
    parser.add_argument('--use-env', action='store_true', help='Use environment variables instead of CLI args')

    args = parser.parse_args()

    translator = GoogleSheetTranslator(args.credentials)

    if args.use_env:
        data = translator.export_from_env()
    else:
        if not args.sheet_name or not args.tab_name:
            raise ValueError("Either use --use-env or provide --sheet-name and --tab-name.")
        data = translator.export_to_dict(args.sheet_name, args.tab_name)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Exported translations to {args.output}")


if __name__ == "__main__":
    main()

