# Round 2 policy image - The Sequential Matching Problem (Vouchsafe hackathon).
#
# Assessed limits: 2 CPU cores, 1 GiB RAM, 10 s per invocation,
# 1 MiB for request/response/carried memory, 2 GiB image, no network.
#
# Deliberately dependency-free: the greedy arm needs only the standard library.
# (networkx is imported lazily and only by the max-weight matcher arms.)
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=0 \
    ROUND2_ARM=greedy

WORKDIR /app

# The organisers' public kit (eligibility + observation contract) and our policy.
COPY kit.py policy.py LICENSE.kit ./

RUN chmod -R a+rX /app

# Unprivileged, matching the organiser's own image.
USER 65534:65534

# One JSON request on stdin, one JSON response on stdout, exit 0. No arguments.
ENTRYPOINT ["python3", "/app/policy.py"]
