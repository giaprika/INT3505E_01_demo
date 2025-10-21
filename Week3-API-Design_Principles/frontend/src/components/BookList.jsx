import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { API, API_V2 } from "../api/api";

export default function BookList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const page = parseInt(searchParams.get("page") || "1");
  const searchQuery = searchParams.get("search") || "";
  const [books, setBooks] = useState([]);
  const [pages, setPages] = useState(1);

  const fetchBooks = async () => {
    const res = await API.get(
      `/books/?page=${page}&per_page=5&search=${encodeURIComponent(
        searchQuery
      )}`
    );
    setBooks(res.data.books || []);
    setPages(res.data.pages || 1);
  };

  useEffect(() => {
    fetchBooks();
  }, [page, searchQuery]);

  const handlePageChange = (newPage) => {
    setSearchParams({ page: newPage, search: searchQuery });
  };

  const handleSearchChange = (e) => {
    setSearchParams({ page: 1, search: e.target.value });
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-xl font-semibold mb-3">📚 Books</h2>
      <div className="mb-3">
        <input
          type="text"
          placeholder="Search books..."
          value={searchQuery}
          onChange={handleSearchChange}
          className="border px-3 py-2 w-full rounded"
        />
      </div>

      <table className="w-full border-collapse border">
        <thead>
          <tr className="bg-gray-200">
            <th className="border px-3 py-2">Title</th>
            <th className="border px-3 py-2">Genre</th>
            <th className="border px-3 py-2">Year</th>
          </tr>
        </thead>
        <tbody>
          {books.length > 0 ? (
            books.map((b) => (
              <tr key={b.book_id}>
                <td className="border px-3 py-2">{b.title}</td>
                <td className="border px-3 py-2">{b.genre}</td>
                <td className="border px-3 py-2">{b.published_year}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="3" className="text-center py-3">
                No books found
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
