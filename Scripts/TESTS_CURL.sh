clear

REPLIT_TESTS()
{
  ## POST 
  thread_id=$(curl "${HTML}/threads" --silent --data "key=${KEY}" -H "Accept:application/json" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" ) 
  echo "[POST] thread_id:${thread_id}"

  ## GET 
  response=$(curl "${HTML}/threads" --silent)  
  echo "[GET]:${response}"

  ## MESSAGE 
  MESSAGE="hola!!"
  response=$(curl "${HTML}/message" --silent --data "key=${KEY}&id=${thread_id}&asst=${ASST}&message=${MESSAGE}")
  echo "[POST] response:${response}"

  MESSAGE="Quiero el plan individual, mi edad es 10 anios. Toda la informacion anterior es correcta"
  response=$(curl "${HTML}/message" --silent --data "key=${KEY}&id=${thread_id}&asst=${ASST}&message=${MESSAGE}")
  echo "[POST] response:${response}"

  MESSAGE="thank you so much!"
  response=$(curl "${HTML}/message" --silent --data "key=${KEY}&id=${thread_id}&asst=${ASST}&message=${MESSAGE}")
  echo "[POST] response:${response}"

  ## DELETE 
  response=$(curl "${HTML}/threads" --silent --data "key=${KEY}&id=${thread_id}" --request "DELETE")
  echo "[DELETE]:${response}"
}


GLITCH_TEST_CURL_ASSISTANT()
{
  ## Step 1
  thread_id=$(curl "${HTML}/threads" --silent --data "key=${KEY}" -H "Accept:application/json" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" )
  echo "[POST] thread_id:${thread_id}"

  ## Step 2a 
  MESSAGE="hola!!"
  response=$(curl "${HTML}/message" --silent --data "key=${KEY}&id=${thread_id}&asst=${ASST}&message=${MESSAGE}")
  echo "[POST] response:${response}"

  ## Step 2b  
  MESSAGE="Quiero el plan individual, mi edad es 10 anios. Toda la informacion anterior es correcta"
  response=$(curl "${HTML}/message" --silent --data "key=${KEY}&id=${thread_id}&asst=${ASST}&message=${MESSAGE}")
  echo "[POST] response:${response}"

  ## Step 2c 
  MESSAGE="thank you so much!"
  response=$(curl "${HTML}/message" --silent --data "key=${KEY}&id=${thread_id}&asst=${ASST}&message=${MESSAGE}")
  echo "[POST] response:${response}"

  ## Step 3 
  response=$(curl "${HTML}/threads" --silent --data "key=${KEY}&id=${thread_id}" --request "DELETE")
  echo "[DELETE]:${response}"
} 

GLITCH_TEST_SIMPLEST()
{
  ## GET 
  response=$(curl "${HTML}/tests" --silent)
  echo "[GET] : '${response}' "

  ## POST 
  #response=$(curl "${HTML}/tests" --silent --data "key=${KEY}&asst=${ASST}")
  echo "[POST] : '${response}' "
} 


KEY=
ASST=
HTML=

##REPLIT_TESTS
GLITCH_TEST_SIMPLEST 
##GLITCH_TEST_CURL_ASSISTANT

