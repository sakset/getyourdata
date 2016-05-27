from __future__ import unicode_literals

from django.db import models


class Organization(models.Model):
	name = models.CharField(max_length=255)

	# Email contact
	email_address = models.CharField(max_length=255, null=True, blank=True,
							 default="")

	# Postal contact
	address_line_one = models.CharField(max_length=255, null=True, blank=True,
										default="")
	address_line_two = models.CharField(max_length=255, null=True, blank=True,
										default="")
	postal_code = models.CharField(max_length=64, null=True, blank=True,
								   default="")
	country = models.CharField(max_length=64, null=True, blank=True,
							   default="")

	# Has admin verified this organization as having correct information
	verified = models.BooleanField(default=False)

	def __unicode__(self):
		return self.name
