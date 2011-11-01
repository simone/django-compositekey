from django.db.models.sql.datastructures import MultiJoin

__author__ = 'aldaran'

from django.db.models.sql.query import Query, get_proxied_model
from django.core.exceptions import FieldError
from django.db.models.fields import FieldDoesNotExist

__all__ = ["CompositeQuery"]

class CompositeQuery(Query):
    def setup_joins(self, names, opts, alias, dupe_multis, allow_many=True,
            allow_explicit_fk=False, can_reuse=None, negate=False,
            process_extras=True):
        """
        Compute the necessary table joins for the passage through the fields
        given in 'names'. 'opts' is the Options class for the current model
        (which gives the table we are joining to), 'alias' is the alias for the
        table we are joining to. If dupe_multis is True, any many-to-many or
        many-to-one joins will always create a new alias (necessary for
        disjunctive filters). If can_reuse is not None, it's a list of aliases
        that can be reused in these joins (nothing else can be reused in this
        case). Finally, 'negate' is used in the same sense as for add_filter()
        -- it indicates an exclude() filter, or something similar. It is only
        passed in here so that it can be passed to a field's extra_filter() for
        customised behaviour.

        Returns the final field involved in the join, the target database
        column (used for any 'where' constraint), the final 'opts' value and the
        list of tables joined.
        """
        joins = [alias]
        last = [0]
        dupe_set = set()
        exclusions = set()
        extra_filters = []
        int_alias = None
        for pos, name in enumerate(names):
            if int_alias is not None:
                exclusions.add(int_alias)
            exclusions.add(alias)
            last.append(len(joins))
            if name == 'pk':
                name = opts.pk.name
            try:
                field, model, direct, m2m = opts.get_field_by_name(name)
            except FieldDoesNotExist:
                for f in opts.fields:
                    if allow_explicit_fk and name == f.attname:
                        # XXX: A hack to allow foo_id to work in values() for
                        # backwards compatibility purposes. If we dropped that
                        # feature, this could be removed.
                        field, model, direct, m2m = opts.get_field_by_name(f.name)
                        break
                else:
                    names = opts.get_all_field_names() + self.aggregate_select.keys()
                    raise FieldError("Cannot resolve keyword %r into field. "
                            "Choices are: %s" % (name, ", ".join(names)))

            if not allow_many and (m2m or not direct):
                for alias in joins:
                    self.unref_alias(alias)
                raise MultiJoin(pos + 1)
            if model:
                # The field lives on a base class of the current model.
                # Skip the chain of proxy to the concrete proxied model
                proxied_model = get_proxied_model(opts)

                for int_model in opts.get_base_chain(model):
                    if int_model is proxied_model:
                        opts = int_model._meta
                    else:
                        lhs_col = opts.parents[int_model].column
                        dedupe = lhs_col in opts.duplicate_targets
                        if dedupe:
                            exclusions.update(self.dupe_avoidance.get(
                                    (id(opts), lhs_col), ()))
                            dupe_set.add((opts, lhs_col))
                        opts = int_model._meta
                        alias = self.join((alias, opts.db_table, lhs_col,
                                opts.pk.column), exclusions=exclusions)
                        joins.append(alias)
                        exclusions.add(alias)
                        for (dupe_opts, dupe_col) in dupe_set:
                            self.update_dupe_avoidance(dupe_opts, dupe_col,
                                    alias)
            cached_data = opts._join_cache.get(name)
            orig_opts = opts
            dupe_col = direct and field.column or field.field.column
            dedupe = dupe_col in opts.duplicate_targets
            if dupe_set or dedupe:
                if dedupe:
                    dupe_set.add((opts, dupe_col))
                exclusions.update(self.dupe_avoidance.get((id(opts), dupe_col),
                        ()))

            if process_extras and hasattr(field, 'extra_filters'):
                extra_filters.extend(field.extra_filters(names, pos, negate))
            if direct:
                if m2m:
                    # Many-to-many field defined on the current model.
                    if cached_data:
                        (table1, from_col1, to_col1, table2, from_col2,
                                to_col2, opts, target) = cached_data
                    else:
                        table1 = field.m2m_db_table()
                        from_col1 = opts.get_field_by_name(
                            field.m2m_target_field_name())[0].column
                        to_col1 = field.m2m_column_name()
                        opts = field.rel.to._meta
                        table2 = opts.db_table
                        from_col2 = field.m2m_reverse_name()
                        to_col2 = opts.get_field_by_name(
                            field.m2m_reverse_target_field_name())[0].column
                        target = opts.pk
                        orig_opts._join_cache[name] = (table1, from_col1,
                                to_col1, table2, from_col2, to_col2, opts,
                                target)

                    int_alias = self.join((alias, table1, from_col1, to_col1),
                            dupe_multis, exclusions, nullable=True,
                            reuse=can_reuse)
                    if int_alias == table2 and from_col2 == to_col2:
                        joins.append(int_alias)
                        alias = int_alias
                    else:
                        alias = self.join(
                                (int_alias, table2, from_col2, to_col2),
                                dupe_multis, exclusions, nullable=True,
                                reuse=can_reuse)
                        joins.extend([int_alias, alias])
                elif field.rel:
                    # One-to-one or many-to-one field
                    if cached_data:
                        (table, from_col, to_col, opts, target) = cached_data
                    else:
                        opts = field.rel.to._meta
                        target = field.rel.get_related_field()
                        table = opts.db_table
                        from_col = field.column
                        to_col = target.column
                        orig_opts._join_cache[name] = (table, from_col, to_col,
                                opts, target)

                    alias = self.join((alias, table, from_col, to_col),
                            exclusions=exclusions, nullable=field.null)
                    joins.append(alias)
                else:
                    # Non-relation fields.
                    target = field
                    break
            else:
                orig_field = field
                field = field.field
                if m2m:
                    # Many-to-many field defined on the target model.
                    if cached_data:
                        (table1, from_col1, to_col1, table2, from_col2,
                                to_col2, opts, target) = cached_data
                    else:
                        table1 = field.m2m_db_table()
                        from_col1 = opts.get_field_by_name(
                            field.m2m_reverse_target_field_name())[0].column
                        to_col1 = field.m2m_reverse_name()
                        opts = orig_field.opts
                        table2 = opts.db_table
                        from_col2 = field.m2m_column_name()
                        to_col2 = opts.get_field_by_name(
                            field.m2m_target_field_name())[0].column
                        target = opts.pk
                        orig_opts._join_cache[name] = (table1, from_col1,
                                to_col1, table2, from_col2, to_col2, opts,
                                target)

                    int_alias = self.join((alias, table1, from_col1, to_col1),
                            dupe_multis, exclusions, nullable=True,
                            reuse=can_reuse)
                    alias = self.join((int_alias, table2, from_col2, to_col2),
                            dupe_multis, exclusions, nullable=True,
                            reuse=can_reuse)
                    joins.extend([int_alias, alias])
                else:
                    # One-to-many field (ForeignKey defined on the target model)
                    if cached_data:
                        (table, from_col, to_col, opts, target) = cached_data
                    else:
                        local_field = opts.get_field_by_name(
                                field.rel.field_name)[0]
                        opts = orig_field.opts
                        table = opts.db_table
                        from_col = local_field.column
                        to_col = field.column
                        # In case of a recursive FK, use the to_field for
                        # reverse lookups as well
                        if orig_field.model is local_field.model:
                            target = opts.get_field_by_name(
                                field.rel.field_name)[0]
                        else:
                            target = opts.pk
                        orig_opts._join_cache[name] = (table, from_col, to_col,
                                opts, target)

                    alias = self.join((alias, table, from_col, to_col),
                            dupe_multis, exclusions, nullable=True,
                            reuse=can_reuse)
                    joins.append(alias)

            for (dupe_opts, dupe_col) in dupe_set:
                if int_alias is None:
                    to_avoid = alias
                else:
                    to_avoid = int_alias
                self.update_dupe_avoidance(dupe_opts, dupe_col, to_avoid)

        if pos != len(names) - 1:
            if pos == len(names) - 2:
                raise FieldError("Join on field %r not permitted. Did you misspell %r for the lookup type?" % (name, names[pos + 1]))
            else:
                raise FieldError("Join on field %r not permitted." % name)

        return field, target, opts, joins, last, extra_filters