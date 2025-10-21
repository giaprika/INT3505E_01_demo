import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import BookList from "./components/BookList";

export default function App() {
  return (
    <BrowserRouter>
      <div className="p-4 bg-gray-100 min-h-screen">
        <h1 className="text-3xl font-bold mb-4 text-center text-blue-600">
          📚 Library Management System
        </h1>

        <nav className="flex justify-center gap-16 mb-6">
          <div className="mx-4">
            <Link to="/books" className="text-blue-500 hover:underline">
              Books
            </Link>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<BookList />} />
          <Route path="/books" element={<BookList />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
