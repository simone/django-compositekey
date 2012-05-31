"""Test raw queries with additional attributes"""

from django.test import TestCase

from .models import *

class TestRawQueries(TestCase):

    def setUp(self):
        CK(k1="a", k2="b", v="c").save()
        CKA(k1="a", k2="b", v="c").save()

    def check(self, model, sql, attr_values):
        x = list(model.objects.raw(sql))[0]
        for (attr, value) in attr_values:
            self.assertEqual(getattr(x, attr), value)

    def test_id_before_simple(self):
        self.check(CK, "SELECT *, 'fake' as id, 'Z' as zzz FROM ck", (
            ("id", "a-b"),
            ("k1", "a"),
            ("k2", "b"),
            ("v", "c"),
            ("zzz", "Z"),
        ))

    def test_id_before_audit(self):
        self.check(CKA, "SELECT *, 'fake' as id, 'Z' as zzz FROM cka", (
            ("id", "a-b"),
            ("k1", "a"),
            ("k2", "b"),
            ("v", "c"),
            ("zzz", "Z"),
        ))

    # following uses same db tables as above

    def test_id_before_proxy(self):
        self.check(CKP,
            "SELECT *, 'fake' as id, 'Z' as zzz, 'Y' as yyy FROM cka", (
            ("id", "a-b"),
            ("k1", "a"),
            ("k2", "b"),
            ("v", "c"),
            ("zzz", "Z"),
            ("yyy", "Y"),
        ))

    def test_id_after_simple(self):
        self.check(CK2,
            "SELECT *, 'fake' as id, 'Z' as zzz, 'Y' as yyy FROM ck", (
            ("id", "a-b"),
            ("k1", "a"),
            ("k2", "b"),
            ("v", "c"),
            ("zzz", "Z"),
            ("yyy", "Y"),
        ))

    def test_id_after_audit(self):
        self.check(CKA2,
            "SELECT *, 'fake' as id, 'Z' as zzz, 'Y' as yyy FROM cka", (
            ("id", "a-b"),
            ("k1", "a"),
            ("k2", "b"),
            ("v", "c"),
            ("zzz", "Z"),
            ("yyy", "Y"),
        ))
