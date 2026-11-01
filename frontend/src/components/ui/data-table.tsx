"use client";

import { useMemo, useState, type ReactNode } from "react";
import { ArrowUpDown, ChevronLeft, ChevronRight, Download, Search } from "lucide-react";

export type Column<T> = {
  key: string;
  header: string;
  render?: (row: T) => ReactNode;
  sortValue?: (row: T) => string | number;
  csvValue?: (row: T) => string | number;
  className?: string;
};

type Props<T> = {
  data: T[];
  columns: Column<T>[];
  searchable?: (row: T) => string;
  searchPlaceholder?: string;
  pageSize?: number;
  csvFilename?: string;
  emptyLabel?: string;
};

export function DataTable<T>({
  data,
  columns,
  searchable,
  searchPlaceholder = "Search…",
  pageSize = 10,
  csvFilename = "export.csv",
  emptyLabel = "No records.",
}: Props<T>) {
  const [query, setQuery] = useState("");
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const [page, setPage] = useState(0);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q || !searchable) return data;
    return data.filter((row) => searchable(row).toLowerCase().includes(q));
  }, [data, query, searchable]);

  const sorted = useMemo(() => {
    if (!sortKey) return filtered;
    const col = columns.find((c) => c.key === sortKey);
    if (!col?.sortValue) return filtered;
    const dir = sortDir === "asc" ? 1 : -1;
    return [...filtered].sort((a, b) => {
      const av = col.sortValue!(a);
      const bv = col.sortValue!(b);
      if (av < bv) return -1 * dir;
      if (av > bv) return 1 * dir;
      return 0;
    });
  }, [filtered, sortKey, sortDir, columns]);

  const pageCount = Math.max(1, Math.ceil(sorted.length / pageSize));
  const current = Math.min(page, pageCount - 1);
  const rows = sorted.slice(current * pageSize, current * pageSize + pageSize);

  const toggleSort = (key: string) => {
    const col = columns.find((c) => c.key === key);
    if (!col?.sortValue) return;
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  const exportCsv = () => {
    const headers = columns.map((c) => `"${c.header}"`).join(",");
    const lines = sorted.map((row) =>
      columns
        .map((c) => {
          const v = c.csvValue
            ? c.csvValue(row)
            : c.sortValue
              ? c.sortValue(row)
              : "";
          return `"${String(v).replace(/"/g, '""')}"`;
        })
        .join(","),
    );
    const csv = [headers, ...lines].join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = csvFilename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      {/* Toolbar */}
      <div className="flex flex-col gap-3 border-b border-slate-200 dark:border-slate-800 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
        {searchable ? (
          <div className="flex h-9 items-center gap-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 px-3 sm:w-72">
            <Search className="size-4 text-slate-400 dark:text-slate-500" />
            <input
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setPage(0);
              }}
              placeholder={searchPlaceholder}
              className="h-full w-full bg-transparent text-sm text-slate-900 dark:text-slate-100 outline-none placeholder:text-slate-400 dark:placeholder:text-slate-500"
            />
          </div>
        ) : (
          <div />
        )}
        <div className="flex items-center gap-2">
          <span className="text-[11px] text-slate-500 dark:text-slate-400">
            {sorted.length} record{sorted.length === 1 ? "" : "s"}
          </span>
          <button
            type="button"
            onClick={exportCsv}
            className="inline-flex h-9 items-center gap-1.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3 text-xs font-medium text-slate-600 dark:text-slate-300 transition-colors hover:border-indigo-300 hover:text-indigo-600 dark:hover:text-indigo-400"
          >
            <Download className="size-3.5" />
            Export CSV
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-800/40">
              {columns.map((c) => (
                <th
                  key={c.key}
                  className={`px-4 py-2.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-slate-500 dark:text-slate-400 ${c.className ?? ""}`}
                >
                  {c.sortValue ? (
                    <button
                      type="button"
                      onClick={() => toggleSort(c.key)}
                      className="inline-flex items-center gap-1 transition-colors hover:text-slate-700 dark:hover:text-slate-300"
                    >
                      {c.header}
                      <ArrowUpDown
                        className={`size-3 ${sortKey === c.key ? "text-indigo-600 dark:text-indigo-400" : "text-slate-300"}`}
                      />
                    </button>
                  ) : (
                    c.header
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td
                  colSpan={columns.length}
                  className="px-4 py-10 text-center text-xs text-slate-400 dark:text-slate-500"
                >
                  {emptyLabel}
                </td>
              </tr>
            ) : (
              rows.map((row, i) => (
                <tr
                  key={i}
                  className="border-b border-slate-100 dark:border-slate-800 last:border-0 hover:bg-slate-50 dark:hover:bg-slate-800/50"
                >
                  {columns.map((c) => (
                    <td key={c.key} className={`px-4 py-3 text-slate-700 dark:text-slate-300 ${c.className ?? ""}`}>
                      {c.render ? c.render(row) : String(c.sortValue?.(row) ?? "")}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pageCount > 1 && (
        <div className="flex items-center justify-between border-t border-slate-200 dark:border-slate-800 px-4 py-3">
          <span className="text-[11px] text-slate-500 dark:text-slate-400">
            Page {current + 1} of {pageCount}
          </span>
          <div className="flex items-center gap-1.5">
            <button
              type="button"
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={current === 0}
              className="flex size-8 items-center justify-center rounded-lg border border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 transition hover:border-indigo-300 hover:text-indigo-600 dark:hover:text-indigo-400 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronLeft className="size-4" />
            </button>
            <button
              type="button"
              onClick={() => setPage((p) => Math.min(pageCount - 1, p + 1))}
              disabled={current >= pageCount - 1}
              className="flex size-8 items-center justify-center rounded-lg border border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 transition hover:border-indigo-300 hover:text-indigo-600 dark:hover:text-indigo-400 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronRight className="size-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
