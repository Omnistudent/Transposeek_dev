from django.urls import path
from . import views
urlpatterns = [
    path('',views.home,name="home"),
    #path('<int:year>/<str:month>',views.home,name="home"),
    #path('events',views.all_events,name="list-events"),
    path('help',views.help,name="help"),
    path('editmap',views.editmap,name="editmap"),
    path('managegenomes',views.managegenomes,name="managegenomes"),
    path('editSettings',views.editSettings,name="editSettings"),
    #path('grid',views.grid,name="grid"),
    path('delete_inactive_temp_users',views.delete_inactive_temp_users,name="delete_inactive_temp_users"),
]
