import aiosqlite

DB_PATH = "bot.db"  # SQLite ֆայլը

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                demo_balance REAL DEFAULT 100.0,
                real_balance REAL DEFAULT 0.0
            )
        """)
        await db.commit()

async def get_balances(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT demo_balance, real_balance FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if row is None:
            # Եթե օգտատեր չկայ, ստեղծենք սկզբնական արժեքներով
            await db.execute(
                "INSERT INTO users (user_id, demo_balance, real_balance) VALUES (?, ?, ?)",
                (user_id, 100.0, 0.0)
            )
            await db.commit()
            return 100.0, 0.0
        return row[0], row[1]

async def update_balance(user_id: int, amount: float, balance_type="demo"):
    async with aiosqlite.connect(DB_PATH) as db:
        col = "demo_balance" if balance_type == "demo" else "real_balance"
        # Ստանում ենք հին մնացորդը
        cursor = await db.execute(f"SELECT {col} FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if row is None:
            # Եթե չկա օգտատեր, ստեղծենք սկզբնական արժեքներով
            demo_start = 100.0 if balance_type == "demo" else 0.0
            real_start = 0.0 if balance_type == "demo" else 0.0
            await db.execute(
                "INSERT INTO users (user_id, demo_balance, real_balance) VALUES (?, ?, ?)",
                (user_id, demo_start, real_start)
            )
            await db.commit()
            current_balance = demo_start if balance_type == "demo" else real_start
        else:
            current_balance = row[0]

        new_balance = current_balance + amount
        if new_balance < 0:
            # Չեղարկել, եթե պակաս մնացորդ է ստացվում
            raise ValueError("Not enough balance")

        await db.execute(
            f"UPDATE users SET {col} = ? WHERE user_id = ?",
            (new_balance, user_id)
        )
        await db.commit()
        return new_balance
