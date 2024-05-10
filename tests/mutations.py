from py_simple_graphql.utils import gen_send_file

def file_upload():
  return gen_send_file(
    name="fileUpload",
    var={
      "img": "Upload!",
      "name": "String!"
    }
  )