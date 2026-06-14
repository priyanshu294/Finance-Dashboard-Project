/**
 * K6 Load Test (Step 16) — Personal Finance Advisor Streamlit app.
 * Run:  k6 run load_testing/k6_load_test.js
 * Visualise results: k6 run --out influxdb=http://localhost:8086/k6 ...
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Trend, Counter } from "k6/metrics";

const analysisLatency = new Trend("analysis_latency_ms");
const successCount    = new Counter("success_count");
const errorCount      = new Counter("error_count");

export const options = {
  stages: [
    { duration: "30s", target: 5  },  // ramp-up
    { duration: "1m",  target: 20 },  // sustained load
    { duration: "30s", target: 50 },  // stress spike
    { duration: "30s", target: 0  },  // ramp-down
  ],
  thresholds: {
    "http_req_duration":  ["p(95)<2000"],  // 95% of requests under 2s
    "analysis_latency_ms": ["avg<500"],
    "http_req_failed":    ["rate<0.02"],   // error rate < 2%
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8501";

export default function () {
  // Simulate Streamlit app health check
  const res = http.get(`${BASE_URL}/`);

  if (check(res, { "status 200": (r) => r.status === 200 })) {
    successCount.add(1);
    analysisLatency.add(res.timings.duration);
  } else {
    errorCount.add(1);
  }

  sleep(1);
}

export function handleSummary(data) {
  return {
    "load_testing/results/summary.json": JSON.stringify(data, null, 2),
    stdout: `
=== Load Test Summary ===
Requests: ${data.metrics.http_reqs.values.count}
Avg Duration: ${data.metrics.http_req_duration.values.avg.toFixed(0)}ms
p95 Duration: ${data.metrics.http_req_duration.values["p(95)"].toFixed(0)}ms
Error Rate: ${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%
`,
  };
}
