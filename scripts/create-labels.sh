#!/bin/bash
# Script to create GitHub labels for project agents
# Usage: ./create-labels.sh
# Requires: GitHub CLI (gh) installed and authenticated

set -e

REPO="Rafi653/Deen-Hidaya"

echo "Creating agent role labels for $REPO..."

# Create role labels
gh label create "role:pm" \
  --repo "$REPO" \
  --color "7057ff" \
  --description "Product management and planning" \
  --force

gh label create "role:lead" \
  --repo "$REPO" \
  --color "d73a4a" \
  --description "Architecture and code review" \
  --force

gh label create "role:frontend" \
  --repo "$REPO" \
  --color "0075ca" \
  --description "Frontend development" \
  --force

gh label create "role:backend" \
  --repo "$REPO" \
  --color "008672" \
  --description "Backend development" \
  --force

gh label create "role:qa" \
  --repo "$REPO" \
  --color "e99695" \
  --description "Quality assurance and testing" \
  --force

# Create meta label for project management issues
gh label create "meta" \
  --repo "$REPO" \
  --color "fbca04" \
  --description "Project management and meta issues" \
  --force

echo "✓ Labels created successfully!"
echo ""
echo "View labels at: https://github.com/$REPO/labels"
