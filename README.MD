cd /medico
nohup python3 manage.py runserver 0.0.0.0:8080 \
  > ~/medico_run.log 2>&1 &

cd /historia_clinica
nohup python3 manage.py runserver 0.0.0.0:8080 \
  > ~/hc_run.log 2>&1 &

cd /medico
python3 manage.py populate_db

cd /historia_clinica
python3 manage.py compute_report

http://<IP-PUBLICA-KONG>:8000/historia-clinica/api/report/?period=2025-05-01