import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import BookList from "./components/BookList";
import AuthorList from "./components/AuthorList";
import ReaderList from "./components/ReaderList";
import RecordList from "./components/RecordList";

export default function App() {
  return (
    <BrowserRouter>
      <div className="p-4 bg-gray-100 min-h-screen">
        <h1 className="text-3xl font-bold mb-4 text-center text-blue-600">
          📚 Library Management System
        </h1>

        <nav className="flex justify-center gap-4 mb-6">
          <Link to="/books" className="text-blue-500 hover:underline">
            Books
          </Link>
          <Link to="/authors" className="text-blue-500 hover:underline">
            Authors
          </Link>
          <Link to="/readers" className="text-blue-500 hover:underline">
            Readers
          </Link>
          <Link to="/records" className="text-blue-500 hover:underline">
            Records
          </Link>
        </nav>

        <Routes>
          <Route path="/" element={<BookList />} />
          <Route path="/books" element={<BookList />} />
          <Route path="/authors" element={<AuthorList />} />
          <Route path="/readers" element={<ReaderList />} />
          <Route path="/records" element={<RecordList />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
