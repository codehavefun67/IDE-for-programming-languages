from subprocess import Popen
class compiler:
    def __init__(s, file_output: str, source_code:str):
        s.file_output = file_output
        s.source_code=source_code
        s.command = "g++ -o {} {}"
        s.compile(s.file_output, s.source_code)
    def compile(s, output, source_code):
        import os
        if os.path.exists(output):
            os.remove(output)
        elif os.path.exists(source_code):
            Popen(s.command.format(output, source_code), shell=True).wait(timeout=3)
            return True
        else:
            raise FileNotFoundError("Source code does not exist")
    def compile_to_obj(s, output, src):
        import os
        if os.path.exists(output):
            os.remove(output)
        elif os.path.exists(src):
            Popen("g++ -c {} -o {}".format(src, output), shell=True).wait(timeout=3)
            return True
        else:
            raise FileNotFoundError("Source code does not exist")
            