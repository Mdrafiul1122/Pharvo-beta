interface Column<T> {
  key: string
  label: string
  render?: (item: T) => React.ReactNode
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  loading?: boolean
  onEdit?: (item: T) => void
  onDelete?: (item: T) => void
}

export default function DataTable<T extends { id: number }>({
  columns,
  data,
  loading,
  onEdit,
  onDelete,
}: DataTableProps<T>) {
  if (loading) {
    return <div className="text-center py-8 text-gray-400">Loading...</div>
  }

  if (data.length === 0) {
    return <div className="text-center py-8 text-gray-400">No data found</div>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            {columns.map((col) => (
              <th key={col.key} className="text-left py-3 px-4 font-medium text-gray-500">
                {col.label}
              </th>
            ))}
            {(onEdit || onDelete) && (
              <th className="text-right py-3 px-4 font-medium text-gray-500">Actions</th>
            )}
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr key={item.id} className="border-b border-gray-100 hover:bg-gray-50">
              {columns.map((col) => (
                <td key={col.key} className="py-3 px-4 text-gray-700">
                  {col.render ? col.render(item) : String((item as Record<string, unknown>)[col.key] ?? "")}
                </td>
              ))}
              {(onEdit || onDelete) && (
                <td className="py-3 px-4 text-right space-x-2">
                  {onEdit && (
                    <button onClick={() => onEdit(item)} className="text-blue-600 hover:text-blue-800 text-xs">
                      Edit
                    </button>
                  )}
                  {onDelete && (
                    <button onClick={() => onDelete(item)} className="text-red-600 hover:text-red-800 text-xs">
                      Delete
                    </button>
                  )}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
