# Old World MP-Fix - Installasjonsveiledning (Norsk)

## Hva er dette?
Dette er en **compatpatch** som fikser multiplayer desync i **The Old World Campaign, Classic** modden.

## Problemet vi løser
Old World-modden har en programmeringsfeil i endgame-scripts som gjør at rekkefølgen på hendelser blir ulik mellom to spillere i multiplayer. Dette fører til desync, typisk rundt tur 20-30.

## Løsningen
Denne patchen erstatter 4 endgame-script-filer med MP-safe versjoner som garanterer at begge maskiner kjører identisk.

---

## Installasjon

### Steg 1: Kopier filer til data-mappen

**Windows:**
```
Kopier hele "old_world_mp_fix"-mappen til:
C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER III\data\
```

**Linux:**
```bash
cp -r old_world_mp_fix ~/.local/share/Steam/steamapps/common/Total\ War\ WARHAMMER\ III/data/
```

### Steg 2: Last rekkefølge (KRITISK!)

Åpne **Total War Warhammer III Launcher**, gå til **Mod Manager**.

**VIKTIG:** Old World MP Fix MÅ laste **ETTER** Old World Campaign!

Slik gjør du:
1. Aktiver begge moddene:
   - ✅ The Old World Campaign, Classic
   - ✅ Old World MP Fix

2. Dra "Old World MP Fix" **UNDER** "The Old World Campaign, Classic" i listen
   - Old World Campaign skal være OVER (laster først)
   - Old World MP Fix skal være UNDER (laster sist, overstyrer)

3. Lagre og start spillet

---

## For Multiplayer (BEGGE spillere må gjøre dette!)

✅ **Samme versjon** av The Old World Campaign
✅ **Samme versjon** av denne fix-modden
✅ **Identisk load order** (MP Fix under Old World Campaign)
✅ **Identiske MCT-innstillinger** (hvis SFO eller andre mods bruker MCT)

### Tips:
- Start **ny kampanje** etter å ha aktivert patchen
- Gamle saves kan allerede ha desync-divergens

---

## Hva endres?

**ENDRES:**
- Rekkefølge armeer spawner i endgames → nå alfabetisk i stedet for tilfeldig
- Rekkefølge i mission objectives → nå sortert

**ENDRES IKKE:**
- Balanse (samme styrke og antall armeer)
- Hvilke fraksjoner som spawner
- Victory conditions
- Gameplay-mekanikker

---

## Teknisk informasjon

**Filer som er fikset:**
```
script/campaign/cr_oldworld/endgame/endgame_wild_hunt.lua
script/campaign/cr_oldworld/endgame/endgame_grudge_too_far.lua
script/campaign/cr_oldworld/endgame/endgame_vampires_rise.lua
script/campaign/cr_oldworld/endgame/endgame_vermintide.lua
```

**Hva vi fikset:**
Alle `pairs()` iterasjoner er erstattet med sortert iterering, slik at begge maskiner alltid får samme rekkefølge.

---

## Feilsøking

**Problem:** Fortsatt desync etter installasjon
**Løsning:**
1. Sjekk at load order er riktig (MP Fix under Old World)
2. Sjekk at begge spillere har identisk oppsett
3. Start **ny kampanje** (gamle saves kan ha divergens)

**Problem:** Spillet crasher ved oppstart
**Løsning:**
1. Sjekk at filene ligger i riktig mappe (`data/old_world_mp_fix/`)
2. Sjekk at du ikke har endret noe i de originale Old World-filene

**Problem:** Modden vises ikke i launcher
**Løsning:**
- Dette er en script-overstyring, ikke en "vanlig" mod
- Den vil ikke vises som separat mod i launcher
- Så lenge filene ligger i `data/old_world_mp_fix/` vil de laste

---

## Kompatibilitet

✅ The Old World Campaign Classic
✅ SFO: Grimhammer III
✅ Andre mods (så lenge de ikke også overskriver endgame-scripts)

---

## Støtte

Hvis dere fortsatt opplever desync etter installasjon:
1. Dobbelsjekk at begge spillere har identisk oppsett
2. Test med **kun** Old World + denne fix (ingen andre mods)
3. Rapport tilbake med hvilken tur desyncen skjer

---

## Kreditter

- **Original mod:** The Old World Campaign team
- **MP-fix:** Claude Code (desync-analyse og patch)
- **Laget for:** Warhammer 3 multiplayer spillere som opplever desync med Old World

God fornøyelse med stabilt multiplayer! 🎮
