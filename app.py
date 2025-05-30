from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import io
from anonymizer import anonymize_transactions
from anonymized_output import apply_anonymization

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Get form values
        k = int(request.form['k_value'])
        m = int(request.form['m_value'])
        t = float(request.form['t_value'])

        # Normalize sensitive column input
        sensitive_columns = [col.strip().lower() for col in request.form['sensitive_columns'].split(",")]

        # Read uploaded file into DataFrame
        df = pd.read_csv(file)
        original_columns = df.columns.tolist()

        # Normalize DataFrame column names
        df.columns = [col.strip().lower() for col in df.columns]

        # Convert each row into a set of strings
        transactions = df.apply(lambda row: set(row.dropna().astype(str)), axis=1).tolist()

        # Check for missing columns
        missing_columns = [col for col in sensitive_columns if col not in df.columns]
        if missing_columns:
            return jsonify({
                "error": f"The following sensitive columns were not found in the uploaded file: {missing_columns}",
                "available_columns": df.columns.tolist()
            }), 400

        # Extract sensitive items
        sensitive_items = set()
        for col in sensitive_columns:
            sensitive_items.update(df[col].dropna().astype(str).tolist())


        print("🔍 Sensitive Items Extracted:", list(sensitive_items)[:5])

        # Run k,m,t-anonymity algorithm
        anonymized_result = anonymize_transactions(transactions, sensitive_items, k, m, t)

        # Flatten all record_chunks from all clusters
        all_chunks = []
        for cluster in anonymized_result:
            all_chunks.extend(cluster['record_chunks'])

        # Apply anonymization to original dataframe
        anonymized_df = apply_anonymization(df, all_chunks, sensitive_columns)

        # Write anonymized data to CSV
        output = io.StringIO()
        anonymized_df.to_csv(output, index=False)
        output.seek(0)

        print("✅ Anonymized Result Length:", len(anonymized_result))
        print("✅ Output Preview:\n", anonymized_df.head().to_string())

        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"anonymized_{file.filename}"
        )

    except Exception as e:
        print("❌ Exception:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/preview_headers', methods=['POST'])
def preview_headers():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        df = pd.read_csv(file)
        # Clean column names
        columns = [col.strip() for col in df.columns.tolist()]
        return jsonify({"columns": columns})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)