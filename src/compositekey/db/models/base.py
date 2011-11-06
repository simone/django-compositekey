__author__ = 'aldaran'

from django.db.models import signals
from django.db.models.base import ModelState, Model
from django.db.models.fields.related import ManyToOneRel
from django.db.models.query_utils import DeferredAttribute

from itertools import izip

def patched_model_init(self, *args, **kwargs):
    signals.pre_init.send(sender=self.__class__, args=args, kwargs=kwargs)

    if len(args)<len(self._meta.fields):
        for value, f in zip(args, self._meta.db_fields):
            kwargs.update({f.attname:value})
        args = []

    # Set up the storage for instance state
    self._state = ModelState()

    # There is a rather weird disparity here; if kwargs, it's set, then args
    # overrides it. It should be one or the other; don't duplicate the work
    # The reason for the kwargs check is that standard iterator passes in by
    # args, and instantiation for iteration is 33% faster.
    args_len = len(args)
    if args_len > len(self._meta.fields):
        # Daft, but matches old exception sans the err msg.
        raise IndexError("Number of args exceeds number of fields")

    fields_iter = iter(self._meta.db_fields)
    if not kwargs:
        # The ordering of the izip calls matter - izip throws StopIteration
        # when an iter throws it. So if the first iter throws it, the second
        # is *not* consumed. We rely on this, so don't change the order
        # without changing the logic.
        for val, field in izip(args, fields_iter):
            setattr(self, field.attname, val)
    else:
        # Slower, kwargs-ready version.
        for val, field in izip(args, fields_iter):
            setattr(self, field.attname, val)
            kwargs.pop(field.name, None)
            # Maintain compatibility with existing calls.
            if isinstance(field.rel, ManyToOneRel):
                kwargs.pop(field.attname, None)

    # Now we're left with the unprocessed fields that *must* come from
    # keywords, or default.

    for field in fields_iter:
        is_related_object = False
        # This slightly odd construct is so that we can access any
        # data-descriptor object (DeferredAttribute) without triggering its
        # __get__ method.
        if (field.attname not in kwargs and
                isinstance(self.__class__.__dict__.get(field.attname), DeferredAttribute)):
            # This field will be populated on request.
            continue
        if kwargs:
            if isinstance(field.rel, ManyToOneRel):
                try:
                    # Assume object instance was passed in.
                    rel_obj = kwargs.pop(field.name)
                    is_related_object = True
                except KeyError:
                    try:
                        # Object instance wasn't passed in -- must be an ID.
                        val = kwargs.pop(field.attname)
                    except KeyError:
                        val = field.get_default()
                else:
                    # Object instance was passed in. Special case: You can
                    # pass in "None" for related objects if it's allowed.
                    if rel_obj is None and field.null:
                        val = None
            else:
                try:
                    val = kwargs.pop(field.attname)
                except KeyError:
                    # This is done with an exception rather than the
                    # default argument on pop because we don't want
                    # get_default() to be evaluated, and then not used.
                    # Refs #12057.
                    val = field.get_default()
        else:
            val = field.get_default()
        if is_related_object:
            # If we are passed a related instance, set it using the
            # field.name instead of field.attname (e.g. "user" instead of
            # "user_id") so that the object gets properly cached (and type
            # checked) by the RelatedObjectDescriptor.
            setattr(self, field.name, rel_obj)
        else:
            setattr(self, field.attname, val)

    if kwargs:
        for prop in kwargs.keys():
            try:
                if hasattr(getattr(self.__class__, prop), "__set__"):
                    setattr(self, prop, kwargs.pop(prop))
            except AttributeError:
                pass
        if kwargs:
            raise TypeError("'%s' is an invalid keyword argument for this function" % kwargs.keys()[0])
    super(Model, self).__init__()

    # setup pk cache
    self.pk
    
    signals.post_init.send(sender=self.__class__, instance=self)
patched_model_init._sign = "composite"
