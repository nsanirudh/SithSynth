from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
import pickle
from App.backend.gen_utils import generate_leadsheet
from App.backend.utils import chords_mel_mid, create_static_conditions
import os

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/generate")
async def generate_music(
    temp: float = Query(..., title="Temperature"),
    timsig_n: int = Query(..., title="Time Signature Numerator"),
    timsig_d: int = Query(..., title="Time Signature Denominator"),
    num_bars: int = Query(..., title="Number of Bars"),
    val: str = Query(..., title="Valence"),
    den: str = Query(..., title="Density"),
    modl: str = Query(..., title="Model (transformer or lstm)")
):
    # Load global variables and dictionaries
    encoders_trans = './aux_files/chords_encoders_all.pickle'
    with open(encoders_trans, 'rb') as handle:
        TransEncoders = pickle.load(handle)

    val_temp_path = './aux_files/Valence_Templates.pickle'
    with open(val_temp_path, 'rb') as handle:
        val_templates = pickle.load(handle)

    dense_temp_path = './aux_files/Density_Templates.pickle'
    with open(dense_temp_path, 'rb') as handle:
        dense_templates = pickle.load(handle)

    # Set user music parameters
    temperature = temp
    timesig = f"[{timsig_n}, {timsig_d}]"
    numOfBars = num_bars
    valence = val
    density = den
    model = modl

    # Generate the lead sheet
    allChords, allDurs, allMels = generate_leadsheet(
        temperature,
        timesig,
        numOfBars,
        valence,
        density,
        model,
        TransEncoders,
        val_templates,
        dense_templates,
    )

    f_chords, f_durs, f_melody, f_bars = create_static_conditions(allChords, allDurs, allMels)
    chords_mel_mid(f_chords,f_durs,f_bars,f_melody,timesig,model)

    midi_file = './midi/music.mid'
    xml_file = './musicxml/sheet.xml'

    if not os.path.exists(midi_file) or not os.path.exists(xml_file):
        raise HTTPException(status_code=500, detail="Failed to generate music files")

    return {"midi_file": midi_file, "xml_file": xml_file}


@app.get("/midi")
async def get_midi():
    midi_file = './midi/music.mid'
    if not os.path.exists(midi_file):
        raise HTTPException(status_code=404, detail="MIDI file not found")
    return FileResponse(midi_file, media_type='audio/midi', filename="music.mid")

@app.get("/xml")
async def get_xml():
    xml_file = './musicxml/sheet.xml'
    if not os.path.exists(xml_file):
        raise HTTPException(status_code=404, detail="XML file not found")
    return FileResponse(xml_file, media_type='application/xml', filename="sheet.xml")