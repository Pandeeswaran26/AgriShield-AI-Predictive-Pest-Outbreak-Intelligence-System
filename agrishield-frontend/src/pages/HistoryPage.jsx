import { useEffect, useMemo, useState } from "react";
import { Search, Download, ChevronLeft, ChevronRight, Trash2 } from "lucide-react";
import toast from "react-hot-toast";
import historyService from "../services/historyService";
import useDebounce from "../hooks/useDebounce";
import Table from "../components/common/Table";
import RiskBadge from "../components/common/RiskBadge";
import Modal from "../components/common/Modal";
import Button from "../components/common/Button";

const PAGE_SIZE = 8;

export default function HistoryPage() {
  const [search, setSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState("all");
  const [sortBy, setSortBy] = useState("date");
  const [sortOrder, setSortOrder] = useState("desc");
  const [page, setPage] = useState(1);
  const [rows, setRows] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [pendingDelete, setPendingDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [refreshTick, setRefreshTick] = useState(0);

  const debouncedSearch = useDebounce(search, 350);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    historyService
      .getHistory({
        page,
        pageSize: PAGE_SIZE,
        search: debouncedSearch,
        sortBy,
        sortOrder,
        filters: riskFilter === "all" ? {} : { risk_level: riskFilter },
      })
      .then((data) => {
        if (!mounted) return;
        setRows(data.items || []);
        setTotal(data.total || 0);
      })
      .catch((err) => toast.error(err.message || "Couldn't load history."))
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, [debouncedSearch, riskFilter, sortBy, sortOrder, page, refreshTick]);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const toggleSort = (col) => {
    if (sortBy === col) {
      setSortOrder((o) => (o === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(col);
      setSortOrder("desc");
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const blob = await historyService.exportCsv(
        riskFilter === "all" ? {} : { risk_level: riskFilter }
      );
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "agrishield-prediction-history.csv";
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      toast.error(err.message || "Export failed.");
    } finally {
      setExporting(false);
    }
  };

  const handleDelete = async () => {
    if (!pendingDelete) return;
    setDeleting(true);
    try {
      await historyService.deleteRecord(pendingDelete.id);
      toast.success("Prediction record deleted");
      setPendingDelete(null);
      setRefreshTick((t) => t + 1);
    } catch (err) {
      toast.error(err.message || "Couldn't delete this record.");
    } finally {
      setDeleting(false);
    }
  };

  const columns = useMemo(
    () => [
      { key: "date", label: "Date", sortable: true },
      { key: "crop", label: "Crop", sortable: true },
      { key: "pestName", label: "Pest" },
      { key: "location", label: "Location", sortable: true },
      {
        key: "riskLevel",
        label: "Risk",
        sortable: true,
        render: (row) => <RiskBadge level={row.riskLevel} />,
      },
      {
        key: "confidence",
        label: "Confidence",
        sortable: true,
        render: (row) => <span className="font-mono">{row.confidence}%</span>,
      },
      {
        key: "actions",
        label: "",
        render: (row) => (
          <button
            onClick={() => setPendingDelete(row)}
            aria-label="Delete record"
            className="rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-500/10"
          >
            <Trash2 size={15} />
          </button>
        ),
      },
    ],
    []
  );

  return (
    <div className="glass-card p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative w-full sm:max-w-xs">
          <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            placeholder="Search crop, pest, location..."
            className="input-field pl-10"
          />
        </div>

        <div className="flex items-center gap-3">
          <select
            value={riskFilter}
            onChange={(e) => {
              setRiskFilter(e.target.value);
              setPage(1);
            }}
            className="input-field !w-auto"
          >
            <option value="all">All risk levels</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
          </select>
          <Button variant="secondary" onClick={handleExport} loading={exporting}>
            <Download size={16} /> Export CSV
          </Button>
        </div>
      </div>

      <div className="mt-6">
        <Table
          columns={columns}
          rows={rows}
          loading={loading}
          sortBy={sortBy}
          sortOrder={sortOrder}
          onSort={toggleSort}
          emptyMessage="No predictions match your filters yet."
        />
      </div>

      <div className="mt-4 flex items-center justify-between text-sm text-slate-400">
        <p>
          Page {page} of {totalPages}
        </p>
        <div className="flex gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="btn-secondary !px-3 !py-1.5"
          >
            <ChevronLeft size={16} />
          </button>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="btn-secondary !px-3 !py-1.5"
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

      <Modal
        open={Boolean(pendingDelete)}
        onClose={() => setPendingDelete(null)}
        title="Delete prediction record?"
        footer={
          <>
            <Button variant="ghost" onClick={() => setPendingDelete(null)}>
              Cancel
            </Button>
            <Button variant="danger" loading={deleting} onClick={handleDelete}>
              Delete
            </Button>
          </>
        }
      >
        <p className="text-sm text-slate-500 dark:text-slate-400">
          This will permanently remove the {pendingDelete?.crop} / {pendingDelete?.pestName}{" "}
          prediction from {pendingDelete?.date}. This can't be undone.
        </p>
      </Modal>
    </div>
  );
}
