from django.db import models


class Customer(models.Model):
    class MembershipTier(models.TextChoices):
        NON_MEMBER = "", "Non-member"
        BRONZE = "bronze", "Bronze"
        SILVER = "silver", "Silver"
        GOLD = "gold", "Gold"

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    address = models.TextField()
    date_of_birth = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    membership_tier = models.CharField(
        max_length=20,
        choices=MembershipTier.choices,
        default=MembershipTier.NON_MEMBER,
        blank=True,
        verbose_name="membership tier",
    )
    member_since = models.DateField(null=True, blank=True)
    loyalty_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "customer"
        verbose_name_plural = "customers"

    def __str__(self):
        return self.name

    @property
    def is_member(self):
        return self.membership_tier != self.MembershipTier.NON_MEMBER
