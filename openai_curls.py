import os
import json
from re import M
import time
import requests
import datetime 

#import dotenv
#dotenv.load_dotenv()
#config = dotenv.dotenv_values(".env")
HTTPS = lambda txt="": 'https://api.openai.com/v1/%s' % txt
THREADS = lambda txt="": HTTPS("/threads%s" % txt)
ASSISTANTS = lambda txt="": HTTPS("/assistants%s" % txt)

##=====================================================================||====##
##=====================================================================||====##
#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#print("[openai_curls] OPENAI_API_KEY:'%s' " % OPENAI_API_KEY)


def client_beta_threads_header(OPENAI_API_KEY):
  headers = {}
  headers["Content-Type"] = 'application/json'
  headers["Authorization"] = 'Bearer %s' % OPENAI_API_KEY
  headers["OpenAI-Beta"] = "assistants=v1"
  return headers


def client_beta_assistants_retrieve(OPENAI_API_KEY, assistant_id):
  ## client.beta.assistants.retrieve
  https = ASSISTANTS("/%s" % assistant_id)
  response = requests.get(https,
                          headers=client_beta_threads_header(OPENAI_API_KEY))
  return response.json()


##=====================================================================||====##
##=====================================================================||====##
## threads
def client_beta_threads_create(API_KEY):
  ## client.beta.threads.create
  https = THREADS()
  response = requests.post(https, headers=client_beta_threads_header(API_KEY))
  return response.json()


def client_beta_threads_delete(API_KEY, thread_id):
  ## client.beta.threads.delete
  https = THREADS("/%s" % thread_id)
  response = requests.delete(https,
                             headers=client_beta_threads_header(API_KEY))
  return response.json()


def client_beta_threads_retrieve(API_KEY, thread_id):
  ## client.beta.threads.retrieve
  https = THREADS("/%s" % thread_id)
  response = requests.get(https, headers=client_beta_threads_header(API_KEY))
  return response.json()


##=====================================================================||====##
def ThreadsRunner(OPENAI_API_KEY, funtion):
  response = client_beta_threads_create(OPENAI_API_KEY)
  thread_id = response.get("id")

  funtion(OPENAI_API_KEY, thread_id)

  response = client_beta_threads_delete(OPENAI_API_KEY, thread_id)
  assert response.get("deleted")
  print("[ThreadsTest] id:'%s' " % response["id"])
  return


##=====================================================================||====##
##=====================================================================||====##
## runs
def client_beta_threads_runs_create(API_KEY, thread_id, assistant_id):
  ## client.beta.threads.runs.create
  json_data = {"assistant_id": assistant_id}
  https = THREADS("/%s/runs" % thread_id)
  response = requests.post(https,
                           headers=client_beta_threads_header(API_KEY),
                           json=json_data)
  return response.json()


def client_beta_threads_runs_cancel(API_KEY, thread_id, run_id):
  ## client.beta.threads.runs.cancel
  https = THREADS("/%s/runs/%s/cancel" % (thread_id, run_id))
  response = requests.post(https, headers=client_beta_threads_header(API_KEY))
  return response.json()


def client_beta_threads_runs_retrieve(API_KEY, thread_id, run_id):
  ## client.beta.threads.runs.retrieve
  https = THREADS("/%s/runs/%s" % (thread_id, run_id))
  response = requests.get(https, headers=client_beta_threads_header(API_KEY))
  return response.json()


##=====================================================================||====##
##=====================================================================||====##
## messages
def client_beta_threads_messages(API_KEY, thread_id, role, content):
  ## client.beta.threads.messages
  json_data = {}
  json_data['role'] = role  # 'user'
  json_data[
      'content'] = content  # 'How does AI work? Explain it in simple terms.'

  #  https = "https://api.openai.com/v1/threads/%s/messages" % thread_id
  https = THREADS("/%s/messages" % (thread_id))
  response = requests.post(https,
                           headers=client_beta_threads_header(API_KEY),
                           json=json_data)
  return response.json()


def client_beta_threads_messages_list(API_KEY, thread_id):
  ## client.beta.threads.list
  #  https = "https://api.openai.com/v1/threads/%s/messages" % thread_id
  https = THREADS("/%s/messages" % (thread_id))
  response = requests.get(https, headers=client_beta_threads_header(API_KEY))
  return response.json()


##=====================================================================||====##
def Messages(API_KEY,
             assistant_id,
             thread_id,
             content,
             functions=None,
             role="user") : 
  MessageExtract = lambda d : (d["role"], [c["text"]["value"] for c in d["content"] if "text" in c["type"]]) 
  conversation = [] 

  client_beta_threads_messages(API_KEY, thread_id, role, content)

  run_id = client_beta_threads_runs_create(API_KEY, thread_id,
                                           assistant_id).get("id")
    
  conversation.append( ("user",[content]) ) 
  while True :
    response = client_beta_threads_runs_retrieve(API_KEY, thread_id, run_id)

    status = response.get("status")
    if not status == "in_progress" :
      print(f"[RunnerController] Status:'{status}'")
    if status == "completed" : 
      response = client_beta_threads_messages_list(API_KEY, thread_id)
      data = response.get("data")
      results = [MessageExtract(d) for d in data] 
      assert len(results) > 0 
      conversation.append( results[0] ) 
      break
    elif status == "requires_action" :
      tool_outputs = RequiredAction(run_id, thread_id, response, functions)
      client_beta_threads_runs_submit_tool_outputs(API_KEY, thread_id, run_id,
                                                   tool_outputs)
      response = client_beta_threads_messages_list(API_KEY, thread_id)
      data = response.get("data")
      results = [MessageExtract(d) for d in data] 
      assert len(results) > 0 
      conversation.append( results[0] ) 
    time.sleep(0.1)

  results = {} 
  for (role,content) in conversation : 
    if not role in results : results[role] = []
    results[role].append(content) 

  print("================================") 
  print( results )
  print("================================")   
  return results


##=====================================================================||====##
##=====================================================================||====##
## tool_outputs
def RequiredAction(run_id, thread_id, response, functions):
  RequiredAction = response.get("required_action")
  RequiredActionSubmitToolOutputs = RequiredAction.get("submit_tool_outputs")
  RequiredActionFunctionToolCall = RequiredActionSubmitToolOutputs.get(
      "tool_calls")

  tool_outputs = []
  tool_arguments = []
  for tool_call in RequiredActionFunctionToolCall:
    function = tool_call["function"]
    function_id = tool_call["id"]
    function_name = function["name"]
    function_arguments = json.loads(function["arguments"])

    function_aux = lambda fid, farg: json.dumps({"response": "Success"})
    function_response = functions.get(function_name,
                                      function_aux)(function_id,
                                                    function_arguments)
    tool_outputs.append({
        "tool_call_id": function_id,
        "output": function_response
    })
    tool_arguments.append({
        "tool_call_id": function_id,
        "output": function_arguments,
        "name": function_name
    })

    print("[RequiredAction] %s(%s)" % (function_name, function_arguments))
  return tool_outputs


def client_beta_threads_runs_submit_tool_outputs(API_KEY, thread_id, run_id,
                                                 tool_outputs):
  ## client.beta.threads.runs.submit_tool_outputs
  json_data = {'tool_outputs': tool_outputs}
  https = THREADS("/%s/runs/%s/submit_tool_outputs" % (thread_id, run_id))
  response = requests.post(https,
                           headers=client_beta_threads_header(API_KEY),
                           json=json_data)
  return response.json()


##=====================================================================||====##
def MessagesSend(API_KEY, assistant_id, messages, RequiredAction):
  response = client_beta_threads_create(API_KEY)
  thread_id = response.get("id")

  results = []
  for message in messages:
    result = Messages(API_KEY, assistant_id, thread_id, message,
                      RequiredAction)
    results.append(result)
    #print("[MessagesTest]", results)
    assert len(result) > 0

  response = client_beta_threads_delete(API_KEY, thread_id)
  assert response.get("deleted")
  return results


def ResponsesPrint(responses):
  row = -1
  for response in responses:
    for i, (k, v) in response.items():
      if i > row:
        print("%03d) [%s] " % (i, k), v)
        row += 1
  return


##=====================================================================||====##
##=====================================================================||====##
def AssistantsTest(OPENAI_API_KEY, assistant_id):
  response = client_beta_assistants_retrieve(OPENAI_API_KEY, assistant_id)
  assert response["id"] == assistant_id
  print("[AssistantsTest] name:'%s' " % response["name"])
  return response


def ThreadsTest(OPENAI_API_KEY):
  response = client_beta_threads_create(OPENAI_API_KEY)
  thread_id = response.get("id")

  response = client_beta_threads_retrieve(OPENAI_API_KEY, thread_id)
  response = client_beta_threads_delete(OPENAI_API_KEY, thread_id)
  assert response.get("deleted")
  print("[ThreadsTest] id:'%s' " % response["id"])
  return


def RunnerTest(OPENAI_API_KEY, assistant_id):
  response = client_beta_threads_create(OPENAI_API_KEY)
  thread_id = response.get("id")

  response = client_beta_threads_runs_create(OPENAI_API_KEY, thread_id,
                                             assistant_id)
  run_id = response.get("id")

  response = client_beta_threads_runs_retrieve(OPENAI_API_KEY, thread_id,
                                               run_id)
  response = client_beta_threads_runs_cancel(OPENAI_API_KEY, thread_id, run_id)

  time.sleep(1.0)
  assert response.get("status") == "cancelling"
  print("[RunnerTest], id:'%s' " % response["id"])

  response = client_beta_threads_delete(OPENAI_API_KEY, thread_id)

  assert response.get("deleted")
  print("[ThreadsTest] id:'%s' " % response["id"])
  return


def MessagesSendTest(API_KEY, assistant_id):
  queries = ["hi!"]
  responses = MessagesSend(API_KEY, assistant_id, queries, None)
  #ResponsesPrint(responses)
  return responses


def RequiredActionTest(API_KEY, assistant_id):
  getplanprice = lambda fid, arguments: json.dumps({"price": 0})
  functions = {"getplanprice": getplanprice}

  queries = []
  queries.append("Hola!")
  queries.append(
      "Quiero el plan individual, mi edad es 10 anios. Toda la informacion anterior es correcta"
  )
  queries.append("thanks!")

  responses = MessagesSend(API_KEY, assistant_id, queries, functions)
  #ResponsesPrint(responses)
  return responses


##=====================================================================||====##
def threads_id_create() : 
  key = os.getenv("OPENAI_API_KEY")
  response = client_beta_threads_create(key)
  thread_id = response.get("id")
  print("[threads_id_create] '%s' created!" % thread_id) 
  return thread_id 


def threads_id_delete(thread_id) : 
  key = os.getenv("OPENAI_API_KEY")
  response = client_beta_threads_delete(key, thread_id)
  assert response.get("deleted") 
  print("[threads_id_delete] '%s' removed!" % thread_id) 
  return 


def message_post(thread_id, message, funcs, db=None) : 
  key = os.getenv("OPENAI_API_KEY")
  assistant = os.getenv("OPENAI_PLANNER_ID") 
  #AssistantsTest(key, assistant_id)

  result = Messages(key, assistant, thread_id, message, funcs)
  result["now"] = str(datetime.datetime.now())
  result["asst"] = assistant  
  return result



##=====================================================================||====##
def Tests(key, assistant) :
  #key = request.form['key']
  #assistant = request.form['assistant']
  AssistantsTest(key, assistant)  
  ThreadsTest(key) 
  RunnerTest(key, assistant) 
  response = MessagesSendTest(key, assistant)   
  response = RequiredActionTest(key, assistant) 
  return response
  

def TestSimplest() : 
  key = os.getenv("OPENAI_API_KEY")
  assistant = os.getenv("OPENAI_PLANNER_ID") 
  response = AssistantsTest(key, assistant)
  ##print(response)
  return response 
  

TestSimplest() 
  
##=====================================================================||====##
##=====================================================================||====##
