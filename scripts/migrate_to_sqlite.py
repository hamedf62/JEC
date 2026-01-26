import os
import pandas as pd
from sqlalchemy.orm import Session
import sys

# Add the project root to sys.path to import app modules
sys.path.append(os.getcwd())

from app.database import engine, SessionLocal, Base
from app.models import DBPayable, DBReceivable, DBInvoice, DBPerforma


def migrate():
    # Ensure data/csv exists
    os.makedirs("data/csv", exist_ok=True)

    # Initialize DB tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # 1. Migrate Payable
        print("Migrating Payable...")
        df_payable = pd.read_excel("data/payable.xlsx", header=1)
        # Rial to Toman
        df_payable["بستانکار"] = (
            pd.to_numeric(df_payable["بستانکار"], errors="coerce").fillna(0) / 10
        )

        mapping_payable = {
            "ردیف": "row_id",
            "شماره موکد": "document_number",
            "تاریخ": "document_date",
            "شرح عملیات": "description",
            "بستانکار": "amount",
            "تاریخ سررسید": "due_date",
            "نام تفصیلی 1": "beneficiary",
            "نام تفصیلی 2": "account_name",
            "تاریخ سررسید.1": "internal_due_date",
        }
        df_payable_mapped = df_payable.rename(columns=mapping_payable)
        # Select and save to CSV
        df_payable_mapped.to_csv("data/csv/payable.csv", index=False)
        # Store in DB
        for _, row in df_payable_mapped.iterrows():
            db.add(DBPayable(**row.to_dict()))

        # 2. Migrate Receivable
        print("Migrating Receivable...")
        df_receivable = pd.read_excel("data/receivable.xlsx", header=1)
        df_receivable["بدهکار"] = (
            pd.to_numeric(df_receivable["بدهکار"], errors="coerce").fillna(0) / 10
        )
        mapping_receivable = {
            "ردیف": "row_id",
            "تاریخ": "document_date",
            "بدهکار": "amount",
            "تاریخ سررسید": "due_date",
            "تاریخ سررسید2": "internal_due_date",
            "نام شرکت": "company_name",
        }
        df_receivable_mapped = df_receivable.rename(columns=mapping_receivable)
        df_receivable_mapped.to_csv("data/csv/receivable.csv", index=False)
        for _, row in df_receivable_mapped.iterrows():
            db.add(DBReceivable(**row.to_dict()))

        # 3. Migrate Invoices
        print("Migrating Invoices...")
        df_invoices = pd.read_excel("data/invoices.xlsx", header=0)
        # Convert amount columns to Toman
        amount_cols_invoices = [
            "جمع بها پس از کسر تخفیف",
            "جمع کل مالیات بر ارزش افزوده",
            "جمع بهای نهایی",
        ]
        for col in amount_cols_invoices:
            df_invoices[col] = (
                pd.to_numeric(df_invoices[col], errors="coerce").fillna(0) / 10
            )

        mapping_invoices = {
            " ": "row_id",
            "نوع": "invoice_type",
            "تاریخ": "invoice_date",
            "کد مشتری": "customer_code",
            "نام مشتری": "customer_name",
            "OC": "order_code",
            "تفصیلی دو مالی": "account_detail",
            "جمع بها پس از کسر تخفیف": "subtotal",
            "جمع کل مالیات بر ارزش افزوده": "tax",
            "جمع بهای نهایی": "total_amount",
        }
        df_invoices_mapped = df_invoices.rename(columns=mapping_invoices)
        df_invoices_mapped.to_csv("data/csv/invoices.csv", index=False)
        for _, row in df_invoices_mapped.iterrows():
            db.add(DBInvoice(**row.to_dict()))

        # 4. Migrate Performa
        print("Migrating Performa...")
        df_performa = pd.read_excel("data/performa.xlsx", header=0)
        df_performa["جمع بهای برگه"] = (
            pd.to_numeric(df_performa["جمع بهای برگه"], errors="coerce").fillna(0) / 10
        )
        mapping_performa = {
            "ردیف": "row_id",
            "نوع": "performa_type",
            "تاریخ": "performa_date",
            "سری": "series",
            "نام نوع فروش": "sale_type",
            "OC": "order_code",
            "تفصیلی دو مالی": "account_detail",
            "کد مشتری": "customer_code",
            "نام مشتری": "customer_name",
            "وضعیت": "status",
            "جمع بهای برگه": "amount",
            "شرح": "description",
        }
        df_performa_mapped = df_performa.rename(columns=mapping_performa)
        df_performa_mapped.to_csv("data/csv/performa.csv", index=False)
        for _, row in df_performa_mapped.iterrows():
            db.add(DBPerforma(**row.to_dict()))

        db.commit()
        print("Migration completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Migration failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
