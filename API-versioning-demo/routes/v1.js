import express from "express";
const router = express.Router();

router.get("/users", (req, res) => {
  res.json([
    { id: 1, name: "Giap" },
    { id: 2, name: "Giapp" },
  ]);
});

export default router;
