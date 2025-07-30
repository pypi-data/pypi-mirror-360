from django.urls import path

from .views.file import save_file
from ..channels.views import handel_channel
from .views.rest import save_many,delete_many,save_one,delete_one,find_one,find,update,table, tree, meta_view

urlpatterns = [
    path('socket/<str:handler>', handel_channel),
    path('save_many', save_many),
    path('delete_many', delete_many),
    path('<str:db>/<str:entity>/save_one', save_one),
    path('<str:db>/<str:entity>/delete_one', delete_one),
    path('<str:db>/<str:entity>/find_one', find_one),
    path('<str:db>/<str:entity>/find', find),
    path('<str:db>/<str:entity>/update', update),
    path('<str:db>/<str:entity>/table', table),
    path('<str:db>/<str:entity>/tree', tree),
    path('<str:db>/<str:entity>/meta_view', meta_view),

    path('<str:db>/<str:entity>/save_file', save_file),


]