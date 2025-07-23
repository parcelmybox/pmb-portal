from django.db import models

class ShippingOrder(models.Model):
    pickup_city = models.CharField(max_length=100)
    destination_country = models.CharField(max_length=100)
    destination_zip = models.CharField(max_length=20)
    carrier = models.CharField(max_length=50)
    package_type = models.CharField(max_length=50)
    length = models.FloatField(null=True, blank=True)
    width = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    volumetric_weight = models.FloatField(null=True, blank=True)
    price = models.FloatField()
    ship_days = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pickup_city} ➝ {self.destination_country} ({self.carrier})"
