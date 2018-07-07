SELECT
  source_ns.nspname || '.' || source_table.relname      AS source_table,
  pg_attribute.attname                                  AS column_name,
  dependent_ns.nspname || '.' || dependent_view.relname AS dependent_view
FROM pg_depend
  JOIN pg_rewrite ON pg_depend.objid = pg_rewrite.oid
  JOIN pg_class AS dependent_view ON pg_rewrite.ev_class = dependent_view.oid
  JOIN pg_class AS source_table ON pg_depend.refobjid = source_table.oid
  JOIN pg_attribute ON pg_depend.refobjid = pg_attribute.attrelid
                       AND pg_depend.refobjsubid = pg_attribute.attnum
  JOIN pg_namespace dependent_ns ON dependent_ns.oid = dependent_view.relnamespace
  JOIN pg_namespace source_ns ON source_ns.oid = source_table.relnamespace
WHERE 1 = 1
      AND pg_attribute.attnum > 0
      AND source_ns.nspname NOT LIKE 'pg_%'
      AND dependent_ns.nspname NOT LIKE 'pg_%'
      AND source_ns.nspname != 'information_schema'
      AND dependent_ns.nspname != 'information_schema'
      AND dependent_ns.nspname != 'public'
