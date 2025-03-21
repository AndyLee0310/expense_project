WITH RECURSIVE dates(date) AS (
    SELECT DATE('2025-03-01')
    UNION ALL
    SELECT DATE(date, '+1 day') FROM dates WHERE date < DATE('2025-03-31')
)
INSERT INTO expenses (item, amount, date)
SELECT 'a餐', (ABS(RANDOM()) % 4901) + 100, date FROM dates;

WITH RECURSIVE dates(date) AS (
    SELECT DATE('2025-04-01')
    UNION ALL
    SELECT DATE(date, '+1 day') FROM dates WHERE date < DATE('2025-04-30')
)
INSERT INTO expenses (item, amount, date)
SELECT 'bb餐', (ABS(RANDOM()) % 4901) + 100, date FROM dates;

WITH RECURSIVE dates(date) AS (
    SELECT DATE('2025-05-01')
    UNION ALL
    SELECT DATE(date, '+1 day') FROM dates WHERE date < DATE('2025-05-31')
)
INSERT INTO expenses (item, amount, date)
SELECT '午餐', (ABS(RANDOM()) % 4901) + 100, date FROM dates;
