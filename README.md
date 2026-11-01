# CSV Pipeline: Upload → Process → MySQL → Tableau

## Step 1: Python install karo
Python 3.9+ hona chahiye.

    pip install -r requirements.txt

## Step 2: MySQL database banao
MySQL mein login karke:

    CREATE DATABASE salesdb;

## Step 3: Password set karo
app.py mein `your_password` ki jagah apna MySQL root password likho,
ya terminal mein environment variable set karo:

    # Windows (PowerShell)
    $env:MYSQL_URL="mysql+pymysql://root:APNA_PASSWORD@localhost:3306/salesdb"

    # Mac/Linux
    export MYSQL_URL="mysql+pymysql://root:APNA_PASSWORD@localhost:3306/salesdb"

## Step 4: App chalao

    streamlit run app.py

Browser mein http://localhost:8501 khulega.

## Step 5: Test karo
1. `raw_sales.csv` file upload karo.
2. Raw data aur processed data ka preview dekho.
   Note: ek row mein date galat hai, ek row mein Sales missing hai, aur ek row duplicate hai.
   Processing ke baad ye hat jayengi, isliye "Raw rows" se "Processed rows" kam dikhega.
3. "MySQL mein save karo" par click karo.

Check karne ke liye MySQL mein:

    USE salesdb;
    SELECT * FROM processed_sales LIMIT 5;

## Step 6: Tableau mein dashboard banao
1. Tableau Desktop → Connect → To a Server → MySQL
2. Server: localhost, Port: 3306, Database: salesdb, username/password daalo.
3. Table `processed_sales` ko drag karo.
4. Sheets banao:
   - Sheet 1: order_month (Columns) + SUM(sales) (Rows) → monthly sales line chart
   - Sheet 2: region (Columns) + SUM(profit) (Rows) → region-wise profit bar chart
   - Sheet 3: category ko Color mein daalo, order_month aur SUM(profit) use karo → category trend
5. New Dashboard banao aur teeno sheets usme daal do.

Naya CSV upload karne ke baad Tableau mein Data → Refresh Data karo.

## Notes
- Append mode mein same file dobara upload karoge to duplicate rows bin jayengi. Tab "Purana table replace karo" checkbox on karo.
- Apni CSV use karte waqt columns ke naam Order Date, Region, Category, Sales, Cost hone chahiye (ya process_data mein badlo).
