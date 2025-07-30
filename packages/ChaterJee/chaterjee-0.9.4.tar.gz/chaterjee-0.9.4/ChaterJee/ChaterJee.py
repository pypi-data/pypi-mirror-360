import os, sys
import time
from datetime import datetime
import urllib.parse
import asyncio
import pickle
import html
import traceback
import logging, json
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Updater, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters, PollAnswerHandler, PollHandler
from telegram.constants import ParseMode
import os.path
import threading
import subprocess
from subprocess import PIPE, Popen
from pathlib import Path
import argparse

start_txt = \
"""
I am ChaterJee, a Research assistant Bot developed by Pallab Dutta in 2025.

*TEXT*
acts as a bash command and runs on host terminal.

*COMMANDS*
/start : returns this text.
/jobs : shows your jobs
/clear : clears chat history
/edit file.json : let you edit the file.json

"""

_data = Path.home() / ".data"
_data.mkdir(exist_ok=True)
jobs_file = _data / "JOB_status.json"

def unformat_text(text):
    special_chars = ['_', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, '\\' + char)
    return text

def read_json(filename):
    with open(filename, 'r') as ffr:
        data = json.load(ffr)
    return data

def save_json(filename,data):
    with open(filename, 'w') as ffw:
        json.dump(data, ffw, indent=4)

def get_jobs_status():
    jobs = read_json(jobs_file)
    TXT = ""
    
    for jobname in jobs:
        try:
            status = jobs[jobname]['status']
            status_sent = jobs[jobname]['stat_sent']
            if (not status_sent) and (status is not None):
                TXT += f"Your JOB: {jobname}"
                if status == 0:
                    TXT += " is completed."
                elif status < 0:
                    TXT += f" is killed by signal {-status}"
                else:
                    TXT += f" exited with error code {status}"
                jobs[jobname]['stat_sent'] = True
                TXT += "\n\n"
        except KeyError:
            pass

    save_json(jobs_file,jobs)
    
    return TXT

def get_scheduled_jobs_status():
    jobs = read_json(jobs_file)
    TXT = ""

    for jobname in jobs:
        try:
            scheduled = jobs[jobname]['scheduled']
            running = jobs[jobname]['running']
            status = jobs[jobname]['status']
            if scheduled == 1 and running:
                TXT += f"Your JOB: {jobname} is dispatched from scheduler for running."
                TXT += "\n\n"
                jobs[jobname]['scheduled'] = 2
            elif status is not None:
                jobs[jobname]['running'] = False
        except KeyError:
            pass

    save_json(jobs_file,jobs)

    return TXT

def get_active_jobs():
    jobs = read_json(jobs_file)

    jobList = []
    for jobname in jobs:
        try:
            seen = jobs[jobname]['seen']
            if not seen:
                jobList.append(jobname)
        except:
            pass

    return jobList

def whether_to_run(jobname):
    jobs = read_json(jobs_file)
    runjob = False
    for jobN in jobs:
        try:
            status = jobs[jobN]['status']
            running = jobs[jobN]['running']
            if (status is None) or running:
                if jobN == jobname:
                    runjob = True
                break
        except KeyError:
            pass
    
    return runjob

def hide_job(jobname):
    jobs = read_json(jobs_file)
    try:
        status = jobs[jobname]['status']
        jobs[jobname]['seen'] = True
        if status is not None:
            save_json(jobs_file,jobs)
    except:
        pass

def get_line(raw_line):
    return b''.join(raw_line.splitlines())

def decode_rawline(raw_line):
    try:
        last1,last2 = raw_line.split(b'\r\r')[-2:]
    except:
        last2 = raw_line.split(b'\r\r')[-1]
        last1 = raw_line.split(b'\r\r')[-1]
    head = get_line(last2.split(b'\r')[-1])
    tail1 = get_line(last1.split(b'\r')[0])
    tail2 = get_line(last2.split(b'\r')[0])
    tail = tail1 if len(tail1)>len(tail2) else tail2
    total = head+tail[len(head):]#+b'\n'
    total = total.decode('utf-8')#[:-1]
    return total

def tail(filepath,n=10):
    """
    Reads a file in binary mode to reveal raw carriage returns,
    then decodes and checks for '\r'.
    """
    try:
        decoded_strings = []
        with open(filepath, 'rb') as ffr_binary:
            raw_bytes = ffr_binary.readlines()[-n:]
            for line in raw_bytes:
                try:
                    decoded_strings.append(decode_rawline(line))
                except UnicodeDecodeError:
                    decoded_strings.append(raw_bytes.decode('latin-1'))
            decoded_string = '\n'.join(decoded_strings)
            return decoded_string

    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

class ChatLogs:
    def __init__(self, TOKEN, CHATID):
        self.home = Path.home()
        self.TOKEN = TOKEN
        self.CHATID = CHATID
        self.txt = ''
        self.fig = ''
        self.path = os.popen('pwd').read()[:-1]
        self.smsID = []
        self.dict = {}
        self.jobs = {}
        self.runexe = "run.sh"
        self.killexe = "kill_run.sh"

    def cmdTRIGGER(self, read_timeout=7, get_updates_read_timeout=42):
        #que = asyncio.Queue()
        application = ApplicationBuilder().token(self.TOKEN).read_timeout(read_timeout)\
                .get_updates_read_timeout(get_updates_read_timeout).build()
        #updater = Updater(application.bot, update_queue=que)

        start_handler = CommandHandler('start', self.start)
        application.add_handler(start_handler)

        jobrun_handler = CommandHandler('run', self.runjob)
        application.add_handler(jobrun_handler)

        #fEdit_handler = CommandHandler('edit', self.EditorBabu)
        #application.add_handler(fEdit_handler)

        #cmd_handler = CommandHandler('sh', self.commands)
        #application.add_handler(cmd_handler)

        #cancel_handler = CommandHandler('cancel', self.cancel)
        #application.add_handler(cancel_handler)

        jobs_handler = ConversationHandler(\
        entry_points=[CommandHandler("jobs", self.ShowJobs),\
                    CommandHandler("clear", self.ask2clear),\
                    CommandHandler("edit", self.EditorBabu),\
                    CommandHandler("kill", self.ask2kill)],\
        states={
            0: [MessageHandler(filters.Regex("^(JOB)"), self.StatJobs)],
            1: [MessageHandler(filters.Regex("^(Yes|No)$"), self.ClearChat)],
            2: [MessageHandler(filters.Regex("^(FILE)"), self.SendEditButton)],
            3: [MessageHandler(filters.Regex("^(Yes|No)$"), self.killjob)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        application.add_handler(jobs_handler)

        application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, self.web_app_data))
        application.add_handler(MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^(JOB:|FILE:|Yes$|No$)")), self.commands))

        #await application.shutdown()
        #await application.initialize()

        #updater = Updater(application.bot, update_queue=que)
        #await updater.initialize()
        #await updater.start_polling()
        job_queue = application.job_queue

        send_job_complete_notification = job_queue.run_repeating(self.send_jobs_status, interval=5, first=10)

        send_job_running_notification = job_queue.run_repeating(self.send_scheduled_jobs_status, interval=5, first=10)

        application.run_polling()

    async def send_jobs_status(self, context: ContextTypes.DEFAULT_TYPE):
        TXT = get_jobs_status()#.strip()
        print(r"{}".format(TXT))
        if len(TXT):
            self.txt = TXT
            await self.sendUpdate(context = context)

    async def send_scheduled_jobs_status(self, context: ContextTypes.DEFAULT_TYPE):
        TXT = get_scheduled_jobs_status()#.strip()
        print(r"{}".format(TXT))
        if len(TXT):
            self.txt = TXT
            await self.sendUpdate(context = context)

    async def sendUpdate(self, context: ContextTypes.DEFAULT_TYPE):
        if len(self.txt):
            await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
            self.txt = unformat_text(self.txt)
            msg = await context.bot.send_message(chat_id=self.CHATID, text=self.txt, parse_mode='MarkdownV2')
            self.smsID.append(msg.message_id)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        self.txt = start_txt
        await self.sendUpdate(context)

    def register_to_log(self, job_name: str, log_path: str):
        self.jobs[job_name] = log_path

    async def ShowJobs(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        self.smsID.append(update.message.message_id)
        jobs_file = self.home / ".data" / "JOB_status.json"
        with open(jobs_file, 'r') as ffr:
            jobs = json.load(ffr)

        active_jobs = get_active_jobs()
        if len(active_jobs):
            reply_keyboard = [[f'JOB: {job}'] for job in active_jobs][::-1]

            await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
            msg = await update.message.reply_text("Select a job to get updates on",\
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Select the job."\
            ),\
            )
            self.smsID.append(msg.message_id)
        else:
            self.txt = "You have no more running jobs in list."
            await self.sendUpdate(context)
        return 0

    async def StatJobs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        job_name = update.message.text[5:]
        
        jobs_file = self.home / ".data" / "JOB_status.json"
        with open(jobs_file, 'r') as ffr:
            jobs = json.load(ffr)
        #self.jobs = jobs

        logDIR = Path(jobs[job_name]['logDIR'])
        logFILE = jobs[job_name]['logFILE']
        try:
            errFILE = jobs[job_name]['errFILE']
        except:
            errFILE = None
        logIMAGE = jobs[job_name]['logIMAGE']
        try:
            logDICT = jobs[job_name]['logDICT']
        except KeyError:
            logDICT = None
        
        self.txt = self.get_report(outFile = logDIR / logFILE, errFile = logDIR/ errFILE)

        if self.txt is None:
            self.txt = 'No updates found'
            #await self.sendUpdate(context)
            #msg = await context.bot.send_message(chat_id=self.CHATID, text=txt)
            #self.smsID.append(msg.message_id)
        elif logDICT is not None:
            self.txt = self.txt + '\n\n'
            for key, value in logDICT.items():
                self.txt = self.txt + f"*{key}*: {value}\n"
       
        #self.txt = self.txt.replace("_","\\_")
        self.txt = unformat_text(self.txt)
        await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
        msg = await update.message.reply_text(
            self.txt, reply_markup=ReplyKeyboardRemove(),
            parse_mode='MarkdownV2'
        )
        self.smsID.append(msg.message_id)

        try:
            with open(logDIR / logIMAGE, 'rb') as ffrb:
                await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
                msg = await context.bot.send_photo(chat_id=self.CHATID, photo=ffrb)
                self.smsID.append(msg.message_id)
        except:
            pass

        hide_job(job_name)

        return ConversationHandler.END

    def get_report(self, outFile, errFile):
        if outFile is not None:
            outs = tail(outFile,n=5)
        else:
            outs = ''
        if errFile is not None:
            errs = tail(errFile,n=5)
        else:
            errs = ''
        report = f"*Output:*\n{outs}\n\n*Errors:*\n{errs}"
        return report

    def get_last_line0(self, filepath):
        with open(filepath, 'rb') as f:
            # Go to the end of file
            f.seek(0, 2)
            end = f.tell()

            # Step backwards looking for newline
            pos = end - 1
            while pos >= 0:
                f.seek(pos)
                char = f.read(1)
                if char == b'\n' and pos != end - 1:
                    break
                pos -= 1

            # Read from found position to end
            f.seek(pos + 1)
            last_line = f.read().decode('utf-8')
            return last_line.strip()

    def get_last_line(self, filepath):
        if not os.path.exists(filepath):
            return None

        try:
            command_chain = f"tail -n 1000 '{filepath}' | grep -Ev '^\s*$' | tail -n 1"
            process = subprocess.run(command_chain, shell=True, capture_output=True, text=True, check=True)
            
            output = process.stdout.strip()
            if output:
                return output
            else:
                return None

        except subprocess.CalledProcessError as e:
            return None
        except FileNotFoundError:
            return None
        except Exception as e:
            return None

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
        msg = await update.message.reply_text(
        "Keyboard is refreshed!", reply_markup=ReplyKeyboardRemove()
        )
        self.smsID.append(msg.message_id)
        return ConversationHandler.END

    async def EditorBabu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        if len(context.args) == 1:
            file_path = context.args[0]
            if os.path.exists(file_path):
                with open(file_path,'r') as ffr:
                    JsonStr = json.load(ffr)
                encoded_params = urllib.parse.quote(json.dumps(JsonStr))
                file_name = file_path.split('/')[-1]
                extender = f"?variables={encoded_params}&fileNAME={file_name}"
                await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
                msg = await update.message.reply_text(
                    "Editor-Babu is opening the Json file.",
                    reply_markup=ReplyKeyboardMarkup.from_button(
                        KeyboardButton(
                            text="Editor Babu",
                            web_app=WebAppInfo(url="https://pallab-dutta.github.io/EditorBabu"+extender),
                        )
                    ),
                )
                self.smsID.append(msg.message_id)
            else:
                self.txt = f"File {file_path} not Found!"
                await self.sendUpdate(context)
            return ConversationHandler.END
        else:
            JSONfiles = self.get_json_files(".")
            #self.txt = "Expected a JSON file as argument. Nothing provided."
            #await self.sendUpdate(context)
            await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
            if len(JSONfiles):
                msg = await update.message.reply_text("Select a JSON file to edit",\
                    reply_markup=ReplyKeyboardMarkup(JSONfiles, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Select the file."\
                    ),\
                    )
                self.smsID.append(msg.message_id)
                return 2
            else:
                self.txt = f"No JSON file found in the current directory!"
                await self.sendUpdate(context)
                return ConversationHandler.END

    def get_json_files(self, directory):
        json_files = []
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                json_files.append([f"FILE: {filename}"])
        return json_files

    async def SendEditButton(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        #print("I'm here!")
        self.smsID.append(update.message.message_id)
        file_name = update.message.text[6:]
        #print(file_name)
        with open(file_name,'r') as ffr:
            JsonStr = json.load(ffr)
            encoded_params = urllib.parse.quote(json.dumps(JsonStr))
        extender = f"?variables={encoded_params}&fileNAME={file_name}"
        await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
        msg = await update.message.reply_text(
            "Editor-Babu is opening the Json file.",
            reply_markup=ReplyKeyboardMarkup.from_button(
                KeyboardButton(
                    text="Editor Babu",
                    web_app=WebAppInfo(url="https://pallab-dutta.github.io/EditorBabu"+extender),
                    ),
                resize_keyboard=True, one_time_keyboard=True
                ),
            )
        self.smsID.append(msg.message_id)
        return ConversationHandler.END

    async def web_app_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None :
        self.smsID.append(update.message.message_id)
        data = json.loads(update.effective_message.web_app_data.data)
        formname = data['formNAME']
        if formname == 'EditorBabu':
            fileNAME = data['fileNAME']
            del data['formNAME']
            del data['fileNAME']
            if len(data):
                with open(fileNAME, 'r') as ffr:
                    JSdata = json.load(ffr)
                JSdata = {**JSdata, **data}
                with open(fileNAME, 'w') as ffw:
                    json.dump(JSdata, ffw, indent=4)
                #await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
                #msg = await update.message.reply_text(
                #    f"edits are saved to {fileNAME}", reply_markup=ReplyKeyboardRemove()
                #)
                #self.smsID.append(msg.message_id)
                self.txt = f"edits are saved to {fileNAME}"
            else:
                #await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
                #msg = await update.message.reply_text(
                #    f"No new changes! file kept unchanged.", reply_markup=ReplyKeyboardRemove()
                #)
                #self.smsID.append(msg.message_id)
                self.txt = f"No new changes! file kept unchanged."
            await self.sendUpdate(context)
            #return ConversationHandler.END

        #msg = await context.bot.send_message(chat_id=self.CHATID, text=txt)
        #self.smsID.append(msg.message_id)
        #await self.sendUpdate(context)

    async def commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        #cmd2run = ' '.join(context.args) #update.message.text.strip()
        cmd2run = update.message.text.strip()
        cmd0 = cmd2run.split(' ')[0]
        if cmd0[0]=='/':
            print('It came here')
            pass
        elif cmd0=='cd':
            cmd1 = cmd2run[3:]
            try:
                os.chdir(cmd1)
                self.txt=os.popen('pwd').read()
            except:
                self.txt='path not found'
        elif cmd0=='clear':
            self.txt="This clears the terminal screen!\nTo clear telegram screen type /clear"
        elif cmd0=='pkill':
            self.txt="pkill cannot be called."
        else:
            print('command: ',cmd2run)
            cmd=cmd2run
            try:
                self.txt=os.popen('%s'%(cmd)).read()
            except:
                self.txt='error !'
        await self.sendUpdate(context)
        #msg = await context.bot.send_message(chat_id=self.CHATID, text=txt)
        #self.smsID.append(msg.message_id)

    async def ClearChat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        if update.message.text == 'Yes':
            await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
            msg = await update.message.reply_text(
            "Full chat history will be cleared", reply_markup=ReplyKeyboardRemove()
            )
            self.smsID.append(msg.message_id)
            for i in self.smsID:
                try:
                    await context.bot.delete_message(chat_id=self.CHATID, message_id=i)
                except:
                    pass
            
            self.smsID = []
            return ConversationHandler.END
        elif update.message.text == 'No':
            await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
            msg = await update.message.reply_text(
            "Chat history is kept uncleared", reply_markup=ReplyKeyboardRemove()
            )
            self.smsID.append(msg.message_id)
            return ConversationHandler.END

    async def ask2clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        self.smsID.append(update.message.message_id)
        reply_keyboard = [['Yes','No']]
        print(reply_keyboard)
        await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
        msg = await update.message.reply_text("Entire chat history in the current session will be cleared. Proceed?",\
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Select to proceed."\
        ),\
        )
        self.smsID.append(msg.message_id)
        return 1

    async def runjob(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        cmd = f"./{self.runexe}"
        try:
            os.popen('%s'%(cmd))#.read()
            self.txt='job submitted !'
        except:
            self.txt='error !'
        await self.sendUpdate(context)

    async def ask2kill(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        self.smsID.append(update.message.message_id)
        reply_keyboard = [['Yes','No']]
        print(reply_keyboard)
        await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
        msg = await update.message.reply_text("Your job will be killed. Proceed?",\
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="Select to proceed."\
        ),\
        )
        self.smsID.append(msg.message_id)
        return 3

    async def killjob(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        cmd = f"./{self.killexe}"
        try:
            txt = os.popen('%s'%(cmd)).read()
        except:
            txt='error !'

        self.smsID.append(update.message.message_id)
        if update.message.text == 'Yes':
            txt = os.popen('%s'%(cmd)).read()
            await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
            msg = await update.message.reply_text(
            txt, reply_markup=ReplyKeyboardRemove()
            )
        elif update.message.text == 'No':
            await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
            msg = await update.message.reply_text(
            "Your job is not killed.", reply_markup=ReplyKeyboardRemove()
            )
        self.smsID.append(msg.message_id)
        return ConversationHandler.END


class NoteLogs:
    def __init__(self, jobNAME: str, scheduled: bool = False):
        self.home = Path.home()
        self.jobNAME = jobNAME
        self.logDIR = None
        self.logFILE = None
        self.errFILE = None
        self.logIMAGE = None
        self.logDICT = None
        self.scheduled = scheduled

    def write(self, logDIR: str = None, logSTRING: str = None, logFILE: str = 'log_file.out', errFILE: str = 'err_file.out', logIMAGE: str = 'log_image.png'):
        if logDIR is None:
            pwd = Path.cwd()
            _logDIR = pwd / self.jobNAME
            _logDIR.mkdir(exist_ok=True)
        else:
            _logDIR = Path(logDIR)

        if logSTRING is not None:
            with open(_logDIR / logFILE, 'a') as ffa:
                print(f"\n{logSTRING}",file=ffa)

        _logFILE = _logDIR / logFILE
        _errFILE = _logDIR / errFILE
        _logIMAGE = _logDIR / logIMAGE

        logDIR = str(_logDIR)

        #self.jobNAME = f"JOB: {jobNAME}"
        self.logDIR = logDIR
        self.logFILE = logFILE
        self.errFILE = errFILE
        self.logIMAGE = logIMAGE
        self.save_job_JSON()

    def save_job_JSON(self, logDICT: str = None):
        _data = self.home / ".data"
        _data.mkdir(exist_ok=True)
        jobs_file = _data / "JOB_status.json"
        try:
            with open(jobs_file, 'r') as ffr:
                jobs = json.load(ffr)
        except FileNotFoundError:
            jobs = {}
        try:
            jobD = jobs[self.jobNAME]
        except KeyError:
            jobs[self.jobNAME] = {}
            jobD = {}
        if self.logDIR is not None:
            jobD["logDIR"] = self.logDIR
        if self.logFILE is not None:
            jobD["logFILE"] = self.logFILE
        if self.errFILE is not None:
            jobD["errFILE"] = self.errFILE
        if self.logIMAGE is not None:
            jobD["logIMAGE"] = self.logIMAGE
        if logDICT is not None:
            jobD["logDICT"] = logDICT
        jobD["running"] = False
        jobD["status"] = None
        jobD["seen"] = False
        jobD["scheduled"] = self.scheduled
        jobD["stat_sent"] = False
        if len(jobD):
            jobs[self.jobNAME] = jobD
            with open(jobs_file, 'w') as ffw:
                json.dump(jobs, ffw, indent=4)


def register():
    parser = argparse.ArgumentParser(description="I am ChaterJee register, I note your jobs for keeping logs.")
    parser.add_argument("--command",type=str,help="command to run in your terminal")
    parser.add_argument("--jobname",type=str,help="name of the job for logging",required=True)
    parser.add_argument("--logdir",default=None,type=str,help="log directory path")
    parser.add_argument("--logfile",default=None,type=str,help="log file path")
    parser.add_argument("--errfile",default=None,type=str,help="error file path")
    parser.add_argument("--logimage",default=None,type=str,help="log image path")
    parser.add_argument("--schedule",default=False,type=bool,help="Whether to schedule the job")
    args = parser.parse_args()
    logDIR = args.logdir
    if logDIR is None:
        logDIR = Path.cwd() / args.jobname
    elif Path(logDIR) == Path('./'):
        logDIR = Path.cwd()
    else:
        logDIR = Path(logDIR) / args.jobname

    logDIR.mkdir(exist_ok=True)

    if args.logfile is None:
        logFile = f'{args.jobname}_log'
    else:
        logFile = args.logfile

    if args.errfile is None:
        errFile = f'{args.jobname}_err'
    else:
        errFile = args.errfile

    job = NoteLogs(args.jobname, args.schedule)
    job.write(logDIR = logDIR, logFILE = logFile, errFILE = errFile)
    job.save_job_JSON()

    if args.command is not None:
        if args.schedule:
            ToRUN = whether_to_run(args.jobname)
            while not ToRUN:
                time.sleep(5)
                ToRUN = whether_to_run(args.jobname)

        with open(logDIR / logFile, "w") as out, open(logDIR / errFile, "w") as err:
            process = subprocess.Popen(
            [f"{args.command}"],
            stdout=out,
            stderr=err,
            )

        jobs = read_json(jobs_file)
        jobs[args.jobname]['running'] = True
        save_json(jobs_file, jobs)

        process.wait()

        jobs = read_json(jobs_file)
        jobs[args.jobname]['status'] = process.returncode
        save_json(jobs_file, jobs)


def updater():
    parser = argparse.ArgumentParser(description="I am ChaterJee updater, I update your registered project logs.")
    parser.add_argument("token",type=str,help="Enter your telegram-bot TOKEN here")
    parser.add_argument("chatid",type=str,help="Enter your telegram-bot CHATID here")
    args = parser.parse_args()
    cbot = ChatLogs(args.token, args.chatid)
    cbot.cmdTRIGGER()
