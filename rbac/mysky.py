from .models import *

from mysky.service.sites import site,ModelMysky

site.register(User)
site.register(Role)



class PermissionConfig(ModelMysky):
    list_display = ['title','url','code']

site.register(Permission,PermissionConfig)

