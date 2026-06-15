# 📊 Dashboard ATC · Opción Yo

Dashboard gerencial de Atención al Cliente (Streamlit + Plotly) sobre los datos
de Treble. Se despliega gratis y queda accesible desde cualquier lugar con una URL.

---

## 📁 Estructura del repositorio

```
opcionyo-dashboard-atc/
├── dashboard_atc_v2.py     ← la app (archivo principal)
├── requirements.txt        ← dependencias
├── README.md
├── .gitignore
└── treble.csv              ← datos (ver "Privacidad" antes de subirlo)
```

---

## 🚀 Publicar en internet (Streamlit Community Cloud · gratis)

### Paso 1 — Subir los archivos a GitHub
**Opción fácil (web):**
1. En GitHub → **New repository** → nombre `opcionyo-dashboard-atc`.
   Recomendado: marcar **Private** (ver "Privacidad").
2. **Add file → Upload files** → arrastra `dashboard_atc_v2.py`,
   `requirements.txt`, `README.md`, `.gitignore` → **Commit**.

**Opción consola (git):**
```bash
git init
git add dashboard_atc_v2.py requirements.txt README.md .gitignore
git commit -m "Dashboard ATC Opción Yo v2"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/opcionyo-dashboard-atc.git
git push -u origin main
```

### Paso 2 — Desplegar
1. Entra a **https://share.streamlit.io** e inicia sesión con tu cuenta de GitHub.
2. **Create app → Deploy a public app from a repository.**
3. Completa:
   - **Repository:** `TU_USUARIO/opcionyo-dashboard-atc`
   - **Branch:** `main`
   - **Main file path:** `dashboard_atc_v2.py`
4. (Opcional) en **Advanced settings** elige una URL: `opcionyo-atc`.
5. **Deploy.** En ~2 min tendrás algo como:
   `https://opcionyo-atc.streamlit.app`

Comparte esa URL: se abre desde cualquier navegador, PC o celular, sin instalar nada.

---

## 🔒 Privacidad de datos (LÉEME — importante)

`treble.csv` contiene **nombres y teléfonos de clientes reales**. No lo dejes
expuesto. Elige UNA opción:

| Opción | Cómo | Resultado |
|---|---|---|
| **A. Recomendada** | Repo **privado** + **contraseña** en la app (abajo) | La URL es pública pero pide clave; solo entra quien tú decidas |
| **B. Sin datos en el repo** | NO subas `treble.csv` (déjalo en `.gitignore`) | La app abre vacía y cada usuario sube el CSV con el botón del panel lateral |
| **C. Anonimizado** | Sube un CSV con teléfonos/nombres enmascarados | Datos no identificables; apto para repo público |

### Activar la contraseña (Opción A)
1. En tu app desplegada → menú **⋮ → Settings → Secrets**.
2. Pega:
   ```toml
   app_password = "TU_CLAVE_SEGURA"
   ```
3. **Save.** La app se reinicia y pedirá esa clave a todos.
   (Sin este secret, la app queda abierta.)

> La app soporta repos **privados** en Streamlit Cloud sin costo: autoriza el
> acceso a repos privados al conectar GitHub. Así `treble.csv` no es navegable
> públicamente aunque esté en el repo.

---

## 🔄 Actualizar el dashboard
Cada vez que hagas *commit/push* a GitHub, la app se actualiza sola en segundos.

## 💻 Correr en local
```bash
pip install -r requirements.txt
python -m streamlit run dashboard_atc_v2.py
```

---

## 📈 Datos opcionales
Las pestañas **Outbound, Fallas, Inversión, HSM y Conexión** se activan al subir,
desde el panel lateral, los exports correspondientes de Treble (CSV).
