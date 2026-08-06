from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from djangoapp.models import CarMake, CarModel


class Command(BaseCommand):
    help = "Seed the Best Cars capstone demo data"

    def handle(self, *args, **options):
        root, _ = User.objects.get_or_create(username="root")
        root.email = "root@bestcars.example"
        root.first_name = "Root"
        root.last_name = "Administrator"
        root.is_staff = True
        root.is_superuser = True
        root.set_password("BestCars!2026")
        root.save()

        student, _ = User.objects.get_or_create(username="dat28062006")
        student.email = "Dat28062006@gmail.com"
        student.first_name = "Dat"
        student.last_name = "Tran"
        student.set_password("BestCars!2026")
        student.save()

        catalog = [
            ("Toyota", "Reliable Japanese automobiles", [("Camry", "Sedan", 2023), ("RAV4", "SUV", 2024)]),
            ("Ford", "American cars and trucks", [("Explorer", "SUV", 2022), ("F-150", "Truck", 2024)]),
            ("Honda", "Efficient and dependable vehicles", [("Civic", "Sedan", 2021), ("CR-V", "SUV", 2023)]),
        ]
        for make_name, description, models in catalog:
            make, _ = CarMake.objects.get_or_create(name=make_name, defaults={"description": description})
            for model_name, car_type, year in models:
                CarModel.objects.get_or_create(
                    car_make=make,
                    name=model_name,
                    year=year,
                    defaults={"car_type": car_type},
                )
        self.stdout.write(self.style.SUCCESS("Seeded 2 users, 3 makes, and 6 models."))
