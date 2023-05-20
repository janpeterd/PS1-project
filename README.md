# Boekingssysteem museum

Deze repo bevat de code voor een webapplicatie geschreven in Django. Deze is ontwikkeld met als doel het hele boekingsproces voor een bezoek aan een museum voor een groep met gids te vergemakkelijken.

Het is geschreven als eindproject voor het vak _Professional Skills_ met als klant het bezoekerscentrum _Pas-sage_ van _OPZ Geel_.

**Meer informatie en uitleg** is te lezen in [de documentatie](./documentatie/documentatie.md). Of in [(pdf-formaat)](./documentatie/documentatie.pdf).

## Gebruikte technologieën

- _Python_ (programmeertaal)
- _Django_ (webframework)
- _Cron_ (achtergrondtaken)
- _HTML/CSS_ (frontend)
- _Bootstrap_ (frontend)
- _Postgres_ (database)
- _Supabase_ (database hosting)
- _Vercel_ (serverless hosting)

## Development installatie

1. Clone de repo

```bash
git clone https://github.com/janpeterd/PS1-project.git

```

2. Maak een virtuele Python-omgeving aan

```bash
cd PS1-project/
python3 -m venv venv
```

3. activeer virtuele Python-omgeving

Linux:

```bash
source venv/bin/activate
```

Windows PowerShell:

```powershell
venv\Scripts\activate
```

4. Installeer Python packages met pip

```bash
pip install -r requirements.txt
```

5. [settings.py](./djangoProject/settings.py) instellen voor lokale development
   - Voor deze stap moet je een .env file toevoegen met gegevens (databaseinformatie, django-secret-key, e-mailgegevens) die met de commando `python os.environ.get("NAME")` opgehaald worden.
     OF
   - verander alle lijnen met `python os.environ.get("")` door je eigen gegevens (database,e-mail, ...)

```python
# voeg localhost toe aan vertrouwde domeinen
ALLOWED_HOSTS = ["localhost"]

# zie errors in browser
DEBUG = TRUE
```

6. Database migratie/setup

```bash
python3 manage.py makemigrations
python3 manage.py migrate

```

7. Start development server

```bash
python3 manage.py runserver
```

### Deploy Vercel

Om naar Vercel te deployen moet je deze repo importeren in Vercel en alle _environment variables_ invullen (of _.env-bestand_ plakken).
