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

The default database is `insightsql.db`. Override it with `INSIGHTSQL_DATABASE_PATH` when needed. The repository also contains `schema.sql` and `seed.sql` for rebuilding the SQLite database. Copy `.env.example` to `.env` for the supported configuration names; load it through your process or deployment secret manager.

For a simple protected deployment, set `INSIGHTSQL_ACCESS_TOKEN`. The application will require that token before showing data. For production, replace this single-token gate with the organization's identity provider and role-based authorization.

## Safety boundary

Only one read-only `SELECT` statement is accepted. `DROP`, `DELETE`, `UPDATE`, `ALTER`, `TRUNCATE`, `INSERT`, and other write or administration operations are rejected by both the SQL guard and the SQLite authorizer. Table and function allowlists, row limits, query timeouts, and a SQLite progress handler provide defense in depth. The UI exposes the validated SQL for every successful request.

Query history is capped at 1,000 records. It is local application history, not an enterprise audit store; production deployments should add authenticated user ownership, retention policies, encryption, and centralized audit storage.

Logs are emitted as structured JSON with request IDs. Do not send raw employee data or secrets to logs, and use a centralized redacted log sink in production.

## Test

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
python -m pytest -q
```

The plugin setting avoids unrelated globally installed Pytest plugins; CI should use an isolated virtual environment instead.