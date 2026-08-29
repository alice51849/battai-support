# BattAI Support Site

Support and privacy pages for the iOS app **BattAI: Battery Health**, served by GitHub Pages.

- Support / FAQ: https://alice51849.github.io/battai-support/
- Privacy policy: https://alice51849.github.io/battai-support/privacy.html

The privacy URL is linked from the in-app paywall (`BattAI/StoreKitLayer/PaywallView.swift`) and is
submitted to App Store Connect as the app's privacy policy URL. It must stay reachable.

## Structure

| File | Purpose |
|---|---|
| `index.html` | Support page: what the app does, FAQ, contact |
| `privacy.html` | Privacy policy |
| `style.css` | Ember Glass styling, light + dark, no external assets |
| `assets/` | App icon and favicon |
| `robots.txt`, `sitemap.xml` | Indexing |

Static only: no build step, no CDN, no third-party scripts, no analytics. Contact address for all
public-facing material is `hourstag.app@gmail.com`.

## Content rules

The privacy policy describes the app's real behaviour and must be kept in sync with the code:
zero network requests, no third-party SDKs, local-only storage, diagnostic files parsed in memory
with only battery fields retained, purchases through Apple StoreKit, no iCloud sync.

## Exact-50 support surfaces

The required `index`, `support`, and `privacy` routes are generated or
normalised from `source/support_surfaces.json`:

```bash
python3 tools/support_surfaces.py build
python3 tools/support_surfaces.py check
```

The source records the verified public catalogue and app/privacy authority
digests used for the copy. Do not hand-edit generated locale pages.
