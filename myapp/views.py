# facebook_ads/views.py
from django.conf import settings

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import FacebookAccessToken
from .serializers import AdAccountSerializer
import requests
# auth_app/views.py

import os
import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
# from dotenv import load_dotenv

# load_dotenv()  # Load environment variables from a .env file

# FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
# FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET")
# FACEBOOK_REDIRECT_URI = os.getenv("FACEBOOK_REDIRECT_URI")
# auth_app/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from .serializers import AdAccountSerializer  # Import the serializer

class LoginFacebookView(APIView):
    def get(self, request):
        # Redirect user to Facebook's OAuth login page with additional permissions
        facebook_auth_url = (
            f"https://www.facebook.com/v13.0/dialog/oauth?client_id={settings.FACEBOOK_APP_ID}"
            f"&redirect_uri={settings.FACEBOOK_REDIRECT_URI}&scope=email,ads_read,ads_management,public_profile"
        )
        response_data = {"redirect_url": facebook_auth_url}
        print("Response data--------------------------------:", response_data)  # This will help you see if the URL is there
        return Response(response_data)
        # return Response({"redirect_url": facebook_auth_url})

class FacebookCallbackView(APIView):
    def get(self, request):
        code = request.GET.get("code")
        token_url = "https://graph.facebook.com/v13.0/oauth/access_token"
        params = {
            "client_id": settings.FACEBOOK_APP_ID,
            "redirect_uri": settings.FACEBOOK_REDIRECT_URI,
            "client_secret": settings.FACEBOOK_APP_SECRET,
            "code": code,
        }

        # Get the access token
        response = requests.get(token_url, params=params)
        access_token_info = response.json()

        if "access_token" in access_token_info:
            access_token = access_token_info["access_token"]

            # Fetch Facebook Ads accounts using the access token
            ads_url = "https://graph.facebook.com/v13.0/me/adaccounts"
            ads_response = requests.get(ads_url, params={"access_token": access_token})

            # Check if the request to get ads data was successful
            if ads_response.status_code == 200:
                ads_data = ads_response.json()
                
                # Log or print the ads_data for debugging
                print("ads_data--------------",ads_data)

                serializer = AdAccountSerializer(ads_data["data"], many=True)

                return Response({
                    "access_token": access_token,
                    "ads_data": serializer.data
                })
            else:
                return Response({
                    "error": "Failed to retrieve ads data",
                    "details": ads_response.json()
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Failed to retrieve access token", "details": access_token_info}, status=status.HTTP_400_BAD_REQUEST)
class GetCampaignsView(APIView):
    def get(self, request, account_id):
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(' ')[1]

        # access_token = request.GET.get("access_token")  # Retrieve the access token
        start_date = request.GET.get("startDate")
        end_date = request.GET.get("endDate")
        print("account_id",account_id)
        print("access_token",access_token)
        campaigns_url = f"https://graph.facebook.com/v20.0/{account_id}/campaigns"
        print("campaigns_url---",campaigns_url)
        params = {
            "access_token": access_token,
            "fields": "id,daily_budget,name,lifetime_budget,status,delivery,insights{actions,clicks,frequency,impressions,reach,spend,social_spend,purchase_roas,website_purchase_roas,cpc,cpm,quality_ranking,engagement_rate_ranking,ctr},adsets{name},ads{id},updated_time",
            "time_range": {"since": start_date, "until": end_date} if start_date and end_date else {}
        }
        
        campaigns_response = requests.get(campaigns_url, params=params)
        print("campaigns_response-------------------------",campaigns_response.json())
        if campaigns_response.status_code == 200:
            campaigns_data = campaigns_response.json()
            return Response(campaigns_data)
        else:
            return Response({
                "error": "Failed to retrieve campaigns",
                "details": campaigns_response.json()
            }, status=status.HTTP_400_BAD_REQUEST)



class ToggleAdObjectView(APIView):
    def post(self, request, ad_object_id):
        """
        Toggle the status of a campaign, ad set, or ad.

        Parameters:
        - ad_object_id: ID of the campaign, ad set, or ad to toggle
        - The request body should contain:
            - 'access_token': Facebook access token
            - 'object_type': 'campaign', 'adset', or 'ad'
            - 'status': The desired status ('ACTIVE' or 'PAUSED')
        """
        
        access_token = request.data.get("access_token")  # Retrieve the access token
        object_type = request.data.get("object_type")    # Type of the object: campaign, adset, or ad
        status_update = request.data.get("status")       # The desired status: ACTIVE or PAUSED
        
        # Validate input parameters
        if not access_token or not object_type or not status_update:
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)
        
        if object_type not in ["campaign", "adset", "ad"]:
            return Response({"error": "Invalid object type. Use 'campaign', 'adset', or 'ad'."}, status=status.HTTP_400_BAD_REQUEST)
        
        if status_update not in ["ACTIVE", "PAUSED"]:
            return Response({"error": "Invalid status. Use 'ACTIVE' or 'PAUSED'."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Construct the URL for updating the status
        toggle_url = f"https://graph.facebook.com/v13.0/{ad_object_id}"
        params = {
            "access_token": access_token,
            "status": status_update
        }

        # Send the request to update the status
        toggle_response = requests.post(toggle_url, params=params)
        
        if toggle_response.status_code == 200:
            return Response({"message": f"Successfully updated the status of the {object_type}.", "data": toggle_response.json()})
        else:
            return Response({
                "error": "Failed to update the status",
                "details": toggle_response.json()
            }, status=status.HTTP_400_BAD_REQUEST)
# facebook_ads/views.py

class UpdateBudgetView(APIView):
    def post(self, request, object_id, object_type):
        """
        Updates the budget for a campaign or ad set in real-time.
        
        Parameters:
        - object_id: ID of the campaign or ad set
        - object_type: 'campaign' or 'adset'
        
        The request body should contain:
        - 'access_token': Facebook access token
        - 'budget': The new budget value in cents
        - 'budget_type': The type of budget ('daily_budget' or 'lifetime_budget')
        """
        
        access_token = request.data.get("access_token")  # Retrieve the access token
        budget = request.data.get("budget")  # The new budget value (in cents)
        budget_type = request.data.get("budget_type")  # The type of budget ('daily_budget' or 'lifetime_budget')
        
        if not access_token or not budget or not budget_type:
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)
        
        if object_type not in ["campaign", "adset"]:
            return Response({"error": "Invalid object type. Use 'campaign' or 'adset'."}, status=status.HTTP_400_BAD_REQUEST)
        
        # The URL for updating a campaign or ad set
        update_url = f"https://graph.facebook.com/v13.0/{object_id}"
        
        # Prepare the data to update
        data = {
            "access_token": access_token,
            budget_type: budget  # Set either the daily_budget or lifetime_budget
        }
        
        # Send the request to update the budget
        response = requests.post(update_url, data=data)
        
        if response.status_code == 200:
            return Response({"message": "Budget updated successfully.", "data": response.json()})
        else:
            return Response({
                "error": "Failed to update the budget",
                "details": response.json()
            }, status=status.HTTP_400_BAD_REQUEST)




































from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
import requests
import os

# API_KEY = 'your_api_key'  # Replace with your Shopify API key
# API_SECRET = 'your_api_secret'  # Replace with your Shopify API secret
SCOPES = 'read_products,read_orders,read_fulfillments,read_customers'  # Add your required scopes here
# REDIRECT_URI = 'https://yourapp.com/api/shopify/callback'  # Your app's callback URL




 
class StartAuthView(APIView):
    def get(self, request):
        shop_name = request.query_params.get('shop')
        if not shop_name:
            return Response({"error": "Shop name is required"}, status=status.HTTP_400_BAD_REQUEST)
        print("shop_name",shop_name)
        # Construct the Shopify OAuth URL
        shopify_auth_url = f"https://{shop_name}.myshopify.com/admin/oauth/authorize"
        state = "random_string_to_prevent_csrf"
          # Generate a unique string for each session

        # Redirect user to Shopify's OAuth authorization page
        full_url = f"{shopify_auth_url}?client_id={settings.SHOPIFY_API_KEY}&scope={SCOPES}&redirect_uri={settings.SHOPIFY_APP_URL}&state={state}"
        return Response({"redirect_url": full_url})

class ShopifyCallbackView(APIView):
    def get(self, request):
        shop_name = request.query_params.get('shop')
        code = request.query_params.get('code')
        state = request.query_params.get('state')

        # Exchange the authorization code for an access token
        print("shop_name---------------",shop_name)
        token_url = f"https://{shop_name}/admin/oauth/access_token"
        payload = {
            'client_id': settings.SHOPIFY_API_KEY,
            'client_secret':settings.SHOPIFY_API_SECRET,
            'code': code
        }

        response = requests.post(token_url, json=payload)
        access_token = response.json().get('access_token')

        if access_token:
            # Store the access token in your database or session for further API calls
            # For demonstration, we just return it in the response
            return Response({"access_token": access_token, "shop": shop_name}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to retrieve access token"}, status=status.HTTP_400_BAD_REQUEST)
