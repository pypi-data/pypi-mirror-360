import csv
import locale


class TR:
    def __init__(self, langcode: str, csv_file: str):
        self.langcode = langcode
        self.csv_file = csv_file
        self.f = open(csv_file, newline="")
        self.locale_csv = csv.DictReader(f=self.f, delimiter=",")
        self.csv_langcodes = self.locale_csv.fieldnames

    # TODO: add rtl support
    def check_rtl(langcode: str):
        print("This is experimental")
        # print(self.locale_csv)
        rtl_langcodes = ["ar", "he", "fa", "ur", "ps", "ku", "dv", "yi", "sd", "kmr"]
        if langcode in rtl_langcodes and langcode in self.locale_csv.fieldnames:
            return True
        else:
            return False

    def tr(self, target_key, langcode: str):
        for item in self.locale_csv:
            if item["stringname"] == target_key:
                try:
                    if item[langcode] == "":
                        self.f.close()
                        return item["en"]
                    else:
                        self.f.close()
                        return item[langcode]
                except:
                    self.f.close()
                    return item["en"]
