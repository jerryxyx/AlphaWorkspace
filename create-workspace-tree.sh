#!/bin/bash
# Create the OpenClaw workspace directory tree as defined in programme/architecture-proposal.md
set -e

cd "$(dirname "$0")"

echo "Creating workspace directory tree..."

# Core workspace files (already exist, but ensure directories)
mkdir -p programme/raw programme/digested programme/reviews
mkdir -p roles/trading-execution/topics roles/trading-execution/delivery
mkdir -p roles/trading-project/topics roles/trading-project/delivery
mkdir -p knowledge/trading knowledge/quantitative knowledge/operational

# Trading products
mkdir -p trading/products/warrants/topics trading/products/warrants/delivery
mkdir -p trading/products/cbbcs/topics trading/products/cbbcs/delivery
mkdir -p trading/products/listed-options/topics trading/products/listed-options/delivery
mkdir -p trading/products/dlc/topics trading/products/dlc/delivery
mkdir -p trading/execution/topics trading/execution/delivery

# Projects
mkdir -p project/warrant-vol-management/topics project/warrant-vol-management/delivery
mkdir -p project/algo-vol-fitter/topics project/algo-vol-fitter/delivery
mkdir -p project/street-directed-flow/topics project/street-directed-flow/delivery
mkdir -p project/ged-signal/topics project/ged-signal/delivery
mkdir -p project/stamp-exemption/topics project/stamp-exemption/delivery
mkdir -p project/fafb/topics project/fafb/delivery
mkdir -p project/elastic/topics project/elastic/delivery
mkdir -p project/alpha/topics project/alpha/delivery

# Business documents, memory, skills (skills already exists)
mkdir -p business-documents
mkdir -p memory/daily memory/weekly memory/long-term

echo "Tree created successfully."
echo "Next steps:"
echo "1. Populate knowledge/INDEX.md with skeleton"
echo "2. Set up weekly review cron job"
echo "3. Begin daily Git commits"