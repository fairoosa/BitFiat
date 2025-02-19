import re
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import UserProfile, KYC, Address, BankDetails



class UserProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='username') 
    name = serializers.CharField(source='first_name') 

    class Meta:
        model = User
        fields = ['phone_number', 'name', 'email', 'password']

    def validate_phone_number(self, value):
        phone_regex = r'^\+?\d{10,15}$'  
        if not re.match(phone_regex, value):
            raise serializers.ValidationError("Invalid phone number format. It should be 10-15 digits.")

        if User.objects.filter(username=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("This phone number is already registered.")
        
        return value

    def validate_email(self, value):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise serializers.ValidationError("Invalid email format.")
        
        if User.objects.filter(email=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value
        

    def create(self, validated_data):
        phone_number = validated_data.pop('username')  
        name = validated_data.pop('first_name')
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            username=phone_number,  
            email=email,
            first_name=name,
            password=password
        )
        user_profile = UserProfile.objects.create(user=user)
        return user
    
    def update(self, instance, validated_data):
        user_profile = instance.userprofile 

        new_phone_number = validated_data.get('username')
        if new_phone_number and new_phone_number != instance.username:
            user_profile.is_verified = False

        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.email = validated_data.get('email', instance.email)

        instance.save()
        user_profile.save()

        return instance


class OtpVerificationSerializer(serializers.ModelSerializer):
    is_verified = serializers.BooleanField()

    class Meta:
        model = UserProfile
        fields = ['is_verified']

    def create(self, validated_data):
        is_verified = validated_data.get('is_verified')
        request = self.context.get('request')
        user = request.user
        try:
            userprofile = UserProfile.objects.get(user = user)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("UserProfile profile not found for this user.")
        
        userprofile.is_verified = is_verified
        userprofile.save()

        return userprofile


class KYCPanSerializer(serializers.ModelSerializer):
    pan_number = serializers.CharField(max_length=10, min_length=10)

    class Meta:
        model = KYC
        fields = ['pan_number']

    def validate_pan_number(self, value):
        # PAN number validation (simple pattern: 5 letters, 4 digits, 1 letter)
        pan_pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"
        if not re.match(pan_pattern, value):
            raise serializers.ValidationError("Invalid PAN number format. It should be in the format: ABCDE1234F")
        if KYC.objects.filter(pan_number=value).exists():
            raise serializers.ValidationError("This PAN Number is already in use.")
        return value
    
    def create(self, validated_data):
        pan_number = validated_data.get('pan_number')
        request = self.context.get('request')
        user = request.user

        kyc_pan = KYC.objects.create(
            user = user,
            pan_number = pan_number
        )

        return kyc_pan
    

class KYCImageSerializer(serializers.ModelSerializer):
    user_image = serializers.ImageField(required = True)

    class Meta:
        model = KYC
        fields = ['user_image']

    def create(self, validated_data):
        user_image = validated_data.get('user_image')
        request = self.context.get('request')
        user = request.user
        try:
            kyc = KYC.objects.get(user=user)
        except KYC.DoesNotExist:
            raise serializers.ValidationError("KYC profile not found for this user.")
        
        kyc.user_image = user_image
        kyc.save()

        return kyc


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

    def validate_phone_number(self, value):
        phone_regex = r'^\+?\d{10,15}$'  
        if not re.match(phone_regex, value):
            raise ValidationError("Invalid phone number format. It should be 10-15 digits.")

        if not  User.objects.filter(username=value).exists():
            raise ValidationError("This phone number is not registered.")
        
        return value


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("The  passwords do not match.")
        return data
    

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['house_flat_apartment','road_street','landmark','city','pincode', 'state', 'address_type']

    def validate_pincode(self, value):
        if not re.match(r'^\d{6}$', value): 
            raise serializers.ValidationError("Pincode must be exactly 6 digits.")
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        address = Address.objects.create(userprofile=user, **validated_data)
        return address
    

class BankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetails
        fields = '__all__'