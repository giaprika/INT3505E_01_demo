import React, { useEffect, useState } from "react";
import API from "../api/api";

export default function AuthorList() {
  const [authors, setAuthors] = useState([]);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");

  const fetchAuthors = async () => {
    const res = await API.get(
      `/authors/?page=${page}&per_page=6&search=${encodeURIComponent(
        searchQuery
      )}`
    );
    setAuthors(res.data.authors || []);
    setPages(res.data.pages || 1);
  };

  useEffect(() => {
    fetchAuthors();
  }, [page, searchQuery]);

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-xl font-semibold mb-3">👤 Authors</h2>
      <div className="mb-3">
        <input
          type="text"
          placeholder="Search authors..."
          value={searchQuery}
          onChange={(e) => {
            setPage(1);
            setSearchQuery(e.target.value);
          }}
          className="border px-3 py-2 w-full rounded"
        />
      </div>

      <table className="w-full border-collapse border">
        <thead>
          <tr className="bg-gray-200">
            <th className="border px-3 py-2">Name</th>
            <th className="border px-3 py-2">Email</th>
            <th className="border px-3 py-2">Birth Date</th>
          </tr>
        </thead>
        <tbody>
          {authors.length > 0 ? (
            authors.map((a) => (
              <tr key={a.author_id}>
                <td className="border px-3 py-2">{a.name}</td>
                <td className="border px-3 py-2">{a.email}</td>
                <td className="border px-3 py-2">{a.birth_date || "-"}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="3" className="text-center py-3">
                No authors found
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <div className="flex justify-between mt-3">
        <button disabled={page <= 1} onClick={() => setPage(page - 1)}>
          Prev
        </button>
        <span>
          Page {page} / {pages}
        </span>
        <button disabled={page >= pages} onClick={() => setPage(page + 1)}>
          Next
        </button>
      </div>
    </div>
  );
}
