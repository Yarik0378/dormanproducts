from django.db import models
from django.urls import reverse


# Non Processed
# Processing
# Done


class Project(models.Model):
    uploaded_file = models.FileField(upload_to='documents/')
    result_file = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    date = models.DateTimeField()
    len_codes = models.CharField(max_length=50)
    finished_codes = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'document'
        verbose_name_plural = 'documents'
