import express from "express";
import { createProxyMiddleware } from "http-proxy-middleware";

const app = express();
const API_TARGET = "http://localhost:5000";

app.use("/api", (req, res, next) => {
  console.log("Header Accept-Version:", req.headers["accept-version"]);
  const version = req.headers["accept-version"] || "v1";
  console.log("Determined version:", version);

  if (version === "v2" && !req.url.startsWith("/v2/")) {
    req.url = `/v2${req.url}`;
  }

  console.log("Forwarding to:", req.url);
  next();
});

app.use(
  "/api",
  createProxyMiddleware({
    target: API_TARGET,
    changeOrigin: true,
    pathRewrite: (path, req) => {
      return `/api${req.url}`;
    },
  })
);

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Node proxy running at http://localhost:${PORT}`);
});
