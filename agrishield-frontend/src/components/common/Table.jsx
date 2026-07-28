import { ArrowUpDown } from "lucide-react";

/**
 * Generic table.
 * columns: [{ key, label, sortable?: boolean, render?: (row) => node }]
 */
export default function Table({
  columns,
  rows,
  loading,
  skeletonRows = 5,
  sortBy,
  sortOrder,
  onSort,
  emptyMessage = "Nothing to show yet.",
  getRowKey = (row) => row.id,
}) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-surface-border text-slate-400 dark:border-surface-darkBorder">
            {columns.map((col) => (
              <th key={col.key} className="whitespace-nowrap py-3 pr-4 font-medium">
                {col.sortable ? (
                  <button
                    onClick={() => onSort?.(col.key)}
                    className="flex items-center gap-1 hover:text-primary-600"
                  >
                    {col.label}
                    <ArrowUpDown
                      size={12}
                      className={sortBy === col.key ? "text-primary-600" : ""}
                    />
                  </button>
                ) : (
                  col.label
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {loading
            ? [...Array(skeletonRows)].map((_, i) => (
                <tr key={i} className="border-b border-surface-border dark:border-surface-darkBorder">
                  {columns.map((c) => (
                    <td key={c.key} className="py-3 pr-4">
                      <div className="skeleton h-4 w-20" />
                    </td>
                  ))}
                </tr>
              ))
            : rows.map((row) => (
                <tr
                  key={getRowKey(row)}
                  className="border-b border-surface-border last:border-0 dark:border-surface-darkBorder"
                >
                  {columns.map((col) => (
                    <td key={col.key} className="py-3 pr-4">
                      {col.render ? col.render(row) : row[col.key]}
                    </td>
                  ))}
                </tr>
              ))}
          {!loading && rows.length === 0 && (
            <tr>
              <td colSpan={columns.length} className="py-10 text-center text-slate-400">
                {emptyMessage}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
