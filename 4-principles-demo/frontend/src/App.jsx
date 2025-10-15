import React, { useState, useEffect } from "react";
import axios from "axios";

const API_URL = "http://localhost:5000";

function App() {
  const [books, setBooks] = useState([]);
  const [token, setToken] = useState("");
  const [loginData, _setLoginData] = useState({
    username: "admin",
    password: "password",
  });

  const login = async () => {
    const res = await axios.post(`${API_URL}/login`, loginData);
    setToken(res.data.token);
  };

  const fetchBooks = async () => {
    const res = await axios.get(`${API_URL}/books`, {
      headers: { "x-access-token": token },
    });
    setBooks(res.data);
  };

  const addBook = async () => {
    const title = prompt("Title?");
    const author = prompt("Author?");
    await axios.post(
      `${API_URL}/books`,
      { title, author },
      { headers: { "x-access-token": token } }
    );
    fetchBooks();
  };

  useEffect(() => {
    if (token) fetchBooks();
  }, [token]);

  return (
    <div style={{ padding: "20px" }}>
      {!token && <button onClick={login}>Login</button>}
      {token && (
        <>
          <h1>Library</h1>
          <button onClick={addBook}>Add Book</button>
          <ul>
            {books.map((book) => (
              <li key={book.id}>
                {book.title} by {book.author}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

export default App;
