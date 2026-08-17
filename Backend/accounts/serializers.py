"""Authentication serializers: user info, signup, and JWT with role claims."""

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

# Roles a member of the public may select during signup (admin is internal).
PUBLIC_ROLES = (User.Role.PHARMACIST, User.Role.CUSTOMER)


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "full_name",
            "first_name",
            "last_name",
            "role",
        )


class PharvTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Token serializer that embeds the role claim and returns the user."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class SignupSerializer(serializers.Serializer):
    """Public signup. Only pharmacist/customer roles are accepted."""

    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=PUBLIC_ROLES)

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return attrs

    @staticmethod
    def _unique_username(base):
        candidate = base or "user"
        index = 1
        while User.objects.filter(username=candidate).exists():
            index += 1
            candidate = f"{base or 'user'}{index}"
        return candidate

    def create(self, validated_data):
        email = validated_data["email"]
        base = "".join(
            char for char in email.split("@")[0].lower() if char.isalnum() or char in "@.+-_"
        )
        parts = validated_data["full_name"].strip().split(None, 1)
        return User.objects.create_user(
            username=self._unique_username(base),
            email=email,
            password=validated_data["password"],
            role=validated_data["role"],
            first_name=parts[0] if parts else "",
            last_name=parts[1] if len(parts) > 1 else "",
        )
