"""
17. Custom column/table names

If your database column name is different than your model attribute, use the
``db_column`` parameter. Note that you'll use the field's name, not its column
name, in API usage.

If your database table name is different than your model name, use the
``db_table`` Meta attribute. This has no effect on the API used to
query the database.

If you need to use a table name for a many-to-many relationship that differs
from the default generated name, use the ``db_table`` parameter on the
``ManyToManyField``. This has no effect on the API for querying the database.

"""

from django.db import models
from compositekey import db

class Author(models.Model):
    id = db.MultipleFieldPrimaryKey(fields=("first_name", "last_name"))
    first_name = models.CharField(max_length=30, db_column='firstname')
    last_name = models.CharField(max_length=30, db_column='last')

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

    class Meta:
        db_table = 'myc_author_table'
        ordering = ('last_name','first_name')

class Article(models.Model):
    headline = models.CharField(max_length=100)
    authors = models.ManyToManyField(Author, db_table='myc_m2m_table')

    def __unicode__(self):
        return self.headline

    class Meta:
        ordering = ('headline',)

