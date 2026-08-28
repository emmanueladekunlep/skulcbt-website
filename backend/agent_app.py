# agent_app.py
# Main Flask Application for SkulCBT Agent Program
# PythonAnywhere Version - August 2026

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import hashlib
import secrets
import random
import string
from datetime import datetime, timedelta
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Import database functions from agent_models
from agent_models import (
    get_db_connection,
    init_db,
    get_setting,
    update_setting,
    get_agent_by_id,
    get_agent_by_email,
    get_agent_by_referral_code,
    get_all_agents,
    delete_agent,
    get_downline_agents,
    get_agent_rank,
    update_agent_rank,
    update_downline_sales_count,
    release_frozen_recruitment_bonus
)

# ============================================
# FIXED PATHS FOR PYTHONANYWHERE
# ============================================
BASE_DIR = '/home/skulcbt/skulcbt-website'

app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, 'static'),
            template_folder=os.path.join(BASE_DIR, 'frontend'))

app.secret_key = secrets.token_hex(32)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
CORS(app)

# Initialize database
init_db()

# Email Configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'skulcbt@gmail.com'
EMAIL_PASSWORD = 'gzbxielexwnthayy'
EMAIL_FROM = 'skulcbt@gmail.com'


# ============================================
# HELPER FUNCTIONS
# ============================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def generate_referral_code(name):
    prefix = name[:3].upper() if len(name) >= 3 else name.upper()
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"{prefix}{suffix}"


def calculate_commission(price, level=0):
    if level == 0:
        percent = float(get_setting('direct_commission_percent') or 35)
    elif level == 1:
        percent = float(get_setting('level1_commission_percent') or 5)
    elif level == 2:
        percent = float(get_setting('level2_commission_percent') or 3)
    elif level == 3:
        percent = float(get_setting('level3_commission_percent') or 1)
    else:
        percent = 0

    return (percent / 100) * price


def get_level_agents(agent_id, level=1):
    conn = get_db_connection()
    cursor = conn.cursor()

    if level == 1:
        cursor.execute('SELECT * FROM agents WHERE referred_by = (SELECT referral_code FROM agents WHERE id = ?)', (agent_id,))
        agents = cursor.fetchall()
        conn.close()
        return agents

    elif level == 2:
        cursor.execute('''
            SELECT * FROM agents
            WHERE referred_by IN (
                SELECT referral_code FROM agents
                WHERE referred_by = (SELECT referral_code FROM agents WHERE id = ?)
            )
        ''', (agent_id,))
        agents = cursor.fetchall()
        conn.close()
        return agents

    elif level == 3:
        cursor.execute('''
            SELECT * FROM agents
            WHERE referred_by IN (
                SELECT referral_code FROM agents
                WHERE referred_by IN (
                    SELECT referral_code FROM agents
                    WHERE referred_by = (SELECT referral_code FROM agents WHERE id = ?)
                )
            )
        ''', (agent_id,))
        agents = cursor.fetchall()
        conn.close()
        return agents

    conn.close()
    return []


def get_all_downline(agent_id):
    level1 = get_level_agents(agent_id, 1)
    level2 = get_level_agents(agent_id, 2)
    level3 = get_level_agents(agent_id, 3)

    return {
        'level1': list(level1),
        'level2': list(level2),
        'level3': list(level3)
    }


# ============================================
# EMAIL FUNCTION
# ============================================

def send_email(to_email, subject, body):
    if not to_email or not to_email.strip():
        print(f"❌ No email address provided")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Email failed to {to_email}: {e}")
        return False


# ============================================
# AUTHENTICATION DECORATORS
# ============================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'agent_id' not in session:
            return redirect(url_for('agent_login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================
# PUBLIC ROUTES
# ============================================

@app.route('/')
def index():
    return redirect(url_for('agent_login'))


@app.route('/agent/login')
def agent_login():
    return render_template('agent/login.html')


@app.route('/agent/register')
def agent_register():
    ref_code = request.args.get('ref', '')
    return render_template('agent/register.html', referral_code=ref_code)


# ============================================
# AGENT AUTHENTICATION API ROUTES
# ============================================

@app.route('/api/agent/register', methods=['POST'])
def api_agent_register():
    data = request.get_json()

    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip().lower()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    referred_by = data.get('referred_by', '').strip()

    if not full_name or not email or not phone or not password:
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    existing = get_agent_by_email(email)
    if existing:
        return jsonify({'success': False, 'message': 'Email already registered'}), 400

    referrer = None
    if referred_by:
        referrer = get_agent_by_referral_code(referred_by)
        if not referrer:
            return jsonify({'success': False, 'message': 'Invalid referral code'}), 400

    referral_code = generate_referral_code(full_name)

    existing_code = get_agent_by_referral_code(referral_code)
    if existing_code:
        referral_code = generate_referral_code(full_name + datetime.now().strftime('%S'))

    free_count = int(get_setting('free_registration_count') or 0)
    free_limit = int(get_setting('free_registration_limit') or 50)
    registration_fee = 0 if free_count < free_limit else float(get_setting('registration_fee') or 10000)

    password_hash = hash_password(password)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO agents (
                full_name, email, phone, password_hash, referral_code,
                referred_by, registration_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (full_name, email, phone, password_hash, referral_code,
              referrer['referral_code'] if referrer else None,
              datetime.now().strftime('%Y-%m-%d'), 'active'))

        agent_id = cursor.lastrowid

        if free_count < free_limit:
            cursor.execute('''
                UPDATE settings
                SET setting_value = ?, updated_at = CURRENT_TIMESTAMP
                WHERE setting_key = 'free_registration_count'
            ''', (str(free_count + 1),))

        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'}), 500
    finally:
        conn.close()

    return jsonify({
        'success': True,
        'message': 'Registration successful. Please login.',
        'registration_fee': registration_fee
    })


@app.route('/api/agent/login', methods=['POST'])
def api_agent_login():
    data = request.get_json()

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password required'}), 400

    agent = get_agent_by_email(email)

    if not agent:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

    if hash_password(password) != agent['password_hash']:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

    session['agent_id'] = agent['id']
    session['agent_name'] = agent['full_name']
    session['agent_referral_code'] = agent['referral_code']
    session.permanent = True

    return jsonify({
        'success': True,
        'message': 'Login successful',
        'redirect': '/agent/dashboard'
    })


@app.route('/api/agent/logout', methods=['POST'])
def api_agent_logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})


# ============================================
# AGENT DASHBOARD ROUTES - FIXED WITH LICENSE KEY
# ============================================

@app.route('/agent/dashboard')
@login_required
def agent_dashboard():
    return render_template('agent/dashboard.html')


@app.route('/api/agent/dashboard')
@login_required
def api_agent_dashboard():
    agent_id = session['agent_id']
    agent = get_agent_by_id(agent_id)

    if not agent:
        return jsonify({'success': False, 'message': 'Agent not found'}), 404

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as count FROM sales WHERE agent_id = ?', (agent_id,))
    total_sales = cursor.fetchone()['count']

    cursor.execute('SELECT SUM(commission) as total FROM sales WHERE agent_id = ?', (agent_id,))
    total_commission = cursor.fetchone()['total'] or 0

    downline = get_all_downline(agent_id)
    downline_count = len(downline['level1'])

    cursor.execute('''
        SELECT COUNT(*) as total FROM sales s
        JOIN agents a ON s.agent_id = a.id
        WHERE a.referred_by = (SELECT referral_code FROM agents WHERE id = ?)
    ''', (agent_id,))
    downline_sales_result = cursor.fetchone()
    downline_sales_count = downline_sales_result['total'] if downline_sales_result else 0

    # FIXED: Include license key from license_keys table
    cursor.execute('''
        SELECT s.*, l.license_key 
        FROM sales s
        LEFT JOIN license_keys l ON s.id = l.sale_id
        WHERE s.agent_id = ?
        ORDER BY s.created_at DESC
        LIMIT 5
    ''', (agent_id,))
    recent_sales = cursor.fetchall()

    cursor.execute('''
        SELECT * FROM commissions
        WHERE agent_id = ?
        ORDER BY created_at DESC
        LIMIT 5
    ''', (agent_id,))
    recent_commissions = cursor.fetchall()

    conn.close()

    # Get recruitment bonus balance safely using dictionary conversion
    agent_dict = dict(agent)
    recruitment_bonus_balance = agent_dict.get('recruitment_bonus_balance', 0)
    
    total_balance = float(agent_dict['balance']) + float(recruitment_bonus_balance)

    return jsonify({
        'success': True,
        'agent': agent_dict,
        'stats': {
            'total_sales': total_sales,
            'total_commission': float(total_commission),
            'balance': total_balance,
            'withdrawable_balance': float(agent_dict['balance']),
            'frozen_balance': float(recruitment_bonus_balance),
            'downline_count': downline_count,
            'rank': agent_dict['rank'],
            'downline_sales_count': downline_sales_count
        },
        'recent_sales': [dict(s) for s in recent_sales],
        'recent_commissions': [dict(c) for c in recent_commissions]
    })


# ============================================
# AGENT DOWNLINE ROUTES
# ============================================

@app.route('/agent/downline')
@login_required
def agent_downline():
    return render_template('agent/downline.html')


@app.route('/api/agent/downline')
@login_required
def api_agent_downline():
    agent_id = session['agent_id']
    agent = get_agent_by_id(agent_id)

    if not agent:
        return jsonify({'success': False, 'message': 'Agent not found'}), 404

    downline = get_all_downline(agent_id)

    result = {
        'level1': [],
        'level2': [],
        'level3': []
    }

    conn = get_db_connection()
    cursor = conn.cursor()

    for level in ['level1', 'level2', 'level3']:
        for a in downline[level]:
            agent_dict = dict(a)
            
            # Get sales count for this downline agent
            cursor.execute('SELECT COUNT(*) as count FROM sales WHERE agent_id = ? AND status = "approved"', (a['id'],))
            sales_count = cursor.fetchone()['count']
            agent_dict['sales_count'] = sales_count
            
            result[level].append(agent_dict)

    conn.close()

    return jsonify({
        'success': True,
        'level1': result['level1'],
        'level2': result['level2'],
        'level3': result['level3'],
        'counts': {
            'level1': len(result['level1']),
            'level2': len(result['level2']),
            'level3': len(result['level3']),
            'total': len(result['level1']) + len(result['level2']) + len(result['level3'])
        }
    })


# ============================================
# AGENT SALES ROUTES
# ============================================

@app.route('/agent/sales')
@login_required
def agent_sales():
    return render_template('agent/sales.html')


@app.route('/api/agent/sales')
@login_required
def api_agent_sales():
    agent_id = session['agent_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM sales
        WHERE agent_id = ?
        ORDER BY created_at DESC
    ''', (agent_id,))

    sales = cursor.fetchall()
    conn.close()

    return jsonify({
        'success': True,
        'sales': [dict(s) for s in sales]
    })


# ============================================
# AGENT COMMISSIONS ROUTES
# ============================================

@app.route('/agent/commissions')
@login_required
def agent_commissions():
    return render_template('agent/commissions.html')


@app.route('/api/agent/commissions')
@login_required
def api_agent_commissions():
    agent_id = session['agent_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM commissions
        WHERE agent_id = ?
        ORDER BY created_at DESC
    ''', (agent_id,))

    commissions = cursor.fetchall()

    cursor.execute('SELECT SUM(amount) as total FROM commissions WHERE agent_id = ? AND paid = 1', (agent_id,))
    paid_total = cursor.fetchone()['total'] or 0

    cursor.execute('SELECT SUM(amount) as total FROM commissions WHERE agent_id = ? AND paid = 0', (agent_id,))
    pending_total = cursor.fetchone()['total'] or 0

    conn.close()

    return jsonify({
        'success': True,
        'commissions': [dict(c) for c in commissions],
        'paid_total': float(paid_total),
        'pending_total': float(pending_total)
    })


# ============================================
# AGENT WITHDRAWAL ROUTES
# ============================================

@app.route('/agent/withdraw')
@login_required
def agent_withdraw():
    return render_template('agent/withdraw.html')


@app.route('/api/agent/withdraw', methods=['POST'])
@login_required
def api_agent_withdraw():
    agent_id = session['agent_id']
    data = request.get_json()

    amount = float(data.get('amount', 0))
    bank_name = data.get('bank_name', '').strip()
    account_number = data.get('account_number', '').strip()
    account_name = data.get('account_name', '').strip()

    if amount <= 0:
        return jsonify({'success': False, 'message': 'Amount must be greater than zero'}), 400

    min_withdrawal = float(get_setting('minimum_withdrawal') or 10000)
    if amount < min_withdrawal:
        return jsonify({'success': False, 'message': f'Minimum withdrawal is ₦{min_withdrawal:,.0f}'}), 400

    agent = get_agent_by_id(agent_id)
    if not agent:
        return jsonify({'success': False, 'message': 'Agent not found'}), 404

    # Only allow withdrawal from main balance, not frozen
    if amount > agent['balance']:
        return jsonify({'success': False, 'message': f'Insufficient withdrawable balance. You have ₦{agent["balance"]:,.0f} available.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE agents SET
            balance = balance - ?,
            bank_name = ?,
            account_number = ?,
            account_name = ?
        WHERE id = ?
    ''', (amount, bank_name, account_number, account_name, agent_id))

    cursor.execute('''
        INSERT INTO withdrawals (agent_id, amount, request_date, status, bank_name, account_number, account_name)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (agent_id, amount, datetime.now().strftime('%Y-%m-%d'), 'pending', bank_name, account_number, account_name))

    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': f'Withdrawal request of ₦{amount:,.0f} submitted successfully'
    })


@app.route('/api/agent/withdrawals')
@login_required
def api_agent_withdrawals():
    agent_id = session['agent_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM withdrawals
        WHERE agent_id = ?
        ORDER BY created_at DESC
    ''', (agent_id,))

    withdrawals = cursor.fetchall()
    conn.close()

    return jsonify({
        'success': True,
        'withdrawals': [dict(w) for w in withdrawals]
    })


# ============================================
# AGENT GENERATE LICENSE ROUTES
# ============================================

@app.route('/agent/generate')
@login_required
def agent_generate():
    return render_template('agent/generate.html')


@app.route('/api/agent/pending-sales')
@login_required
def api_agent_pending_sales():
    agent_id = session['agent_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM sales
        WHERE agent_id = ? AND status = 'pending'
        ORDER BY created_at DESC
    ''', (agent_id,))
    sales = cursor.fetchall()
    conn.close()

    return jsonify({
        'success': True,
        'sales': [dict(s) for s in sales]
    })


@app.route('/api/agent/sales', methods=['POST'])
@login_required
def api_agent_create_sale():
    agent_id = session['agent_id']
    data = request.get_json()

    school_name = data.get('school_name', '').strip()
    school_email = data.get('school_email', '').strip()
    school_phone = data.get('school_phone', '').strip()
    tier = data.get('tier', '').strip()
    plan = data.get('plan', '').strip()
    price = float(data.get('price', 0))
    commission = float(data.get('commission', 0))

    if not school_name or not school_email or not tier or not plan:
        return jsonify({'success': False, 'message': 'School name, email, tier, and plan are required'}), 400

    if price <= 0:
        return jsonify({'success': False, 'message': 'Invalid price'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO sales (
            agent_id, school_name, school_email, school_phone,
            tier, plan, price, commission, status, sale_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (agent_id, school_name, school_email, school_phone,
          tier, plan, price, commission, 'pending',
          datetime.now().strftime('%Y-%m-%d')))

    sale_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': f'Sale recorded successfully! Waiting for admin approval. You will earn ₦{commission:,.0f} when approved.',
        'sale_id': sale_id
    })


# ============================================
# ADMIN ROUTES
# ============================================

@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')


@app.route('/api/admin/login', methods=['POST'])
def api_admin_login():
    data = request.get_json()

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if username == 'admin' and password == 'Lawrenceamanda1*':
        session['admin'] = True
        session['admin_name'] = 'Administrator'
        session.permanent = True
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'redirect': '/admin/dashboard'
        })

    return jsonify({'success': False, 'message': 'Invalid username or password'}), 401


@app.route('/api/admin/logout', methods=['POST'])
def api_admin_logout():
    session.pop('admin', None)
    session.pop('admin_name', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'})


@app.route('/api/admin/dashboard')
@admin_required
def api_admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as count FROM agents')
    total_agents = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM agents WHERE status = "active"')
    active_agents = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM sales')
    total_sales = cursor.fetchone()['count']

    cursor.execute('SELECT SUM(price) as total FROM sales WHERE status = "approved"')
    total_revenue = cursor.fetchone()['total'] or 0

    cursor.execute('SELECT SUM(amount) as total FROM commissions WHERE paid = 1')
    total_commissions = cursor.fetchone()['total'] or 0

    cursor.execute('SELECT COUNT(*) as count FROM sales WHERE status = "pending"')
    pending_sales = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM withdrawals WHERE status = "pending"')
    pending_withdrawals = cursor.fetchone()['count']

    cursor.execute('SELECT * FROM agents ORDER BY created_at DESC LIMIT 5')
    recent_agents = cursor.fetchall()

    cursor.execute('SELECT * FROM sales ORDER BY created_at DESC LIMIT 5')
    recent_sales = cursor.fetchall()

    conn.close()

    return jsonify({
        'success': True,
        'stats': {
            'total_agents': total_agents,
            'active_agents': active_agents,
            'total_sales': total_sales,
            'total_revenue': float(total_revenue),
            'total_commissions': float(total_commissions),
            'pending_sales': pending_sales,
            'pending_withdrawals': pending_withdrawals
        },
        'recent_agents': [dict(a) for a in recent_agents],
        'recent_sales': [dict(s) for s in recent_sales]
    })


@app.route('/api/admin/agents')
@admin_required
def api_admin_agents():
    agents = get_all_agents()
    return jsonify({
        'success': True,
        'agents': [dict(a) for a in agents]
    })


@app.route('/api/admin/agents/delete/<int:agent_id>', methods=['DELETE'])
@admin_required
def api_admin_delete_agent(agent_id):
    delete_agent(agent_id)
    return jsonify({'success': True, 'message': 'Agent deleted successfully'})


@app.route('/api/admin/sales')
@admin_required
def api_admin_sales():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM sales ORDER BY created_at DESC')
    sales = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) as count FROM sales')
    total_sales = cursor.fetchone()['count']

    cursor.execute('SELECT SUM(price) as total FROM sales WHERE status = "approved"')
    total_revenue = cursor.fetchone()['total'] or 0

    cursor.execute('SELECT SUM(commission) as total FROM sales WHERE status = "approved"')
    total_commission = cursor.fetchone()['total'] or 0

    cursor.execute('SELECT COUNT(*) as count FROM sales WHERE status = "pending"')
    pending_sales = cursor.fetchone()['count']

    conn.close()

    return jsonify({
        'success': True,
        'sales': [dict(s) for s in sales],
        'stats': {
            'total_sales': total_sales,
            'total_revenue': float(total_revenue),
            'total_commission': float(total_commission),
            'pending_sales': pending_sales
        }
    })


# ============================================
# ADMIN AGENT TREE ROUTE
# ============================================

@app.route('/api/admin/agent-tree/<int:agent_id>')
@admin_required
def api_admin_agent_tree(agent_id):
    agent = get_agent_by_id(agent_id)
    if not agent:
        return jsonify({'success': False, 'message': 'Agent not found'}), 404

    downline = get_all_downline(agent_id)

    result = {
        'level1': [],
        'level2': [],
        'level3': []
    }

    conn = get_db_connection()
    cursor = conn.cursor()

    for level in ['level1', 'level2', 'level3']:
        for a in downline[level]:
            agent_dict = dict(a)
            cursor.execute('SELECT COUNT(*) as count FROM sales WHERE agent_id = ? AND status = "approved"', (a['id'],))
            sales_count = cursor.fetchone()['count']
            agent_dict['sales_count'] = sales_count
            result[level].append(agent_dict)

    conn.close()

    return jsonify({
        'success': True,
        'agent': dict(agent),
        'level1': result['level1'],
        'level2': result['level2'],
        'level3': result['level3'],
        'counts': {
            'level1': len(result['level1']),
            'level2': len(result['level2']),
            'level3': len(result['level3']),
            'total': len(result['level1']) + len(result['level2']) + len(result['level3'])
        }
    })


# ============================================
# ADMIN TOP PERFORMING AGENTS
# ============================================

@app.route('/api/admin/top-agents')
@admin_required
def api_admin_top_agents():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            id, full_name, email, phone, rank, status,
            total_sales, total_commission, balance,
            (SELECT COUNT(*) FROM agents WHERE referred_by = a.referral_code) as downline_count,
            (SELECT COUNT(*) FROM sales WHERE agent_id = a.id AND status = 'approved') as approved_sales
        FROM agents a
        WHERE status = 'active'
        ORDER BY total_sales DESC, total_commission DESC
        LIMIT 20
    ''')
    top_agents = cursor.fetchall()

    conn.close()

    return jsonify({
        'success': True,
        'agents': [dict(a) for a in top_agents]
    })


# ============================================
# ADMIN APPROVE SALE - FIXED
# ============================================

@app.route('/api/admin/sales/approve/<int:sale_id>', methods=['POST'])
@admin_required
def api_admin_approve_sale(sale_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM sales WHERE id = ?', (sale_id,))
        sale = cursor.fetchone()

        if not sale:
            conn.close()
            return jsonify({'success': False, 'message': 'Sale not found'}), 404

        if sale['status'] != 'pending':
            conn.close()
            return jsonify({'success': False, 'message': 'Sale is not pending'}), 400

        # Generate license key
        tier_map = {'ESS': 'ES', 'PRO': 'PR', 'ENT': 'EN'}
        plan_map = {'TERMLY': 'TM', 'YEARLY': 'YR', 'LIFETIME': 'LF'}

        tier_short = tier_map.get(sale['tier'], 'PK')
        plan_short = plan_map.get(sale['plan'], 'PL')

        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        license_key = f"SKUL-{tier_short}-{plan_short}-{random_part}"

        # Update sale status
        cursor.execute('UPDATE sales SET status = "approved" WHERE id = ?', (sale_id,))

        # SAVE LICENSE KEY TO DATABASE WITH SCHOOL NAME
        if sale['plan'] == 'LIFETIME':
            expiry_date = 'LIFETIME'
        else:
            days = 90 if sale['plan'] == 'TERMLY' else 365
            expiry_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')

        cursor.execute('''
            INSERT INTO license_keys (
                license_key, school_name, tier, plan, price,
                agent_id, sale_id, created_date, expiry_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (license_key, sale['school_name'], sale['tier'], sale['plan'],
              sale['price'], sale['agent_id'], sale_id,
              datetime.now().strftime('%Y-%m-%d'), expiry_date, 'active'))

        # Level 0: Direct agent commission (35%) - goes to main balance
        cursor.execute('''
            UPDATE agents SET
                balance = balance + ?,
                total_sales = total_sales + 1,
                total_commission = total_commission + ?
            WHERE id = ?
        ''', (sale['commission'], sale['commission'], sale['agent_id']))

        cursor.execute('''
            INSERT INTO commissions (agent_id, sale_id, level, amount, paid, created_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (sale['agent_id'], sale_id, 0, sale['commission'], 1, datetime.now().strftime('%Y-%m-%d')))

        # Get selling agent details for emails
        cursor.execute('SELECT full_name, email FROM agents WHERE id = ?', (sale['agent_id'],))
        selling_agent = cursor.fetchone()

        # ============================================
        # SEND EMAIL TO SELLING AGENT
        # ============================================
        if selling_agent and selling_agent['email']:
            tier_names = {'ESS': 'Essential', 'PRO': 'Professional', 'ENT': 'Enterprise'}
            plan_names = {'TERMLY': 'Termly (90 days)', 'YEARLY': 'Yearly (365 days)', 'LIFETIME': 'Lifetime (Never Expires)'}
            
            email_body = f"""
🎉 YOUR SALE HAS BEEN APPROVED! 🎉

Dear {selling_agent['full_name']},

Congratulations! Your sale has been approved by the administrator.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 SALE DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
School Name: {sale['school_name']}
School Email: {sale['school_email']}
Tier: {tier_names.get(sale['tier'], sale['tier'])}
Plan: {plan_names.get(sale['plan'], sale['plan'])}
Sale Price: ₦{sale['price']:,.0f}
Your Commission: ₦{sale['commission']:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔑 LICENSE KEY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{license_key}

Please provide this license key to the school.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 NEED HELP?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Contact: Emmanuel Adekunle Peace
Phone: 07032977572
Email: emmanueladekunlep@gmail.com

Thank you for being a SkulCBT Agent! 🚀
"""
            print(f"📧 Sending approval email to: {selling_agent['email']}")
            send_email(selling_agent['email'], "🎉 Your Sale Has Been Approved - SkulCBT", email_body)

        # ============================================
        # UPLINE COMMISSIONS (Level 1, 2, 3) - goes to main balance
        # ============================================
        cursor.execute('SELECT referral_code FROM agents WHERE id = ?', (sale['agent_id'],))
        current_agent = cursor.fetchone()

        if current_agent:
            current_referral_code = current_agent['referral_code']
            level = 1

            while level <= 3:
                cursor.execute('SELECT referred_by FROM agents WHERE referral_code = ?', (current_referral_code,))
                upline = cursor.fetchone()

                if not upline or not upline['referred_by']:
                    break

                cursor.execute('SELECT id FROM agents WHERE referral_code = ?', (upline['referred_by'],))
                upline_agent = cursor.fetchone()

                if not upline_agent:
                    break

                if level == 1:
                    percent = 0.05
                elif level == 2:
                    percent = 0.03
                elif level == 3:
                    percent = 0.01

                level_amount = sale['price'] * percent

                if level_amount > 0:
                    cursor.execute('UPDATE agents SET balance = balance + ? WHERE id = ?', (level_amount, upline_agent['id']))
                    cursor.execute('''
                        INSERT INTO commissions (agent_id, sale_id, level, amount, paid, created_date)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (upline_agent['id'], sale_id, level, level_amount, 1, datetime.now().strftime('%Y-%m-%d')))

                    cursor.execute('SELECT full_name, email FROM agents WHERE id = ?', (upline_agent['id'],))
                    upline_info = cursor.fetchone()

                    if upline_info and upline_info['email'] and selling_agent:
                        level_names = {1: 'Level 1 (Direct Upline)', 2: 'Level 2 (Upline)', 3: 'Level 3 (Upline)'}
                        
                        email_body = f"""
💰 YOU EARNED A COMMISSION FROM YOUR DOWNLINE! 💰

Dear {upline_info['full_name']},

Great news! Your downline agent made a sale!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 COMMISSION DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Agent Who Sold: {selling_agent['full_name']}
School: {sale['school_name']}
Sale Price: ₦{sale['price']:,.0f}
Your Level: {level_names.get(level, 'Level ' + str(level))}
Your Commission: ₦{level_amount:,.0f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 NEED HELP?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Contact: Emmanuel Adekunle Peace
Phone: 07032977572
Email: emmanueladekunlep@gmail.com

Keep building your downline! 🚀
"""
                        print(f"📧 Sending commission email to upline: {upline_info['email']}")
                        send_email(upline_info['email'], "💰 You Earned Commission from Your Downline - SkulCBT", email_body)

                current_referral_code = upline['referred_by']
                level += 1

        # ============================================
        # RECRUITMENT BONUS (First Sale Only) - goes to FROZEN balance
        # ============================================
        cursor.execute('SELECT COUNT(*) as count FROM sales WHERE agent_id = ? AND status = "approved"', (sale['agent_id'],))
        sales_count = cursor.fetchone()['count']

        if sales_count == 1:
            cursor.execute('SELECT referred_by FROM agents WHERE id = ?', (sale['agent_id'],))
            agent = cursor.fetchone()

            if agent and agent['referred_by']:
                cursor.execute('SELECT id FROM agents WHERE referral_code = ?', (agent['referred_by'],))
                referrer = cursor.fetchone()

                if referrer:
                    recruitment_bonus = float(get_setting('recruitment_bonus') or 5000)
                    cursor.execute('UPDATE agents SET recruitment_bonus_balance = recruitment_bonus_balance + ? WHERE id = ?',
                                   (recruitment_bonus, referrer['id']))
                    cursor.execute('''
                        INSERT INTO commissions (agent_id, sale_id, level, amount, paid, created_date)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (referrer['id'], sale_id, 0, recruitment_bonus, 1, datetime.now().strftime('%Y-%m-%d')))

                    cursor.execute('SELECT full_name, email FROM agents WHERE id = ?', (referrer['id'],))
                    referrer_info = cursor.fetchone()

                    if referrer_info and referrer_info['email'] and selling_agent:
                        email_body = f"""
🎊 CONGRATULATIONS! YOU EARNED A RECRUITMENT BONUS! 🎊

Dear {referrer_info['full_name']},

Excellent news! Someone you recruited just made their FIRST sale!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 BONUS DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
New Agent: {selling_agent['full_name']}
This is their FIRST sale! 🎉
Recruitment Bonus: ₦{recruitment_bonus:,.0f}

⚠️ This bonus is FROZEN until your downline makes a sale.
Once your downline makes a sale, it will automatically become withdrawable.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 NEED HELP?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Contact: Emmanuel Adekunle Peace
Phone: 07032977572
Email: emmanueladekunlep@gmail.com

Keep recruiting! 🚀
"""
                        print(f"📧 Sending recruitment bonus email to: {referrer_info['email']}")
                        send_email(referrer_info['email'], "🎊 You Earned a Recruitment Bonus - SkulCBT", email_body)

        # ============================================
        # RELEASE FROZEN BONUSES FOR ALL UPLINE AGENTS IF THEY HAVE DOWNLINE SALES
        # ============================================
        cursor.execute('SELECT referral_code FROM agents WHERE id = ?', (sale['agent_id'],))
        current_agent = cursor.fetchone()
        
        if current_agent:
            current_referral_code = current_agent['referral_code']
            while True:
                cursor.execute('SELECT referred_by FROM agents WHERE referral_code = ?', (current_referral_code,))
                upline = cursor.fetchone()
                if not upline or not upline['referred_by']:
                    break
                cursor.execute('SELECT id FROM agents WHERE referral_code = ?', (upline['referred_by'],))
                upline_agent = cursor.fetchone()
                if not upline_agent:
                    break
                
                # Check if this upline agent has downline sales
                cursor.execute('''
                    SELECT COUNT(*) as count FROM sales s
                    JOIN agents a ON s.agent_id = a.id
                    WHERE a.referred_by = (SELECT referral_code FROM agents WHERE id = ?)
                    AND s.status = 'approved'
                ''', (upline_agent['id'],))
                downline_sales = cursor.fetchone()['count']
                
                if downline_sales > 0:
                    # Release frozen bonus using the connection
                    release_frozen_recruitment_bonus(conn, upline_agent['id'])
                    print(f"✅ Released frozen bonuses for agent {upline_agent['id']}")
                
                current_referral_code = upline['referred_by']

        # Update downline sales count for all upline agents
        cursor.execute('SELECT referral_code FROM agents WHERE id = ?', (sale['agent_id'],))
        current_agent = cursor.fetchone()
        
        if current_agent:
            current_referral_code = current_agent['referral_code']
            while True:
                cursor.execute('SELECT referred_by FROM agents WHERE referral_code = ?', (current_referral_code,))
                upline = cursor.fetchone()
                if not upline or not upline['referred_by']:
                    break
                cursor.execute('SELECT id FROM agents WHERE referral_code = ?', (upline['referred_by'],))
                upline_agent = cursor.fetchone()
                if not upline_agent:
                    break
                # Use the existing connection for update_downline_sales_count
                cursor.execute('''
                    SELECT COUNT(*) as total_sales FROM sales s
                    JOIN agents a ON s.agent_id = a.id
                    WHERE a.referred_by = (SELECT referral_code FROM agents WHERE id = ?)
                    AND s.status = 'approved'
                ''', (upline_agent['id'],))
                result = cursor.fetchone()
                count = result['total_sales'] if result else 0
                cursor.execute('UPDATE agents SET downline_sales_count = ? WHERE id = ?', (count, upline_agent['id']))
                current_referral_code = upline['referred_by']

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Sale approved! License key: {license_key}',
            'license_key': license_key
        })

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"❌ Error approving sale: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/api/admin/sales/reject/<int:sale_id>', methods=['POST'])
@admin_required
def api_admin_reject_sale(sale_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM sales WHERE id = ?', (sale_id,))
    sale = cursor.fetchone()

    if not sale:
        conn.close()
        return jsonify({'success': False, 'message': 'Sale not found'}), 404

    cursor.execute('UPDATE sales SET status = "rejected" WHERE id = ?', (sale_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Sale rejected'})


@app.route('/api/admin/sales/delete/<int:sale_id>', methods=['DELETE'])
@admin_required
def api_admin_delete_sale(sale_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM sales WHERE id = ?', (sale_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Sale deleted successfully'})


@app.route('/api/admin/withdrawals')
@admin_required
def api_admin_withdrawals():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT w.*, a.full_name as agent_name
        FROM withdrawals w
        JOIN agents a ON w.agent_id = a.id
        ORDER BY w.created_at DESC
    ''')
    withdrawals = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) as count FROM withdrawals')
    total_withdrawals = cursor.fetchone()['count']

    cursor.execute('SELECT SUM(amount) as total FROM withdrawals')
    total_amount = cursor.fetchone()['total'] or 0

    cursor.execute('SELECT COUNT(*) as count FROM withdrawals WHERE status = "pending"')
    pending_count = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM withdrawals WHERE status = "approved"')
    approved_count = cursor.fetchone()['count']

    conn.close()

    return jsonify({
        'success': True,
        'withdrawals': [dict(w) for w in withdrawals],
        'stats': {
            'total_withdrawals': total_withdrawals,
            'total_amount': float(total_amount),
            'pending_count': pending_count,
            'approved_count': approved_count
        }
    })


@app.route('/api/admin/withdrawals/approve/<int:withdrawal_id>', methods=['POST'])
@admin_required
def api_admin_approve_withdrawal(withdrawal_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE withdrawals SET status = "approved", approval_date = ? WHERE id = ?',
                   (datetime.now().strftime('%Y-%m-%d'), withdrawal_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Withdrawal approved'})


@app.route('/api/admin/withdrawals/reject/<int:withdrawal_id>', methods=['POST'])
@admin_required
def api_admin_reject_withdrawal(withdrawal_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE withdrawals SET status = "rejected" WHERE id = ?', (withdrawal_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Withdrawal rejected'})


@app.route('/api/admin/reports/<string:report_type>')
@admin_required
def api_admin_report(report_type):
    conn = get_db_connection()
    cursor = conn.cursor()

    if report_type == 'agents':
        cursor.execute('SELECT full_name as Agent, email as Email, total_sales as Sales, total_commission as Commission, rank as Rank FROM agents ORDER BY total_sales DESC')
        title = 'Agent Performance Report'
    elif report_type == 'sales':
        cursor.execute('SELECT school_name as School, tier as Tier, plan as Plan, price as Price, commission as Commission, sale_date as Date FROM sales ORDER BY created_at DESC')
        title = 'Sales Summary Report'
    elif report_type == 'commissions':
        cursor.execute('SELECT a.full_name as Agent, c.amount as Amount, c.level as Level, c.paid as Paid, c.created_date as Date FROM commissions c JOIN agents a ON c.agent_id = a.id ORDER BY c.created_at DESC')
        title = 'Commission Report'
    elif report_type == 'withdrawals':
        cursor.execute('SELECT a.full_name as Agent, w.amount as Amount, w.status as Status, w.request_date as Date FROM withdrawals w JOIN agents a ON w.agent_id = a.id ORDER BY w.created_at DESC')
        title = 'Withdrawal Report'
    elif report_type == 'licenses':
        cursor.execute('SELECT license_key as "License Key", school_name as "School Name", tier as Tier, plan as Plan, price as Price, status as Status, created_date as "Created Date", expiry_date as "Expiry Date" FROM license_keys ORDER BY created_at DESC')
        title = 'License Report'
    else:
        conn.close()
        return jsonify({'success': False, 'message': 'Invalid report type'}), 400

    data = cursor.fetchall()
    conn.close()

    return jsonify({
        'success': True,
        'title': title,
        'data': [dict(row) for row in data]
    })


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')


@app.route('/admin/agents')
@admin_required
def admin_agents():
    return render_template('admin/agents.html')


@app.route('/admin/sales')
@admin_required
def admin_sales():
    return render_template('admin/sales.html')


@app.route('/admin/licenses')
@admin_required
def admin_licenses():
    return render_template('admin/licenses.html')


@app.route('/admin/withdrawals')
@admin_required
def admin_withdrawals():
    return render_template('admin/withdrawals.html')


@app.route('/admin/reports')
@admin_required
def admin_reports():
    return render_template('admin/reports.html')


# ============================================
# LICENSE VALIDATION API
# ============================================

@app.route('/api/validate-license', methods=['POST'])
def api_validate_license():
    data = request.get_json()

    license_key = data.get('license_key', '').strip().upper()
    school_name = data.get('school_name', '').strip()

    if not license_key or not school_name:
        return jsonify({
            'success': False,
            'message': 'License key and school name are required'
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM license_keys
        WHERE license_key = ? AND school_name = ?
    ''', (license_key, school_name))

    license_data = cursor.fetchone()

    if not license_data:
        conn.close()
        return jsonify({
            'success': False,
            'message': 'Invalid license key or school name does not match'
        }), 404

    if license_data['expiry_date'] and license_data['expiry_date'] != 'LIFETIME':
        from datetime import datetime
        expiry = datetime.strptime(license_data['expiry_date'], '%Y-%m-%d')
        if datetime.now() > expiry:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'License has expired'
            }), 403

    if not license_data['activated_at']:
        cursor.execute('''
            UPDATE license_keys SET activated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (license_data['id'],))
        conn.commit()

    conn.close()

    return jsonify({
        'success': True,
        'message': 'License is valid',
        'data': {
            'school_name': license_data['school_name'],
            'tier': license_data['tier'],
            'plan': license_data['plan'],
            'expiry_date': license_data['expiry_date']
        }
    })


# ============================================
# ADMIN LICENSES API ROUTE
# ============================================

@app.route('/api/admin/licenses')
@admin_required
def api_admin_licenses():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT l.*, a.full_name as agent_name
        FROM license_keys l
        LEFT JOIN agents a ON l.agent_id = a.id
        ORDER BY l.created_at DESC
    ''')
    licenses = cursor.fetchall()

    cursor.execute('SELECT COUNT(*) as count FROM license_keys')
    total_licenses = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM license_keys WHERE status = "active"')
    active_licenses = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM license_keys WHERE status = "expired"')
    expired_licenses = cursor.fetchone()['count']

    cursor.execute('SELECT SUM(price) as total FROM license_keys')
    total_revenue = cursor.fetchone()['total'] or 0

    conn.close()

    return jsonify({
        'success': True,
        'licenses': [dict(l) for l in licenses],
        'stats': {
            'total_licenses': total_licenses,
            'active_licenses': active_licenses,
            'expired_licenses': expired_licenses,
            'total_revenue': float(total_revenue)
        }
    })


# ============================================
# RUN THE APPLICATION
# ============================================

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)