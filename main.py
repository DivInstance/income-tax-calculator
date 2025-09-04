import sys
import pyttsx3
import urllib.request
import mysql.connector as mysql
import csv

# ---------------- Database Connection ---------------- #
mycon = mysql.connect(
    host="localhost",
    user="root",
    passwd="toor",
    database="incometax_db"
)

if mycon.is_connected():
    print("Database connection successful")
else:
    print("Connection failed")
    sys.exit()

cursor = mycon.cursor(buffered=True)
mycon.autocommit = True

# Create table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS tax_records(
    ClientID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50),
    Age INT,
    Gender VARCHAR(20),
    SalaryIncome INT,
    PayerType VARCHAR(30),
    AssessmentYear VARCHAR(20),
    HouseIncome INT,
    CapitalGain INT,
    OtherIncome INT,
    BusinessProfit INT,
    AgricultureIncome INT,
    Deductions INT,
    TotalTax INT
) AUTO_INCREMENT=10001
""")

# ---------------- Speech Engine ---------------- #
speaker = pyttsx3.init()
voices = speaker.getProperty('voices')
speaker.setProperty('voice',voices[1].id)
speaker.setProperty('rate',135)

# ---------------- Utility: Internet check ---------------- #
def check_network():
    try:
        urllib.request.urlopen("https://www.google.com/")
        return True
    except:
        return False

# ---------------- Admin Menu ---------------- #

# -------- Main Program --------
print(r""" 
 ************************************************************************************************* 
 *************************************************************************************************
 *************************************************************************************************
 *****                                                                                       *****
 *****  --------   |\        |      |-------   ---------   |\          |\    |-------        *****                                    
 *****     |       | \       |     |          |        \   | \        | \    |               *****
 *****     |       |  \      |     |          |        \   |  \      |  \    |               *****
 *****     |       |   \     |     |          |        \   |   \    |   \    |               *****
 *****     |       |    \    |     |          |        \   |    \  |    \    |-------        *****
 *****     |       |     \   |     |          |        \   |     \|     \    |               *****
 *****     |       |      \  |     |          |        \   |            \    |               *****
 *****     |       |       \ |     |          |        \   |            \    |               *****
 *****  --------   |        \|     \--------  \--------|   |            \    |-------        *****                 
 *****                                                                                       *****
 *****                         Income Tax Calculator Project                                 *****
 *****                          Made by: Divyaranjan Sahoo                                   *****
 *****                                                                                       *****
 ************************************************************************************************* 
 *************************************************************************************************
 *************************************************************************************************
""")


def admin_menu():
    while True:
        print("\n------ Admin Menu ------")
        print("1. View All Records")
        print("2. Search Records")
        print("3. Update Record")
        print("4. Delete Record")
        print("5. Delete Entire Table")
        print("6. Count Records")
        print("0. Exit Admin Menu")

        choice = int(input("Enter your choice: "))

        if choice == 0:
            break

        elif choice == 1:
            cursor.execute("SELECT * FROM tax_records")
            for row in cursor.fetchall():
                print(row)

        elif choice == 2:
            print("Search by: 1.Name  2.Age  3.Gender")
            param = int(input("Enter choice: "))
            if param == 1:
                name = input("Enter Name: ")
                cursor.execute("SELECT * FROM tax_records WHERE Name=%s", (name,))
            elif param == 2:
                age = int(input("Enter Age: "))
                cursor.execute("SELECT * FROM tax_records WHERE Age=%s", (age,))
            elif param == 3:
                gender = input("Enter Gender (Male/Female/Senior): ")
                cursor.execute("SELECT * FROM tax_records WHERE Gender=%s", (gender,))
            print(cursor.fetchall())

        elif choice == 3:
            cid = int(input("Enter ClientID to update: "))
            field = input("Enter field to update (Name, Age, Gender, SalaryIncome, etc.): ")
            value = input("Enter new value: ")
            query = f"UPDATE tax_records SET {field}=%s WHERE ClientID=%s"
            cursor.execute(query, (value, cid))
            mycon.commit()
            print("Record updated successfully")

        elif choice == 4:
            cid = int(input("Enter ClientID to delete: "))
            cursor.execute("SELECT * FROM tax_records WHERE ClientID=%s", (cid,))
            record = cursor.fetchall()
            print("Selected Record:", record)

            confirm = input("Are you sure you want to delete this record? (Yes/No): ")
            if confirm.lower() == "yes":
                cursor.execute("DELETE FROM tax_records WHERE ClientID=%s", (cid,))
                mycon.commit()

                with open("backup_deleted_records.csv", "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerows(record)

                print("Record deleted and backup saved")

        elif choice == 5:
            confirm = input("This will delete all data. Are you sure? (Yes/No): ")
            if confirm.lower() == "yes":
                cursor.execute("DROP TABLE IF EXISTS tax_records")
                mycon.commit()
                print("Entire table deleted")

        elif choice == 6:
            cursor.execute("SELECT COUNT(*) FROM tax_records")
            print("Total Records:", cursor.fetchone()[0])

# ---------------- Tax Calculation ---------------- #
def calculate_tax():
    name = input("Enter Your Name: ")
    age = int(input("Enter Your Age: "))
    gender = input("Enter Gender (Male/Female/Senior): ")
    salary_income = int(input("Enter Income From Salary (After Deduction of ₹50,000): "))
    
    print("\nPayer Types:")
    print("1. Individual\n2. Hindu Undivided Family\n3. Body of Individuals\n4. Firm\n5. Domestic Company\n6. Foreign Company")
    payer_type_input = input("Choose Payer Type (1-6): ")
    
    payer_map = {
        "1": "Individual",
        "2": "HUF",
        "3": "Body of Individuals",
        "4": "Firm",
        "5": "Domestic Company",
        "6": "Foreign Company"
    }
    payer_type = payer_map.get(payer_type_input, "Individual")

    assessment_year = "2024-25"
    house_income = int(input("Enter House Income: "))
    capital_gain = int(input("Enter Capital Gains: "))
    other_income = int(input("Enter Other Income (Lottery/Commission/etc.): "))
    business_profit = int(input("Enter Business Profit: "))
    agriculture_income = int(input("Enter Agricultural Income: "))

    print("\nEnter Deductions:")
    life_insurance = int(input("Life Insurance: "))
    provident_fund = int(input("Provident Fund (PPF): "))
    annuity = int(input("Pension: "))
    medical = int(input("Medical Expenditure: "))

    deductions = min(life_insurance + provident_fund + annuity + medical, 150000)

    # Taxable Income calculation
    if payer_type_input in ["1", "2", "3"]:
        taxable_income = salary_income + house_income + capital_gain + other_income + business_profit + agriculture_income - deductions
    else:
        taxable_income = business_profit  # For firms and companies

    # Tax Slabs for individuals
    total_tax = 0
    if payer_type_input in ["1", "2", "3"]:
        if taxable_income <= 250000:
            total_tax = 0
        elif taxable_income <= 500000:
            total_tax = (taxable_income - 250000) * 0.05
        elif taxable_income <= 750000:
            total_tax = 12500 + (taxable_income - 500000) * 0.10
        elif taxable_income <= 1000000:
            total_tax = 37500 + (taxable_income - 750000) * 0.15
        elif taxable_income <= 1250000:
            total_tax = 75000 + (taxable_income - 1000000) * 0.20
        elif taxable_income <= 1500000:
            total_tax = 125000 + (taxable_income - 1250000) * 0.25
        else:
            total_tax = 187500 + (taxable_income - 1500000) * 0.30

        # Add capital gains & business profit tax
        total_tax += (capital_gain * 0.30) + (business_profit * 0.30)
    else:
        total_tax = business_profit * 0.30  # Companies/Firms flat 30%

    print(f"\n{name}, your Taxable Income = ₹{taxable_income}")
    print(f"Total Tax Payable = ₹{int(total_tax)}")
    print("Thank you for using Income Tax Calculator! Visit again.")

    # Insert into database
    cursor.execute("""
    INSERT INTO tax_records 
    (Name, Age, Gender, SalaryIncome, PayerType, AssessmentYear, HouseIncome,
     CapitalGain, OtherIncome, BusinessProfit, AgricultureIncome, Deductions, TotalTax)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (name, age, gender, salary_income, payer_type, assessment_year,
          house_income, capital_gain, other_income, business_profit,
          agriculture_income, deductions, int(total_tax)))
    mycon.commit()

# ---------------- Main Program Loop ---------------- #
while True:
    print("\nWelcome to Income Tax Calculator")
    speaker.say("Welcome to Income Tax Calculator, please chose your option from the menu")
    speaker.runAndWait()
    print("1. Admin Login")
    print("2. Client Login")
    print("3. Exit Program")
    

    login = input("Enter Your Choice: ")

    if login == "3":
        print("Exiting program. Have a good day ahead!")
        break
    elif login == "1":
        pw = input("Please Enter Admin Password (Password is admin): ")
        if pw == "admin":
            print("Welcome Admin!")
            admin_menu()
        else:
            print("Wrong Password!")
    elif login == "2":
        calculate_tax()
    else:
        print("Invalid Choice. Try again.")
