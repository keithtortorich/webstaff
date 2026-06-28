/**
 * WebStaff Lead Capture — Netlify Function
 * Receives form submissions from generated client sites.
 *
 * In production: replace the TODO block with:
 *   - Webhook to a CRM (GoHighLevel, HubSpot, etc.)
 *   - Twilio SMS notification to the contractor
 *   - Email via SendGrid to the lead routing contact
 *
 * Env vars (set in Netlify dashboard):
 *   NOTIFY_PHONE   — contractor's phone for SMS alert
 *   NOTIFY_EMAIL   — contractor's email for lead alert
 *   WEBSTAFF_SECRET — shared secret for internal builds
 */

exports.handler = async (event) => {
  const HEADERS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json",
  };

  // CORS preflight
  if (event.httpMethod === "OPTIONS") {
    return { statusCode: 200, headers: HEADERS, body: "" };
  }

  if (event.httpMethod !== "POST") {
    return { statusCode: 405, headers: HEADERS, body: JSON.stringify({ error: "Method not allowed" }) };
  }

  let data;
  try {
    data = JSON.parse(event.body || "{}");
  } catch {
    return { statusCode: 400, headers: HEADERS, body: JSON.stringify({ error: "Invalid JSON" }) };
  }

  // Basic validation
  if (!data.phone && !data.name) {
    return {
      statusCode: 400,
      headers: HEADERS,
      body: JSON.stringify({ error: "At minimum, name or phone is required" }),
    };
  }

  // Structured lead record
  const lead = {
    received_at: new Date().toISOString(),
    name:        data.name        || "",
    phone:       data.phone       || "",
    email:       data.email       || "",
    service:     data.service     || "",
    message:     data.message     || "",
    source_site: event.headers?.referer || "unknown",
    // WebStaff metadata (injected by site generator)
    webstaff_plan:    data.webstaff_plan    || "",
    webstaff_client:  data.webstaff_client  || "",
  };

  // Log to Netlify function logs (visible in Netlify dashboard)
  console.log("NEW_LEAD", JSON.stringify(lead));

  // TODO (production): uncomment and configure
  //
  // ── Twilio SMS to contractor ─────────────────────────────────────────
  // const twilio = require("twilio")(process.env.TWILIO_SID, process.env.TWILIO_AUTH);
  // await twilio.messages.create({
  //   body: `New lead: ${lead.name} · ${lead.phone} · ${lead.service}`,
  //   from: process.env.TWILIO_FROM,
  //   to:   process.env.NOTIFY_PHONE,
  // });
  //
  // ── Webhook to CRM ────────────────────────────────────────────────────
  // await fetch(process.env.CRM_WEBHOOK_URL, {
  //   method:  "POST",
  //   headers: { "Content-Type": "application/json" },
  //   body:    JSON.stringify(lead),
  // });

  return {
    statusCode: 200,
    headers: HEADERS,
    body: JSON.stringify({
      success: true,
      message: "We'll be in touch within 1 hour.",
    }),
  };
};
