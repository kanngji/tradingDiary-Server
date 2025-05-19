from fastapi import APIRouter, HTTPException, Response
from models.monthly_setup import MonthlySetupRequest, ProfitLossRequest
from db.mysqldatabase import get_connection  # ✅ MySQL용 DB 연결
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api", tags=["calendar"])


@router.get("/calendar/{email}/monthlySetup")
async def get_monthly_setup(email: str, response: Response):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = row["id"]

    now = datetime.now()
    year = now.year
    month = now.month

    cursor.execute("""
        SELECT start_amount FROM usersMonthlySetupAmount
        WHERE user_id = %s AND year = %s AND month = %s
    """, (user_id, year, month))

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if not result:
        return {"start_amount": 0}
    return {"start_amount": result["start_amount"]}


@router.post("/calendar")
async def calendar(user: MonthlySetupRequest, response: Response):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = row["id"]
    now = datetime.now()
    year = now.year
    month = now.month

    # UPDATE OR INSERT
    cursor.execute("""
        SELECT COUNT(*) FROM usersMonthlySetupAmount
        WHERE user_id = %s AND year = %s AND month = %s
    """, (user_id, year, month))
    exists = cursor.fetchone()["COUNT(*)"] > 0

    if exists:
        cursor.execute("""
            UPDATE usersMonthlySetupAmount
            SET start_amount = %s, updated_at = NOW()
            WHERE user_id = %s AND year = %s AND month = %s
        """, (user.start_amount, user_id, year, month))
    else:
        cursor.execute("""
            INSERT INTO usersMonthlySetupAmount
            (user_id, start_amount, year, month, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
        """, (user_id, user.start_amount, year, month))

    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Setup amount saved."}


@router.post("/calendar/record")
async def record_profit_loss(data: ProfitLossRequest, response: Response):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = %s", (data.email,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = row["id"]

    cursor.execute("""
        INSERT INTO profitLossCalendar (user_id, date, profit_loss)
        VALUES (%s, %s, %s)
    """, (user_id, data.date, data.profit_loss))

    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "INSERT 완료"}


@router.get("/calendar/{email}/records")
async def get_profit_loss_records(email: str, year: int, month: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = row["id"]

    cursor.execute("""
        SELECT date, profit_loss FROM profitLossCalendar
        WHERE user_id = %s AND YEAR(date) = %s AND MONTH(date) = %s
    """, (user_id, year, month))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [
        {
            "title": f"{'+' if row['profit_loss'] >= 0 else '-'}${abs(row['profit_loss']):,}",
            "date": row['date'].strftime('%Y-%m-%d'),
            "color": "green" if row['profit_loss'] >= 0 else "red"
        }
        for row in rows
    ]


@router.get("/calendar/{email}/currentMoney")
async def get_current_money(email: str):
    now = datetime.now()
    year = now.year
    month = now.month

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = row["id"]

    cursor.execute("""
        SELECT
            s.start_amount,
            IFNULL(SUM(p.profit_loss), 0) AS total_pl,
            s.start_amount + IFNULL(SUM(p.profit_loss), 0) AS current_amount
        FROM usersMonthlySetupAmount s
        LEFT JOIN profitLossCalendar p
            ON s.user_id = p.user_id AND MONTH(p.date) = %s AND YEAR(p.date) = %s
        WHERE s.user_id = %s AND s.year = %s AND s.month = %s
        GROUP BY s.start_amount
    """, (month, year, user_id, year, month))

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="이번 달 시작금액이 없습니다.")

    start_amount = row["start_amount"]
    total_pl = row["total_pl"]
    current_amount = row["current_amount"]
    pnl_ratio = round((current_amount - start_amount) / start_amount * 100)

    return {
        "start_amount": start_amount,
        "total_pl": total_pl,
        "current_amount": current_amount,
        "pnl_ratio": pnl_ratio
    }
