import json
import string
import numpy as np
import music21 as m21
import tensorflow as tf
#tf.compat.v1.disable_eager_execution()
from fractions import Fraction
from random import choice,randint
from copy import deepcopy

def sample(preds, temperature=1.0):
    '''
    @param preds: a np.array with the probabilities to all categories
    @param temperature: the temperature. Below 1.0 the network makes more "safe"
                        predictions
    @return: the index after the sampling
    '''
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
   
    return np.argmax(probas)  


def create_encoder_ev(TransEncoders,timesig,numOfBars,val_templates,dense_templates,valence,density):
    
    #create the encoder part. First define idxs   
    enc_sos_idx = int(np.where(TransEncoders[0].categories_[0] == 'sos')[0])+1 #all shifted
    enc_eos_idx = int(np.where(TransEncoders[0].categories_[0] == 'eos')[0])+1
    enc_bar_idx = int(np.where(TransEncoders[0].categories_[0] == 'bar')[0])+1
    enc_timesig_idx = int(np.where(TransEncoders[0].categories_[0] == timesig)[0])+1
    
    
    #select a random valence and density template 
    #select a template from >= numOfbars with the suggested average from the user
    stop_condition = False
    while not stop_condition:
        try:
            #set a random length to get a template
            lgt_r = str(randint(numOfBars,40))
            #check if the valence avg exists as an option
            enc_val = deepcopy(choice(list(val_templates[lgt_r][valence]))) 
            enc_val = enc_val[:numOfBars]

        except:
            continue
        stop_condition = True
    #do the same for density
    stop_condition = False
    while not stop_condition:
        try:
            #set a random length to get a template
            lgt_r = str(randint(numOfBars,40))
            #check if the valence avg exists as an option
            enc_den = deepcopy(choice(list(dense_templates[lgt_r][density]))) 
            enc_den = enc_den[:numOfBars]

        except:
            continue
        stop_condition = True                
        
    enc_list = [enc_sos_idx,enc_bar_idx]
    for i in range(0,numOfBars):
        #check for Grouing
        if i == 0:
           curr_group_idx = int(np.where(TransEncoders[0].categories_[0] == 'start1')[0])+1
        elif i == 1:
           curr_group_idx = int(np.where(TransEncoders[0].categories_[0] == 'start2')[0])+1
        elif i == numOfBars-2:
           curr_group_idx = int(np.where(TransEncoders[0].categories_[0] == 'end1')[0])+1
        elif i == numOfBars-1:
           curr_group_idx = int(np.where(TransEncoders[0].categories_[0] == 'end2')[0])+1
        else:
           curr_group_idx = int(np.where(TransEncoders[0].categories_[0] == '-')[0])+1
        #get the Valence Idx for this current bar
        aVal = str(enc_val[i])
        curr_val_idx = int(np.where(TransEncoders[0].categories_[0] == aVal)[0])+1
        #get the Density Idx for this current bar
        aDen = str(enc_den[i])
        curr_den_idx = int(np.where(TransEncoders[0].categories_[0] == aDen)[0])+1
        #apply with that order TimeSig,Grouping,Valence and bar
        enc_list.extend([enc_timesig_idx,curr_group_idx,curr_val_idx,curr_den_idx,enc_bar_idx ])

        
    enc_list.append(enc_eos_idx)
    
    return enc_list
        
def convert_to_ChordDurMels(dec_out,TransEncoders):
    
    dec_bar_idx = int(np.where(TransEncoders[1].categories_[0] == 'bar')[0])
    
    bar_idxs = [i for i, x in enumerate(dec_out) if x == dec_bar_idx]
    
    allChords = ['bar']
    allDurs = ['bar']
    allMels = ['bar']
    
    for i in range(0,len(bar_idxs)-1):
        #get the range
        leftR = bar_idxs[i]+1
        rigtR = bar_idxs[i+1]
        
        #first for chords  
        for c in range(leftR,rigtR,3):
            aChord_idx = dec_out[c]
            aChord = str(TransEncoders[1].categories_[0][aChord_idx])
            allChords.append(aChord)
            
        for m in range(leftR+1,rigtR,3):
            aMel_idx = dec_out[m]
            aMel = str(TransEncoders[1].categories_[0][aMel_idx])
            allMels.append(aMel)
            
        #then for durs
        for d in range(leftR+2,rigtR,3):
            aDur_idx = dec_out[d]
            aDur= str(TransEncoders[1].categories_[0][aDur_idx])
            allDurs.append(aDur)  
            
        #add bar events
        allChords.append('bar')
        allDurs.append('bar')
        allMels.append('bar')
        
    return allChords,allDurs,allMels
                     


def create_static_conditions(allChords, allDurs, allMels):
    #set grouping flags
    bar_idxs = [i for i, x in enumerate(allDurs) if x == "bar"]
        
    #get bar indications
    bar_info = len(allDurs)*['no_bar']
    bar_info[0] = 'bar'
    for i in bar_idxs[:-1]:
        bar_info[i+1] = 'bar'
    
    #remove the bar idxs
    bar_idxs_d = {i for i, x in enumerate(allDurs) if x == "bar"}
    f_chords = [v for i, v in enumerate(allChords) if i not in bar_idxs_d]
    f_durs = [v for i, v in enumerate(allDurs) if i not in bar_idxs_d]
    f_melody = [v for i, v in enumerate(allMels) if i not in bar_idxs_d]
    f_bars = [v for i, v in enumerate(bar_info) if i not in bar_idxs_d]
    
    
    return f_chords, f_durs, f_melody, f_bars



def string_durs_to_float(bar_durs):
    #auxilliary function to 
    
    #create new list
    float_durs = []
    for b in bar_durs:
        if '/' in b:
            nom = int(b.split('/')[0])
            den = int(b.split('/')[-1])
            fr = Fraction(nom,den)
            float_durs.append(fr)
        else:
            float_durs.append(float(b))
    
    return float_durs
    

def chords_mel_mid(f_chords,f_durs,f_bars,allMelody,timesig,prefix):
    
    #path for generations
    midi_out = './midi/'
    xml_out = './musicxml/'
    
    #create the m21 instance for MIDI
    rc = m21.stream.Stream()
    #set tonality and tempo (default 120 tempo or set it to tempo21)
    kf = m21.key.Key('C', 'major')
    tempo21 = m21.tempo.MetronomeMark(number=100)
    rc.append(kf)
    rc.append(tempo21)
    #create m21 instance for XML
    rx = m21.stream.Stream()
    rx.append(m21.text.TextBox(prefix+' generation'))
    #calculate all bars according to f_bars
    all_bars = [index for index, value in enumerate(f_bars) if value == 'bar']
    #add the last idx which is the len of the events
    all_bars.append(len(f_bars))
    melody = m21.stream.Part()
    fl = m21.instrument.Flute()
    melody.insert(0, fl)
    chords = m21.stream.Part()
    pp = m21.instrument.Piano()
    chords.insert(0, pp)
    melodyxml = m21.stream.Part()
    melodyxml.insert(0, fl)
    #get TimeSig nominator denominator
    timesig = json.loads(timesig)
    ts = m21.meter.TimeSignature(str(timesig[0])+'/'+str(timesig[1]))

    for m in range(0,len(all_bars)-1):
        #create measure
        cho_m = m21.stream.Measure()
        mel_m = m21.stream.Measure()
        melxml_m = m21.stream.Measure()
        if m == 0:
            clef_s = m21.clef.TrebleClef()
            clef_b = m21.clef.BassClef()
            cho_m.insert(0, clef_b)
            cho_m.insert(0, ts)
            mel_m.insert(0, clef_s)
            mel_m.insert(0, ts)
            melxml_m.insert(0, clef_s)
            melxml_m.insert(0, ts)
            
        #for lead sheet only melody track will be given with chord symbols
        bar_prev = all_bars[m]
        bar_new = all_bars[m+1]
        #get the sum of durations
        bar_durs = f_durs[bar_prev:bar_new]
        bar_durs = string_durs_to_float(bar_durs)
        #get the chord list for this bar
        bar_chords = f_chords[bar_prev:bar_new]
        bar_melody = allMelody[bar_prev:bar_new]
        offset = 0.0
        prevChord = ''
        for b in range(0,len(bar_chords)):
            cho = bar_chords[b]
            dur = bar_durs[b]
            mel = bar_melody[b]
            if cho == 'Rest':
               aChord_t = m21.note.Rest() 
               aChord_name = 'Rest'
            else:
               aChord_s = m21.harmony.ChordSymbol(cho)
               pitchNames = [p for p in aChord_s.pitches]
               aChord_t = m21.chord.Chord(pitchNames)
               aChord_name = aChord_t.pitchedCommonName
            if prevChord == aChord_name:
                apC = cho_m.pop(-1)
                apC.quarterLength += float(dur)
                cho_m.append(apC)
            else: 
                aChord_t.offset = offset
                aChord_t.quarterLength = float(dur)
                cho_m.append(aChord_t)
                #append Chord Symbol if it is not rest
                if aChord_name != 'Rest':
                    aChord_s.offset = offset
                    aChord_s.writeAsChord = False
                    melxml_m.append(aChord_s) # add the chord symbol to mel track
                prevChord = aChord_name
            if mel == 'Rest' or mel =='eos': #check if to create a Note or Rest and set offset
                aNote = m21.note.Rest()
            else: #set pitch also
                pitch = m21.pitch.Pitch()
                pitch.midi = int(mel)
                aNote = m21.note.Note()
                aNote.pitch = pitch               
            #set onset and duration and append it
            aNote.offset = offset
            aNote.quarterLength = float(dur)
            mel_m.append(aNote) 
            melxml_m.append(aNote)
            offset = dur
        ############################  
        #append the measures to the parts
        chords.append(cho_m)
        melody.append(mel_m)
        melodyxml.append(melxml_m)
    #append the parts to the MIDI and XML streams
    #create end bar lines
    #chords[-1].append(m21.bar.Barline(type='final'))
    #melody[-1].append(m21.bar.Barline(type='final'))
    # MIDI
    rc.append(melody)
    rc.append(chords)
    # XML
    rx.append(melodyxml)
    rx.append(chords)
    #get random string seed
    rstr = randomString(5)
    #first MIDI
    mf = m21.midi.translate.streamToMidiFile(rc)
    #midiOut = midi_out+str(len(all_bars)-1)+'_'+str(timesig)+'_'+prefix+'_'+rstr+'.mid'
    midiOut = midi_out+'music.mid'
    mf.open(midiOut, 'wb')
    mf.write()
    mf.close()   
    print(midiOut, ' has been generated!')
    #then musicXML
    mx = m21.musicxml.m21ToXml.GeneralObjectExporter(rx)
    #xmlOut = xml_out+str(len(all_bars)-1)+'_'+str(timesig)+'_'+prefix+'_'+rstr+'.xml'
    xmlOut = xml_out+'sheet.xml'
    mxText = mx.parse().decode('utf-8')
    f = open(xmlOut, 'w')
    f.write(mxText.strip())
    f.close()   
    print(xmlOut, ' has been generated!')
    
    
def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(choice(letters) for i in range(stringLength))