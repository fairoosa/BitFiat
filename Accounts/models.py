from django.db import models
from django.contrib.auth.models import User



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.user.username
    

class KYC(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="kyc_details")
    pan_number = models.CharField(max_length=10, unique=True)
    user_image = models.ImageField(upload_to='user_images/', null=True, blank=True)
    
    def __str__(self):
        return f"KYC details for {self.user.username}"

    def get_document_name(self):
        return f"kyc_{self.user.username}.jpg"


STATE_CHOICES = [
    ('andhra pradesh', 'Andhra Pradesh'),
    ('arunachal pradesh', 'Arunachal Pradesh'),
    ('assam', 'Assam'),
    ('bihar', 'Bihar'),
    ('chhattisgarh', 'Chhattisgarh'),
    ('goa', 'Goa'),
    ('gujarat', 'Gujarat'),
    ('haryana', 'Haryana'),
    ('himachal pradesh', 'Himachal Pradesh'),
    ('jharkhand', 'Jharkhand'),
    ('karnataka', 'Karnataka'),
    ('kerala', 'Kerala'),
    ('madhya pradesh', 'Madhya Pradesh'),
    ('maharashtra', 'Maharashtra'),
    ('manipur', 'Manipur'),
    ('meghalaya', 'Meghalaya'),
    ('mizoram', 'Mizoram'),
    ('nagaland', 'Nagaland'),
    ('odisha', 'Odisha'),
    ('punjab', 'Punjab'),
    ('rajasthan', 'Rajasthan'),
    ('sikkim', 'Sikkim'),
    ('tamil nadu', 'Tamil Nadu'),
    ('telangana', 'Telangana'),
    ('tripura', 'Tripura'),
    ('uttar pradesh', 'Uttar Pradesh'),
    ('uttarakhand', 'Uttarakhand'),
    ('west bengal', 'West Bengal'),
    ('andaman and nicobar islands', 'Andaman and Nicobar Islands'),
    ('chandigarh', 'Chandigarh'),
    ('dadra and nagar haveli and daman and diu', 'Dadra and Nagar Haveli and Daman and Diu'),
    ('lakshadweep', 'Lakshadweep'),
    ('delhi', 'Delhi'),
    ('puducherry', 'Puducherry'),
    ('jammu & kashmir', 'Jammu & Kashmir'),
    ('ladakh', 'Ladakh')
]


class Address(models.Model):
    userprofile = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    house_flat_apartment = models.CharField(max_length=255)
    road_street = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    state = models.CharField(max_length=100, choices=STATE_CHOICES)
    address_type = models.CharField(
        max_length=10,
        choices=[('home', 'Home'), ('work', 'Work'), ('other', 'Other')],
        default='home',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.house_flat_apartment}-{self.address_type}"


class BankDetails(models.Model):
    user_profile = models.OneToOneField(User, on_delete=models.CASCADE, related_name='bank_details')
    name = models.CharField(max_length=255) 
    vpa = models.CharField(max_length=255, unique=True)  
    merchant_ifsc = models.CharField(max_length=20) 
    tpap = models.JSONField() 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.vpa}"