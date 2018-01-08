__VERSION__ = 0.4

'''
TO DO:
    *** Verification for data entered in the newspaper entries
    * Fix Combobox on datawidgets
    * Newspapers data communicates with the customer fields.
    * getid function and corresponding connections change to combobox and then move the get data id retrieve
      line from getdata function in to separate a function
'''

from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tinydb import *

db = TinyDB('people.json')
newsdb = TinyDB('newspaper.json')

class AppEntry(Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.name = StringVar()
        self.address = StringVar()
        self.paperName = StringVar()
        self.paperPrice = DoubleVar()
        self.satPaperPrice = DoubleVar()
        self.sunPaperPrice = DoubleVar()
        self.selectedcombovalue = StringVar().set("search News paper")
        self.daynames = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.weeklist = []
        for i in range(7):
            self.weeklist.append(BooleanVar())
        self.masterframe = Frame(self.master)
        self.createwidgets()

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
    def clearwidgets(self):
        self.masterframe.destroy()
        self.masterframe = Frame(self.master)
        self.masterframe.grid()

        Button(self.masterframe, text="Back", command=self.createwidgets).grid(row=9)

    '''
    Create all the widgets for the main menu such as 
    submitting data viewing data and newspaper date.
    '''
    def createwidgets(self, clear=True):
        if clear:
            self.clearwidgets()

        Label(self.masterframe, text="Newspapers V.{}".format(__VERSION__)).grid(row=0)
        Button(self.masterframe, text="Deliveries", command=self.datawidgets).grid(row=1)
        Button(self.masterframe, text="Newspapers", command=self.newspaperwidgets).grid(row=2)
        Button(self.masterframe, text="New Customers", command=self.editwidgets).grid(row=3)

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
        if str(self.paperName.get().lower() )not in self.readdata('Name', True, database=newsdb):
            newsdb.insert({'Name' : self.paperName.get(), 'Normal Price' : self.paperPrice.get(),
                           'Saturday Price' : self.satPaperPrice.get(), 'Sunday Price' : self.sunPaperPrice.get() })
            self.clearnewsvar()
            self.newspaperwidgets()
        else:
            response = messagebox.askquestion('Data exists', "Data already exists, would you like it to be replaced ?")
            if response == "yes":
                newsdb.update({'Name': self.paperName.get(), 'Normal Price': self.paperPrice.get(),
                               'Saturday Price': self.satPaperPrice.get(), 'Sunday Price': self.sunPaperPrice.get()},
                                doc_ids=[self.getid()])

    '''
    If data already exist then delete that data using
    confirmation otherwise state that there is nothing to
    delete. 
    '''
    def deletenewspaperdata(self):
        newsdb.remove(doc_ids=[self.getid()])
        self.clearnewsvar()
        self.newspaperwidgets()

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

        Label(self.masterframe, text='Paper Name: ').grid(row=0, column=2)
        Entry(self.masterframe, textvariable=self.paperName).grid(row=0,column=3)

        Label(self.masterframe, text="Price").grid(row=1, column=2)
        Entry(self.masterframe, textvariable=self.paperPrice).grid(row=1, column=3)

        Label(self.masterframe, text="Saturday Price").grid(row=2, column=2)
        Entry(self.masterframe, textvariable=self.satPaperPrice).grid(row=2, column=3)

        Label(self.masterframe, text="Sunday Price").grid(row=3, column=2)
        Entry(self.masterframe, textvariable=self.sunPaperPrice).grid(row=3, column=3)

        Button(self.masterframe, text="Submit", command=self.sendnewspaperdata).grid(row=4, column=3, sticky='e')
        Button(self.masterframe, text="Delete",command=self.deletenewspaperdata).grid(row=4, column=3, sticky='w')

        self.combobox = Combobox(self.masterframe, values=self.readdata('Name', True, newsdb))
        self.combobox.grid(row=0)
        self.combobox.bind("<<ComboboxSelected>>", self.getdata)

    '''
    Creates all the widgets for the submit application.
    Such as Name label and entry and so on...
    '''
    def editwidgets(self, clear=True):
        if clear:
            self.clearwidgets()

        self.nameLabel = Label(self.masterframe, text="Full Name:").grid(row=0)
        self.nameEntry = Entry(self.masterframe, textvariable=self.name).grid(row=0, column=1)

        self.addressLabel = Label(self.masterframe, text="Address:").grid(row=1)
        self.addressEntry = Entry(self.masterframe, textvariable=self.address).grid(row=1, column=1)

        self.submit = Button(self.masterframe, text="Submit", command=self.submitbutton).grid(row=0, column=2, padx=5)

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
    Creates the widgets for the dataWindow 
    '''
    def datawidgets(self, clear=True):
        if clear:
            self.clearwidgets()

        self.combobox = Combobox(self.masterframe, values=self.readdata("Address", False))
        self.combobox.bind("<<ComboboxSelected>>", self.getidalt)
        self.combobox.grid(row=0)

        Button(self.masterframe, text="Submit", command=self.datasubmit).grid(row=0, column=7, sticky='s')
        Button(self.masterframe, text="Delete", command=self.datadelete).grid(row=0, column=4, columnspan=3, sticky='se')

    '''
    Gets the ID of the selected field by using regex and then
    stores this value which can be accessed by any other function
    that will need it. The variable stays the same until a new field
    is selected
    '''
    def getid(self):
        return newsdb.all()[self.combobox.current()].doc_id

    def getidalt(self, event):
        self.getid()

    '''
    Update the list by checking the json file and retrieving 
    data of the appropriate user
    '''
    def updateweeklist(self):
        self.userdata = db.get(doc_id=self.dataid)
        try:
            for i in range(len(self.daynames)):
                if not self.userdata[self.daynames[i]]:
                    self.weeklist[i].set(False)
                elif KeyError:
                    self.weeklist[i].set(True)
        except KeyError:
            self.weekreset()

    '''
    Update the checkbox for the appropriate user after
    getting their id and corresponding week values
    '''
    def updatedata(self):
        self.updateweeklist()
        for i in range(len(self.weeklist)):
            Checkbutton(self.dataWindow, text=i + 1, variable=self.weeklist[i], onvalue=True,
                        offvalue=False).grid(row=0, column=i + 1, sticky='nw')

    '''
    Submits the week data to the json file so that it can be stored 
    permanently for that user
    '''
    def datasubmit(self):
        for i in range(len(self.weeklist)):
            db.update({str(self.daynames[i]): self.weeklist[i].get()}, doc_ids=[int(self.dataid)])

    '''
    Deletes the selected data from the json file and after which
    the window is updated to represent the changes
    '''
    def datadelete(self):
        if messagebox.askyesno("Confirmation", "Are you sure you want to delete {} record ?".format(self.userdata['Name'])):
            db.remove(doc_ids=[self.dataid])
        self.datawidgets(clear=False)


root = Tk()
app = AppEntry(master=root)

app.mainloop()
