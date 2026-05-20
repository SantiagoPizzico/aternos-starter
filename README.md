# 🟩 Aternos Starter — Panel de servidor Minecraft

Un botón para que cualquiera del squad pueda iniciar el servidor sin depender del host.

---

## ¿Cómo funciona?

```
[index.html] → click "Iniciar" → [backend en Railway] → Playwright abre Aternos → login → click Start
```

---

## 🚀 Deploy del backend en Railway

### 1. Crear cuenta en Railway
- Ir a https://railway.app
- Registrarse con GitHub (tier gratuito da 5 USD/mes, suficiente para uso esporádico)

### 2. Subir el código
```bash
# Instalar Railway CLI (opcional, también se puede desde la web)
npm install -g @railway/cli

# Desde la carpeta del proyecto:
railway login
railway init
railway up
```

O desde la web: New Project → Deploy from GitHub repo (subí los archivos a un repo privado).

### 3. Configurar variables de entorno
En Railway → tu proyecto → Variables, agregar:

| Variable        | Valor                              |
|----------------|------------------------------------|
| ATERNOS_USER   | tu_usuario_de_aternos              |
| ATERNOS_PASS   | tu_contraseña_de_aternos           |
| SECRET_TOKEN   | una_contraseña_que_inventés_vos    |
| PORT           | 5000                               |

> ⚠️ El SECRET_TOKEN es lo que van a escribir tus amigos en el panel web para autenticarse.
> Inventá algo como "minecraft2024squad" y compartíselo por Discord.

### 4. Copiar la URL del backend
Railway te da una URL tipo: `https://aternos-starter-production.up.railway.app`

---

## 🌐 Configurar la web (index.html)

Abrí `index.html` y cambiá esta línea:

```javascript
const BACKEND_URL = "https://TU-BACKEND.up.railway.app";
```

Reemplazá con la URL que te dio Railway.

### ¿Dónde hospedar el index.html?
Opciones gratuitas:
- **GitHub Pages**: subí el repo y activá Pages en Settings
- **Netlify**: arrastrá el archivo en https://netlify.com/drop
- **Vercel**: igual de fácil

---

## 📁 Estructura de archivos

```
aternos-starter/
├── app.py              # Backend Flask + Playwright
├── requirements.txt    # Dependencias Python
├── Dockerfile          # Para Railway/Render
├── railway.toml        # Config de Railway
└── index.html          # La web que ven tus amigos
```

---

## ⚠️ Notas importantes

- **Aternos puede hacer queue**: si hay mucha gente en cola, el servidor espera. El bot confirma automáticamente la cola.
- **El inicio tarda 2-3 minutos**: Playwright tiene que iniciar sesión y navegar, no es instantáneo.
- **Seguridad**: el `SECRET_TOKEN` evita que cualquier desconocido inicie el servidor si encuentra la URL del backend.
- **Aternos puede actualizar su HTML**: si dejan de funcionar los selectores (`#start`, `.login-button`), puede que haya que actualizar `app.py`.

---

## 🐛 Troubleshooting

**El backend dice "No se encontró el botón de inicio"**
→ Aternos cambió su UI. Abrí Aternos en el browser, click derecho en el botón Start → Inspeccionar, y copiá el selector CSS correcto en `app.py`.

**Error de login**
→ Verificá las variables de entorno `ATERNOS_USER` y `ATERNOS_PASS` en Railway.

**La web no llega al backend (CORS error)**
→ Ya está configurado `flask-cors`, revisá que `BACKEND_URL` en el HTML esté bien escrita (sin `/` al final).
