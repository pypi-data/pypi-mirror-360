from uuid import uuid4
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)



class UserManager(BaseUserManager):

    def create_user(self, username, nickname, phone_number, email_address, password):
        """
        Creates and saves a User with the username, nickname, phone_number, email_address.
        """
        if not (username and nickname and phone_number and email_address and password):
            raise ValueError('Users must have username, nickname, phone_number, email_address')

        user = self.model(
            username=username,
            nickname=nickname,
            phone_number=phone_number,
            email_address=self.normalize_email(email_address)
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, nickname, phone_number, email_address, password):
        """
        Creates and saves a superuser with the username, nickname, phone_number, email_address.
        """
        user = self.create_user(
            username=username,
            nickname=nickname,
            phone_number=phone_number,
            email_address=email_address,
            password=password
        )
        user.is_superuser = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    username = models.CharField(
        verbose_name='Username',
        max_length=80,
        blank=False,
        null=False,
        unique=True,
    )
    nickname = models.CharField(
        verbose_name='Nickname',
        max_length=32,
        blank=False,
        null=False,
    )
    first_name = models.CharField(
        verbose_name='First Name',
        max_length=32,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        verbose_name='Last Name',
        max_length=32,
        blank=False,
        null=False,
    )
    phone_number = models.CharField(
        verbose_name='Phone Number',
        max_length=32,
        blank=False,
        null=False,
    )
    email_address = models.EmailField(
        verbose_name='Email Address',
        max_length=128,
        unique=True,
        blank=False,
        null=False,
    )
    photo_url = models.URLField(
        verbose_name='Photo URL',
        max_length=128,
        blank=True,
        null=True,
    )
    is_verified = models.BooleanField(default=False, blank=False, null=False)
    is_active = models.BooleanField(default=True, blank=False, null=False)
    is_admin = models.BooleanField(default=False, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    updated_at = models.DateTimeField(auto_now=True, blank=False, null=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email_address'
    REQUIRED_FIELDS = [
        'nickname',
        'first_name',
        'last_name',
        'email_address',
        'phone_number',
    ]

    class Meta:
        ordering = ["last_name", "first_name", "is_admin", "is_active",]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.nickname

    def get_absolute_url(self):
        return "/users/%s/" % self.id

    @property
    def uid(self):
        return self.id

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Simplest possible answer: All admins are staff
        return self.is_admin


