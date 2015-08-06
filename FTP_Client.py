import os
import sys
import platform
import socket
from ftplib import FTP

def grablines(line='', lines=[]):
		if (line):
			lines.append(line)
		else:
			result = lines[:]
			del lines[:]
			return result

def popLastDir(path, slash):
	path = path.split(slash)
	path.pop(-2)
	path = slash.join(path)
	return path

class PSP_FTP():
	def cls(self):
		os.system(['clear','cls'][os.name == 'nt'])

	def downloadFile(self, localDir, serverFileName):
		passed = True

		name = serverFileName[serverFileName.rfind(self.remoteDirSlash)+1:]

		print "Downloading " + name + "..."
		try:
			outFile = open(localDir + name, "wb")
		except:
			print "Error 19 (downloadFile): Could not make local file, insufficent permissions or file exsists and is locked."
			passed = False
		if (outFile > 0):
			try:
				self.server.retrbinary('RETR ' + serverFileName, outFile.write)
				print "File downloaded."
			except socket.timeout:
				print "Error 26 (downloadFile): Server connection timedout, you will need to reconnect."
				self.server.close()
				passed = False
			except:
				print "Error retreving file from server."
				passed = False
			outFile.close()
			if passed == False:
				os.remove(localDir + name)
		return passed
	
	def downloadFilePrompt(self, serverFileName):
		print "Where would you like to save the file: "
		try:
			localDir = os.getcwd() + self.localDirSlash
		except socket.timeout:
			print "Error 38 (downloadFilePrompt): Server connection timedout, you will need to reconnect."
			self.server.close()
			return False
		localDirDone = False
		lastKnownGood = localDir
		while (localDirDone == False):
			validDir = True
			print localDir
			try:
				localDirFull = os.listdir(localDir)
			except:
				print "Error 233: " + localDir + " may be a broken link or you do not have permissions to it."
				localDirFull = []
				validDir = False
			if (validDir == True):
				localDirFiltered = self.localDirList(localDir, localDirFull, True)
				if (localDirFiltered == "Empty"):
					print "There are no folders in " + localDir
				lastKnownGood = localDir
			print "Enter in 'N' to make a new directory here,"
			print "Enter in 'P' to go to previous directory,"
			print "Enter in 'R' to refresh this directory,"
			print "Enter in 'Q' to cancel downloading file,"
			print "Enter in desired directory number to go to that directory,"
			if (validDir == True):
				temp3 = raw_input("Enter in 'H' to download to this directory: ")
			else:
				temp3 = raw_input("Enter in 'B' to go back to last directory you had premissions in, or use 'P' to continue going back to try another directory tree: ")
			if ((temp3 == 'h') or (temp3 == 'H')):
				## transfer the file
				valid = self.downloadFile(localDir, serverFileName)
				if (valid == False):
					return False
				fileGood = True
				localDirDone = True
			elif ((temp3 == 'b') or (temp3 == 'B')):
				os.chdir(lastKnownGood)
				localDir = lastKnownGood
			elif ((temp3 == 'n') or (temp3 == 'N')):
				newDir = raw_input("Enter in new directory name: ")
				os.mkdir(localDir+newDir)
				localDir += newDir
			elif ((temp3 == 'p') or (temp3 == 'P')):
				localDir = popLastDir(localDir, self.localDirSlash)
			elif ((temp3 == 'r') or (temp3 == 'R')):
				print "Refreshing..."
			elif ((temp3 == 'q') or (temp3 == 'Q')):
				localDirDone = True
			else :
				if temp3.isdigit():
					if ((int(temp3) > 0) and (int(temp3) <= len(localDirFiltered))):
						localDir += localDirFiltered[int(temp3)-1]
						localDir += self.localDirSlash
					else:
						print "Error 276: invalid number selection."
				else:
					print "Error 278: invalid selection input."
	
	def downloadFolderPrompt(self, serverFolderName):
		print "Where would you like to save the folder: "
		localDir = os.getcwd() + self.localDirSlash
		localDirDone = False
		lastKnownGood = localDir
		while (localDirDone == False):
			validDir = True
			print localDir
			try:
				os.chdir(localDir)
				localDirFull = os.listdir(localDir)
			except:
				print localDir + " may be a broken link or you do not have permissions to it."
				localDirFull = []
				validDir = False
			if (validDir == True):
				lastKnownGood = localDir
				self.localDirList(localDir, localDirFull)
			print "Enter in 'N' to make a new directory here,"
			print "Enter in 'P' to go to previous directory,"
			print "Enter in 'R' to refresh this directory,"
			print "Enter in 'Q' to cancel downloading the folder,"
			print "Enter in desired directory number to go to that directory,"
			if (validDir == True):
				temp3 = raw_input("Enter in 'H' to download to this directory: ")
			else:
				temp3 = raw_input("Enter in 'B' to go back to last directory you had permissions in, or use 'P' to continue going back to try another directory tree: ")
			if ((temp3 == 'h') or (temp3 == 'H')):
				## transfer the file
				print "Getting a list of the files and folders, may take a while..."
				files = self.traverse(serverFolderName)
				if (files == -1):
					return -1
				for file in files:
					print "File to get: " + file
					fileName = file[file.rfind(self.remoteDirSlash)+1:]
					dirToCheck = file[0:file.rfind(self.remoteDirSlash)+1]
					dirExsists = os.path.isdir(localDir+dirToCheck)
					if (dirExsists == True):
						os.chdir("./"+dirToCheck+'/')
						self.downloadFile(localDir[:len(localDir)-1]+dirToCheck, file)
					else:
						dirsToMake = dirToCheck.split(self.remoteDirSlash)
						dirsToMake.pop(0)
						dirsToMake.pop(len(dirsToMake)-1)
						tempDir = localDir
						for dir in dirsToMake:
							alreadyExists = os.path.isdir(dir)
							if (alreadyExists == False):
								os.mkdir(dir)
							os.chdir(dir)
							tempDir += dir + self.localDirSlash
						self.downloadFile(localDir[:len(localDir)-1]+dirToCheck, file)
					os.chdir(localDir)
				fileGood = True
				localDirDone = True
			elif ((temp3 == 'b') or (temp3 == 'B')):
				os.chdir(lastKnownGood)
				localDir = lastKnownGood
			elif ((temp3 == 'n') or (temp3 == 'N')):
				newDir = raw_input("Enter in new directory name: ")
				os.mkdir(localDir+newDir)
				localDir += newDir
			elif ((temp3 == 'p') or (temp3 == 'P')):
				localDir = popLastDir(localDir, self.localDirSlash)
			elif ((temp3 == 'r') or (temp3 == 'R')):
				print "Refreshing..."
			elif ((temp3 == 'q') or (temp3 == 'Q')):
				localDirDone = True
			else :
				if temp3.isdigit():
					if ((int(temp3) > 0) and (int(temp3) <= len(localDirFull))):
						localDir += localDirFull[int(temp3)-1]
						localDir += self.localDirSlash
						print localDir
					else:
						print "Error, invalid number selection."
				else:
					print "Error, invalid selection input."

	def localDirList(self, localDir, localFileNames, returnDirs=False):
		passed = True
		if (returnDirs == True):
			localFoldersOnly = []
			try:
				for line in localFileNames :
					if os.path.isdir(localDir+line) == True:
						localFoldersOnly.append(line)
			except:
				print "Error 90: in filtering for just local directories."
				passed = False
			if (len(localFoldersOnly) > 0):
				for entry in range(0,len(localFoldersOnly)):
					print str(entry+1).rjust(2,' ') + " : Directory : " + localFoldersOnly[entry]
				return localFoldersOnly
			else:
				passed = "Empty"
		else:
			if (len(localFileNames) > 0):
				for entry in range(0,len(localFileNames)):
					try:
						if (os.path.isdir(localDir+localFileNames[entry])):
							print str(entry+1).rjust(2,' ') + " : Directory : " + localFileNames[entry]
						else:
							period = localFileNames[entry].rfind('.')
							if (period != -1):
								ext = localFileNames[entry][period+1:]
								ext = ext.upper()
							else :
								ext = "None"
							ext = ext.ljust(9,' ')
							print str(entry+1).rjust(2,' ') + " : " + ext + " : " + localFileNames[entry]
					except:
						print "Error 114: determining local directories from local files and extensions."
						passed = False
			else:
				print "There are no files/folders here."
			passed = False
		return passed

	def remoteDirList(self, serverFiles, serverFileNames):
		ignores = [ "$RECYCLE.BIN", ".DS_Store", ".TemporaryItems", '.', '..' ]
		passed = True
		if (len(serverFiles) > 0):
			for line in ignores:
				try:
					slot = serverFileNames.index(line)
					serverFiles.pop(slot)
					serverFileNames.pop(slot)
				except:
					pass
			total = len (serverFiles)
			spaces = 1
			while (total > 10):
				total = total / 10
				spaces += 1
			for entry in range(0,len(serverFiles)):
				# try:
					if ((serverFiles[entry][0] == 'd') or (serverFiles[entry][0] == 'D')):
						print str(entry+1).rjust(spaces,' ') + " : Directory : " + serverFileNames[entry]
					else:
						period = serverFiles[entry].rfind('.')
						if (period != -1):
							ext = serverFiles[entry][period+1:]
							ext = ext.upper()
						else:
							ext = "None"
						ext = ext.ljust(9,' ')
						print str(entry+1).rjust(spaces,' ') + " : " + ext + " : " + serverFileNames[entry]
				# except:
					# print "Error 73: Directory list information is malformed and not able to be printed."
		else:
			print "There are no files/folders here."
			passed = False
		return passed

	def get_data(self, dirToGet):
		if (dirToGet[0] == '/'):
			dirToGet = dirToGet[1:]
		try:
			curDir = str(self.server.pwd())
		except socket.timeout:
			print "Error 17 (get_data): Server connection timedout, you will need to reconnect."
			server.close()
		if (curDir == '/'):
			pass
		elif (curDir[len(curDir)-1] != '/'):
			curDir += '/'
		print "Current Dir: " + curDir
		print "Directory to check: " + dirToGet
		dir = 0
		files = 1
		passed = True
		full = [[],[]]
		try:
			self.server.cwd(dirToGet)
			self.server.dir(grablines)
			dirToGet_FullList = grablines()
			self.server.retrlines("NLST", grablines)
			dirToGet_FullListName = grablines()
		except socket.timeout:
			print "Error 29 (get_data): Server connection timedout, you will need to reconnect."
			server.close()
		except:
			print "Error 29 (get_data): getting remote directories and files names from server."
			passed = False
		if (passed == True):
			try:
				slot = dirToGet_FullListName.index("$RECYCLE.BIN")
				dirToGet_FullList.pop(slot)
				dirToGet_FullListName.pop(slot)
			except Exception: 
				pass
			for entry in range(0, len(dirToGet_FullList)):
				if (dirToGet_FullList[entry][0] == 'd'):
					full[dir].append(dirToGet_FullListName[entry])
				elif (dirToGet_FullListName[entry][0] != '.'):
					full[files].append(curDir+dirToGet+dirToGet_FullListName[entry])
			while (len(full[dir]) > 0):
				print "Directories to check: " + str(len(full[dir]))
				print "Going deeper into: " + full[dir][0]
				data = get_data(self.server, full[dir][0]+self.remoteDirSlash)
				print "Returned back a level..."
				full[dir].pop(0)
				for entry in data[files]:
					full[files].append(entry)
			self.server.cwd("..")
		return full
		
	def traverse(self, dirToGet):
		passed = True
		try:
			self.server.cwd("..")
			data = get_data(self.server, dirToGet)
		except socket.timeout:
			print "Error 69 (traverse): Server connection timedout, you will need to reconnect."
			server.close()
			passed = False
		if (data == False):
			passed = False
		else:
			passed = data[1]
		return passed
		
	def traverse2(self, dirToGet):
		print dirToGet
		raw_input("Continue?")
		dir = 0
		files = 1
		passed = True
		full = [[],[]]
		try:
			self.server.cwd(dirToGet)
			self.server.dir(grablines)
			dirToGet_FullList = grablines()
			self.server.retrlines("NLST", grablines)
			dirToGet_FullListName = grablines()
		except:
			print "Error 22 (Traverse): getting remote directories and files names from server."
			passed = False
		if (passed == True):
			try:
				slot = dirToGet_FullListName.index("$RECYCLE.BIN")
				dirToGet_FullList.pop(slot)
				dirToGet_FullListName.pop(slot)
			except Exception: 
				pass
			for entry in range(0, len(dirToGet_FullList)):
				if (dirToGet_FullList[entry][0] == 'd'):
					full[dir].append(dirToGet_FullListName[entry])
				elif (dirToGet_FullListName[entry][0] != '.'):
					temp = dirToGet_FullListName[entry]
					full[files].append(temp)
			if (len(full[dir]) > 0):
				baseDir = self.remoteDirSlash
				while ((len(full[dir]) > 0) and (passed == True)):
					self.server.cwd(full[dir][0])
					baseDir += full[dir][0] + remoteDirSlash
					try:
						self.server.dir(grablines)
						dirToGet_FullList = grablines()
					except:
						print "Error 44 (traverse): Failed to get directory listing, usually from a network drop-age."
						passed = False
					if (passed == True):
						try:
							self.server.retrlines("NLST", grablines)
							dirToGet_FullListName = grablines()
						except:
							print "Error 51 (traverse): Failed to get directory listing names, usually from a network drop-age."
							passed = False
						if (passed == True):
							for entry in range(0, len(dirToGet_FullList)):
								if (dirToGet_FullList[entry][0] == 'd'):
									full[dir].append(baseDir[1:] + dirToGet_FullListName[entry])
								elif (dirToGet_FullListName[entry][0] != '.'):
									full[files].append(baseDir[1:] + dirToGet_FullListName[entry])
							try:
								full[dir].pop(0)
								baseDir = remoteDirSlash
								ftp.cwd(dirToGet)
							except:
								print "Error 67 (traverse): failed to reset the working directory, usually from a network drop-age."
								passed = False
			if (passed == True):
				for index in range(0, len(full)):
					print dirToGet + full[files][index]
					full[files][index] = dirToGet + full[files][index]
				passed = full
		return passed

	def uploadFile(self, localDir, localFile):
		passed = True
		print "Uploading file..."
		print localDir + localFile
		try:
			inFile=open(localDir+localFile, "rb")
			try:
				self.server.storbinary('STOR ' + localFile, inFile)
				print "File downloaded."
			except:
				print "Error 132: Upload of " + localFile + " failed."
				passed = False
			inFile.close()
		except:
			print "Error 136: Could not open file to upload insufficent permissions or file is locked."
			passed = False
		return passed

	def uploadFilePrompt(self):
		print "Where would you like to save the file: "
		localUploadDone = False
		localDir = os.getcwd() + self.localDirSlash
		while (localUploadDone == False):
			print localDir
			try:
				localDirFull = os.listdir(localDir)
			except:
				print "Error: " + localDir + " may be a broken shortcut or you do not have permission to access this folder."
				localDir = popLastDir(localDir, self.localDirSlash)
			for index in range(0,len(localDirFull)):
				if (os.path.isdir(localDir+localDirFull[index]) == True):
					print str(index+1).rjust(2, ' ') + " : Directory : " + localDirFull[index]
				else:
					period = localDirFull[index].rfind('.')
					if (period != -1):
						ext = localDirFull[index][period+1:]
						ext = ext.upper()
					else:
						ext = "None"
					ext = ext.ljust(9,' ')
					print str(index+1).rjust(2,' ') + " : " + ext + " : " + localDirFull[index]
			print "Enter in a directory number,"
			print "Enter in 'Back' to go to previous directory,"
			print "Enter in 'Refresh' to refresh this directory,"
			print "Enter in 'Quit' to cancel uploading a file,"
			temp3 = raw_input("Enter in a file number to upload: ")
			if (temp3.lower() == 'back'):
				localDir = popLastDir(localDir, self.localDirSlash)
			elif (temp3.lower() == 'refresh'):
				print "Refreshing..."
			elif (temp3.lower() == 'quit'):
				localUploadDone = True
			elif (temp3.isdigit()):
				if ((int(temp3) > 0) and (int(temp3) <= len(localDirFull))):
					temp3 = int(temp3)-1
					if (os.path.isdir(localDir+localDirFull[temp3]) == True):
						localDir += localDirFull[temp3]
						localDir += self.localDirSlash
					else:
						localUploadDone = uploadFile(server, localDir, localDirFull[temp3])
				else:
					print "Error, invalid choice."
			else:
				print "Did not enter a valid choice."

	def pspBypass(self):
		print "Renaming PSP to PSP2"
		self.server.rename("/PSP", "/PSP2")
		if self.serverDir.startswith("/PSP/"):
			tempDir = "/PSP2/" + self.serverDir[4:]
			self.server.cwd(tempDir)
			self.serverDir = self.server.pwd()
		self.psp = True

	def pspReset(self):
		print "Renaming PSP2 to PSP"
		self.server.rename("/PSP2", "/PSP")
		if self.serverDir.startswith("/PSP2/"):
			tempDir = "/PSP/" + self.serverDir[5:]
			self.server.cwd(tempDir)
			self.serverDir = self.server.pwd()
		self.psp = False

	def menu(self, serverFileName):
		fileGood = False
		while (fileGood == False):
			print "1 : Rename " + serverFileName
			print "2 : Download " + serverFileName
			print "3 : Delete " + serverFileName
			print "4 : Exit"
			temp2 = raw_input("Enter in selection: ")
			# Make a new folder on the server
			if (int(temp2) == 1) :
				loopRename = False
				while (loopRename == False):
					newName = raw_input("Enter in new name with file extension: ")
					period = newName.rfind('.')
					if ((period == -1) or (period == len(newName)-1)):
						noExtOkay = raw_input("No extension was added, enter 'Y' to confirm: " + newName + " : ")
						if ((noExtOkay == 'y') or (noExtOkay == 'Y')):
							try:
								self.pspBypass()
								self.server.rename(serverFileName, newName)
								self.pspReset()
							except Exception:
								print "Error 38 (Menu): server rejected or failed to rename the file."
							loopRename = True
							fileGood = True
					else:
						try:
							self.pspBypass()
							self.server.rename(serverFileName, newName)
							self.pspReset()
						except Exception:
							print "Error 38 (Menu): server rejected or failed to rename the file."
						loopRename = True
						fileGood = True
			# Download entry
			elif (int(temp2) == 2):
				valid = self.downloadFilePrompt(serverFileName)
				if (valid == False):
					return False
			# Delete server file
			elif (int(temp2) == 3):
				error = False
				try:
					self.pspBypass()
					deleted = self.server.delete(serverFileName)
					self.pspReset()
				except socket.timeout:
					print "Error 59 (menu): Server connection timedout, you will need to reconnect."
					server.close()
					return 59
				except Exception:
					print "Error 57 (menu): server rejected or failed to delete the file."
					error = True
				if (deleted == "error_perm"):
					print "Error, you do not have the permission to delete " + serverFileName
				elif (deleted == "error_reply"):
					print "Error, file is in use."
				elif (error == False):
					print "Delete " + serverFileName
				fileGood = True
			# Exit the menu and perform no action
			elif (int(temp2) == 4):
				fileGood = True
			else:
				print "Error, invalid input."

	def printDirectory(self):
		print "Directory: " + self.serverDir
		# Get directory's list with info
		try:
			self.server.dir(grablines)
			self.serverFiles = grablines()
		except socket.timeout:
			print "Error 132 (main): Server connection timed-out, you will need to reconnect."
			self.server.close()
			return
		except Exception:
			print "Error communicating directory contents."
			self.server.close()
			return
		# Variables for control
		self.serverFilesCount = len(self.serverFiles)
		
		self.serverFileNames = []
		for line in self.serverFiles:
			self.serverFileNames.append(line[line.rfind(' ')+1:])

		# Print out the directory's content, indicating directory from file (plus extension)
		# Checking if the directory is empty
		if (len(self.serverFiles) == 0):
			print "No files or folders here."
		else:
			#Print the directory menu
			self.remoteDirList(self.serverFiles, self.serverFileNames)

	def establishConnection(self):
		print "Enter in server address (Example: ftp.home.com:21),"
		host = raw_input("Enter in 'Q' to quit: ")
		if (host == 'q' or host == 'Q'):
			print "Quitting..."
			return False

		colon = host.rfind(':')
		if (colon != -1):
			port = int(host[colon+1:])
		else:
			port = 21

		self.server = FTP()

		try:
			print "Establishing active connection..."
			self.server.set_pasv(False)
			self.server.connect(host, port)
		except:
			print "Could not connect to server address."
			return False

		print "Connection established."
		return True

	def mainMenu(self):
		# Variables for control
		loop = True

		# Selection loop
		while (loop == True):
			self.cls()
			self.printDirectory()
			print "Enter in the number for a file/folder,"
			print "Enter in 'rename' to change the current folders name,"
			print "Enter in 'download' to download this entire directory,"
			print "Enter in 'new' to make a new folder,"
			print "Enter in 'upload' to upload a file to this directory,"
			print "Enter in 'back' to go to previous directory,"
			print "Enter in 'refresh' to refresh this directory,"
			print "Enter in 'delete' to delete current directory,"
			print "Enter in 'PSP2' to set up folder,"
			print "Enter in 'PSP' to set up folder"
			temp = raw_input("Enter in 'quit' to quit: ")

			# User quits
			if (temp[0].lower() == 'q'):
				if self.psp == True:
					self.pspReset()
				quit = True
				loop = False

			elif (temp.lower() == 'download'):
				print "Call: " + self.remoteDirSlash
				self.downloadFolderPrompt()
				
			elif (temp.lower() == 'delete'):
				self.pspBypass()
				print "Deleting " + self.serverDir + "..."
				self.server.cwd('..')
				dirs = self.serverDir.split(self.remoteDirSlash)
				self.server.rmd(dirs[len(dirs)-2])
				self.serverDir = self.server.pwd()
				self.pspReset()
				
			elif (temp.lower() == 'rename'):
				loopRename = False
				while (loopRename == False):
					newName = raw_input("Enter in new folder name: ")
					if newName == 'q' or newName == 'Q':
						loopRename = True
					elif len(newName) > 0:
						try:
							self.pspBypass()
							dirs = self.serverDir.split(self.remoteDirSlash)
							dirs.pop(0)
							dirs.pop(len(dirs)-1)
							self.server.cwd('..')
							oldFolderName = dirs[len(dirs)-1]
							self.server.rename(oldFolderName, newName)
							self.server.cwd(newName)
							self.serverDir = server.pwd()
							self.pspReset()
						except Exception:
							print "Error 38 (Menu): server rejected or failed to rename the file."
					else:
						print "Did not enter anything? Enter in 'Q' to exit."
				
			elif (temp.upper() == 'PSP2'):
				self.pspBypass()
				
			elif (temp.upper() == 'PSP'):
				self.pspReset()

			# User goes up a directory
			elif (temp[0].lower() == 'b'):
				backupDir = self.serverDir
				# try:
				tempDir = self.serverDir.split('/')
				tempDir.pop(len(tempDir)-2)
				self.serverDir = '/'.join(tempDir)
				print self.serverDir
				self.server.cwd(self.serverDir)
				# except socket.timeout:
				# 	print "Error 184 (main): Server connection timedout, you will need to reconnect."
				# 	server.close()
				# 	return
				# except Exception:
				# 	print "Error 184 (main): Server did not change directory."
				# 	self.serverDir = backupDir

			# User wants to make a new directory
			elif (temp[0].lower() == 'n'):
				newDir = raw_input("Enter in new directory name: ")
				self.pspBypass()
				self.server.mkd(newDir)
				self.serverDir += newDir + self.remoteDirSlash
				self.server.cwd(newDir)
				self.pspReset()

			#user wants to upload a local file
			elif (temp[0].lower() == 'u'):
				self.uploadFilePrompt(self.localDirSlash)

			#user wants to refresh the directory
			elif (temp.lower() == 'refresh'):
				self.cls()
				print "Refreshing..."
			else:
				if temp.isdigit():
					# Check if the number entered is in the acceptable entries
					if ((int(temp) >= 1) and (int(temp) <= self.serverFilesCount)):
						# Since now we know its an acceptable entry but it has a value 1 higher then the array so we adjust
						temp = int(temp) - 1
						# Check if the selected entry is a directory, if so move the server into it
						if ((self.serverFiles[temp][0] == 'd') or (self.serverFiles[temp][0] == 'D')):
							self.server.cwd(self.serverFileNames[temp])
							self.serverDir += self.serverFileNames[temp] + self.remoteDirSlash
						# Since it is not a folder we want to give a menu
						else:
							valid = self.menu(self.serverFileNames[temp])
					else:
						print "You entered an invalid numerical choice."
				else:
					print "You did not enter a valid option."

	def __init__(self):
		error = False
		try :
			systemName = platform.system()
			if ((systemName == "Darwin") or (systemName == "Linux")):
				self.localDirSlash = "/"
			elif ((systemName == "Microsoft") or (systemName == "Windows")):
				self.localDirSlash = "\\"
			else :
				self.localDirSlash = "/"
				print "Your operating system could not be identified, uploading and downloading may cause this to crash."
				print "Email heathen711@me.com with the following: Error Code: 13 " + systemName
			if ((sys.version_info[0] <= 2) and (sys.version_info[1] < 6)):
				socket.setdefaulttimeout(timeoutWait)
			print "System libraries imported."
		except:
			print "Error 266: Missing or broken libraries: OS, SYS, Platform, Socket; Check your python install."
			error = True
		
		if (error ==  False):
			self.psp = False
			self.error = False
			self.lines = []
			
			connected = self.establishConnection()
			if connected == True:
				self.server.getwelcome()
				print "Logging in..."
				try:
					self.server.login('', '')
				except:
					print "Error with login info."
					login = False
				print "Logged in."
				self.quit = False
				try:
					self.serverDir = self.server.pwd()
					if (self.serverDir == "/"):
						self.remoteDirSlash = "/"
					else:
						self.remoteDirSlash = "\\"
				except Exception:
					print "Error 115 (main): server did not respond with it's current directory."
					self.server.close()
					return
				self.mainMenu()
					
				self.server.close()
				print "Closed connection."

if __name__ == "__main__":
	root = PSP_FTP()