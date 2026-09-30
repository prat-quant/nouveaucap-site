"""Builds the Nouveau Cap website (nouveaucap.pixapop.fr) into docs/, served by GitHub Pages.

Usage: python3 build.py
Sources: this file (page texts), assets/ (styles, script, fonts, images), data/nouveau-cap-legal.json
(prices and publisher, exported by the app repository: node scripts/build-legal.mjs, the same file as
pixapop-site/data/). Standard library only. Never edit docs/ by hand: it is rewritten on every build.
"""
import html
import json
import shutil
import blog
import guides
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
SITE = "https://nouveaucap.pixapop.fr"
AGENCY = "https://www.pixapop.fr"
LEGAL = json.loads((ROOT / "data" / "nouveau-cap-legal.json").read_text(encoding="utf-8"))
PUB = LEGAL["publisher"]
PRICES = LEGAL["prices"]
EMAIL = PUB["email"]
YEAR = date.today().year
# Supabase project pixapop-marketing (sources in the AIOS repo, projects/nouveau-cap-marketing/supabase/).
FUNCTIONS = "https://nidcxvwmdezaxurcwivv.supabase.co/functions/v1"
WAITLIST_URL = FUNCTIONS + "/liste-attente"
GUIDE_URL = FUNCTIONS + "/guide"
VISIT_URL = FUNCTIONS + "/visite"
CONSENT = ("J’accepte que Pixapop conserve mon adresse e-mail uniquement pour me prévenir du lancement de Nouveau Cap. "
           "Elle est effacée après l’annonce, et au plus tard 12 mois après mon inscription.")
# Separate, unticked and optional box of the guide forms (CNIL rule): the guide is sent either way.
GUIDE_NEWS = blog.nbsp("Oui, envoyez-moi aussi 4 conseils pour avancer avec ce guide, puis les nouvelles de Nouveau Cap "
                       "(l’application, les prochains guides), un e-mail par mois au plus. Désinscription en un clic.")
# Google Play page of the app, set on launch day: /app/ then redirects there (link used in the e-mails).
PLAY_URL = ""
# The app's own legal pages stay on pixapop.fr: they are declared to Google Play and must never move.
APP_PRIVACY = AGENCY + "/nouveau-cap/confidentialite/"
APP_TERMS = AGENCY + "/nouveau-cap/conditions/"
APP_NOTICE = AGENCY + "/nouveau-cap/mentions-legales/"
esc = html.escape

ARROW = '<svg class="arr" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'


def page(path, title, description, body, *, jsonld=None, noindex=False):
    """Writes one page. path is the URL path ('/', '/confidentialite/', ...)."""
    url = SITE + path
    lds = "".join(f'<script type="application/ld+json">{json.dumps(d, ensure_ascii=False)}</script>' for d in (jsonld or []))
    doc = f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{url}">
{'<meta name="robots" content="noindex">' if noindex else ''}
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#F3F6FB" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#061631" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="Nouveau Cap">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/img/og-light.jpg">
<link rel="icon" href="/assets/img/favicon-64.png" type="image/png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/sora-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/manrope-latin-500-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/styles.css">
<link rel="alternate" type="application/rss+xml" title="Blog Nouveau Cap" href="/blog/feed.xml">
{lds}
</head>
<body data-visit="{VISIT_URL}">
<div class="sky" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
<a class="skip" href="#contenu">Aller au contenu</a>
<header class="top"><div class="wrap bar glass">
  <a class="brand" href="/" aria-label="Nouveau Cap, accueil"><img src="/assets/img/icon-192.png" alt="" width="34" height="34"><span>Nouveau Cap</span></a>
  <nav class="nav" aria-label="Menu principal">
    <a href="/#fonctions" class="hide-sm">L’app</a>
    <a href="/#offres" class="hide-sm">Offres</a>
    <a href="/blog/" class="hide-sm">Blog</a>
    <a href="/guides/" class="hide-sm">Guides</a>
    <a href="/#liste" class="cta">Être prévenu</a>
  </nav>
</div></header>
<main id="contenu">
{body}
</main>
<footer><div class="wrap">
  <p class="disclaimer">Nouveau Cap est un outil d’aide à la décision et d’organisation. Il ne remplace ni un conseil juridique ou financier, ni un accompagnement professionnel, et ne délivre pas de diplôme.</p>
  <div class="row">
    <p>© {YEAR} <a href="{AGENCY}/">Pixapop</a></p>
    <nav aria-label="Liens légaux">
      <a href="/blog/">Blog</a>
      <a href="/guides/">Guides</a>
      <a href="https://www.youtube.com/channel/UCwgrPyMgV04sl71rjCPfBGQ">YouTube</a>
      <a href="/confidentialite/">Confidentialité du site</a>
      <a href="/mentions-legales/">Mentions légales</a>
      <a href="{APP_PRIVACY}">Confidentialité de l’app</a>
      <a href="{APP_TERMS}">Conditions de l’app</a>
    </nav>
  </div>
</div></footer>
<script src="/assets/site.js" defer></script>
</body>
</html>
"""
    target = OUT / path.strip("/") / "index.html" if path != "/404" else OUT / "404.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc, encoding="utf-8")
    return path


def shot(name, alt, cls=""):
    """A Play Store visual, light or dark to match the visitor's phone."""
    return (f'<picture class="shot {cls}"><source srcset="/assets/img/dark-{name}.webp" media="(prefers-color-scheme: dark)">'
            f'<img src="/assets/img/light-{name}.webp" alt="{esc(alt)}" width="540" height="960" loading="lazy" decoding="async"></picture>')


FEATURES = [
    ("Faire le point, gratuitement", ["Votre runway : combien de mois vous pouvez tenir pendant la transition, avec la fin des droits ARE",
                                      "Le comparateur de pistes de métier et un plan de départ pour vos 30 premiers jours",
                                      "Le score de votre CV sur 100 et vos points faibles",
                                      "L’essentiel de la VAE : durée, étapes, jury"]),
    ("Trouver et financer", ["Des idées de métier proposées par le Copilote à partir de votre parcours, à tester sur le terrain",
                             "Projet de transition professionnelle, CPF, démission, immersion : pour qui, étapes, délais, dossier",
                             "Le calendrier à rebours de votre dossier et la formation financée dans votre runway",
                             "Avec Premium : la présentation écrite de votre projet, rédigée avec l’IA"]),
    ("Avancer chaque semaine", ["Un plan d’action de 90 jours, en étapes concrètes", "Des fiches « Comment faire » avec méthode et scripts",
                                "Des tests de pistes sur le terrain, avec un verdict", "Le feu vert financier et le mode Focus : 20 minutes, une tâche"]),
    ("Votre CV et LinkedIn", ["Vos corrections prioritaires et l’analyse d’une annonce", "La réécriture par l’IA, sans jamais inventer de chiffre",
                              "Créer son CV : PDF et Word adaptés à chaque annonce", "Votre titre et votre résumé LinkedIn"]),
    ("Le Copilote IA", ["Vos questions à tout moment, par un assistant qui connaît votre parcours (Pilote et Premium)", "Des actions à ajouter à votre plan en un geste",
                        "Avec Premium : un bilan de progression toutes les deux semaines", "Avec Premium : le module VAE complet, diagnostic, dossier et entraînement au jury"]),
]


def faq():
    p = PRICES
    return [
        ("Qu’est-ce que Nouveau Cap ?",
         "Une application Android pour les cadres de 40 ans et plus qui veulent changer de métier. Elle chiffre combien de mois vous pouvez tenir pendant la transition, vous aide à trouver des idées de métier et à financer votre formation, compare vos pistes, les transforme en plan d’action de 90 jours avec des tests sur le terrain, et prépare votre CV et votre profil LinkedIn, avec un Copilote IA qui connaît votre parcours."),
        ("Nouveau Cap remplace-t-il l’Apec, un bilan de compétences ou un coach ?",
         "Non. Le conseil en évolution professionnelle de l’Apec est gratuit pour les cadres : utilisez-le. Un bilan de compétences ou un coach apportent un regard humain. Nouveau Cap fait le travail entre deux rendez-vous : chaque jour, à votre rythme, avec votre plan et vos chiffres."),
        ("Combien coûte Nouveau Cap ?",
         f"Une version gratuite, sans IA, permet de faire le point par vous-même : runway, comparateur de pistes, fiches de financement, score de votre CV, essentiel de la VAE. L’offre Pilote coûte {p['pilote']} par mois, l’offre Premium {p['premium']} par mois avec {p['trialDays']} jours d’essai gratuit, et Créer son CV {p['cvBuilder']} en achat unique (inclus dans Premium). Sans engagement, résiliable à tout moment dans Google Play."),
        ("Quand sort l’application, et sur quels téléphones ?",
         "Nouveau Cap sort d’abord sur Android, via Google Play. La date n’est pas encore fixée : laissez votre adresse sur cette page pour être prévenu le jour de la sortie. Une version iPhone n’est pas encore prévue ; si vous êtes sur iPhone, dites-le dans le formulaire, cela nous aide à décider."),
        ("Comment savoir combien de mois je peux tenir pendant une reconversion ?",
         "Nouveau Cap calcule votre runway à partir de votre épargne, de vos dépenses, de vos allocations chômage (ARE) jusqu’à la fin de vos droits, et d’un éventuel nouveau revenu. Vous voyez le nombre de mois, la date où l’épargne serait épuisée, et l’effet d’un revenu d’appoint. Les montants d’ARE sont ceux que vous saisissez : l’app ne calcule pas vos droits à la place de France Travail."),
        ("Comment financer ma reconversion avec Nouveau Cap ?",
         "L’application présente quatre dispositifs : le projet de transition professionnelle, le CPF, la démission pour reconversion et l’immersion en entreprise. Pour chacun : à qui il s’adresse, ce qu’il finance, les étapes, les délais et les pièces du dossier, avec les sources officielles. Avec Pilote, vous obtenez le calendrier à rebours de votre dossier et vous ajoutez la rémunération de la formation à votre runway ; avec Premium, l’IA rédige un premier jet de la présentation de votre projet. Ce sont des informations générales : l’application ne dépose aucun dossier et ne remplace pas un conseiller en évolution professionnelle."),
        ("Nouveau Cap propose-t-il des idées de reconversion ?",
         "Oui, avec les offres Pilote et Premium : le Copilote propose des métiers à partir de votre parcours, de vos compétences et de vos motivations, avec leurs raisons et une première façon de les tester. Il ne donne aucun chiffre de salaire : vous vérifiez chaque piste sur le terrain, et vous la comparez aux autres dans l’application."),
        ("L’IA invente-t-elle des informations dans mon CV ?",
         "L’IA de Nouveau Cap est conçue pour ne jamais inventer de chiffre ni d’expérience : elle reformule ce que vous lui donnez. Vous relisez et validez tout. Rien n’est envoyé à l’IA sans votre accord, et un bouton permet de signaler une réponse."),
        ("Mes données sont-elles protégées ?",
         "Votre profil, votre plan et vos CV restent sur votre téléphone. Le serveur est hébergé à Paris. Il n’y a ni publicité ni mesure d’audience dans l’application, et vous pouvez tout effacer depuis l’app."),
        ("Qui édite Nouveau Cap ?",
         f"Pixapop, agence de création d’applications mobiles (nom commercial de {PUB['name']}, entrepreneur individuel), en France. Contact : {EMAIL}."),
    ]


def waitlist_block():
    return f"""<section id="liste" class="band" aria-labelledby="w"><div class="wrap">
  <div class="waitlist glass">
    <p class="eyebrow">Liste d’attente</p>
    <h2 id="w">Soyez prévenu du lancement.</h2>
    <p class="lead">Nouveau Cap sort d’abord sur Android. Laissez votre adresse : vous recevrez un seul e-mail, le jour de la sortie. Vous êtes sur iPhone&nbsp;? Indiquez-le, cela nous aide à décider de la version iPhone.</p>
    <form class="wl-form" data-waitlist data-endpoint="{WAITLIST_URL}" data-app="nouveau-cap" data-source="/" novalidate>
      <div class="wl-row">
        <label class="wl-label" for="wl-email">Votre adresse e-mail</label>
        <input class="wl-input" id="wl-email" type="email" name="email" autocomplete="email" inputmode="email" placeholder="prenom.nom@exemple.fr" required maxlength="254">
      </div>
      <fieldset class="wl-row wl-phones">
        <legend class="wl-label">Votre téléphone <span class="wl-opt">(facultatif)</span></legend>
        <label><input type="radio" name="platform" value="android"> Android</label>
        <label><input type="radio" name="platform" value="iphone"> iPhone</label>
        <label><input type="radio" name="platform" value="autre"> Autre</label>
      </fieldset>
      <div class="wl-hp" aria-hidden="true"><label>Ne pas remplir ce champ <input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
      <label class="wl-check"><input type="checkbox" name="consent" required> <span data-consent>{esc(CONSENT)}</span></label>
      <button class="btn btn-primary" type="submit">Prévenez-moi au lancement {ARROW}</button>
      <p class="wl-status" role="status" aria-live="polite"></p>
    </form>
    <p class="note">Pas de publicité, pas de revente, désinscription en un clic. <a href="/confidentialite/">Comment nous utilisons votre adresse</a>.</p>
  </div>
</div></section>"""


def home():
    p = PRICES
    feats = "".join(
        f'<article class="card glass"><h3>{esc(t)}</h3><ul>{"".join(f"<li>{esc(x)}</li>" for x in items)}</ul></article>'
        for t, items in FEATURES)
    gallery = "".join(shot(n, a) for n, a in [
        ("01_home", "Écran d’accueil : le mot du Copilote et le point de la semaine"),
        ("02_financer", "Financer ma reconversion : le calendrier à rebours d’un projet de transition professionnelle"),
        ("03_idees", "Idées de pistes : des métiers proposés à partir du parcours, ici l’exemple de Sophie"),
        ("06_cv", "Mon CV : le score et les critères"),
        ("07_creer", "Créer son CV : un CV adapté à chaque annonce"),
        ("08_vae", "Module VAE : diagnostic, dossier et entraînement au jury"),
    ])
    questions = faq()
    faq_html = "".join(f'<details class="qa glass"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in questions)
    body = f"""
<section class="hero"><div class="wrap hero-grid">
  <div class="hero-copy">
    <p class="pill"><b>Bientôt</b> sur Google Play, Android</p>
    <h1>Reconversion après 40 ans : <span class="hl">votre plan, votre CV</span> et un Copilote IA à vos côtés.</h1>
    <p class="lead">Nouveau Cap aide les cadres de 40 ans et plus à passer de l’envie de changer de métier à un projet chiffré et testé, sans se mettre en danger financièrement.</p>
    <div class="btns">
      <a class="btn btn-primary" href="#liste">Être prévenu du lancement {ARROW}</a>
      <a class="btn btn-ghost" href="#fonctions">Voir ce que fait l’app</a>
    </div>
  </div>
  <div class="hero-shot">{shot('04_finances', 'Écran Finances : votre runway en mois, avec la fin des droits ARE', 'lift')}</div>
</div></section>

<section class="band" aria-labelledby="m"><div class="wrap">
  <div class="head"><p class="eyebrow">Pourquoi Nouveau Cap</p><h2 id="m">Beaucoup de cadres y pensent. Peu se lancent.</h2>
  <p class="lead">Le frein n’est pas l’envie, c’est le passage à l’acte : l’argent, le doute, le temps. Nouveau Cap s’attaque aux trois.</p></div>
  <div class="trio">
    <article class="card glass"><span class="num">1</span><h3>Combien de mois pouvez-vous tenir&nbsp;?</h3><p>Épargne, dépenses, allocations jusqu’à la fin des droits ARE, nouveau revenu : votre runway en clair, et le feu vert financier avant de sauter.</p></article>
    <article class="card glass"><span class="num">2</span><h3>Testez avant de sauter</h3><p>Comparez vos pistes de métier, testez-les sur le terrain avec un verdict, et avancez avec un plan de 90 jours en étapes concrètes.</p></article>
    <article class="card glass"><span class="num">3</span><h3>Un CV qui parle au métier visé</h3><p>Score, analyse d’annonce, réécriture par l’IA sans rien inventer, CV en PDF et Word, titre et résumé LinkedIn.</p></article>
  </div>
</div></section>

<section id="fonctions" class="band" aria-labelledby="f"><div class="wrap">
  <div class="head"><p class="eyebrow">L’app</p><h2 id="f">Tout pour changer de cap, pas à pas.</h2></div>
  <div class="features">{feats}</div>
  <div class="gallery" role="list" aria-label="Captures d’écran de l’app">{gallery}</div>
  <p class="note">Captures réalisées avec un profil exemple (Sophie, 44 ans, ex-responsable marketing).</p>
</div></section>

<section class="band" aria-labelledby="a"><div class="wrap narrow">
  <div class="apec glass">
    <p class="eyebrow">Avec l’Apec, pas à sa place</p>
    <h2 id="a">Le conseil de l’Apec est gratuit : utilisez-le.</h2>
    <p>Le conseil en évolution professionnelle de l’Apec est gratuit pour les cadres, et un bilan de compétences ou un coach apportent un regard humain. Nouveau Cap fait le travail entre deux rendez-vous : chaque jour, à votre rythme, avec votre plan et vos chiffres.</p>
    <p><a href="https://www.apec.fr/candidat/faire-le-point--changer-de-voie/se-reconvertir/conseil-en-evolution-professionnelle.html" rel="noopener">Le conseil en évolution professionnelle de l’Apec</a></p>
  </div>
</div></section>

<section id="offres" class="band" aria-labelledby="o"><div class="wrap">
  <div class="head"><p class="eyebrow">Offres</p><h2 id="o">Simple, sans engagement.</h2><p class="lead">Résiliable à tout moment dans Google Play.</p></div>
  <div class="plans">
    <article class="card glass"><h3>Gratuit</h3><p class="price">0 €</p><p>Faire le point par vous-même, sans IA : runway, comparateur de pistes, plan de départ, exemples de ce que fait le Copilote.</p></article>
    <article class="card glass"><h3>Pilote</h3><p class="price">{esc(p['pilote'])} <small>/ mois</small></p><p>La méthode guidée pour avancer chaque semaine : plan de 90 jours, fiches, tests de pistes, Mon CV, le Copilote IA (10 messages par jour).</p></article>
    <article class="card glass best"><h3>Premium <span class="tag">recommandé</span></h3><p class="price">{esc(p['premium'])} <small>/ mois</small></p><p>Le suivi rapproché : bilan toutes les deux semaines, Copilote et fonctions IA sans limite, Créer son CV inclus. {p['trialDays']} jours d’essai gratuit pour un premier abonnement.</p></article>
    <article class="card glass"><h3>Créer son CV</h3><p class="price">{esc(p['cvBuilder'])}</p><p>Achat unique, sans abonnement : votre CV rédigé par l’IA à partir de vos réponses, adapté à chaque annonce.</p></article>
  </div>
  <p class="note">Prix toutes taxes comprises. Le prix qui s’applique est celui affiché par Google Play au moment de l’achat.</p>
</div></section>

<section class="band" aria-labelledby="d"><div class="wrap narrow">
  <div class="head"><p class="eyebrow">Vos données</p><h2 id="d">Votre projet vous appartient.</h2></div>
  <p class="lead">Votre profil, votre plan et vos CV restent sur votre téléphone. Le serveur est hébergé à Paris. Rien n’est envoyé à l’IA sans votre accord, pas de publicité, pas de mesure d’audience dans l’app, et vous pouvez tout effacer depuis l’app.</p>
  <p><a href="{APP_PRIVACY}">Politique de confidentialité de l’app</a></p>
</div></section>

{waitlist_block()}

{blog_teaser()}

{guides_teaser()}

<section id="questions" class="band" aria-labelledby="q"><div class="wrap narrow">
  <div class="head"><p class="eyebrow">Questions fréquentes</p><h2 id="q">Ce qu’on nous demande.</h2></div>
  <div class="faq">{faq_html}</div>
</div></section>
"""
    org = {"@context": "https://schema.org", "@type": "Organization", "@id": AGENCY + "/#organization", "name": "Pixapop",
           "url": AGENCY + "/", "email": EMAIL, "logo": SITE + "/assets/img/icon-192.png",
           "legalName": f"{PUB['name']}, entrepreneur individuel"}
    app = {"@context": "https://schema.org", "@type": "MobileApplication", "name": "Nouveau Cap",
           "alternateName": "Nouveau Cap : reconversion après 40 ans",
           "description": "Application de reconversion professionnelle pour les cadres de 40 ans et plus : runway financier, plan de 90 jours, tests de pistes, CV et LinkedIn, Copilote IA, VAE.",
           "operatingSystem": "Android", "applicationCategory": "BusinessApplication", "inLanguage": "fr", "url": SITE + "/",
           "image": SITE + "/assets/img/icon-192.png",
           "publisher": {"@id": AGENCY + "/#organization"},
           "offers": [{"@type": "Offer", "name": n, "price": v, "priceCurrency": "EUR"} for n, v in [
               ("Gratuit", "0"), ("Pilote", p["pilote"].replace(" €", "").replace(",", ".")),
               ("Premium", p["premium"].replace(" €", "").replace(",", ".")),
               ("Créer son CV", p["cvBuilder"].replace(" €", "").replace(",", "."))]]}
    fq = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in questions]}
    return page("/", "Nouveau Cap : l’app de reconversion professionnelle après 40 ans",
                "Nouveau Cap aide les cadres de 40 ans et plus à changer de métier : combien de mois vous pouvez tenir, plan de 90 jours, tests de pistes, CV et LinkedIn, Copilote IA. Bientôt sur Android.",
                body, jsonld=[org, app, fq])


ARTICLES = blog.read_articles()
GUIDES = guides.read_guides()
_ARTICLE_SLUGS = {a["slug"] for a in ARTICLES}
_ORDER = {a["slug"]: n for n, a in enumerate(ARTICLES)}
# Guides offered on the site: those whose PDF exists and whose article is published, in the blog's order.
PUBLISHED = sorted((g for g in GUIDES if (ROOT / "guides" / "pdf" / f"{g['slug']}.pdf").exists() and g.get("article") in _ARTICLE_SLUGS),
                   key=lambda g: _ORDER[g["article"]])
GUIDE_FOR = {g["article"]: g for g in PUBLISHED}


def gtext(text):
    """Guide header text, with French apostrophes and non-breaking spaces, escaped for HTML."""
    return esc(blog.nbsp(text.replace("'", "’")), quote=False)


def guide_pages(g):
    return g["body"].count('<section class="page"')


def guide_contents(g):
    return '<ul class="checks">' + "".join(f"<li>{gtext(c.strip())}</li>" for c in g["contents"].split(" | ")) + "</ul>"


def guide_form(g, source):
    uid = "g-" + g["slug"]
    return f"""<form class="wl-form" data-guide-form data-endpoint="{GUIDE_URL}" data-guide="{esc(g['slug'])}" data-source="{esc(source)}" novalidate>
      <div class="wl-row">
        <label class="wl-label" for="{uid}">Votre adresse e-mail</label>
        <input class="wl-input" id="{uid}" type="email" name="email" autocomplete="email" inputmode="email" placeholder="prenom.nom@exemple.fr" required maxlength="254">
      </div>
      <div class="wl-hp" aria-hidden="true"><label>Ne pas remplir ce champ <input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
      <label class="wl-check"><input type="checkbox" name="news"> <span data-consent>{esc(GUIDE_NEWS)}</span></label>
      <button class="btn btn-primary" type="submit">Recevoir le guide {ARROW}</button>
      <p class="wl-status" role="status" aria-live="polite"></p>
    </form>
    <p class="note">Votre adresse sert à vous envoyer ce guide. Sans la case cochée, nous ne vous écrirons rien d’autre et l’effacerons dans 30 jours. <a href="/confidentialite/#guides">Confidentialité</a></p>"""


def guide_tip(g):
    """Short box under the article header, pointing to the full guide block."""
    return f"""<aside class="guide-tip glass" aria-label="Guide gratuit">
    <p><strong>{blog.nbsp("Guide gratuit à télécharger :")}</strong> {gtext(g["title"])} ({guide_pages(g)} pages à imprimer)</p>
    <a class="btn btn-ghost" href="#guide">Recevoir le guide {ARROW}</a>
  </aside>"""


def guide_block(g, source):
    return f"""<section id="guide" class="guide glass" aria-labelledby="guide-t">
    <p class="eyebrow">Guide gratuit</p>
    <h2 id="guide-t">{gtext(g["title"])}</h2>
    <p>{gtext(g["pitch"])}</p>
    {guide_contents(g)}
    <p class="meta">PDF de {guide_pages(g)} pages, à imprimer et à remplir au stylo</p>
    {guide_form(g, source)}
  </section>"""


def guide_card(g, heading="h3"):
    return (f'<article class="card glass guide-card"><{heading}>{gtext(g["title"])}</{heading}><p>{gtext(g["pitch"])}</p>'
            f'{guide_contents(g)}<a class="btn btn-ghost" href="/blog/{g["article"]}/#guide">Recevoir ce guide {ARROW}</a></article>')


def guides_teaser():
    if not PUBLISHED:
        return ""
    cards = "".join(guide_card(g) for g in PUBLISHED[:4])
    return f"""<section class="band" aria-labelledby="gg"><div class="wrap">
  <div class="head"><p class="eyebrow">Guides gratuits</p><h2 id="gg">Des guides PDF à remplir, offerts.</h2>
  <p class="lead">{blog.nbsp("Check-lists, tableaux et modèles à imprimer : chaque guide accompagne un article du blog et vous est envoyé par e-mail.")}</p></div>
  <div class="posts">{cards}</div>
  <p style="margin-top:20px"><a class="btn btn-ghost" href="/guides/">Tous les guides {ARROW}</a></p>
</div></section>"""


def guides_page():
    cards = "".join(guide_card(g, "h2") for g in PUBLISHED)
    body = f"""<div class="wrap">
  <div class="head" style="padding-top:clamp(30px,6vw,60px)"><nav class="crumbs" aria-label="Fil d’Ariane"><a href="/">Nouveau Cap</a></nav>
  <p class="eyebrow">Guides gratuits</p><h1>Guides gratuits pour préparer votre reconversion</h1>
  <p class="lead">{blog.nbsp("Chaque guide est un PDF de quelques pages à imprimer et à remplir au stylo : check-lists, tableaux, modèles. Il accompagne un article du blog et vous est envoyé par e-mail, gratuitement.")}</p></div>
  <div class="posts guides-list">{cards}</div>
</div>"""
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Nouveau Cap", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Guides gratuits", "item": SITE + "/guides/"}]}]
    return page("/guides/", "Guides gratuits pour préparer votre reconversion · Nouveau Cap",
                "Guides PDF gratuits à remplir pour préparer votre reconversion après 40 ans : CV, financement, VAE, bilan de compétences, démission, trésorerie.",
                body, jsonld=ld)


def article_card(a):
    return (f'<article class="card glass post"><h3><a href="/blog/{a["slug"]}/">{esc(a["title"])}</a></h3>'
            f'<p>{esc(a["description"])}</p><p class="meta">Mis à jour le {blog.french_date(a["updated"])} · {max(1, round(a["words"] / 220))} min de lecture</p></article>')


def blog_teaser():
    if not ARTICLES:
        return ""
    cards = "".join(article_card(a) for a in ARTICLES[:4])
    return f"""<section class="band" aria-labelledby="b"><div class="wrap">
  <div class="head"><p class="eyebrow">Le blog</p><h2 id="b">Les guides pour préparer votre reconversion.</h2>
  <p class="lead">Financement, CV, VAE, droits au chômage : des réponses précises, vérifiées sur les sources officielles.</p></div>
  <div class="posts">{cards}</div>
  <p style="margin-top:20px"><a class="btn btn-ghost" href="/blog/">Tous les articles {ARROW}</a></p>
</div></section>"""


def blog_pages():
    paths = []
    for n, a in enumerate(ARTICLES):
        body, toc, faq_items = blog.markdown(a["body"], blog.WIDGETS)
        others = [x for x in ARTICLES if x is not a]
        related = (others[n:] + others[:n])[:3]
        toc_html = "".join(f'<li><a href="#{k}">{esc(t)}</a></li>' for k, t in toc if not t.lower().startswith("sources"))
        url = f"{SITE}/blog/{a['slug']}/"
        minutes = max(1, round(a["words"] / 220))
        g = GUIDE_FOR.get(a["slug"])
        html_body = f"""<div class="wrap narrow article">
  <nav class="crumbs" aria-label="Fil d’Ariane"><a href="/">Nouveau Cap</a> › <a href="/blog/">Blog</a></nav>
  <header class="art-head">
    <h1>{esc(a["title"])}</h1>
    <p class="lead">{esc(a["description"])}</p>
    <p class="meta">Mis à jour le <time datetime="{a["updated"]}">{blog.french_date(a["updated"])}</time> · {minutes} min de lecture · Par l’équipe Nouveau Cap (Pixapop)</p>
  </header>
  {guide_tip(g) if g else ""}
  <details class="toc glass"><summary>Sommaire</summary><ol>{toc_html}</ol></details>
  <div class="prose">
{body}
  </div>
  {guide_block(g, f"/blog/{a['slug']}/") if g else ""}
  <aside class="cta glass" aria-label="Liste d’attente">
    <p class="eyebrow">Nouveau Cap</p>
    <h2>Préparez votre reconversion avec un plan.</h2>
    <p>Runway, pistes testées sur le terrain, plan de 90 jours, CV : l’app sort bientôt sur Android. Laissez votre adresse pour être prévenu le jour du lancement.</p>
    <p><a class="btn btn-primary" href="/#liste">Être prévenu du lancement {ARROW}</a></p>
  </aside>
  <p class="note">Article d’information générale, rédigé avec l’aide d’outils d’IA et vérifié sur les sources officielles citées. Il ne remplace pas un conseil personnalisé : pour votre situation, adressez-vous à France Travail, à Transitions Pro ou à l’Apec.</p>
  <section class="related" aria-labelledby="r"><h2 id="r">À lire aussi</h2><div class="posts">{"".join(article_card(x) for x in related)}</div></section>
</div>"""
        ld = [{"@context": "https://schema.org", "@type": "BlogPosting", "headline": a["title"], "description": a["description"],
               "datePublished": a.get("published", a["updated"]), "dateModified": a["updated"], "inLanguage": "fr",
               "mainEntityOfPage": url, "url": url, "image": SITE + "/assets/img/og-light.jpg",
               "author": {"@type": "Organization", "name": "Nouveau Cap (Pixapop)", "url": SITE + "/"},
               "publisher": {"@id": AGENCY + "/#organization"}, "keywords": a.get("keyword", "")},
              {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "Nouveau Cap", "item": SITE + "/"},
                  {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog/"},
                  {"@type": "ListItem", "position": 3, "name": a["title"], "item": url}]}]
        if faq_items:
            ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in faq_items]})
        paths.append(page(f"/blog/{a['slug']}/", f"{a['title']} · Nouveau Cap", a["description"], html_body, jsonld=ld))
    cards = "".join(article_card(a) for a in ARTICLES)
    index = f"""<div class="wrap">
  <div class="head" style="padding-top:clamp(30px,6vw,60px)"><nav class="crumbs" aria-label="Fil d’Ariane"><a href="/">Nouveau Cap</a></nav>
  <p class="eyebrow">Le blog</p><h1>Réussir sa reconversion après 40 ans : les guides</h1>
  <p class="lead">Financer une formation, écrire un CV de reconversion, préparer une VAE, connaître ses droits au chômage, savoir combien de mois tenir : des réponses précises et sourcées.</p></div>
  <div class="posts">{cards}</div>
</div>"""
    paths.append(page("/blog/", "Blog Nouveau Cap : guides de reconversion après 40 ans",
                      "Guides pratiques et sourcés pour réussir sa reconversion professionnelle après 40 ans : financement, CV, VAE, chômage, bilan de compétences.", index))
    items = "".join(f"<item><title>{esc(a['title'])}</title><link>{SITE}/blog/{a['slug']}/</link><guid>{SITE}/blog/{a['slug']}/</guid>"
                    f"<description>{esc(a['description'])}</description><pubDate>{date.fromisoformat(a['updated']).strftime('%a, %d %b %Y')} 08:00:00 +0200</pubDate></item>" for a in ARTICLES)
    (OUT / "blog").mkdir(parents=True, exist_ok=True)
    (OUT / "blog" / "feed.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>Blog Nouveau Cap</title><link>{SITE}/blog/</link><description>Guides de reconversion après 40 ans</description><language>fr</language>{items}</channel></rss>\n', encoding="utf-8")
    return paths


def text_page(path, title, description, sections, *, noindex=False):
    blocks = "".join((f'<h2 id="{s[2]}">' if len(s) > 2 else "<h2>") + f"{esc(s[0])}</h2>" + "".join(f"<p>{l}</p>" for l in s[1])
                     for s in sections)
    body = f"""<div class="wrap narrow legal"><div class="paper glass">
  <p class="crumbs"><a href="/">Nouveau Cap</a></p>
  <h1>{esc(title)}</h1>
  {blocks}
</div></div>"""
    return page(path, f"{title} · Nouveau Cap", description, body, noindex=noindex)


def legal_pages():
    e = esc
    privacy = [
        ("En bref", [
            "Ce site ne dépose aucun cookie et n’enregistre rien sur votre appareil. Il compte les visites de façon anonyme, et il ne recueille votre adresse e-mail que si vous vous inscrivez sur la liste d’attente ou si vous demandez un guide gratuit.",
            f"Les données de l’application elle-même sont décrites dans sa <a href=\"{APP_PRIVACY}\">politique de confidentialité</a>."]),
        ("Responsable", [e(f"Pixapop, nom commercial de {PUB['name']}, entrepreneur individuel, {PUB['address']}. Contact : {EMAIL}.")]),
        ("Compteur de visites", [
            "Pour savoir quelles pages sont lues et d’où viennent les visiteurs, chaque page vue envoie à notre serveur la page visitée et, le cas échéant, le nom du site d’où vous venez (par exemple linkedin.com). Nous n’enregistrons ni votre adresse IP, ni votre navigateur, ni aucun identifiant : seuls des totaux par jour sont conservés.",
            "Aucun cookie ni autre traceur n’est utilisé, rien n’est lu ou écrit sur votre appareil, et ces chiffres ne sont ni croisés avec d’autres données ni partagés. Si votre navigateur demande à ne pas être suivi (réglages « Do Not Track » ou « Global Privacy Control »), rien n’est envoyé.",
            "Les totaux sont hébergés par Supabase, sur des serveurs situés à Paris, et effacés au bout de 25 mois."]),
        ("Liste d’attente", [
            "Finalité : vous prévenir par e-mail du lancement de l’application Nouveau Cap, et rien d’autre. Base : votre consentement, donné en cochant la case du formulaire.",
            "Données : votre adresse e-mail, le type de téléphone si vous l’indiquez, la page d’inscription, la date et le texte accepté. Pour limiter les abus, une empreinte non réversible de votre connexion est conservée 24 heures.",
            "Hébergement : Supabase, serveurs situés à Paris. Le jour du lancement, votre adresse est transmise à MailerLite (UAB MailerLite, Vilnius, Lituanie, Union européenne), qui envoie cet unique e-mail pour notre compte. Aucune revente, aucune publicité, aucun partage.",
            "Durée : l’adresse est effacée 30 jours après l’e-mail de lancement, chez nous comme chez MailerLite, et au plus tard 12 mois après l’inscription."]),
        ("Guides gratuits", [blog.nbsp(x) for x in [
            "Finalité : vous envoyer par e-mail le guide que vous demandez. Et, seulement si vous cochez la case prévue, vous envoyer 4 conseils pour avancer avec ce guide, puis les nouvelles de Nouveau Cap (l’application, les prochains guides), un e-mail par mois au plus.",
            "Base : votre demande pour l’envoi du guide ; votre consentement, donné en cochant la case, pour les nouvelles. La case n’est jamais cochée d’avance, et le guide vous est envoyé même si vous ne la cochez pas.",
            "Données : votre adresse e-mail, le guide demandé, la page d’où vous le demandez, la date et, si vous cochez la case, le texte accepté. Pour limiter les abus, une empreinte non réversible de votre connexion est conservée 24 heures.",
            "Hébergement : Supabase, serveurs situés à Paris. Le guide part d’une boîte e-mail hébergée par o2switch, en France. Si vous cochez la case, votre adresse, le titre du guide demandé et ses liens sont aussi transmis à MailerLite (UAB MailerLite, Vilnius, Lituanie, Union européenne), qui envoie les nouvelles pour notre compte. Aucune revente, aucune publicité, aucun partage.",
            "Durée : sans la case cochée, l’adresse est effacée 30 jours après votre demande et n’est jamais transmise à MailerLite. Avec la case cochée, elle est conservée 24 mois après votre dernière demande, ou jusqu’à votre désinscription. Après une désinscription, MailerLite garde seulement la mention « désinscrit », pour ne plus jamais vous écrire.",
            "Désinscription : si vous avez coché la case, chaque e-mail contient un lien pour vous désinscrire en un clic. Vous ne recevez alors plus rien, et votre adresse est effacée dans les 30 jours."]], "guides"),
        ("Hébergement du site", ["Le site est hébergé par GitHub Pages (GitHub, Inc., États-Unis), qui peut conserver temporairement l’adresse IP des visiteurs pour la sécurité du service."]),
        ("Vos droits", [e(f"Chaque e-mail contient un lien de désinscription immédiate. Vous pouvez aussi écrire à {EMAIL} pour accéder à vos données, les corriger ou les effacer, et saisir la CNIL (cnil.fr).")]),
    ]
    text_page("/confidentialite/", "Confidentialité du site", "Confidentialité du site de Nouveau Cap : compteur de visites sans cookie, liste d’attente, guides gratuits envoyés par e-mail, hébergement, vos droits.", privacy)
    notice = [
        ("Éditeur", [e(f"Pixapop, nom commercial de {PUB['name']}, {PUB['legalForm']}."), e(f"Adresse : {PUB['address']}."),
                     e(f"SIRET : {PUB['siret']}."), e(f"Directeur de la publication : {PUB['director']}."), e(f"Contact : {EMAIL}.")]),
        ("Hébergement", ["GitHub, Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis (service GitHub Pages). Compteur de visites, liste d’attente et guides gratuits : Supabase, serveurs situés à Paris. Envoi des guides par e-mail : boîte e-mail hébergée par o2switch, en France. Envoi des nouvelles et de l’e-mail de lancement : MailerLite (UAB MailerLite, Vilnius, Lituanie)."]),
        ("Application", [f"Les mentions légales, conditions et politique de confidentialité de l’application Nouveau Cap sont sur <a href=\"{APP_NOTICE}\">pixapop.fr</a>."]),
        ("Propriété intellectuelle", ["Les textes, images et logos de ce site appartiennent à Pixapop, sauf mention contraire. Toute reproduction sans autorisation est interdite.",
                                     "Polices Sora et Manrope, sous licence SIL Open Font License 1.1."]),
    ]
    text_page("/mentions-legales/", "Mentions légales", "Mentions légales du site de Nouveau Cap : éditeur, hébergement.", notice)
    return ["/confidentialite/", "/mentions-legales/"]


def unsubscribe():
    body = f"""<div class="wrap narrow legal"><div class="paper glass center">
  <p class="eyebrow" data-unsub-kind>Liste d’attente</p>
  <h1>Se désinscrire</h1>
  <p class="lead" data-unsub-lead>Vous ne recevrez plus d’e-mail au sujet du lancement, et votre adresse sera effacée de notre liste.</p>
  <p><button class="btn btn-primary" type="button" data-unsubscribe data-endpoint="{WAITLIST_URL}" data-endpoint-guide="{GUIDE_URL}">Confirmer la désinscription</button></p>
  <p class="wl-status" role="status" aria-live="polite"></p>
</div></div>"""
    page("/desinscription/", "Se désinscrire · Nouveau Cap", "Se désinscrire de la liste d’attente de Nouveau Cap.", body, noindex=True)


def app_link():
    """/app/: the one link to the app used in e-mails and posts. Before launch it points to the waitlist;
    on launch day, set PLAY_URL and it redirects to Google Play (no e-mail to edit)."""
    if PLAY_URL:
        body = f"""<meta http-equiv="refresh" content="0; url={esc(PLAY_URL)}"><div class="wrap narrow legal"><div class="paper glass center">
  <h1>Nouveau Cap sur Google Play</h1>
  <p><a class="btn btn-primary" href="{esc(PLAY_URL)}">Ouvrir Google Play {ARROW}</a></p>
</div></div>"""
    else:
        body = f"""<div class="wrap narrow legal"><div class="paper glass center">
  <p class="eyebrow">Bientôt sur Google Play</p><h1>Nouveau Cap arrive sur Android</h1>
  <p class="lead">{blog.nbsp("L’application n’est pas encore publiée. Laissez votre adresse sur la page d’accueil : vous serez prévenu le jour de sa sortie.")}</p>
  <p><a class="btn btn-primary" href="/#liste">Être prévenu {ARROW}</a></p>
</div></div>"""
    page("/app/", "Nouveau Cap sur Google Play", "Installer l’application Nouveau Cap sur Android.", body, noindex=True)


def not_found():
    body = f"""<div class="wrap narrow legal"><div class="paper glass center">
  <p class="eyebrow">Erreur 404</p><h1>Cette page n’existe pas.</h1>
  <p class="lead">Elle a peut-être changé d’adresse.</p>
  <p><a class="btn btn-primary" href="/">Revenir à l’accueil {ARROW}</a></p>
</div></div>"""
    page("/404", "Page introuvable · Nouveau Cap", "Cette page n’existe pas.", body, noindex=True)


def publish_guides():
    """Copies the PDF guides to /telechargement/ (not indexed) with a catalogue read by the Supabase function
    `guide`, which e-mails them. Only guides whose PDF exists are published."""
    out = OUT / "telechargement"
    out.mkdir()
    catalogue = []
    by_slug = {a["slug"]: a for a in ARTICLES}
    for g in (g for g in GUIDES if g in PUBLISHED):  # catalogue in file order
        pdf = ROOT / "guides" / "pdf" / f"{g['slug']}.pdf"
        art = by_slug[g["article"]]
        shutil.copy(pdf, out / pdf.name)
        catalogue.append({"slug": g["slug"], "title": g["title"], "pdf": f"/telechargement/{pdf.name}",
                          "article": f"/blog/{art['slug']}/", "article_title": art["title"],
                          "first_step": g.get("first_step", ""), "short": g.get("short", "")})
    (out / "index.json").write_text(json.dumps(catalogue, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    publish_guides()
    (OUT / "CNAME").write_text("nouveaucap.pixapop.fr\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    paths = [home(), guides_page(), *legal_pages(), *blog_pages()]
    unsubscribe()
    app_link()
    not_found()
    today = date.today().isoformat()
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{today}</lastmod></url>\n" for p in paths)
        + "</urlset>\n", encoding="utf-8")
    # Search engines and AI search assistants are welcome: being found is the point of this site.
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /desinscription/\nDisallow: /telechargement/\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print(f"{len(paths) + 2} pages written to docs/")


if __name__ == "__main__":
    main()
