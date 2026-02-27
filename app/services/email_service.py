import resend
import os
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL     = os.getenv("RESEND_FROM",    "onboarding@resend.dev")
ADMIN_EMAIL    = os.getenv("ADMIN_EMAIL",    "alexanderberaun18@gmail.com")

def _base_template(content: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
                background:#050510; color:#e2e8f0; }}
        .wrapper {{ max-width:600px; margin:0 auto; padding:20px; }}
        .header {{ background:linear-gradient(135deg,#0a0a2e,#0d0d3d);
                   border:1px solid rgba(0,212,255,0.3);
                   border-radius:16px 16px 0 0; padding:32px; text-align:center; }}
        .logo {{ font-size:28px; font-weight:900; letter-spacing:3px;
                 color:#00d4ff; text-shadow:0 0 20px rgba(0,212,255,0.5); }}
        .logo span {{ color:#ffffff; }}
        .body {{ background:#0a0a1f;
                 border-left:1px solid rgba(0,212,255,0.15);
                 border-right:1px solid rgba(0,212,255,0.15); padding:32px; }}
        .footer {{ background:#050510; border:1px solid rgba(0,212,255,0.15);
                   border-radius:0 0 16px 16px; padding:20px; text-align:center; }}
        .footer p {{ color:#4a5568; font-size:12px; }}
        h1  {{ color:#00d4ff; font-size:22px; margin-bottom:16px; }}
        p   {{ color:#a0aec0; line-height:1.7; margin-bottom:12px; font-size:14px; }}
        .badge {{ display:inline-block; padding:4px 12px; border-radius:999px;
                  font-size:12px; font-weight:700; }}
        .badge-blue   {{ background:rgba(0,212,255,0.1);  color:#00d4ff;  border:1px solid rgba(0,212,255,0.3); }}
        .badge-green  {{ background:rgba(0,255,136,0.1);  color:#00ff88;  border:1px solid rgba(0,255,136,0.3); }}
        .badge-orange {{ background:rgba(255,107,53,0.1); color:#ff6b35;  border:1px solid rgba(255,107,53,0.3); }}
        .badge-purple {{ background:rgba(124,58,237,0.1); color:#7c3aed;  border:1px solid rgba(124,58,237,0.3); }}
        .btn {{ display:inline-block; padding:12px 28px; border-radius:10px;
                font-weight:700; font-size:14px; text-decoration:none;
                background:linear-gradient(135deg,#00d4ff,#0099bb); color:#050510; }}
        .divider {{ height:1px; background:rgba(0,212,255,0.1); margin:24px 0; }}
        .order-table {{ width:100%; border-collapse:collapse; margin:16px 0; }}
        .order-table th {{ text-align:left; padding:10px 12px; font-size:11px;
                           text-transform:uppercase; letter-spacing:1px; color:#4a5568;
                           border-bottom:1px solid rgba(0,212,255,0.1); }}
        .order-table td {{ padding:12px; font-size:13px; color:#a0aec0;
                           border-bottom:1px solid rgba(255,255,255,0.04); }}
        .order-table td.price {{ color:#00d4ff; font-weight:700; }}
        .total-row td {{ background:rgba(0,212,255,0.05);
                         color:#00d4ff !important; font-weight:700 !important; font-size:15px !important; }}
        .info-box {{ background:rgba(0,212,255,0.05); border:1px solid rgba(0,212,255,0.15);
                     border-radius:10px; padding:16px; margin:16px 0; }}
        .info-box p {{ margin:0; font-size:13px; }}
        .steps {{ display:table; width:100%; margin:20px 0; }}
        .step  {{ display:table-cell; text-align:center; }}
        .step-dot {{ width:32px; height:32px; border-radius:50%; margin:0 auto 6px;
                     line-height:32px; font-size:14px; }}
        .step-active   {{ background:rgba(0,212,255,0.2); border:2px solid #00d4ff; color:#00d4ff; }}
        .step-inactive {{ background:rgba(255,255,255,0.05); border:2px solid rgba(255,255,255,0.1); color:#4a5568; }}
        .step p {{ font-size:10px; color:#4a5568; margin:0; }}
        .step p.active {{ color:#00d4ff; }}
      </style>
    </head>
    <body>
      <div class="wrapper">
        <div class="header">
          <div class="logo">TECH<span>STORE</span></div>
          <p style="color:#4a5568;font-size:12px;margin-top:6px;">Tu tienda tech de confianza</p>
        </div>
        <div class="body">{content}</div>
        <div class="footer">
          <p>© 2025 TechStore · Todos los derechos reservados</p>
          <p style="margin-top:4px;">Este es un correo automático, no respondas a este mensaje.</p>
        </div>
      </div>
    </body>
    </html>
    """

# ── 1. Bienvenida al registrarse ──────────────────────────────────────────────
def send_welcome_email(user_email: str, user_name: str):
    content = f"""
    <h1>¡Bienvenido a TechStore! 👋</h1>
    <p>Hola <strong style="color:#ffffff">{user_name}</strong>,
       nos alegra que te hayas unido a nuestra comunidad tech.</p>
    <div class="divider"></div>
    <p style="color:#ffffff;font-weight:600;margin-bottom:12px;">¿Qué puedes hacer ahora?</p>
    <div class="info-box" style="margin-bottom:10px">
      <p>🛍️ <strong style="color:#ffffff">Explorar productos</strong> —
         Smartphones, laptops, gaming, audio y más</p>
    </div>
    <div class="info-box" style="margin-bottom:10px">
      <p>💳 <strong style="color:#ffffff">Comprar de forma segura</strong> —
         Pagos con tarjeta protegidos por Stripe</p>
    </div>
    <div class="info-box" style="margin-bottom:10px">
      <p>📦 <strong style="color:#ffffff">Rastrear tus pedidos</strong> —
         Sigue el estado de tus compras en tiempo real</p>
    </div>
    <div class="divider"></div>
    <p>Si tienes alguna duda estamos disponibles por WhatsApp 📱</p>
    """
    try:
        resend.Emails.send({
            "from":    FROM_EMAIL,
            "to":      [user_email],
            "subject": "🎉 ¡Bienvenido a TechStore!",
            "html":    _base_template(content),
        })
        print(f"[EMAIL] Bienvenida enviada a {user_email}")
    except Exception as e:
        print(f"[EMAIL ERROR] welcome: {e}")


# ── 2. Confirmación de orden ──────────────────────────────────────────────────
def send_order_confirmation(order: dict, user_email: str, user_name: str):
    items_html = ""
    for item in order.get("items", []):
        items_html += f"""
        <tr>
          <td>{item.get('name','Producto')}</td>
          <td style="text-align:center">{item.get('quantity',1)}</td>
          <td class="price" style="text-align:right">S/ {float(item.get('price',0)):.2f}</td>
        </tr>
        """
    order_id = str(order.get("id", order.get("_id", "N/A")))[-8:].upper()
    total    = float(order.get("total", 0))
    content  = f"""
    <h1>¡Gracias por tu compra! 🎉</h1>
    <p>Hola <strong style="color:#ffffff">{user_name}</strong>,
       tu pedido ha sido confirmado y está siendo procesado.</p>
    <div class="info-box">
      <p>📦 Número de orden: <strong style="color:#00d4ff">#{order_id}</strong></p>
    </div>
    <div class="divider"></div>
    <table class="order-table">
      <thead>
        <tr>
          <th>Producto</th>
          <th style="text-align:center">Cant.</th>
          <th style="text-align:right">Precio</th>
        </tr>
      </thead>
      <tbody>
        {items_html}
        <tr class="total-row">
          <td colspan="2"><strong>TOTAL</strong></td>
          <td class="price" style="text-align:right">S/ {total:.2f}</td>
        </tr>
      </tbody>
    </table>
    <div class="divider"></div>
    <p style="color:#ffffff;font-weight:600;margin-bottom:12px;">Estado de tu pedido:</p>
    <div class="steps">
      <div class="step">
        <div class="step-dot step-active">✓</div>
        <p class="active">Confirmado</p>
      </div>
      <div class="step">
        <div class="step-dot step-inactive">📦</div>
        <p>Preparando</p>
      </div>
      <div class="step">
        <div class="step-dot step-inactive">🚚</div>
        <p>En camino</p>
      </div>
      <div class="step">
        <div class="step-dot step-inactive">✅</div>
        <p>Entregado</p>
      </div>
    </div>
    <div class="divider"></div>
    <p>Te notificaremos cuando tu pedido sea enviado. Si tienes dudas escríbenos por WhatsApp 📱</p>
    """
    try:
        resend.Emails.send({
            "from":    FROM_EMAIL,
            "to":      [user_email],
            "subject": f"✅ Pedido #{order_id} confirmado — TechStore",
            "html":    _base_template(content),
        })
        print(f"[EMAIL] Confirmación de orden enviada a {user_email}")
    except Exception as e:
        print(f"[EMAIL ERROR] order_confirmation: {e}")


# ── 3. Cambio de estado de orden ──────────────────────────────────────────────
STATUS_CONFIG = {
    "confirmed": ("📦 Tu pedido fue confirmado",  "badge-blue",   "confirmado y está siendo preparado"),
    "shipped":   ("🚚 Tu pedido está en camino",   "badge-purple", "enviado y está en camino a tu dirección"),
    "delivered": ("✅ Tu pedido fue entregado",    "badge-green",  "entregado exitosamente. ¡Disfrútalo!"),
    "cancelled": ("❌ Tu pedido fue cancelado",    "badge-orange", "cancelado"),
}

def send_order_status_update(order: dict, user_email: str, user_name: str, new_status: str):
    cfg = STATUS_CONFIG.get(new_status)
    if not cfg:
        return
    title, badge_class, desc = cfg
    order_id = str(order.get("id", order.get("_id", "N/A")))[-8:].upper()
    total    = float(order.get("total", 0))
    extra    = ""
    if new_status == "delivered":
        extra = "<p>¡Esperamos que disfrutes tu compra! Si tienes algún problema contáctanos 🎉</p>"
    if new_status == "cancelled":
        extra = "<p>Si no solicitaste esta cancelación contáctanos por WhatsApp inmediatamente.</p>"
    content = f"""
    <h1>{title}</h1>
    <p>Hola <strong style="color:#ffffff">{user_name}</strong>,
       tu pedido <strong style="color:#00d4ff">#{order_id}</strong> ha sido {desc}.</p>
    <div class="info-box">
      <p>Estado actual:
        <span class="badge {badge_class}" style="margin-left:8px">{new_status.upper()}</span>
      </p>
    </div>
    <div class="divider"></div>
    <p>Total de tu pedido: <strong style="color:#00d4ff">S/ {total:.2f}</strong></p>
    {extra}
    """
    try:
        resend.Emails.send({
            "from":    FROM_EMAIL,
            "to":      [user_email],
            "subject": f"{title} — TechStore #{order_id}",
            "html":    _base_template(content),
        })
        print(f"[EMAIL] Estado actualizado enviado a {user_email}: {new_status}")
    except Exception as e:
        print(f"[EMAIL ERROR] status_update: {e}")


# ── 4. Notificación al admin de nueva orden ───────────────────────────────────
def send_admin_new_order(order: dict, user_email: str, user_name: str):
    items_html = ""
    for item in order.get("items", []):
        items_html += f"""
        <tr>
          <td>{item.get('name','Producto')}</td>
          <td style="text-align:center">{item.get('quantity',1)}</td>
          <td class="price" style="text-align:right">S/ {float(item.get('price',0)):.2f}</td>
        </tr>
        """
    order_id = str(order.get("id", order.get("_id", "N/A")))[-8:].upper()
    total    = float(order.get("total", 0))
    content  = f"""
    <h1>🛒 Nueva orden recibida</h1>
    <p>Se ha realizado una nueva compra en TechStore.</p>
    <div class="info-box">
      <p>👤 Cliente: <strong style="color:#ffffff">{user_name}</strong> ({user_email})</p>
      <p style="margin-top:6px">📦 Orden: <strong style="color:#00d4ff">#{order_id}</strong></p>
    </div>
    <table class="order-table">
      <thead>
        <tr>
          <th>Producto</th>
          <th style="text-align:center">Cant.</th>
          <th style="text-align:right">Precio</th>
        </tr>
      </thead>
      <tbody>
        {items_html}
        <tr class="total-row">
          <td colspan="2"><strong>TOTAL</strong></td>
          <td class="price" style="text-align:right">S/ {total:.2f}</td>
        </tr>
      </tbody>
    </table>
    """
    try:
        resend.Emails.send({
            "from":    FROM_EMAIL,
            "to":      [ADMIN_EMAIL],
            "subject": f"🛒 Nueva orden #{order_id} — S/ {total:.2f}",
            "html":    _base_template(content),
        })
        print(f"[EMAIL] Admin notificado de nueva orden #{order_id}")
    except Exception as e:
        print(f"[EMAIL ERROR] admin_new_order: {e}")


# ── 5. Recuperación de contraseña ─────────────────────────────────────────────
def send_password_reset(user_email: str, user_name: str, reset_token: str,
                         base_url: str = "http://localhost:5173"):
    reset_url = f"{base_url}/reset-password?token={reset_token}"
    content   = f"""
    <h1>Recuperar contraseña 🔑</h1>
    <p>Hola <strong style="color:#ffffff">{user_name}</strong>,
       recibimos una solicitud para restablecer tu contraseña.</p>
    <div class="divider"></div>
    <p>Haz click en el botón de abajo para crear una nueva contraseña.
       Este enlace expira en <strong style="color:#ff6b35">30 minutos</strong>.</p>
    <div style="text-align:center;margin:28px 0">
      <a href="{reset_url}" class="btn">Restablecer contraseña</a>
    </div>
    <div class="divider"></div>
    <div class="info-box">
      <p>⚠️ Si no solicitaste este cambio, ignora este correo.
         Tu contraseña no será modificada.</p>
    </div>
    <p style="font-size:12px;color:#4a5568;margin-top:16px">
      O copia este enlace en tu navegador:<br>
      <span style="color:#00d4ff;word-break:break-all">{reset_url}</span>
    </p>
    """
    try:
        resend.Emails.send({
            "from":    FROM_EMAIL,
            "to":      [user_email],
            "subject": "🔑 Restablecer contraseña — TechStore",
            "html":    _base_template(content),
        })
        print(f"[EMAIL] Reset de contraseña enviado a {user_email}")
    except Exception as e:
        print(f"[EMAIL ERROR] password_reset: {e}")