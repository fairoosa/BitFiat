import re
import uuid
import requests
from django.shortcuts import render
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile, KYC, BankDetails
from .serializers import UserProfileSerializer, OtpVerificationSerializer, KYCPanSerializer, KYCImageSerializer, PhoneNumberSerializer, PasswordSerializer, AddressSerializer, BankDetailsSerializer



class UserProfileCreateAPIView(APIView):
    def post(self, request):
        print("data_1:", request.data)
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  
            token, created = Token.objects.get_or_create(user=user)

            response_data = {
                "user_profile": UserProfileSerializer(user).data,
                "token": token.key
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]  

    def put(self, request):
        user = request.user  
        serializer = UserProfileSerializer(user, data=request.data, partial=True)  

        if serializer.is_valid():
            updated_user = serializer.save()  
            user_profile = updated_user.userprofile
            user_profile = updated_user.userprofile
            response_data = {
                "message": "Profile updated successfully",
                "user_profile": serializer.data,
                "is_verified": user_profile.is_verified  # Add is_verified field
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    def validate_phone_number(self, value):
        phone_regex = r'^\+?\d{10,15}$'  
        if not re.match(phone_regex, value):
            raise ValidationError("Invalid phone number format. It should be 10-15 digits.")
        return value
    
    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')

        if not phone_number or not password:
            return Response({"detail" : "Phone number and password are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            self.validate_phone_number(phone_number)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=phone_number, password=password)
        
        if user is not None:
            user_profile = UserProfile.objects.get(user=user)
            if user_profile.is_verified:
                token, created = Token.objects.get_or_create(user=user)

                return Response({
                    'token':token.key},
                    status =status.HTTP_200_OK) 
            else:
                return Response({
                 "detail": "Phone number is not verified."},
                status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response({
                 "detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED)
        

class OtpVerificationAPIView(APIView):
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated] 
    def post(self, request):
        serializer = OtpVerificationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            userprofile = serializer.save()
            response_data = {
                "userprofile": OtpVerificationSerializer(userprofile).data
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class KYCPanAPIView(APIView):
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        serializer = KYCPanSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            kyc_pan = serializer.save()
            response_data = {
                "kyc_pan" :  KYCPanSerializer(kyc_pan).data
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class KYCImageAPIView(APIView):
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        serializer = KYCImageSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            kyc_img = serializer.save()
            response_data = {
                'kyc_img' : KYCImageSerializer(kyc_img).data
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PhoneNumbrAPIView(APIView):
    def post(self, request):
        serializer = PhoneNumberSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            user = User.objects.get(username = phone_number)

            token, created = Token.objects.get_or_create(user=user)

            response_data = {
                'token': token.key
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PasswordAPIView(APIView):
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated] 
    
    def post(self, request):
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data['password']

            user = request.user
            print("user:", user)
            user.set_password(password)
            user.save()
            return Response({"message": "Password has been updated successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressAPIView(APIView):
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated] 
    def post(self, request):
        serializer = AddressSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            address = serializer.save()

            response_data = {
                "address": AddressSerializer(address).data
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


DECENTRO_BASE_URL = "https://in.staging.decentro.tech/v2/financial_services/mobile_to_vpa/advance"
CLIENT_ID = "Kaiztren_0_sop"
CLIENT_SECRET = "e67052de696541a28bb545f185a02af5"
MODULE_SECRET = "HmNIAyKZOq3cH82Z24rIZ6QxI9uk2KTX" 

def generate_reference_id():
    return str(uuid.uuid4())

class FetchBankDetailsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reference_id = generate_reference_id()
        user = request.user
        phone_number = user.username

        headers = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "module_secret": MODULE_SECRET,
            "Content-Type": "application/json"
        }
        payload = {
            "reference_id": reference_id,
            "consent": True,
            "purpose": "Fetch user VPA from mobile number",
            "mobile": phone_number
        }

        try:
            response = requests.post(DECENTRO_BASE_URL, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return Response({
                "reference_id": reference_id,
                "error": f"Failed to connect to Decentro API: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = response.json()
        print("Decentro API Response:", data)
        accounts = data.get("data", {}).get("results", [])

        if not accounts:
            return Response({
                "reference_id": reference_id,
                "error": "No bank details found for this phone number."
            }, status=status.HTTP_400_BAD_REQUEST)

        all_bank_details = []

        for account_info in accounts:
            name = account_info.get("name", "")
            vpa = account_info.get("vpa", "")
            merchant_ifsc = account_info.get("merchantIfsc", "")
            tpap = account_info.get("tpap", [])

            bank_details, created = BankDetails.objects.update_or_create(
                user_profile=user,
                vpa=vpa,  
                defaults={
                    "name": name,
                    "merchant_ifsc": merchant_ifsc,
                    "tpap": ", ".join(tpap) if tpap else None
                }
            )

            all_bank_details.append({
                "reference_id": reference_id,
                "name": name,
                "vpa": vpa,
                "merchant_ifsc": merchant_ifsc,
                "tpap": tpap
            })

        return Response({
            "message": "Bank details fetched successfully",
            "bank_details": all_bank_details
        }, status=status.HTTP_200_OK)
    


