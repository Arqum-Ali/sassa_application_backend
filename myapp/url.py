# auth_app/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('login/facebook/', LoginFacebookView.as_view(), name='login_facebook'),
    path('callback/', FacebookCallbackView.as_view(), name='callback'),
    path('adaccounts/<str:account_id>/campaigns/', GetCampaignsView.as_view(), name='get_campaigns'),  # New URL for fetching campaigns
    path('toggle-ad-object/<str:ad_object_id>/', ToggleAdObjectView.as_view(), name='toggle-ad-object'),
    path('update-budget/<str:object_id>/<str:object_type>/', UpdateBudgetView.as_view(), name='update_budget'),



    # path('auth/', initiate_auth, name='initiate_auth'),
    # path('auth/shopify/callback/', auth_callback, name='auth_callback'),
    path('api/start-auth/', StartAuthView.as_view(), name='start-auth'),
    path('api/shopify/callback/', ShopifyCallbackView.as_view(), name='shopify-callback'),

]
