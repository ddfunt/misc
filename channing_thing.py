# -*- coding: utf-8 -*-
"""
Created on Sat Apr 29 18:01:55 2017

@author: chann
"""
import time
import os
import numpy as np
import visa

class ExperimentFoo:
    save_every=input('Enter the number of averaged FIDs before saving: \n')
    run_until=input('Enter the number of files to be saved: \n')
    file_folder=input('Enter the path to the folder you want to save to: \n')
    base_name=input('Enter the base name for the files: \n')

    def __init__(self, host, port, timeout, save_every, run_until, file_folder, base_name):
        ScopeDriver.__init__(host, port, timeout)
        self.save_every = save_every
        self.run_until = run_until
        self.file_folder = file_folder
        self.base_name = base_name
        #Removed  self.scope = ScopeDriver(...)
    
    def experiment_loop(self):
        experiment_counter=0
        experiment_counter <= self.run_until
        while True:
            time.sleep(5)
            is_saved=self._auto_save()
            if is_saved is self._archive_data():
                experiment_counter += 1
            if experiment_counter >= self.run_until:
                break

    def _auto_save(self):
        current_averages = self.get_averages() #Removed .scope
        if current_averages > self.save_every:
            self._archive_data() #might need to change back to (self, averages)
        self.query('CLEAR')
        
    def _archive_data(self, averages):
        save_file = os.path.join(self.file_folder, 
                                 '{base_name}_{averages}_{time}'.format(base_name=self.base_name,
                                 averages=self.save_every, 
                                 time=time.strftime('%H_%M_%S')))
        data = self.get_data(channel='math2') 
        #formatted_data = FORMAT_YOUR_DATA
        with open(save_file, 'r') as f:
            f.write(data) #Changed from (formatted_data) for the time being
            
class ScopeDriver:
    _host = ("GPIB8::1::INSTR")
    _timeout = 5
    _port = 5000

    def __init__(self, host="GPIB8::1::INSTR", port=5000, timeout=5): 
        if host:
            self._host = host
        if timeout:
            self._timeout = timeout
        if port:
            self._port = port

        self._socket = self._connect()
    
    def _connect(self):
   
        rm = visa.ResourceManager()
        try:
            self._conn = rm.open_resource(self._host)
        except:
            raise ConnectionError('Error message here')
    
    def _query(self, command):
        return self._conn.query(command)
    
    def get_averages(self):
        return self._query('ACQuire:NUMAVg?')

    def set_data_source(self, source='math2'):

        accepted = ['ch1', 'ch2', 'ch3', 'ch4', 'math1', 'math2', 'math3', 'math4']

        if source.lower() in accepted:
            self.write('data:source %s' % source)
        else:
            raise ValueError('Source %s unknown, expected %s' % (source, ' or '.join(accepted)))
    
    def set_data_range(self, start, stop): #(self, start=1, stop=1000)
        self.write('data:start %i' % start)
        self.write('data:stop %i' % stop)
        
    def get_data(self, channel, frame=None):
        header = self._query('WFMOutpre?').split(',')

        for row in header:
            if 'points' in row:
                data_len = int(row.replace('points', ''))

        if frame is not None:

            self.write('data:framestart %s'%frame)
            self.write('data:framestop %s'%frame)

        self.set_data_range(0, data_len)

        output = self._query('curve?').strip().split(',')

        data = np.array(output, dtype='f8')
        return data
