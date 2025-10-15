import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import API from "../api/api";

export default function AuthorList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const page = parseInt(searchParams.get("page") || "1");
  const searchQuery = searchParams.get("search") || "";
  const [authors, setAuthors] = useState([]);
  const [pages, setPages] = useState(1);

  const fetchAuthors = async () => {
    const res = await API.get(
      `/authors/?page=${page}&per_page=5&search=${encodeURIComponent(
        searchQuery
      )}`
    );
    setAuthors(res.data.authors || []);
    setPages(res.data.pages || 1);
  };

  useEffect(() => {
    fetchAuthors();
  }, [page, searchQuery]);

  const handlePageChange = (newPage) =>
    setSearchParams({ page: newPage, search: searchQuery });
  const handleSearchChange = (e) =>
    setSearchParams({ page: 1, search: e.target.value });

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-xl font-semibold mb-3">👤 Authors</h2>
      <div className="mb-3">
        <input
          type="text"
          placeholder="Search authors..."
          value={searchQuery}
          onChange={handleSearchChange}
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
