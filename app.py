from flask import Flask, request, jsonify, send_file
import sqlite3, json, os
import xlsxwriter
from fpdf import FPDF
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_FILE = "forms.db"

# Initialize DB
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS forms (
        id TEXT PRIMARY KEY,
        title TEXT,
        questions TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        form_id TEXT,
        answers TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# ----------------------
# Faculty creates form
# ----------------------
@app.route("/api/forms", methods=["POST"])
def create_form():
    data = request.json
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO forms (id, title, questions) VALUES (?, ?, ?)",
                (data["id"], data["title"], json.dumps(data["questions"])))
    conn.commit()
    conn.close()
    return jsonify({"message": "Form created!"})

# Get form by ID
@app.route("/api/forms/<form_id>", methods=["GET"])
def get_form(form_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, title, questions FROM forms WHERE id=?", (form_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify({"id": row[0], "title": row[1], "questions": json.loads(row[2])})
    return jsonify({"error": "Form not found"}), 404

# ----------------------
# Student submits response
# ----------------------
@app.route("/api/forms/<form_id>/responses", methods=["POST"])
def submit_response(form_id):
    data = request.json
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO responses (form_id, answers) VALUES (?, ?)",
                (form_id, json.dumps(data["answers"])))
    conn.commit()
    conn.close()
    return jsonify({"message": "Response saved!"})

# Faculty views responses
@app.route("/api/forms/<form_id>/responses", methods=["GET"])
def get_responses(form_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT answers FROM responses WHERE form_id=?", (form_id,))
    rows = cur.fetchall()
    conn.close()
    return jsonify([json.loads(r[0]) for r in rows])

# ----------------------
# Export responses
# ----------------------
@app.route("/api/forms/<form_id>/export/excel", methods=["GET"])
def export_excel(form_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT answers FROM responses WHERE form_id=?", (form_id,))
    rows = cur.fetchall()
    conn.close()

    os.makedirs("exports", exist_ok=True)
    filepath = f"exports/{form_id}.xlsx"
    workbook = xlsxwriter.Workbook(filepath)
    sheet = workbook.add_worksheet()

    # Write responses
    for i, row in enumerate(rows):
        answers = json.loads(row[0])
        for j, val in enumerate(answers):
            sheet.write(i, j, val)
    workbook.close()
    return send_file(filepath, as_attachment=True)

@app.route("/api/forms/<form_id>/export/pdf", methods=["GET"])
def export_pdf(form_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT answers FROM responses WHERE form_id=?", (form_id,))
    rows = cur.fetchall()
    conn.close()

    os.makedirs("exports", exist_ok=True)
    filepath = f"exports/{form_id}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for i, row in enumerate(rows):
        answers = json.loads(row[0])
        pdf.multi_cell(0, 10, f"{i+1}. " + " | ".join(answers))
    pdf.output(filepath)
    return send_file(filepath, as_attachment=True)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
