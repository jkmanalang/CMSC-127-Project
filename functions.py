import mysql.connector
import datetime

mydb = mysql.connector.connect(host="localhost", user="group1", passwd="group1pass", database="task_record")
mycursor = mydb.cursor()

def getUserAnswer():
	try:
		user_answer = input ("Choice: ")
	except:
		print ("\nInvalid input.")
	return user_answer

def getIntInput(min_range, max_range, needed_input):
	while True:
		try:
			userInput = int (input (needed_input + " [" + str(min_range) + "-" + str(max_range) + "]: "))
			while min_range > userInput or userInput > max_range:
				userInput = int (input (needed_input + " [" + min_range + "-" + max_range + "]: "))
			break
		except:
			print("\nEnter integer within the given range only.")
	return userInput

def getHighestCategoryNo():
	select_maxCategoryNo = "SELECT MAX(categoryNo) FROM category"
	mycursor.execute(select_maxCategoryNo)

	for i in mycursor:
		highest = i
		break
	
	if highest[0]==None:
		return 0
	return (highest[0])

def getHighestTaskNo():
	select_maxTaskNo = "SELECT MAX(taskNo) FROM task"
	mycursor.execute(select_maxTaskNo)

	for i in mycursor:
		highest = i
		break
	
	if highest[0]==None:
		return 0
	return (highest[0])

def getAllCategories():
	get_categories = "SELECT * FROM category"
	mycursor.execute(get_categories)

	categories = []

	for i in mycursor:
		categories.append(i)

	return categories

def getAllTasks():
	get_tasks = "SELECT * FROM task"
	mycursor.execute(get_tasks)

	tasks = []
	for i in mycursor:
		tasks.append(i)
		
	return tasks

def getAllCategoriesAndTasks():
	# join every task with their category and storing it to 'tasks' list
	select_categoriesWithTask = "SELECT * FROM category a NATURAL JOIN task b"
	mycursor.execute(select_categoriesWithTask)
	tasks = []

	for i in mycursor:
		tasks.append(i)

	return tasks

def isTasksEmpty():
	if getHighestTaskNo()!=0:
		return 1
	print("\n\t[NO TASKS YET]\n\n")
	return 0

def isCategoryEmpty():
	if getHighestCategoryNo()!=0:
		return 1
	print("\n\t[NO CATEGORIES YET]\n\n")
	return 0

# to print all categories
def showListOfCategories():
	categories = getAllCategories()

	for i in categories:
		print("   [" + str(i[0]) + "] " + i[1])

# to print status choices. can also give status in dictionary form
def showTaskStatus():
	status_dict = {1:"NOT YET STARTED",
	2:"IN-PROGRESS", 3:"MISSED",
	4:"COMPLETED"}

	for x, y in status_dict.items():
		print("   [" + str(x) + "] " + y)

	return status_dict

def showCategoryTypes():
	cType_dict = {1:"Personal",
	2:"Professional",
	3:"Others"
	}

	for x, y in cType_dict.items():
		print("   [" + str(x) + "] " + y)

	return cType_dict	

def viewByDayMonth(statement):
	get_taskOrderedByDueDate = statement
	mycursor.execute(get_taskOrderedByDueDate)

	# this will just be needed for printing purposes only
	status_dict = {1:"NOT YET STARTED",
	2:"IN-PROGRESS", 3:"MISSED",
	4:"COMPLETED"}

	tasks = []

	for i in mycursor:
		tasks.append(i)

	counter = 0

	while counter < len(tasks):
		print(tasks[counter][0])
		nextTask = 0
		
		while (counter+nextTask) < len(tasks):
			if (tasks[counter+nextTask][0] == tasks[counter][0]):
				print("   " + str(counter+nextTask+1) + ") " + tasks[counter+nextTask][2], end="")
				# this if-else is just for aligning the strings
				if (tasks[counter+nextTask][2] == status_dict.get(2) or tasks[counter+nextTask][2] == status_dict.get(1)): print("\t" + tasks[counter+nextTask][3] + " ~ " + tasks[counter+nextTask][1])
				else : print("\t\t" + tasks[counter+nextTask][3] + " ~ " + tasks[counter+nextTask][1])
				nextTask += 1
				continue
			break

		counter += nextTask

# this automatically sets the status as 'MISSED' or as the default 'NOT YET STARTED' based on the current status and due date
def autoMissedUnMissed():
	sql = "UPDATE task SET taskStatus='MISSED' WHERE dueDate < CURDATE()"
	mycursor.execute(sql)
	mydb.commit()
	
	sql = "UPDATE task SET taskStatus='NOT YET STARTED' WHERE taskStatus='MISSED' AND dueDate>CURDATE()"
	mycursor.execute(sql)
	mydb.commit()

# this updates the taskNos of the remaining tasks after category deletion
def updateTaskNos():
	if isTasksEmpty():
		task= getAllTasks()

		counter=1

		for i in task:
			if i[0] != counter:
				sql = "UPDATE task SET taskNo=%s WHERE taskNo=%s"
				num = (counter,i[0])
				mycursor.execute(sql,num)
				mydb.commit()
			counter =counter+1

# [0] View Task (all)
def showTasks():
	print("\n----------------------------- Viewing tasks -----------------------------")

	print("""
   [1] View by category
   [2] View by day
   [3] View by month""")

	user_choice = getIntInput(1, 3, "View by:")

	print("\n")

	if user_choice == 1:
		print("==== viewing by category ====")
		# join every task with their category and storing it to 'tasks' list
		categoryAndTask = getAllCategoriesAndTasks()

		# getting category list
		categories = getAllCategories()

		# printing categories together with their tasks
		counter = 1
		status_dict = {1:"NOT YET STARTED",
		2:"IN-PROGRESS", 3:"MISSED",
		4:"COMPLETED"}
		for i in categories:
			print(str(counter) + ") " + i[1])
			for j in categoryAndTask:
				if(i[0] == j[0]):	# using datetime library to convert date to string
					print("\t[" + j[4].strftime("%m/%d/%Y") + "]\t\t" + j[6], end="")
					# this if-else is just for aligning the strings
					if (j[6] == status_dict.get(2) or j[6] == status_dict.get(1)): print("\t\t" + j[5])
					else : print("\t\t\t" + j[5])
			# print("\n")
			counter += 1

	elif user_choice == 2:
		print("==== viewing by day ====")
		viewByDayMonth("SELECT DATE_FORMAT(a.dueDate, '%M %d, %Y'), a.details, a.taskStatus, b.categoryName FROM task AS a NATURAL JOIN category AS b ORDER BY a.dueDate")

	else:
		print("==== viewing by month ====")
		viewByDayMonth("SELECT DATE_FORMAT(a.dueDate, '%M %Y'), a.details, a.taskStatus, b.categoryName FROM task AS a NATURAL JOIN category AS b ORDER BY a.dueDate")

# [1] Add/Create task
# creates a new task and assign it to an existing category
def createTask():
	# Add task to an existing category
	print("\n----------------------------- Add task -----------------------------")

	categories = getAllCategories()

	if isCategoryEmpty():
		# shows all existing categories
		print("Category_no\tCategory_name")
		for i in categories:
			print(str(i[0])+"\t\t"+i[1])
		
		category_num= getIntInput(1,getHighestCategoryNo(), "Add task to category_no")
		cName = categories[category_num-1][1]
	
		while True:
			task_details = input("Task details: ")
			if task_details!="":
				break

		# limit year to 50 years from now
		task_dueDate_year = getIntInput(2022,2072,"Due date(year)")	
		task_dueDate_month = getIntInput(1,12,"Due date(month)")

		#to specifically limit number of days in the selected month	
		mon31= [1,3,5,7,8,10,12]
		dateNumMax= 0
		if task_dueDate_month==2:
			dateNumMax = 28
			if task_dueDate_year%4==0:
				dateNumMax= 29
		elif task_dueDate_month in mon31:
			dateNumMax=31
		else:
			dateNumMax=30
		task_dueDate_day = getIntInput(1,dateNumMax,"Due date(day)")	
		
		taskno = getHighestTaskNo()+1
		data= (taskno,category_num,task_dueDate_day, task_dueDate_month, task_dueDate_year ,task_details)
		sql = "INSERT INTO task(taskNo, categoryNo, dueDate, details) VALUES(%s,%s, STR_TO_DATE('%s-%s-%s','%d-%m-%Y'), %s)"

		try:
			mycursor.execute(sql,data)
			mydb.commit()
			autoMissedUnMissed()
			print("New task was added to ",cName, " successfully!")
		except:
			print("Adding task failed")	

# [2] Edit Task
def editTask():
	print("\n----------------------------- Editing Task -----------------------------")
	if isTasksEmpty():
		print("Which task you want to edit?")

		# getting category with its tasks tuple
		categoryAndTask = getAllCategoriesAndTasks()

		# getting taskNo of the task to be edited
		for i in categoryAndTask:
			print("\t[" + str(i[3]) +"] " + i[5] + " (Category: " + i[1] + ")")	
		userChoice = getIntInput(1, getHighestTaskNo(), "Task")

		# continues editing of values until user wishes to end
		while(True):
			categoryAndTask = getAllCategoriesAndTasks()

			# getting which attribute to edit
			print("\nChoose what you want to edit")
			for i in categoryAndTask:
				if(userChoice == i[3]):
					print("\t[1] Details: " + i[5])
					print("\t[2] Deadline: " + i[4].strftime("%m/%d/%Y"))
					print("\t[3] Status: " + i[6])
					print("\t[0] Exit")
			editChoice = getIntInput(0, 3, "Choice")

			# updating the database
			if(editChoice == 1):
				while True:
					value = input ("New task name: ")
					if (value != ""): break
					print("Name must not be empty\n")

				mycursor.execute("UPDATE task SET details=%s WHERE taskNo=%s", (value, userChoice))
				mydb.commit()

				print("Task name successfully edited!")

			elif(editChoice == 2):

				task_dueDate_year = getIntInput(2022, 2072, "Due date (year)")
				task_dueDate_month = getIntInput(1, 12, "Due date (month)")
				#to specifically limit number of days in the selected month	
				mon31= [1,3,5,7,8,10,12]
				dateNumMax= 0
				if task_dueDate_month==2:
					dateNumMax = 28
					if task_dueDate_year%4==0:
						dateNumMax= 29
				elif task_dueDate_month in mon31:
					dateNumMax=31
				else:
					dateNumMax=30

				day = getIntInput(1, dateNumMax, "Due date (day)")


				mycursor.execute("UPDATE task SET dueDate='%s/%s/%s' WHERE taskNo=%s", (task_dueDate_year, task_dueDate_month, day, userChoice))
				mydb.commit()
				autoMissedUnMissed()

				print("Task due date successfully edited!")

			elif(editChoice == 3):
				status_dict = showTaskStatus()
				status = getIntInput(1, 4, "Status")

				for x, y in status_dict.items():
					if (x == status):
						mycursor.execute("UPDATE task SET taskStatus=%s WHERE taskNo=%s", (y, userChoice))
						mydb.commit()
						break

				print("Task status successfully edited!")

			else: break
			print("\n")

# [3] Delete Task
# deletes task of the chosen task no, decrements taskNos of the affected tasks
def deleteTask():
	print("\n----------------------------- delete task -----------------------------")
	category_task = getAllCategoriesAndTasks()
	if isTasksEmpty():
		for i in category_task:
			print("\t"+str(i[3])+".\t["+i[1]+"] "+i[5]+"\t........"+i[6]+ " (due: "+i[4].strftime("%m/%d/%Y")+")")


		task_no = getIntInput(1,getHighestTaskNo(),"Delete task_no ")

		print("The deleted data will not be retrieved. Proceed with deletion? \n[Press [y] to delete, press any key to cancel]")
		go = input()

		if go=='y':	
			sql="DELETE FROM task WHERE taskno=" + str(task_no)
			mycursor.execute(sql)
			mydb.commit()
			print("Task_no ",task_no," deleted succesfully!")

			# to decrement taskNo of all tasks above the deleted task, 
			# ensures that there are no missing tasks in 1-max(taskNo), all taskNo in options exist
			sql= "UPDATE task SET taskNo = taskNo-1 WHERE taskno>"+str(task_no)
			mycursor.execute(sql)
			mydb.commit()
			print("Tasks task_number updated!")

		else:
			print("Deleting task cancelled")

# [4] Mark task as done
# allows the user to set the status of the task as 'DONE'
def markAsDone():
	print("\n----------------------------- mark as done -----------------------------")
	category_task = getAllCategoriesAndTasks()

	if isTasksEmpty():
		for i in category_task:
			print("\t"+str(i[3])+".\t["+i[1]+"] "+i[5]+"\t........"+i[6]+ " (due: "+i[4].strftime("%m/%d/%Y")+")")

		task_no = getIntInput(1,getHighestTaskNo(),"Mark as done task_no ")
		
		sql="UPDATE task SET taskStatus='DONE' WHERE taskno=" + str(task_no)
		mycursor.execute(sql)
		mydb.commit()
		print("Task status updated!")

# [5] Add category
def addCategory():
	print("\n----------------------------- Adding Category -----------------------------")

	# getting category name
	categoryName = input("Category name: ")

	# getting category type
	print ("""													
   [1] Personal
   [2] Professional
   [3] Others""")

	categoryTypeNo = getIntInput(1,3,"Category type")
	if (categoryTypeNo == 1):
		categoryType = "Personal"
	elif (categoryTypeNo == 2):
		categoryType = "Professional"
	else:
		categoryType = "Others"

	categoryno = getHighestCategoryNo()+1
	# inserting to database
	insertCategoryStatement = "INSERT INTO category (categoryNo, categoryName, categoryType) VALUES (%s,%s, %s)"
	values = (categoryno, categoryName, categoryType)
	
	mycursor.execute(insertCategoryStatement, values)

	mydb.commit()
	print("Category " + categoryName + " successfully added!")

# [6] Edit category
def editCategory(): #Function to edit the Category's name and type
	print("\n----------------------------- Editing Category -----------------------------")
	print("Which category do you want to edit?")
	
	if isCategoryEmpty():
		categories = getAllCategories()

		for i in categories: #Choosing which Category to edit
			print("\t[" + str(i[0]) + "] " + i[1] )
		userChoice = getIntInput(1, getHighestCategoryNo(), "Category")

		while(True): #Choosing what function to do to the Category
			categories = getAllCategories()
			print("\nChoose what you want to edit")
			for i in categories:
				if(userChoice == i[0]):
					print("\t[1] Name: " + i[1])
					print("\t[2] Type: " + i[2])
					print("\t[0] Exit")
			editChoice = getIntInput(0, 2, "Choice")

			if (editChoice == 1): #Edits the Category name 
				while True:
					value = input ("New category name: ")
					if (value != ""): break
					print("Name must not be empty\n")
				mycursor.execute("UPDATE category SET categoryName=%s WHERE categoryNo=%s", (value, userChoice))
				mydb.commit()

				print("Category name successfully edited!")

			elif (editChoice == 2): #Edits the Category type
				cType_dict = showCategoryTypes()
				cType = getIntInput(1, 3, "Category type")

				for x, y in cType_dict.items():
					if (x == cType):
						mycursor.execute("UPDATE category SET categoryType=%s WHERE categoryNo=%s", (y, userChoice))
						mydb.commit()
						break	

				print("Category type successfully edited!")

			else: #Stops the function
				break
				print("\n")

# [7] Delete category
# deletes category of the chosen categoryNo, decrements category no of the affected categories and tasks
def deleteCategory():
	print("\n----------------------------- delete category -----------------------------")
	
	if isCategoryEmpty():
		category_task = getAllCategoriesAndTasks()	
		categories= getAllCategories()
		mycursor.execute("SELECT DISTINCT(categoryNo), COUNT(taskNo) FROM task GROUP BY categoryNo")

		numoftask = []
		for i in mycursor:
			numoftask.append(i)

		distinct_cat=[]
		# prints categories with tasks
		for i in categories:
			for j in numoftask:
				if i[0]==j[0] and i[1] not in distinct_cat:
					print("\t"+str(i[0])+".\t"+i[1]+" ["+str(j[1])+" tasks]")
					distinct_cat.append(i[1])
		
		# prints categories with tasks
		for i in categories:
			if i[1] not in distinct_cat:
				print("\t"+str(i[0])+".\t"+i[1]+" [empty]")
				distinct_cat.append(i[1])

		cat_no = getIntInput(1,getHighestCategoryNo(),"Delete category_no")

		print("List of tasks in category_no ",cat_no)
		for i in category_task:
			if i[0]==cat_no:
				print("\t[" + i[6] + "] "+ i[5] +" (due: "+i[4].strftime("%m/%d/%Y")+")")
		
		print("Deleting a category also deletes all tasks in the category. Proceed with deletion? \n[Press [y] to delete, press any key to cancel]")
		go = input()

		if go=='y':	
			# creates temporary table that stores all category_task that is above the category that will be deleted
			createTempCat = "CREATE TABLE tempcat AS SELECT * FROM category WHERE categoryNo>"+str(cat_no)
			createTempTask = "CREATE TABLE temptask AS SELECT * FROM task WHERE categoryNo>"+str(cat_no)
			mycursor.execute(createTempCat)
			mycursor.execute(createTempTask)
			mydb.commit()

			# decrement all categoryNo values
			mycursor.execute("UPDATE tempcat SET categoryNo= categoryNo-1")
			mycursor.execute("UPDATE temptask SET categoryNo= categoryNo-1")
			mydb.commit()

			# deletes rows that has categoryNo greater than or equal to the selected categoryNo
			deletetasks = "DELETE FROM task WHERE categoryNo >="+str(cat_no)
			deletecat = "DELETE FROM category WHERE categoryNo >="+str(cat_no)
			mycursor.execute(deletetasks)
			mycursor.execute(deletecat)
			mydb.commit()


			# insert all data from the temporary table
			mycursor.execute("INSERT INTO category(categoryNo, categoryName, categoryType) SELECT * FROM tempcat")
			mycursor.execute("INSERT INTO task(taskNo, categoryNo, dueDate, details, taskStatus) SELECT * FROM temptask")
			mydb.commit()

			# deletes temporary table
			mycursor.execute("DROP TABLE tempcat")
			mycursor.execute("DROP TABLE temptask")
			mydb.commit()
			
			updateTaskNos()
			print("Category_no ",cat_no," and tasks inside deleted successfully!")
			print("Category_task updated!")

		else:
			print("Deleting category cancelled")

# [8] View category
def viewCategory():
	autoMissedUnMissed()
	print("\n----------------------------- Viewing Category -----------------------------")
	
	if isCategoryEmpty():
		# getting which category to view
		print("Which category you want to view?")
		categories = getAllCategories()
		for i in categories:
			print("\t[" + str(i[0]) + "] " + i[1])
		userChoice = getIntInput(1, getHighestCategoryNo(), "Category")

		print("\n")

		# printing category attributes together with its tasks available
		for i in categories:
			if (i[0] == userChoice):
				print("Category name: " + i[1])
				print("Category type: " + i[2])

		status_dict = {1:"NOT YET STARTED",
		2:"IN-PROGRESS", 3:"MISSED",
		4:"COMPLETED"}

		print("Task/s:")
		tasks = getAllTasks()
		counter = 0
		for i in tasks:
			if(i[1] == userChoice):
				print("\t[" + i[2].strftime("%m/%d/%Y") + "]\t\t" + i[4], end="")
				# this if-else is just for aligning the strings
				if (i[4] == status_dict.get(2) or i[4] == status_dict.get(1)): print("\t\t" + i[3])
				else : print("\t\t\t" + i[3])
				counter += 1

		if(counter == 0):
			print("\t [no task yet]")
	
# [9] Move task to category
def addTaskToCategory():
	print("Select task to move: ")

	# getting category with its tasks tuple
	categoryAndTask = getAllCategoriesAndTasks()

	# getting taskNo of the task to be moved
	for i in categoryAndTask:
		print("\t[" + str(i[3]) +"] " + i[5] + " (Category: " + i[1] + ")")	
	user_choice_task = getIntInput(1, getHighestTaskNo(), "Task")

	print("\nSelect category to move selected task to: ")
	categories = getAllCategories()
	for i in categories:
		print("\t[" + str(i[0]) + "] " + i[1])
	user_choice_categ = getIntInput(1, getHighestCategoryNo(), "Category")

	mycursor.execute("UPDATE task SET categoryNo=%s WHERE taskNo=%s", (user_choice_categ, user_choice_task))
	mydb.commit()
	print("\nTask successfully moved.")