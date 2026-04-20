import mysql.connector
from flask import Flask, render_template_string, request, redirect

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

@app.route('/')
def home():
    html = """
    <style>
    body {
        font-family: Arial, sans-serif;
        background: #f4f6f9;
        margin: 0;
    }

    .container {
        max-width: 800px;
        margin: 50px auto;
    }

    .card {
        background: white;
        padding: 20px;
        border-radius: 6px;
        margin-bottom: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }

    h1 {
        margin-bottom: 5px;
    }

    input {
        width: 100%;
        padding: 8px;
        margin: 8px 0;
    }

    button {
        padding: 8px 14px;
        background: #2c7be5;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }

    button:hover {
        background: #1a5fd1;
    }

    .row {
        display: flex;
        gap: 15px;
    }

    .col {
        flex: 1;
    }
    </style>

    <div class="container">

        <div class="card">
            <h1>Delivery Tracker</h1>
            <p>Track and update shipment status</p>
        </div>

        <div class="row">

            <div class="card col">
                <h3>Track</h3>
                <form action="/track" method="get">
                    <input name="id" placeholder="Tracking ID" required>
                    <button>Track</button>
                </form>
            </div>

            <div class="card col">
                <h3>Update</h3>
                <form action="/update" method="get">
                    <input name="id" placeholder="Tracking ID" required>
                    <input name="status" placeholder="Status" required>
                    <button>Update</button>
                </form>
            </div>

        </div>

        <div class="card">
            <a href="/check"><button>View Pending</button></a>
            <a href="/create"><button style="margin-left:10px;">Create Entry</button></a>
        </div>

    </div>
    """
    return render_template_string(html)


# ---------- CREATE ----------
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        tracking_id = request.form.get("tracking_id")
        courier = request.form.get("courier")
        status = request.form.get("status")

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO shipments (tracking_id, courier_name, status) VALUES (%s, %s, %s)",
            (tracking_id, courier, status)
        )
        conn.commit()

        return redirect('/')

    html = f"""
    {base_style}
    <div class="container">
        <div class="card">
            <h2>Create Shipment</h2>

            <form method="post">
                <label>Tracking ID</label>
                <input name="tracking_id" required>

                <label>Courier Name</label>
                <input name="courier" required>

                <label>Status</label>
                <input name="status" required>

                <button type="submit">Submit</button>
            </form>

            <a href="/"><button class="nav-btn">Back</button></a>
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
        html = f"""
        {base_style}
        <div class="container">
            <div class="card">
                <h2>Shipment Details</h2>
                <p><b>Tracking ID:</b> {result[0]}</p>
                <p><b>Courier:</b> {result[1]}</p>
                <p><b>Status:</b> {result[2]}</p>

                <a href="/"><button class="nav-btn">Back</button></a>
            </div>
        </div>
        """
        return render_template_string(html)
    else:
        return "Not found"


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

    return redirect('/')


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
        rows += f"<p>{row[0]} — {row[1]}</p>"

    html = f"""
    {base_style}
    <div class="container">
        <div class="card">
            <h2>Pending Shipments</h2>
            {rows if rows else "All delivered"}
            <a href="/"><button class="nav-btn">Back</button></a>
        </div>
    </div>
    """
    return render_template_string(html)


# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)