from django.db import models
from compositekey import db

setattr(models, "CompositeField", db.MultiFieldPK)
