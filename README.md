# Sith Synth

It's an application that allows users to configure certain parameters from an input panel 
which are used as inputs into to a selected model (LSTM or Transformer). These models then run 
inference on the values to produce a MIDI file and an XML file which can be visualized and played.

For backend server
```commandline
conda create -n kyloren python=3.9
conda activate kyloren
pip install -r requirements_solved.txt
```

To run backend server:
```commandline
python run.py
```

To run the frontend server in dev mode:
```commandline
npm run dev
```

---

Roadmap:
* Delete to-delete directory
* Fix UI bug for displaying sheet music
* Create a method to allow multiple generations at the same time
* Implement asyncio code in server
* 