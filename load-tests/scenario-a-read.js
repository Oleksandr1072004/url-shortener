import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '30s', target: 10 },   // warm-up
        { duration: '1m',  target: 50 },
        { duration: '2m',  target: 100 },
        { duration: '2m',  target: 200 },
        { duration: '30s', target: 0 },
    ],
    thresholds: {
        http_req_duration: ['p(95)<500', 'p(99)<1000'],
        http_req_failed: ['rate<0.01'],
    },
};

const BASE = 'http://localhost:8080';

export default function () {
    const res = http.get(`${BASE}/api/v1/links/abc123`, { redirects: 0 });
    check(res, {
        'status is 307': (r) => r.status === 307,
    });
    sleep(0.1);
}