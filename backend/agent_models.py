# agent_models.py
# Database models for SkulCBT Agent Program
# Full path: C:\Users\Peace\Desktop\skulcbt-website\backend\agent_models.py
#
# ============================================
# AUTHOR: Emmanuel Adekunle Peace
# WEBSITE: www.emmanueladekunlepeace.com
# PHONE: 07032977572
# EMAIL: emmanueladekunlep@gmail.com
# ============================================
# SkulCBT Agent Program - Database Models
# Copyright (c) 2026 SkulCBT. All rights reserved.
# ============================================

import sqlite3
import json
from datetime import datetime
import os

DB_PATH = 'C:/Users/Peace/Desktop/skulcbt-website/database/agents.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            referral_code TEXT UNIQUE NOT NULL,
            referred_by TEXT,
            registration_date TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            rank TEXT DEFAULT 'bronze',
            total_sales INTEGER DEFAULT 0,
            total_commission REAL DEFAULT 0,
            balance REAL DEFAULT 0,
            bank_name TEXT,
            account_number TEXT,
            account_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            school_name TEXT NOT NULL,
            school_email TEXT,
            school_phone TEXT,
            tier TEXT NOT NULL,
            plan TEXT NOT NULL,
            price REAL NOT NULL,
            commission REAL NOT NULL,
            status TEXT DEFAULT 'approved',
            sale_date TEXT NOT NULL,
            renew_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            sale_id INTEGER NOT NULL,
            level INTEGER NOT NULL,
            amount REAL NOT NULL,
            paid INTEGER DEFAULT 0,
            created_date TEXT NOT NULL,
            paid_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id),
            FOREIGN KEY (sale_id) REFERENCES sales(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            request_date TEXT NOT NULL,
            approval_date TEXT,
            bank_name TEXT,
            account_number TEXT,
            account_name TEXT,
            transaction_id TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS license_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_key TEXT UNIQUE NOT NULL,
            school_name TEXT NOT NULL,
            tier TEXT NOT NULL,
            plan TEXT NOT NULL,
            price REAL NOT NULL,
            agent_id INTEGER NOT NULL,
            sale_id INTEGER NOT NULL,
            created_date TEXT NOT NULL,
            expiry_date TEXT,
            status TEXT DEFAULT 'active',
            activated_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id),
            FOREIGN KEY (sale_id) REFERENCES sales(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ranks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rank_name TEXT UNIQUE NOT NULL,
            min_sales INTEGER DEFAULT 0,
            min_recruits INTEGER DEFAULT 0,
            profit_pool_percent REAL DEFAULT 0,
            bonus_amount REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('SELECT COUNT(*) FROM ranks')
    count = cursor.fetchone()[0]

    if count == 0:
        ranks = [
            ('bronze', 3, 2, 2, 0),
            ('silver', 10, 5, 5, 0),
            ('gold', 25, 15, 10, 0),
            ('platinum', 50, 30, 15, 0),
            ('diamond', 100, 50, 25, 1000000)
        ]
        for rank in ranks:
            cursor.execute('''
                INSERT INTO ranks (rank_name, min_sales, min_recruits, profit_pool_percent, bonus_amount)
                VALUES (?, ?, ?, ?, ?)
            ''', rank)

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('SELECT COUNT(*) FROM settings')
    count = cursor.fetchone()[0]

    if count == 0:
        settings = [
            ('direct_commission_percent', '35', 'Direct agent commission percentage'),
            ('level1_commission_percent', '5', 'Level 1 upline commission percentage'),
            ('level2_commission_percent', '3', 'Level 2 upline commission percentage'),
            ('level3_commission_percent', '1', 'Level 3 upline commission percentage'),
            ('recruitment_bonus', '5000', 'Bonus for recruiting a new agent'),
            ('registration_fee', '10000', 'Agent registration fee amount'),
            ('free_registration_limit', '50', 'Number of free registrations allowed'),
            ('minimum_withdrawal', '10000', 'Minimum amount for withdrawal request'),
            ('payout_day', '1', 'Day of month for payouts'),
            ('commission_levels', '3', 'Number of commission levels'),
            ('free_registration_count', '0', 'Current count of free registrations')
        ]
        for setting in settings:
            cursor.execute('''
                INSERT INTO settings (setting_key, setting_value, description)
                VALUES (?, ?, ?)
            ''', setting)

    conn.commit()
    conn.close()


def get_setting(key):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT setting_value FROM settings WHERE setting_key = ?', (key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return None


def update_setting(key, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE settings 
        SET setting_value = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE setting_key = ?
    ''', (value, key))
    conn.commit()
    conn.close()


def get_agent_by_id(agent_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM agents WHERE id = ?', (agent_id,))
    agent = cursor.fetchone()
    conn.close()
    return agent


def get_agent_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM agents WHERE email = ?', (email,))
    agent = cursor.fetchone()
    conn.close()
    return agent


def get_agent_by_referral_code(code):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM agents WHERE referral_code = ?', (code,))
    agent = cursor.fetchone()
    conn.close()
    return agent


def get_all_agents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM agents ORDER BY created_at DESC')
    agents = cursor.fetchall()
    conn.close()
    return agents


def delete_agent(agent_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM agents WHERE id = ?', (agent_id,))
    conn.commit()
    conn.close()


def get_downline_agents(agent_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM agents WHERE referred_by = ?', (agent_id,))
    agents = cursor.fetchall()
    conn.close()
    return agents


def get_agent_rank(agent):
    sales = agent['total_sales'] if agent else 0
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ranks ORDER BY min_sales DESC')
    ranks = cursor.fetchall()
    conn.close()
    
    for rank in ranks:
        if sales >= rank['min_sales']:
            return rank['rank_name']
    
    return 'bronze'


def update_agent_rank(agent_id):
    agent = get_agent_by_id(agent_id)
    if not agent:
        return
    
    new_rank = get_agent_rank(agent)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE agents SET rank = ? WHERE id = ?', (new_rank, agent_id))
    conn.commit()
    conn.close()