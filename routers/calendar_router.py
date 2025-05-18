from fastapi import APIRouter, HTTPException, Response
from models.monthly_setup import MonthlySetupRequest, ProfitLossRequest
from db.mssqldatabase import get_connection
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api", tags=["calendar"])
# 초기 셋업 시작금액 db에 저장된 값 가져오기
@router.get("/calendar/{email}/monthlySetup")
async def get_monthly_setup(email:str, response: Response):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = ?",(email,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = row[0]
    
    # 현재 연/워 계산
    now = datetime.now()
    year = now.year
    month = now.month

    # 시작금액 조회
    cursor.execute(
        """
        SELECT start_amount FROM usersMonthlySetupAmount
        WHERE user_id = ? AND year = ? AND month = ?
        """,(user_id,year,month)
    )

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if not result:
        return {"start_amount":0}
    return {"start_amount": result[0]}

@router.post("/calendar")
async def calendar(user: MonthlySetupRequest, response: Response):
    print("1")
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. email -> user 테이블의 id 조회
    cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
    row = cursor.fetchone()
    print(row)
    print("2026")
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = row[0]
    print(user_id)
    # 2. 현재 연/월 계산
    now = datetime.now()
    year = now.year
    month = now.month

    # 3. UPDATE OR INSERT
    # 먼저 존재하는지 확인
    cursor.execute(
        """
        SELECT COUNT(*) FROM usersMonthlySetupAmount
        WHERE user_id = ? AND year = ? AND month = ?
        """,
        (user_id, year, month)
    )
    exists = cursor.fetchone()[0] > 0

    if exists:
        cursor.execute(
            """
            UPDATE usersMonthlySetupAmount
            SET start_amount = ?, updated_at = GETDATE()
            WHERE user_id = ? AND year = ? AND month = ?
            """,
            (user.start_amount, user_id, year, month)
        )
    else:
        cursor.execute(
            """
            INSERT INTO usersMonthlySetupAmount (user_id, start_amount, year, month, created_at, updated_at)
            VALUES (?, ?, ?, ?, GETDATE(), GETDATE())
            """,
            (user_id, user.start_amount, year, month)
        )

    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Setup amount saved."}

# 손익기록
@router.post("/calendar/record")
async def record_profit_loss(data: ProfitLossRequest, response:Response):
    conn = get_connection()
    cursor = conn.cursor()

    # 사용자 아이디 찾기
    cursor.execute("SELECT id FROM users WHERE email = ?",(data.email,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = row[0]
    
    # 손익 저장
    cursor.execute("""
                    INSERT INTO profitLossCalendar (user_id, date, profit_loss)
                   VALUES (?,?,?)
                   """,(user_id, data.date, data.profit_loss)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {"message":"INSERT 완료"}

@router.get("/calendar/{email}/records")
async def get_profit_loss_records(email: str, year: int, month: int):
    conn = get_connection()
    cursor = conn.cursor()

    # 사용자 ID 조회
    cursor.execute("SELECT id FROM users WHERE email = ?",(email,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = row[0]

    # 해당 워의 손익 데이터 가져오기
    cursor.execute("""
                   SELECT date,profit_loss FROM profitLossCalendar
                   WHERE user_id = ? AND YEAR(date) = ? AND MONTH(date) = ?"""
                   ,(user_id,year,month))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [
        {
            "title": f"{'+' if pl >= 0 else '-'}${abs(pl):,}",
            "date": date.strftime('%Y-%m-%d'),
            "color": "green" if pl >= 0 else "red"

        }
        for date, pl in rows
    ]

@router.get("/calendar/{email}/currentMoney")
async def get_current_money(email: str):
    now = datetime.now()
    year = now.year
    month = now.month

    conn = get_connection()
    cursor = conn.cursor()

    # 유저 ID 찾기
    cursor.execute("SELECT id from users WHERE email = ?",(email,))
    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = row[0]

    # 시작 금액 및 손익 합계 가져오기
    cursor.execute("""
                    SELECT
                            s.start_amount, ISNULL(SUM(p.profit_loss),0) AS total_pl,
                            s.start_amount + ISNULL(SUM(p.profit_loss),0) AS current_amount
                    FROM usersMonthlySetupAmount s
                    LEFT JOIN profitLossCalendar p
                        ON s.user_id = p.user_id AND MONTH(p.date) = ? AND YEAR(p.date) = ?
                    WHERE s.user_id = ? AND s.year = ? AND s.month = ?
                    GROUP BY s.start_amount
                """,(month,year,user_id,year,month))
    
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="이번 달 시작금액이 없습니다.")
    
    start_amount, total_pl, current_amount = row
    pnl_ratio = round((current_amount - start_amount) / start_amount * 100)

    return {
        "start_amount":start_amount,
        "total_pl": total_pl,
        "current_amount": current_amount,
        "pnl_ratio": pnl_ratio
    }