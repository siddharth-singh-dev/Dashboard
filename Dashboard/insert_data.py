import pandas as pd
import logging

logging.basicConfig(
    filename='db_insert.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("DB insertion started")

def clean_df(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df = df.where(pd.notnull(df), None)
    return df

def insert_bill(df, cursor):
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT IGNORE INTO bill (
                    uhid, bill_date, patient_name, age, gender,
                    bill_id, file_id, doctor_name, department,
                    panel_name, service_gross_amt, bill_discount,
                    service_final_amt, payment_total,
                    total_refund, settlement_received
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row.get('uhid'),
                row.get('doa'),
                row.get('patient_name'),
                row.get('age'),
                row.get('gender'),
                row.get('bill_id'),
                row.get('file_id'),
                row.get('doctor_name'),
                row.get('dept._name'),
                row.get('panel_name'),
                row.get('service_gross_amt'),
                row.get('bill_dis_amt'),
                row.get('service_final_amt'),
                row.get('payment_total'),
                row.get('total_refund'),
                row.get('settlement_amount_received')
            ))
        except Exception as e:
            logging.error(f"Bill insert error: {e}")


def insert_service(df, cursor):
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT IGNORE INTO service (
                    uhid, service_date, patient_name,
                    doctor_name, department, panel_name,
                    service_name, service_type, qty,
                    service_gross_amt, service_discount,
                    bill_discount, service_final_amt
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row.get('uhid'),
                row.get('service_date'),
                row.get('patient_name'),
                row.get('doctor_name'),
                row.get('dept._name'),
                row.get('panel_name'),
                row.get('service_name'),
                row.get('service_type'),
                row.get('qty'),
                row.get('service_gross_amt'),
                row.get('service_dis_amt'),
                row.get('bill_dis_amt'),
                row.get('service_final_amt')
            ))
        except Exception as e:
            logging.error(f"Service insert error: {e}")


def insert_receipt(df, cursor):
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT IGNORE INTO receipt (
                    receipt_date, uhid, patient_name,
                    bill_id, file_id, doctor_name,
                    panel_name, receipt_no, payment_type,
                    payment_category, payment_mode,
                    total_payment, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row.get('receipt_date'),
                row.get('uhid'),
                row.get('patient_name'),
                row.get('bill_id'),
                row.get('file_id'),
                row.get('doctor_name'),
                row.get('panel_name'),
                row.get('receipt_id'),
                row.get('type'),
                row.get('payment_category'),
                row.get('payment_mode'),
                row.get('total_payment'),
                row.get('created_at')
            ))
        except Exception as e:
            logging.error(f"Receipt insert error: {e}")

from db_config import get_connection

conn = get_connection()
cursor = conn.cursor()

# FILE PATH
base_path = "scraper_exports"

# BILL
bill_df = pd.read_excel(f"{base_path}/bill.xlsx")
bill_df = clean_df(bill_df)
insert_bill(bill_df, cursor)

# SERVICE
service_df = pd.read_excel(f"{base_path}/service.xlsx")
service_df = clean_df(service_df)
insert_service(service_df, cursor)

# RECEIPT
receipt_df = pd.read_excel(f"{base_path}/receipt.xlsx")
receipt_df = clean_df(receipt_df)
insert_receipt(receipt_df, cursor)

conn.commit()
cursor.close()
conn.close()

logging.info("All data inserted successfully")
print("ALL DATA INSERTED")