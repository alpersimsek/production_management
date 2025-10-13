import json
from sqlalchemy import text
from app.db import engine

DEFAULT_SETTINGS = {
  "fire_thresholds": {
    "poset": {"level1_percent": 3, "level1_kg": 15, "level2_percent": 6, "level2_kg": 30},
    "deterjan": {"level1_percent": 2, "level1_kg": 10, "level2_percent": 4, "level2_kg": 20}
  },
  "termin": {"minimum_days": 7},
  "warehouses": [
    {"code": "MERKEZ", "name": "Merkez Depo"},
    {"code": "YAN", "name": "Yan Depo"}
  ]
}

with engine.begin() as conn:
    # roles
    conn.execute(text("INSERT INTO roles (name, permissions) VALUES (:n, '{}'::jsonb) ON CONFLICT DO NOTHING"), {"n":"admin"})
    conn.execute(text("INSERT INTO roles (name, permissions) VALUES (:n, '{}'::jsonb) ON CONFLICT DO NOTHING"), {"n":"manager"})
    conn.execute(text("INSERT INTO roles (name, permissions) VALUES (:n, '{}'::jsonb) ON CONFLICT DO NOTHING"), {"n":"operator"})
    conn.execute(text("INSERT INTO roles (name, permissions) VALUES (:n, '{}'::jsonb) ON CONFLICT DO NOTHING"), {"n":"packaging"})
    conn.execute(text("INSERT INTO roles (name, permissions) VALUES (:n, '{}'::jsonb) ON CONFLICT DO NOTHING"), {"n":"warehouse"})
    conn.execute(text("INSERT INTO roles (name, permissions) VALUES (:n, '{}'::jsonb) ON CONFLICT DO NOTHING"), {"n":"sales"})

    # admin user (şifre hash'i örnek, prod'da değiştir)
    conn.execute(text("""
      INSERT INTO users (full_name,email,password_hash,role_id)
      VALUES ('Admin','admin@local','$2b$12$2r8Q0z2b1f1r5W1ZQbE1A.3n8cKjQ1p6Z/2tps7H3Sxh0bW3oXl9u',
              (SELECT id FROM roles WHERE name='admin'))
      ON CONFLICT (email) DO NOTHING
    """))

    # settings
    for k,v in DEFAULT_SETTINGS.items():
        conn.execute(text("INSERT INTO settings (key,value) VALUES (:k, :v) ON CONFLICT (key) DO UPDATE SET value=:v"), {"k":k, "v":json.dumps(v)})

    # warehouses
    for wh in DEFAULT_SETTINGS["warehouses"]:
        conn.execute(text("INSERT INTO warehouses (code,name) VALUES (:c,:n) ON CONFLICT (code) DO NOTHING"), {"c": wh["code"], "n": wh["name"]})

print("Seed completed")

