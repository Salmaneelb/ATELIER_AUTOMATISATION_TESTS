# API Choice

- **Étudiant :** Salmane El BOUBAKKARI
- **API choisie :** Frankfurter
- **URL base :** `https://api.frankfurter.app`
- **Documentation officielle :** https://frankfurter.dev
- **Auth :** None

## Endpoints testés
- `GET /latest` — Taux du jour (base EUR)
- `GET /latest?base=USD` — Taux avec base USD
- `GET /latest?symbols=USD,GBP` — Filtrage devises
- `GET /currencies` — Liste des devises supportées
- `GET /2020-01-02` — Taux historiques
- `GET /latest?base=INVALIDXXX` — Cas invalide (attendu 4xx)
- `GET /9999-99-99` — Date invalide (attendu 4xx)

## Hypothèses de contrat
| Endpoint | Champs attendus | Types | Code HTTP |
|---|---|---|---|
| `/latest` | `base`, `date`, `rates` | str, str, dict→float | 200 |
| `/currencies` | codes ISO 4217 | dict(str→str) | 200 |
| `/{date}` | `base`, `date`, `rates` | str, str, dict | 200 |
| `/latest?base=INVALID` | message d'erreur | — | 4xx |

## Limites / rate limiting
- Aucune limite officielle pour usage raisonnable
- Données mises à jour 1x/jour (source BCE)
- Données disponibles depuis le 4 janvier 1999

## Risques
- Indisponibilité les weekends (pas de cotation BCE)
- Données EOD (End of Day), pas temps réel
