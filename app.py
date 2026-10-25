from flask import Flask, request, redirect, session, send_file, jsonify
import datetime, os, random, base64
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'noble-school-2026'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXT = {'pdf','doc','docx','jpg','png'}

USERS = {
    "NGS001": {"pass": "1234", "name": "Ahmed Ali", "class": "10-A", "role": "student", "parent_no": "923001234567"},
    "TEA001": {"pass": "teacher123", "name": "Sir Bilal", "role": "teacher", "parent_no": "923001234568"},
    "admin": {"pass": "admin123", "name": "Principal", "role": "admin"}
}
attendance_db = {}
marks_db = {"NGS001": {"English": 85, "Math": 90, "Science": 78}}
fees_db = {}
admissions_db = []
SCHOOL_WHATSAPP = "923001234567"
JAZZCASH_NO = "03001234567"
EASYPAISA_NO = "03001234567"

STAFF_DB = {
    "TEA001": {"id":"TEA001","name":"Sir Bilal","role":"teacher","phone":"923001234568","salary":"40000","salary_status":"Unpaid","join_date":"2026-01-01","class_incharge":"10-A","pass":"teacher123"}
}
CLASS_TEACHER_DB = {"10-A": "TEA001"}
EXPENSE_DB = []
SUBJECT_DB = {"10-A": ["English","Math","Science","Urdu","Islamiat","Computer","Sindhi"],"9-A": ["English","Math","Science"],"Class 1": ["English","Math","Urdu"]}
EXAM_DB = []
EXAM_MARKS_DB = {}
ASSIGNMENT_DB = [] # {id, class, subject, title, desc, file, teacher, date}
PAPER_DB = [] # {id, exam_id, exam_name, class, subject, title, file, teacher, date, status}

MAROON = "#5D0F1A"
BG = "#FDF6F0"
LOGO_PATHS = ["/mnt/data/wa_image_5960797837294250810","/mnt/data/wa_image_6183010334366155265","logo.jpeg","logo.png"]

def get_current_month_key(): return datetime.date.today().strftime("%Y-%m")
def ensure_monthly_fees():
    cur = get_current_month_key()
    for uid in USERS:
        if USERS[uid]['role'] == 'student':
            if uid not in fees_db: fees_db[uid] = {}
            if cur not in fees_db[uid]: fees_db[uid][cur] = {"status": "Unpaid", "amount": "2000"}
def get_fee_status(uid):
    cur = get_current_month_key(); ensure_monthly_fees()
    if uid in fees_db and cur in fees_db[uid]: return fees_db[uid][cur]
    return {"status": "Unpaid", "amount": "2000"}
def get_today_att(uid):
    today = datetime.date.today().isoformat()
    for a in attendance_db.get(uid, []):
        if a['date'] == today: return a['status']
    return "Not Marked"

@app.route('/logo')
def logo():
    for p in LOGO_PATHS:
        if os.path.exists(p): return send_file(p, mimetype='image/jpeg')
    return "", 404

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

def page_wrap(body, hide_top=False, home_mode=False):
    top_html = f"""<div class="top"><a href="/"><img src="/logo" style="width:120px;height:120px;border-radius:50%;border:4px solid white;background:white;object-fit:cover"></a><h1 style="margin:10px 0 0 0">NOBLE GRAMMAR SCHOOL</h1><div style="letter-spacing:5px;font-weight:bold;background:white;color:{MAROON};display:inline-block;padding:3px 15px;border-radius:20px;margin-top:8px">N G S</div></div>""" if not hide_top else ""
    bg_style = f"background:linear-gradient(180deg, {MAROON} 0%, #8B1E2E 30%, {BG} 100%);min-height:100vh" if home_mode else f"background:{BG}"
    return f"""<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
    <style>body{{font-family:Arial;margin:0;padding:0;{bg_style}}} .top{{background:{MAROON};padding:25px 15px 10px 15px;text-align:center;color:white}} .box{{background:white;padding:22px;border-radius:16px;box-shadow:0 4px 20px #0002;max-width:800px;margin:15px auto}} .btn{{background:{MAROON};color:white;padding:13px;border:none;border-radius:10px;width:100%;font-size:16px;margin-top:12px;display:block;text-align:center;text-decoration:none;font-weight:bold;cursor:pointer}} .btn-green{{background:#166534}} .btn-red{{background:#7f1d1d}} .btn-yellow{{background:#FFC107;color:{MAROON}}} .btn-blue{{background:#1565C0}} .btn-small{{padding:6px 10px;font-size:12px;display:inline-block;width:auto;margin:2px}} input,select,textarea{{width:100%;padding:12px;margin:7px 0;border:2px solid #e7c9c9;border-radius:10px;box-sizing:border-box}} h2,h3{{color:{MAROON};text-align:center}} table{{width:100%;border-collapse:collapse}} th,td{{border:1px solid #e7c9c9;padding:8px;font-size:13px}} th{{background:{MAROON};color:white}} .hero{{background:linear-gradient(135deg,{MAROON} 0%, #8B1E2E 100%);color:white;text-align:center;padding:40px 20px 30px 20px;border-bottom:5px solid #FFC107}} .hero-logo{{width:180px;height:180px;border-radius:50%;border:6px solid white;background:white;object-fit:cover}} .grid2{{display:grid;grid-template-columns:1fr 1fr;gap:10px}} .card{{background:#FDF6F0;padding:12px;border-radius:10px;border-left:5px solid {MAROON};margin:8px 0}} .scroll-box{{padding:7px 0;overflow:hidden;white-space:nowrap;font-weight:bold}} .notify-scroll{{background:#FFC107;color:{MAROON}}} .scroll-text{{display:inline-block;padding-left:100%;animation:scroll 12s linear infinite}} @keyframes scroll{{0%{{transform:translateX(0)}}100%{{transform:translateX(-100%)}}}}</style></head><body>{top_html}{body}</body></html>"""

@app.route('/', methods=['GET','POST'])
def home():
    ensure_monthly_fees()
    if 'uid' in session and request.method == 'GET':
        uid = session['uid']; role = USERS[uid]['role']
        if role == 'student': return redirect('/student')
        if role == 'teacher': return redirect('/teacher')
        if role == 'admin': return redirect('/admin')
    if request.method == 'POST':
        uid = request.form['uid'].strip(); pwd = request.form['pwd'].strip()
        if uid in USERS and USERS[uid]['pass'] == pwd:
            session['uid'] = uid; return redirect('/')
        return page_wrap('<div class="box"><h2>Wrong Password</h2><a href="/" class="btn">Try Again</a></div>', home_mode=True)
    cur = get_current_month_key(); msg = request.args.get('msg','')
    alert = f'<div style="background:#166534;color:white;padding:12px;border-radius:10px;text-align:center;margin:10px auto;max-width:500px">✅ {msg}</div>' if msg else ""
    return page_wrap(f"""<div class="scroll-box notify-scroll"><div class="scroll-text">📢 Admissions Open 2026-27 | Voucher {cur} | WhatsApp {SCHOOL_WHATSAPP}</div></div>{alert}<div class="hero"><img src="/logo" class="hero-logo"><h1>NOBLE GRAMMAR SCHOOL</h1><div style="background:white;color:{MAROON};display:inline-block;padding:6px 25px;border-radius:20px;font-weight:bold;letter-spacing:6px">N G S</div><p>Learn Today, Lead Tomorrow</p><a href="/admission" target="_blank" class="btn" style="max-width:260px;margin:20px auto;background:#FFC107;color:{MAROON}">📝 Admission Form (New Tab)</a><a href="#login" class="btn" style="max-width:260px;margin:10px auto;background:white;color:{MAROON}">🚀 Login Portal</a></div><div style="max-width:500px;margin:auto;padding:10px"><div id="login" class="box" style="border:3px solid {MAROON}"><h2>Login Portal</h2><form method="POST"><input name="uid" placeholder="ID: NGS001 / TEA001 / admin" required><input name="pwd" type="password" placeholder="Password" required><button class="btn">LOGIN</button></form><small>Student: NGS001 / 1234 | Teacher: TEA001 / teacher123 | Admin: admin / admin123</small></div></div>""", hide_top=True, home_mode=True)

@app.route('/admission')
def admission_page():
    return page_wrap(f"""<div class="hero" style="padding:20px"><img src="/logo" style="width:100px;height:100px;border-radius:50%;border:4px solid white;background:white"><h2 style="color:white">NGS Admission 2026-27</h2></div><div class="box"><h2>📝 Admission Form</h2><form action="/admit" method="POST"><input name="s_name" placeholder="Student Full Name *" required><input name="f_name" placeholder="Father Name *" required><select name="s_class" required><option value="">Select Class *</option><option>Class 1</option><option>Class 2</option><option>Class 9</option><option>Class 10-A</option></select><input name="s_phone" placeholder="Parent WhatsApp 92300xxxxxxx *" required><textarea name="s_address" placeholder="Address" rows="2"></textarea><button class="btn btn-yellow">✅ Submit</button></form><a href="/" class="btn">⬅ Back</a></div>""", hide_top=False)

@app.route('/admit', methods=['POST'])
def admit():
    s_name = request.form.get('s_name','').strip(); f_name = request.form.get('f_name','').strip(); s_class = request.form.get('s_class',''); s_phone = request.form.get('s_phone','').strip()
    new_id = f"NGS{random.randint(100,999)}"
    while new_id in USERS: new_id = f"NGS{random.randint(100,999)}"
    new_pass = f"{random.randint(1000,9999)}"
    USERS[new_id] = {"pass": new_pass, "name": s_name, "class": s_class, "role": "student", "parent_no": s_phone, "father": f_name}
    cur = get_current_month_key(); fees_db[new_id] = {cur: {"status": "Unpaid", "amount": "2000"}}
    admissions_db.append({"id": new_id, "name": s_name, "father": f_name, "class": s_class, "phone": s_phone, "pass": new_pass, "date": datetime.date.today().isoformat()})
    return redirect(f"/?msg=Admission Done! ID {new_id} Pass {new_pass}")

@app.route('/student', methods=['GET','POST'])
def student():
    if 'uid' not in session: return redirect('/')
    ensure_monthly_fees(); uid = session['uid']; user = USERS[uid]; cur = get_current_month_key(); fee = get_fee_status(uid)
    att_html = "".join([f"<tr><td>{a['date']}</td><td>{a['status']}</td></tr>" for a in attendance_db.get(uid, [])]) or "<tr><td colspan=2>No record</td></tr>"
    # Exams for student class
    class_exams = [ex for ex in EXAM_DB if ex['class']==user.get('class','')]
    exam_opts = "".join([f"<option value='{ex['id']}'>{ex['name']} - {ex['date']}</option>" for ex in class_exams]) or "<option>No exams</option>"
    # Show results
    exam_result_html = ""
    for ex in class_exams:
        if ex['id'] in EXAM_MARKS_DB and uid in EXAM_MARKS_DB[ex['id']]:
            subs = EXAM_MARKS_DB[ex['id']][uid]
            rows = "".join([f"<tr><td>{s}</td><td>{m}</td></tr>" for s,m in subs.items()])
            total = sum(int(v) if str(v).isdigit() else 0 for v in subs.values())
            exam_result_html += f"<div class='card'><b>{ex['name']} - {ex['date']}</b><table><tr><th>Subject</th><th>Marks</th></tr>{rows}<tr><th>Total</th><th>{total}</th></tr></table></div>"
    if not exam_result_html: exam_result_html = "<p style='text-align:center'>No result yet. Generate below.</p>"
    # Assignments for student class
    my_assign = [a for a in ASSIGNMENT_DB if a['class']==user.get('class','')]
    assign_html = "".join([f"<div class='card'><b>{a['title']}</b> ({a['subject']}) by {a['teacher']}<br>{a['desc']}<br><small>{a['date']}</small><br><a href='/uploads/{a['file']}' target='_blank' class='btn btn-small btn-blue'>📄 Download {a['file']}</a></div>" for a in my_assign]) or "<p>No assignments</p>"
    
    pay_buttons = f'<a href="/pay/{uid}" class="btn btn-green">✅ Pay Now</a> <a href="/voucher/{uid}" target="_blank" class="btn">📄 Fee Receipt PDF</a>' if fee['status']!="Paid" else f"<p style='color:green;text-align:center'>✔ Paid</p><a href='/voucher/{uid}' target='_blank' class='btn'>📄 Fee Receipt PDF</a>"
    return page_wrap(f'''
    <div class="box"><h2>{user["name"]} - {uid}</h2><p style="text-align:center">Class: {user.get("class","")} | Teacher: {CLASS_TEACHER_DB.get(user.get("class",""),"Not Assigned")} | Today: {get_today_att(uid)}</p>
    <h3>💳 Voucher {cur} - {fee["status"]} Rs {fee["amount"]}</h3>{pay_buttons}
    <h3>📝 Generate My Result Card</h3>
    <div style="background:#E3F2FD;padding:15px;border-radius:10px;border:2px dashed {MAROON}">
        <form action="/download_result/{uid}" method="GET" target="_blank">
            <select name="exam_id" required><option value="">Select Exam Type</option>{exam_opts}<option value="ALL">ALL EXAMS</option></select>
            <button class="btn btn-blue">🎓 Generate Result PDF - By Exam Type</button>
        </form>
        <small>Select Mid Term / Final / Monthly Test then Generate</small>
    </div>
    <h3>📚 My Exam Results</h3>{exam_result_html}
    <h3>📖 Assignments (Uploaded by Teacher)</h3>{assign_html}
    <h3>📚 Attendance</h3><table><tr><th>Date</th><th>Status</th></tr>{att_html}</table>
    <a href="/logout" class="btn btn-red">Logout</a></div>''')

@app.route('/pay/<sid>')
def pay_auto(sid):
    ensure_monthly_fees(); cur = get_current_month_key()
    if sid not in fees_db: fees_db[sid] = {}
    fees_db[sid][cur] = {"status": "Paid", "amount": "2000"}
    EXPENSE_DB.append({"date": datetime.date.today().isoformat(), "type": "Revenue", "title": f"Fees {sid}", "amount": "2000", "desc": f"Student {USERS.get(sid,{}).get('name','')}"})
    return redirect('/student')

@app.route('/voucher/<sid>')
def voucher(sid):
    fee = get_fee_status(sid); user = USERS.get(sid, {}); cur = get_current_month_key()
    return f'''<html><body style="font-family:Arial;padding:20px"><div style="max-width:600px;margin:auto;border:3px solid {MAROON};padding:20px;border-radius:12px"><img src="/logo" style="width:80px;height:80px;border-radius:50%;display:block;margin:auto"><h1 style="color:{MAROON};text-align:center">NGS Fee Receipt {cur}</h1><table style="width:100%;border-collapse:collapse"><tr><th style="background:{MAROON};color:white;padding:10px">ID</th><td style="border:1px solid #ccc;padding:10px">{sid}</td></tr><tr><th style="background:{MAROON};color:white;padding:10px">Name</th><td style="border:1px solid #ccc;padding:10px">{user.get("name","")}</td></tr><tr><th style="background:{MAROON};color:white;padding:10px">Status</th><td style="border:1px solid #ccc;padding:10px"><b>{fee["status"]}</b> Rs {fee["amount"]}</td></tr></table><button onclick="window.print()" style="background:{MAROON};color:white;padding:12px;border:none;border-radius:8px;width:100%;margin-top:20px">🖨️ Print PDF</button></div></body></html>'''

@app.route('/salary_slip/<staff_id>')
def salary_slip(staff_id):
    if staff_id not in STAFF_DB: return "Not found",404
    s = STAFF_DB[staff_id]; cur = get_current_month_key()
    return f'''<html><body style="font-family:Arial;padding:20px"><div style="max-width:600px;margin:auto;border:3px solid {MAROON};padding:20px;border-radius:10px"><h1 style="color:{MAROON};text-align:center">NGS Salary Slip {cur}</h1><table style="width:100%;border-collapse:collapse"><tr><th style="background:{MAROON};color:white;padding:10px;text-align:left">ID</th><td style="border:1px solid #ccc;padding:10px">{s["id"]}</td></tr><tr><th style="background:{MAROON};color:white;padding:10px;text-align:left">Name</th><td style="border:1px solid #ccc;padding:10px">{s["name"]} - Login: {s["id"]} / Pass: {s["pass"]}</td></tr><tr><th style="background:{MAROON};color:white;padding:10px;text-align:left">Salary</th><td style="border:1px solid #ccc;padding:10px">Rs {s["salary"]} - {s["salary_status"]}</td></tr></table><button onclick="window.print()" style="background:{MAROON};color:white;padding:12px;width:100%;margin-top:20px;border:none;border-radius:8px">🖨️ Print PDF</button></div></body></html>'''

@app.route('/expense_report')
@app.route('/expense_report/<month>')
def expense_report(month=None):
    if not month: month = get_current_month_key()
    filtered = [e for e in EXPENSE_DB if e['date'].startswith(month)] or EXPENSE_DB
    total_exp = sum(int(e['amount']) for e in filtered if e['type']=='Expense' and str(e['amount']).isdigit())
    total_rev = sum(int(e['amount']) for e in filtered if e['type']=='Revenue' and str(e['amount']).isdigit())
    profit = total_rev - total_exp
    rows = "".join([f"<tr><td>{e['date']}</td><td>{e['type']}</td><td>{e['title']}</td><td>Rs {e['amount']}</td></tr>" for e in filtered]) or "<tr><td colspan=4>No data</td></tr>"
    return f'''<html><body style="font-family:Arial;padding:20px"><div style="max-width:800px;margin:auto;border:2px solid {MAROON};padding:20px"><h1 style="color:{MAROON};text-align:center">Expense Report {month}</h1><p>Revenue Rs {total_rev} | Expense Rs {total_exp} | Profit Rs {profit}</p><table border=1 style="width:100%;border-collapse:collapse"><tr><th>Date</th><th>Type</th><th>Title</th><th>Amount</th></tr>{rows}</table><button onclick="window.print()" style="background:{MAROON};color:white;padding:12px;width:100%;margin-top:15px">Print</button></div></body></html>'''

@app.route('/teacher', methods=['GET','POST'])
def teacher():
    if 'uid' not in session: return redirect('/')
    ensure_monthly_fees(); msg=""; cur=get_current_month_key(); uid=session['uid']
    if request.method=='POST':
        act=request.form.get('action')
        if act=='attendance':
            sid=request.form.get('student_id'); today=datetime.date.today().isoformat()
            new_list=[a for a in attendance_db.get(sid,[]) if a['date']!=today]
            new_list.append({"date":today,"status":request.form.get('status')}); attendance_db[sid]=new_list; msg=f"Attendance {sid}"
        elif act=='exam_marks':
            ex_id=request.form.get('exam_id'); sub=request.form.get('exam_subject'); m=request.form.get('exam_marks_val'); sid_ex=request.form.get('student_id_exam')
            if ex_id not in EXAM_MARKS_DB: EXAM_MARKS_DB[ex_id]={}
            if sid_ex not in EXAM_MARKS_DB[ex_id]: EXAM_MARKS_DB[ex_id][sid_ex]={}
            EXAM_MARKS_DB[ex_id][sid_ex][sub]=m; msg=f"✅ Result Generated! {sid_ex} {sub}:{m} -> Student can see now + Teacher panel"
        elif act=='assignment':
            f = request.files.get('assign_file')
            filename = "no_file"
            if f and f.filename:
                filename = secure_filename(f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{f.filename}")
                f.save(os.path.join(UPLOAD_FOLDER, filename))
            ASSIGNMENT_DB.append({"id":f"ASN{random.randint(100,999)}","class":request.form['assign_class'],"subject":request.form['assign_subject'],"title":request.form['assign_title'],"desc":request.form['assign_desc'],"file":filename,"teacher":USERS[uid]['name'],"date":datetime.date.today().isoformat()})
            msg="📖 Assignment uploaded -> Shows in Student panel"
        elif act=='paper':
            f = request.files.get('paper_file')
            filename = "no_file"
            if f and f.filename:
                filename = secure_filename(f"PAPER_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{f.filename}")
                f.save(os.path.join(UPLOAD_FOLDER, filename))
            ex_id_sel = request.form['paper_exam_id']
            ex_name = next((ex['name'] for ex in EXAM_DB if ex['id']==ex_id_sel), ex_id_sel)
            PAPER_DB.append({"id":f"PAP{random.randint(100,999)}","exam_id":ex_id_sel,"exam_name":ex_name,"class":request.form['paper_class'],"subject":request.form['paper_subject'],"title":request.form['paper_title'],"file":filename,"teacher":USERS[uid]['name'],"date":datetime.date.today().isoformat(),"status":"Pending"})
            msg="📝 Paper uploaded -> Shows in Principal/Admin panel only (not students)"

    opt="".join([f"<option value='{k}'>{k} - {USERS[k]['name']} ({USERS[k].get('class','')})</option>" for k in USERS if USERS[k]['role']=='student'])
    exam_opts = "".join([f"<option value='{ex['id']}'>{ex['name']} - {ex['class']} ({ex['date']})</option>" for ex in EXAM_DB])
    exam_list = "".join([f"<div class='card'><b>{ex['name']}</b> Class: {ex['class']} Date: {ex['date']}<br>Subjects: {', '.join(ex['subjects'])} ID: {ex['id']}</div>" for ex in EXAM_DB]) or "No exams - Admin creates"
    # Teacher's generated results view
    my_results = ""
    for ex_id, studs in EXAM_MARKS_DB.items():
        for s_id, subs in studs.items():
            my_results += f"<tr><td>{ex_id}</td><td>{s_id} {USERS.get(s_id,{}).get('name','')}</td><td>{', '.join([f'{k}:{v}' for k,v in subs.items()])}</td></tr>"
    if not my_results: my_results = "<tr><td colspan=3>No results yet</td></tr>"

    return page_wrap(f'''
    <div class="box"><h2>Teacher Panel - {USERS[uid]["name"]}</h2><p style="color:green;text-align:center;font-weight:bold">{msg}</p>
    <h3>📝 Exams (Admin Created)</h3>{exam_list}<hr>
    <h3>✅ GENERATE RESULT - Reflect in Student + Teacher Panel</h3>
    <form method="POST" style="background:#E8F5E9;padding:15px;border-radius:10px;border:2px solid #166534">
        <select name="exam_id" required><option value="">Select Exam Type</option>{exam_opts}</select>
        <select name="student_id_exam" required><option value="">Select Student</option>{opt}</select>
        <div class="grid2"><input name="exam_subject" placeholder="Subject e.g. Math" required><input name="exam_marks_val" placeholder="Marks e.g. 85" required></div>
        <input type="hidden" name="action" value="exam_marks"><button class="btn btn-green">💾 Generate Result - Show to Student + Teacher</button>
    </form>
    <h3>📊 Generated Results (Teacher View)</h3><table><tr><th>Exam</th><th>Student</th><th>Marks</th></tr>{my_results}</table>
    <hr>
    <h3>📖 Upload Assignment (PDF/DOC) -> Student Panel</h3>
    <form method="POST" enctype="multipart/form-data" style="background:#FFF8E1;padding:15px;border-radius:10px">
        <input type="hidden" name="action" value="assignment"><div class="grid2"><input name="assign_class" placeholder="Class e.g. 10-A" required><input name="assign_subject" placeholder="Subject" required></div>
        <input name="assign_title" placeholder="Assignment Title e.g. Chapter 5 Homework" required><textarea name="assign_desc" placeholder="Description"></textarea>
        <input type="file" name="assign_file" accept=".pdf,.doc,.docx,.jpg,.png"><button class="btn btn-yellow">📤 Upload Assignment -> Student Will See</button>
    </form>
    <hr>
    <h3>📝 Upload Paper - Select Exam Type -> Principal Panel Only</h3>
    <form method="POST" enctype="multipart/form-data" style="background:#E3F2FD;padding:15px;border-radius:10px;border:2px dashed #1565C0">
        <input type="hidden" name="action" value="paper"><select name="paper_exam_id" required><option value="">Select Exam Type</option>{exam_opts}</select>
        <div class="grid2"><input name="paper_class" placeholder="Class e.g. 10-A" required><input name="paper_subject" placeholder="Subject e.g. Math" required></div>
        <input name="paper_title" placeholder="Paper Title e.g. Mid Term Math Paper" required><input type="file" name="paper_file" accept=".pdf,.doc,.docx" required>
        <button class="btn btn-blue">📤 Upload Paper -> Only Principal Can See</button>
        <small style="color:#1565C0">This paper will NOT show to students, only in Admin/Principal panel for approval</small>
    </form>
    <hr><form method="POST"><h3>Attendance</h3><select name="student_id">{opt}</select><select name="status"><option>Present</option><option>Absent</option></select><input type="hidden" name="action" value="attendance"><button class="btn">Save Attendance</button></form>
    <a href="/logout" class="btn btn-red">Logout</a></div>''')

@app.route('/admin', methods=['GET','POST'])
def admin_panel():
    if 'uid' not in session: return redirect('/')
    ensure_monthly_fees(); cur=get_current_month_key(); msg=""
    if request.method=='POST':
        act = request.form.get('admin_action')
        if act == 'add_staff':
            nid=request.form['staff_id'].strip().upper(); name=request.form['staff_name']; role=request.form['staff_role']; phone=request.form['staff_phone']; salary=request.form['staff_salary']; staff_class=request.form.get('staff_class',''); pwd=request.form['staff_pass']
            USERS[nid] = {"pass": pwd, "name": name, "role": role if role in ['teacher','admin'] else 'staff', "parent_no": phone, "class": staff_class}
            STAFF_DB[nid] = {"id":nid,"name":name,"role":role,"phone":phone,"salary":salary,"salary_status":"Unpaid","join_date":datetime.date.today().isoformat(),"class_incharge":staff_class,"pass":pwd}
            if staff_class and role=='teacher': CLASS_TEACHER_DB[staff_class]=nid
            msg=f"Staff {nid} Login: {nid} Pass: {pwd} Added & Visible Below"
        elif act == 'reset_pass':
            sid=request.form['reset_id']; newp=request.form['new_password']
            if sid in USERS: USERS[sid]['pass']=newp
            if sid in STAFF_DB: STAFF_DB[sid]['pass']=newp
            msg=f"Password Reset for {sid} New: {newp}"
        elif act == 'assign_teacher': CLASS_TEACHER_DB[request.form['assign_class']]=request.form['assign_teacher_id']; msg="Assigned"
        elif act == 'add_expense': EXPENSE_DB.append({"date": datetime.date.today().isoformat(), "type": request.form['exp_type'], "title": request.form['exp_title'], "amount": request.form['exp_amount'], "desc": request.form['exp_desc']}); msg="Added"
        elif act == 'add_subject':
            cls=request.form['sub_class']; sub=request.form['sub_name'].strip()
            if cls not in SUBJECT_DB: SUBJECT_DB[cls]=[]
            if sub not in SUBJECT_DB[cls]: SUBJECT_DB[cls].append(sub); msg=f"{sub} added"
        elif act == 'create_exam':
            ex_id=f"EXAM{random.randint(100,999)}"; EXAM_DB.append({"id":ex_id,"name":request.form['exam_name'],"class":request.form['exam_class'],"date":request.form['exam_date'],"subjects":[s.strip() for s in request.form['exam_subjects'].split(',') if s.strip()]}); msg=f"Exam {ex_id} created"
        elif act == 'salary_pay':
            sid=request.form['salary_id']
            if sid in STAFF_DB: STAFF_DB[sid]['salary_status']='Paid' if STAFF_DB[sid]['salary_status']=='Unpaid' else 'Unpaid'; msg=f"Salary for {sid} now {STAFF_DB[sid]['salary_status']}"
        elif act == 'add_student':
            nid=request.form['new_id'].strip().upper(); USERS[nid]={"pass":request.form['new_pass'],"name":request.form['new_name'],"class":request.form['new_class'],"role":"student","parent_no":request.form['parent_no']}; fees_db[nid]={cur:{"status":"Unpaid","amount":"2000"}}; msg=f"Student {nid} added"

    student_rows="".join([f"<tr><td>{k}</td><td>{v['name']}</td><td>{v.get('class','')}</td><td>{CLASS_TEACHER_DB.get(v.get('class',''),'None')}</td><td>{get_fee_status(k)['status']}</td></tr>" for k,v in USERS.items() if v['role']=='student'])
    # NEW: Show ID + Password + Reset
    staff_rows="".join([f"<tr><td>{s['id']}</td><td>{s['name']}</td><td>{s['role']}</td><td style='font-weight:bold'>{s['id']}<br><span style='color:blue'>{s['pass']}</span></td><td>Rs {s['salary']}</td><td><span style='background:{'green' if s['salary_status']=='Paid' else 'red'};color:white;padding:4px 8px;border-radius:12px'>{s['salary_status']}</span></td><td><form method='POST' style='margin:0;display:inline'><input type='hidden' name='admin_action' value='salary_pay'><input type='hidden' name='salary_id' value='{s['id']}'><button class='btn btn-small {'btn-green' if s['salary_status']=='Unpaid' else 'btn-red'}'>{'Mark Paid' if s['salary_status']=='Unpaid' else 'Mark Unpaid'}</button></form> <a href='/salary_slip/{s['id']}' target='_blank' class='btn btn-small btn-blue'>📄 Slip</a><form method='POST' style='margin-top:5px;display:flex;gap:2px'><input type='hidden' name='admin_action' value='reset_pass'><input type='hidden' name='reset_id' value='{s['id']}'><input name='new_password' placeholder='New Pass' style='width:80px;padding:4px'><button class='btn btn-small btn-yellow' style='padding:4px'>Reset</button></form></td></tr>" for s in STAFF_DB.values()])
    expense_rows="".join([f"<tr><td>{e['date']}</td><td>{e['type']}</td><td>{e['title']}</td><td>Rs {e['amount']}</td></tr>" for e in EXPENSE_DB[-15:]]) or "<tr><td colspan=4>No data</td></tr>"
    total_exp = sum(int(e['amount']) for e in EXPENSE_DB if e['type']=='Expense' and str(e['amount']).isdigit())
    total_rev = sum(int(e['amount']) for e in EXPENSE_DB if e['type']=='Revenue' and str(e['amount']).isdigit())
    subject_rows="".join([f"<tr><td>{cls}</td><td>{', '.join(subs)}</td><td>{CLASS_TEACHER_DB.get(cls,'None')}</td></tr>" for cls,subs in SUBJECT_DB.items()])
    exam_rows="".join([f"<tr><td>{ex['id']}</td><td>{ex['name']}</td><td>{ex['class']}</td><td>{ex['date']}</td><td>{', '.join(ex['subjects'])}</td></tr>" for ex in EXAM_DB]) or "<tr><td colspan=5>No exams</td></tr>"
    teacher_opts="".join([f"<option value='{k}'>{k} - {v['name']}</option>" for k,v in STAFF_DB.items() if 'teacher' in v['role'].lower() or v['role']=='teacher']) + "".join([f"<option value='{k}'>{k} - {USERS[k]['name']}</option>" for k in USERS if USERS[k]['role']=='teacher'])
    # Papers for Principal only
    paper_rows = "".join([f"<tr><td>{p['id']}</td><td>{p['exam_name']} ({p['exam_id']})</td><td>{p['class']}</td><td>{p['subject']}</td><td>{p['title']} by {p['teacher']}</td><td>{p['date']}</td><td><a href='/uploads/{p['file']}' target='_blank' class='btn btn-small btn-blue'>📄 View Paper</a></td></tr>" for p in PAPER_DB]) or "<tr><td colspan=7>No papers uploaded by teachers yet</td></tr>"
    assign_rows_admin = "".join([f"<tr><td>{a['class']}</td><td>{a['subject']}</td><td>{a['title']}</td><td>{a['teacher']}</td><td><a href='/uploads/{a['file']}' target='_blank'>View</a></td></tr>" for a in ASSIGNMENT_DB[-10:]]) or "<tr><td colspan=5>No assignments</td></tr>"

    return page_wrap(f'''
    <div class="box" style="max-width:850px"><h2>Admin / Principal Panel</h2><p style="color:green;text-align:center;font-weight:bold">{msg}</p><p style="text-align:center">Month: {cur} | Profit: Rs {total_rev - total_exp} | <a href="/expense_report" target="_blank" class="btn btn-small" style="background:{MAROON}">📊 Expense PDF</a></p>
    <h3>1️⃣ Add Staff - Login Visible + Reset</h3><form method="POST" style="background:#FDF6F0;padding:15px;border-radius:10px;border:2px solid {MAROON}"><input type="hidden" name="admin_action" value="add_staff"><div class="grid2"><input name="staff_id" placeholder="ID TEA002 / PRI001" required><input name="staff_name" placeholder="Full Name" required></div><div class="grid2"><select name="staff_role" required><option value="">Role</option><option value="teacher">Teacher</option><option value="principal">Principal</option><option value="admin">Vice Principal</option><option value="clerk">Clerk</option><option value="peon">Peon</option></select><input name="staff_class" placeholder="Class Incharge"></div><div class="grid2"><input name="staff_phone" placeholder="Phone" required><input name="staff_salary" placeholder="Salary" required></div><input name="staff_pass" placeholder="Login Password e.g. teacher123" required><button class="btn btn-green">➕ Add Staff - ID+Pass Will Show Below</button></form>
    <h3>2️⃣ Staff List - ID + Password + Salary Paid + Reset + Slip</h3><table><tr><th>ID</th><th>Name</th><th>Role</th><th>Login ID / Password</th><th>Salary</th><th>Status</th><th>Actions</th></tr>{staff_rows}</table>
    <h3>📝 Papers Uploaded by Teachers (Only Principal Sees - Exam Type)</h3><table><tr><th>ID</th><th>Exam Type</th><th>Class</th><th>Subject</th><th>Title / Teacher</th><th>Date</th><th>File</th></tr>{paper_rows}</table>
    <h3>📖 Recent Assignments</h3><table><tr><th>Class</th><th>Sub</th><th>Title</th><th>Teacher</th><th>File</th></tr>{assign_rows_admin}</table>
    <h3>3️⃣ Assign Class Teacher</h3><form method="POST"><input type="hidden" name="admin_action" value="assign_teacher"><div class="grid2"><input name="assign_class" placeholder="Class e.g. 10-A" required><select name="assign_teacher_id" required><option value="">Select Teacher</option>{teacher_opts}</select></div><button class="btn btn-yellow">📌 Assign</button></form>
    <h3>4️⃣ Add Student</h3><form method="POST" style="background:#E8F5E9;padding:12px;border-radius:10px"><input type="hidden" name="admin_action" value="add_student"><div class="grid2"><input name="new_id" placeholder="ID NGS002" required><input name="new_name" placeholder="Name" required></div><div class="grid2"><input name="new_class" placeholder="Class" required><input name="new_pass" placeholder="Password" required></div><input name="parent_no" placeholder="Parent WhatsApp" required><button class="btn btn-green">Add Student</button></form><table><tr><th>ID</th><th>Name</th><th>Class</th><th>Teacher</th><th>Fees</th></tr>{student_rows}</table>
    <h3>5️⃣ Add Subjects</h3><form method="POST"><input type="hidden" name="admin_action" value="add_subject"><div class="grid2"><input name="sub_class" placeholder="Class" required><input name="sub_name" placeholder="Subject" required></div><button class="btn">📚 Add Subject</button></form><table><tr><th>Class</th><th>Subjects</th><th>Teacher</th></tr>{subject_rows}</table>
    <h3>6️⃣ Expenses & Revenue</h3><form method="POST" style="background:#FFEBEE;padding:12px;border-radius:10px"><input type="hidden" name="admin_action" value="add_expense"><div class="grid2"><select name="exp_type" required><option value="Expense">Expense</option><option value="Revenue">Revenue</option></select><input name="exp_amount" placeholder="Amount" required></div><input name="exp_title" placeholder="Title" required><input name="exp_desc" placeholder="Desc"><button class="btn btn-red">💰 Add</button></form><table><tr><th>Date</th><th>Type</th><th>Title</th><th>Amount</th></tr>{expense_rows}</table>
    <h3>7️⃣ Create Exam</h3><form method="POST" style="background:#E3F2FD;padding:12px;border-radius:10px"><input type="hidden" name="admin_action" value="create_exam"><input name="exam_name" placeholder="Exam Name e.g. Mid Term" required><div class="grid2"><input name="exam_class" placeholder="Class" required><input name="exam_date" type="date" required></div><input name="exam_subjects" placeholder="Subjects comma separated" required><button class="btn" style="background:#1565C0">📝 Create Exam</button></form><table><tr><th>ID</th><th>Exam</th><th>Class</th><th>Date</th><th>Subjects</th></tr>{exam_rows}</table>
    <a href="/logout" class="btn btn-red">Logout</a></div>''')

@app.route('/download_result/<sid>')
def download_result(sid):
    exam_filter = request.args.get('exam_id','ALL')
    user=USERS.get(sid,{}); 
    html=f'<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{{font-family:Arial;padding:20px}} table{{width:100%;border-collapse:collapse}} th,td{{border:1px solid #ccc;padding:8px}} th{{background:{MAROON};color:white}}</style></head><body><div style="max-width:700px;margin:auto;border:3px solid {MAROON};padding:20px;border-radius:12px"><img src="/logo" style="width:80px;height:80px;border-radius:50%;display:block;margin:auto;border:2px solid {MAROON}"><h1 style="color:{MAROON};text-align:center">NOBLE GRAMMAR SCHOOL - Result Card</h1><p><b>Name:</b> {user.get("name","")} | <b>ID:</b> {sid} | <b>Class:</b> {user.get("class","")} | <b>Teacher:</b> {CLASS_TEACHER_DB.get(user.get("class",""),"")} | <b>Filter:</b> {exam_filter}</p>'
    found=False
    for ex in EXAM_DB:
        if exam_filter!='ALL' and ex['id']!=exam_filter: continue
        if ex['class']==user.get('class','') and ex['id'] in EXAM_MARKS_DB and sid in EXAM_MARKS_DB[ex['id']]:
            subs=EXAM_MARKS_DB[ex['id']][sid]; html+=f"<h3>{ex['name']} - {ex['date']} - {ex['class']}</h3><table><tr><th>Subject</th><th>Marks</th></tr>"
            total=0
            for s,m in subs.items():
                html+=f"<tr><td>{s}</td><td>{m}</td></tr>"
                try: total+=int(m)
                except: pass
            html+=f"<tr><th>Total</th><th>{total}</th></tr></table><br>"; found=True
    if not found: html+="<p style='text-align:center;color:red'>No result for selected exam type. Teacher not yet generated.</p>"
    html+=f"<br><div style='display:flex;justify-content:space-between;margin-top:40px'><div>Class Teacher<br>__________</div><div>Principal<br>__________</div></div><button onclick='window.print()' style='background:{MAROON};color:white;padding:12px;width:100%;margin-top:20px;border:none;border-radius:8px'>🖨️ Print / Save PDF</button></div></body></html>"
    return html

@app.route('/logout')
def logout(): session.clear(); return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting NGS on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)