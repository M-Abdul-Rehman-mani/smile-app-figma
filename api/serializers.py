from rest_framework import serializers
from .models import MyUser, UserProfile_step1, UserProfile_step2, UserProfile_step3, StreakSystem,UserSmileModel,UserLevelModel,ActivitiesModel, DailyQuoteModel
from django.conf import settings

#send mail 
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input': 'password'}, write_only=True)

    class Meta:
        model = MyUser
        fields = ["email", "name", "password", "password2", "tc"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        password = attrs.get("password")  
        password2 = attrs.get("password2") 

        if password != password2:
            raise serializers.ValidationError("Passwords do not match")

        return attrs

    def create(self, validated_data): 
        return MyUser.objects.create_user(**validated_data) 



class UserLoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255)

    class Meta:
        model=MyUser
        fields=["email","password"]




class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=MyUser
        fields=['id', 'email', 'name', 'is_active','is_staff', 'is_admin', ]



class ChangePasswordSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=100, style={'input': 'password'}, write_only=True)
    password2=serializers.CharField(max_length=100, style={'input': 'password'}, write_only=True)

    class Meta:
        model=MyUser
        fields=["password","password2"]

    def validate(self, attrs):
        password = attrs.get("password")  
        password2 = attrs.get("password2") 
        user=self.context.get("user")
        if password != password2:
            raise serializers.ValidationError("Passwords do not match")
        user.set_password(password)
        user.save()
        return attrs



class SendPasswordMailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user = MyUser.objects.get(email=email)
        except MyUser.DoesNotExist:
            raise serializers.ValidationError("Email is not registered")

        # Create an instance of PasswordResetTokenGenerator
        token_generator = PasswordResetTokenGenerator()

        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = token_generator.make_token(user)
        link = 'http://localhost:8000/api/reset_password/'+uid+'/'+token

        subject = 'password reset mail smile app'
        message = f'Hi, Pleasae click the link below to reset the password \n {link}'

        from_email = settings.EMAIL_HOST_USER  # Sender's email address

        send_mail(subject, message, from_email, [email], fail_silently=False)

        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=100, style={'input': 'password'}, write_only=True)
    password2=serializers.CharField(max_length=100, style={'input': 'password'}, write_only=True)

    class Meta:
        model=MyUser
        fields=["password","password2"]

    def validate(self, attrs):
        try:
            password = attrs.get("password")  
            password2 = attrs.get("password2") 
            uid=self.context.get("uid")
            token=self.context.get("token")
            if password != password2:
                raise serializers.ValidationError("Passwords do not match")
            id=smart_str(urlsafe_base64_decode(uid)) 

            user = MyUser.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("token is not valid or expired")
            user.set_password(password)
            user.save()
            return attrs
        
        except DjangoUnicodeDecodeError :
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError("token is not valid or expired")



class ProfileStep1Serializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile_step1
        exclude = ['id',"user"]

    def create(self, validated_data):
        user = self.context['user']
        validated_data['user'] = user
        return UserProfile_step1.objects.create(**validated_data)
        

class ProfileStep2Serializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile_step2
        exclude = ['id', 'user','step_2']

    def validate(self, data):
        user = self.context['user']

        if not user.profile_step1.step_1:
            raise serializers.ValidationError("Please complete Step 1 before proceeding with Step 2.")

        return data

    def create(self, validated_data):
        user = self.context['user']
        validated_data['user'] = user
        return UserProfile_step2.objects.create(**validated_data)

        

class ProfileStep3Serializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile_step3
        exclude = ['id', 'user','step_3']

    def validate(self, data):
        user = self.context['user']

        if not user.profile_step2.step_2:
            raise serializers.ValidationError("Please complete Step 2 before proceeding with Step 3.")

        return data

    def create(self, validated_data):
        user = self.context['user']
        validated_data['user'] = user
        return UserProfile_step3.objects.create(**validated_data)
        


class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreakSystem
        fields = ['current_streak','longest_streak']


class SmileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSmileModel
        exclude=['user','id','smile_time','best_smile_count','best_smile_day','best_smile_time']


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLevelModel
        fields=['level']



class StatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSmileModel
        fields=['best_smile_day', "best_smile_time"]


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivitiesModel
        fields=['id','activity_name']

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivitiesModel
        fields='__all__'



class DailyQuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyQuoteModel
        fields=['quote']