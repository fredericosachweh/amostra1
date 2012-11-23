# -*- encoding:utf-8 -*-


from django.contrib.admin import site
import models


site.register(models.SetTopBox)
site.register(models.SetTopBoxParameter)
site.register(models.SetTopBoxChannel)
