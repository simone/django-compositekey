from django.db import models
from compositekey.db import MultiFieldPK

# id going before the model fields

class CK(models.Model):
    id = MultiFieldPK("k1", "k2")

    k1 = models.CharField(max_length=100)
    k2 = models.CharField(max_length=100)

    v = models.CharField(max_length=100)

    zzz = None

    class Meta:
        db_table = "ck"


class WithAudit(models.Model):
    created_by = models.SmallIntegerField(editable=False, null=True, blank=True)
    created_on = models.DateTimeField(editable=False, null=True, blank=True)
    updated_by = models.SmallIntegerField(editable=False, null=True, blank=True)
    updated_on = models.DateTimeField(editable=False, null=True, blank=True)

    class Meta:
        abstract = True


class CKA(WithAudit):
    id = MultiFieldPK("k1", "k2")

    k1 = models.CharField(max_length=100)
    k2 = models.CharField(max_length=100)

    v = models.CharField(max_length=100)

    zzz = None

    class Meta:
        db_table = "cka"


class CKP(CKA):
    class Meta:
        proxy = True

    yyy = None


# id going after the model fields

class CK2(models.Model):
    k1 = models.CharField(max_length=100)
    k2 = models.CharField(max_length=100)

    v = models.CharField(max_length=100)

    id = MultiFieldPK("k1", "k2")

    zzz = None

    class Meta:
        db_table = "ck2"


class CKA2(WithAudit):

    v = models.CharField(max_length=100)

    k1 = models.CharField(max_length=100)
    k2 = models.CharField(max_length=100)

    id = MultiFieldPK("k1", "k2")

    zzz = None

    class Meta:
        db_table = "cka2"


