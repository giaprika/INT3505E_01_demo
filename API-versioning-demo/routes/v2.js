import express from "express";
const router = express.Router();

router.get("/users", (req, res) => {
  res.json({
    data: [
      { id: 1, name: "Giap", email: "giap@gmail.com" },
      { id: 2, name: "Giapp", email: "giapp@gmail.com" },
    ],
    version: "v2",
  });
});

export default router;
