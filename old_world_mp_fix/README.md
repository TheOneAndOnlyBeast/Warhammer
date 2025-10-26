# Old World Classic - Multiplayer Desync Fix

## Hva er dette?
Dette er en compatpatch-mod som fikser multiplayer desync-problemer i **"The Old World Campaign, Classic"** modden.

## Problemet
Old World-modden bruker `pairs()` til å iterere over fraksjoner i endgame-scripts. `pairs()` gir **ikke garantert samme rekkefølge** på to forskjellige maskiner, noe som fører til at:
- Endgame-armeer spawner i ulik rekkefølge
- Spilltilstanden divergerer mellom klienter
- Desync skjer typisk rundt tur 20-30 (når endgame kan trigge)

## Løsningen
Denne patchen erstatter endgame-scriptene med MP-safe versjoner som:
✅ Sorterer alle fraksjoner alfabetisk før iterering
✅ Garanterer identisk rekkefølge på begge maskiner
✅ Beholder all original funksjonalitet og balanse

## Installasjon

### Steg 1: Plassering
Kopier hele `old_world_mp_fix`-mappen til:
```
Windows: C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER III\data\
Linux: ~/.local/share/Steam/steamapps/common/Total War WARHAMMER III/data/
```

### Steg 2: Load Order
**KRITISK VIKTIG:** Denne modden MÅ laste **ETTER** Old World Campaign i mod manager!

I launcher:
1. Aktiver "The Old World Campaign, Classic"
2. Aktiver "Old World MP Fix"
3. Sørg for at "Old World MP Fix" er **UNDER** (laster senere enn) Old World i listen

### Steg 3: Multiplayer
**Begge spillere** må ha:
- Samme versjon av Old World Campaign
- Denne MP-fix modden installert
- Identisk load order
- Identiske MCT-innstillinger (hvis brukt)

## Hva endres?
**ENDRES:**
- Rekkefølge armeer spawner i endgames (alfabetisk i stedet for tilfeldig)
- Rekkefølge i mission objectives (sortert)

**ENDRES IKKE:**
- Balanse (samme antall og styrke på armeer)
- Hvilke fraksjoner som spawner
- Victory conditions
- Noen gameplay-mekanikker

## Filene som er fikset
```
script/campaign/cr_oldworld/endgame/endgame_wild_hunt.lua
script/campaign/cr_oldworld/endgame/endgame_grudge_too_far.lua
script/campaign/cr_oldworld/endgame/endgame_vampires_rise.lua
script/campaign/cr_oldworld/endgame/endgame_vermintide.lua
```

## Tekniske detaljer
Alle `pairs()` loops er erstattet med sortert iterering:
```lua
-- FØR (ikke MP-safe):
for faction_key, region_key in pairs(faction_table) do
    spawn_army(faction_key)
end

-- ETTER (MP-safe):
local sorted_keys = {}
for k in pairs(faction_table) do table.insert(sorted_keys, k) end
table.sort(sorted_keys)
for i = 1, #sorted_keys do
    local faction_key = sorted_keys[i]
    spawn_army(faction_key)
end
```

## Kompatibilitet
- ✅ Old World Campaign Classic
- ✅ SFO: Grimhammer III
- ✅ Andre mods (så lenge de ikke også overskriver endgame-scripts)

## Hvis Old World oppdateres
Hvis Old World-modden oppdateres:
1. Test først om desync er fikset i original mod
2. Hvis ikke, kan denne patchen sannsynligvis fortsatt brukes
3. Sjekk for nye endgame-filer som kanskje også trenger fikses

## Support
Laget for å løse desync-problemer rapportert av spillere.
Basert på analyse av Old World Campaign v[versjon] scripts.

## Kreditter
- Original mod: The Old World Campaign team
- MP-fix: Claude Code desync-analyse og patch

---
**Tips:** Start ny kampanje etter å ha aktivert denne modden. Gamle saves kan allerede ha divergens.
