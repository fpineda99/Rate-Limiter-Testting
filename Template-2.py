#!/usr/bin/env python3
import binascii
import hashlib
import json
import sys
import asyncio
import aiohttp
import requests
from collections import Counter

LOG_FILE = "rate_limit_results.csv"

def _log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{message}\n")

def md5_checksum(data):# This function calculates the checksum
    return hashlib.md5(data.encode()).hexdigest()

def find_port(md5):
    url = "http://100.26.120.158:5000/port"
    payload = {"ID": md5}
    response = requests.post(url, json=payload)
    data = response.json()
    port = int(data["Port"])
    return port

def _classify_response(response_data):
    answer = str(response_data.get("Answer", ""))
    if answer == "Error":
        return "error"
    elif "." in answer:
        return "float"
    else:
        return "int"

async def _test_rate(md5, port, n1, n2, rps, verbose):
    sample_count = max(50, int(rps * 1.5))
    url = f"http://100.26.120.158:{port}/compute"
    payload = {"ID": md5, "N1": str(n1), "N2": str(n2)}
    responses = []

    async with aiohttp.ClientSession() as session:
        tasks = [session.post(url, json=payload) for _ in range(sample_count)]
        results = await asyncio.gather(*tasks)
        for i, resp in enumerate(results, 1):
            data = await resp.json()
            response_type = _classify_response(data)
            responses.append(response_type)

            if verbose:
                answer = data.get('Answer', 'N/A')
                print(f"  RPS: {rps:.2f} | Request {i}/{sample_count} | Response: {answer} | Type: {response_type}")

    counts = Counter(responses)
    dominant = counts.most_common(1)[0][0]

    if verbose:
        print(f"  → Result: {dominant} ({dict(counts)})")

    return dominant

async def _binary_search_threshold(md5, port, n1, n2, low_rps, high_rps, transition_from, verbose):
    precision = 1.0

    while high_rps - low_rps > precision:
        mid_rps = (low_rps + high_rps) / 2.0

        if not verbose:
            print(f"Testing: {mid_rps:.2f} RPS", end="\r")
        else:
            print(f"\nTesting RPS: {mid_rps:.2f} (range: {low_rps:.2f} - {high_rps:.2f})")

        response_type = await _test_rate(md5, port, n1, n2, mid_rps, verbose)
        _log(f"{mid_rps:.2f},{response_type}")

        if response_type == transition_from:
            if verbose:
                print(f"  Still '{transition_from}', threshold is higher")
            low_rps = mid_rps
        else:
            if verbose:
                print(f"  Changed to '{response_type}', threshold is lower")
            high_rps = mid_rps

    return round((low_rps + high_rps) / 2.0, 2)

async def find_limits(md5, port, first_number=0.0, second_number=0.0, verbose=False):
    with open(LOG_FILE, "w") as f:
        f.write("RPS,ResponseType\n")

    print("Finding First threshold (float -> int)")
    first_limit = await _binary_search_threshold(md5, port, first_number, second_number, 1.0, 50.0, "float", verbose)
    print(f"\nFirst threshold: {first_limit} RPS")

    print("\nFinding Second threshold (int -> error)")
    second_limit = await _binary_search_threshold(md5, port, first_number, second_number, first_limit + 0.5, 100.0, "int", verbose)
    print(f"\nSecond threshold: {second_limit} RPS")

    return first_limit, second_limit

def main():
    verbose = False
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <Last 4 digits of Cougar ID> <first_number> <second_number> <-v(Verbose Option)>")
        sys.exit(1)
    md5=md5_checksum(sys.argv[1])
    first_number=float(sys.argv[2])
    second_number=float(sys.argv[3])
    port=find_port(md5)
    print(f"MD5: {md5}",f"Port: {port}",sep=",")
    if len(sys.argv) >4:
        verbose=True
    first_limit,second_limit=asyncio.run(find_limits(md5, port, first_number, second_number, verbose))
    print(f"MD5: {md5}",f"Port: {port}",f"First Limit: {first_limit}",f"Second Limit: {second_limit}",sep=",")
    print(verbose)

if __name__ == "__main__":
    main()
