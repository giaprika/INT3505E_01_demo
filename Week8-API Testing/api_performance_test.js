import http from "k6/http";
import { check, sleep, group } from "k6";
import { Trend } from "k6/metrics";
import { SharedArray } from "k6/data";

export let options = {
  vus: 20, // 20 VU
  duration: "30s",
  thresholds: {
    http_req_duration: ["p(95)<500"],
    http_req_failed: ["rate<0.01"],
  },
  summaryTrendStats: ["avg", "min", "med", "max", "p(90)", "p(95)", "p(99)"],
};

const BASE_URL = "http://127.0.0.1:5000/api";
const ADMIN_EMAIL = "admin@gmail.com";
const ADMIN_PASSWORD = "123456";

// Custom metric để đo response time cho từng endpoint
let bookTrend = new Trend("books_duration");
let recordsTrend = new Trend("records_duration");
let authorsTrend = new Trend("authors_duration");
let readersTrend = new Trend("readers_duration");

export default function () {
  group("Login", function () {
    let loginRes = http.post(
      `${BASE_URL}/admin/login`,
      JSON.stringify({ email: ADMIN_EMAIL, password: ADMIN_PASSWORD }),
      { headers: { "Content-Type": "application/json" } }
    );

    if (
      !check(loginRes, {
        "Login success": (r) => r.status === 200,
        "Access token returned": (r) => r.json("access_token") !== undefined,
      })
    ) {
      console.error(`Login failed: ${loginRes.status} - ${loginRes.body}`);
      return; // không tiếp tục nếu login thất bại
    }

    let token = loginRes.json("access_token");
    let authHeader = { headers: { Authorization: `Bearer ${token}` } };

    //Books
    group("Get books", function () {
      let res = http.get(`${BASE_URL}/books`, authHeader);
      bookTrend.add(res.timings.duration);

      if (
        !check(res, {
          "Books 200": (r) => r.status === 200,
          "Has books": (r) => r.json("books") !== undefined,
        })
      ) {
        console.error(`Books error: ${res.status} - ${res.body}`);
      }
    });

    //Records
    group("Get records", function () {
      let res = http.get(`${BASE_URL}/records`, authHeader);
      recordsTrend.add(res.timings.duration);

      if (
        !check(res, {
          "Records 200": (r) => r.status === 200,
          "Has records": (r) => r.json("records") !== undefined,
        })
      ) {
        console.error(`Records error: ${res.status} - ${res.body}`);
      }
    });

    //Authors
    group("Create author (expect 400)", function () {
      let res = http.post(
        `${BASE_URL}/authors`,
        JSON.stringify({
          email: "test_author@example.com",
          birth_date: "1980-01-01",
        }),
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );
      authorsTrend.add(res.timings.duration);

      if (
        !check(res, {
          "Author returns 400": (r) => r.status === 400,
          "Error is name required": (r) => r.json("error") === "name required",
        })
      ) {
        console.error(`Authors error: ${res.status} - ${res.body}`);
      }
    });

    //Readers (no token)
    group("Get readers (no token)", function () {
      let res = http.get(`${BASE_URL}/readers`);
      readersTrend.add(res.timings.duration);

      if (
        !check(res, {
          "Readers 401": (r) => r.status === 401,
          "Has Missing Authorization Header": (r) =>
            r.json("msg") === "Missing Authorization Header",
        })
      ) {
        console.error(`Readers error: ${res.status} - ${res.body}`);
      }
    });
  });

  sleep(1);
}
