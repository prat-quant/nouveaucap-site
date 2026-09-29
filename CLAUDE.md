# CLAUDE.md : site nouveaucap.pixapop.fr

Guide pour les sessions Claude qui travaillent sur ce dépôt. Toujours écrire à Cyril en français, simplement,
une étape à la fois, sans tiret cadratin.

## Avant toute modification (obligatoire, demandé par Cyril)

1. Récupérer `main` de ce dépôt et de `prat-quant/AIOS`.
2. Lire `docs/JOURNAL-MISES-A-JOUR.md` d'AIOS (entrées récentes, tâches « À répercuter », tableau des
   dépendances).
3. Après la modification : ajouter une entrée en haut de ce journal et l'envoyer sur `main` d'AIOS.

## Règles

- Voir `README.md` pour construire et tester. Ne jamais modifier `docs/` à la main.
- Honnêteté : aucun chiffre de résultat inventé, les captures montrent un profil exemple (le dire),
  l'app ne remplace ni un conseil ni un accompagnement professionnel. Rien n'est promis que l'app ne fait pas.
- Toute nouvelle collecte de données : mettre à jour `/confidentialite/` avant la mise en ligne.
- Tester avant d'envoyer : pages, 360, 412 et 1280 px, thèmes clair et sombre, formulaire (réponses
  simulées), aucune erreur JavaScript, pas de débordement horizontal.
- Le serveur (Supabase « pixapop-marketing ») n'accepte que l'origine `https://nouveaucap.pixapop.fr`
  (fonctions `liste-attente` et `visite`). Changer d'adresse demande de mettre à jour ces fonctions.
- DNS chez o2switch : une seule ligne pour ce site (CNAME `nouveaucap` vers `prat-quant.github.io`). Ne
  jamais toucher aux autres lignes de pixapop.fr.
