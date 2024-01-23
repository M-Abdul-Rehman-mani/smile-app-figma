from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (UserRegistrationSerializer, UserLoginSerializer,UserProfileSerializer,ChangePasswordSerializer,SendPasswordMailSerializer,ForgotPasswordSerializer,ExerciseSerializer,
                           ProfileStep1Serializer,ProfileStep2Serializer,ProfileStep3Serializer,DashboardSerializer, SmileSerializer,LevelSerializer,StatsSerializer, ActivitySerializer,DailyQuoteSerializer)
from rest_framework.permissions import IsAuthenticated
from .models import MyUser, StreakSystem, UserSmileModel,UserLevelModel,ActivitiesModel,DailyQuoteModel
from datetime import datetime
from django.utils import timezone 
import time
# Create your views here.


#generate token manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

    
class UserRegistration(APIView):
    def post(self, request, format=None):
        serializer=UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.save()
        token=get_tokens_for_user(user)
        return Response({"token":token,"msg":"registration successfull" },status=status.HTTP_201_CREATED)
    

class UserLogin(APIView):
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            try:
                user = MyUser.objects.get(email=email)
            except MyUser.DoesNotExist:
                return Response({"errors": {'non_field_errors': ['This email is not registered.']}}, status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(request, email=email, password=password)

            if user is not None:
                token=get_tokens_for_user(user)

                #streak system
                streak,created = StreakSystem.objects.get_or_create(user=user) 
                streak.update_streak(datetime.now().date())
                return Response({"token":token,"msg": "Login successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"errors": {'non_field_errors': ['Email or password is not valid']}}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ViewUser(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)  
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = ChangePasswordSerializer(data=request.data, context={"user": request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({"msg": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class SendPasswordEmail(APIView):
    def post(self, request, format=None):
        serializer =SendPasswordMailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({"msg": "Password reset link has been sent successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ForgotPassword(APIView):
    def post(self, request,uid, token, format=None):
        serializer =ForgotPasswordSerializer(data=request.data,context={"uid":uid, "token":token})
        if serializer.is_valid(raise_exception=True):
            return Response({"msg": "Password reset successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

#profile setup
class ProfileStep1View(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = ProfileStep1Serializer(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"msg": "Step 1 completed "}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProfileStep2View(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = ProfileStep2Serializer(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"msg": "Step 2 completed "}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProfileStep3View(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = ProfileStep3Serializer(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"msg": "Step 3 completed "}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


#dashboard
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            streak = StreakSystem.objects.get(user=request.user)
            smile = UserSmileModel.objects.get(user=request.user)

            streak_serializer = DashboardSerializer(streak)
            smile_serializer = SmileSerializer(smile)

            response_data = {
                'streak_data': streak_serializer.data,
                'smile_data': smile_serializer.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except StreakSystem.DoesNotExist:
            return Response({"error": "streak not found"}, status=status.HTTP_404_NOT_FOUND)


    def post(self, request, format=None):
        serializer = SmileSerializer(data=request.data)
        user = request.user

        if serializer.is_valid():
            if 'start_time' not in request.session:
                # if start_time is not in session
                request.session['start_time'] = time.time()
                context = {'message': 'Smiling started'}
            else:
                # if start_time is already in session calculate total time
                end_time = time.time()
                start_time = request.session['start_time']
                total_time = end_time - start_time

                # remove start_time from session to reset the time
                del request.session['start_time']

                # update smile count and time
                smile, created = UserSmileModel.objects.get_or_create(user=user)
                current_time = timezone.now()

                if created or smile.smile_time.date() != current_time.date():
                    # if a new instance was created or the date is different set the initial values
                    smile.smile_time = current_time
                    smile.total_smile_time=total_time
                    smile.smile_count = 1
                    if total_time > smile.best_smile_time:
                        smile.best_smile_time =total_time
                else:
                    # if the instance already existed and the date is the same update the values
                    smile.smile_time = current_time
                    smile.total_smile_time+=total_time
                    smile.smile_count += 1
                    if total_time > smile.best_smile_time:
                        smile.best_smile_time =total_time

                smile.save()
                context = {'message': 'Smile recorded', 'smile_seconds': int(total_time)}

            return Response(context, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoalsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user=request.user
        user_smile_data = UserSmileModel.objects.get(user=user)
        user_streak_data = StreakSystem.objects.get(user=user)
        user_level_data = UserLevelModel.objects.get(user=user)

        serializer = SmileSerializer(user_smile_data)
        streak_serializer = DashboardSerializer(user_streak_data)
        level_serializer = LevelSerializer(user_level_data)

        response_data = [streak_serializer.data,serializer.data,level_serializer.data]

        return Response(response_data, status=status.HTTP_200_OK)

 


class StatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user=request.user
        user_smile_data = UserSmileModel.objects.get(user=user)
        user_streak_data = StreakSystem.objects.get(user=user)

        serializer = StatsSerializer(user_smile_data)
        streak_serializer = DashboardSerializer(user_streak_data)

        averaage=user_smile_data.calculate_average_smile()

        response_data = [streak_serializer.data,serializer.data,{"average smile duration":averaage}]

        return Response(response_data, status=status.HTTP_200_OK)



class ActivitiesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        data = ActivitiesModel.objects.all()
        serializer = ActivitySerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExerciseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, activity_id, format=None):
        try:
            data = ActivitiesModel.objects.get(id=activity_id)
            serializer = ExerciseSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ActivitiesModel.DoesNotExist:
            return Response({"error": "Activity not found"}, status=status.HTTP_404_NOT_FOUND)
        

class LevelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            user_level = UserLevelModel.objects.get(user=request.user)
            total_steps = user_level.prev_step + 2
            custom_data = {
                'level': user_level.level,
                'goals completed ': user_level.steps,
                'goals requird to complete level': total_steps,
            }

            return Response(custom_data, status=status.HTTP_200_OK)
        except UserLevelModel.DoesNotExist:
            return Response({"error": "User level not found"}, status=status.HTTP_404_NOT_FOUND)
        


class DailyQuoteView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, format=None):
        quote = DailyQuoteModel.objects.order_by('?').first()
        serializer = DailyQuoteSerializer(quote)
        return Response(serializer.data, status=status.HTTP_200_OK)

