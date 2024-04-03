# import waitress # Run with a Production Server
from flask import Flask
from flask import request
from flask import jsonify 
from flask import render_template  

import os 
import json 
import time 
import datetime
import openai_curls 
import firebase_tools 


##=====================================================================||====##  
##=====================================================================||====##
app = Flask(__name__, template_folder='', static_folder='')
#app = Flask(__name__)


def getplanprice(function_id, function_arguments) : 
  firebase_tools.Calls.update({function_id:function_arguments}) 
  return json.dumps({"price":0})  


funcs = {"collect_guest_info":getplanprice}


##=====================================================================||====##
##=====================================================================||====##
## Step 1
@app.route('/threads', methods=['POST'])
def threads_id_create() : 
  key = request.form['key'] 
  response = openai_curls.client_beta_threads_create(key)
  thread_id = response.get("id")
  print("[threads_id_create] '%s' created!" % thread_id) 
  return jsonify({"id":thread_id})


## Step  2
@app.route('/message', methods=['POST']) 
def message_post() : 
  key = request.form['key'] 
  thread_id = request.form['id'] 
  assistant_id = request.form['asst'] 
  openai_curls.AssistantsTest(key, assistant_id)

  message = request.form['message'] 
  result = openai_curls.Messages(key, assistant_id, thread_id, message, funcs)

  result["now"] = str(datetime.datetime.now())
  result["asst"] = assistant_id
 
  child1 = firebase_tools.Threads.child(thread_id) 
  child1.push(result) 
  return jsonify(result) 


## Step 3
@app.route('/threads', methods=['DELETE'])
def threads_id_delete() : 
  key = request.form['key'] 
  thread_id = request.form['id'] 
  response = openai_curls.client_beta_threads_delete(key, thread_id)
  assert response.get("deleted") 
  print("[threads_id_delete] '%s' removed!" % thread_id) 
  return "'%s' removed!\n" % thread_id 


##=====================================================================||====##
##=====================================================================||====##
@app.route('/calls')
def calls() : 
  firebase_tools.ReferenceKeysPrint("/Guests") 
  Calls = firebase_tools.ReferenceGet("/Guests").child('Calls').get() 
  return jsonify(Calls)  


@app.route('/threads')
def threads() : 
  firebase_tools.ReferenceKeysPrint("/Guests") 
  threads = firebase_tools.ReferenceGet("/Guests").child('Threads').get() 
  return jsonify(threads)  


##=====================================================================||====##
##=====================================================================||====##
@app.route('/tests', methods=['POST'])
def tests_post() :
  key = request.form['key']
  assistant = request.form['asst']
  response = openai_curls.Tests(key, assistant)
  return jsonify(response) 


@app.route('/tests', methods=['GET'])
def tests_get() : 
  response = openai_curls.TestSimplest() 
  return jsonify(response)


##=====================================================================||====##
##=====================================================================||====##
@app.route('/chat', methods=['GET', 'POST'])
def chat() :
    return render_template('FrontEnd/chat.html')


@app.route('/')
def wellcome() :
  return render_template("FrontEnd/wellcome.html", data="SpicyTech")


##=====================================================================||====##  
##=====================================================================||====##  
import flask_socketio 


class MyCustomNamespace(flask_socketio.Namespace) :
  
  def on_disconnect(self) :
    openai_curls.threads_id_delete(self.threads_id)     
    print('Client Disconnected!!')
  
  def on_connect(self) :
    self.threads_id = openai_curls.threads_id_create() 
    print("Client Connected !!") 

  def on_event1(self, data) :
    flask_socketio.emit('event2', -1)  
    print("[on_event1] received:'%s' " % data)
     
  def on_event2(self, data) :
    print("[on_event2] received:'%s' " % data)
    #print( data )

    # {"getplanprice":getplanprice}
    message = data["msg"]
    responses = openai_curls.message_post(self.threads_id, message, funcs) 
    ##print("responses:", responses) 

    child1 = firebase_tools.Threads.child(self.threads_id) 
    child1.push(responses) 
    
    for response in responses.get('assistant',[['processing...']]) :
      ##time.sleep(0.5)
      data = response[0] 
      flask_socketio.emit('my_response', data)
      print("[on_my_response] sent:'%s' " % data)

      
##
socketio = flask_socketio.SocketIO(app)
socketio.on_namespace(MyCustomNamespace("/"))


##=====================================================================||====##
if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=3000)
    socketio.run(app, host='0.0.0.0', port=3000, 
                 debug=True, allow_unsafe_werkzeug=True)

##=====================================================================||====##
##=====================================================================||====##
