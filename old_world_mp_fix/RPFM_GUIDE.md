# Hvordan lage .pack-fil med RPFM (Steg-for-steg)

## Hva du trenger:
- RPFM (Rusted Pack File Manager): https://github.com/Frodo45127/rpfm/releases
- Filene fra `old_world_mp_fix/script/` mappen

---

## Steg 1: Installer RPFM

1. Last ned nyeste versjon fra: https://github.com/Frodo45127/rpfm/releases
2. Pakk ut og kjør `rpfm_ui.exe` (Windows) eller `rpfm_ui` (Linux)

---

## Steg 2: Opprett ny PackFile

1. Åpne RPFM
2. Klikk **"PackFile" → "New PackFile"**
3. Velg **"Mod"** som type
4. Velg **"Warhammer 3"** som game

---

## Steg 3: Legg til script-filene

1. **Høyreklikk** på rot-noden i venstre panel
2. Velg **"Add" → "Add File"** eller **"Add from Folder"**
3. Naviger til `old_world_mp_fix/script/` mappen
4. Velg **hele strukturen**:
   ```
   script/
   └── campaign/
       └── cr_oldworld/
           └── endgame/
               ├── endgame_wild_hunt.lua
               ├── endgame_grudge_too_far.lua
               ├── endgame_vampires_rise.lua
               └── endgame_vermintide.lua
   ```

**VIKTIG:** Strukturen MÅ være nøyaktig slik! RPFM vil ofte spørre hvor du vil plassere filene - velg:
```
script/campaign/cr_oldworld/endgame/
```

---

## Steg 4: Lagre PackFile

1. Klikk **"PackFile" → "Save PackFile As..."**
2. Gi den et navn: `old_world_mp_fix.pack`
3. Lagre den i:
   ```
   Windows: C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER III\data\
   Linux: ~/.local/share/Steam/steamapps/common/Total War WARHAMMER III/data/
   ```

---

## Steg 5: Aktiver modden i launcher

1. Start **Total War Warhammer III Launcher**
2. Gå til **Mod Manager**
3. Du skal nå se **"old_world_mp_fix"** i listen
4. ✅ Aktiver den
5. **VIKTIG:** Dra den **UNDER** "The Old World Campaign" i load order!
   ```
   ✅ The Old World Campaign        ← Laster først
   ✅ old_world_mp_fix               ← Laster sist (overstyrer)
   ```

---

## Steg 6: Test

1. Start en ny kampanje
2. Spill til tur 30-40
3. Sjekk om desync er borte!

---

## Feilsøking RPFM

### Problem: "Invalid file structure"
**Løsning:** Sjekk at filstien i RPFM er:
```
script/campaign/cr_oldworld/endgame/endgame_wild_hunt.lua
```
IKKE:
```
old_world_mp_fix/script/campaign/cr_oldworld/endgame/endgame_wild_hunt.lua
```

### Problem: Modden vises ikke i launcher
**Løsning:**
- Sjekk at .pack-filen ligger i `data/`-mappen
- Sjekk at filnavnet IKKE har mellomrom eller æøå
- Restart launcher

### Problem: Fortsatt desync
**Løsning:**
- Sjekk load order (MP fix MÅ være under Old World)
- Sjekk at BEGGE spillere har modden installert
- Start NY kampanje (gamle saves har divergens)

---

## Avansert: Legg til mod-metadata (valgfritt)

Hvis du vil at modden skal ha ordentlig navn/beskrivelse i launcher:

1. I RPFM, høyreklikk rot → **"Add" → "Add from Template"**
2. Velg **"Pack Metadata"**
3. Fyll ut:
   - **Name:** Old World MP-Fix
   - **Description:** Fixes multiplayer desync in The Old World Campaign
   - **Author:** [Ditt navn]
4. Lagre

---

## Tips

✅ **Test modden alene først:** Aktiver kun Old World + MP-fix (ingen andre mods)
✅ **Steam Workshop (valgfritt):** Du kan laste opp .pack-filen til Workshop for enkel deling
✅ **Backup:** Ta backup av .pack-filen før du gjør endringer

---

Lykke til! 🎮
