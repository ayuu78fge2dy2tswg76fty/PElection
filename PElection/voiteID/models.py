import secrets
import string

from django.db import models 




def generate_voting_id():
    while True:
        letters = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(2))
        numbers = ''.join(secrets.choice(string.digits) for _ in range(5))
        voting_id = f"{letters}{numbers}"

        if not ID_DB.objects.filter(_c_id=voting_id).exists():
            return voting_id
        



class ID_DB(models.Model):

    _c_id = models.CharField(primary_key=True,max_length=7,default=generate_voting_id,editable=False,unique=True)
    _is_used = models.BooleanField(default=False)
    _created_at = models.DateTimeField(auto_now_add=True)



    class Meta:
        verbose_name = "ID_"
        verbose_name_plural = "IDYADA"
        ordering = ["_c_id"]

    def __str__(self):
        return self._c_id