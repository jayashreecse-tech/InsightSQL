# InsightSQL

InsightSQL is a Streamlit workforce analytics assistant. Users ask questions in plain English; OpenAI GPT generates a SQLite query, Python validates it, and the application displays the result and validated SQL.

## Run locally

Install dependencies with the available Python interpreter:

```powershell
python -m pip install -r requirements.txt
```

Set `OPENAI_API_KEY` for free-form natural-language SQL generation. Without a key, the app runs in safe demo mode for department, employee, project, and salary examples.

```powershell
$env:OPENAI_API_KEY = "your-key"
streamlit run app.py
```

The default database is `insightsql.db`. Override it with `INSIGHTSQL_DATABASE_PATH` when needed. The repository also contains `schema.sql` and `seed.sql` for rebuilding the SQLite database.

## Safety boundary

Only one read-only `SELECT` statement is accepted. `DROP`, `DELETE`, `UPDATE`, `ALTER`, `TRUNCATE`, `INSERT`, and other write or administration operations are rejected by both the SQL guard and the SQLite authorizer. The UI exposes the validated SQL for every successful request.

## Test

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
python -m pytest -q
```

The plugin setting avoids unrelated globally installed Pytest plugins; CI should use an isolated virtual environment instead.