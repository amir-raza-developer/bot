from django.db import models


class Listing(models.Model):
    category = models.CharField(max_length=100)
    condition = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    tags = models.TextField(null=True, blank=True)
    availability = models.CharField(max_length=100, null=True, blank=True)
    delivery = models.CharField(max_length=255, null=True, blank=True)  # e.g. "pickup,delivery"
    
    # ✅ THIS LINE HAS BEEN ADDED
    tabs = models.IntegerField(default=1)

    meetup_preference = models.CharField(max_length=255, null=True, blank=True)
    save_as_draft = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Listing {self.id} - {self.category}"


class ListingTitle(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="titles"
    )
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class ListingLocation(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="locations"
    )
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.location


class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="listing_images/")

    def __str__(self):
        return f"Image for Listing {self.listing.id}"


class FacebookCredential(models.Model):
    phone_or_email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone_or_email