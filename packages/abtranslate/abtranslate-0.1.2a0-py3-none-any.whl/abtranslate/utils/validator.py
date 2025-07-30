from zipfile import ZipFile
def is_valid_model_file(model_file):
    try:
        with ZipFile(model_file) as model:
            print(model.namelist())
    except:
        return False