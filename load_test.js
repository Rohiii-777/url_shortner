import { check, sleep } from "k6";
import http from "k6/http";

export const options = {
    vus: 100,
    duration: "2m",
};

export default function () {
    const res = http.get("http://localhost:8000/5HIHlU", {
        redirects: 0,
    });

    check(res, {
        "status is 302": (r) => r.status === 302,
    });

    sleep(0.01);
}
