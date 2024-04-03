

GCF_DEPLOY() 
{
  FUNCTION_NAME="hello_world"

  gcloud functions deploy $FUNCTION_NAME \
    --runtime python312 \
    --trigger-http \
    --allow-unauthenticated
}


