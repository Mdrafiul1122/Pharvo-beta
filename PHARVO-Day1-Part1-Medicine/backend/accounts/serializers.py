from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.models import UserProfile


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        source="profile.role",
        choices=UserProfile.ROLE_CHOICES,
    )

    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=6,
    )

    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "password",
            "role",
            "email",
            "is_active",
            "date_joined",
        ]

        read_only_fields = [
            "id",
            "date_joined",
        ]

    def create(self, validated_data):
        profile_data = validated_data.pop(
            "profile",
            {},
        )

        password = validated_data.pop(
            "password",
            None,
        )

        if not password:
            raise serializers.ValidationError(
                {
                    "password":
                    "Password is required."
                }
            )

        user = User.objects.create(
            **validated_data
        )

        user.set_password(password)
        user.save()

        UserProfile.objects.create(
            user=user,
            role=profile_data.get(
                "role",
                "customer",
            ),
        )

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop(
            "profile",
            {},
        )

        password = validated_data.pop(
            "password",
            None,
        )

        for attr, value in validated_data.items():
            setattr(
                instance,
                attr,
                value,
            )

        if password:
            instance.set_password(password)

        instance.save()

        profile, _ = (
            UserProfile.objects.get_or_create(
                user=instance
            )
        )

        if "role" in profile_data:
            profile.role = profile_data["role"]
            profile.save()

        return instance