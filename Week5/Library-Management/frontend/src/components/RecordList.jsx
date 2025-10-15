import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import API from "../api/api";

export default function RecordList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const page = parseInt(searchParams.get("page") || "1");
  const searchQuery = searchParams.get("search") || "";
  const [records, setRecords] = useState([]);
  const [pages, setPages] = useState(1);

  const fetchRecords = async () => {
    const res = await API.get(
      `/records/?page=${page}&per_page=5&search=${encodeURIComponent(
        searchQuery
      )}`
    );
    setRecords(res.data.records || []);
    setPages(res.data.pages || 1);
  };

  useEffect(() => {
    fetchRecords();
  }, [page, searchQuery]);

  const handlePageChange = (newPage) =>
    setSearchParams({ page: newPage, search: searchQuery });
  const handleSearchChange = (e) =>
    setSearchParams({ page: 1, search: e.target.value });

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-xl font-semibold mb-3">📜 Records</h2>
      <div className="mb-3">
        <input
          type="text"
          placeholder="Search records..."
          value={searchQuery}
          onChange={handleSearchChange}
          className="border px-3 py-2 w-full rounded"
        />
      </div>

      <table className="w-full border-collapse border">
        <thead>
          <tr className="bg-gray-200">
            <th className="border px-3 py-2">Book Copy</th>
            <th className="border px-3 py-2">Reader</th>
            <th className="border px-3 py-2">Borrow Date</th>
            <th className="border px-3 py-2">Return Date</th>
            <th className="border px-3 py-2">Status</th>
          </tr>
        </thead>
        <tbody>
          {records.length > 0 ? (
            records.map((r) => (
              <tr key={r.record_id}>
                <td className="border px-3 py-2">{r.book_copy_id}</td>
                <td className="border px-3 py-2">{r.reader_id}</td>
                <td className="border px-3 py-2">{r.borrow_date}</td>
                <td className="border px-3 py-2">{r.return_date || "-"}</td>
                <td className="border px-3 py-2">{r.status}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="5" className="text-center py-3">
                No records found
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <div className="flex justify-between mt-3">
        <button disabled={page <= 1} onClick={() => handlePageChange(page - 1)}>
          Prev
        </button>
        <span>
          Page {page} / {pages}
        </span>
        <button
          disabled={page >= pages}
          onClick={() => handlePageChange(page + 1)}
        >
          Next
        </button>
      </div>
    </div>
  );
}
