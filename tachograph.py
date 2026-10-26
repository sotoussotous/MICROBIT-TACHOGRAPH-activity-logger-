
import tkinter as tk
from tkinter import ttk
import serial
import threading
import queue
import time
from datetime import datetime
import winsound
import os


# ==================================================
# SETTINGS
# ==================================================

PORT = "COM3"
BAUDRATE = 115200

SUBOR = r"D:\python\zápis služby.txt"
SUBOR_SOFERI = r"D:\python\šoféri.txt"

DOBA_AKTIVITY_SENZORA = 1.0

MODE_LABELS = {
    "JAZDA": "DRIVING",
    "PRESTÁVKA": "BREAK",
    "INÁ PRÁCA": "OTHER WORK",
}


# ==================================================
# MICRO:BIT CONNECTION
# ==================================================

ser = serial.Serial(
    PORT,
    BAUDRATE,
    timeout=1
)

fronta_microbit = queue.Queue()


# ==================================================
# PROGRAM STATE
# ==================================================

aktualny_rezim = "PRESTÁVKA"
zaciatok_rezimu = None

posun_stlaceny = False
posledny_sofer = ""
posledny_pohyb = 0.0

alarm_aktivovat = threading.Event()
alarm_ukoncit = threading.Event()


# ==================================================
# TIME FORMATTING
# ==================================================

def format_casu(sekundy):

    sekundy = int(sekundy)

    hodiny = sekundy // 3600
    minuty = (sekundy % 3600) // 60
    sekundy = sekundy % 60

    return f"{hodiny:02d}:{minuty:02d}:{sekundy:02d}"


# ==================================================
# LOAD DRIVERS
# ==================================================

def nacitaj_soferov():

    try:

        with open(
            SUBOR_SOFERI,
            "r",
            encoding="utf-8"
        ) as subor:

            return [
                riadok.strip()
                for riadok in subor
                if riadok.strip()
            ]

    except FileNotFoundError:

        return []


# ==================================================
# WRITE TO LOG FILE
# ==================================================

def zapis_do_txt(text):

    cas = datetime.now().strftime(
        "%d.%m.%Y %H:%M:%S"
    )

    with open(
        SUBOR,
        "a",
        encoding="utf-8"
    ) as subor:

        subor.write(
            f"{cas} - {text}\n"
        )


def zapis_rezim(rezim, trvanie, sofer):

    zapis_do_txt(
        f"{rezim} - "
        f"vodič: {sofer} - "
        f"trvanie {format_casu(trvanie)}"
    )


# ==================================================
# OPEN LOG
# ==================================================

def otvor_zapis():

    if not os.path.exists(SUBOR):

        with open(
            SUBOR,
            "a",
            encoding="utf-8"
        ):
            pass

    os.startfile(SUBOR)


# ==================================================
# REPEATING ALARM
# ==================================================

def alarm():

    while not alarm_ukoncit.is_set():

        if not alarm_aktivovat.wait(0.1):
            continue

        if (
            time.monotonic() - posledny_pohyb
            >= DOBA_AKTIVITY_SENZORA
        ):

            alarm_aktivovat.clear()
            continue

        try:

            winsound.Beep(523, 160)

            if (
                alarm_ukoncit.is_set()
                or not alarm_aktivovat.is_set()
            ):
                continue

            winsound.Beep(784, 160)

        except RuntimeError:

            alarm_aktivovat.clear()


# ==================================================
# BUTTON CONTROL
# ==================================================

def aktualizuj_ovladanie():

    driver_selected = bool(sofer_var.get())

    button_state = (
        "normal" if driver_selected else "disabled"
    )

    tlacidlo_jazda.config(
        state=button_state
    )

    tlacidlo_prestavka.config(
        state=button_state
    )

    tlacidlo_ina_praca.config(
        state=button_state
    )

    posun_tlacidlo.config(
        state=button_state
    )

    if (
        not driver_selected
        or aktualny_rezim == "PRESTÁVKA"
    ):

        sofer_combo.config(
            state="readonly"
        )

    else:

        sofer_combo.config(
            state="disabled"
        )


# ==================================================
# DRIVER SELECTION
# ==================================================

def vybrany_sofer(event=None):

    global posledny_sofer
    global zaciatok_rezimu

    novy_sofer = sofer_var.get()

    if not novy_sofer:
        return

    alarm_aktivovat.clear()

    # FIRST DRIVER

    if not posledny_sofer:

        posledny_sofer = novy_sofer

        zaciatok_rezimu = time.time()

        stav.set(
            "BREAK    00:00:00"
        )

        aktualizuj_ovladanie()

        return

    # SAME DRIVER

    if novy_sofer == posledny_sofer:

        aktualizuj_ovladanie()
        return

    # DRIVER CHANGE ONLY DURING BREAK

    if aktualny_rezim != "PRESTÁVKA":

        sofer_var.set(
            posledny_sofer
        )

        aktualizuj_ovladanie()

        return

    # SAVE PREVIOUS DRIVER'S BREAK

    teraz = time.time()

    if zaciatok_rezimu is not None:

        zapis_rezim(
            "PRESTÁVKA",
            teraz - zaciatok_rezimu,
            posledny_sofer
        )

    # SAVE DRIVER CHANGE

    zapis_do_txt(
        f"ZMENA VODIČA - "
        f"z {posledny_sofer} "
        f"na {novy_sofer}"
    )

    # START NEW DRIVER

    posledny_sofer = novy_sofer

    zaciatok_rezimu = teraz

    stav.set(
        "BREAK    00:00:00"
    )

    aktualizuj_ovladanie()


# ==================================================
# CHANGE MODE
# ==================================================

def zmen_rezim(novy_rezim):

    global aktualny_rezim
    global zaciatok_rezimu

    sofer = sofer_var.get()

    if not sofer:
        return

    if novy_rezim == aktualny_rezim:
        return

    teraz = time.time()

    # SAVE OLD MODE

    if zaciatok_rezimu is not None:

        zapis_rezim(
            aktualny_rezim,
            teraz - zaciatok_rezimu,
            sofer
        )

    # START NEW MODE

    aktualny_rezim = novy_rezim

    zaciatok_rezimu = teraz

    aktualizuj_ovladanie()


# ==================================================
# MODES
# ==================================================

def jazda():

    zmen_rezim(
        "JAZDA"
    )


def prestavka():

    zmen_rezim(
        "PRESTÁVKA"
    )


def ina_praca():

    zmen_rezim(
        "INÁ PRÁCA"
    )


# ==================================================
# YARD MOVE
# ==================================================

def posun_stlac():

    global posun_stlaceny

    posun_stlaceny = True

    posun_label.set(
        "YARD MOVE: PRESSED"
    )


def posun_pust():

    global posun_stlaceny

    posun_stlaceny = False

    posun_label.set(
        "YARD MOVE: RELEASED"
    )


# ==================================================
# MICRO:BIT MOTION SENSOR
# ==================================================

def spracuj_pohyb_microbitu(signal):

    global posledny_pohyb

    posledny_pohyb = time.monotonic()

    # SENSOR INDICATOR

    senzor_stav.set(
        "MOTION SENSOR: ACTIVATED"
    )

    senzor_posledny.set(
        "LAST SENSOR EVENT: "
        + datetime.now().strftime("%H:%M:%S")
    )

    # NO DRIVER = REPEATING ALARM

    if not sofer_var.get():

        alarm_aktivovat.set()
        return

    # DRIVER SELECTED = NO ALARM

    alarm_aktivovat.clear()

    # MOTION ONLY UPDATES SENSOR STATUS
    # SHAKE ACTIVATES DRIVING

    if signal != "SHAKE":
        return

    # YARD MOVE BLOCKS SHAKE

    if posun_stlaceny:
        return

    jazda()


# ==================================================
# READ MICRO:BIT
# ==================================================

def citaj_microbit():

    while not alarm_ukoncit.is_set():

        try:

            riadok = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if riadok in ("SHAKE", "MOTION"):

                fronta_microbit.put(riadok)

        except Exception:

            break


# ==================================================
# PROCESS MICRO:BIT MESSAGES
# ==================================================

def spracuj_frontu():

    while not fronta_microbit.empty():

        signal = fronta_microbit.get_nowait()

        spracuj_pohyb_microbitu(signal)

    okno.after(
        50,
        spracuj_frontu
    )


# ==================================================
# UPDATE MOTION SENSOR INDICATOR
# ==================================================

def aktualizuj_senzor():

    rozdiel = (
        time.monotonic() -
        posledny_pohyb
    )

    if rozdiel >= DOBA_AKTIVITY_SENZORA:

        senzor_stav.set(
            "MOTION SENSOR: INACTIVE"
        )

        alarm_aktivovat.clear()

    okno.after(
        100,
        aktualizuj_senzor
    )


# ==================================================
# TIMER
# ==================================================

def aktualizuj_cas():

    if not sofer_var.get():

        stav.set(
            "SELECT A DRIVER"
        )

    elif zaciatok_rezimu is not None:

        trvanie = (
            time.time() -
            zaciatok_rezimu
        )

        stav.set(
            MODE_LABELS[aktualny_rezim]
            + "    "
            + format_casu(trvanie)
        )

    okno.after(
        1000,
        aktualizuj_cas
    )


# ==================================================
# CLOSE PROGRAM
# ==================================================

def pri_zatvoreni():

    sofer = sofer_var.get()

    if (
        sofer
        and zaciatok_rezimu is not None
    ):

        zapis_rezim(
            aktualny_rezim,
            time.time() - zaciatok_rezimu,
            sofer
        )

    alarm_ukoncit.set()
    alarm_aktivovat.set()

    ser.close()

    okno.destroy()


# ==================================================
# MAIN WINDOW
# ==================================================

okno = tk.Tk()

okno.title(
    "Tachograph Simulator"
)

okno.geometry(
    "700x800"
)

okno.protocol(
    "WM_DELETE_WINDOW",
    pri_zatvoreni
)


# ==================================================
# TITLE
# ==================================================

tk.Label(
    okno,
    text="TACHOGRAPH SIMULATOR",
    font=("Arial", 24)
).pack(
    pady=20
)


# ==================================================
# DRIVER
# ==================================================

tk.Label(
    okno,
    text="Driver:",
    font=("Arial", 16)
).pack(
    pady=5
)

sofer_var = tk.StringVar()

sofer_combo = ttk.Combobox(
    okno,
    textvariable=sofer_var,
    values=nacitaj_soferov(),
    state="readonly",
    font=("Arial", 15),
    width=30
)

sofer_combo.pack(
    pady=5
)

sofer_combo.bind(
    "<<ComboboxSelected>>",
    vybrany_sofer
)


# ==================================================
# MODE AND TIME
# ==================================================

stav = tk.StringVar(
    value="SELECT A DRIVER"
)

tk.Label(
    okno,
    textvariable=stav,
    font=("Arial", 30)
).pack(
    pady=30
)


# ==================================================
# DRIVING BUTTON
# ==================================================

tlacidlo_jazda = tk.Button(
    okno,
    text="DRIVING",
    font=("Arial", 16),
    width=20,
    height=2,
    command=jazda,
    state="disabled"
)

tlacidlo_jazda.pack(
    pady=5
)


# ==================================================
# BREAK BUTTON
# ==================================================

tlacidlo_prestavka = tk.Button(
    okno,
    text="BREAK",
    font=("Arial", 16),
    width=20,
    height=2,
    command=prestavka,
    state="disabled"
)

tlacidlo_prestavka.pack(
    pady=5
)


# ==================================================
# OTHER WORK BUTTON
# ==================================================

tlacidlo_ina_praca = tk.Button(
    okno,
    text="OTHER WORK",
    font=("Arial", 16),
    width=20,
    height=2,
    command=ina_praca,
    state="disabled"
)

tlacidlo_ina_praca.pack(
    pady=5
)


# ==================================================
# OPEN LOG BUTTON
# ==================================================

tlacidlo_zapis = tk.Button(
    okno,
    text="OPEN LOG",
    font=("Arial", 16),
    width=20,
    height=2,
    command=otvor_zapis
)

tlacidlo_zapis.pack(
    pady=10
)


# ==================================================
# YARD MOVE BUTTON
# ==================================================

posun_tlacidlo = tk.Button(
    okno,
    text="YARD MOVE",
    font=("Arial", 16),
    width=20,
    height=2,
    state="disabled"
)

posun_tlacidlo.bind(
    "<ButtonPress-1>",
    lambda event: posun_stlac()
)

posun_tlacidlo.bind(
    "<ButtonRelease-1>",
    lambda event: posun_pust()
)

posun_tlacidlo.pack(
    pady=15
)


# ==================================================
# YARD MOVE INDICATOR
# ==================================================

posun_label = tk.StringVar(
    value="YARD MOVE: RELEASED"
)

tk.Label(
    okno,
    textvariable=posun_label,
    font=("Arial", 14)
).pack()


# ==================================================
# MOTION SENSOR INDICATOR
# ==================================================

senzor_stav = tk.StringVar(
    value="MOTION SENSOR: INACTIVE"
)

senzor_posledny = tk.StringVar(
    value="LAST SENSOR EVENT: NONE"
)

tk.Label(
    okno,
    textvariable=senzor_stav,
    font=("Arial", 15, "bold")
).pack(
    pady=(10, 2)
)

tk.Label(
    okno,
    textvariable=senzor_posledny,
    font=("Arial", 12)
).pack(
    pady=2
)


# ==================================================
# ALARM THREAD
# ==================================================

alarm_vlakno = threading.Thread(
    target=alarm,
    daemon=True
)

alarm_vlakno.start()


# ==================================================
# MICRO:BIT THREAD
# ==================================================

vlakno = threading.Thread(
    target=citaj_microbit,
    daemon=True
)

vlakno.start()


# ==================================================
# TIMERS
# ==================================================

okno.after(
    1000,
    aktualizuj_cas
)

okno.after(
    100,
    aktualizuj_senzor
)

okno.after(
    50,
    spracuj_frontu
)


# ==================================================
# START PROGRAM
# ==================================================

aktualizuj_ovladanie()

okno.mainloop()
