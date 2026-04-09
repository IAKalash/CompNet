import csv
import re
import subprocess

DOMAINS = [
    "github.com",
    "wikipedia.org",
    "cloudflare.com",
]
OUTPUT = "results.csv"

def main():
    rows = []
    hop_pattern = re.compile(r"^(\d+)\s+(.*)$")
    rtt_pattern = re.compile(r"([0-9.]+)\s*ms")

    for domain in DOMAINS:
        dns_result = subprocess.run(
            ["dig", "+short", domain],
            capture_output=True,
            text=True,
            check=False,
        )

        ips = []
        for line in dns_result.stdout.splitlines():
            ips.append(line)

        for ip in sorted(set(ips)):
            rows.append({
                "phase": "dns",
                "domain": domain,
                "ip": ip,
                "hop": "",
                "status": "resolved",
                "hop_address": "",
                "rtt_ms": "",
                "raw_line": "",
            })

            traceroute_result = subprocess.run(
                ["traceroute", "-n", "-q", "1", "-w", "1", ip],
                capture_output=True,
                text=True,
                check=False,
            )

            for raw_line in traceroute_result.stdout.splitlines():
                line = raw_line.strip()
                if not line:
                    continue

                match = hop_pattern.match(line)
                if not match:
                    continue

                hop = match.group(1)
                remainder = match.group(2)

                if remainder.startswith("*"):
                    rows.append({
                        "phase": "traceroute",
                        "domain": domain,
                        "ip": ip,
                        "hop": hop,
                        "status": "timeout",
                        "hop_address": "",
                        "rtt_ms": "",
                        "raw_line": raw_line,
                    })
                    continue

                hop_address = remainder.split()[0]
                rtt_match = rtt_pattern.search(remainder)
                rows.append({
                    "phase": "traceroute",
                    "domain": domain,
                    "ip": ip,
                    "hop": hop,
                    "status": "ok",
                    "hop_address": hop_address,
                    "rtt_ms": rtt_match.group(1) if rtt_match else "",
                    "raw_line": raw_line,
                })

    with open(OUTPUT, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "phase",
                "domain",
                "ip",
                "hop",
                "status",
                "hop_address",
                "rtt_ms",
                "raw_line",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to {OUTPUT}")

if __name__ == "__main__":
    main()