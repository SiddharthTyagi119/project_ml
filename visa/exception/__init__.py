#it will run on complete program and whatever error that we get , it get stored under the log file
import os
import sys

#we need to capture error message and error details.
class CustomException(Exception):
    
    def __init__(self, error_message:Exception,error_detail:sys):
        super().__init__(error_message)
        self.error_message=CustomException.get_detailed_error_message(error_message=error_message,
                                                                       error_detail=error_detail)

    @staticmethod
    #both the error info captured as a string
    def get_detailed_error_message(error_message:Exception,error_detail:sys)->str:
        
        #error detail exec unction return 3 things and we need only one thing that is executable class.
        _,_ ,exec_tb = error_detail.exc_info()

        #to know n which line we got the error for both exception and try blocks
        exception_block_line_number = exec_tb.tb_frame.f_lineno
        try_block_line_number = exec_tb.tb_lineno
        
        #in which file we are getting the error
        file_name = exec_tb.tb_frame.f_code.co_filename
        error_message = f"""
        Error occured in script: 
        [ {file_name} ] at 
        try block line number: [{try_block_line_number}] and exception block line number: [{exception_block_line_number}] 
        error message: [{error_message}]
        """
        return error_message
    
    def __str__(self):
        return self.error_message


    def __repr__(self) -> str:
        return CustomException.__name__.str()
    
