from flask import Flask, request, jsonify
from jamaibase import JamAI, types as p
import os, sys, re
from datetime import datetime

# Initialize Flask app once
app = Flask(__name__)

# 1. Configuration
PROJECT_ID = os.getenv("JAMAI_PROJECT_ID")
API_KEY = os.getenv("JAMAI_PAT")
TABLE_ID = os.getenv("ACTION_TABLE_ID")

# Initialize JamAI Client
jamai = JamAI(
    project_id=PROJECT_ID,
    token=API_KEY
)

@app.route('/api/analyze', methods=['POST'])
def analyze_route():
    try:
        data = request.json or {}
        user_input = data.get('user_input')
        location_details = data.get('location_details')
        # --- NEW: Capture the math/distance data from frontend ---
        context_data = data.get('context_data') 
        # ---------------------------------------------------------
        row_id_to_fetch = data.get('row_id')

        if not user_input and not row_id_to_fetch:
            return jsonify({"error": "User input or row_id is required"}), 400

        # =========================================================
        # MODE 2: FETCH STATUS (Polling)
        # =========================================================
        if row_id_to_fetch:
            print(f"DEBUG: Fetching Row ID: {row_id_to_fetch}", file=sys.stderr)

            try:
                # 1. Fetch the row with specific columns
                row_response = jamai.table.get_table_row(
                    p.TableType.ACTION,
                    TABLE_ID,
                    row_id_to_fetch,
                    columns=["route_analysis", "selected_pps", "decoded_tags"]
                )

                # --- UNIVERSAL DATA NORMALIZER ---
                def normalize_to_dict(obj):
                    if isinstance(obj, dict):
                        return obj
                    if hasattr(obj, "to_dict"):
                        return obj.to_dict()
                    if hasattr(obj, "model_dump"):
                        return obj.model_dump()
                    if hasattr(obj, "dict"):
                        return obj.dict()
                    if hasattr(obj, "__dict__"):
                        return obj.__dict__
                    return {}

                full_response_dict = normalize_to_dict(row_response)

                # Extract row data
                row_data = {}
                if "route_analysis" in full_response_dict:
                    row_data = full_response_dict
                elif "row" in full_response_dict:
                    row_data = normalize_to_dict(full_response_dict["row"])
                else:
                    print(f"DEBUG: Unknown structure. Keys found: {list(full_response_dict.keys())}", file=sys.stderr)

                # Helper to extract cell values safely
                def get_cell_val(data_dict, key):
                    if not data_dict:
                        return None
                    cell = data_dict.get(key)
                    if not cell:
                        return None
                    if isinstance(cell, dict):
                        return cell.get("value")
                    if hasattr(cell, "value"):
                        return cell.value
                    return cell

                analysis_text = get_cell_val(row_data, "route_analysis")
                pps_text = get_cell_val(row_data, "selected_pps")
                tags_text = get_cell_val(row_data, "decoded_tags")

                if analysis_text and pps_text:
                    clean_pps = pps_text
                    if len(clean_pps) > 50:
                        match = re.search(r"(Shelter\s+\d+|[\w\s]+(Hall|Center|Centre|School|Club))", clean_pps, re.IGNORECASE)
                        if match:
                            clean_pps = match.group(0).strip()
                        else:
                            clean_pps = clean_pps.split('.')[0].split(',')[0]

                    return jsonify({
                        "success": True,
                        "status": "complete",
                        "analysis": analysis_text,
                        "tags": tags_text if tags_text else "",
                        "selected_pps": clean_pps
                    }), 200

                return jsonify({
                    "success": False,
                    "status": "pending",
                    "row_id": row_id_to_fetch
                }), 200

            except Exception as e:
                print(f"ERROR in polling loop: {e}", file=sys.stderr)
                return jsonify({
                    "success": False,
                    "status": "pending",
                    "error_details": str(e),
                    "row_id": row_id_to_fetch
                }), 200

        # =========================================================
        # MODE 1: SUBMIT JOB
        # =========================================================
        else:
            print("DEBUG: Submitting new job...", file=sys.stderr)

            # --- KEY CHANGE: Merge Math Data into User Input ---
            # If context_data exists, we append it to the user_input string.
            # This allows the AI to see the distances without needing a new table column.
            final_user_input = user_input
            if context_data:
                final_user_input = (
                    f"{user_input}\n\n"
                    f"--- SYSTEM DATA (VERIFIED DISTANCES) ---\n"
                    f"{context_data}\n"
                    f"----------------------------------------"
                )

            row_data = {
                "action": "find_safe_shelter",
                "user_input": final_user_input, # Sending the combined data
                "location_details": location_details,
                "created_at": datetime.now().isoformat()
            }

            add_request = p.MultiRowAddRequest(
                table_id=TABLE_ID,
                data=[row_data],
                stream=False,
            )

            completion = jamai.table.add_table_rows(
                table_type=p.TableType.ACTION,
                request=add_request,
            )

            row_id = None
            if hasattr(completion, "rows") and completion.rows:
                row_id = completion.rows[0].row_id
            elif isinstance(completion, dict) and "rows" in completion:
                rows = completion["rows"]
                if rows:
                    row_id = rows[0].get("row_id")

            if not row_id:
                return jsonify({"error": "Failed to submit job - no Row ID returned"}), 500

            print(f"DEBUG: Job Submitted. Row ID: {row_id}", file=sys.stderr)

            return jsonify({
                "success": True,
                "status": "submitted",
                "row_id": row_id
            }), 200

    except Exception as e:
        print(f"FATAL ERROR in analyze_route: {e}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500