import express from "express";
import v1Routes from "./routes/v1.js";
import v2Routes from "./routes/v2.js";

const app = express();
const PORT = 8000;

app.use("/api/v1", v1Routes);
app.use("/api/v2", v2Routes);

app.get("/api/query-version/users", (req, res) => {
  const version = req.query.version || "v1";

  if (version === "v2") {
    res.json({
      version: "v2",
      data: [
        { id: 1, name: "Giap", email: "giap@gmail.com" },
        { id: 2, name: "Giapp", email: "giapp@gmail.com" },
      ],
    });
  } else {
    res.json([
      { id: 1, name: "Giap" },
      { id: 2, name: "Giap" },
    ]);
  }
});

app.get("/api/header-version/users", (req, res) => {
  const version = req.headers["accept-version"] || "v1";

  if (version === "v2") {
    res.json({
      version: "v2",
      data: [
        { id: 1, name: "Giap", email: "giap@gmail.com" },
        { id: 2, name: "Giapp", email: "giapp@gmail.com" },
      ],
    });
  } else {
    res.json([
      { id: 1, name: "Giap" },
      { id: 2, name: "Giapp" },
    ]);
  }
});

app.get("/api/users", (req, res) => {
  const accept = req.headers["accept"] || "";

  if (accept.includes("vnd.myapp.v2")) {
    res.json({
      version: "v2",
      data: [
        { id: 1, name: "Giap", email: "giap@gmail.com" },
        { id: 2, name: "Giapp", email: "giapp@gmail.com" },
      ],
    });
  } else {
    res.json([
      { id: 1, name: "Giap" },
      { id: 2, name: "Giapp" },
    ]);
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
