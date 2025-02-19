from django.contrib import admin
from .models import UserProfile, KYC, Address, BankDetails



admin.site.register(UserProfile)
admin.site.register(KYC)
admin.site.register(Address)
admin.site.register(BankDetails)


