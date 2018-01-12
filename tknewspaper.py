__VERSION__ = 1.1


from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tinydb import *
from simplecrypt import encrypt, decrypt
import datetime, os, getpass, shutil

'''
Creates a Snapshot backup of the encrypted file in the "Snapshots" folder
This is so we can have incremental backups in case there is a file loss
or file corruption.
'''
def backup(file):
    date = str(datetime.datetime.today()).replace(":", ".").split(" ")
    if not os.path.exists("Snapshot"):
        os.mkdir("Snapshot")
    if not os.path.exists("Snapshot/{}".format(date[0])):
        os.mkdir("Snapshot/{}".format(date[0]))
    date = "__{} {}.json".format(date[0], date[1][:8])
    path = "Snapshot/{}/{}".format(str(datetime.date.today()), file.split('.')[0] + date)
    open(path, "a").close()
    shutil.copy(file, path)


'''
Read the encrypted data by decrypting the data
then writing the plain text onto the original file
this will let TinyDB to read the files
'''
def readencrypted(password, filename):
    print("Unlocking files")
    with open(filename, 'rb') as input:
        global plaintext
        ciphertext = input.read()
        plaintext = decrypt(password, ciphertext)
        plaintext = plaintext.decode('utf8')
    with open(filename, 'w') as file:
        file.write(plaintext)

'''
Read the plaintext file and encrypt the text
after which we store the encrypted text back in to the file
This will keep the data secured when not in use.
'''
def writeencrypted(password, filename):
    print("Locking files")
    global plaintext
    with open(filename, 'r') as text:
        plaintext = text.read()
    with open(filename, 'wb') as output:
        ciphertext = encrypt(password, plaintext)
        output.write(ciphertext)

'''
If the root (Window) is closing prompts the user
to wait a bit, as the program encrypts the files
after which you are prompted with success and the root is destroyed
'''
def onquit():
    messagebox.showinfo("Info", "Stay put Saving data")
    writeencrypted(password, "people.json")
    writeencrypted(password, "newspaper.json")
    messagebox.showinfo("Info","Saving Complete")
    root.destroy()


global db, newsdb
FILES = ["people.json", "newspaper.json"]
password = getpass.getpass("Password: ")


for file in FILES:
    if os.path.exists(file):
        backup(file)
        try:
            readencrypted(password, file)
        except:
            db = TinyDB("people.json")
            newsdb = TinyDB("newspaper.json")
    else:
        open(file, 'w+')
        writeencrypted(password, file)
        readencrypted(password, file)

db = TinyDB("people.json")
newsdb = TinyDB("newspaper.json")


class AppEntry(Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.paidfor = IntVar()
        self.name = StringVar()
        self.address = StringVar()
        self.paperName = StringVar()
        self.paperPrice = DoubleVar()
        self.satPaperPrice = DoubleVar()
        self.sunPaperPrice = DoubleVar()
        self.paydays = IntVar()
        self.paydays.set(0)
        self.totalprice = 0.0
        self.datedifference = 0.0
        self.newsname = ""
        self.comboname = ""
        self.daynames = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.weeklist = []
        for i in range(7):
            self.weeklist.append(BooleanVar())
        self.masterframe = Frame(self.master)
        self.createwidgets()
        root.focus_set()

    '''
    Clears all the values in the newspaper section Entries
    '''
    def clearnewsvar(self):
        self.paperName.set("")
        self.paperPrice.set("")
        self.satPaperPrice.set("")
        self.sunPaperPrice.set("")

    '''
    Reset the week list. This is mainly used in exception handling
    and initialisation
    '''
    def weekreset(self):
        for i in range(7):
            self.weeklist[i].set(False)

    '''
    Clears the mainframe of the root so that we can redraw new widgets
    this will allow the program to operate in a single screen.
    '''
    def clearwidgets(self, back=True):
        self.masterframe.destroy()
        self.masterframe = Frame(self.master)
        self.masterframe.grid()

        if back:
            Button(self.masterframe, text="Back", command=self.createwidgets).grid(row=9)

    '''
    Create all the widgets for the main menu such as 
    submitting data viewing data and newspaper date.
    '''
    def createwidgets(self, clear=True):
        if clear:
            self.clearwidgets(back=False)

        Label(self.masterframe, text="Newspapers V.{}".format(__VERSION__)).grid(row=0)

        labelframe = LabelFrame(self.masterframe, text="Options")

        Button(labelframe, text="Deliveries", command=self.datawidgets).grid(row=1, columnspan=2, sticky="n")
        Button(labelframe, text="Newspapers", command=self.newspaperwidgets).grid(row=2, columnspan=2)
        Button(labelframe, text="New Customers", command=self.editwidgets).grid(row=3, columnspan=2)

        labelframe.grid(row=1, ipadx=5, ipady=5, padx=10, columnspan=2)

    '''
    Get the data that is search for
    Using the value recieved from the Combobox 
    retrieve all the necessary data and insert it to the appropriate fields
    '''
    def getdata(self, event):
        data = newsdb.all()[self.combobox.current()]

        self.paperName.set(data["Name"])
        self.paperPrice.set(data["Normal Price"])
        self.satPaperPrice.set(data["Saturday Price"])
        self.sunPaperPrice.set(data["Sunday Price"])

    '''
    Push the data back to the json.
    If the data is exist then replace using confirmation
    otherwise simply enter new data
    '''
    def sendnewspaperdata(self):
        if str(self.paperName.get().lower())not in self.readdata('Name', True, database=newsdb):
            newsdb.insert({'Name': self.paperName.get(), 'Normal Price': self.paperPrice.get(),
                           'Saturday Price': self.satPaperPrice.get(), 'Sunday Price': self.sunPaperPrice.get()})
            self.clearnewsvar()
            self.newspaperwidgets()
        else:
            response = messagebox.askquestion('Data exists', "Data already exists, would you like it to be replaced ?")
            if response == "yes":
                newsdb.update({'Name': self.paperName.get(), 'Normal Price': self.paperPrice.get(),
                               'Saturday Price': self.satPaperPrice.get(), 'Sunday Price': self.sunPaperPrice.get()},
                              doc_ids=[self.getid(self.combobox)])

    '''
    If data already exist then delete that data using
    confirmation otherwise state that there is nothing to
    delete. 
    '''
    def deletenewspaperdata(self):
        if messagebox.askyesno("Confirmation", "Are you sure you want to delete '{}' data".format(newsdb.get(doc_id=self.getid(self.combobox))["Name"])):
            newsdb.remove(doc_ids=[self.getid(self.combobox)])
            self.clearnewsvar()
            self.newspaperwidgets()
        else:
            pass

    '''
    Widgets for the newspaper window
    all of the gui elements should be located here.
    When an item is selected via combo box the "getdata" function will get called
    When "Delete" button is pressed the deletenewspaperdata function will get called
    when "Submit" button is pressed the sendnewspaperdata function will get called
    '''
    def newspaperwidgets(self, clear=True):
        if clear:
            self.clearwidgets()

        labelframe = LabelFrame(self.masterframe, text="Data")

        Label(labelframe, text='Paper Name: ').grid(row=0, column=2, sticky="w")
        Entry(labelframe, textvariable=self.paperName).grid(row=0,column=3)

        Label(labelframe, text="Price").grid(row=1, column=2, sticky="w")
        Entry(labelframe, textvariable=self.paperPrice).grid(row=1, column=3)

        Label(labelframe, text="Saturday Price").grid(row=2, column=2, sticky="w")
        Entry(labelframe, textvariable=self.satPaperPrice).grid(row=2, column=3)

        Label(labelframe, text="Sunday Price").grid(row=3, column=2, sticky="w")
        Entry(labelframe, textvariable=self.sunPaperPrice).grid(row=3, column=3)

        labelframe.grid(row=0, column=1, ipady=3)

        labelframe = LabelFrame(self.masterframe, text="Buttons")

        Button(labelframe, text="Submit", command=self.sendnewspaperdata).grid(row=4, column=3, sticky='e')
        Button(labelframe, text="Delete",command=self.deletenewspaperdata).grid(row=4, column=4, sticky='w')
        labelframe.grid(row=1,column=1, sticky="e")
        
        labelframe = LabelFrame(self.masterframe, text="Newspaper")

        self.combobox = Combobox(labelframe, values=self.readdata('Name', False, newsdb))
        self.combobox.grid(row=0)
        self.combobox.bind("<<ComboboxSelected>>", self.getdata)

        labelframe.grid(row=0, padx=5, ipady=3, sticky="n")

    '''
    Creates all the widgets for the submit application.
    Such as Name label and entry and so on...
    '''
    def editwidgets(self, clear=True):
        if clear:
            self.clearwidgets()

        labelframe = LabelFrame(self.masterframe, text="Data")

        self.nameLabel = Label(labelframe, text="Full Name:").grid(row=0)
        self.nameEntry = Entry(labelframe, textvariable=self.name).grid(row=0, column=1)

        self.addressLabel = Label(labelframe, text="Address:").grid(row=1)
        self.addressEntry = Entry(labelframe, textvariable=self.address).grid(row=1, column=1)

        labelframe.grid(row=0)

        labelframe = LabelFrame(self.masterframe, text="Button")

        self.submit = Button(labelframe, text="Submit", command=self.submitbutton).grid(row=0, column=2, padx=5)

        labelframe.grid(row=0, column=1, padx=3, sticky="n")

    '''
    Reads the desired Key of data in the database
    and then returns all the values for that desired field
    '''
    def readdata(self, nameofdata, lower, database=db):
        if lower == True:
            return [str(data[nameofdata]).lower() for data in database.all()]
        else:
            return [data[nameofdata] for data in database.all()]

    '''
    Submits data after checking it and clears the entry fields.
    The checks include checking if the data is already present and
    if the entry fields are not empty
    '''
    def submitbutton(self):
        if self.name.get() != '' and self.address.get() != '':
            if str(self.name.get()).lower() not in self.readdata('Name', True) or str(self.address.get()).lower() not in self.readdata('Address', True):
                db.insert({"Name": self.name.get(), "Address": self.address.get()})
                self.editwidgets()
                self.name.set('')
                self.address.set('')
            else:
                messagebox.showerror("Error", "Data already in the database")

    '''
    Creates the widgets for the deliveries.
    Using Label frames to create a neat layout which should look
    similar on all platforms.
    '''
    def datawidgets(self, clear=True):
        if clear:
            self.clearwidgets()

        labelframe = LabelFrame(self.masterframe)

        Label(labelframe, text="Paper").grid(row=0)

        self.newscombo = Combobox(labelframe, values=self.readdata("Name", True, database=newsdb))
        self.newscombo.bind("<<ComboboxSelected>>", self.setnewsname)
        self.newscombo.set(self.newsname)
        self.newscombo.grid(row=0, column=1, sticky="w")

        Label(labelframe, text="Address").grid(row=1)

        self.combobox = Combobox(labelframe, values=self.readdata("Address", False))
        self.combobox.bind("<<ComboboxSelected>>", self.updatedata)
        self.combobox.set(self.comboname)
        self.combobox.grid(row=1, column=1, sticky="w")

        labelframe.grid(row=0, padx=5, ipadx=2, ipady=2)

        labelframe = LabelFrame(self.masterframe, text="Total")

        Label(labelframe, text="{:0.2f}".format(self.totalprice)).grid(row=0)

        labelframe.grid(row=1, column=0, padx=10, sticky="w")

        labelframe = LabelFrame(self.masterframe, text="Pay Due in")

        Label(labelframe, text=self.datedifference).grid(row=0)

        labelframe.grid(row=1, column=0)


        labelframe = LabelFrame(self.masterframe, text="Buttons")

        Button(labelframe, text="Submit", command=self.datasubmit).grid(row=0, column=7, sticky='s')
        Button(labelframe, text="Delete", command=self.datadelete).grid(row=0, column=4, columnspan=3, sticky='se')
        Button(labelframe, text="Pay", command=self.paybillwidgets).grid(row=0, column=8, columnspan=3)

        labelframe.grid(row=1, column=1)


    '''
    Sets a global variable of a newspaper name which is selected.
    '''
    def setnewsname(self, event):
        self.newsname = self.newscombo.get()

    '''
    Gets the ID of the selected field by using regex and then
    stores this value which can be accessed by any other function
    that will need it. The variable stays the same until a new field
    is selected
    '''
    def getid(self, box, database=newsdb):
        return database.all()[box.current()].doc_id

    '''
    Alternative way of calling getid this is for bind event in tkinter
    as they do require an addition argument so that you can call a function.
    Aswell as needing to link the json files in the same window.
    '''
    def getidalt(self, event):
        self.getid(self.combobox)

    '''
    Update the list by checking the json file and retrieving 
    data of the appropriate user
    '''
    def updateweeklist(self):
        try:
            for i in range(len(self.daynames)):
                if not self.userdata[str(self.newsname+self.daynames[i])]:
                    self.weeklist[i].set(False)
                elif KeyError:
                    self.weeklist[i].set(True)
        except KeyError:
            self.weekreset()

    '''
    Update the checkbox for the appropriate user after
    getting their id and corresponding week values
    '''
    def updatedata(self, event):
        self.comboname = self.combobox.get()
        self.datedifference = str(self.getdate(outscope=True, key="PaidTill"))[:10]
        self.userdata = db.get(doc_id=self.getid(self.combobox, database=db))

        self.calculateprice()

        if self.newscombo.get() == "":
            messagebox.showerror("Error", "No newspaper Selected")

        else:
            self.updateweeklist()
            labelframe = LabelFrame(self.masterframe, text="Days")
            for i in range(len(self.weeklist)):
                Checkbutton(labelframe, text=i + 1, variable=self.weeklist[i], onvalue=True,
                          offvalue=False).grid(row=0, column=i, sticky='nw')
            labelframe.grid(row=0, column=1, padx=10)
            self.datawidgets(clear=False)

    '''
    Calculates the Price that is either in credit or is due
    for the currently selected user.
    '''
    def calculateprice(self):
        try:
            credit = False
            totalprice = 0
            diff = self.getdate(outscope=True, key="PaidTill") - datetime.datetime.today()
            data = db.get(doc_id=self.getid(self.combobox, database=db))
            newspapernames = self.readdata("Name", False, database=newsdb)

            if diff.days >= 0:
                credit = True

            diff = abs(diff.days)
            for newsname in newspapernames:
                for i in range(diff + 1):
                    dayname = self.daynames[(i + datetime.datetime.today().weekday()) % 7]
                    try:
                        if data[newsname.lower() + dayname]:
                            if dayname == "Saturday":
                                totalprice += float(newsdb.get(where("Name") == newsname)["Saturday Price"])
                            elif dayname == "Sunday":
                                totalprice += float(newsdb.get(where("Name") == newsname)["Sunday Price"])
                            else:
                                totalprice += float(newsdb.get(where("Name") == newsname)["Normal Price"])
                    except Exception:
                        pass
            if credit:
                self.totalprice = totalprice
            else:
                self.totalprice = -totalprice

        except Exception:
            self.totalprice = 0

    '''
    Gets a date from the json file. Depending if "outscope" is false or true
    it will give you the paid on date or the paid till date
    default value for outscope is false
    '''
    def getdate(self, outscope=False, key="PaidOn"):
        if not outscope:
            try:
                return(datetime.datetime.strptime(self.paydata["PaidTill"], "%Y-%m-%d"))
            except KeyError:
                return None
        else:
            try:
                return(datetime.datetime.strptime(db.get(doc_id=self.getid(self.combobox, database=db))[key], "%Y-%m-%d"))
            except KeyError:
                return None

    '''
    Generates the necissary widgets for the pay bill window
    uses labelframe to order eveyrything in a neat order
    '''
    def paybillwidgets(self, clear=True):
        self.paydata = db.get(doc_id=self.getid(self.combobox, database=db))
        if clear:
            self.clearwidgets()

        labelframe = LabelFrame(self.masterframe, text="Data")

        Label(labelframe, text="Pay for").grid(row=0, column=0)
        Entry(labelframe, width=5, textvariable=self.paydays).grid(row=0, column=1)
        Label(labelframe, text="Days").grid(row=0, column=2)

        labelframe.grid(row=0, padx=5, pady=5)

        labelframe = LabelFrame(self.masterframe, text="Button")

        Button(labelframe, text="Submit", command=self.paybuttonsubmit).grid(row=0)

        labelframe.grid(row=0, column=1)

    '''
    Calculates the date difference and returns date
    in the following format: YEAR-MONTH-DAY
    '''
    def countdatediff(self, date):
        paytill = str(date + datetime.timedelta(days=int(self.paydays.get())))
        return datetime.datetime.strptime(paytill[:10], "%Y-%m-%d")

    '''
    Submit the date stamps to the appropriate user.
    PaidOn key shows when the person has last payed
    PaidTill key show when the next payment is due
    if you pay before PaidTill expires you will add ontop of the paid till
    if you are late then you will be paying back for the days missed.
    '''
    def paybuttonsubmit(self):

        if not self.getdate():
            date = datetime.date.today()
            ndate = str(self.countdatediff(date))
            db.update({"PaidOn": str(date)[:10], "PaidTill": ndate[:10]}, doc_ids=[self.paydata.doc_id])
        else:
            date = self.getdate()
            ndate = str(self.countdatediff(date))
            db.update({"PaidOn": str(date)[:10], "PaidTill": ndate[:10]}, doc_ids=[self.paydata.doc_id])

        messagebox.showinfo("Success", "Data has been updated")
        self.datawidgets()
        self.updatedata(None)

    '''
    Submits the week data to the json file so that it can be stored 
    permanently for that user
    '''
    def datasubmit(self):
        for i in range(len(self.weeklist)):
            db.update({str(self.newsname+self.daynames[i]): self.weeklist[i].get()}, doc_ids=[self.userdata.doc_id])
        messagebox.showinfo("Success", "Data has been updated")

    '''
    Deletes the selected data from the json file and after which
    the window is updated to represent the changes
    '''
    def datadelete(self):
        if messagebox.askyesno("Confirmation", "Are you sure you want to delete {} record ?".format(self.userdata["Address"])):
            db.remove(doc_ids=[self.userdata.doc_id])
        self.datawidgets(clear=False)


root = Tk()
app = AppEntry(master=root)
root.protocol("WM_DELETE_WINDOW", onquit)
app.mainloop()

