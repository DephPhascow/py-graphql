from py_simple_graphql.utils import gen_send_file

def file_upload():
  return gen_send_file(
    name="addMessage",
    request="message",
    var={
      "appoitmentId": "String!",
      "message": "String!",
      "file": "Upload!"
    }
  )