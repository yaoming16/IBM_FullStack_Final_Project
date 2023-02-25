from django.contrib import admin
from .models import  CarMake, CarModel


# Register your models here.

# CarModelInline class
class CarModelInlineInline(admin.StackedInline):
    model = CarModel
    extra = 0

# CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
    list_display = ['name','carMake','dealerId','year','carType']
    list_filter = ['dealerId','year','carType']
    search_fields = ['name','year','carType']

# CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInlineInline]
    list_display = ['name','description']

# Register models here
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)
