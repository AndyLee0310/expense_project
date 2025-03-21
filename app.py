from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__, instance_relative_config=True)
DATABASE = 'instance/expense_management.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db:
        db.close()

@app.route('/')
def index():
    db = get_db()
    
    # 取得當前的 year 和 month（若無則預設為當前月份）
    year = request.args.get('year', type=int, default=datetime.today().year)
    month = request.args.get('month', type=int, default=datetime.today().month)

    # 計算本月範圍
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year + 1}-01-01"
    else:
        end_date = f"{year}-{month + 1:02d}-01"

    # 取得當月的支出資料
    expenses = db.execute(
        'SELECT * FROM expenses WHERE date >= ? AND date < ? ORDER BY date ASC',
        (start_date, end_date)
    ).fetchall()

    # 本月總支出
    monthly_total = db.execute(
        'SELECT SUM(amount) FROM expenses WHERE date >= ? AND date < ?',
        (start_date, end_date)
    ).fetchone()[0] or 0

    # 計算每週支出
    weekly_expenses = db.execute(
        '''
        SELECT strftime('%W', date) AS week, SUM(amount) 
        FROM expenses 
        WHERE date >= ? AND date < ?
        GROUP BY week
        ORDER BY week
        ''', 
        (start_date, end_date)
    ).fetchall()

    # 計算上一個月 & 下一個月的參數
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    page = request.args.get('page', default=1, type=int)

    return render_template(
        'index.html',
        expenses=expenses,
        monthly_total=monthly_total,
        weekly_expenses=weekly_expenses,
        year=year,
        month=month,
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month,
        page=page
    )

@app.route('/add', methods=['POST'])
def add_expense():
    db = get_db()
    item = request.form['item']
    amount = request.form['amount']
    date = request.form['date']

    db.execute('INSERT INTO expenses (item, amount, date) VALUES (?, ?, ?)', (item, amount, date))
    db.commit()

    # 解析年月（不使用 form 裡的 hidden year/month）
    from datetime import datetime
    dt = datetime.strptime(date, '%Y-%m-%d')
    year = dt.year
    month = dt.month

    # 計算該筆資料會落在哪一頁（依目前排序邏輯）
    total_items_before = db.execute(
        'SELECT COUNT(*) FROM expenses WHERE date >= ? AND date < ? AND date < ?',
        (f"{year}-{month:02d}-01",
         f"{year + 1 if month == 12 else year}-{(month % 12) + 1:02d}-01", date)
    ).fetchone()[0]

    page = (total_items_before // 10) + 1

    return redirect(url_for('index', year=year, month=month, page=page))

@app.route('/delete', methods=['POST'])
def delete_expense():
    db = get_db()
    expense_id = request.form['id']

    db.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    db.commit()

    # 回到目前頁面（使用表單中的年份、月份和頁碼）
    year = int(request.form.get('year'))
    month = int(request.form.get('month'))
    page = int(request.form.get('page'))
    return redirect(url_for('index', year=year, month=month, page=page))

@app.route('/calendar')
def calendar():
    db = get_db()

    # year = request.args.get('year', type=int)
    # month = request.args.get('month', type=int)
    year = request.args.get('year', type=int, default=datetime.today().year)
    month = request.args.get('month', type=int, default=datetime.today().month)
    print(f"test:{year}")
    print(f"test:{month}")


    if year and month:
        current_date = datetime(year, month, 1)
    else:
        current_date = datetime.today()
    
    print(f"test:{current_date}")

    start_month = current_date.replace(day=1).strftime('%Y-%m-%d')
    end_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1).strftime('%Y-%m-%d')

    expenses = db.execute(
        'SELECT item, amount, date FROM expenses WHERE date >= ? AND date < ?',
        (start_month, end_month)
    ).fetchall()

    events = [{
        'title': f"{exp['item']} ${exp['amount']:,}",
        'start': exp['date']
    } for exp in expenses]

    return render_template('calendar.html', events=events, current_date=current_date)

if __name__ == '__main__':
    app.run(debug=True)