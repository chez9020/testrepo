import re,os,glob,sys,csv

from openpyxl import Workbook

def Alarms(PathDate,BSC,Technology):

    SitesFolders = next(os.walk(PathDate))[1]

    FileName = (PathDate + "\\" + Technology +"_" + os.path.basename(os.path.normpath(PathDate))+".csv")

    FileNameStatus = FileName[:-4]+'_Status.txt'

    datoslog = []

    if Technology == "2G":
        datoslog.append("Technology")
        datoslog.append("Site ID")
        datoslog.append("BSC")
        datoslog.append("Command")
        datoslog.append("Alarms")
    else:
        datoslog.append("Technology")
        datoslog.append("Site ID")
        datoslog.append("Site IP")
        datoslog.append("Total Alarms")
        datoslog.append("Alarms")

    with open(FileName,'a',newline='') as LogFileAlarms:
        log_writer = csv.writer(LogFileAlarms, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        log_writer.writerow(datoslog)
        datoslog = []

    Folder = os.path.join(PathDate,Technology,"*.log")
    LogsPath = glob.glob(Folder)

    for LogPath in LogsPath:
        log_file_path = LogPath
        logfile_name = os.path.split(log_file_path)[1]
        logfile = open(log_file_path, 'r')
        log = logfile.read()
        if Technology == "4G":
            Commands = ["(.*?)> st sec\n","(.*?)> st cell\n","(.*?)> ue print -admitted\n"]
            Identifiers = ["Total:\s(.*?)\n","Total:\s(.*?)\n","(.*?)> st cell"]
            for i in range(len(Commands)):
                Status(Commands[i],log,FileNameStatus,Identifiers[i])
            Alarms_4G_3G(Technology,FileName,log,logfile_name)
        elif Technology == "3G":
            Commands = ["(.*?)> st sect\n","(.*?)> st cell\n","(.*?)> get radiolink noof\n"]
            Identifiers = ["Total:\s(.*?)\n","Total:\s(.*?)\n","Total:\s(.*?)\n"]
            for i in range(len(Commands)):
                Status(Commands[i],log,FileNameStatus,Identifiers[i])
            Alarms_4G_3G(Technology,FileName,log,logfile_name)
        elif Technology == "2G":
            Commands = ["<RXMSP:MO=RXOTG(.*?)\n","<RLCRP:CELL=(.*?)\n"]
            Identifiers = ["END\n|NOT ACCEPTED\n","END\n|CELL NOT DEFINED\n"]
            for i in range(len(Commands)):
                Status(Commands[i],log,FileNameStatus,Identifiers[i])
            Commands = ["<RXASP:MO=RXOTG","<RXASP:MO=RXOCF"]
            Identifiers = ["<RXASP:MO=RXOCF","<RXMFP:MO=RXOTG"]
            Nemonico = ["RXOTG","RXOCF"]
            for i in range(len(Commands)):
                Alarms_2G(Technology,FileName,log,Commands[i],Identifiers[i],BSC,Nemonico[i])

def Status(Command,log,FileName,Identificador):
    with open(FileName,'a') as LogFileStatus:
        regex_cell = Command
        matches = re.finditer(regex_cell,log,re.IGNORECASE)
        for match in matches:
            begin = match.start()
            cell_status = log[begin:]
            regex_end = Identificador
            match_end = re.search(regex_end,cell_status)
            end = match_end.end()
            cell_status = cell_status[:end]
            LogFileStatus.write(cell_status+"\n")

def Alarms_4G_3G(Technology,FileName,log,logfile_name):
    datoslog = []
    with open(FileName,'a',newline='') as LogFileAlarms:
        log_writer = csv.writer(LogFileAlarms, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)

        regex_contacto = '(.*?)> alt\n'
        contacto = re.search(regex_contacto,log,re.S)

        regex_Site_Name = ',MeContext=(.*?),'
        site_name = re.search(regex_Site_Name,log,re.S)

        if contacto and site_name != None:
            begin = contacto.end()
            Site_Alarms = log[begin:]
            regex_end = '>>> Total:\s' + '(.*?)\)'
            match_end = re.search(regex_end,Site_Alarms)
            end = match_end.end()
            Site_Alarms = Site_Alarms[:end]
            Total_Alarms = match_end.group(1) + ")"
            Total_Alarms = re.sub(r',', ' ', Total_Alarms)
            Regex_Alarms = '(.*?)\sAlarms'
            match_Total = re.search(Regex_Alarms,Total_Alarms)
            if match_Total.group(1) == "0":
                datoslog.append(Technology)
                if site_name:
                    datoslog.append(site_name.group(1))
                datoslog.append(logfile_name.split(".log")[0])
                datoslog.append(Total_Alarms)
                datoslog.append("Sin Alarmas")
                log_writer.writerow(datoslog)
                datoslog = []
            else:
                alarms_str = ""
                match_alarms_text = re.finditer(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\s(.*?)\n',Site_Alarms)
                for alarm_match in match_alarms_text:
                    str_tmp = re.sub(r',',' ',alarm_match.group(0))
                    str_tmp = re.sub(r'\n','',str_tmp)
                    str_tmp = re.sub(r'(\s+)',' ',str_tmp)
                    alarms_str = alarms_str + str_tmp + " "
                datoslog.append(Technology)
                if site_name:
                    datoslog.append(site_name.group(1))
                datoslog.append(logfile_name.split(".log")[0])
                datoslog.append(Total_Alarms)
                datoslog.append(alarms_str)
                log_writer.writerow(datoslog)
                datoslog = []
                
        else:
            datoslog.append(Technology)
            datoslog.append("")
            datoslog.append(logfile_name.split(".log")[0])
            datoslog.append("Sin contacto del sitio")
            log_writer.writerow(datoslog)
            datoslog = []

def Alarms_2G(Technology,FileName,log,Command,Identifer,BSC,Nemonico):

    datoslog = []
    with open(FileName,'a',newline='') as LogFileAlarms:
        log_writer = csv.writer(LogFileAlarms, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        
        begin_alarm = Command + '(.*?)\n'
        matches = re.finditer(begin_alarm ,log,re.S)
        for match in matches:
            begin = match.start()
            alarm = log[begin:]
            regex_end = Identifer + '(.*?)\n'
            match_end = re.search(regex_end,alarm)
            end = match_end.start()
            text = alarm[:end]
            regex_text = "ALARM SITUATIONS\n"
            begin_text = re.search(regex_text,text,re.S)

            if begin_text != None:
                cut_alarms = text[begin_text.end():]
                begin_Nemonico = Nemonico + "-(.*?)\n"
                matches = re.search(begin_Nemonico,cut_alarms,re.S)
                if matches != None:
                    status = re.sub(r"\s+",'\t',matches.group(1))
                    palabras = re.split('\t',status)
                    if len(palabras) > 2:
                        datoslog.append(Technology)
                        datoslog.append(palabras[1])
                        datoslog.append(BSC)
                        datoslog.append(Command)
                        texts = palabras[2:]
                        alarmas = ""
                        for text in texts:
                            alarmas = alarmas + " " + text 
                        datoslog.append(alarmas)
                        log_writer.writerow(datoslog)
                        datoslog = []
                    else:
                        datoslog.append(Technology)
                        datoslog.append(palabras[1])
                        datoslog.append(BSC)
                        datoslog.append(Command)
                        datoslog.append("Sin Alarmas")
                        log_writer.writerow(datoslog)
                        datoslog = []
                else:
                    datoslog.append(Technology)
                    datoslog.append("")
                    datoslog.append(BSC)
                    datoslog.append(Command)
                    datoslog.append("BSC Erronea")
                    log_writer.writerow(datoslog)
                    datoslog = []
            else:
                datoslog.append(Technology)
                datoslog.append("")
                datoslog.append(BSC)
                datoslog.append(Command)
                datoslog.append("BSC Erronea")
                log_writer.writerow(datoslog)
                datoslog = []
                
##Alarms("C:\\Users\\EORATJU\\Documents\\My Received Files\\012120200929","CAREB1","4G")
##Alarms("C:\\E-HealthCheck\\OUTPUT\\012520200642","SPEEB1","3G")
##Alarms("C:\\E-HealthCheck\\OUTPUT\\012620201017","","2G")
