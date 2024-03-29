import csv
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient


def path_become(file_name: str) -> Path:
    return Path(settings.CSV_DATA_DIR, file_name)


class Command(BaseCommand):
    files_to_models = (("ingredients.csv", Ingredient),)

    def check_files(self) -> None:
        """
        Folder presence check.

        Сheck for each file in the tuple `files_to_models`.
        Returns:
           None.

        Raises:
            FileNotFoundError: Файл не найден.

        """
        for file_name, _ in self.files_to_models:
            if not path_become(file_name).is_file():
                raise FileNotFoundError(f"{file_name} not exist")

    def to_base(self) -> None:
        """
        Transfer data from csv files in the `static/data` directory
        to the database.

        Returns:
            None.

        """
        for file_name, model in self.files_to_models:
            file: Path = path_become(file_name)
            date_list = []
            with open(file, "r", encoding="utf8") as csv_file:
                reader = csv.reader(csv_file, delimiter=",", quotechar='"')
                for num, row in enumerate(reader):
                    header = (
                        "name",
                        "measurement_unit",
                    )
                    new_date = model(
                        **{key: value for key, value in zip(header, row)},
                    )
                    date_list.append(new_date)
                model.objects.bulk_create(date_list, ignore_conflicts=True)
                print("done!")

    def handle(self, *args, **options) -> None:
        self.check_files()
        self.to_base()
