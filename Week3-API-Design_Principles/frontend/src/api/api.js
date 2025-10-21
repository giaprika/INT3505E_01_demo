import axios from "axios";

const BASE_URL = "http://localhost:3000/api";

export const API = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Accept-Version": "v1",
  },
});

export const API_V2 = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Accept-Version": "v2",
  },
});
