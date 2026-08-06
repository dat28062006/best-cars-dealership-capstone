from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class CarMake(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class CarModel(models.Model):
    SEDAN = "Sedan"
    SUV = "SUV"
    WAGON = "Wagon"
    TRUCK = "Truck"
    TYPES = [(SEDAN, "Sedan"), (SUV, "SUV"), (WAGON, "Wagon"), (TRUCK, "Truck")]

    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE, related_name="models")
    name = models.CharField(max_length=100)
    car_type = models.CharField(max_length=20, choices=TYPES, default=SEDAN)
    year = models.IntegerField(validators=[MinValueValidator(2015), MaxValueValidator(2026)])

    class Meta:
        constraints = [models.UniqueConstraint(fields=["car_make", "name", "year"], name="unique_car_model")]

    def __str__(self):
        return f"{self.car_make.name} {self.name} ({self.year})"

