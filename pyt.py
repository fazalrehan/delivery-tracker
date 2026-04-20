import mysql.connector
from flask import Flask, render_template_string, request

app = Flask(__name__)

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="fazal",
    database="delivery_tracker"
)

# ---------- GLOBAL STYLE ----------
base_style = """
<style>
body {
    font-family: 'Segoe UI', Arial, sans-serif;
    background-color: #eef2f7;
    margin: 0;
    padding: 0;
}

.container {
    width: 100%;
    max-width: 900px;
    margin: 60px auto;
}

.card {
    background: #ffffff;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

h1, h2 {
    margin-bottom: 15px;
    color: #333;
}

label {
    display: block;
    margin-top: 10px;
    font-weight: 500;
}

input {
    width: 100%;
    padding: 10px;
    margin-top: 5px;
    border-radius: 5px;
    border: 1px solid #ccc;
}

button {
    margin-top: 15px;
    padding: 10px 18px;
    border: none;
    border-radius: 5px;
    background-color: #2c7be5;
    color: white;
    cursor: pointer;
    font-size: 14px;
}

button:hover {
    background-color: #1a5fd1;
}

.status {
    font-weight: bold;
    margin-top: 10px;
}

.success {
    color: green;
}

.warning {
    color: #e67e22;
}

.nav-btn {
    background-color: #6c757d;
}

.nav-btn:hover {
    background-color: #5a6268;
}

.row {
    display: flex;
    gap: 20px;
}

.column {
    flex: 1;
}
</style>
"""

# ---------- HOME ----------
@app.route('/')
def home():
    html = f"""
    {base_style}
    <div class="container">

        <div class="card">
            <h1>Delivery Tracker</h1>
            <p>Track shipments and update delivery status.</p>
        </div>

        <div class="row">

            <div class="column">
                <div class="card">
                    <h2>Track Shipment</h2>
                    <form action="/track" method="get">
                        <label>Tracking ID</label>
                        <input name="id" required>
                        <button type="submit">Track</button>
                    </form>
                </div>
            </div>

            <div class="column">
                <div class="card">
                    <h2>Update Status</h2>
                    <form action="/update" method="get">
                        <label>Tracking ID</label>
                        <input name="id" required>

                        <label>Status</label>
                        <input name="status" required placeholder="shipped / in transit / delivered">

                        <button type="submit">Update</button>
                    </form>
                </div>
            </div>

        </div>

        <div class="card">
            <h2>Pending Shipments</h2>
            <a href="/check">
                <button>View Pending</button>
            </a>
        </div>

    </div>
    """
    return render_template_string(html)


# ---------- TRACK ----------
@app.route('/track')
def track():
    tracking_id = request.args.get("id")

    cursor = conn.cursor()
    cursor.execute(
        "SELECT tracking_id, courier_name, status FROM shipments WHERE tracking_id = %s",
        (tracking_id,)
    )
    result = cursor.fetchone()

    if result:
        status_class = "success" if result[2] == "delivered" else "warning"

        html = f"""
        {base_style}
        <div class="container">
            <div class="card">
                <h2>Shipment Details</h2>
                <p><b>Tracking ID:</b> {result[0]}</p>
                <p><b>Courier:</b> {result[1]}</p>
                <p class="status {status_class}"><b>Status:</b> {result[2]}</p>

                <a href="/"><button class="nav-btn">Back</button></a>
            </div>
        </div>
        """
        return render_template_string(html)
    else:
        return render_template_string(f"""
        {base_style}
        <div class="container">
            <div class="card">
                <h2>Result</h2>
                <p>No shipment found.</p>
                <a href="/"><button class="nav-btn">Back</button></a>
            </div>
        </div>
        """)


# ---------- UPDATE ----------
@app.route('/update')
def update():
    tracking_id = request.args.get("id")
    new_status = request.args.get("status")

    cursor = conn.cursor()
    cursor.execute(
        "UPDATE shipments SET status = %s WHERE tracking_id = %s",
        (new_status, tracking_id)
    )
    conn.commit()

    html = f"""
    {base_style}
    <div class="container">
        <div class="card">
            <h2>Status Updated</h2>
            <p><b>{tracking_id}</b> has been updated to <b>{new_status}</b>.</p>
            <a href="/"><button class="nav-btn">Back</button></a>
        </div>
    </div>
    """
    return render_template_string(html)


# ---------- CHECK ----------
@app.route('/check')
def check():
    cursor = conn.cursor()

    cursor.execute(
        "SELECT tracking_id, status FROM shipments WHERE status != %s",
        ("delivered",)
    )
    results = cursor.fetchall()

    rows = ""
    for row in results:
        rows += f"<p><b>{row[0]}</b> — {row[1]}</p>"

    html = f"""
    {base_style}
    <div class="container">
        <div class="card">
            <h2>Pending Shipments</h2>
            {rows if rows else "<p>All shipments have been delivered.</p>"}
            <a href="/"><button class="nav-btn">Back</button></a>
        </div>
    </div>
    """
    return render_template_string(html)


# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)