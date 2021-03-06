import numpy as np 
import pandas as pd
import math
from sklearn import metrics
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from functools import partial
import keras.backend as K
from keras.models import model_from_json
from sklearn.preprocessing import StandardScaler,MinMaxScaler,normalize
import joblib
from sklearn import metrics
from sklearn.utils import resample
import time

def Boot_Loss(y_true,y_pred):
    return(K.sum(K.log(y_pred)+y_true/y_pred)/2)

def Params(Path,Scope,target='',MP=True,processes=3,L=1,memory=.3,Act='relu'):
    params = {}
    params['Spath'] = Path+target
    if MP == False:params['proc']=1
    else:params['proc']=processes
    if Scope == 'Full':
        K = 30
    elif Scope == 'Test':
        K = 3
    else :
        K = 1
    params['K'] = K
    params['epochs'] = 1000
    params['target'] = target
    # params['splits_per_mod'] = splits_per_mod
    params['Save'] = {}
    params['Save']['Weights']=True
    params['Save']['Model']=True
    params['Loss']='mean_squared_error'
    params['Memory']=memory
    params['iteration'] = 1
    params['Verbose'] = 0
    params['Eval'] = True
    params['validation_split'] = 0.1
    # params['validation_split'] = 0.3
    params['patience']=10
    params['HiddenLayers']=L
    params['N']=None
    params['Activation']=Act
    return(params)

def Dense_Model(params,inputs,lr=1e-4):
    import keras
    from keras.models import Sequential
    from keras.layers import Dense, Activation, Dropout
    from keras.wrappers.scikit_learn import KerasRegressor
    from keras.callbacks import EarlyStopping,ModelCheckpoint,LearningRateScheduler
    import tensorflow as tf
    from keras.constraints import nonneg
    # tf.random.set_seed(params['iteration'])
    # patience=10
    config = tf.compat.v1.ConfigProto()
    config.gpu_options.per_process_gpu_memory_fraction = params['Memory']
    session = tf.compat.v1.Session(config=config)
    model = Sequential()#'relu'
    NUM_GPU = 1 # or the number of GPUs available on your machine
    adam = keras.optimizers.Adam(lr = lr)
    gpu_list = []
    initializer = keras.initializers.glorot_uniform(seed=params['iteration'])
    # print(params['Save']['Weights'])
    for i in range(NUM_GPU): gpu_list.append('gpu(%d)' % i)
    if params['Loss'] == 'Boot_Loss':
        model.add(Dense(params['N'], input_dim=inputs,activation='relu',kernel_initializer=initializer,kernel_constraint=nonneg()))
        model.add(Dense(1,activation='elu',kernel_constraint=nonneg()))
        model.compile(loss=Boot_Loss, optimizer='adam')
    elif params['HiddenLayers']==1:
        model.add(Dense(params['N'], input_dim=inputs,activation=params['Activation'],kernel_initializer=initializer))
        # model.add(Dropout(0.1))
        # model.add(Dense(params['N'], input_dim=inputs,activation='sigmoid',kernel_initializer=initializer))#,kernel_constr
        model.add(Dense(1))
        # model.add(Dense(1,activation='elu',kernel_constraint=nonneg()))
        model.compile(loss=params['Loss'], optimizer='adam')
    else:
        model.add(Dense(params['N'], input_dim=inputs,activation=params['Activation'],kernel_initializer=initializer))
        model.add(Dropout(0.1))
        model.add(Dense(int(params['N']/2), activation=params['Activation']))
        model.add(Dense(1))
        model.compile(loss=params['Loss'], optimizer='adam')#,context=gpu_list) # - Add if using MXNET
    if params['Save']['Weights'] == True:
        # callbacks = [EarlyStopping(monitor='val_loss', patience=params['patience'],verbose=0),#params['Verbose']),
        #      ModelCheckpoint(filepath=params['Spath']+params['Sname']+str(params['iteration'])+'.h5', monitor='val_loss', save_best_only=True)]
        callbacks = [EarlyStopping(monitor='val_loss', patience=params['patience'],verbose=0),#params['Verbose']),
             ModelCheckpoint(filepath=params['Spath']+params['Sname']+str(params['iteration'])+'.h5', monitor='loss', save_best_only=True)]
    else:
        callbacks = [EarlyStopping(monitor='val_loss', patience=params['patience'])]
    return(model,callbacks)

def Train_DNN(params,X_train,y_train,X,y):#,X_fill):X_test,y_test,
    epochs = params['epochs']
    np.random.seed(params['iteration'])
    from keras import backend as K
    Mod,callbacks = Dense_Model(params,X_train.shape[1])
    # print(Mod)
    batch_size=int(y_train.shape[0]*.1)
    history = Mod.fit(X_train, # Features
            y_train, # Target vector
            epochs=epochs, # Number of epochs
            callbacks=callbacks, # Early stopping
            verbose=params['Verbose'], # Print description after each epoch
            batch_size=batch_size, # Number of observations per batch
            # validation_data=(X_test, y_test),# Data for evaluation
            validation_split=params['validation_split']
            ) 
    df = pd.DataFrame(data=history.history)
    df.to_csv(params['Spath']+params['Sname']+str(params['iteration'])+'.csv')
    Y_target = Mod.predict(X,batch_size = batch_size)
    if params['Save']['Model'] == True:
        model_json = Mod.to_json()
        with open(params['Spath']+params['Sname']+".json", "w") as json_file:
            json_file.write(model_json)
    return(Y_target)#,history)#,y_val,Rsq)

def Bootstrap(iteration,params,X,y,Stratify=None):
    params['iteration']=iteration
    np.random.seed(params['iteration'])
    ones = np.ones(y.shape[0],dtype=int)
    indicies = np.arange(0,y.shape[0],dtype=int)
    # if Stratify is not None:
    #     X_train,y_train = resample(X,y, n_samples=y.shape[0],stratify=Stratify)
    # else:
    X_train,y_train = resample(X,y,n_samples=y.shape[0])
    Test = np.array([i for i,x in zip(indicies,y) if x.tolist() not in y_train.tolist()]) 
    ones[Test] *= 0
    # Y_hat,history=
    Y_hat = Train_DNN(params,X_train,y_train,X,y)

    Cons,Derivs,Outputs = Derivatives(iteration,params,X,y)
    return(Y_hat,y,X,ones,Cons,Derivs,Outputs)#,history)

def Calculate_Var(params,Y_hat_train,Y_hat_val,y_true,X_true,count_train,count_val):
    Y_hat_train_bar=np.nanmean(Y_hat_train,axis=0)
    Y_hat_val_bar=np.nanmean(Y_hat_val,axis=0)

    Y_hat_train_var = 1/(np.nansum(count_train)-1)*np.nansum((Y_hat_train - Y_hat_train_bar)**2,axis=0)
    Y_hat_val_var = 1/(np.nansum(count_val)-1)*np.nansum((Y_hat_val - Y_hat_val_bar)**2,axis=0)
    r2_train = np.maximum((y_true[0,:]-Y_hat_train_bar)**2-Y_hat_train_var,0)
    r2_val = np.maximum((y_true[0,:]-Y_hat_val_bar)**2-Y_hat_val_var,0)
    params['Loss'] = 'Boot_Loss'
    params['Validate'] = False
    params['Sname'] = 'Var'
    params['Save']['Model'] = True
    y = r2_val
    Valid = np.where(np.isnan(y)==False)
    y = y[Valid]
    X = X_true[Valid]
    YStandard = MinMaxScaler(feature_range=(.1, 1))
    # YStandard = StandardScaler()
    # XStandard = StandardScaler()
    YScaled = YStandard.fit(y.reshape(-1, 1))
    XStandard = joblib.load(params['Spath']+'X_scaler.save') 
    XScaled = XStandard.fit(X)#.reshape(-1, 1))
    y = YScaled.transform(y.reshape(-1, 1))
    X = XScaled.transform(X)
    scaler_filename = "YVar_scaler.save"
    joblib.dump(YStandard, params['Spath']+scaler_filename) 
    scaler_filename = "XVar_scaler.save"
    joblib.dump(XStandard, params['Spath']+scaler_filename) 
    # print('Var!!')
    init=1
    params['iteration'] = 0
    Y_hat_var= Train_DNN(params,X,y,X,y) #,history 
    Y_hat_var = YScaled.inverse_transform(Y_hat_var.reshape(-1,1))
    y_true_var = YScaled.inverse_transform(y.reshape(-1,1))
    # print(Y_hat_var,Y_hat_var.shape)
    MSE = []
    if params['Eval'] == True:
        for i in range(params['K']):
            try:
                Test = pd.DataFrame(data={'target':Y_hat_val[i],'y':y_true[i]}).dropna()
                # print(Y_hat_val,y_true)
                MSE.append(metrics.mean_squared_error(Test['target'],Test['y']))
            except:
                print('No Go'+str(i))
                pass
    MSE = np.asanyarray(MSE)
    RMSE = MSE ** .5

    Test = pd.DataFrame(data={'target':Y_hat_val_bar,'y':y_true[i]}).dropna()

    mse = metrics.mean_squared_error(Test['y'],Test['target'])
    rmse = mse**.5
    r2 = metrics.r2_score(Test['y'],Test['target'])

    # SE = ((((MSE-mse)**2).sum()/(params['K']))**.5)/(params['K']**.5)
    SE = (MSE.std()/params['K']**.5)
    
    # SE = ((MSE-mse).std()/params['K']**.5)
    return(mse,rmse,SE,r2,y_true,Y_hat_val)

def Sort_outputs(k,params,Y_hat,y_true,X_true,ones):
    ones_train = ones+0.0
    ones_val = ones*-1+1.0
    count_train = ones_train
    count_val = ones_val
    ones_train[ones_train==0] = np.nan
    ones_val[ones_val==0] = np.nan
    Y_hat_train = Y_hat.copy()*ones_train
    Y_hat_val = Y_hat.copy()*ones_val
    y_true2 = y_true.copy()
    X_true2 = X_true.copy()
    return(Calculate_Var(params,Y_hat_train,Y_hat_val,y_true2,
               X_true2[0,:,],count_train,count_val))#,ones_train,ones_val)


def Load_Model(i,X,params):
    json_file = open(params['Spath']+params['Sname']+'.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # return(loaded_model)

# def Load_Weights(loaded_model,params):
    loaded_model.load_weights(params['Spath']+params['Sname']+str(i)+'.h5')
    Weights = loaded_model.get_weights()
    if params['Loss'] =='Boot_Loss':
        loaded_model.compile(loss=Boot_Loss, optimizer='adam')
    elif params['Loss']=='Variance_Loss':
        loaded_model.compile(loss=Variance_Loss, optimizer='adam')
    else:
        loaded_model.compile(loss=params['Loss'], optimizer='adam')

    return(loaded_model.predict(X).reshape(-1,1),Weights)

def Derivatives(file,params,X,y):
    # time.sleep(2)
    import json
    try:
        with open(params['Spath']+params['Sname']+'.json', 'r') as json_file:
            # loaded_model = model_from_json(json_file.read())
            architecture = json.load(json_file)
            # loaded_model = model_from_json(architecture)
            loaded_model = model_from_json(json.dumps(architecture))
    except:
        try:
            time.sleep(10)
            with open(params['Spath']+params['Sname']+'.json', 'r') as json_file:
                # loaded_model = model_from_json(json_file.read())
                architecture = json.load(json_file)
                # loaded_model = model_from_json(architecture)
                loaded_model = model_from_json(json.dumps(architecture))
        except:
            pass
    loaded_model.load_weights(params['Spath']+params['Sname']+str(file)+'.h5')
    W = loaded_model.get_weights()
    if params['Loss'] =='Boot_Loss':
        loaded_model.compile(loss=Boot_Loss, optimizer='adam')
    elif params['Loss']=='Variance_Loss':
        loaded_model.compile(loss=Variance_Loss, optimizer='adam')
    else:
        loaded_model.compile(loss=params['Loss'], optimizer='adam')

    YStandard = joblib.load(params['Spath']+"Y_scaler.save")
    Op = []
    wi = W[0]
    wc = W[1]
    wo = W[2]
    nh = W[2].shape[0]
    Z = np.zeros(nh)
    for i in range(X.shape[0]):
        Ip = X[i]
        H1 = (((Ip*W[0].T)).sum(axis=1)+W[1])
        # print(H1.shape)
        if params['Activation'] == 'relu':
            H1 = np.maximum(H1,np.zeros(H1.shape[0]))
            # AD = np.maximum(Z,H1)
            # AD[AD>0]=1
        if params['Activation'] == 'sigmoid':
            H1 = 1/(1+np.exp(-H1))
        #     AD = H1*(1-H1)
        # print(AD)
        H2 = (H1*W[2].T).sum()+W[3]
        Op.append(H2)
    y = YStandard.transform(y.reshape(-1,1))
    Op = np.array(Op)#YStandard.inverse_transform(np.array(Op).reshape(-1,1))
    Cons = []
    # print(wi.shape,wc.shape,wo.shape)
    Derivs = []
    # print(X.shape)
    for i in range(X.shape[1]):

        dj=[]

        for j in range(y.shape[0]):
            target = y[j]
            output = float(Op[j])
            Xj = X[j][i]
            if np.isnan(target)==False:
                H1 = ((Xj*wi[i,:]))+wc#[i]
                if params['Activation']=='relu':
                    AD = np.maximum(Z,H1)
                    AD[AD>0]=1
                else:
                    H1 = 1/(1+np.exp(-H1))
                    AD = H1*(1-H1)
                # print(wo,AD,H1,wi,wc)
                Sum = np.array([wo[h]*AD[h]*wi[i,h] for h in range(nh)]).sum()
                # print(Sum)
                # print()
                Sj = 1
                dj.append(Sj*Sum)
        dji = np.array(dj)
        Derivs.append(dji)
        Cons.append(np.sum(dji**2))
    Cons = np.array(Cons)
    Derivs = np.array(Derivs)
    return(Cons,Derivs,Op)