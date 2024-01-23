from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, name, tc, password=None, password2=None):
        """
        Creates and saves a User with the given email, name and tc and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            tc=tc,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

      # other methods...

    def create_superuser(self, email, name, tc, password=None):
        user = self.create_user(
            email,
            password=password,
            name=name,
            tc=tc,
        )
        user.is_admin = True

        # Set the updated_at field to the current timestamp
        user.save(using=self._db)
        
        return user

class MyUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    name=models.CharField(max_length=100)
    tc = models.BooleanField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at=models.DateTimeField(default=timezone.now, editable=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name","tc"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def __str__(self):
        return self.email
    

class UserProfile_step1(models.Model):
    age_choices = [
        ('18-24', '18-24'),
        ('25-34', '25-34'),
        ('35-44', '35-44'),
        ('45-54', '45-54'),
        ('55-64', '55-64'),
        ('64 and older', '64 and older'),
    ]

    gender_choices = [
        ('Female', 'Female'),
        ('Male', 'Male'),
        ('Other', 'Other'),
    ]
    
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='profile_step1')
    step1_age = models.CharField(max_length=20, choices=age_choices)
    step1_gender = models.CharField(max_length=10, choices=gender_choices)
    step1_username = models.CharField(max_length=50)
    step_1 = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.step_1 = True  
        super().save(*args, **kwargs)


class UserProfile_step2(models.Model):   
    relatioship_choices = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    childern_choices = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    professional_choices = [
        ('employed', 'Employed'),
        ('unemployed', 'Unemployed'),
    ]
    
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='profile_step2')
    step2_relationship = models.CharField(max_length=3, choices=relatioship_choices)
    step2_children = models.CharField(max_length=3, choices=childern_choices)
    step2_professional_status = models.CharField(max_length=10, choices=professional_choices)
    step_2 = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.step_2 = True  
        super().save(*args, **kwargs)


class UserProfile_step3(models.Model):   
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='profile_step3')
    step_3 = models.BooleanField(default=False)

    MULTIPLE_CHOICES = [
        ('option1', 'I want to increase happiness'),
        ('option2', 'I want to express gratitude'),
        ('option3', 'I want an energy boost'),
        ('option4', 'I want to feel more confident'),
        ('option5', 'I want to feel more relaxed'),
        ('option6', 'I want to feel peace'),
        ('option7', 'I want to reduce stress'),
        ('option8', 'I want to calm anxiety'),
        ('option9', 'I want to lower my blood pressure and heart rate'),
    ]

    step3_data = models.CharField(
        max_length=20,
        choices=MULTIPLE_CHOICES
    )


    def save(self, *args, **kwargs):
        self.step_3 = True  
        super().save(*args, **kwargs)




#streak system 
class StreakSystem(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_login_date = models.DateField(null=True, blank=True)

    def update_streak(self, login_date):
        if self.last_login_date and (login_date - self.last_login_date).days == 1:
            # user logged in consecutively to update streak
            self.current_streak += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        elif self.last_login_date and (login_date - self.last_login_date).days > 1:
            # if user skip a day reset streak
            self.current_streak = 1
        else:
            # if user first_time login or after a streak_break
            self.current_streak = 1

        self.last_login_date = login_date
        self.save()

    def __str__(self):
        return f"Streak for {self.user.name}"
    


class GoalsSettingModel(models.Model):
    smile_limit = models.PositiveIntegerField(default=5)
    count_limit = models.PositiveIntegerField(default=5)

class UserSmileModel(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    smile_time = models.DateTimeField(auto_now_add=True)
    smile_count = models.PositiveIntegerField(default=0)
    total_smile_time = models.PositiveIntegerField(default=0)    
    best_smile_time = models.PositiveIntegerField(default=0)    
    best_smile_count= models.PositiveIntegerField(default=0)
    best_smile_day= models.DateField(auto_now_add=True, null=True, blank=True)

    def calculate_average_smile(self):
        lis=[self.best_smile_time,self.total_smile_time]
        total=sum(lis)
        count=len(lis)
        average_smile_time=total/count
        return int(average_smile_time)


    def calculate_step(self):
        user = self.user
        user_level_model, created = UserLevelModel.objects.get_or_create(user=user)
        if self.total_smile_time >= GoalsSettingModel.objects.first().smile_limit or self.smile_count >= GoalsSettingModel.objects.first().count_limit:
            user_level_model.steps += 1
            user_level_model.save()


    def calculate_best_smile_date(self):            
        if self.smile_count >= self.best_smile_count:
            self.best_smile_count = self.smile_count
            self.best_smile_day = timezone.now()


    def save(self, *args, **kwargs):
        self.calculate_step()
        self.calculate_best_smile_date()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.user.name} smile data"

class UserLevelModel(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    steps = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    prev_step = models.PositiveIntegerField(default=0)

    def calculate_level(self):
        step = self.steps
        if step >= self.prev_step + 2:
            self.level += 1
            self.prev_step = step
            self.steps = 0

    def save(self, *args, **kwargs):
        self.calculate_level()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.name} - Level {self.level}"
    


class ActivitiesModel(models.Model):
    activity_name=models.CharField(max_length=100)
    activity_detail=models.CharField(max_length=300)
    activity_about=models.CharField( max_length=600)

    def __str__(self):
        return self.activity_name


class DailyQuoteModel(models.Model):
    quote=models.CharField(max_length=200)

    def __str__(self):
        return str(self.id)
    

