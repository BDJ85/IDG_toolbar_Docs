# Documentatiesite IDG Toolbar — beheer

Statische site voor Cloudflare Pages. Geen build-stap, geen framework: `index.html`
leest `register.json` en tekent de tegels. Toegang wordt buiten de site geregeld,
met Cloudflare Access (zie §4).

## 1. Structuur

```
site/
├── index.html          landingspagina (huisstijl-CSS byte-identiek aan de template,
│                       eigen <style>-blok voor de tegels, eigen renderer-script)
├── register.json       enige bron van waarheid — hier bewerk je alles
├── check_register.py   controle vóór je pusht
├── docs/               de documenten zelf (HTML, PDF, zip), bestandsnaam = code
├── 404.html            eerlijke foutpagina; zonder dit bestand serveert Pages stil index.html
├── _headers            noindex + basisbeveiligingsheaders (Pages leest dit bestand)
└── robots.txt          zoekmachines geweigerd
```

## 2. Werkwijze bij een nieuw of gewijzigd document

1. Zet het bestand in `docs/` met de code als naam: `docs/IDG-UITL-XXXX.html`.
2. Voeg in `register.json` een object toe (of verhoog `versie` en `bijgewerkt`).
   `publiek: false` houdt eigen naslagwerk van de site zonder tweede register.
   `status: "vervangen"` + `vervangen_door` houdt een document uit beeld maar in de
   geschiedenis.
3. `python check_register.py --strict` — moet eindigen op "in orde".
4. Commit en push. Pages publiceert binnen een minuut.

Wat er op de site verschijnt: alleen documenten met `publiek: true` én
`status: "actief"`. Een publiek document zonder `bestand` wordt een grijze tegel
zonder link — handig als aankondiging, maar het controlescript waarschuwt ervoor.

## 3. Deploy op Cloudflare Pages

Repository koppelen of de map `site/` direct uploaden; build command leeg,
output directory `/` (of `site` als de map in een grotere repo zit). Pages
respecteert `_headers` automatisch.

## 4. Inloggen: Cloudflare Access

Access zit vóór de hele site (dus ook vóór `docs/` en de PDF's) en staat los van
de code: er hoeft niets in `index.html` voor te veranderen. Het gratis
Zero Trust-plan dekt tot 50 gebruikers; daarboven wordt het per gebruiker per
maand betaald. Een gebruiker telt als "seat" zodra hij één keer inlogt.

### 4.1 Inrichten (menunamen uit het geheugen — controleer ze in het dashboard)

1. Cloudflare dashboard → **Zero Trust** → **Access** → **Applications** →
   *Add an application* → **Self-hosted**.
2. Application domain: het domein van de site, bv. `docs.jouwdomein.nl`.
   Voeg ook het `*.pages.dev`-adres toe, anders blijft de site daar open.
3. Identity provider: kies één van de drie hieronder (§4.2).
4. Policy: *Allow*, met als **Include**-regel wie erin mag (§4.3).
5. Session duration: 24 uur tot een week is voor documentatie prima.

### 4.2 Hoe collega's inloggen — drie opties, in volgorde van aanbeveling

| Optie | Wat de collega ziet | Wat jij inricht | Oordeel |
|---|---|---|---|
| **One-time PIN (e-mail)** | Vult zijn werkmail in, krijgt een zescijferige code, plakt die in | Niets extra — staat standaard aan | **Aanbevolen.** Nul beheer, werkt voor iedereen met een `@interduct.nl`-adres, geen wachtwoord om te vergeten |
| **Microsoft Entra ID** | Logt in met het Interduct-Microsoft-account dat hij al gebruikt | App-registratie in de Entra-tenant van Interduct — daar heb je IT voor nodig | Prettigst voor de gebruiker (SSO), maar je maakt de toegang afhankelijk van Interduct-IT terwijl de toolbar jouw IP is |
| **Autodesk-account** | Logt in met zijn Autodesk ID | Eigen app registreren op APS (developer.autodesk.com) en die als *Generic OIDC*-provider in Access hangen | **Afgeraden.** Technisch waarschijnlijk mogelijk — APS Authentication v2 ondersteunt OpenID Connect, uit mijn geheugen, controleer op aps.autodesk.com — maar Autodesk-accounts staan vaak op een privé- of ander mailadres, het toestemmingsscherm van Autodesk verwart, en je onderhoudt een app-registratie die niets toevoegt boven een mailcode |

De gedachte achter "Autodesk-account" — *iedereen op de tekenkamer heeft er een* —
geldt óók voor het werkmailadres, en dat vraagt niets van niemand.

### 4.3 Bevoegdheid vrijgeven

Twee manieren, combineerbaar in één policy:

- **Op domein** — Include: *Emails ending in* `@interduct.nl`. Iedereen bij Interduct
  kan erin; vertrekkende collega's verliezen hun mailadres en daarmee de toegang.
- **Op naam** — Include: *Emails* met een expliciete lijst. Strakker, meer beheer.
  Handig voor externen (een tekenbureau, een stagiair met eigen adres).

Wil je later per document differentiëren (bv. de cursus alleen voor een groep),
maak dan een tweede Access-application voor het pad `docs/IDG-CUR-*` met een eigen
policy. Voor nu is één policy voor de hele site genoeg.

## 5. Te verifiëren voordat je live gaat

- Versienummers en `bijgewerkt`-maanden in het register zijn gereconstrueerd uit de
  werksessies; loop ze langs bij je versiecontrole.
- Welke documenten publiek zijn is mijn inschatting: handboek, starthandleiding,
  bundel, Opstellingen 4.0, iExport-handleiding en de WPF-cursus staan open;
  technische referentie, bouwbrief, register en de vijf losse (vervangen)
  uitlegdocumenten staan dicht. Omzetten is één veld.
- `docs/` is nu leeg op het register-document na; het controlescript noemt precies
  welke bestanden er nog in moeten.
