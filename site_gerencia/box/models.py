#!/usr/bin/env python

from django.db import models
from fields import MACAddressField
# Create your models here.


class SetupBox(models.Model):
    mac = MACAddressField()


