#!/bin/bash

DD_API_KEY=""
DD_APP_KEY=""
INPUT_FILE="dashboard-list.txt"

while IFS=',' read -r url team_raw || [[ -n "$url" ]]; do
  [[ -z "$url" ]] && continue

  team=$(echo "$team_raw" | tr -d '\r' | xargs)

  # Get dashboard ID 
  if [[ "$url" =~ /dashboard/([a-z0-9-]+) ]]; then
    dashboard_id="${BASH_REMATCH[1]}"
  else
    echo "Wrong format URL: $url"
    continue
  fi

  echo "Processing dashboard ID: $dashboard_id | Team: $team"

  # Download JSON dashboard
  curl -s -X GET "https://api.datadoghq.com/api/v1/dashboard/${dashboard_id}" \
    -H "Accept: application/json" \
    -H "DD-API-KEY: ${DD_API_KEY}" \
    -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
    -o "dashboard_${dashboard_id}.json"

  if [[ ! -s "dashboard_${dashboard_id}.json" ]]; then
    echo "Failed download dashboard $dashboard_id"
    continue
  fi

  team_tags_json=$(printf '["team:%s"]' "$team")

  # JSON validation
  if ! echo "$team_tags_json" | jq empty 2>/dev/null; then
    echo "Invalid team tag JSON: $team_tags_json"
    continue
  fi

  # Add team tag to existing tags
  jq --argjson team_tags "$team_tags_json" '
    .tags as $existing_tags |
    ($existing_tags // []) as $existing |
    ($team_tags - $existing) as $new_tags |
    .tags = $existing + $new_tags
  ' "dashboard_${dashboard_id}.json" > "dashboard_${dashboard_id}_modified.json"

  # Patch the dashboard with new team tag
  curl -s -X PUT "https://api.datadoghq.com/api/v1/dashboard/${dashboard_id}" \
    -H "Content-Type: application/json" \
    -H "DD-API-KEY: ${DD_API_KEY}" \
    -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
    -d @"dashboard_${dashboard_id}_modified.json" > /dev/null
   
  echo "Dashboard $dashboard_id is successfully updated"

  # Clean up temporary files 
  rm "dashboard_${dashboard_id}.json" "dashboard_${dashboard_id}_modified.json"

done < "$INPUT_FILE"
