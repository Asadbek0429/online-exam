from django.urls import path
from .views import TestViewSet, QuestionViewSet, OptionViewSet, TestStatsViewSet

urlpatterns = [
    # test
    path('test/', TestViewSet.as_view({'get': 'get_tests', 'post': 'create_test'}), name='create_test'),
    path('test/<int:pk>/', TestViewSet.as_view({'get': 'get_test', 'patch': 'update_test', 'delete': 'delete_test'}),
         name='update_test'),
    path('test/start/<int:pk>/', TestViewSet.as_view({'post': 'start_test'})),
    path('test/take/', TestViewSet.as_view({'post': 'take_test'})),
    path('test/stats/user/', TestStatsViewSet.as_view({'get': 'get_by_user'})),
    path('test/stats/<int:pk>/', TestStatsViewSet.as_view({'get': 'get_by_test'})),

    # question
    path('question/', QuestionViewSet.as_view({'get': 'get_questions', 'post': 'create_question'}),
         name='create_question'),
    path('question/<int:pk>/',
         QuestionViewSet.as_view({'get': 'get_question', 'patch': 'update_question', 'delete': 'delete_question'}),
         name='update_question'),

    # option
    path('option/', OptionViewSet.as_view({'get': 'get_options', 'post': 'create_option'}),
         name='create_option'),
    path('option/<int:pk>/',
         OptionViewSet.as_view({'get': 'get_option', 'patch': 'update_option', 'delete': 'delete_option'}),
         name='update_Option'),
]
