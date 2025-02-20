# accounts/urls.py

from django.urls import path

from . import auth
from . import category
from . import link
from . import share
from . import user
from . import views

urlpatterns = [
    path('', views.index),

    path('auth/refresh', auth.refresh),
    path('auth/sign-in', auth.sign_in),
    path('auth/sign-out', auth.sign_out),
    path('auth/sign-up', auth.sign_up),

    path('api/categories', category.get_categories),

    path('api/link', link.add_link),
    path('api/links', link.get_links),
    path('api/link/<str:link_id>', link.remove_update_link),

    path('api/share', share.add_share),
    path('api/shares', share.add_shares),
    path('api/shares/<str:link_id>', share.get_shares),
    path('api/share/<str:share_id>', share.remove_update_share),

    path('api/users', user.get_users),
]
