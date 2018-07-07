WITH view_depend AS (
    SELECT
      source_ns.nspname      AS source_schema,
      source_table.relname   AS source_table,
      pg_attribute.attname   AS source_column_name,
      dependent_ns.nspname   AS dependent_schema,
      dependent_view.relname AS dependent_view
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
          AND dependent_ns.nspname != 'information_schema'),
    all_cols AS (
      SELECT
        table_schema AS schema,
        table_name   AS table,
        column_name  AS column
      FROM information_schema.columns
      WHERE 1 = 1
            AND table_schema NOT LIKE 'pg_%'
            AND table_schema != 'information_schema'
  )
SELECT
  schema,
  a.table,
  a.column,
  dependent_schema,
  dependent_view
FROM all_cols AS a
  LEFT JOIN view_depend AS d
    ON a.schema = d.source_schema
       AND a.table = d.source_table
       AND a.column = d.source_column_name
ORDER BY 1, 2, 3, 4, 5
