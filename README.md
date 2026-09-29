# nouveaucap.pixapop.fr

Site de l'app Nouveau Cap (reconversion des cadres de 40 ans et plus), édité par Pixapop.
Hébergé gratuitement par GitHub Pages, à partir du dossier `docs/` de la branche `main`.

## Mettre à jour

1. Modifier les textes dans `build.py`, le style dans `assets/styles.css`, le script dans `assets/site.js`.
2. Prix et éditeur : `data/nouveau-cap-legal.json`, le même fichier que `pixapop-site/data/` (exporté par
   le dépôt `nouveau-cap` avec `node scripts/build-legal.mjs`). Quand les prix changent, le recopier ici aussi.
3. Lancer `python3 build.py` (Python 3, aucune dépendance) : le dossier `docs/` est réécrit.
4. Vérifier en local : `cd docs && python3 -m http.server 8777`, puis ouvrir http://localhost:8777
   (en local, le compteur de visites ne s'envoie pas).
5. Enregistrer et envoyer (`git add -A && git commit && git push`) : le site se met à jour en une minute.

Ne jamais modifier `docs/` à la main.

## Blog

- Articles : un fichier Markdown par article dans `content/blog/<slug>.md` (en-tête `title`, `description`,
  `slug`, `keyword`, `updated`, `order`, puis `---`). Sous-ensemble Markdown : `##`, `###`, paragraphes,
  listes `-` et `1.`, `**gras**`, `[liens](url)`, tableaux `|`. `[[CALCULATEUR]]` insère le calculateur de runway.
- `blog.py` convertit et produit : page de chaque article (sommaire, encadré liste d'attente, « À lire
  aussi », données structurées BlogPosting, fil d'Ariane et FAQ), `/blog/` et le flux `/blog/feed.xml`.
- Calcul du runway : fonction `nouveauCapRunway` dans `assets/site.js` (testée, cas limites et 20 000 cas
  aléatoires) ; rien n'est envoyé.
- Calendrier et stratégie : dépôt AIOS, `projects/nouveau-cap-marketing/` (`CALENDRIER-CONTENUS.md`,
  `SEO-CONTENU.md`).

## Ce que fait le site

- Page d'accueil : promesse, fonctions, captures (claires ou sombres selon le téléphone), lien avec l'Apec,
  offres, données, liste d'attente, questions fréquentes (avec données structurées pour Google et les IA).
- Liste d'attente : fonction `liste-attente` du projet Supabase « pixapop-marketing » (Paris).
  Désinscription : `/desinscription/?t=<jeton>` (au clic seulement).
- Compteur de visites sans cookie : fonction `visite` du même projet, totaux par jour (page, site d'origine),
  sans adresse IP ni identifiant ; rien n'est envoyé si le navigateur demande à ne pas être suivi.
- Pages : `/confidentialite/` (site), `/mentions-legales/`. Les textes légaux de l'application restent
  sur pixapop.fr (déclarés à Google Play, à ne jamais déplacer).
- Sources des fonctions serveur : dépôt AIOS, `projects/nouveau-cap-marketing/supabase/`.

## Choix

- Couleurs et polices de l'app (Sora, Manrope, licence SIL OFL 1.1, hébergées ici) ; thème clair ou sombre
  selon le réglage du téléphone.
- Aucun cookie, aucune ressource tierce chargée à l'affichage.
- Images : visuels de la fiche Google Play (`nouveau-cap/store/google-play/`), réduits en WebP 540 x 960.
