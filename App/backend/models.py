import tensorflow as tf
tf.compat.v1.disable_eager_execution()
from aux_files import Encoder, Decoder

def chords_inf_model_ev(model_tr, LSTM_dim):
    
    '''Inference Model for event_based Enc-Dec'''
    # Encoder
    enc_inputs = model_tr.get_layer('input_var1').input

    encoder_shared_emb = model_tr.get_layer('encoder_embedding')    
    enc_emb = encoder_shared_emb(enc_inputs)
    
    
    encoder_1 = model_tr.get_layer('encoder_blstm_1')
    encoder1_outputs, forward1_h, forward1_c, backward1_h, backward1_c = encoder_1(enc_emb)
    state1_h = tf.keras.layers.Concatenate()([forward1_h, backward1_h])
    state1_c = tf.keras.layers.Concatenate()([forward1_c, backward1_c])
    encoder1_states = [state1_h, state1_c] 

    encoder_2 = model_tr.get_layer('encoder_blstm_2')
    encoder2_outputs, forward2_h, forward2_c, backward2_h, backward2_c = encoder2_outputs)
    state2_h = tf.keras.layers.Concatenate()([forward2_h, backward2_h])
    state2_c = tf.keras.layers.Concatenate()([forward2_c, backward2_c])
    encoder2_states = [state2_h, state2_c]    
    
    encoder_3 = model_tr.get_layer('encoder_blstm_3')
    encoder3_outputs, forward3_h, forward3_c, backward3_h, backward3_c = encoder_3(encoder2_outputs)
    state3_h = tf.keras.layers.Concatenate()([forward3_h, backward3_h])
    state3_c = tf.keras.layers.Concatenate()([forward3_c, backward3_c])
    encoder3_states = [state3_h, state3_c] 
    
    encoder_model = tf.keras.models.Model([enc_inputs], 
                                 encoder1_states+encoder2_states+encoder3_states)
    
    # Decoder
    dec_inputs = model_tr.get_layer('input_var2').input

    
    decoder_shared_emb = model_tr.get_layer('decoder_embedding')
    dec_emb = decoder_shared_emb(dec_inputs)
    
       
    decoder1 = model_tr.get_layer('decoder_lstm_1')
    decoder1_state_input_h = tf.keras.layers.Input(shape=(LSTM_dim*2,))
    decoder1_state_input_c = tf.keras.layers.Input(shape=(LSTM_dim*2,))
    decoder1_states_inputs = [decoder1_state_input_h, decoder1_state_input_c]  
    decoder1_outputs, decoder1_h, decoder1_c = decoder1(dec_emb, initial_state=decoder1_states_inputs)
    decoder1_states = [decoder1_h, decoder1_c]
    
  
    decoder2 = model_tr.get_layer('decoder_lstm_2')
    decoder2_state_input_h = tf.keras.layers.Input(shape=(LSTM_dim*2,))
    decoder2_state_input_c = tf.keras.layers.Input(shape=(LSTM_dim*2,))
    decoder2_states_inputs = [decoder2_state_input_h, decoder2_state_input_c]  
    decoder2_outputs, decoder2_h, decoder2_c = decoder2(decoder1_outputs, initial_state=decoder2_states_inputs)
    decoder2_states = [decoder2_h, decoder2_c]    
    
    decoder3 = model_tr.get_layer('decoder_lstm_3')
    decoder3_state_input_h = tf.keras.layers.Input(shape=(LSTM_dim*2,))
    decoder3_state_input_c = tf.keras.layers.Input(shape=(LSTM_dim*2,))
    decoder3_states_inputs = [decoder3_state_input_h, decoder3_state_input_c]  
    decoder3_outputs, decoder3_h, decoder3_c = decoder3(decoder2_outputs, initial_state=decoder3_states_inputs)
    decoder3_states = [decoder3_h, decoder3_c]  
    
    decoder_dense_melody = model_tr.get_layer('out_var1')
    decoder_outputs_melody = decoder_dense_melody(decoder3_outputs)
    
    decoder_model = tf.keras.models.Model([dec_inputs]+decoder1_states_inputs+decoder2_states_inputs+decoder3_states_inputs,
                                [decoder_outputs_melody]+decoder1_states+decoder2_states+decoder3_states)
    
    return encoder_model, decoder_model



def chord_trans_ev_model(enc_vocab,dec_vocab):
    #create the architecture first
    
    num_layers = 4  #4
    d_model = 48 #for Embedding 
    dff = 1536 #for Dense
    num_heads = 8 #8
    dropout_rate = 0.1

    enc_input = tf.keras.layers.Input(shape=(None,), name = 'input_var1')
    dec_input = tf.keras.layers.Input(shape=(None,), name = 'input_var2')
    
    encoder = Encoder(enc_vocab+1, num_layers = num_layers, d_model = d_model, num_heads = num_heads, dff = dff, dropout = dropout_rate)
    decoder = Decoder(dec_vocab+1, num_layers = num_layers, d_model = d_model*4, num_heads = num_heads, dff = dff, dropout = dropout_rate)
    
    x = encoder(enc_input)
    x = decoder([dec_input, x] , mask = encoder.compute_mask(enc_input))
    
    dec_output = tf.keras.layers.Dense(dec_vocab, activation='softmax', name = 'out_var1')
    out = dec_output(x)
    
    model = tf.keras.models.Model(inputs=[enc_input, dec_input], outputs=out)
    
    #load the weights
    model.load_weights('./aux_files/ChordDurMel_Trans_w.h5')
    
    return model