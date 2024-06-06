import json
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext, UserCredential
from office365.runtime.client_request import ClientRequest
from office365.runtime.http.request_options import RequestOptions


site_url = 'https://checkptsystems.sharepoint.com'
username = "StoreOperations@checkptsystems.onmicrosoft.com/sites/"
password = "5F6c5tL!W2"
localpath = "/test.txt"
remotepath = "/sites/iovideos/"+"test.txt"
 
ctx_auth = AuthenticationContext(url=site_url)
if ctx_auth.acquire_token_for_user(username=username, password=password):
 
    ctx = ClientContext(site_url, ctx_auth)
    web=ctx.web
    ctx.load(web)
    ctx.execute_query()

    target_library = ctx.web.lists.get_by_title("iovideos")
 
 
    with open(f"/test.txt", "rb") as file:
        target_folder = target_library.root_folder
        upload_file = target_folder.upload_file("test.txt", file)
        ctx.execute_query()
else:
    print("error", ctx_auth.get_last_error())

