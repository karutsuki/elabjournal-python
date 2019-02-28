from .pager import *
import json
import xlrd
import pandas as pd
import matplotlib
import PIL
from io import BytesIO


class section:

    def __init__(self, api, data):        
        if (not(data==None) & (type(data) == dict) & 
            ("expJournalID" in data.keys()) & 
            ("experimentID" in data.keys()) & 
            ("sectionType" in data.keys()) & 
            ("sectionHeader" in data.keys())
           ):
            self.__api = api
            self.__expJournalID = data["expJournalID"]
            self.__experimentID = data["experimentID"]
            self.__sectionType = data["sectionType"]
            self.__sectionHeader = data["sectionHeader"]
            self.__title = "Section '"+self.__sectionHeader+"' ("+str(self.__expJournalID)+", "+self.__sectionType+")"
            self.__data = data
        else:
            raise Exception("no (valid) section data") 
        
    def __repr__(self):
        return(self.__title)
        
    def type(self):
        return(self.__sectionType)
    
    def title(self):
        return(self.__sectionHeader)
    
    def experiment(self):
        request = {}
        return(self.__api.experiment(self.__experimentID))
           
    def get(self):
        if self.__sectionType=="DATATABLE":
            rp = self.__api.request("/api/v1/experiments/sections/"+str(self.__expJournalID)+"/datatable", "get", {})
            if not(rp==None) & (type(rp) == list):
                return(pd.DataFrame(rp))                                                 
            else:
                raise Exception("section type "+self.__sectionType+" returns unexpected data")
        elif self.__sectionType=="PARAGRAPH":
            rp = self.__api.request("/api/v1/experiments/sections/"+str(self.__expJournalID)+"/html", "get", {}, stream=True)
            return(rp.decode("utf-8"))                                                             
        elif self.__sectionType=="CANVAS":
            rp = self.__api.request("/api/v1/experiments/sections/"+str(self.__expJournalID)+"/canvas", "get", {}, stream=True)
            stream = BytesIO(rp)
            return(PIL.Image.open(stream))                                                             
        elif self.__sectionType=="EXCEL":
            rp = self.__api.request("/api/v1/experiments/sections/"+str(self.__expJournalID)+"/excel", "get", {}, stream=True)
            wb = xlrd.open_workbook(file_contents=rp)
            xlsx = pd.ExcelFile(wb, engine="xlrd")                        
            return(xlsx)                                                             
        elif self.__sectionType=="IMAGE":
            return(pager(self.__api, "Images", "/api/v1/experiments/sections/"+str(self.__expJournalID)+"/images", {}, "experimentFileID", "experimentFileID", 5))                                  
        else:
            raise Exception("section type "+self.__sectionType+" not supported")
            
    def set(self, data):
        if self.__sectionType=="DATATABLE":
            if type(data) == pd.DataFrame:
                location = "/api/v1/experiments/sections/"+str(self.__expJournalID)+"/datatable"
                rp = self.__api.request(location, "put", json.dumps(data.values.tolist()), headers={"Content-Type": "application/json"})                
            else:
                raise Exception("data type not supported to set "+self.__sectionType) 
        elif self.__sectionType=="CANVAS":
            location = "/api/v1/experiments/sections/"+str(self.__expJournalID)+"/canvas"
            if type(data) == matplotlib.figure.Figure:
                sizes = data.get_size_inches()
                dpi = 825/sizes[0]
                figfile = BytesIO()
                data.savefig(figfile, format="png", dpi=dpi, bbox_inches="tight")
                rp = self.__api.request(location, "put", figfile.getvalue(), headers={"Content-Type": "image/png"}) 
            elif type(data) == PIL.PngImagePlugin.PngImageFile:
                with BytesIO() as output:
                    data.save(output, format="png")
                    contents = output.getvalue()
                rp = self.__api.request(location, "put", contents, headers={"Content-Type": "image/png"}) 
            else:
                raise Exception("data type not supported to set "+self.__sectionType)    
        elif self.__sectionType=="EXCEL":
            if type(data) == pd.DataFrame:
                location = "/api/v1/experiments/sections/"+str(self.__expJournalID)+"/excel"
                raise Exception("section type EXCEL not (yet) supported")
                #rp = self.__api.request(location, "put", dump)                
            else:
                raise Exception("data type not supported to set "+self.__sectionType)                             
        else:
            raise Exception("section type "+self.__sectionType+" not supported")    
        
        
        