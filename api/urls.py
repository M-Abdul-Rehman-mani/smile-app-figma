from django.urls import path,include
# from .views import UserRegistration,UserLogin,ViewUser,ChangePassword,SendPasswordEmail
from . import views


urlpatterns = [
    path('register/', views.UserRegistration.as_view()),
    path('login/', views.UserLogin.as_view()),
    path('view_user/', views.ViewUser.as_view()),
    path('change_password/', views.ChangePassword.as_view()),
    path('reset_password_mail/', views.SendPasswordEmail.as_view()),
    path('reset_password/<uid>/<token>/', views.ForgotPassword.as_view()),


    path('step_1/', views.ProfileStep1View.as_view()),
    path('step_2/', views.ProfileStep2View.as_view()),
    path('step_3/', views.ProfileStep3View.as_view()),

    path('dashboard/', views.DashboardView.as_view()),
    path('goals/', views.GoalsView.as_view()),
    path('stats/', views.StatsView.as_view()),
    path('activities/', views.ActivitiesView.as_view()),
    path('level/', views.LevelView.as_view()),
    path('daily_quote/', views.DailyQuoteView.as_view()),
    path('smile_exercise/<int:activity_id>/', views.ExerciseView.as_view()),

]
