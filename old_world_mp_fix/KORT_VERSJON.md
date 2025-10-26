# Old World MP-Fix - Rask oppsummering

## Hva er dette?
En mod som fikser multiplayer desync i **The Old World Campaign** (både hovedmod og Classic-submod).

## Problemet
Endgame-scripts bruker `pairs()` som gir ulik rekkefølge på to maskiner → desync rundt tur 20-30.

## Løsningen
4 script-filer med sortert iterering i stedet for `pairs()` → garantert lik rekkefølge.

---

## Slik lager du modden (3 steg):

### 1️⃣ Last ned RPFM
https://github.com/Frodo45127/rpfm/releases

### 2️⃣ Lag .pack-fil
1. Åpne RPFM
2. New PackFile → Mod (Warhammer 3)
3. Add from Folder → velg `old_world_mp_fix/script/`
4. Save as `old_world_mp_fix.pack` i TWW3 `data/`-mappen

### 3️⃣ Aktiver i launcher
- ✅ The Old World Campaign (øverst)
- ✅ old_world_mp_fix (under)

**Les `RPFM_GUIDE.md` for detaljert guide!**

---

## Fungerer på:
✅ The Old World Campaign
✅ Old World Classic (submod)
✅ Med SFO og andre mods

## Endrer:
✅ Kun rekkefølge armeer spawner (alfabetisk)
❌ IKKE balanse, styrke, eller gameplay

---

## Multiplayer:
🎮 **BEGGE** spillere trenger modden
🎮 **Identisk** load order
🎮 Start **ny kampanje**

---

## Filer som er fikset:
```
script/campaign/cr_oldworld/endgame/
├── endgame_wild_hunt.lua
├── endgame_grudge_too_far.lua
├── endgame_vampires_rise.lua
└── endgame_vermintide.lua
```

✨ **Total:** 6 `pairs()` → sortert iterering
