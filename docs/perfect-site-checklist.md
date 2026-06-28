THE PERFECT SITE — BUILD CHECKLIST
🟧 1. HERO
[ ] Full-screen real photo/video — your work, your people. No stock.
[ ] Headline = the promise: "[Result] for [audience] without [pain]"
[ ] Subheadline = location + specialty + speed
[ ] CTA #1 (ready now): "Call Now" / "Book Appointment"
[ ] CTA #2 (still researching): "See Our Work" / "How It Works"
🟧 2. TRUST BAR
[ ] Live Google stars + review count
[ ] Cert/affiliation logos
[ ] One killer stat: "Serving [City] since ___ · ___ jobs completed"
🟧 3. SERVICES
[ ] 3–6 cards only — top earners, not the laundry list
[ ] Each card: name + one-line benefit + CTA link
[ ] Each links to its own page: problem headline → what's included → 3-step process → pricing signal → 5 FAQs → CTA
[ ] Title each page "[Service] in [City]" ← local SEO weapon
🟧 4. WHY US
[ ] 3 columns, 3 real differentiators
[ ] Specific > generic: "Same-day, guaranteed" ✅ / "We care" ❌
[ ] Can't name 3? Fix the offer before the website.
🟧 5. PROOF
[ ] Live-pulled reviews (no screenshots)
[ ] Visual trades/MedSpa: before/after sliders
[ ] Service biz: testimonials w/ name + photo
[ ] ⚠️ Medical: signed release, zero PHI
🟧 6. STORY
[ ] One short section. Owner/team photo. Human origin story.
[ ] This is where local beats the chains — don't skip it.
🟧 7. LOCAL PRESENCE
[ ] Embedded Google Map
[ ] City/neighborhood list
[ ] Phone number — big, clickable
🟧 8. LEAD CAPTURE
[ ] High-contrast section. One headline. One form OR phone.
[ ] 3 fields max: name · phone · service needed
[ ] Incentive: "Free estimate" / "First visit free"
[ ] Response promise: "We reply within 1 business hour"
[ ] Mobile: sticky call/text bar on every page
🟧 9. FOOTER
[ ] Logo · nav · contact · social · privacy policy
[ ] License #s (non-negotiable for trades)
⚙️ TECHNICAL FLOOR
[ ] Mobile-first · loads under ~3s
[ ] Click-to-call everywhere
[ ] One H1/page · titles = "[Service] [City] | [Brand]"
[ ] LocalBusiness/MedicalClinic schema
[ ] SSL · WebP images · alt text
[ ] GBP linked, NAP matches exactly



🔨 BUILD ORDER
☐ Nail offer + headline
☐ Collect proof assets
☐ Build 9-section homepage
☐ Build service pages
☐ Technical floor
☐ GBP + local SEO
☐ Iterate on analytics








INTAKE FORM — 9 SECTIONS
1 · BASICS → name · contact · address · industry · service area · years in biz · emergency service Y/N
2 · WEB PRESENCE (conditional) → site Y/N → URL · platform · domain owner · registrar access · what's broken | + GBP exists? access?
3 · BRAND (conditional) → logo upload · colors or "build for me" · personality in 3 words · 2–3 sites they like
4 · POSITIONING → mission (1 sentence) · #1 reason customers pick you · top 3 competitors · tone · tagline
5 · SERVICES → top 3–6 ranked by profit · pricing shown? (yes/ranges/no) · promos · seasonal
6 · PROOF → Google review link + count · certs + license #s · before/afters upload · testimonials (+ release if medical)
7 · SOCIAL & TOOLS → platforms + URLs · embed Y/N · booking system · CRM
8 · GOALS & LOGISTICS → #1 site goal · feature checklist · leads go where? who answers? how fast? · timeline · budget · final approver
9 · CONTENT & SEO → photos exist or shoot needed · who writes copy · 5–10 customer keywords · extra pages · open notes
Mechanics: ☐ progress bar ☐ conditional blocks ☐ confirmation screen






Industry
Font
Vibe
Unique Feature
Contractor
Oswald + Inter
Industrial, rugged
Dark theme, underline accent on hover, stats bar
Restaurant
Playfair Display
Warm Italian
Centered hero, menu cards with prices, story section
 Med Spa
Cormorant Garamond
Luxurious, elegant
Purple gradients, treatment cards with prices
Dentist
Outfit + Inter
Clean, modern
Teal scheme, big stat numbers, rounded cards
Plumber
Archivo Black
Bold, urgent
Blue sticky nav/red emergency bar, guarantee badge
Electrician
Sora + Inter
Dark, energetic
Yellow/amber on dark, diagonal hero layout
Real Estate
DM Serif Display
Sophisticated
Green + gold, serif typography, premium stamp
 Law Firm
Lora + Inter
Serious, traditional
Navy + gold, star badges, structured layout
Gym
Bebas Neue
Aggressive, bold
All-black theme, red accents, angled hero image
 Other
Space Grotesk
Modern, clean
Blue gradient, process steps, multi-purpose



INTAKE HTML


<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Client Intake — Frontline AI</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root{
    --bg:#14160F;
    --panel:#1C1F15;
    --panel-2:#22261A;
    --line:#3A3F2C;
    --bone:#E9E4D4;
    --khaki:#A8A488;
    --amber:#E8941A;
    --amber-dim:#9C6512;
    --green:#8FAE5D;
    --red:#D26A4A;
    --radius:10px;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html{scroll-behavior:smooth}
  body{
    background:var(--bg);
    color:var(--bone);
    font-family:'Inter',system-ui,sans-serif;
    font-size:15px;
    line-height:1.55;
    background-image:radial-gradient(ellipse at 50% -10%, #20241640 0%, transparent 60%);
  }

  /* ---------- sticky progress readout ---------- */
  .tracker{
    position:sticky;top:0;z-index:50;
    background:rgba(20,22,15,.92);
    backdrop-filter:blur(8px);
    border-bottom:1px solid var(--line);
    padding:12px 20px 10px;
  }
  .tracker-inner{max-width:760px;margin:0 auto}
  .tracker-row{display:flex;justify-content:space-between;align-items:baseline;gap:12px}
  .tracker-label{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.18em;color:var(--khaki);text-transform:uppercase}
  .tracker-pct{font-family:'Saira Condensed',sans-serif;font-size:22px;font-weight:700;color:var(--amber);min-width:64px;text-align:right}
  .bar{height:6px;background:var(--panel-2);border-radius:3px;margin-top:8px;overflow:hidden}
  .bar-fill{height:100%;width:0%;background:linear-gradient(90deg,var(--amber-dim),var(--amber));border-radius:3px;transition:width .35s ease}
  .pips{display:flex;gap:5px;margin-top:8px}
  .pip{flex:1;height:3px;border-radius:2px;background:var(--line);transition:background .3s}
  .pip.done{background:var(--green)}
  .pip.active{background:var(--amber)}

  /* ---------- header ---------- */
  header{max-width:760px;margin:0 auto;padding:44px 20px 8px}
  .eyebrow{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.22em;color:var(--amber);text-transform:uppercase}
  h1{font-family:'Saira Condensed',sans-serif;font-size:clamp(34px,6vw,52px);font-weight:700;letter-spacing:.02em;text-transform:uppercase;line-height:1.05;margin:8px 0 10px}
  .lede{color:var(--khaki);max-width:560px}
  .lede strong{color:var(--bone)}

  /* ---------- form ---------- */
  form{max-width:760px;margin:0 auto;padding:24px 20px 80px}
  section.card{
    background:var(--panel);
    border:1px solid var(--line);
    border-radius:var(--radius);
    padding:26px 24px 28px;
    margin-bottom:22px;
  }
  .sec-head{display:flex;align-items:baseline;gap:12px;border-bottom:1px solid var(--line);padding-bottom:12px;margin-bottom:20px}
  .sec-num{font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--amber);letter-spacing:.15em}
  .sec-title{font-family:'Saira Condensed',sans-serif;font-size:22px;font-weight:700;text-transform:uppercase;letter-spacing:.04em}

  .field{margin-bottom:18px}
  .field:last-child{margin-bottom:0}
  label.q{display:block;font-weight:600;font-size:14px;margin-bottom:6px}
  .hint{font-size:12.5px;color:var(--khaki);margin:-2px 0 7px}
  .req{color:var(--amber);font-weight:600}

  input[type=text],input[type=tel],input[type=email],input[type=url],input[type=number],select,textarea{
    width:100%;
    background:var(--panel-2);
    border:1px solid var(--line);
    border-radius:7px;
    color:var(--bone);
    font:inherit;
    padding:11px 13px;
    transition:border-color .15s, box-shadow .15s;
  }
  textarea{min-height:88px;resize:vertical}
  input:focus,select:focus,textarea:focus{outline:none;border-color:var(--amber);box-shadow:0 0 0 3px rgba(232,148,26,.15)}
  input.invalid,select.invalid,textarea.invalid{border-color:var(--red)}
  select{appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%23A8A488' stroke-width='2' fill='none'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 13px center;padding-right:36px}

  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px 16px}
  @media(max-width:560px){.grid2{grid-template-columns:1fr}}

  /* choice chips (radio/checkbox) */
  .chips{display:flex;flex-wrap:wrap;gap:8px}
  .chip{position:relative}
  .chip input{position:absolute;opacity:0;inset:0;cursor:pointer}
  .chip span{
    display:inline-block;
    padding:8px 14px;
    border:1px solid var(--line);
    border-radius:999px;
    background:var(--panel-2);
    color:var(--khaki);
    font-size:13.5px;
    cursor:pointer;
    transition:all .15s;
    user-select:none;
  }
  .chip input:checked + span{background:rgba(232,148,26,.14);border-color:var(--amber);color:var(--bone)}
  .chip input:focus-visible + span{box-shadow:0 0 0 3px rgba(232,148,26,.25)}

  /* conditional blocks */
  .cond{display:none;margin-top:14px;padding:16px;border-left:2px solid var(--amber);background:rgba(232,148,26,.05);border-radius:0 8px 8px 0;animation:slide .25s ease}
  .cond.open{display:block}
  @keyframes slide{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:none}}

  .note{font-family:'IBM Plex Mono',monospace;font-size:11.5px;color:var(--khaki);background:var(--panel-2);border:1px dashed var(--line);border-radius:7px;padding:10px 12px;margin-top:10px}
  .note b{color:var(--amber);font-weight:500}

  input[type=file]{color:var(--khaki);font-size:13px}
  input[type=file]::file-selector-button{
    background:var(--panel-2);border:1px solid var(--line);color:var(--bone);
    padding:8px 14px;border-radius:7px;margin-right:10px;cursor:pointer;font:inherit;font-size:13px;
  }

  /* submit */
  .submit-wrap{text-align:center;padding-top:6px}
  button.go{
    font-family:'Saira Condensed',sans-serif;
    font-size:20px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
    background:var(--amber);color:#14160F;border:none;border-radius:8px;
    padding:15px 44px;cursor:pointer;transition:transform .12s, box-shadow .12s;
  }
  button.go:hover{transform:translateY(-1px);box-shadow:0 6px 22px rgba(232,148,26,.3)}
  .err-msg{color:var(--red);font-size:13.5px;margin-top:12px;display:none}

  /* confirmation */
  .confirm{display:none;max-width:760px;margin:0 auto;padding:60px 20px;text-align:center}
  .confirm.show{display:block;animation:slide .4s ease}
  .confirm .badge{
    width:74px;height:74px;border-radius:50%;border:2px solid var(--green);
    display:flex;align-items:center;justify-content:center;margin:0 auto 18px;
    font-size:32px;color:var(--green);
  }
  .confirm h2{font-family:'Saira Condensed',sans-serif;font-size:34px;text-transform:uppercase;letter-spacing:.03em;margin-bottom:10px}
  .confirm p{color:var(--khaki);max-width:480px;margin:0 auto 22px}
  .confirm button{
    background:var(--panel-2);color:var(--bone);border:1px solid var(--line);
    border-radius:8px;padding:11px 22px;font:inherit;font-size:14px;cursor:pointer;
  }
  .confirm button:hover{border-color:var(--amber)}

  footer{max-width:760px;margin:0 auto;padding:0 20px 40px;text-align:center;font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.15em;color:#5a5e48;text-transform:uppercase}
</style>
</head>
<body>

<div class="tracker">
  <div class="tracker-inner">
    <div class="tracker-row">
      <span class="tracker-label">Intake Progress</span>
      <span class="tracker-pct" id="pct">0%</span>
    </div>
    <div class="bar"><div class="bar-fill" id="barFill"></div></div>
    <div class="pips" id="pips"></div>
  </div>
</div>

<header>
  <div class="eyebrow">Frontline AI · Mission Intake</div>
  <h1>New Client Questionnaire</h1>
  <p class="lede">15 minutes here gives us <strong>80% of what we need</strong> before your first call — so the call is about strategy, not paperwork. Required fields are marked <span class="req">*</span>.</p>
</header>

<form id="intake" novalidate>

  <!-- ============ SECTION 1 ============ -->
  <section class="card" data-sec="1">
    <div class="sec-head"><span class="sec-num">01 /</span><span class="sec-title">Business Basics</span></div>
    <div class="grid2">
      <div class="field"><label class="q">Business name <span class="req">*</span></label><input type="text" name="biz_name" required></div>
      <div class="field"><label class="q">Your name <span class="req">*</span></label><input type="text" name="contact_name" required></div>
      <div class="field"><label class="q">Phone <span class="req">*</span></label><input type="tel" name="phone" required></div>
      <div class="field"><label class="q">Email <span class="req">*</span></label><input type="email" name="email" required></div>
    </div>
    <div class="field"><label class="q">Business address</label><input type="text" name="address" placeholder="Street, city, province/state"></div>
    <div class="grid2">
      <div class="field">
        <label class="q">Industry <span class="req">*</span></label>
        <select name="industry" id="industry" required>
          <option value="">Select one…</option>
          <option>Medical / Dental / Health</option>
          <option>MedSpa / Aesthetics</option>
          <option>Contractor / Construction</option>
          <option>Plumbing / HVAC / Electrical</option>
          <option>Roofing</option>
          <option>Auto Repair / Detailing</option>
          <option>Landscaping / Cleaning</option>
          <option>Professional Services</option>
          <option>Solopreneur / Consultant</option>
          <option>Other</option>
        </select>
      </div>
      <div class="field"><label class="q">Years in business</label><input type="number" name="years" min="0" placeholder="e.g. 12"></div>
    </div>
    <div class="field"><label class="q">Service area <span class="req">*</span></label><p class="hint">Cities, neighborhoods, or radius you serve</p><input type="text" name="service_area" required placeholder="e.g. Angeles City + 25km, Clark, Mabalacat"></div>
    <div class="field">
      <label class="q">Do you offer emergency / after-hours service?</label>
      <div class="chips">
        <label class="chip"><input type="radio" name="emergency" value="Yes"><span>Yes</span></label>
        <label class="chip"><input type="radio" name="emergency" value="No"><span>No</span></label>
      </div>
    </div>
  </section>

  <!-- ============ SECTION 2 ============ -->
  <section class="card" data-sec="2">
    <div class="sec-head"><span class="sec-num">02 /</span><span class="sec-title">Current Web Presence</span></div>
    <div class="field">
      <label class="q">Do you have a website right now? <span class="req">*</span></label>
      <div class="chips">
        <label class="chip"><input type="radio" name="has_site" value="Yes" data-cond="siteYes" required><span>Yes</span></label>
        <label class="chip"><input type="radio" name="has_site" value="No" data-cond="siteNo"><span>No</span></label>
      </div>
      <div class="cond" id="siteYes">
        <div class="field"><label class="q">Website URL</label><input type="url" name="site_url" placeholder="https://"></div>
        <div class="grid2">
          <div class="field"><label class="q">Platform (if known)</label><input type="text" name="site_platform" placeholder="WordPress, Wix, GoDaddy, no idea…"></div>
          <div class="field"><label class="q">Who owns the domain?</label><input type="text" name="domain_owner" placeholder="Me / old web guy / not sure"></div>
        </div>
        <div class="field">
          <label class="q">Do you have login access to the domain registrar?</label>
          <div class="chips">
            <label class="chip"><input type="radio" name="registrar_access" value="Yes"><span>Yes</span></label>
            <label class="chip"><input type="radio" name="registrar_access" value="No"><span>No</span></label>
            <label class="chip"><input type="radio" name="registrar_access" value="Not sure"><span>Not sure</span></label>
          </div>
        </div>
        <div class="field"><label class="q">What's working — and what's broken?</label><textarea name="site_pain" placeholder="e.g. Looks dated, no calls coming in, can't edit it myself…"></textarea></div>
      </div>
      <div class="cond" id="siteNo">
        <div class="field">
          <label class="q">Do you already own a domain name?</label>
          <div class="chips">
            <label class="chip"><input type="radio" name="owns_domain" value="Yes"><span>Yes</span></label>
            <label class="chip"><input type="radio" name="owns_domain" value="No"><span>No</span></label>
          </div>
        </div>
      </div>
    </div>
    <div class="field">
      <label class="q">Do you have a Google Business Profile?</label>
      <div class="chips">
        <label class="chip"><input type="radio" name="has_gbp" value="Yes" data-cond="gbpYes"><span>Yes</span></label>
        <label class="chip"><input type="radio" name="has_gbp" value="No"><span>No</span></label>
        <label class="chip"><input type="radio" name="has_gbp" value="Not sure"><span>Not sure</span></label>
      </div>
      <div class="cond" id="gbpYes">
        <div class="field">
          <label class="q">Can you grant us manager access?</label>
          <p class="hint">This is the single biggest lever for local search visibility.</p>
          <div class="chips">
            <label class="chip"><input type="radio" name="gbp_access" value="Yes"><span>Yes</span></label>
            <label class="chip"><input type="radio" name="gbp_access" value="Need help"><span>I'll need help doing that</span></label>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- ============ SECTION 3 ============ -->
  <section class="card" data-sec="3">
    <div class="sec-head"><span class="sec-num">03 /</span><span class="sec-title">Brand Assets</span></div>
    <div class="field">
      <label class="q">Do you have a logo?</label>
      <div class="chips">
        <label class="chip"><input type="radio" name="has_logo" value="Yes" data-cond="logoYes"><span>Yes</span></label>
        <label class="chip"><input type="radio" name="has_logo" value="No"><span>No — build one for me</span></label>
      </div>
      <div class="cond" id="logoYes">
        <div class="field"><label class="q">Upload your logo</label><input type="file" name="logo_file" accept="image/*,.pdf,.svg"></div>
      </div>
    </div>
    <div class="field"><label class="q">Brand colors</label><input type="text" name="brand_colors" placeholder="Hex codes, “navy and gold,” or “pick for me”"></div>
    <div class="field"><label class="q">Your brand personality in 3 words</label><input type="text" name="personality" placeholder="e.g. Reliable, fast, no-nonsense"></div>
    <div class="field"><label class="q">2–3 websites you like — and why</label><textarea name="inspo" placeholder="Paste URLs, one per line, with a note on what you like"></textarea></div>
  </section>

  <!-- ============ SECTION 4 ============ -->
  <section class="card" data-sec="4">
    <div class="sec-head"><span class="sec-num">04 /</span><span class="sec-title">Positioning</span></div>
    <div class="field"><label class="q">Your mission in one sentence</label><input type="text" name="mission" placeholder="What you do, who for, and the result"></div>
    <div class="field"><label class="q">The #1 reason customers choose you over competitors <span class="req">*</span></label><p class="hint">Be specific. “Same-day service, guaranteed” beats “we care.”</p><textarea name="differentiator" required></textarea></div>
    <div class="field"><label class="q">Your top 2–3 local competitors</label><input type="text" name="competitors" placeholder="Names or websites"></div>
    <div class="field">
      <label class="q">Voice / tone preference</label>
      <div class="chips">
        <label class="chip"><input type="radio" name="tone" value="Professional"><span>Professional</span></label>
        <label class="chip"><input type="radio" name="tone" value="Friendly"><span>Friendly &amp; warm</span></label>
        <label class="chip"><input type="radio" name="tone" value="Bold"><span>Bold &amp; direct</span></label>
        <label class="chip"><input type="radio" name="tone" value="Premium"><span>Premium / luxury</span></label>
      </div>
    </div>
    <div class="field"><label class="q">Existing tagline (if any)</label><input type="text" name="tagline"></div>
  </section>

  <!-- ============ SECTION 5 ============ -->
  <section class="card" data-sec="5">
    <div class="sec-head"><span class="sec-num">05 /</span><span class="sec-title">Services &amp; Offers</span></div>
    <div class="field"><label class="q">Your top 3–6 services — ranked by profit, not volume <span class="req">*</span></label><textarea name="services" required placeholder="One per line, most profitable first"></textarea></div>
    <div class="field">
      <label class="q">Show pricing on the site?</label>
      <div class="chips">
        <label class="chip"><input type="radio" name="pricing" value="Exact"><span>Yes — exact prices</span></label>
        <label class="chip"><input type="radio" name="pricing" value="Ranges"><span>Ranges / “starting at”</span></label>
        <label class="chip"><input type="radio" name="pricing" value="No"><span>No pricing</span></label>
      </div>
    </div>
    <div class="field"><label class="q">Current promos or incentives</label><input type="text" name="promos" placeholder="Free estimate, first visit free, 10% off…"></div>
    <div class="field"><label class="q">Seasonal services?</label><input type="text" name="seasonal" placeholder="e.g. AC tune-ups in summer"></div>
  </section>

  <!-- ============ SECTION 6 ============ -->
  <section class="card" data-sec="6">
    <div class="sec-head"><span class="sec-num">06 /</span><span class="sec-title">Proof Assets</span></div>
    <div class="grid2">
      <div class="field"><label class="q">Google review link or business name as listed</label><input type="text" name="review_link"></div>
      <div class="field"><label class="q">Approx. review count + star rating</label><input type="text" name="review_stats" placeholder="e.g. 84 reviews · 4.8★"></div>
    </div>
    <div class="field"><label class="q">Certifications &amp; license numbers</label><p class="hint">These go in the footer — critical for trades.</p><textarea name="certs"></textarea></div>
    <div class="field">
      <label class="q">Do you have before/after photos?</label>
      <div class="chips">
        <label class="chip"><input type="radio" name="has_ba" value="Yes" data-cond="baYes"><span>Yes</span></label>
        <label class="chip"><input type="radio" name="has_ba" value="No"><span>No</span></label>
      </div>
      <div class="cond" id="baYes">
        <div class="field"><label class="q">Upload a few samples</label><input type="file" name="ba_files" multiple accept="image/*"></div>
      </div>
    </div>
    <div class="field"><label class="q">Testimonials, awards, media mentions</label><textarea name="testimonials"></textarea></div>
    <div class="note" id="hipaaNote" style="display:none"><b>⚠ Health/medical:</b> patient testimonials and photos require a signed release — no protected health information goes on the site without it. We'll handle the release template with you.</div>
  </section>

  <!-- ============ SECTION 7 ============ -->
  <section class="card" data-sec="7">
    <div class="sec-head"><span class="sec-num">07 /</span><span class="sec-title">Social &amp; Tools</span></div>
    <div class="field">
      <label class="q">Active platforms</label>
      <div class="chips">
        <label class="chip"><input type="checkbox" name="social" value="Facebook"><span>Facebook</span></label>
        <label class="chip"><input type="checkbox" name="social" value="Instagram"><span>Instagram</span></label>
        <label class="chip"><input type="checkbox" name="social" value="TikTok"><span>TikTok</span></label>
        <label class="chip"><input type="checkbox" name="social" value="YouTube"><span>YouTube</span></label>
        <label class="chip"><input type="checkbox" name="social" value="LinkedIn"><span>LinkedIn</span></label>
        <label class="chip"><input type="checkbox" name="social" value="None"><span>None</span></label>
      </div>
    </div>
    <div class="field"><label class="q">Profile URLs</label><textarea name="social_urls" placeholder="One per line"></textarea></div>
    <div class="field">
      <label class="q">Embed social feeds on the site?</label>
      <div class="chips">
        <label class="chip"><input type="radio" name="embed" value="Yes"><span>Yes</span></label>
        <label class="chip"><input type="radio" name="embed" value="No"><span>No</span></label>
      </div>
    </div>
    <div class="grid2">
      <div class="field"><label class="q">Booking / scheduling system in use</label><input type="text" name="booking" placeholder="Calendly, Jobber, none…"></div>
      <div class="field"><label class="q">CRM in use</label><input type="text" name="crm" placeholder="GoHighLevel, HubSpot, spreadsheet, none…"></div>
    </div>
  </section>

  <!-- ============ SECTION 8 ============ -->
  <section class="card" data-sec="8">
    <div class="sec-head"><span class="sec-num">08 /</span><span class="sec-title">Goals &amp; Logistics</span></div>
    <div class="field">
      <label class="q">#1 goal for the site <span class="req">*</span></label>
      <div class="chips">
        <label class="chip"><input type="radio" name="goal" value="Phone calls" required><span>Phone calls</span></label>
        <label class="chip"><input type="radio" name="goal" value="Bookings"><span>Bookings</span></label>
        <label class="chip"><input type="radio" name="goal" value="Quote requests"><span>Quote requests</span></label>
        <label class="chip"><input type="radio" name="goal" value="Authority/credibility"><span>Authority</span></label>
      </div>
    </div>
    <div class="field">
      <label class="q">Features you want</label>
      <div class="chips">
        <label class="chip"><input type="checkbox" name="features" value="Online booking"><span>Online booking</span></label>
        <label class="chip"><input type="checkbox" name="features" value="Live chat / AI chat"><span>Live / AI chat</span></label>
        <label class="chip"><input type="checkbox" name="features" value="Payments"><span>Payments</span></label>
        <label class="chip"><input type="checkbox" name="features" value="Photo gallery"><span>Gallery</span></label>
        <label class="chip"><input type="checkbox" name="features" value="Blog"><span>Blog</span></label>
        <label class="chip"><input type="checkbox" name="features" value="Financing calculator"><span>Financing calc</span></label>
      </div>
    </div>
    <div class="field"><label class="q">Where should leads go — and who answers, how fast? <span class="req">*</span></label><p class="hint">Phone, email, text, CRM? Name the person and the response window.</p><textarea name="lead_routing" required placeholder="e.g. Text + email to Maria, replies within 1 hour, 8am–6pm"></textarea></div>
    <div class="grid2">
      <div class="field">
        <label class="q">Timeline</label>
        <select name="timeline">
          <option value="">Select…</option>
          <option>ASAP — this week</option>
          <option>Within 2 weeks</option>
          <option>Within a month</option>
          <option>Flexible</option>
        </select>
      </div>
      <div class="field">
        <label class="q">Budget range</label>
        <select name="budget">
          <option value="">Select…</option>
          <option>Under $500</option>
          <option>$500 – $1,500</option>
          <option>$1,500 – $3,000</option>
          <option>$3,000+</option>
          <option>Monthly plan preferred</option>
        </select>
      </div>
    </div>
    <div class="field"><label class="q">Who has final approval authority? <span class="req">*</span></label><p class="hint">One name. This kills revision loops.</p><input type="text" name="approver" required></div>
  </section>

  <!-- ============ SECTION 9 ============ -->
  <section class="card" data-sec="9">
    <div class="sec-head"><span class="sec-num">09 /</span><span class="sec-title">Content &amp; SEO</span></div>
    <div class="field">
      <label class="q">Photos / video of your business and work</label>
      <div class="chips">
        <label class="chip"><input type="radio" name="assets" value="Have plenty"><span>Have plenty</span></label>
        <label class="chip"><input type="radio" name="assets" value="Have some"><span>Have some</span></label>
        <label class="chip"><input type="radio" name="assets" value="Need a shoot"><span>Need a shoot</span></label>
      </div>
    </div>
    <div class="field">
      <label class="q">Who writes the copy?</label>
      <div class="chips">
        <label class="chip"><input type="radio" name="copy" value="You write it"><span>You write it</span></label>
        <label class="chip"><input type="radio" name="copy" value="I'll provide"><span>I'll provide it</span></label>
        <label class="chip"><input type="radio" name="copy" value="Mix"><span>Mix of both</span></label>
      </div>
    </div>
    <div class="field"><label class="q">5–10 things customers type into Google to find a business like yours</label><textarea name="keywords" placeholder="e.g. emergency plumber angeles city, dental implants near me…"></textarea></div>
    <div class="field"><label class="q">Pages needed beyond the standard five (Home, Services, About, Proof, Contact)?</label><input type="text" name="extra_pages"></div>
    <div class="field"><label class="q">Anything else we should know</label><textarea name="notes"></textarea></div>
  </section>

  <div class="submit-wrap">
    <button type="submit" class="go">Submit Intake →</button>
    <p class="err-msg" id="errMsg">A few required fields are missing — they're highlighted above.</p>
  </div>
</form>

<div class="confirm" id="confirm">
  <div class="badge">✓</div>
  <h2>Intake Received</h2>
  <p>Mission briefing locked in. We'll review everything and come to your first call with a plan — not a list of questions. Expect to hear from us within <strong style="color:var(--bone)">1 business day</strong>.</p>
  <button id="copyBtn">Copy a text summary of your answers</button>
</div>

<footer>Frontline AI · Victory Vibe LLC</footer>

<script>
(function(){
  const form = document.getElementById('intake');
  const pct = document.getElementById('pct');
  const barFill = document.getElementById('barFill');
  const pipsWrap = document.getElementById('pips');
  const errMsg = document.getElementById('errMsg');

  // build 9 section pips
  for(let i=1;i<=9;i++){const d=document.createElement('div');d.className='pip';d.dataset.sec=i;pipsWrap.appendChild(d);}

  // ---- conditional blocks ----
  function refreshConds(){
    // site yes/no
    toggle('siteYes', val('has_site')==='Yes');
    toggle('siteNo',  val('has_site')==='No');
    toggle('gbpYes',  val('has_gbp')==='Yes');
    toggle('logoYes', val('has_logo')==='Yes');
    toggle('baYes',   val('has_ba')==='Yes');
    // HIPAA note for health industries
    const ind = form.industry.value;
    document.getElementById('hipaaNote').style.display =
      (/Medical|MedSpa/.test(ind)) ? 'block' : 'none';
  }
  function val(name){const el=form.querySelector(`[name="${name}"]:checked`);return el?el.value:'';}
  function toggle(id,show){document.getElementById(id).classList.toggle('open',show);}

  // ---- progress ----
  function visibleFields(){
    return [...form.querySelectorAll('input,select,textarea')].filter(el=>{
      if(el.type==='file') return el.closest('.cond') ? el.closest('.cond').classList.contains('open') : true;
      const c = el.closest('.cond');
      return !c || c.classList.contains('open');
    });
  }
  function updateProgress(){
    const els = visibleFields();
    const groups = new Map(); // group radios/checkboxes by name
    els.forEach(el=>{
      const key = el.name || el.id;
      if(!groups.has(key)) groups.set(key, []);
      groups.get(key).push(el);
    });
    let total=0, filled=0;
    const secFill = {}, secTotal = {};
    groups.forEach((items,key)=>{
      total++;
      const sec = items[0].closest('section')?.dataset.sec;
      secTotal[sec]=(secTotal[sec]||0)+1;
      const isFilled = items.some(el=>{
        if(el.type==='radio'||el.type==='checkbox') return el.checked;
        if(el.type==='file') return el.files && el.files.length>0;
        return el.value.trim()!=='';
      });
      if(isFilled){filled++;secFill[sec]=(secFill[sec]||0)+1;}
    });
    const p = total? Math.round(filled/total*100):0;
    pct.textContent = p+'%';
    barFill.style.width = p+'%';
    document.querySelectorAll('.pip').forEach(pip=>{
      const s=pip.dataset.sec;
      const f=secFill[s]||0, t=secTotal[s]||1;
      pip.classList.toggle('done', f>=t);
      pip.classList.toggle('active', f>0 && f<t);
    });
  }

  form.addEventListener('input', ()=>{refreshConds();updateProgress();});
  form.addEventListener('change', ()=>{refreshConds();updateProgress();});

  // ---- submit ----
  form.addEventListener('submit', e=>{
    e.preventDefault();
    let ok=true, firstBad=null;
    form.querySelectorAll('[required]').forEach(el=>{
      const cond=el.closest('.cond');
      if(cond && !cond.classList.contains('open')) return;
      let bad=false;
      if(el.type==='radio'){ bad = !form.querySelector(`[name="${el.name}"]:checked`); }
      else { bad = el.value.trim()===''; }
      el.classList.toggle('invalid', bad);
      if(bad){ ok=false; if(!firstBad) firstBad=el; }
    });
    errMsg.style.display = ok?'none':'block';
    if(!ok){ firstBad.scrollIntoView({behavior:'smooth',block:'center'}); return; }

    // build summary
    const fd=new FormData(form); const lines=[];
    const seen=new Set();
    for(const [k] of fd){ if(seen.has(k))continue; seen.add(k);
      const all=fd.getAll(k).filter(v=>typeof v==='string'&&v.trim()!=='');
      if(all.length) lines.push(k.toUpperCase()+': '+all.join(', '));
    }
    window.__intakeSummary = 'FRONTLINE AI — CLIENT INTAKE\n'+'='.repeat(32)+'\n'+lines.join('\n');

    /* HOOK YOUR ENDPOINT HERE:
       fetch('https://YOUR-WEBHOOK-OR-FORMSPREE-URL', {method:'POST', body:new FormData(form)});
       File uploads need a backend or form service (Formspree, Tally, GHL, n8n webhook). */

    document.querySelector('.tracker').style.display='none';
    form.style.display='none';
    document.getElementById('confirm').classList.add('show');
    window.scrollTo({top:0,behavior:'smooth'});
  });

  document.getElementById('copyBtn').addEventListener('click', function(){
    navigator.clipboard.writeText(window.__intakeSummary||'').then(()=>{
      this.textContent='Copied ✓'; setTimeout(()=>this.textContent='Copy a text summary of your answers',2000);
    });
  });

  refreshConds();
  updateProgress();
})();
</script>
</body>
</html>


