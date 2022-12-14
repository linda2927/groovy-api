import logging
from datetime import datetime

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext_lazy as _
from softdelete.models import SoftDeleteManager, SoftDeleteObject


class UserManager(BaseUserManager, SoftDeleteManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    use_in_migrations = True

    def create_user(
            self,
            email=None,
        password=None,
        **extra_fields,
    ):
        """
        Create and save a User with the given email and password.
        """
        extra_fields.setdefault("is_superuser", False)

        if not email:
            raise ValueError("Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        user.save(using=self._db)
        logging.info(f"User [{user.id}] 회원가입")
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("university_id", 1)
        extra_fields.setdefault("admission_class", 2018)
        extra_fields.setdefault("grade", User.FRESHMEN)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email=email, password=password, **extra_fields)


class TimeStampMixin(models.Model):
    """
    abstract timestamp mixin base model for created_at, updated_at field
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractBaseUser, PermissionsMixin, TimeStampMixin, SoftDeleteObject):
    MALE = "MALE"
    FEMALE = "FEMALE"
    GENDER_CHOICES = (
        (None, "NONE"),
        (MALE, "MALE"),
        (FEMALE, "FEMALE"),
    )

    ADMISSION_YEAR = [(r, r) for r in range(2000, datetime.now().year + 2)]

    FRESHMEN = 1
    SOPHOMORE = 2
    JUNIOR = 3
    SENIOR = 4
    GRADE_CHOICES = (
        (FRESHMEN, 1),
        (SOPHOMORE, 2),
        (JUNIOR, 3),
        (SENIOR, 4),
    )

    OTHER = "기타"
    DELETE_REASONS = ((OTHER, _("기타")),)

    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(max_length=64, unique=True, null=True)
    is_university_email = models.BooleanField(default=True)
    nickname = models.CharField(
        max_length=20, blank=True, default="", help_text="서비스 상에서 사용되는 이름"
    )
    gender = models.CharField(max_length=8, choices=GENDER_CHOICES)
    birth_date = models.DateField(null=True)

    university = models.ForeignKey("University", on_delete=models.DO_NOTHING, null=True)
    is_university_confirmed = models.BooleanField(default=False)
    university_confirmed_at = models.DateTimeField(null=True)

    admission_class = models.SmallIntegerField(
        choices=ADMISSION_YEAR, default=datetime.now().year
    )
    grade = models.SmallIntegerField(choices=GRADE_CHOICES)

    profile_image_url = models.URLField(max_length=256, blank=True, default="")
    thumbnail_image_url = models.URLField(max_length=256, blank=True, default="")

    is_service_terms_agreed = models.BooleanField(default=False)
    is_push_allowed = models.BooleanField(default=False)
    push_id = models.CharField(null=True, max_length=64)

    login_attempt_at = models.DateTimeField(null=True)
    last_login_at = models.DateTimeField(null=True)

    app_version = models.CharField(null=True, max_length=16)
    auth_token = models.CharField(null=True, max_length=128)

    # deleted_at
    deleted_reason = models.CharField(
        choices=DELETE_REASONS, max_length=255, blank=True, null=True
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    is_active = None

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname"]

    class Meta:
        db_table = "user"
        unique_together = ["email"]
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return f"[{self.id}] {self.get_username()}"

    def __repr__(self):
        return f"User({self.id}, {self.get_username()})"

    def get_username(self):
        return getattr(self, self.USERNAME_FIELD)

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class UserSuggestion(TimeStampMixin):

    OTHER = "기타"
    SUGGESTION_TYPES = (OTHER, _("기타"))

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    suggestion_type = models.CharField(max_length=16)
    content = models.TextField()

    class Meta:
        db_table = "user_suggestion"


class University(TimeStampMixin):
    YONSEI = "YONSEI"

    UNIV_CHOICE = (
        (YONSEI, "YONSEI"),
    )

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, choices=UNIV_CHOICE, default=YONSEI)

    class Meta:
        db_table = "university"


class UserNotification(TimeStampMixin):
    FRIEND_REQUEST_RECEIVED = "FRIEND REQUEST RECEIVED"
    FRIEND_REQUEST_ACCEPTED = "FRIEND REQUEST ACCEPTED"
    JOIN_REQUEST_RECEIVED = "JOIN REQUEST RECEIVED"
    JOIN_REQUEST_ACCEPTED = "JOIN REQUEST ACCEPTED"
    JOIN_REQUEST_REFUSED = "JOIN REQUEST REFUSED"
    GENERAL = "GENERAL"
    PROMOTION = "PROMOTION"
    OTHER = "OTHER"

    NOTIFICATION_TYPE = (
        (FRIEND_REQUEST_RECEIVED, "FRIEND REQUEST RECEIVED"),
        (FRIEND_REQUEST_ACCEPTED, "FRIEND REQUEST ACCEPTED"),
        (JOIN_REQUEST_RECEIVED, "JOIN REQUEST RECEIVED"),
        (JOIN_REQUEST_ACCEPTED, "JOIN REQUEST ACCEPTED"),
        (JOIN_REQUEST_REFUSED, "JOIN REQUEST REFUSED"),
        (GENERAL, "GENERAL"),
        (PROMOTION, "PROMOTION"),
        (OTHER, "OTHER"),
    )

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(choices=NOTIFICATION_TYPE, max_length=30)
    content = models.CharField(max_length=300)
    redirect_url = models.URLField(blank=True, null=True, max_length=30)

    class Meta:
        db_table = "user_notification"


class UniversityManualVerification(TimeStampMixin):
    STUDENT_ID = "STUDENT ID"
    PROOF_OF_ENROLLMENT = "PROOF OF ENROLLMENT"
    PROOF_OF_ACCEPTANCE = "PROOF OF ACCEPTANCE"

    VERIFICATION_METHOD = (
        (STUDENT_ID, "STUDENT ID"),
        (PROOF_OF_ENROLLMENT, "PROOF OF ENROLLMENT"),
        (PROOF_OF_ACCEPTANCE, "PROOF OF ACCEPTANCE"),
    )

    REFUSED = "REFUSED"
    ACCEPTED = "ACCEPTED"
    PENDING = "PENDING"
    VERIFICATION_STATUS = (
        (REFUSED, "REFUSED"),
        (ACCEPTED, "ACCEPTED"),
        (PENDING, "PENDING"),
    )

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.DO_NOTHING)
    verification_method = models.CharField(choices=VERIFICATION_METHOD, max_length=20)
    verification_img_url = models.URLField(max_length=256, blank=True, default="")
    verification_status = models.CharField(choices=VERIFICATION_STATUS, default=PENDING, max_length=15)
    status_changed_at = models.DateTimeField(null=True)
