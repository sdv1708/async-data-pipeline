# dbt Profiles

Profiles are configured via environment variables so no secrets live in the repo.
Set variables like `DBT_HOST`, `DBT_PORT`, `DBT_USER`, `DBT_PASSWORD`, `DBT_DBNAME`, and `DBT_SCHEMA` before running dbt.

Example profile snippet:

```yaml
default:
  target: dev
  outputs:
    dev:
      type: postgres
      host: "{{ env_var('DBT_HOST') }}"
      user: "{{ env_var('DBT_USER') }}"
      password: "{{ env_var('DBT_PASSWORD') }}"
      port: "{{ env_var('DBT_PORT') | int }}"
      dbname: "{{ env_var('DBT_DBNAME') }}"
      schema: "{{ env_var('DBT_SCHEMA') }}"
      threads: 1
      keepalives_idle: 0
```

Set `DBT_PROFILES_DIR` to this directory when running in CI.
