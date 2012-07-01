"""Test raw queries with additional attributes"""

from django.test import TestCase

from .models import *
from compositekey.utils import assemble_pk

class TestRawQueries(TestCase):

    def setUp(self):
        CK(k1="a", k2="b", v="c").save()
        CKA(k1="a", k2="b", v="c").save()
        CK2(k1="a", k2="b", v="c").save()
        CKA2(k1="a", k2="b", v="c").save()
        CKN(k1="a", k2="b", v="c").save()
        CKAN(k1="a", k2="b", v="c").save()

    def check(self, model, sql, attr_values):
        x = list(model.objects.raw(sql))[0]
        for (attr, value) in attr_values:
            self.assertEqual(getattr(x, attr), value)


    def test_id_simple(self):
        self.check(CK, "SELECT *, 'Z' as zzz FROM ck", (
            ("id", assemble_pk("a", "b")),
            ("k1", "a"),
            ("k2", "b"),
            ("v", "c"),
            ("zzz", "Z"),
            ))

    def test_id_audit(self):
        self.check(CKA, "SELECT *, 'Z' as zzz FROM cka", (
            ("id", assemble_pk("a", "b")),
            ("k1", "a"),
            ("k2", "b"),
            ("v", "c"),
            ("zzz", "Z"),
            ))

    def test_id_before_simple(self):
        self.check(CK, "SELECT *, 'fake' as id, 'Z' as zzz FROM ck", (
            ("id", assemble_pk("a", "b")),
            ("k1", "a"),
            ("k2", "b"),
            ("v", "c"),
            ("zzz", "Z"),
            ))

    def test_id_before_audit(self):
        self.check(CKA, "SELECT *, 'fake' as id, 'Z' as zzz FROM cka", (
            ("id", assemble_pk("a", "b")),
            ("k1", "a"),
            ("k2", "b"),
            ("v", "c"),
            ("zzz", "Z"),
            ))


    # following uses same db tables as above

    def test_id_before_proxy(self):
        self.check(CKP,
            "SELECT *, 'fake' as id, 'Z' as zzz, 'Y' as yyy FROM cka", (
                ("id", assemble_pk("a", "b")),
                ("k1", "a"),
                ("k2", "b"),
                ("v", "c"),
                ("zzz", "Z"),
                ("yyy", "Y"),
                ))

    def test_id_after_simple(self):
        self.check(CK2,
            "SELECT *, 'fake' as id, 'Z' as zzz, 'Y' as yyy FROM ck2", (
                ("id", assemble_pk("a", "b")),
                ("k1", "a"),
                ("k2", "b"),
                ("v", "c"),
                ("zzz", "Z"),
                ("yyy", "Y"),
                ))

    def test_id_after_audit(self):
        self.check(CKA2,
            "SELECT *, 'fake' as id, 'Z' as zzz, 'Y' as yyy FROM cka2", (
                ("id", assemble_pk("a", "b")),
                ("k1", "a"),
                ("k2", "b"),
                ("v", "c"),
                ("zzz", "Z"),
                ("yyy", "Y"),
                ))

    def test_id_after_proxy(self):
        self.check(CKP2,
            "SELECT *, 'fake' as id, 'Z' as zzz, 'Y' as yyy FROM cka2", (
                ("id", assemble_pk("a", "b")),
                ("k1", "a"),
                ("k2", "b"),
                ("v", "c"),
                ("zzz", "Z"),
                ("yyy", "Y"),
                ))

    def test_id_normal_simple(self):
        self.check(CKN,
            "SELECT *, 'fake' as id, 'Z' as zzz, 'Y' as yyy FROM ckn", (
                ("id", "fake"),
                ("k1", "a"),
                ("k2", "b"),
                ("v", "c"),
                ("zzz", "Z"),
                ("yyy", "Y"),
                ))

    def test_id_normal_audit(self):
        self.check(CKAN,
            "SELECT *, 'fake' as id, 'Z' as zzz, 'Y' as yyy FROM ckan", (
                ("id", "fake"),
                ("k1", "a"),
                ("k2", "b"),
                ("v", "c"),
                ("zzz", "Z"),
                ("yyy", "Y"),
                ))

    def test_id_normal_proxy(self):
        self.check(CKPN,
            "SELECT *, 'fake' as id, 'Z' as zzz, 'Y' as yyy FROM ckan", (
                ("id", "fake"),
                ("k1", "a"),
                ("k2", "b"),
                ("v", "c"),
                ("zzz", "Z"),
                ("yyy", "Y"),
                ))
